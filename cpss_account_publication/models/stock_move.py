# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        """
        Surcharge pour mettre à jour les compteurs de stock publié/non publié
        lors de la validation d'un mouvement
        """
        res = super()._action_done(cancel_backorder=cancel_backorder)

        # Recalculer les quantités publiées/non publiées pour les quants affectés
        if self.company_id.enable_publication_stock_tracking:
            affected_quants = self.env['stock.quant'].search([
                ('product_id', 'in', self.mapped('product_id').ids),
                ('location_id', 'in', (self.mapped('location_id') + self.mapped('location_dest_id')).ids),
                ('company_id', '=', self.company_id.id)
            ])
            if affected_quants:
                affected_quants._compute_qty_by_publication_state()

        return res
