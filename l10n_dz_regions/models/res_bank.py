# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class ResBank(models.Model):
    _inherit = 'res.bank'

    commune_id = fields.Many2one(
        "res.country.state.commune",
        string='Commune',
        domain="[('state_id', '=', state)]"
    )

    localite_id = fields.Many2one(
        "res.country.state.localite",
        string='Localité',
        domain="[('state_id', '=', state)]"
    )

    # Note: country and bic fields already exist in res.bank (Odoo 17)
    # We don't need to redefine them, just use them in our logic

    # Set state to False if another country gets selected
    @api.onchange('country')
    def _onchange_country_empty_state(self):
        """Vide l'état quand le pays change"""
        if self.country:
            self.state = False
            self.commune_id = False
            self.localite_id = False

    # Set commune_id to False if another state gets selected
    @api.onchange('state')
    def _onchange_state_empty_commune(self):
        """Vide la commune et localité quand l'état change"""
        if self.state:
            self.commune_id = False
            self.localite_id = False

    # Check if localite_id, country and state are true and fill zip with localite_id.code
    @api.onchange('localite_id', 'country', 'state')
    def _onchange_localite_get_zip(self):
        """Met à jour le code postal basé sur la localité"""
        if self.country and self.state and self.localite_id:
            if hasattr(self.localite_id, 'code') and self.localite_id.code:
                self.zip = self.localite_id.code
        else:
            self.zip = False
