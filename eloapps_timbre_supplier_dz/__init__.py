from . import models
from odoo import api
import logging

_logger = logging.getLogger(__name__)


def post_init_hook_t(env):
    """Initialiser le compte d'achat pour le timbre fiscal"""

    company = env.company

    if not company.purchase_offset_account:

        account_timbr = env['account.account'].search([('code', '=', '645700')], limit=1).id

        if account_timbr:
            company.write({
                'purchase_offset_account': account_timbr,
            })
            _logger.info(f"Compte d'achat timbre configuré pour {company.name}")
        else:
            _logger.warning(f"Compte 645700 introuvable pour l'entreprise {company.name}")