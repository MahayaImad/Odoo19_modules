# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    num_agrement = fields.Char(
        string="Numéro d'agrément",
        help="Numéro d'agrément"
    )
