from . import models


def pre_init_hook(env):
    """
    Pre-installation hook to fix NULL values in res.bank
    before applying NOT NULL constraints.
    """
    import logging
    _logger = logging.getLogger(__name__)

    cr = env.cr

    # Fix NULL country_id values
    _logger.info("Fixing NULL country_id values in res.bank...")
    cr.execute("""
        UPDATE res_bank
        SET country_id = (SELECT id FROM res_country WHERE code = 'DZ' LIMIT 1)
        WHERE country_id IS NULL
    """)
    updated_country = cr.rowcount
    _logger.info(f"Updated {updated_country} banks with default country (DZ)")

    # Fix NULL code values
    _logger.info("Fixing NULL code values in res.bank...")
    cr.execute("""
        UPDATE res_bank
        SET code = COALESCE(
            SUBSTRING(UPPER(REGEXP_REPLACE(name, '[^A-Za-z0-9]', '', 'g')) FROM 1 FOR 5),
            'BANK' || id::text
        )
        WHERE code IS NULL OR code = ''
    """)
    updated_code = cr.rowcount
    _logger.info(f"Updated {updated_code} banks with generated codes")

    _logger.info("✓ Pre-init hook completed successfully")
