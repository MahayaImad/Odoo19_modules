# Copyright 2025 CPSS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CpssCompanyDataConfig(models.Model):
    _name = 'cpss.company.data.config'
    _description = 'Company Data Sharing Configuration'
    _rec_name = 'name'

    name = fields.Char(
        string="Configuration Name",
        default="Company Data Sharing",
        readonly=True
    )

    # Functional Data Sharing Configuration
    share_taxes = fields.Boolean(
        string="Share Taxes",
        default=True,
        help="Share taxes between operational and fiscal companies. "
             "When enabled, taxes will be available in both companies without duplication."
    )

    share_payment_terms = fields.Boolean(
        string="Share Payment Terms",
        default=True,
        help="Share payment terms (including stamp taxes) between companies."
    )

    share_fiscal_positions = fields.Boolean(
        string="Share Fiscal Positions",
        default=True,
        help="Share fiscal positions between companies."
    )

    share_products = fields.Boolean(
        string="Share Products",
        default=True,
        help="Share products and product templates between companies."
    )

    share_partners = fields.Boolean(
        string="Share Partners/Contacts",
        default=True,
        help="Share customer and supplier contacts between companies."
    )

    share_pricelist = fields.Boolean(
        string="Share Pricelists",
        default=False,
        help="Share pricelists between companies."
    )

    # Account Sharing - Note: Chart of Accounts remains company-specific by design
    # but we synchronize/copy them between companies
    sync_chart_of_accounts = fields.Boolean(
        string="Synchronize Chart of Accounts",
        default=True,
        help="Copy chart of accounts from operational to fiscal company. "
             "Accounts remain company-specific for accounting compliance."
    )

    # Statistics
    nb_shared_taxes = fields.Integer(
        string="Shared Taxes",
        compute="_compute_sharing_stats"
    )

    nb_shared_payment_terms = fields.Integer(
        string="Shared Payment Terms",
        compute="_compute_sharing_stats"
    )

    nb_shared_products = fields.Integer(
        string="Shared Products",
        compute="_compute_sharing_stats"
    )

    nb_shared_partners = fields.Integer(
        string="Shared Partners",
        compute="_compute_sharing_stats"
    )

    @api.depends()
    def _compute_sharing_stats(self):
        """Compute statistics about shared data"""
        for record in self:
            # Get sync config to know which companies
            config = self.env['cpss.sync.config'].search([], limit=1)
            if config:
                company_ids = [config.societe_operationnelle_id.id, config.societe_fiscale_id.id]

                # Count shared taxes
                record.nb_shared_taxes = self.env['account.tax'].search_count([
                    ('company_id', '=', False),
                    ('company_ids', 'in', company_ids)
                ])

                # Count shared payment terms
                record.nb_shared_payment_terms = self.env['account.payment.term'].search_count([
                    ('company_id', '=', False)
                ])

                # Count shared products
                record.nb_shared_products = self.env['product.product'].search_count([
                    ('company_id', '=', False),
                    ('company_ids', 'in', company_ids)
                ])

                # Count shared partners
                record.nb_shared_partners = self.env['res.partner'].search_count([
                    ('company_id', '=', False),
                    ('company_ids', 'in', company_ids)
                ])
            else:
                record.nb_shared_taxes = 0
                record.nb_shared_payment_terms = 0
                record.nb_shared_products = 0
                record.nb_shared_partners = 0

    def action_apply_sharing_configuration(self):
        """Apply the sharing configuration to all relevant data"""
        self.ensure_one()

        config = self.env['cpss.sync.config'].search([], limit=1)
        if not config:
            raise UserError(_(
                "Sync configuration not found. "
                "Please configure the sync settings first."
            ))

        company_ids = [config.societe_operationnelle_id.id, config.societe_fiscale_id.id]

        messages = []

        try:
            # Apply tax sharing
            if self.share_taxes:
                count = self._apply_tax_sharing(company_ids)
                messages.append(_("✅ %d taxes shared") % count)
            else:
                messages.append(_("⏭️ Tax sharing skipped (disabled)"))

            # Apply payment terms sharing
            if self.share_payment_terms:
                count = self._apply_payment_terms_sharing(company_ids)
                messages.append(_("✅ %d payment terms shared") % count)
            else:
                messages.append(_("⏭️ Payment terms sharing skipped (disabled)"))

            # Apply products sharing
            if self.share_products:
                count = self._apply_products_sharing(company_ids)
                messages.append(_("✅ %d products shared") % count)
            else:
                messages.append(_("⏭️ Products sharing skipped (disabled)"))

            # Apply partners sharing
            if self.share_partners:
                count = self._apply_partners_sharing(company_ids)
                messages.append(_("✅ %d partners shared") % count)
            else:
                messages.append(_("⏭️ Partners sharing skipped (disabled)"))

            # Apply fiscal positions sharing
            if self.share_fiscal_positions:
                count = self._apply_fiscal_positions_sharing(company_ids)
                messages.append(_("✅ %d fiscal positions shared") % count)
            else:
                messages.append(_("⏭️ Fiscal positions sharing skipped (disabled)"))

            # Apply pricelist sharing
            if self.share_pricelist:
                count = self._apply_pricelist_sharing(company_ids)
                messages.append(_("✅ %d pricelists shared") % count)
            else:
                messages.append(_("⏭️ Pricelist sharing skipped (disabled)"))

            # Synchronize chart of accounts if enabled
            if self.sync_chart_of_accounts:
                config._synchroniser_plans_comptables(config)
                messages.append(_("✅ Chart of accounts synchronized"))
            else:
                messages.append(_("⏭️ Chart of accounts sync skipped (disabled)"))

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('✅ Configuration Applied Successfully'),
                    'message': "\n".join(messages),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error(f"Error applying sharing configuration: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('❌ Error'),
                    'message': _("Error applying configuration: %s") % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def _apply_tax_sharing(self, company_ids):
        """Share taxes between companies"""
        _logger.info("🔄 Applying tax sharing configuration...")

        # Find all taxes in the operational and fiscal companies
        taxes = self.env['account.tax'].sudo().search([
            '|',
            ('company_id', 'in', company_ids),
            ('company_ids', 'in', company_ids)
        ])

        # Group taxes by signature (name, amount, type)
        tax_groups = {}
        for tax in taxes:
            signature = (tax.name, tax.amount, tax.type_tax_use, tax.amount_type)
            if signature not in tax_groups:
                tax_groups[signature] = []
            tax_groups[signature].append(tax)

        shared_count = 0

        # For each group, keep one tax and make it shared
        for signature, group_taxes in tax_groups.items():
            if len(group_taxes) > 1:
                # Keep the first tax, deactivate others
                main_tax = group_taxes[0]
                duplicate_taxes = group_taxes[1:]

                # Make the main tax shared
                main_tax.sudo().write({
                    'company_id': False,
                    'company_ids': [(6, 0, company_ids)]
                })

                # Archive duplicates (don't delete to preserve data integrity)
                for dup_tax in duplicate_taxes:
                    # Check if it's used in any documents
                    usage_count = self.env['account.move.line'].sudo().search_count([
                        ('tax_ids', 'in', [dup_tax.id])
                    ])
                    if usage_count == 0:
                        dup_tax.sudo().active = False

                shared_count += 1
            else:
                # Single tax - just make it shared
                group_taxes[0].sudo().write({
                    'company_id': False,
                    'company_ids': [(6, 0, company_ids)]
                })
                shared_count += 1

        _logger.info(f"✅ Tax sharing applied: {shared_count} taxes shared")
        return shared_count

    def _apply_payment_terms_sharing(self, company_ids):
        """Share payment terms between companies"""
        _logger.info("🔄 Applying payment terms sharing configuration...")

        payment_terms = self.env['account.payment.term'].sudo().search([
            '|',
            ('company_id', 'in', company_ids),
            ('company_id', '=', False)
        ])

        # Group by name
        term_groups = {}
        for term in payment_terms:
            if term.name not in term_groups:
                term_groups[term.name] = []
            term_groups[term.name].append(term)

        shared_count = 0

        for name, group_terms in term_groups.items():
            if len(group_terms) > 1:
                main_term = group_terms[0]
                duplicate_terms = group_terms[1:]

                main_term.sudo().write({'company_id': False})

                for dup_term in duplicate_terms:
                    usage_count = self.env['account.move'].sudo().search_count([
                        ('invoice_payment_term_id', '=', dup_term.id)
                    ])
                    if usage_count == 0:
                        dup_term.sudo().active = False

                shared_count += 1
            else:
                group_terms[0].sudo().write({'company_id': False})
                shared_count += 1

        _logger.info(f"✅ Payment terms sharing applied: {shared_count} terms shared")
        return shared_count

    def _apply_products_sharing(self, company_ids):
        """Share products between companies"""
        _logger.info("🔄 Applying products sharing configuration...")

        products = self.env['product.product'].sudo().search([
            '|',
            ('company_id', 'in', company_ids),
            ('company_ids', 'in', company_ids)
        ])

        for product in products:
            product.sudo().write({
                'company_id': False,
                'company_ids': [(6, 0, company_ids)]
            })

        templates = self.env['product.template'].sudo().search([
            '|',
            ('company_id', 'in', company_ids),
            ('company_ids', 'in', company_ids)
        ])

        for template in templates:
            template.sudo().write({
                'company_id': False,
                'company_ids': [(6, 0, company_ids)]
            })

        _logger.info(f"✅ Products sharing applied: {len(products)} products + {len(templates)} templates shared")
        return len(products)

    def _apply_partners_sharing(self, company_ids):
        """Share partners between companies"""
        _logger.info("🔄 Applying partners sharing configuration...")

        partners = self.env['res.partner'].sudo().search([
            '|',
            ('company_id', 'in', company_ids),
            ('company_ids', 'in', company_ids),
            ('is_company', '=', False)  # Don't share company records
        ])

        for partner in partners:
            partner.sudo().write({
                'company_id': False,
                'company_ids': [(6, 0, company_ids)]
            })

        _logger.info(f"✅ Partners sharing applied: {len(partners)} partners shared")
        return len(partners)

    def _apply_fiscal_positions_sharing(self, company_ids):
        """Share fiscal positions between companies"""
        _logger.info("🔄 Applying fiscal positions sharing configuration...")

        fiscal_positions = self.env['account.fiscal.position'].sudo().search([
            ('company_id', 'in', company_ids)
        ])

        shared_count = 0
        for position in fiscal_positions:
            position.sudo().write({
                'company_id': False
            })
            shared_count += 1

        _logger.info(f"✅ Fiscal positions sharing applied: {shared_count} positions shared")
        return shared_count

    def _apply_pricelist_sharing(self, company_ids):
        """Share pricelists between companies"""
        _logger.info("🔄 Applying pricelist sharing configuration...")

        pricelists = self.env['product.pricelist'].sudo().search([
            ('company_id', 'in', company_ids)
        ])

        shared_count = 0
        for pricelist in pricelists:
            pricelist.sudo().write({
                'company_id': False
            })
            shared_count += 1

        _logger.info(f"✅ Pricelist sharing applied: {shared_count} pricelists shared")
        return shared_count
