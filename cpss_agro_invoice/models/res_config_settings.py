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
             "Utilisez le compte 441100 - État, Subventions FNDIA à recevoir",
        domain="[('account_type', 'in', ['asset_current', 'asset_receivable'])]",
        check_company=True
    )

    def _setup_fndia_account_on_install(self):
        """
        Configuration du compte FNDIA lors de l'installation
        Crée le compte 441100 s'il n'existe pas, ou le configure s'il existe déjà
        """
        for company in self:
            # Chercher le compte 441100
            account_441100 = self.env['account.account'].search([
                ('code', '=', '441100'),
                ('company_id', '=', company.id)
            ], limit=1)

            # Si le compte n'existe pas, le créer
            if not account_441100:
                _logger.info("Création du compte 441100 - État, Subventions FNDIA à recevoir")
                account_441100 = self.env['account.account'].create({
                    'name': 'État - Subventions FNDIA à recevoir',
                    'code': '441100',
                    'account_type': 'asset_current',
                    'reconcile': True,
                    'company_id': company.id,
                    'note': 'Compte utilisé pour enregistrer les subventions FNDIA sur les factures de vente d\'engrais (créance sur le Fonds National de Développement de l\'Investissement Agricole)'
                })
                _logger.info(f"✓ Compte 441100 créé avec succès (ID: {account_441100.id})")
            else:
                _logger.info(f"✓ Compte 441100 existe déjà (ID: {account_441100.id}, Type: {account_441100.account_type})")

                # Vérifier que le type est correct
                if account_441100.account_type != 'asset_current':
                    _logger.warning(f"⚠ ATTENTION: Le compte 441100 est de type '{account_441100.account_type}' au lieu de 'asset_current'")
                    _logger.warning("⚠ Cela peut causer des erreurs. Changez manuellement le type à 'asset_current'")

            # Configurer le compte FNDIA pour la société
            if not company.fndia_subsidy_account_id:
                company.fndia_subsidy_account_id = account_441100.id
                _logger.info(f"✓ Compte FNDIA configuré pour la société: {account_441100.code} - {account_441100.name}")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        related='company_id.fndia_subsidy_account_id',
        readonly=False,
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA"
    )
