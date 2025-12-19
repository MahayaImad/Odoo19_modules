# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FormeJuridique(models.Model):
    _name = 'forme.juridique'
    _description = 'Forme Juridique'

    name = fields.Char(
        string="Nom",
        required=True
    )

    code = fields.Char(
        string="Code"
    )

    # Concaténation du Code et du Nom dans les vues Partner et Company
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id, (record.code and (record.code + ' - ') or '') + record.name))
        return result
