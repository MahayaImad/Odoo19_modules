# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stamp_purchase_account_id = fields.Many2one('account.account',
                                       "Compte achat du timbre fiscal",
                                       config_parameter='l10n_dz_on_timbre_fiscal.stamp_purchase_account_id',)

    stamp_sale_account_id = fields.Many2one('account.account',
                                       "Compte vente du timbre fiscal",
                                       config_parameter='l10n_dz_on_timbre_fiscal.stamp_sale_account_id',)

    default_payment_term_id = fields.Many2one(
        'account.payment.term',
        string="Conditions de paiement par défaut",
        config_parameter='l10n_dz_on_timbre_fiscal.default_payment_term_id',
        help="Définir les conditions de paiement par défaut (ex: Espèce Timbre)"
    )

