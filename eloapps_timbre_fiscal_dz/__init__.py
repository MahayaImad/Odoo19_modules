from . import models
from odoo import api
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Initialiser les paramètres de timbre fiscal après installation"""

    company = env.company

    if not company.sale_timbre:
        # Rechercher le compte comptable de vente du timbre
        account_id = env['account.account'].search([('code', '=', '445750')], limit=1).id

        # Mise à jour des paramètres (seulement les champs existants)
        company.write({
            'tranche': 100.0,
            'prix': 1.0,
            'mnt_min': 500.0,
            'mnt_max': 1000000.0,
            'sale_timbre': account_id,
            'montant_en_lettre': True,
        })

        _logger.info(f"Configuration timbre fiscal initialisée pour {company.name}")