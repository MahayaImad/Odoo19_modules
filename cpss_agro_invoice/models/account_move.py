# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

# Importer StampCalculator au niveau du module plutôt que dans les méthodes
try:
    from odoo.addons.l10n_dz_on_timbre_fiscal.utils import StampCalculator
    STAMP_CALCULATOR_AVAILABLE = True
    _logger.info("✓ StampCalculator importé avec succès depuis odoo.addons.l10n_dz_on_timbre_fiscal.utils")
except ImportError as e:
    STAMP_CALCULATOR_AVAILABLE = False
    _logger.error(f"✗ Impossible d'importer StampCalculator: {e}")
    StampCalculator = None


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fndia_subsidy_amount = fields.Monetary(
        string="Montant FNDIA",
        compute='_compute_fndia_subsidy_amount',
        store=True,
        currency_field='currency_id',
        help="Montant de subvention FNDIA pour cette ligne (prix_soutien × quantité)"
    )

    isFNDIA = fields.Boolean(
        string="Ligne FNDIA",
        default=False,
        help="Indique si cette ligne est une écriture de subvention FNDIA"
    )

    @api.depends('product_id', 'quantity', 'move_id.fndia_subsidized', 'move_id.move_type')
    def _compute_fndia_subsidy_amount(self):
        """Calcule le montant de subvention FNDIA pour chaque ligne"""
        for line in self:
            if (line.move_id.fndia_subsidized and
                line.move_id.move_type == 'out_invoice' and
                line.product_id and
                line.product_id.categ_id):

                # Récupérer le montant de soutien depuis la catégorie produit
                prix_soutien = line.product_id.categ_id.prix_soutien or 0.0
                line.fndia_subsidy_amount = prix_soutien * line.quantity
            else:
                line.fndia_subsidy_amount = 0.0


class AccountMove(models.Model):
    _inherit = 'account.move'

    fndia_subsidized = fields.Boolean(
        string="Subventionné FNDIA",
        default=False,
        tracking=True,
        help="Si activé, la subvention FNDIA sera calculée et enregistrée dans un compte séparé"
    )

    fndia_subsidy_total = fields.Monetary(
        string="Montant Total FNDIA",
        compute='_compute_fndia_amounts',
        store=True,
        currency_field='currency_id',
        help="Montant total de la subvention FNDIA (somme des montants FNDIA de toutes les lignes)"
    )

    fndia_amount_to_pay = fields.Monetary(
        string="Montant à Payer",
        compute='_compute_fndia_amounts',
        store=True,
        currency_field='currency_id',
        help="Montant à payer par le client (Montant TTC - Montant FNDIA)"
    )

    @api.depends('invoice_line_ids', 'invoice_line_ids.isFNDIA')
    def _compute_invoice_line_ids_visible(self):
        """
        Override du module l10n_dz_on_timbre_fiscal pour filtrer aussi les lignes FNDIA
        afin de masquer les lignes FNDIA de l'onglet "Lignes de facture"
        """
        _logger.info("=" * 80)
        _logger.info("DIAGNOSTIC: _compute_invoice_line_ids_visible APPELÉE")

        super()._compute_invoice_line_ids_visible()

        for move in self:
            _logger.info(f"  Facture: {move.name or 'Nouveau'}")
            _logger.info(f"  Nombre total de lignes (invoice_line_ids): {len(move.invoice_line_ids)}")

            # Afficher détails de chaque ligne
            for idx, line in enumerate(move.invoice_line_ids, 1):
                _logger.info(f"    Ligne {idx}: {line.name[:50] if line.name else 'Sans nom'}")
                _logger.info(f"      - account_id: {line.account_id.code if line.account_id else 'None'}")
                _logger.info(f"      - isFNDIA: {line.isFNDIA}")
                _logger.info(f"      - isStamp: {line.isStamp}")
                _logger.info(f"      - display_type: {line.display_type}")

            # Filtrer à la fois les lignes Stamp ET FNDIA
            move.invoice_line_ids_visible = move.invoice_line_ids.filtered(
                lambda l: not l.isStamp and not l.isFNDIA
            )

            _logger.info(f"  Nombre lignes APRÈS filtrage (invoice_line_ids_visible): {len(move.invoice_line_ids_visible)}")
            _logger.info("=" * 80)

    @api.depends('invoice_line_ids.fndia_subsidy_amount', 'amount_total', 'fndia_subsidized')
    def _compute_fndia_amounts(self):
        """Calcule les montants FNDIA totaux"""
        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice':
                # Somme des montants FNDIA de toutes les lignes
                move.fndia_subsidy_total = sum(move.invoice_line_ids.mapped('fndia_subsidy_amount'))
                # Montant à payer = Total TTC - Subvention FNDIA
                move.fndia_amount_to_pay = move.amount_total - move.fndia_subsidy_total
            else:
                move.fndia_subsidy_total = 0.0
                move.fndia_amount_to_pay = move.amount_total

    @api.onchange('fndia_subsidized')
    def _onchange_fndia_subsidized(self):
        """Recalcule les montants quand on change le statut FNDIA"""
        if self.fndia_subsidized and self.move_type != 'out_invoice':
            return {
                'warning': {
                    'title': _('Attention'),
                    'message': _('La subvention FNDIA est disponible uniquement pour les factures client.')
                }
            }
        for line in self.invoice_line_ids:
            line._compute_fndia_subsidy_amount()

        # Forcer le recalcul des totaux FNDIA (première passe)
        self._compute_fndia_amounts()
        self._compute_amount()

        # Recalculer les totaux FNDIA (deuxième passe avec amount_total à jour)
        self._compute_fndia_amounts()

        # Forcer le recalcul des tax_totals (pour afficher/masquer FNDIA dans les totaux)
        self._compute_tax_totals()

    def write(self, vals):
        """
        Surcharge pour gérer le changement de fndia_subsidized sur une facture validée
        """
        _logger.info("🔵" * 80)
        _logger.info(f"FNDIA write() APPELÉE - vals: {vals}")
        _logger.info(f"  Nombre de factures dans self: {len(self)}")

        # Détecter si fndia_subsidized change
        if 'fndia_subsidized' in vals:
            _logger.info(f"  ✓ 'fndia_subsidized' détecté dans vals = {vals['fndia_subsidized']}")

            for move in self:
                _logger.info(f"  Facture: {move.name}")
                _logger.info(f"    - state: {move.state}")
                _logger.info(f"    - move_type: {move.move_type}")
                _logger.info(f"    - fndia_subsidized actuel: {move.fndia_subsidized}")
                _logger.info(f"    - fndia_subsidized nouveau: {vals['fndia_subsidized']}")

                # Si facture validée et changement FNDIA
                if move.state == 'posted' and move.move_type == 'out_invoice':
                    _logger.info(f"    ✓ Facture validée de type out_invoice")

                    old_value = move.fndia_subsidized
                    new_value = vals['fndia_subsidized']

                    # Si on décoche FNDIA sur facture validée
                    if old_value and not new_value:
                        _logger.info("=" * 80)
                        _logger.info(f"FNDIA write() - DÉCOCHER FNDIA sur facture validée {move.name}")
                        _logger.info(f"  Transition: True → False")

                        # DIAGNOSTIC : Afficher TOUTES les lignes de la facture
                        _logger.info(f"  AVANT modification - Toutes les lignes de la facture:")
                        for idx, line in enumerate(move.line_ids, 1):
                            _logger.info(f"    Ligne {idx}: {line.name[:40] if line.name else 'Sans nom'}")
                            _logger.info(f"      - account: {line.account_id.code} ({line.account_id.account_type})")
                            _logger.info(f"      - debit: {line.debit}, credit: {line.credit}")
                            _logger.info(f"      - isFNDIA: {line.isFNDIA}")
                            _logger.info(f"      - ID: {line.id}")

                        # Chercher lignes FNDIA existantes
                        fndia_lines = move.line_ids.filtered(lambda l: l.isFNDIA)
                        _logger.info(f"  Lignes FNDIA trouvées: {len(fndia_lines)}")

                        if fndia_lines:
                            _logger.info(f"  ✓ Trouvé {len(fndia_lines)} lignes FNDIA à supprimer")
                            for fndia_line in fndia_lines:
                                _logger.info(f"    - ID {fndia_line.id}: {fndia_line.name}, debit={fndia_line.debit}, credit={fndia_line.credit}")

                            # Récupérer la ligne client
                            partner_line = move.line_ids.filtered(
                                lambda l: l.account_id.account_type == 'asset_receivable'
                            )

                            _logger.info(f"  Lignes receivable trouvées: {len(partner_line)}")

                            if partner_line:
                                try:
                                    partner_line.ensure_one()  # S'assurer qu'il n'y a qu'une seule ligne
                                    _logger.info(f"  ✓ Une seule ligne client trouvée: {partner_line.account_id.code}")
                                except ValueError as e:
                                    _logger.error(f"  ✗ ERREUR: Multiple lignes receivable trouvées!")
                                    for pl in partner_line:
                                        _logger.error(f"    - {pl.account_id.code}: debit={pl.debit}, credit={pl.credit}")
                                    raise

                                sign = move.direction_sign
                                _logger.info(f"  direction_sign: {sign}")

                                # Montant FNDIA à remettre sur compte client
                                fndia_total = sum(fndia_lines.mapped('debit')) - sum(fndia_lines.mapped('credit'))

                                _logger.info(f"  Montant FNDIA à remettre: {fndia_total}")
                                _logger.info(f"  Ligne client AVANT suppression:")
                                _logger.info(f"    - debit: {partner_line.debit}")
                                _logger.info(f"    - credit: {partner_line.credit}")

                                # Supprimer les lignes FNDIA
                                _logger.info(f"  Suppression des lignes FNDIA avec unlink()...")
                                fndia_lines.unlink()
                                _logger.info(f"  ✓ unlink() exécuté")

                                # Augmenter le compte client
                                new_debit = partner_line.debit + fndia_total if -sign > 0 else partner_line.debit
                                new_credit = partner_line.credit if -sign > 0 else partner_line.credit + fndia_total

                                _logger.info(f"  Calcul nouveaux montants:")
                                _logger.info(f"    - Nouveau debit: {new_debit} (ancien: {partner_line.debit})")
                                _logger.info(f"    - Nouveau credit: {new_credit} (ancien: {partner_line.credit})")

                                partner_line.write({
                                    'debit': new_debit,
                                    'credit': new_credit,
                                })
                                _logger.info(f"  ✓ partner_line.write() exécuté")

                                _logger.info(f"  Ligne client APRÈS modification:")
                                _logger.info(f"    - debit: {partner_line.debit}")
                                _logger.info(f"    - credit: {partner_line.credit}")

                                # DIAGNOSTIC : Afficher TOUTES les lignes après suppression
                                _logger.info(f"  APRÈS modification - Toutes les lignes de la facture:")
                                for idx, line in enumerate(move.line_ids, 1):
                                    _logger.info(f"    Ligne {idx}: {line.name[:40] if line.name else 'Sans nom'}")
                                    _logger.info(f"      - account: {line.account_id.code}")
                                    _logger.info(f"      - debit: {line.debit}, credit: {line.credit}")
                                    _logger.info(f"      - isFNDIA: {line.isFNDIA}")

                                # Recalculer invoice_line_ids_visible
                                move._compute_invoice_line_ids_visible()
                                _logger.info(f"  ✓ invoice_line_ids_visible recalculé")

                        else:
                            _logger.warning(f"  ✗ AUCUNE ligne FNDIA trouvée!")
                            _logger.warning(f"  Vérification: Toutes les lignes avec isFNDIA:")
                            for line in move.line_ids:
                                if hasattr(line, 'isFNDIA'):
                                    _logger.warning(f"    - {line.name}: isFNDIA={line.isFNDIA}")

                    # Si on coche FNDIA sur facture validée
                    elif not old_value and new_value:
                        _logger.info("=" * 80)
                        _logger.info(f"FNDIA write() - COCHER FNDIA sur facture validée {move.name}")
                        _logger.info(f"  Transition: False → True")

                        # Chercher lignes FNDIA existantes
                        fndia_lines = move.line_ids.filtered(lambda l: l.isFNDIA)

                        if fndia_lines:
                            _logger.info(f"  Trouvé {len(fndia_lines)} lignes FNDIA à supprimer")

                            # Récupérer la ligne client
                            partner_line = move.line_ids.filtered(
                                lambda l: l.account_id.account_type == 'asset_receivable'
                            )

                            if partner_line:
                                partner_line.ensure_one()  # S'assurer qu'il n'y a qu'une seule ligne
                                sign = move.direction_sign
                                # Montant FNDIA à remettre sur compte client
                                fndia_total = sum(fndia_lines.mapped('debit')) - sum(fndia_lines.mapped('credit'))

                                _logger.info(f"  Montant FNDIA à remettre: {fndia_total}")
                                _logger.info(f"  Ligne client avant: debit={partner_line.debit}, credit={partner_line.credit}")

                                # Supprimer les lignes FNDIA
                                fndia_lines.unlink()

                                # Augmenter le compte client
                                partner_line.write({
                                    'debit': partner_line.debit + fndia_total if -sign > 0 else partner_line.debit,
                                    'credit': partner_line.credit if -sign > 0 else partner_line.credit + fndia_total,
                                })

                                _logger.info(f"  Ligne client après: debit={partner_line.debit}, credit={partner_line.credit}")
                                _logger.info("  ✓ Lignes FNDIA supprimées")

                                # Recalculer invoice_line_ids_visible
                                move._compute_invoice_line_ids_visible()

                    # Si on coche FNDIA sur facture validée
                    elif not old_value and new_value:
                        _logger.info("=" * 80)
                        _logger.info(f"FNDIA write() - Création lignes FNDIA sur facture validée {move.name}")

                        # Appeler d'abord super().write() pour que fndia_subsidized soit mis à jour
                        super(AccountMove, move).write(vals)

                        # Recalculer les montants FNDIA
                        for line in move.invoice_line_ids:
                            line._compute_fndia_subsidy_amount()
                        move._compute_fndia_amounts()
                        move._compute_amount()

                        # Créer les lignes FNDIA si montant > 0
                        if move.fndia_subsidy_total > 0:
                            fndia_account = move.company_id.fndia_subsidy_account_id

                            if not fndia_account:
                                raise UserError(_(
                                    "Le compte de subvention FNDIA n'est pas configuré.\n"
                                    "Veuillez le configurer dans Facturation > Configuration > Paramètres."
                                ))

                            _logger.info(f"  Montant FNDIA: {move.fndia_subsidy_total}")

                            # Récupérer la ligne client
                            partner_line = move.line_ids.filtered(
                                lambda l: l.account_id.account_type == 'asset_receivable'
                            )

                            if partner_line:
                                partner_line.ensure_one()  # S'assurer qu'il n'y a qu'une seule ligne
                                sign = move.direction_sign

                                _logger.info(f"  Ligne client avant: debit={partner_line.debit}, credit={partner_line.credit}")

                                # Réduire le compte client
                                partner_line.write({
                                    'debit': partner_line.debit - move.fndia_subsidy_total if -sign > 0 else partner_line.debit,
                                    'credit': partner_line.credit if -sign > 0 else partner_line.credit - move.fndia_subsidy_total,
                                })

                                # Créer la ligne FNDIA
                                self.env['account.move.line'].create({
                                    'name': 'Subvention FNDIA',
                                    'move_id': move.id,
                                    'account_id': fndia_account.id,
                                    'debit': move.fndia_subsidy_total if -sign > 0 else 0.0,
                                    'credit': 0.0 if -sign > 0 else move.fndia_subsidy_total,
                                    'partner_id': move.partner_id.id,
                                    'isFNDIA': True,
                                })

                                _logger.info(f"  Ligne client après: debit={partner_line.debit}, credit={partner_line.credit}")
                                _logger.info("  ✓ Ligne FNDIA créée")

                                # Recalculer invoice_line_ids_visible
                                move._compute_invoice_line_ids_visible()

                        # Ne pas appeler super().write() à la fin car déjà fait
                        _logger.info(f"  Retour anticipé (super().write() déjà appelé)")
                        return True
                else:
                    _logger.info(f"    ⚠ Facture NON validée (state={move.state}) OU type incorrect (move_type={move.move_type})")
        else:
            _logger.info(f"  ⚠ 'fndia_subsidized' N'EST PAS dans vals")

        _logger.info(f"🔵 Fin write() - Appel super().write(vals)")
        result = super().write(vals)
        _logger.info(f"🔵 super().write() terminé avec succès")
        return result

    def _get_fndia_account(self):
        """Retourne le compte comptable pour la subvention FNDIA"""
        self.ensure_one()

        # Récupérer le compte depuis la configuration
        fndia_account = self.company_id.fndia_subsidy_account_id

        if not fndia_account and self.fndia_subsidized and self.fndia_subsidy_total > 0:
            raise UserError(_(
                "Le compte de subvention FNDIA n'est pas configuré. "
                "Veuillez le configurer dans Facturation > Configuration > Paramètres."
            ))

        return fndia_account

    def _prepare_fndia_subsidy_line(self, subsidy_account):
        """Prépare la ligne d'écriture pour la subvention FNDIA"""
        self.ensure_one()

        return {
            'name': _('Subvention FNDIA'),
            'move_id': self.id,
            'account_id': subsidy_account.id,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'debit': self.fndia_subsidy_total if self.move_type == 'out_invoice' else 0.0,
            'credit': self.fndia_subsidy_total if self.move_type == 'out_refund' else 0.0,
            'isFNDIA': True,
        }

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        """
        Surcharge pour ajouter la ligne de subvention FNDIA dans les écritures comptables
        et modifier le calcul du timbre fiscal
        """
        res = super()._recompute_dynamic_lines(
            recompute_all_taxes=recompute_all_taxes,
            recompute_tax_base_amount=recompute_tax_base_amount
        )

        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice' and move.fndia_subsidy_total > 0:
                # Récupérer le compte FNDIA
                subsidy_account = move._get_fndia_account()
                _logger.info("=" * 80)
                _logger.info(subsidy_account)
                _logger.info("=" * 80)


                if subsidy_account:
                    # Supprimer l'ancienne ligne FNDIA si elle existe
                    old_fndia_lines = move.line_ids.filtered(
                        lambda l: l.account_id == subsidy_account and l.isFNDIA
                    )
                    if old_fndia_lines:
                        old_fndia_lines.unlink()

                    # Créer la nouvelle ligne de subvention FNDIA
                    fndia_line_vals = move._prepare_fndia_subsidy_line(subsidy_account)
                    move.line_ids = [(0, 0, fndia_line_vals)]

                    # Ajuster la ligne client pour refléter le montant à payer
                    # (Total - FNDIA) au lieu du total
                    receivable_line = move.line_ids.filtered(
                        lambda l: l.account_id.account_type == 'asset_receivable' and not l.isFNDIA
                    )

                    if receivable_line:
                        # Le montant débiteur doit être = montant à payer (total - FNDIA)
                        receivable_line.debit = move.fndia_amount_to_pay
                        receivable_line.amount_currency = move.fndia_amount_to_pay

        return res

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.origin_payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.origin_payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state',
        'invoice_payment_term_id',
        'fndia_subsidized',  # Ajouter FNDIA aux dépendances
        'fndia_subsidy_total',  # Ajouter FNDIA aux dépendances
        'invoice_line_ids.fndia_subsidy_amount',  # Recalculer quand les montants FNDIA des lignes changent
    )
    def _compute_amount(self):
        """
        Surcharge de la méthode du module l10n_dz_on_timbre_fiscal
        pour calculer le timbre sur le montant après déduction FNDIA
        """
        import logging
        _logger = logging.getLogger(__name__)

        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice':
                _logger.info("=" * 80)
                _logger.info(f"FNDIA _compute_amount DÉBUT - Facture {move.name}")
                _logger.info(f"  AVANT super() - amount_untaxed: {move.amount_untaxed}")
                _logger.info(f"  AVANT super() - amount_tax: {move.amount_tax}")
                _logger.info(f"  AVANT super() - amount_total: {move.amount_total}")
                _logger.info(f"  AVANT super() - timbre: {move.timbre}")
                _logger.info(f"  AVANT super() - fndia_subsidy_total: {move.fndia_subsidy_total}")

        # Appeler la méthode parente pour calculer le timbre
        super()._compute_amount()

        # Si FNDIA est activé, recalculer le timbre sur la bonne base
        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice' and move.fndia_subsidy_total > 0:
                _logger.info(f"  APRÈS super() - amount_untaxed: {move.amount_untaxed}")
                _logger.info(f"  APRÈS super() - amount_tax: {move.amount_tax}")
                _logger.info(f"  APRÈS super() - amount_total: {move.amount_total}")
                _logger.info(f"  APRÈS super() - timbre: {move.timbre}")

                # Vérifier si on est en paiement comptant (condition du module parent)
                if move.invoice_payment_term_id and move.invoice_payment_term_id.payment_type == 'cash':
                    _logger.info(f"  Type paiement: {move.invoice_payment_term_id.payment_type} ✓")

                    # Vérifier que StampCalculator est disponible
                    if not STAMP_CALCULATOR_AVAILABLE or StampCalculator is None:
                        _logger.error("  ERREUR: StampCalculator n'est pas disponible (import a échoué au chargement du module)")
                        continue

                    # Recalculer la base du timbre en déduisant FNDIA
                    base_timbre_original = move.amount_untaxed + move.amount_tax
                    base_timbre_fndia = move.amount_untaxed + move.amount_tax - move.fndia_subsidy_total

                    _logger.info(f"  CALCUL base_timbre_original: {move.amount_untaxed} + {move.amount_tax} = {base_timbre_original}")
                    _logger.info(f"  CALCUL base_timbre_fndia: {base_timbre_original} - {move.fndia_subsidy_total} = {base_timbre_fndia}")

                    # Calculer le nouveau timbre avec StampCalculator
                    c_timbre = StampCalculator(self.env).calculate(base_timbre_fndia)
                    sign = move.direction_sign

                    _logger.info(f"  StampCalculator.calculate({base_timbre_fndia}) retourne:")
                    _logger.info(f"    - timbre: {c_timbre.get('timbre')}")
                    _logger.info(f"    - amount_timbre: {c_timbre.get('amount_timbre')}")
                    _logger.info(f"  direction_sign: {sign}")

                    # Mettre à jour les montants avec le nouveau timbre
                    old_timbre = move.timbre
                    old_amount_total = move.amount_total

                    move.timbre = c_timbre['timbre']
                    move.timbre_signed = -sign * move.timbre
                    move.amount_total = c_timbre['amount_timbre']
                    move.amount_total_signed = -sign * move.amount_total
                    move.amount_total_in_currency_signed = -sign * move.amount_total
                    move.amount_residual = c_timbre['amount_timbre']
                    move.amount_residual_signed = -sign * move.amount_residual

                    _logger.info(f"  MISE À JOUR:")
                    _logger.info(f"    timbre: {old_timbre} → {move.timbre}")
                    _logger.info(f"    amount_total: {old_amount_total} → {move.amount_total}")
                else:
                    _logger.warning(f"  Type paiement NON comptant: {move.invoice_payment_term_id.payment_type if move.invoice_payment_term_id else 'None'}")

                _logger.info("FNDIA _compute_amount FIN")
                _logger.info("=" * 80)

    def action_post(self):
        """
        Surcharge pour créer/supprimer les écritures FNDIA AVANT validation
        et recalculer le timbre fiscal
        """


        # Gérer les écritures FNDIA AVANT validation
        for move in self:
            if not move.is_invoice() or move.move_type != 'out_invoice':
                continue

            # Récupérer le compte FNDIA
            fndia_account = move.company_id.fndia_subsidy_account_id

            # Chercher les lignes FNDIA existantes
            fndia_lines = move.line_ids.filtered(lambda l: l.isFNDIA)

            # CAS 1 : FNDIA décoché → Supprimer les lignes FNDIA existantes
            if not move.fndia_subsidized:
                if fndia_lines:

                    # Récupérer la ligne client
                    partner_line = move.line_ids.filtered(
                        lambda l: l.account_id.account_type == 'asset_receivable'
                    )

                    if partner_line:
                        sign = move.direction_sign

                        # Montant total FNDIA à remettre sur le compte client
                        fndia_total = sum(fndia_lines.mapped('debit')) - sum(fndia_lines.mapped('credit'))

                        # Supprimer les lignes FNDIA et augmenter le compte client
                        move.line_ids = [
                            # AUGMENTER la ligne client
                            (1, partner_line.id, {
                                'debit': partner_line.debit + fndia_total if -sign > 0 else partner_line.debit,
                                'credit': partner_line.credit if -sign > 0 else partner_line.credit + fndia_total,
                            }),

                            # SUPPRIMER les lignes FNDIA
                            *[(2, line.id) for line in fndia_lines]
                        ]
                        move._compute_invoice_line_ids_visible()

            # CAS 2 : FNDIA coché → Créer/Mettre à jour les lignes FNDIA
            elif move.fndia_subsidy_total > 0:

                if not fndia_account:
                    raise UserError(_(
                        "Le compte de subvention FNDIA n'est pas configuré.\n"
                        "Veuillez le configurer dans Facturation > Configuration > Paramètres."
                    ))

                # DIAGNOSTIC : Afficher toutes les lignes receivable AVANT création FNDIA
                receivable_lines_before = move.line_ids.filtered(
                    lambda l: l.account_id.account_type == 'asset_receivable'
                )

                if not fndia_lines:
                    sign = move.direction_sign
                    partner_line = move.line_ids.filtered(
                        lambda l: l.account_id.account_type == 'asset_receivable'
                    )

                    if partner_line:

                        # Modifier directement line_ids (avant validation, c'est possible)
                        move.line_ids = [
                            # RÉDUIRE la ligne client
                            (1, partner_line.id, {
                                'debit': partner_line.debit - move.fndia_subsidy_total if -sign > 0 else partner_line.debit,
                                'credit': partner_line.credit if -sign > 0 else partner_line.credit - move.fndia_subsidy_total,
                            }),
                            # CRÉER la ligne FNDIA
                            (0, 0, {
                                'name': 'Subvention FNDIA',
                                'account_id': fndia_account.id,
                                'debit': move.fndia_subsidy_total if -sign > 0 else 0.0,
                                'credit': 0.0 if -sign > 0 else move.fndia_subsidy_total,
                                'partner_id': move.partner_id.id,
                                'isFNDIA': True,
                            })
                        ]

        # Recalculer le timbre pour les factures FNDIA avant validation
        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice' and move.fndia_subsidy_total > 0:

                if move.invoice_payment_term_id and move.invoice_payment_term_id.payment_type == 'cash':

                    # Vérifier que StampCalculator est disponible
                    if not STAMP_CALCULATOR_AVAILABLE or StampCalculator is None:
                        continue
                    else:
                        # Recalculer la base du timbre
                        base_timbre_original = move.amount_untaxed + move.amount_tax
                        base_timbre = move.amount_untaxed + move.amount_tax - move.fndia_subsidy_total

                        # Calculer le nouveau timbre
                        c_timbre = StampCalculator(self.env).calculate(base_timbre)
                        sign = move.direction_sign

                        old_timbre = move.timbre
                        old_amount_total = move.amount_total

                        # Mettre à jour AVANT l'appel à super()
                        move.timbre = c_timbre['timbre']
                        move.timbre_signed = -sign * move.timbre
                        move.amount_total = c_timbre['amount_timbre']
                        move.amount_total_signed = -sign * move.amount_total
                        move.amount_total_in_currency_signed = -sign * move.amount_total
                        move.amount_residual = c_timbre['amount_timbre']
                        move.amount_residual_signed = -sign * move.amount_residual

                else:
                    continue


        # Appeler le super pour créer les écritures avec le bon montant de timbre
        result = super().action_post()

        return result

    @api.depends_context('lang')
    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
        'fndia_subsidized',
        'fndia_subsidy_total',
        'invoice_line_ids.fndia_subsidy_amount',
    )
    def _compute_tax_totals(self):
        """
        Surcharge pour ajouter la subvention FNDIA dans les totaux affichés
        avant le timbre fiscal
        """
        super()._compute_tax_totals()

        for move in self:
            if move.is_invoice() and move.fndia_subsidized and move.move_type == 'out_invoice' and move.fndia_subsidy_total > 0:
                # Ajouter la subvention FNDIA dans les sous-totaux avant le timbre
                # Le timbre a une séquence de 1000, donc on met FNDIA à 999 pour qu'il apparaisse avant
                move.tax_totals.setdefault('subtotals', []).append({
                    'name': "Subvention FNDIA",
                    'amount': -move.fndia_subsidy_total,  # Négatif car c'est une déduction
                    'base_amount': -move.fndia_subsidy_total,
                    'base_amount_currency': -move.fndia_subsidy_total,
                    'form_label': "Subvention FNDIA",
                    'tax_ids': [],
                    'display': True,
                    'sequence': 999,  # Avant le timbre (1000)
                    'code': "fndia",
                    'group': "fndia",
                    'tax_groups': [],
                })

    @api.constrains('fndia_subsidized', 'fndia_subsidy_total', 'amount_total')
    def _check_fndia_subsidy(self):
        """Vérifications sur la subvention FNDIA"""
        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice':
                # Ne vérifier que si amount_total a été calculé (> 0)
                # Pendant la création de la facture, amount_total peut être 0
                if move.amount_total > 0 and move.fndia_subsidy_total > move.amount_total:
                    raise ValidationError(_(
                        "Le montant de la subvention FNDIA (%(subsidy)s) ne peut pas dépasser "
                        "le montant total de la facture (%(total)s).",
                        subsidy=move.fndia_subsidy_total,
                        total=move.amount_total
                    ))

                if move.fndia_subsidy_total < 0:
                    raise ValidationError(_(
                        "Le montant de la subvention FNDIA ne peut pas être négatif."
                    ))