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
        string="Société Fiscale",
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

    @api.model
    def get_navbar_colors(self, company_id=None):
        """
        Get navbar colors for a specific company.
        Returns dict with background and text colors.
        """
        if not company_id:
            company_id = self.env.company.id

        company = self.browse(company_id)

        if company.use_navbar_color and company.navbar_color:
            return {
                'navbar_bg': company.navbar_color,
                'navbar_text': company.navbar_text_color or '#ffffff',
                'use_custom': True
            }
        elif company.primary_color:
            # Fallback to primary color if custom navbar color not set
            return {
                'navbar_bg': company.primary_color,
                'navbar_text': company.navbar_text_color or '#ffffff',
                'use_custom': True
            }
        else:
            return {
                'navbar_bg': '#1f2937',  # Default Odoo navbar color
                'navbar_text': '#ffffff',
                'use_custom': False
            }
