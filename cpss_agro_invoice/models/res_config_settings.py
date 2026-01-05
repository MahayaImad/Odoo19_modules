# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA (créance sur l'État). "
             "Utilisez le compte 441000 - État et autres collectivités publiques, subventions à recevoir",
        domain="[('account_type', 'in', ['asset_current', 'asset_receivable'])]",
        check_company=True
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
