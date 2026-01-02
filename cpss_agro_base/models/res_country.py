# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    subdivision_ids = fields.One2many(
        'cpss.subdivision',
        'state_id',
        string='Subdivisions'
    )

    daira_ids = fields.One2many(
        'cpss.daira',
        'state_id',
        string='Daïras'
    )


class ResCountryStateCommune(models.Model):
    _inherit = 'res.country.state.commune'

    daira_id = fields.Many2one(
        'cpss.daira',
        string='Daïra',
        ondelete='set null'
    )

    subdivision_id = fields.Many2one(
        'cpss.subdivision',
        string='Subdivision',
        related='daira_id.subdivision_id',
        store=True,
        readonly=True
    )
