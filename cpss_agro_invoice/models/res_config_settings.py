# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA (créance sur l'État)",
        domain="[('account_type', 'in', ['asset_current', 'asset_receivable'])]",
        check_company=True
    )

    def _auto_configure_fndia_account(self):
        """Configure automatiquement le compte FNDIA 441000 s'il existe"""
        for company in self:
            if not company.fndia_subsidy_account_id:
                # Chercher le compte 441000 (État, subventions à recevoir)
                account_441000 = self.env['account.account'].search([
                    ('code', '=', '441000'),
                    ('company_id', '=', company.id)
                ], limit=1)

                if account_441000:
                    company.fndia_subsidy_account_id = account_441000.id
                    _logger.info(f"✓ Compte FNDIA configuré automatiquement: {account_441000.code} - {account_441000.name}")
                else:
                    _logger.warning("⚠ Compte 441000 non trouvé. Configurez manuellement le compte FNDIA dans les paramètres.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fndia_subsidy_account_id = fields.Many2one(
        'account.account',
        related='company_id.fndia_subsidy_account_id',
        readonly=False,
        string="Compte de Subvention FNDIA",
        help="Compte comptable utilisé pour enregistrer les subventions FNDIA"
    )
