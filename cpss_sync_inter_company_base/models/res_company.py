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
