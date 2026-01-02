# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    qty_published = fields.Float(
        string="Quantité Publiée",
        compute='_compute_qty_by_publication_state',
        store=True,
        help="Quantité de stock provenant de factures publiées"
    )

    qty_unpublished = fields.Float(
        string="Quantité Non Publiée",
        compute='_compute_qty_by_publication_state',
        store=True,
        help="Quantité de stock provenant de factures non publiées"
    )

    @api.depends('quantity', 'location_id', 'product_id', 'company_id')
    def _compute_qty_by_publication_state(self):
        """
        Calcule les quantités publiées et non publiées
        basées sur les mouvements de stock entrants (achats)
        """
        for quant in self:
            if not quant.company_id.enable_publication_stock_tracking:
                quant.qty_published = 0
                quant.qty_unpublished = 0
                continue

            # Chercher tous les mouvements entrants vers cet emplacement pour ce produit
            incoming_moves = self.env['stock.move'].search([
                ('product_id', '=', quant.product_id.id),
                ('location_dest_id', '=', quant.location_id.id),
                ('state', '=', 'done'),
                ('company_id', '=', quant.company_id.id)
            ])

            # Sommer les quantités par état de publication
            qty_published = sum(incoming_moves.filtered(
                lambda m: m.purchase_line_id.invoice_lines.filtered(
                    lambda il: il.move_id.publication_state == 'published'
                )
            ).mapped('quantity_done'))

            qty_unpublished = sum(incoming_moves.filtered(
                lambda m: not m.purchase_line_id or not m.purchase_line_id.invoice_lines or
                         m.purchase_line_id.invoice_lines.filtered(
                             lambda il: il.move_id.publication_state == 'not_published'
                         )
            ).mapped('quantity_done'))

            # Ajuster selon les mouvements sortants (ventes)
            outgoing_moves = self.env['stock.move'].search([
                ('product_id', '=', quant.product_id.id),
                ('location_id', '=', quant.location_id.id),
                ('state', '=', 'done'),
                ('company_id', '=', quant.company_id.id)
            ])

            # Déduire les ventes publiées du stock publié
            qty_published -= sum(outgoing_moves.filtered(
                lambda m: m.sale_line_id.invoice_lines.filtered(
                    lambda il: il.move_id.publication_state == 'published'
                )
            ).mapped('quantity_done'))

            # Déduire les ventes non publiées du stock non publié
            qty_unpublished -= sum(outgoing_moves.filtered(
                lambda m: not m.sale_line_id or not m.sale_line_id.invoice_lines or
                         m.sale_line_id.invoice_lines.filtered(
                             lambda il: il.move_id.publication_state == 'not_published'
                         )
            ).mapped('quantity_done'))

            quant.qty_published = max(0, qty_published)
            quant.qty_unpublished = max(0, qty_unpublished)
