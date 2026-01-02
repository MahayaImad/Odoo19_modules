# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CpssSubdivision(models.Model):
    _name = 'cpss.subdivision'
    _description = 'Subdivision Agricole'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
        help='Nom de la subdivision'
    )

    code = fields.Char(
        string='Code',
        help='Code de la subdivision'
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='Wilaya',
        required=True,
        ondelete='cascade'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        related='state_id.country_id',
        store=True,
        readonly=True
    )

    daira_ids = fields.One2many(
        'cpss.daira',
        'subdivision_id',
        string='Daïras'
    )

    daira_count = fields.Integer(
        string='Nombre de daïras',
        compute='_compute_daira_count'
    )

    @api.depends('daira_ids')
    def _compute_daira_count(self):
        for subdivision in self:
            subdivision.daira_count = len(subdivision.daira_ids)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def action_read_subdivision(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cpss.subdivision',
            'res_id': self.id,
        }
