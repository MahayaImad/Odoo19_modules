# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

class ActivityCode(models.Model):

    _name = "activity.code"
    _description = "Code d'activité"


    name = fields.Char(string="Nom", required=True, index=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company.id)
    code = fields.Integer(string="Code", required=True, index=True, tracking=True)
    is_principal = fields.Boolean(string="C'est le code principal")
    regulation = fields.Selection(string="Réglementation",
        selection=[
        ('regulated_activity', 'Activité réglementée'),
        ('unauthorized_activity', 'Activité non autorisée'),
        ('none', 'Aucune réglementation'),], default='none')



    # Concaténation du Code et du Nom dans les vues Partner et Company
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id, (record.code and (str(record.code) + ' - ') or '') + record.name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]

        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
