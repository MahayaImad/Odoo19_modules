from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    partage = fields.Selection([
        ('not_shared', 'Non Partagée'),
        ('proposed', 'Proposée pour Partage'),
        ('shared', 'Partagée'),
        ('refused', 'Refusée'),
    ], string="État de Partage", default='not_shared', copy=False, readonly=True)

    facture_societe_fiscale_id = fields.Many2one('account.move', string="Facture Société Fiscale", copy=False,
                                                 readonly=True)
    facture_origine_operationnelle_id = fields.Many2one('account.move', string="Facture Origine", copy=False,
                                                        readonly=True)
    is_operational_company = fields.Boolean(string="Est Société Opérationnelle",
                                            compute="_compute_is_operational_company")
    active_company_ids = fields.Many2many('res.company', string="Sociétés actives",
                                          compute="_compute_selected_companies")

    @api.depends('company_id')
    def _compute_is_operational_company(self):
        for move in self:
            config = self.env['cpss.sync.config'].search([], limit=1)
            move.is_operational_company = bool(config and move.company_id == config.societe_operationnelle_id)

    @api.depends_context('allowed_company_ids')
    def _compute_selected_companies(self):
        allowed_ids = self.env.context.get('allowed_company_ids', [])
        companies = self.env['res.company'].sudo().browse(allowed_ids)
        for rec in self:
            rec.active_company_ids = companies

    def action_proposer_sync(self):
        self.ensure_one()
        if self.state != 'posted':
            raise UserError(_("Seules les factures validées peuvent être proposées."))
        if self.facture_societe_fiscale_id:
            raise UserError(_("Cette facture est déjà partagée."))
        self.partage = 'proposed'
        self.message_post(body=_("Facture proposée pour synchronisation."))

    def action_synchroniser(self):
        self.ensure_one()
        if self.partage != 'proposed':
            raise UserError(_("Seules les factures proposées peuvent être synchronisées."))

        config = self.env['cpss.sync.config'].get_config()

        try:
            utilisateur_sync = config.utilisateur_intersocietes_id
            ctx_fiscal = {
                'allowed_company_ids': [config.societe_operationnelle_id.id, config.societe_fiscale_id.id],
                'check_move_validity': False,
                'bypass_company_validation': True,
            }

            self_sync = self.with_context(ctx_fiscal).with_user(utilisateur_sync).sudo()
            facture_fiscale = self_sync._synchroniser_chaine_complete(config)

            self.write({'partage': 'shared', 'facture_societe_fiscale_id': facture_fiscale.id})

            paiements_existants = self._trouver_paiements_rapproches()
            for paiement in paiements_existants.filtered(lambda p: p.partage == 'not_shared'):
                try:
                    paiement._synchroniser_paiement_automatique()
                except Exception:
                    paiement.write({'partage': 'error'})

            self._log_sync_success(facture_fiscale, config)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('✅ Synchronisation Terminée'),
                    'message': _('Facture "%s" synchronisée\n📄 Facture fiscale : %s\n💰 %d paiement(s)') % (
                        self.name, facture_fiscale.name, len(paiements_existants)),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        except Exception as e:
            self._log_sync_error(str(e), config)
            raise UserError(_("Échec de la synchronisation : %s") % str(e))

    def action_refuser_partage(self):
        self.ensure_one()
        if self.partage != 'proposed':
            raise UserError(_("Seules les factures proposées peuvent être refusées."))
        self.partage = 'refused'
        self.message_post(body=_("Partage refusé."))

    def _synchroniser_chaine_complete(self, config):
        if self.move_type in ['out_invoice', 'out_refund']:
            return self._synchroniser_chaine_vente(config)
        elif self.move_type in ['in_invoice', 'in_refund']:
            return self._synchroniser_chaine_achat(config)
        else:
            return self._creer_facture_fiscale(config)

    def _synchroniser_chaine_vente(self, config):
        commande_origine = None
        if self.invoice_origin:
            commande_origine = self.env['sale.order'].sudo().search([('name', '=', self.invoice_origin)], limit=1)
        if not commande_origine:
            return self._creer_facture_fiscale(config)
        commande_fiscale = self._creer_commande_vente_fiscale(commande_origine, config)
        commande_fiscale.action_confirm()
        if commande_fiscale.picking_ids:
            for picking in commande_fiscale.picking_ids:
                self._traiter_livraison_fiscale(picking)
        return self._creer_facture_depuis_commande(commande_fiscale, config)

    def _synchroniser_chaine_achat(self, config):
        commande_origine = None
        if self.invoice_origin:
            commande_origine = self.env['purchase.order'].sudo().search([('name', '=', self.invoice_origin)], limit=1)
        if not commande_origine:
            return self._creer_facture_fiscale(config)
        commande_fiscale = self._creer_commande_achat_fiscale(commande_origine, config)
        commande_fiscale.button_confirm()
        if commande_fiscale.picking_ids:
            for picking in commande_fiscale.picking_ids:
                self._traiter_reception_fiscale(picking)
        facture_fiscale = self._creer_facture_fiscale(config)
        facture_fiscale.invoice_origin = commande_fiscale.name
        return facture_fiscale

    def _creer_commande_vente_fiscale(self, commande_origine, config):
        ctx = {'allowed_company_ids': [config.societe_operationnelle_id.id, config.societe_fiscale_id.id]}
        vals = {
            'partner_id': commande_origine.partner_id.id,
            'company_id': config.societe_fiscale_id.id,
            'date_order': commande_origine.date_order,
            'client_order_ref': f"SYNC-{commande_origine.name}",
            'order_line': []
        }
        for ligne in commande_origine.order_line:
            taxes_fiscales = self._mapper_taxes_vers_societe_fiscale_safe(ligne.tax_id, config)
            vals['order_line'].append((0, 0, {
                'product_id': ligne.product_id.id,
                'name': ligne.name,
                'product_uom_qty': ligne.product_uom_qty,
                'price_unit': ligne.price_unit,
                'tax_id': [(6, 0, taxes_fiscales.ids)],
            }))
        return self.env['sale.order'].with_company(config.societe_fiscale_id.id).with_context(
            ctx).with_user(config.utilisateur_intersocietes_id).sudo().create(vals)

    def _creer_commande_achat_fiscale(self, commande_origine, config):
        ctx = {'allowed_company_ids': [config.societe_operationnelle_id.id, config.societe_fiscale_id.id]}
        vals = {
            'partner_id': commande_origine.partner_id.id,
            'company_id': config.societe_fiscale_id.id,
            'date_order': commande_origine.date_order,
            'partner_ref': f"SYNC-{commande_origine.name}",
            'order_line': []
        }
        for ligne in commande_origine.order_line:
            taxes_fiscales = self._mapper_taxes_vers_societe_fiscale_safe(ligne.taxes_id, config)
            vals['order_line'].append((0, 0, {
                'product_id': ligne.product_id.id,
                'name': ligne.name,
                'product_qty': ligne.product_qty,
                'price_unit': ligne.price_unit,
                'taxes_id': [(6, 0, taxes_fiscales.ids)],
                'date_planned': ligne.date_planned,
            }))
        return self.env['purchase.order'].with_company(config.societe_fiscale_id.id).with_context(
            ctx).with_user(config.utilisateur_intersocietes_id).sudo().create(vals)

    def _traiter_livraison_fiscale(self, picking):
        if picking.state in ['draft', 'waiting', 'confirmed', 'assigned']:
            if picking.state in ['draft', 'waiting', 'confirmed']:
                picking.action_assign()
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.button_validate()

    def _traiter_reception_fiscale(self, picking):
        if picking.state in ['draft', 'waiting', 'confirmed', 'assigned']:
            if picking.state in ['draft', 'waiting', 'confirmed']:
                picking.action_assign()
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.button_validate()

    def _creer_facture_depuis_commande(self, commande_fiscale, config):
        ctx = {'allowed_company_ids': [config.societe_operationnelle_id.id, config.societe_fiscale_id.id]}
        facture_vals = commande_fiscale._prepare_invoice()
        facture_vals.update({
            'ref': f"SYNC-{self.name}",
            'invoice_origin': commande_fiscale.name,
            'narration': f"Synchronisé depuis {config.societe_operationnelle_id.name}: {self.name}",
        })
        return self.env['account.move'].with_company(config.societe_fiscale_id.id).with_context(
            ctx).with_user(config.utilisateur_intersocietes_id).sudo().create(facture_vals)

    def _creer_facture_fiscale(self, config):
        """Crée la facture dans la société fiscale"""
        utilisateur_sync = config.utilisateur_intersocietes_id

        ctx_fiscal = {
            'allowed_company_ids': [config.societe_operationnelle_id.id, config.societe_fiscale_id.id],
            'check_move_validity': False,
            'bypass_company_validation': True,
            'tracking_disable': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'default_invoice_line_tax_ids': False,
        }

        vals_facture = self._preparer_vals_facture_fiscale(config)

        if not vals_facture.get('invoice_line_ids'):
            raise UserError(_(
                "Impossible de créer la facture fiscale : aucune ligne valide.\n\n"
                "Causes possibles :\n"
                "• Comptes comptables manquants dans la société fiscale\n"
                "• Taxes modifiées manuellement sans équivalent fiscal\n"
                "• Plan comptable non installé"
            ))

        facture_fiscale = self.env['account.move'].with_context(
            ctx_fiscal
        ).with_user(utilisateur_sync).sudo().create(vals_facture)

        facture_fiscale.sudo().write({'facture_origine_operationnelle_id': self.id})
        return facture_fiscale

    def _preparer_vals_facture_fiscale(self, config):
        """Prépare les données pour la facture fiscale - VERSION ULTRA SAFE"""
        journal_fiscal = self._obtenir_journal_fiscal(config)

        vals = {
            'move_type': self.move_type,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'company_id': config.societe_fiscale_id.id,
            'journal_id': journal_fiscal.id,
            'invoice_date': self.invoice_date,
            'ref': f"SYNC-{self.name}",
            'narration': f"Synchronisé depuis {config.societe_operationnelle_id.name}: {self.name}",
            'invoice_line_ids': []
        }

        if self.invoice_origin:
            vals['invoice_origin'] = f"SYNC-{self.invoice_origin}"

        # ✅ SOLUTION FINALE: try/except sur CHAQUE ligne individuellement
        lignes_ajoutees = 0
        lignes_ignorees = []

        for idx, ligne in enumerate(self.invoice_line_ids, 1):
            try:
                vals_ligne = self._preparer_ligne_fiscale(ligne, config)
                if vals_ligne:
                    vals['invoice_line_ids'].append((0, 0, vals_ligne))
                    lignes_ajoutees += 1
            except Exception as e:
                # ✅ Capturer l'erreur et continuer avec les autres lignes
                lignes_ignorees.append(f"Ligne {idx} ({ligne.name}) : {str(e)}")
                continue

        # ✅ Vérification finale
        if lignes_ajoutees == 0:
            # Aucune ligne créée - erreur bloquante
            details_erreurs = "\n".join(lignes_ignorees) if lignes_ignorees else "Aucune ligne valide"
            raise UserError(_(
                "Impossible de créer la facture fiscale : aucune ligne valide.\n\n"
                "Détails des erreurs :\n%s\n\n"
                "Vérifiez :\n"
                "• Les comptes comptables existent dans la société fiscale\n"
                "• Le plan comptable est installé"
            ) % details_erreurs)

        # ✅ Avertissement si certaines lignes ignorées (mais ne pas bloquer)
        if lignes_ignorees:
            message = _(
                "⚠️ %d ligne(s) sur %d ignorée(s) lors de la synchronisation :\n\n%s\n\n"
                "✅ %d ligne(s) créée(s) avec succès"
            ) % (len(lignes_ignorees), len(self.invoice_line_ids), "\n".join(lignes_ignorees), lignes_ajoutees)

            # Message dans le chatter
            try:
                self.message_post(body=message, message_type='notification', subtype_xmlid='mail.mt_note')
            except Exception:
                pass

        return vals

    def _preparer_ligne_fiscale(self, ligne, config):
        """Prépare une ligne de facture fiscale - VERSION ULTRA SAFE"""
        try:
            # Mapping du compte
            compte_fiscal = self._mapper_compte_vers_societe_fiscale(ligne.account_id, config)
        except Exception as e:
            # ✅ Si compte manquant, lever l'exception pour ignorer cette ligne
            raise UserError(_("Compte %s manquant : %s") % (ligne.account_id.code, str(e)))

        # ✅ Mapping des taxes (ne lève JAMAIS d'exception)
        taxes_fiscales = self._mapper_taxes_vers_societe_fiscale_safe(ligne.tax_ids, config)

        vals_ligne = {
            'product_id': ligne.product_id.id if ligne.product_id else False,
            'account_id': compte_fiscal.id,
            'name': ligne.name,
            'quantity': ligne.quantity,
            'price_unit': ligne.price_unit,
            'tax_ids': [(6, 0, taxes_fiscales.ids)],
        }

        if ligne.discount:
            vals_ligne['discount'] = ligne.discount
        if ligne.product_uom_id:
            vals_ligne['product_uom_id'] = ligne.product_uom_id.id

        return vals_ligne

    def _mapper_taxes_vers_societe_fiscale_safe(self, taxes_operationnelles, config):
        """
        Mapper les taxes de manière ULTRA SAFE : ne JAMAIS lever d'exception
        Retourne toujours un recordset (vide si aucune taxe trouvée)
        """
        if not taxes_operationnelles:
            return self.env['account.tax']

        taxes_fiscales = self.env['account.tax']
        taxes_manquantes = []

        for taxe in taxes_operationnelles:
            try:
                taxe_fiscale = self.env['account.tax'].sudo().search([
                    ('name', '=', taxe.name),
                    ('amount', '=', taxe.amount),
                    ('type_tax_use', '=', taxe.type_tax_use),
                    ('company_id', '=', config.societe_fiscale_id.id)
                ], limit=1)

                if taxe_fiscale:
                    taxes_fiscales |= taxe_fiscale
                else:
                    taxes_manquantes.append(f"{taxe.name} ({taxe.amount}%)")
            except Exception as e:
                # ✅ AUCUNE exception ne doit sortir de cette fonction
                taxes_manquantes.append(f"{taxe.name} (erreur: {str(e)})")
                continue

        # ✅ Avertissement dans le chatter (ne bloque rien)
        if taxes_manquantes and hasattr(self, 'message_post'):
            try:
                message = _("⚠️ Taxes sans équivalent (lignes créées SANS ces taxes) :\n%s") % "\n".join(
                    [f"  • {t}" for t in taxes_manquantes])
                self.message_post(body=message, message_type='notification', subtype_xmlid='mail.mt_note')
            except Exception:
                # ✅ Même le message_post ne doit pas bloquer
                pass

        # ✅ Toujours retourner un recordset (vide ou rempli)
        return taxes_fiscales

    def _obtenir_journal_fiscal(self, config):
        env_sync = self.env(user=config.utilisateur_intersocietes_id.id)
        journal_type = {'out_invoice': 'sale', 'out_refund': 'sale',
                        'in_invoice': 'purchase', 'in_refund': 'purchase'}.get(self.move_type, 'general')
        journal = env_sync['account.journal'].sudo().search([
            ('type', '=', journal_type),
            ('company_id', '=', config.societe_fiscale_id.id)
        ], limit=1)
        if not journal:
            raise UserError(_("Aucun journal de type '%s' trouvé.") % journal_type)
        return journal

    def _mapper_compte_vers_societe_fiscale(self, compte_operationnel, config):
        compte = self.env['account.account'].sudo().search([
            ('code', '=', compte_operationnel.code),
            ('company_id', '=', config.societe_fiscale_id.id)
        ], limit=1)
        if not compte:
            raise UserError(_("Compte %s introuvable dans %s") % (
                compte_operationnel.code, config.societe_fiscale_id.name))
        return compte

    def _trouver_paiements_rapproches(self):
        self.ensure_one()
        paiements = self.env['account.payment']
        invoice_lines = self.line_ids.filtered(
            lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable'])
        for line in invoice_lines:
            for match in line.matched_debit_ids + line.matched_credit_ids:
                payment_line = match.debit_move_id if match.credit_move_id == line else match.credit_move_id
                if payment_line.payment_id and payment_line.payment_id.state == 'posted':
                    paiements |= payment_line.payment_id
            if line.full_reconcile_id:
                reconcile_lines = self.env['account.move.line'].search([
                    ('full_reconcile_id', '=', line.full_reconcile_id.id),
                    ('id', '!=', line.id)
                ])
                for rline in reconcile_lines:
                    if rline.payment_id and rline.payment_id.state == 'posted':
                        paiements |= rline.payment_id
        return paiements

    def _log_sync_success(self, facture_fiscale, config):
        self.env['cpss.sync.log']._log_sync_event(
            operation_name='Synchronisation Facture',
            status='success',
            sync_type='manual',
            source_doc=self,
            target_doc=facture_fiscale,
            config=config
        )
        self.message_post(body=_("Facture synchronisée : %s") % facture_fiscale.name)

    def _log_sync_error(self, message_erreur, config):
        self.env['cpss.sync.log']._log_sync_event(
            operation_name='Synchronisation Facture',
            status='error',
            sync_type='manual',
            error_msg=message_erreur,
            source_doc=self,
            config=config
        )
        self.message_post(body=_("Échec : %s") % message_erreur)