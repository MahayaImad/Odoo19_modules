# -*- encoding: utf-8 -*-
from odoo import models, fields, api

class ResCountry(models.Model):
    _inherit = 'res.country'

    commune_ids = fields.One2many('res.country.state.commune','country_id','Communes')
    localite_ids = fields.One2many('res.country.state.localite','country_id','Localités')

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    commune_ids = fields.One2many('res.country.state.commune','state_id','Communes')
    localite_ids = fields.One2many('res.country.state.localite','state_id','Localités')

    def action_read_state(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.country.state',
            'res_id': self.id,
        }

class ResCountryCommune(models.Model):
    _name = 'res.country.state.commune'
    _description = 'Commune'

    name = fields.Char('Commune', required=True,)
    code = fields.Char('Code', required=True)
    state_id = fields.Many2one('res.country.state', 'Wilaya', required=True)
    country_id = fields.Many2one('res.country', 'Pays', required=True, related='state_id.country_id')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|',('name', operator, name),('code', operator, name)]
            
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def action_read_commune(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.country.state.commune',
            'res_id': self.id,
        }

class ResCountryLocalite(models.Model):
    _name = 'res.country.state.localite'
    _description = 'Localité'

    name = fields.Char('Localité', required=True,)
    code = fields.Char('Code', required=True)
    state_id = fields.Many2one('res.country.state', 'Wilaya', required=True)
    country_id = fields.Many2one('res.country', 'Pays', required=True, related='state_id.country_id')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|',('name', operator, name),('code', operator, name)]
            
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def action_read_localite(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.country.state.localite',
            'res_id': self.id,
        }