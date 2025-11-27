from odoo import models, fields, api

class FormeJuridique(models.Model):
    _name = "forme.juridique"
    _description = "Forme juridique"
    _order = "name"

    name = fields.Char(string="Forme juridique", required=True, index=True)
    code = fields.Char(string="Code", index=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company.id)

    def _valid_field_parameter(self, field, name):
        # Autoriser le paramètre tracking même s'il n'est pas utilisé
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code, company_id)', 'Le code de forme juridique doit être unique par société !'),
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