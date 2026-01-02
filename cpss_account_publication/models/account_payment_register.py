# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_published_invoice = fields.Boolean(
        string="Facture publiée",
        compute='_compute_is_published_invoice'
    )

    @api.depends('line_ids')
    def _compute_is_published_invoice(self):
        """Détermine si on traite des factures publiées"""
        for wizard in self:
            moves = wizard.line_ids.mapped('move_id')
            wizard.is_published_invoice = any(move.publication_state == 'published' for move in moves)

    @api.model
    def default_get(self, fields_list):
        """Définit le journal par défaut selon l'état de publication"""
        res = super().default_get(fields_list)

        # Récupérer les factures sélectionnées
        if self._context.get('active_model') == 'account.move':
            move_ids = self._context.get('active_ids', [])
            moves = self.env['account.move'].browse(move_ids)

            # Si toutes les factures sont publiées, utiliser le journal de publication
            if moves and all(m.publication_state == 'published' for m in moves):
                company = moves[0].company_id
                if company.journal_publication_id:
                    res['journal_id'] = company.journal_publication_id.id

        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        """Surcharge pour utiliser le journal de publication si nécessaire"""
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)

        # Vérifier si on traite des factures publiées
        lines = batch_result['lines']
        if lines:
            moves = lines.mapped('move_id')
            # Si au moins une facture est publiée, utiliser le journal de publication
            if any(move.publication_state == 'published' for move in moves):
                company = moves[0].company_id
                if company.journal_publication_id:
                    payment_vals['journal_id'] = company.journal_publication_id.id

        return payment_vals

    def action_create_payments(self):
        """Vérifie la cohérence avant de créer les paiements"""
        # Vérifier si on mélange des factures publiées et non publiées
        moves = self.line_ids.mapped('move_id')
        published = moves.filtered(lambda m: m.publication_state == 'published')
        not_published = moves.filtered(lambda m: m.publication_state == 'not_published')

        if published and not_published:
            # Avertissement si on mélange les types
            raise UserError(_(
                "Vous ne pouvez pas payer simultanément des factures publiées et non publiées. "
                "Veuillez sélectionner uniquement un type de facture."
            ))

        # Si factures publiées, vérifier qu'un journal de publication est configuré
        if published:
            company = published[0].company_id
            if not company.journal_publication_id:
                raise UserError(_(
                    "Aucun journal de publication n'est configuré pour cette société. "
                    "Veuillez configurer un journal dans les paramètres de la société."
                ))

        return super().action_create_payments()