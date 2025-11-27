from odoo import models, fields, api
from odoo.osv import expression
import logging


class ActivityCode(models.Model):
    _name = "activity.code"
    _description = "Code d'activité"

    name = fields.Char(string="Nom", required=True, index=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company.id)
    code = fields.Integer(string="Code", required=True, index=True)
    is_principal = fields.Boolean(string="C'est le code principal")
    regulation = fields.Selection(
        string="Réglementation",
        selection=[
            ('regulated_activity', 'Activité réglementée'),
            ('unauthorized_activity', 'Activité non autorisée'),
            ('none', 'Aucune réglementation'),
        ],
        default='none'
    )

    def _valid_field_parameter(self, field, name):
        # Autoriser le paramètre tracking même s'il n'est pas utilisé
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code, company_id)', 'Le code d\'activité doit être unique par société !'),
    ]

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}" if record.code else record.name
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []

        domain = args[:]
        if name:
            domain += ['|', ('name', operator, name), ('code', operator, name)]

        return self.search(domain, limit=limit).name_get()