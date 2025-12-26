# Copyright 2025 CPSS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _check_company_auto = True

    partage = fields.Selection([
        ('not_shared', 'Non Partagé'),
        ('shared', 'Partagé'),
        ('error', 'Erreur de Partage'),
    ], string="État de Partage", default='not_shared', copy=False, readonly=True,
        help="Indique l'état de partage du paiement avec la service comptabilité")

    paiement_societe_fiscale_id = fields.Many2one(
        'account.payment',
        string="Paiement Service Comptabilité",
        copy=False,
        readonly=True,
        check_company=False,  # Permet de lier des paiements de sociétés différentes
        help="Le paiement correspondant dans la service comptabilité"
    )

    paiement_origine_operationnelle_id = fields.Many2one(
        'account.payment',
        string="Paiement Origine",
        copy=False,
        readonly=True,
        check_company=False,  # Permet de lier des paiements de sociétés différentes
        help="Le paiement d'origine de la société opérationnelle"
    )

    is_operational_company = fields.Boolean(
        string="Est Société Opérationnelle",
        compute="_compute_is_operational_company",
        store=False,
        help="Détermine si ce paiement appartient à la société opérationnelle"
    )

    partage_error_message = fields.Text(
        string="Message d'erreur",
        readonly=True,
        help="Détails de l'erreur lors du partage"
    )

    @api.depends('company_id')
    def _compute_is_operational_company(self):
        """Détermine si le paiement appartient à la société opérationnelle"""
        config = self.env['cpss.sync.config'].search([], limit=1)
        for payment in self:
            if config:
                payment.is_operational_company = (payment.company_id == config.societe_operationnelle_id)
            else:
                payment.is_operational_company = False

    def action_post(self):
        """Override pour synchroniser automatiquement les paiements sur factures partagées"""
        res = super(AccountPayment, self).action_post()

        for payment in self:
            if not payment.is_operational_company:
                continue

            if payment.partage in ['shared', 'error']:
                continue

            if payment._doit_etre_partage():
                try:
                    payment._synchroniser_paiement_automatique()
                except Exception as e:
                    payment.write({
                        'partage': 'error',
                        'partage_error_message': str(e)
                    })

        return res

    def _doit_etre_partage(self):
        """Vérifie si le paiement doit être partagé"""
        self.ensure_one()

        if not self.reconciled_invoice_ids:
            return False

        for invoice in self.reconciled_invoice_ids:
            if hasattr(invoice, 'partage') and invoice.partage == 'shared':
                return True

        return False

    def _synchroniser_paiement_automatique(self):
        """Synchronise automatiquement le paiement vers la service comptabilité"""
        self.ensure_one()

        config = self.env['cpss.sync.config'].get_config()

        ctx_comptable = {
            'allowed_company_ids': [config.societe_operationnelle_id.id, config.societe_fiscale_id.id],
            'check_move_validity': False,
            'bypass_company_validation': True,
        }

        self_sync = self.with_company(config.societe_fiscale_id).with_context(
            ctx_comptable
        ).with_user(config.utilisateur_intersocietes_id).sudo()

        paiement_comptable = self_sync._creer_paiement_comptable_simple(config)

        self.write({
            'partage': 'shared',
            'paiement_societe_fiscale_id': paiement_comptable.id,
            'partage_error_message': False,
        })

        self._log_partage_success(paiement_comptable, config)

        self.message_post(
            body=_("✅ Paiement partagé automatiquement avec la service comptabilité : %s") % paiement_comptable.name
        )

        return paiement_comptable

    def _creer_paiement_comptable_simple(self, config):
        """Crée un paiement simple dans la service comptabilité SANS lien avec les factures"""
        self.ensure_one()

        journal_comptable = self._obtenir_journal_paiement_comptable(config)

        vals_paiement = {
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': self.date,
            'ref': f"SYNC-{self.name}",
            'journal_id': journal_comptable.id,
            'company_id': config.societe_fiscale_id.id,
            'payment_method_line_id': self._obtenir_methode_paiement_comptablee(journal_comptable).id,
            'paiement_origine_operationnelle_id': self.id,
        }

        paiement_comptable = self.env['account.payment'].create(vals_paiement)
        paiement_comptable.action_post()

        paiement_comptable.sudo().write({
            'paiement_origine_operationnelle_id': self.id
        })

        return paiement_comptable

    def _obtenir_journal_paiement_comptable(self, config):
        """Trouve le journal de paiement équivalent dans la service comptabilité"""
        self.ensure_one()

        journal_comptable = self.env['account.journal'].sudo().search([
            ('type', '=', self.journal_id.type),
            ('company_id', '=', config.societe_fiscale_id.id)
        ], limit=1)

        if not journal_comptable:
            raise UserError(_(
                "Aucun journal de type '%s' trouvé dans la service comptabilité."
            ) % self.journal_id.type)

        return journal_comptable

    def _obtenir_methode_paiement_comptablee(self, journal_comptable):
        """Trouve la méthode de paiement dans le journal comptable"""
        self.ensure_one()

        if self.payment_type == 'inbound':
            methode = journal_comptable.inbound_payment_method_line_ids[:1]
        else:
            methode = journal_comptable.outbound_payment_method_line_ids[:1]

        if not methode:
            raise UserError(_(
                "Aucune méthode de paiement trouvée pour le journal comptable %s"
            ) % journal_comptable.name)

        return methode

    def _log_partage_success(self, paiement_comptable, config):
        """Log de succès du partage"""
        self.ensure_one()

        self.env['cpss.sync.log']._log_sync_event(
            operation_name='Synchronisation Paiement',
            status='success',
            sync_type='automatic',
            source_doc=self,
            target_doc=paiement_comptable,
            config=config,
            details=f"Montant: {self.amount} {self.currency_id.name}"
        )

    def action_retry_partage(self):
        """Réessayer le partage d'un paiement en erreur"""
        self.ensure_one()

        if self.partage != 'error':
            raise UserError(_("Seuls les paiements en erreur peuvent être re-synchronisés."))

        try:
            self.write({'partage': 'not_shared', 'partage_error_message': False})
            self._synchroniser_paiement_automatique()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('✅ Succès'),
                    'message': _('Paiement synchronisé avec succès !'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.write({
                'partage': 'error',
                'partage_error_message': str(e)
            })
            raise UserError(_("Échec de la synchronisation : %s") % str(e))

    def action_partager_paiement(self):
        """Partager manuellement un paiement vers la service comptabilité"""
        self.ensure_one()

        if not self.is_operational_company:
            raise UserError(_("Cette action n'est disponible que dans la société opérationnelle."))

        if self.state != 'posted':
            raise UserError(_("Seuls les paiements validés peuvent être partagés."))

        if self.partage == 'shared':
            raise UserError(_("Ce paiement est déjà partagé avec la service comptabilité."))

        config = self.env['cpss.sync.config'].get_config()

        try:
            ctx_comptable = {
                'allowed_company_ids': [config.societe_operationnelle_id.id, config.societe_fiscale_id.id],
                'check_move_validity': False,
            }

            self_sync = self.with_company(config.societe_fiscale_id).with_context(
                ctx_comptable
            ).with_user(config.utilisateur_intersocietes_id).sudo()

            paiement_comptable = self_sync._creer_paiement_comptable_simple(config)

            self.write({
                'partage': 'shared',
                'paiement_societe_fiscale_id': paiement_comptable.id,
                'partage_error_message': False,
            })

            self._log_partage_success(paiement_comptable, config)

            self.message_post(
                body=_("✅ Paiement partagé manuellement avec la service comptabilité : %s") % paiement_comptable.name
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('✅ Partage Réussi'),
                    'message': _(
                        'Paiement "%s" partagé avec succès !\n\n'
                        '🏢 Service comptabilité : %s\n'
                        '💰 Paiement comptable : %s\n'
                        '💵 Montant : %s %s'
                    ) % (
                        self.name,
                        config.societe_fiscale_id.name,
                        paiement_comptable.name,
                        self.amount,
                        self.currency_id.name
                    ),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except UserError:
            raise
        except Exception as e:
            self.write({
                'partage': 'error',
                'partage_error_message': str(e)
            })
            raise UserError(_("Échec du partage : %s") % str(e))