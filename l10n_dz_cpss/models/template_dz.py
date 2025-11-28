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

    def _load_data(self, template_code, company, install_demo):
        """Override to configure default accounts after chart is loaded"""
        res = super()._load_data(template_code, company, install_demo)

        if template_code == 'dz_cpss':
            self._configure_dz_default_accounts(company)

        return res

    def _configure_dz_default_accounts(self, company):
        """Configure default accounts for Algerian chart of accounts"""
        # Find accounts by code
        accounts = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('code', 'in', ['766', '666', '758', '657', '413'])
        ])

        account_map = {acc.code: acc.id for acc in accounts}

        # Find taxes by external ID
        tax_sale = self.env.ref('l10n_dz_cpss.l10n_dz_vat_sale_19_prod', raise_if_not_found=False)
        tax_purchase = self.env.ref('l10n_dz_cpss.l10n_dz_vat_purchase_19', raise_if_not_found=False)

        vals = {}

        # Comptes de change
        if '766' in account_map:
            vals['income_currency_exchange_account_id'] = account_map['766']
        if '666' in account_map:
            vals['expense_currency_exchange_account_id'] = account_map['666']

        # Comptes de différence de caisse
        if '758' in account_map:
            vals['default_cash_difference_income_account_id'] = account_map['758']
        if '657' in account_map:
            vals['default_cash_difference_expense_account_id'] = account_map['657']

        # Compte de créances POS
        if '413' in account_map:
            vals['account_default_pos_receivable_account_id'] = account_map['413']

        # Taxes par défaut
        if tax_sale:
            vals['account_sale_tax_id'] = tax_sale.id
        if tax_purchase:
            vals['account_purchase_tax_id'] = tax_purchase.id

        if vals:
            company.write(vals)

