# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Hook appelé après l'installation du module
    Configure automatiquement le compte FNDIA 441000 s'il existe
    """
    _logger.info("=" * 80)
    _logger.info("Configuration post-installation du module cpss_agro_invoice")
    _logger.info("=" * 80)

    # Configurer le compte FNDIA pour toutes les sociétés
    companies = env['res.company'].search([])
    companies._auto_configure_fndia_account()

    _logger.info("=" * 80)
    _logger.info("Configuration terminée")
    _logger.info("=" * 80)
