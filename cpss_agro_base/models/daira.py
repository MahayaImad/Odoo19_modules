# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CpssDaira(models.Model):
    _name = 'cpss.daira'
    _description = 'Daïra'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
        help='Nom de la daïra'
    )

    code = fields.Char(
        string='Code',
        help='Code de la daïra'
    )

    subdivision_id = fields.Many2one(
        'cpss.subdivision',
        string='Subdivision',
        required=True,
        ondelete='cascade'
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='Wilaya',
        related='subdivision_id.state_id',
        store=True,
        readonly=True
    )

    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        related='state_id.country_id',
        store=True,
        readonly=True
    )

    commune_ids = fields.One2many(
        'res.country.state.commune',
        'daira_id',
        string='Communes'
    )

    commune_count = fields.Integer(
        string='Nombre de communes',
        compute='_compute_commune_count'
    )

    @api.depends('commune_ids')
    def _compute_commune_count(self):
        for daira in self:
            daira.commune_count = len(daira.commune_ids)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def action_read_daira(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cpss.daira',
            'res_id': self.id,
        }
