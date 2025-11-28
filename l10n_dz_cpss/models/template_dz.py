# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('dz_cpss')
    def _get_dz_template_data(self):
        return {
            'name': 'Plan Comptable Algérien CPSS',
            'code_digits': 6,
            'display_invoice_amount_total_words': True,
        }

    @template('dz_cpss', 'res.company')
    def _get_dz_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.dz',
                'bank_account_code_prefix': '512',
                'cash_account_code_prefix': '53',
                'transfer_account_code_prefix': '58',
            },
        }
