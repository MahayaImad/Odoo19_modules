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
        default=lambda self: self._get_default_fndia_subsidized(),
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

    @api.model
    def _get_default_fndia_subsidized(self):
        """Active FNDIA par défaut pour les factures de vente uniquement"""
        # Si on est dans un contexte de création avec move_type défini
        move_type = self.env.context.get('default_move_type')
        return move_type == 'out_invoice'

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
        Surcharge pour créer les écritures FNDIA AVANT validation
        et recalculer le timbre fiscal
        """
        import logging
        _logger = logging.getLogger(__name__)

        # Créer les écritures FNDIA AVANT validation
        for move in self:
            if move.is_invoice() and move.fndia_subsidized and move.move_type == 'out_invoice' and move.fndia_subsidy_total > 0:
                _logger.info("█" * 80)
                _logger.info(f"FNDIA action_post - Création écritures FNDIA AVANT validation")

                # Récupérer le compte FNDIA
                fndia_account = move.company_id.fndia_subsidy_account_id

                if not fndia_account:
                    raise UserError(_(
                        "Le compte de subvention FNDIA n'est pas configuré.\n"
                        "Veuillez le configurer dans Facturation > Configuration > Paramètres."
                    ))

                _logger.info(f"  Compte FNDIA: {fndia_account.code} - {fndia_account.name}")
                _logger.info(f"  Montant FNDIA: {move.fndia_subsidy_total}")

                # Vérifier si la ligne FNDIA existe déjà
                fndia_line = move.line_ids.filtered(
                    lambda l: l.account_id.id == fndia_account.id
                )

                if not fndia_line:
                    _logger.info("  Création ligne FNDIA AVANT validation...")

                    sign = move.direction_sign
                    partner_line = move.line_ids.filtered(
                        lambda l: l.account_id.account_type == 'asset_receivable'
                    )

                    if partner_line:
                        _logger.info(f"  Ligne client AVANT - debit: {partner_line.debit}, credit: {partner_line.credit}")

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

                        _logger.info(f"  ✓ Ligne FNDIA créée")

        # Recalculer le timbre pour les factures FNDIA avant validation
        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice' and move.fndia_subsidy_total > 0:
                _logger.info("█" * 80)
                _logger.info(f"FNDIA action_post DÉBUT - Facture {move.name}")
                _logger.info(f"  AVANT recalcul - amount_untaxed: {move.amount_untaxed}")
                _logger.info(f"  AVANT recalcul - amount_tax: {move.amount_tax}")
                _logger.info(f"  AVANT recalcul - amount_total: {move.amount_total}")
                _logger.info(f"  AVANT recalcul - timbre: {move.timbre}")
                _logger.info(f"  AVANT recalcul - fndia_subsidy_total: {move.fndia_subsidy_total}")

                if move.invoice_payment_term_id and move.invoice_payment_term_id.payment_type == 'cash':
                    _logger.info(f"  Type paiement: {move.invoice_payment_term_id.payment_type} ✓")

                    # Vérifier que StampCalculator est disponible
                    if not STAMP_CALCULATOR_AVAILABLE or StampCalculator is None:
                        _logger.error("  ERREUR: StampCalculator n'est pas disponible")
                    else:
                        # Recalculer la base du timbre
                        base_timbre_original = move.amount_untaxed + move.amount_tax
                        base_timbre = move.amount_untaxed + move.amount_tax - move.fndia_subsidy_total

                        _logger.info(f"  CALCUL base_timbre: {move.amount_untaxed} + {move.amount_tax} - {move.fndia_subsidy_total} = {base_timbre}")

                        # Calculer le nouveau timbre
                        c_timbre = StampCalculator(self.env).calculate(base_timbre)
                        sign = move.direction_sign

                        _logger.info(f"  StampCalculator.calculate({base_timbre}) retourne:")
                        _logger.info(f"    - timbre: {c_timbre.get('timbre')}")
                        _logger.info(f"    - amount_timbre: {c_timbre.get('amount_timbre')}")

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

                        _logger.info(f"  MISE À JOUR:")
                        _logger.info(f"    timbre: {old_timbre} → {move.timbre}")
                        _logger.info(f"    amount_total: {old_amount_total} → {move.amount_total}")
                else:
                    _logger.warning(f"  Type paiement NON comptant ou None")

                _logger.info("FNDIA action_post FIN - Appel super()")
                _logger.info("█" * 80)

        # Appeler le super pour créer les écritures avec le bon montant de timbre
        result = super().action_post()

        # Vérifier les écritures créées (pour logging)
        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice' and move.fndia_subsidy_total > 0:
                _logger.info("█" * 80)
                _logger.info(f"FNDIA action_post APRÈS validation - Vérification")

                # Afficher les écritures finales
                partner_line = move.line_ids.filtered(
                    lambda l: l.account_id.account_type == 'asset_receivable'
                )
                _logger.info(f"  Ligne client FINAL:")
                _logger.info(f"    - debit: {partner_line.debit}")
                _logger.info(f"    - credit: {partner_line.credit}")

                fndia_account = move.company_id.fndia_subsidy_account_id
                if fndia_account:
                    fndia_line = move.line_ids.filtered(
                        lambda l: l.account_id.id == fndia_account.id
                    )
                    if fndia_line:
                        _logger.info(f"  Ligne FNDIA FINAL:")
                        _logger.info(f"    - debit: {fndia_line.debit}")
                        _logger.info(f"    - credit: {fndia_line.credit}")

                if STAMP_CALCULATOR_AVAILABLE and StampCalculator is not None:
                    try:
                        timbre_account_id = StampCalculator(self.env).GetStampAccount(move.move_type)
                        timbre_line = move.line_ids.filtered(lambda l: l.account_id.id == int(timbre_account_id))
                        if timbre_line:
                            _logger.info(f"  Ligne timbre FINAL:")
                            _logger.info(f"    - debit: {timbre_line.debit}")
                            _logger.info(f"    - credit: {timbre_line.credit}")
                    except Exception as e:
                        _logger.error(f"  Erreur timbre: {e}")

                _logger.info("█" * 80)

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