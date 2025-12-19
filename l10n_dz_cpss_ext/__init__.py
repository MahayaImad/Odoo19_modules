# -*- coding: utf-8 -*-

from . import models


def post_init_hook(env):
    """
    Post-installation hook to load accounts only if they don't already exist.
    This prevents "duplicate code" errors when accounts were created by
    a previous module installation (e.g., l10n_dz_cpss).
    """
    import csv
    import os
    import logging
    from odoo.modules import get_module_path

    _logger = logging.getLogger(__name__)

    # Get the CSV file path
    module_path = get_module_path('l10n_dz_cpss_ext')
    csv_path = os.path.join(module_path, 'data', 'template', 'account.account-dz.csv')

    if not os.path.exists(csv_path):
        _logger.warning("Account CSV file not found at: %s", csv_path)
        return

    _logger.info("Loading additional accounts from CSV...")

    # Read accounts from CSV
    accounts_data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get('code', '').strip()
            if code:
                accounts_data.append(row)

    if not accounts_data:
        _logger.warning("No accounts found in CSV file")
        return

    _logger.info("Found %d accounts in CSV", len(accounts_data))

    # Get all companies (usually just one in fresh install)
    companies = env['res.company'].search([])

    for company in companies:
        _logger.info("Processing accounts for company: %s", company.name)

        created_count = 0
        skipped_count = 0

        for account_data in accounts_data:
            code = account_data['code']

            # Check if account already exists for this company
            existing = env['account.account'].search([
                ('code', '=', code),
                ('company_id', '=', company.id)
            ], limit=1)

            if existing:
                skipped_count += 1
                continue

            # Create the account
            try:
                # Prepare account vals
                vals = {
                    'code': code,
                    'name': account_data.get('name', ''),
                    'account_type': account_data.get('account_type', 'asset_current'),
                    'company_id': company.id,
                }

                # Handle reconcile field
                reconcile = account_data.get('reconcile', '').strip()
                if reconcile:
                    vals['reconcile'] = reconcile.lower() in ('true', '1', 'yes')

                # Handle tag_ids if present
                tag_ids_str = account_data.get('tag_ids', '').strip()
                if tag_ids_str:
                    # Format: "module.xml_id1,module.xml_id2"
                    tag_ids = []
                    for tag_ref in tag_ids_str.split(','):
                        tag_ref = tag_ref.strip()
                        if tag_ref:
                            try:
                                tag = env.ref(tag_ref, raise_if_not_found=False)
                                if tag:
                                    tag_ids.append(tag.id)
                            except:
                                pass
                    if tag_ids:
                        vals['tag_ids'] = [(6, 0, tag_ids)]

                env['account.account'].create(vals)
                created_count += 1

            except Exception as e:
                _logger.error("Failed to create account %s: %s", code, str(e))
                continue

        _logger.info(
            "Account loading complete for %s: %d created, %d skipped (already exist)",
            company.name, created_count, skipped_count
        )

    _logger.info("✓ Additional accounts loaded successfully")
