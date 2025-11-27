from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
import logging as log

GLOBAL_REGEXEX_NIS_NIF = "^[a-zA-Z0-9]{15}$"
GLOBAL_REGEXEX_AI = "^[a-zA-Z0-9]{11}$"


class ResPartner(models.Model):
    _inherit = 'res.partner'

    activity_code = fields.Many2many("activity.code", string="Code d'activité", index=True)
    fiscal_position = fields.Many2one('account.fiscal.position', string="Position fiscal")

    # Informations fiscales algériennes
    rc = fields.Char(string="N° RC")
    nis = fields.Char(string="N.I.S")
    ai = fields.Char(string="A.I")
    nif = fields.Char(string="N.I.F")
    fax = fields.Char(string="Fax", size=64)

    @api.constrains('nis')
    def _check_nis(self):
        for record in self:
            if record.nis and not re.match(GLOBAL_REGEXEX_NIS_NIF, record.nis):
                raise ValidationError(_("Le format du N.I.S doit être de 15 caractères alphanumériques."))

    @api.constrains('nif')
    def _check_nif(self):
        for record in self:
            if record.nif and not re.match(GLOBAL_REGEXEX_NIS_NIF, record.nif):
                raise ValidationError(_("Le format du N.I.F doit être de 15 caractères alphanumériques."))

    @api.constrains('ai')
    def _check_ai(self):
        for record in self:
            if record.ai and not re.match(GLOBAL_REGEXEX_AI, record.ai):
                raise ValidationError(_("Le format de l'A.I doit être de 11 caractères alphanumériques."))

    @api.model
    def _get_address_format(self):
        for record in self:
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