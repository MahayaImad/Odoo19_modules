# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import models


def post_init_hook(env):
    """
    Hook appelé après l'installation du module
    S'assure que le template est bien enregistré
    """
    # Forcer le rechargement du template
    env['account.chart.template'].flush_model()

    # Log pour confirmer que le hook a été appelé
    import logging
    _logger = logging.getLogger(__name__)
    _logger.info("=" * 70)
    _logger.info("l10n_dz_cpss: post_init_hook appelé")
    _logger.info("Template 'dz' enregistré pour le plan comptable algérien")
    _logger.info("=" * 70)
