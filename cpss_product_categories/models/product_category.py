# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    prix_reference = fields.Float(
        string="Prix de référence (DA)",
        help="Prix de référence en Dinars Algériens",
        digits=(12, 2)
    )

    prix_soutien = fields.Float(
        string="Montant de soutien 50% (DA)",
        help="Montant de soutien à 50% en Dinars Algériens",
        digits=(12, 2)
    )

    @api.onchange('prix_reference')
    def _onchange_prix_reference(self):
        """Calcule automatiquement le prix de soutien à 50% du prix de référence"""
        if self.prix_reference:
            self.prix_soutien = self.prix_reference * 0.5
