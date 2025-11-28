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
                # Comptes de change
                'income_currency_exchange_account_id': 'l10n_dz_766',
                'expense_currency_exchange_account_id': 'l10n_dz_666',
                # Comptes de suspension et paiements
                'account_journal_suspense_account_id': 'l10n_dz_512001',
                'account_journal_payment_debit_account_id': 'l10n_dz_512002',
                'account_journal_payment_credit_account_id': 'l10n_dz_512003',
                # Comptes d'escomptes (early payment discounts)
                'account_journal_early_pay_discount_gain_account_id': 'l10n_dz_999997',
                'account_journal_early_pay_discount_loss_account_id': 'l10n_dz_999998',
                # Comptes de différence de caisse
                'default_cash_difference_income_account_id': 'l10n_dz_758',
                'default_cash_difference_expense_account_id': 'l10n_dz_657',
                # Compte de créances POS
                'account_default_pos_receivable_account_id': 'l10n_dz_413',
                # Taxes par défaut
                'account_sale_tax_id': 'l10n_dz_vat_sale_19_prod',
                'account_purchase_tax_id': 'l10n_dz_vat_purchase_19',
            },
        }
