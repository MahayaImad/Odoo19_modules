#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de conversion des fichiers JSON du plan comptable algérien vers CSV Odoo 19
Maintient la structure de template du module l10n_dz
"""

import json
import csv
from collections import defaultdict

def clean_xml_id(prefix, code):
    """Créer un XML ID propre et unique"""
    clean_code = str(code).replace(' ', '_').replace('-', '_').replace('à', 'a').replace('é', 'e').replace('è', 'e')
    return f"{prefix}_{clean_code}"

def convert_account_groups_to_csv():
    """Convertir account_group.json vers CSV"""
    print("Conversion des groupes de comptes vers CSV...")

    with open('account_group.json', 'r', encoding='utf-8') as f:
        groups = json.load(f)

    # Créer un mapping id -> group pour résoudre les références
    id_to_group = {group['id']: group for group in groups}

    # Créer un mapping id -> xml_id
    id_to_xmlid = {}
    for group in groups:
        code = group.get('code_prefix_start', '').strip()
        if code and code not in ['Classes 6 à 7', '']:
            xml_id = clean_xml_id('l10n_dz', code)
            id_to_xmlid[group['id']] = xml_id

    # Préparer les données CSV
    csv_rows = []

    for group in groups:
        code_start = group.get('code_prefix_start', '').strip()
        code_end = group.get('code_prefix_end', '').strip()
        name = group.get('name', '').strip()

        # Ignorer les groupes sans code valide ou avec des codes spéciaux
        if not code_start or code_start in ['Classes 6 à 7', '0']:
            continue

        xml_id = id_to_xmlid.get(group['id'])
        if not xml_id:
            continue

        # Pour le CSV, on n'a besoin que de l'ID, code_prefix_start, name et name@fr
        # On garde le même nom pour les deux langues (la plupart sont déjà en français)
        csv_rows.append({
            'id': xml_id,
            'code_prefix_start': code_start,
            'name': name,
            'name@fr': name
        })

    # Trier par code_prefix_start pour une meilleure organisation
    csv_rows.sort(key=lambda x: x['code_prefix_start'])

    # Écrire le fichier CSV
    with open('template/account.group-dz.csv', 'w', encoding='utf-8', newline='') as f:
        if csv_rows:
            writer = csv.DictWriter(f, fieldnames=['id', 'code_prefix_start', 'name', 'name@fr'])
            writer.writeheader()
            writer.writerows(csv_rows)

    print(f"✓ {len(csv_rows)} groupes de comptes convertis -> template/account.group-dz.csv")
    return id_to_xmlid

def map_account_type(account_type, code):
    """
    Mapper les types de comptes vers les types Odoo 19
    Basé sur le plan comptable algérien
    """
    # Essayer d'abord par le code
    code_prefix = str(code)[:2] if code else ''

    mapping = {
        # Classe 1 : Capitaux (Equity & Liabilities)
        '10': 'equity',
        '11': 'equity',
        '12': 'equity_unaffected',
        '13': 'liability_current',
        '15': 'liability_non_current',
        '16': 'liability_current',
        '17': 'liability_current',
        '18': 'liability_current',

        # Classe 2 : Immobilisations (Fixed Assets)
        '20': 'asset_fixed',
        '21': 'asset_fixed',
        '22': 'asset_fixed',
        '23': 'asset_fixed',
        '26': 'asset_non_current',
        '27': 'asset_non_current',
        '28': 'asset_fixed',  # Amortissements
        '29': 'asset_fixed',  # Pertes de valeur

        # Classe 3 : Stocks (Current Assets)
        '30': 'asset_current',
        '31': 'asset_current',
        '32': 'asset_current',
        '33': 'asset_current',
        '34': 'asset_current',
        '35': 'asset_current',
        '36': 'asset_current',
        '37': 'asset_current',
        '38': 'asset_current',
        '39': 'asset_current',

        # Classe 4 : Tiers (Receivables & Payables)
        '40': 'liability_payable',
        '41': 'asset_receivable',
        '42': 'liability_current',
        '43': 'liability_current',
        '44': 'liability_current',
        '45': 'liability_current',
        '46': 'asset_current',
        '47': 'asset_current',
        '48': 'asset_prepayments',
        '49': 'asset_current',

        # Classe 5 : Comptes financiers (Financial Accounts)
        '50': 'asset_current',
        '51': 'asset_cash',
        '52': 'asset_current',
        '53': 'asset_cash',
        '54': 'asset_cash',
        '58': 'asset_current',
        '59': 'asset_current',

        # Classe 6 : Charges (Expenses)
        '60': 'expense',
        '61': 'expense',
        '62': 'expense',
        '63': 'expense',
        '64': 'expense',
        '65': 'expense',
        '66': 'expense',
        '67': 'expense',
        '68': 'expense_depreciation',
        '69': 'expense',

        # Classe 7 : Produits (Income)
        '70': 'income',
        '72': 'income',
        '73': 'income',
        '74': 'income',
        '75': 'income_other',
        '76': 'income_other',
        '77': 'income_other',
        '78': 'income_other',
    }

    # Essayer de mapper par code
    mapped_type = mapping.get(code_prefix)
    if mapped_type:
        return mapped_type

    # Sinon, utiliser le type original s'il est valide
    valid_types = {
        'equity', 'equity_unaffected', 'asset_cash', 'asset_receivable',
        'asset_current', 'asset_non_current', 'asset_fixed', 'asset_prepayments',
        'liability_payable', 'liability_credit_card', 'liability_current',
        'liability_non_current', 'income', 'income_other', 'expense',
        'expense_depreciation', 'expense_direct_cost', 'off_balance'
    }

    if account_type in valid_types:
        return account_type

    # Par défaut, retourner expense pour éviter les erreurs
    return 'expense'

def convert_account_accounts_to_csv(group_id_mapping):
    """Convertir account_account.json vers CSV"""
    print("\nConversion des comptes vers CSV...")

    with open('account_account.json', 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    # Préparer les données CSV
    csv_rows = []
    seen_codes = set()  # Pour éviter les doublons

    for account in accounts:
        code = account.get('code', '').strip()
        name = account.get('name', '').strip()

        # Ignorer les comptes sans code ou nom
        if not code or not name:
            continue

        # Ignorer les doublons
        if code in seen_codes:
            continue
        seen_codes.add(code)

        xml_id = clean_xml_id('l10n_dz', code)

        # Type de compte
        original_type = account.get('account_type', 'expense')
        account_type = map_account_type(original_type, code)

        # Reconcile
        reconcile = account.get('reconcile', False)
        reconcile_str = 'True' if reconcile else 'False'

        csv_rows.append({
            'id': xml_id,
            'name': name,
            'code': code,
            'account_type': account_type,
            'tag_ids': '',
            'reconcile': reconcile_str,
            'name@fr': name  # On garde le même nom en français
        })

    # Trier par code pour une meilleure organisation
    csv_rows.sort(key=lambda x: x['code'])

    # Écrire le fichier CSV
    with open('template/account.account-dz.csv', 'w', encoding='utf-8', newline='') as f:
        if csv_rows:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'code', 'account_type', 'tag_ids', 'reconcile', 'name@fr'])
            writer.writeheader()
            writer.writerows(csv_rows)

    print(f"✓ {len(csv_rows)} comptes convertis -> template/account.account-dz.csv")

def main():
    """Fonction principale"""
    print("="*60)
    print("Conversion du Plan Comptable Algérien - JSON vers CSV Odoo 19")
    print("="*60)

    # Conversion des groupes
    group_id_mapping = convert_account_groups_to_csv()

    # Conversion des comptes
    convert_account_accounts_to_csv(group_id_mapping)

    print("\n" + "="*60)
    print("✓ Conversion terminée avec succès!")
    print("="*60)
    print("\nFichiers générés:")
    print("  - template/account.group-dz.csv")
    print("  - template/account.account-dz.csv")
    print("\nLes fichiers CSV sont maintenant prêts pour être utilisés par Odoo.")

if __name__ == '__main__':
    main()
