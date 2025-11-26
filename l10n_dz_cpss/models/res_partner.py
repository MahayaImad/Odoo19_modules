# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re
from odoo.exceptions import ValidationError
import logging as log

GLOBAL_REGEXEX_NIS_NIF = "^[a-zA-Z0-9]{15}$"
GLOBAL_REGEXEX_AI = "^[a-zA-Z0-9]{11}$"

class ResPartner(models.Model):
    _inherit = 'res.partner'

    activity_code = fields.Many2many("activity.code", string="Code d'activité", index=True)


    fiscal_position = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Position fiscal"
    )

    rc = fields.Char(
        string="N° RC"
    )

    nis = fields.Char(
        string="N.I.S",
    )

    ai = fields.Char(
        string="A.I",
    )

    nif = fields.Char(
        string="N.I.F",
    )

    fax = fields.Char(
        string="Fax"
    )







    @api.model
    def _get_address_format(self):
        for record in self:
            format_adress = ""
            if record.state_id:
                format_adress = "%(street)s\n%(street2)s\n%(zip)s %(city)s (%(state_name)s), %(country_name)s"
            else:
                format_adress = "%(street)s\n%(street2)s\n%(zip)s %(city)s %(state_name)s %(country_name)s"
            return format_adress

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{}".format(record.name)))
        return result
