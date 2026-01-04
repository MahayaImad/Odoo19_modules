# -*- coding: utf-8 -*-

from odoo import fields, models, api


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
        help="Définir les conditions de paiement par défaut (ex: Espèce Timbre)"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        payment_term_id = param.get_param('l10n_dz_on_timbre_fiscal.default_payment_term_id')
        res.update(
            default_payment_term_id=int(payment_term_id) if payment_term_id else False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('l10n_dz_on_timbre_fiscal.default_payment_term_id',
                       self.default_payment_term_id.id if self.default_payment_term_id else False)


