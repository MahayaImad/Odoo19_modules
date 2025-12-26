# Copyright 2025 CPSS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Champs de configuration sync stockés au niveau société
    sync_societe_operationnelle_id = fields.Many2one(
        'res.company',
        string="Société Opérationnelle",
        help="Société qui gère toutes les opérations"
    )

    sync_societe_fiscale_id = fields.Many2one(
        'res.company',
        string="Service Comptabilité",
        help="Société qui gère uniquement les opérations déclarées"
    )

    sync_utilisateur_intersocietes_id = fields.Many2one(
        'res.users',
        string="Utilisateur Technique Inter-Sociétés",
        help="Utilisateur avec accès aux deux sociétés pour la synchronisation"
    )

    sync_journal_fiscal_defaut_id = fields.Many2one(
        'account.journal',
        string="Journal Fiscal par Défaut"
    )

    sync_notifier_erreurs = fields.Boolean(
        string="Notifier les Erreurs de Sync",
        default=True
    )

    sync_utilisateurs_notification_ids = fields.Many2many(
        'res.users',
        'company_sync_notification_users_rel',
        'company_id',
        'user_id',
        string="Utilisateurs à Notifier"
    )

    # Navbar Color Customization
    navbar_color = fields.Char(
        string='Navbar Background Color',
        help='Navbar background color for this company (hex code, e.g., #1f2937). '
             'If not set, uses primary_color or default color.',
        default='#1f2937'
    )

    navbar_text_color = fields.Char(
        string='Navbar Text Color',
        help='Navbar text color for this company (hex code, e.g., #ffffff). '
             'If not set, uses white color.',
        default='#ffffff'
    )

    use_navbar_color = fields.Boolean(
        string='Use Custom Navbar Color',
        default=False,
        help='Enable custom navbar color for this company. Helps distinguish between companies visually.'
    )

    is_fiscal_company = fields.Boolean(
        string='Is Service Comptabilité',
        compute='_compute_is_fiscal_company',
        store=False,
        help='Indicates if this company is configured as a service comptabilité in sync settings'
    )

    @api.depends('id')
    def _compute_is_fiscal_company(self):
        """Determine if this company is a service comptabilité"""
        for company in self:
            # Check if this company is set as service comptabilité in any sync config
            config = self.env['cpss.sync.config'].sudo().search([
                ('societe_fiscale_id', '=', company.id)
            ], limit=1)
            company.is_fiscal_company = bool(config)

    def action_configure_navbar_colors(self):
        """
        Auto-configure navbar colors based on company type:
        - Operational company: Default Odoo color (no custom color)
        - Service Comptabilité: Distinctive color (orange) to warn users
        """
        self.ensure_one()

        config = self.env['cpss.sync.config'].sudo().search([], limit=1)
        if not config:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Configuration Required',
                    'message': 'Please configure sync settings first (operational company and accounting service).',
                    'type': 'warning',
                }
            }

        # Check if this is the service comptabilité
        if self == config.societe_fiscale_id:
            # Service Comptabilité: Distinctive orange color
            self.write({
                'use_navbar_color': True,
                'navbar_color': '#ea580c',  # Orange
                'navbar_text_color': '#ffffff',
            })
            message = f'✅ Service Comptabilité navbar configured with distinctive orange color'
        elif self == config.societe_operationnelle_id:
            # Operational company: Default Odoo color (disable custom color)
            self.write({
                'use_navbar_color': False,
                'navbar_color': '#1f2937',
                'navbar_text_color': '#ffffff',
            })
            message = f'✅ Operational company navbar set to default Odoo color'
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Not Configured',
                    'message': 'This company is not configured as operational or service comptabilité.',
                    'type': 'info',
                }
            }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Navbar Colors Configured',
                'message': message,
                'type': 'success',
            }
        }

    @api.model
    def get_navbar_colors(self, company_id=None):
        """
        Get navbar colors for a specific company.
        Returns dict with background and text colors.

        Strategy:
        - Operational company: Default Odoo color (use_navbar_color = False)
        - Service Comptabilité: Custom distinctive color (use_navbar_color = True)
        """
        if not company_id:
            company_id = self.env.company.id

        company = self.browse(company_id)

        # Only use custom colors if explicitly enabled
        if company.use_navbar_color and company.navbar_color:
            return {
                'navbar_bg': company.navbar_color,
                'navbar_text': company.navbar_text_color or '#ffffff',
                'use_custom': True
            }
        elif company.use_navbar_color and company.primary_color:
            # Fallback to primary color if custom navbar color not set but enabled
            return {
                'navbar_bg': company.primary_color,
                'navbar_text': company.navbar_text_color or '#ffffff',
                'use_custom': True
            }
        else:
            # Default Odoo navbar color (operational company default)
            return {
                'navbar_bg': '#1f2937',  # Default Odoo navbar color
                'navbar_text': '#ffffff',
                'use_custom': False
            }
