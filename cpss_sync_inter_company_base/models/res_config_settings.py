# Copyright 2025 CPSS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Synchronisation Inter-Sociétés
    sync_societe_operationnelle_id = fields.Many2one(
        'res.company',
        string="Société Opérationnelle",
        related='company_id.sync_societe_operationnelle_id',
        readonly=False,
        help="Société qui gère toutes les opérations"
    )

    sync_societe_fiscale_id = fields.Many2one(
        'res.company',
        string="Service Comptabilité",
        related='company_id.sync_societe_fiscale_id',
        readonly=False,
        help="Société qui gère uniquement les opérations déclarées"
    )

    sync_utilisateur_intersocietes_id = fields.Many2one(
        'res.users',
        string="Utilisateur Technique",
        related='company_id.sync_utilisateur_intersocietes_id',
        readonly=False,
        help="Utilisateur avec accès aux deux sociétés"
    )

    sync_journal_fiscal_defaut_id = fields.Many2one(
        'account.journal',
        string="Journal Comptable par Défaut",
        related='company_id.sync_journal_fiscal_defaut_id',
        readonly=False,
        domain="[('company_id', '=', sync_societe_fiscale_id)]"
    )

    sync_notifier_erreurs = fields.Boolean(
        string="Notifier les Erreurs",
        related='company_id.sync_notifier_erreurs',
        readonly=False,
        default=True
    )

    sync_utilisateurs_notification_ids = fields.Many2many(
        'res.users',
        string="Utilisateurs à Notifier",
        related='company_id.sync_utilisateurs_notification_ids',
        readonly=False
    )

    # Statistiques (lecture seule)
    sync_nb_contacts_partages = fields.Integer(
        string="Contacts Partagés",
        compute="_compute_sync_stats"
    )

    sync_nb_produits_partages = fields.Integer(
        string="Produits Partagés",
        compute="_compute_sync_stats"
    )

    @api.depends()
    def _compute_sync_stats(self):
        """Calcule les statistiques de partage"""
        for record in self:
            record.sync_nb_contacts_partages = self.env['res.partner'].search_count([
                ('company_id', '=', False),
                ('is_company', '=', False)
            ])
            record.sync_nb_produits_partages = self.env['product.product'].search_count([
                ('company_id', '=', False)
            ])

    # def set_values(self):
    #     """Override pour assigner les menus lors de la sauvegarde"""
    #     res = super(ResConfigSettings, self).set_values()
    #
    #     # Synchroniser avec cpss.sync.config
    #     self._onchange_sync_config()
    #
    #     # ✅ ASSIGNER LES MENUS À LA SOCIÉTÉ OPÉRATIONNELLE
    #     if self.sync_societe_operationnelle_id and self.sync_societe_fiscale_id:
    #         self._assigner_menus_a_societe_operationnelle()
    #
    #     return res

    def action_configurer_donnees_partagees(self):
        """Configure les données partagées entre sociétés"""
        config = self.env['cpss.sync.config'].search([], limit=1)
        if config:
            config.configurer_donnees_partagees()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuration Terminée'),
                'message': _('Les données ont été configurées comme partagées entre les sociétés.'),
                'type': 'success',
            }
        }

    def action_test_synchronisation(self):
        """Test de la configuration"""
        try:
            config = self.env['cpss.sync.config'].search([], limit=1)
            if not config:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Erreur'),
                        'message': _('Configuration de synchronisation non trouvée.'),
                        'type': 'danger',
                    }
                }

            return config.action_test_synchronisation()

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test Échoué'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    def action_synchroniser_plans_comptables(self):
        """Synchronise les plans comptables entre les sociétés"""
        try:
            config = self.env['cpss.sync.config'].search([], limit=1)
            if not config:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('❌ Erreur'),
                        'message': _('Configuration de synchronisation non trouvée.'),
                        'type': 'danger',
                    }
                }

            # Lancer la synchronisation
            config._synchroniser_plans_comptables(config)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('✅ Synchronisation Terminée'),
                    'message': _(
                        'Les plans comptables ont été synchronisés.\n\n'
                        'Tous les comptes de %s ont été copiés vers %s.\n\n'
                        'Vous pouvez maintenant partager vos factures!'
                    ) % (
                        config.societe_operationnelle_id.name,
                        config.societe_fiscale_id.name
                    ),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('❌ Synchronisation Échouée'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    @api.onchange('sync_societe_operationnelle_id', 'sync_societe_fiscale_id',
                  'sync_utilisateur_intersocietes_id', 'sync_journal_fiscal_defaut_id',
                  'sync_notifier_erreurs', 'sync_utilisateurs_notification_ids')
    def _onchange_sync_config(self):
        """Synchronise avec cpss.sync.config"""
        config = self.env['cpss.sync.config'].search([], limit=1)
        if config:
            vals = {}
            if self.sync_societe_operationnelle_id:
                vals['societe_operationnelle_id'] = self.sync_societe_operationnelle_id.id
            if self.sync_societe_fiscale_id:
                vals['societe_fiscale_id'] = self.sync_societe_fiscale_id.id
            if self.sync_utilisateur_intersocietes_id:
                vals['utilisateur_intersocietes_id'] = self.sync_utilisateur_intersocietes_id.id
            if self.sync_journal_fiscal_defaut_id:
                vals['journal_fiscal_defaut_id'] = self.sync_journal_fiscal_defaut_id.id

            vals['notifier_erreurs_sync'] = self.sync_notifier_erreurs

            if self.sync_utilisateurs_notification_ids:
                vals['utilisateurs_notification_erreurs'] = [(6, 0, self.sync_utilisateurs_notification_ids.ids)]

            if vals:
                config.write(vals)
