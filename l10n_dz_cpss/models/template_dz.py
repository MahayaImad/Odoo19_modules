# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.exceptions import UserError
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
                'account_sale_tax_id': 'l10n_dz_vat_sale_19_prod',
                'account_purchase_tax_id': 'l10n_dz_vat_purchase_19',
            },
        }

    def _load_data(self, template_code, company, install_demo):
        """Override to configure default accounts after chart is loaded"""
        res = super()._load_data(template_code, company, install_demo)

        if template_code == 'dz_cpss':
            print("fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
            self._configure_dz_default_accounts(company)

        return res

    def _configure_dz_default_accounts(self, company):
        """Configure default accounts for Algerian chart of accounts"""

        company = company.ensure_one()

        if not company.id:
            raise UserError("Company not yet created; cannot configure accounts.")

        # Find accounts by code
        accounts = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('code', 'in', ['766', '666', '758', '657', '413', '411100', '401310',
                           '700000', '701000', '600000', '601000', '355000', '380000',
                           '709', '609'])
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

        # Comptes d'escompte
        if '709' in account_map:
            vals['account_journal_early_pay_discount_loss_account_id'] = account_map['709']
        if '609' in account_map:
            vals['account_journal_early_pay_discount_gain_account_id'] = account_map['609']

        # Taxes par défaut
        if tax_sale:
            vals['account_sale_tax_id'] = tax_sale.id
        if tax_purchase:
            vals['account_purchase_tax_id'] = tax_purchase.id

        if vals:
            company.write(vals)

        # Configure default accounts on product categories
        self._configure_product_categories(company, account_map, tax_sale, tax_purchase)

        # Configure default partner accounts
        self._configure_partner_accounts(company, account_map)

    def _configure_product_categories(self, company, account_map, tax_sale, tax_purchase):
        """Configure default income/expense accounts on product categories"""

        # Get the "All" product category (parent of all categories)
        ProductCategory = self.env['product.category']
        all_category = ProductCategory.search([
            '|', ('parent_id', '=', False),
            ('name', '=', 'All')
        ], limit=1)

        if not all_category:
            # Create root category if it doesn't exist
            all_category = ProductCategory.create({
                'name': 'All',
                'parent_id': False,
            })

        # Set default accounts on the root category
        category_vals = {}

        # Default income account (Sales of goods)
        if '700000' in account_map:
            category_vals['property_account_income_categ_id'] = account_map['700000']

        # Default expense account (Purchase of goods)
        if '600000' in account_map:
            category_vals['property_account_expense_categ_id'] = account_map['600000']

        # Default stock accounts
        if '355000' in account_map:
            category_vals['property_stock_account_output_categ_id'] = account_map['355000']
        if '380000' in account_map:
            category_vals['property_stock_account_input_categ_id'] = account_map['380000']

        # Stock valuation account (finished products)
        if '355000' in account_map:
            category_vals['property_stock_valuation_account_id'] = account_map['355000']

        if category_vals:
            all_category.write(category_vals)

    def _configure_partner_accounts(self, company, account_map):
        """Configure default receivable/payable accounts for partners"""

        # Set default accounts at company level for new partners
        partner_vals = {}

        # Default receivable account (Clients)
        if '411100' in account_map:
            partner_vals['account_receivable_id'] = account_map['411100']

        # Default payable account (Fournisseurs)
        if '401310' in account_map:
            partner_vals['account_payable_id'] = account_map['401310']

        if partner_vals:
            # Set properties for the company
            for field_name, account_id in partner_vals.items():
                self.env['ir.property']._set_default(
                    field_name,
                    'res.partner',
                    account_id,
                    company
                )

