# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fndia_subsidy_amount = fields.Monetary(
        string="Montant FNDIA",
        compute='_compute_fndia_subsidy_amount',
        store=True,
        currency_field='currency_id',
        help="Montant de subvention FNDIA pour cette ligne (prix_soutien × quantité)"
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
            'exclude_from_invoice_tab': True,
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
                        lambda l: l.account_id == subsidy_account and l.exclude_from_invoice_tab
                    )
                    if old_fndia_lines:
                        old_fndia_lines.unlink()

                    # Créer la nouvelle ligne de subvention FNDIA
                    fndia_line_vals = move._prepare_fndia_subsidy_line(subsidy_account)
                    move.line_ids = [(0, 0, fndia_line_vals)]

                    # Ajuster la ligne client pour refléter le montant à payer
                    # (Total - FNDIA) au lieu du total
                    receivable_line = move.line_ids.filtered(
                        lambda l: l.account_id.account_type == 'asset_receivable' and not l.exclude_from_invoice_tab
                    )

                    if receivable_line:
                        # Le montant débiteur doit être = montant à payer (total - FNDIA)
                        receivable_line.debit = move.fndia_amount_to_pay
                        receivable_line.amount_currency = move.fndia_amount_to_pay

        # Modifier le calcul du timbre fiscal pour qu'il soit basé sur le montant à payer
        self._recompute_stamp_tax_on_fndia_amount()

        return res

    def _recompute_stamp_tax_on_fndia_amount(self):
        """
        Modifie le montant du timbre fiscal pour qu'il soit calculé sur le montant à payer
        et non sur le montant total
        """
        for move in self:
            if move.fndia_subsidized and move.move_type == 'out_invoice':
                # Trouver les lignes de timbre fiscal (généralement avec is_stamp_tax=True)
                stamp_lines = move.line_ids.filtered(
                    lambda l: hasattr(l, 'tax_line_id') and l.tax_line_id and
                    hasattr(l.tax_line_id, 'is_stamp_tax') and l.tax_line_id.is_stamp_tax
                )

                for stamp_line in stamp_lines:
                    # Recalculer le timbre basé sur le montant à payer au lieu du total
                    # Le timbre en Algérie est généralement un montant fixe basé sur des tranches
                    # mais si c'est un pourcentage, on utilise le montant à payer
                    if stamp_line.tax_line_id.amount_type == 'percent':
                        base_amount = move.fndia_amount_to_pay
                        new_stamp_amount = base_amount * (stamp_line.tax_line_id.amount / 100)
                        stamp_line.credit = new_stamp_amount
                        stamp_line.balance = -new_stamp_amount

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
