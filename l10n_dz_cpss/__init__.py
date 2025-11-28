# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import models


def post_init_hook(env):
    """
    Hook appelé après l'installation du module
    S'assure que le template est bien enregistré et configure le compte equity_unaffected
    """
    import logging
    _logger = logging.getLogger(__name__)

    # Forcer le rechargement du template
    env['account.chart.template'].flush_model()

    # Gérer le compte equity_unaffected (120000 au lieu de 999999)
    # Rechercher et supprimer le compte 999999 auto-généré par Odoo s'il existe
    account_999999 = env['account.account'].search([
        ('code', '=', '999999'),
        ('account_type', '=', 'equity_unaffected')
    ], limit=1)

    if account_999999:
        _logger.info("Suppression du compte 999999 auto-généré")
        # Vérifier qu'il n'y a pas d'écritures sur ce compte avant de le supprimer
        if not env['account.move.line'].search_count([('account_id', '=', account_999999.id)]):
            account_999999.unlink()
            _logger.info("Compte 999999 supprimé avec succès")
        else:
            _logger.warning("Impossible de supprimer le compte 999999 car il contient des écritures")

    # Vérifier que le compte 120000 existe et est bien de type equity_unaffected
    account_120000 = env.ref('l10n_dz_cpss.l10n_dz_120000', raise_if_not_found=False)
    if account_120000:
        if account_120000.account_type != 'equity_unaffected':
            account_120000.account_type = 'equity_unaffected'
            _logger.info("Compte 120000 configuré comme equity_unaffected")

    _logger.info("=" * 70)
    _logger.info("l10n_dz_cpss: post_init_hook appelé")
    _logger.info("Template 'dz_cpss' enregistré pour le plan comptable algérien")
    _logger.info("=" * 70)
