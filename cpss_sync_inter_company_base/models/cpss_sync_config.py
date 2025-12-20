# Copyright 2025 CPSS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CpssSyncConfig(models.Model):
    _name = 'cpss.sync.config'
    _description = 'Configuration Synchronisation Inter-Sociétés'
    _rec_name = 'societe_operationnelle_id'
    _check_company_auto = True

    # Configuration de base
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company,
        help="Société à laquelle appartient cette configuration"
    )
    societe_operationnelle_id = fields.Many2one(
        'res.company',
        string="Société Opérationnelle",
        required=True,
        help="Société qui gère toutes les opérations (déclarées et non-déclarées)"
    )
    societe_fiscale_id = fields.Many2one(
        'res.company',
        string="Société Fiscale",
        required=True,
        help="Société qui gère uniquement les opérations déclarées"
    )

    # Utilisateur pour synchronisation (SOLUTION PERMISSIONS)
    utilisateur_intersocietes_id = fields.Many2one(
        'res.users',
        string="Utilisateur Inter-Sociétés",
        required=True,
        help="Utilisateur technique avec accès aux deux sociétés pour la synchronisation"
    )

    # Configuration des notifications
    notifier_erreurs_sync = fields.Boolean(
        string="Notifier les Erreurs",
        default=True,
        help="Envoyer des notifications en cas d'erreur de synchronisation"
    )
    utilisateurs_notification_erreurs = fields.Many2many(
        'res.users',
        string="Utilisateurs à Notifier",
        help="Utilisateurs à notifier en cas d'erreur de synchronisation"
    )

    # Journal par défaut
    journal_fiscal_defaut_id = fields.Many2one(
        'account.journal',
        string="Journal Fiscal par Défaut",
        check_company=False,
        help="Journal par défaut pour les factures fiscales"
    )

    # Champs informatifs (lecture seule)
    nb_contacts_partages = fields.Integer(
        string="Contacts Partagés",
        compute="_compute_donnees_partagees",
        help="Nombre de contacts partagés entre sociétés"
    )
    nb_produits_partages = fields.Integer(
        string="Produits Partagés",
        compute="_compute_donnees_partagees",
        help="Nombre de produits partagés entre sociétés"
    )

    @api.depends()
    def _compute_donnees_partagees(self):
        """Calcule le nombre d'éléments partagés"""
        for config in self:
            config.nb_contacts_partages = self.env['res.partner'].search_count([
                ('company_id', '=', False),
                ('is_company', '=', True)
            ])
            config.nb_produits_partages = self.env['product.product'].search_count([
                ('company_id', '=', False)
            ])

    @api.model
    def get_config(self):
        """Récupère la configuration active"""
        config = self.search([], limit=1)
        if not config:
            raise ValidationError(_(
                "Aucune configuration de synchronisation trouvée. "
                "La configuration automatique a peut-être échoué lors de l'installation."
            ))
        return config

    @api.constrains('societe_operationnelle_id', 'societe_fiscale_id')
    def _check_societes_differentes(self):
        """Les deux sociétés doivent être différentes"""
        for config in self:
            if config.societe_operationnelle_id == config.societe_fiscale_id:
                raise ValidationError(_(
                    "La société opérationnelle et la société fiscale doivent être différentes."
                ))

    @api.constrains('utilisateur_intersocietes_id', 'societe_operationnelle_id', 'societe_fiscale_id')
    def _check_acces_utilisateur(self):
        """L'utilisateur doit avoir accès aux deux sociétés"""
        for config in self:
            if config.utilisateur_intersocietes_id:
                societes_utilisateur = config.utilisateur_intersocietes_id.company_ids
                if (config.societe_operationnelle_id not in societes_utilisateur or
                        config.societe_fiscale_id not in societes_utilisateur):
                    raise ValidationError(_(
                        "L'utilisateur inter-sociétés doit avoir accès aux deux sociétés "
                        "(opérationnelle et fiscale)."
                    ))

    def action_configurer_donnees_partagees(self):
        """Action manuelle pour reconfigurer les données partagées"""
        self.configurer_donnees_partagees()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def configurer_donnees_partagees(self):
        """
        Configure les données pour qu'elles soient partagées entre les sociétés
        en utilisant company_ids (Odoo 19)
        """
        try:
            config = self.search([], limit=1)
            if not config or not config.societe_operationnelle_id or not config.societe_fiscale_id:
                _logger.warning("⚠️  Configuration sync manquante - partage impossible")
                return False

            company_ids = [config.societe_operationnelle_id.id, config.societe_fiscale_id.id]

            # 1. Partners partagés (sauf les sociétés elles-mêmes)
            # Odoo 19: Utilise company_ids pour partage explicite
            partners = self.env['res.partner'].search([
                '|',
                ('company_id', '!=', False),
                ('company_ids', '!=', False),
                ('is_company', '=', False)  # Ne pas partager les sociétés
            ])
            if partners:
                # ✅ Odoo 19: Partage explicite avec company_ids
                partners.write({
                    'company_id': False,  # Rétrocompatibilité
                    'company_ids': [(6, 0, company_ids)]  # Partage explicite
                })
                _logger.info(f"✅ {len(partners)} contacts partagés entre {len(company_ids)} sociétés")

            # 2. Produits partagés
            produits = self.env['product.product'].search([
                '|',
                ('company_id', '!=', False),
                ('company_ids', '!=', False)
            ])
            if produits:
                # ✅ Odoo 19: Partage explicite avec company_ids
                produits.write({
                    'company_id': False,  # Rétrocompatibilité
                    'company_ids': [(6, 0, company_ids)]  # Partage explicite
                })
                _logger.info(f"✅ {len(produits)} produits partagés entre {len(company_ids)} sociétés")

            # 3. Templates de produits partagés
            templates = self.env['product.template'].search([
                '|',
                ('company_id', '!=', False),
                ('company_ids', '!=', False)
            ])
            if templates:
                templates.write({
                    'company_id': False,
                    'company_ids': [(6, 0, company_ids)]
                })
                _logger.info(f"✅ {len(templates)} templates produits partagés")

            # 4. IMPORTANT : Ne PAS partager les comptes et taxes
            # Ils doivent rester spécifiques à chaque société pour la conformité comptable
            # Le mapping sera fait automatiquement lors de la synchronisation

            _logger.info("🎯 Configuration des données partagées terminée avec succès (Odoo 19)")
            _logger.info(f"   Sociétés : {config.societe_operationnelle_id.name} ↔ {config.societe_fiscale_id.name}")
            _logger.info("⚠️  Les comptes et taxes restent spécifiques par société (mapping automatique)")
            return True

        except Exception as e:
            _logger.error(f"❌ Erreur lors de la configuration des données partagées : {str(e)}")
            return False

    def action_test_synchronisation(self):
        """Test de la configuration de synchronisation"""
        try:
            # Vérifications de base
            if not self.utilisateur_intersocietes_id:
                raise ValidationError(_("Utilisateur inter-sociétés non défini"))

            if not self.journal_fiscal_defaut_id:
                raise ValidationError(_("Journal fiscal par défaut non défini"))

            # Test d'accès aux sociétés
            self.env['account.move'].with_user(self.utilisateur_intersocietes_id).check_access_rights('read')

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Test Réussi"),
                    'message': _("La configuration de synchronisation est fonctionnelle !"),
                    'type': 'success',
                }
            }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Test Échoué"),
                    'message': _("Erreur de configuration : %s") % str(e),
                    'type': 'danger',
                }
            }