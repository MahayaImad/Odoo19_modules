# -*- coding: utf-8 -*-

from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA (créance sur l'État). "
             "Compte recommandé : 441200 - Subventions d'exploitation à recevoir",
        domain="[('account_type', 'in', ['asset_current', 'asset_receivable'])]",
        check_company=True
    )

    def _setup_fndia_account_on_install(self):
        """
        Configuration du compte FNDIA lors de l'installation
        Utilise le compte 441200 (Subventions d'exploitation à recevoir)
        """
        for company in self:
            # Chercher le compte 441200 (Subventions d'exploitation à recevoir)
            account_441200 = self.env['account.account'].search([
                ('code', '=', '441200'),
                ('company_id', '=', company.id)
            ], limit=1)

            if account_441200:
                _logger.info(f"✓ Compte 441200 trouvé (Type actuel: {account_441200.account_type})")

                # Vérifier et CORRIGER le type si nécessaire
                if account_441200.account_type != 'asset_current':
                    _logger.warning(f"⚠ ATTENTION: Le compte 441200 est de type '{account_441200.account_type}'")
                    _logger.warning("⚠ CORRECTION: Changement du type à 'asset_current' (actif circulant)")

                    try:
                        account_441200.write({'account_type': 'asset_current'})
                        _logger.info("✓ Type du compte 441200 corrigé → asset_current")
                    except Exception as e:
                        _logger.error(f"✗ Impossible de corriger le type automatiquement: {e}")
                        _logger.error("→ Changez MANUELLEMENT le type du compte 441200 à 'Actif circulant'")

                # Configurer comme compte FNDIA
                if not company.fndia_subsidy_account_id:
                    company.fndia_subsidy_account_id = account_441200.id
                    _logger.info(f"✓ Compte FNDIA configuré: {account_441200.code} - {account_441200.name}")
            else:
                _logger.error("✗ Compte 441200 non trouvé dans le plan comptable")
                _logger.error("→ Veuillez configurer manuellement le compte FNDIA dans les paramètres")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        related='company_id.fndia_subsidy_account_id',
        readonly=False,
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA"
    )
