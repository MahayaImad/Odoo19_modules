# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _default_country(self):
        """Set Algeria as default country"""
        return self.env.ref('base.dz', raise_if_not_found=False)

    country_id = fields.Many2one(
        'res.country',
        default=_default_country
    )

    commune_id = fields.Many2one(
        "res.country.state.commune",
        'Commune',
        domain="[('state_id', '=', state_id)]"
    )

    localite_id = fields.Many2one(
        "res.country.state.localite",
        'Localité',
        domain="[('state_id', '=', state_id)]"
    )

    # Set state_id to False if another country get selected
    @api.onchange('country_id')
    def empty_state(self):
        for record in self:
            record.state_id = False

    # Set commune_id to False if another state get selected
    @api.onchange('state_id')
    def empty_commune(self):
        for record in self:
            record.commune_id = False
            record.localite_id = False

    # Check if localite_id, country_id and state_id are true and fill zip with localite_id.code
    # Set zip to False if another country or state or commune get selected
    @api.onchange('localite_id', 'country_id', 'state_id')
    def get_zip(self):
        for record in self:
            if record.country_id and record.state_id and record.localite_id:
                record.zip = record.localite_id.code
            else:
                record.update({'zip': False})
