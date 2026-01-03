# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA",
        domain="[('account_type', '=', 'asset_receivable'), ('company_id', '=', id)]"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        related='company_id.fndia_subsidy_account_id',
        readonly=False,
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA"
    )
