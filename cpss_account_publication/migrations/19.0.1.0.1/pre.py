# -*- coding: utf-8 -*-
"""
Migration script pour ajouter les colonnes manquantes à res_company
avant le chargement du module
"""

import logging

_logger = logging.getLogger(__name__)


def _column_exists(cr, table_name, column_name):
    """Vérifie si une colonne existe dans une table"""
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name=%s AND column_name=%s
    """, (table_name, column_name))
    return bool(cr.fetchone())


def migrate(cr, version):
    """
    Ajoute les colonnes manquantes à res_company si elles n'existent pas déjà
    """
    _logger.info("Running pre-migration for cpss_account_publication 19.0.1.0.1")

    # Liste des colonnes à ajouter
    columns_to_add = [
        ('journal_publication_id', 'INTEGER'),
        ('publication_sequence_id', 'INTEGER'),
        ('enable_publication_stock_tracking', 'BOOLEAN DEFAULT FALSE'),
    ]

    for column_name, column_type in columns_to_add:
        if not _column_exists(cr, 'res_company', column_name):
            _logger.info(f"Adding column {column_name} to res_company")
            cr.execute(f"""
                ALTER TABLE res_company
                ADD COLUMN {column_name} {column_type}
            """)
        else:
            _logger.info(f"Column {column_name} already exists in res_company")

    _logger.info("Pre-migration completed successfully")
