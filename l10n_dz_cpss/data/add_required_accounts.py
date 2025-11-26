#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter les comptes requis par le template au CSV account.account-dz.csv
"""

import csv

# Comptes requis par template_dz.py
required_accounts = [
    # Comptes de base
    {
        'id': 'l10n_dz_401',
        'code': '401',
        'name': 'Fournisseurs',
        'account_type': 'liability_payable',
        'reconcile': 'True',
    },
    {
        'id': 'l10n_dz_412',
        'code': '412',
        'name': 'Clients - Retenues de garantie',
        'account_type': 'asset_receivable',
        'reconcile': 'True',
    },
    {
        'id': 'l10n_dz_413',
        'code': '413',
        'name': 'Clients - Effets à recevoir',
        'account_type': 'asset_receivable',
        'reconcile': 'True',
    },

    # Comptes de stock
    {
        'id': 'l10n_dz_31',
        'code': '31',
        'name': 'Matières premières et fournitures',
        'account_type': 'asset_current',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_601',
        'code': '601',
        'name': 'Achats de matières premières',
        'account_type': 'expense',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_603',
        'code': '603',
        'name': 'Variation des stocks de matières premières',
        'account_type': 'expense',
        'reconcile': 'False',
    },

    # Comptes de base - Charges et Produits
    {
        'id': 'l10n_dz_600',
        'code': '600',
        'name': 'Achats de marchandises vendues',
        'account_type': 'expense',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_609',
        'code': '609',
        'name': 'Rabais, remises et ristournes obtenus sur achats',
        'account_type': 'expense',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_657',
        'code': '657',
        'name': 'Charges exceptionnelles de gestion courante',
        'account_type': 'expense',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_666',
        'code': '666',
        'name': 'Pertes de change',
        'account_type': 'expense',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_700',
        'code': '700',
        'name': 'Ventes de marchandises',
        'account_type': 'income',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_709',
        'code': '709',
        'name': 'Rabais, remises et ristournes accordés',
        'account_type': 'income',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_758',
        'code': '758',
        'name': 'Produits exceptionnels de gestion courante',
        'account_type': 'income_other',
        'reconcile': 'False',
    },
    {
        'id': 'l10n_dz_766',
        'code': '766',
        'name': 'Gains de change',
        'account_type': 'income_other',
        'reconcile': 'False',
    },
]

def add_required_accounts():
    """Ajouter les comptes requis au CSV"""
    csv_file = 'template/account.account-dz.csv'

    print(f"Lecture du fichier {csv_file}...")

    # Lire le CSV existant
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        existing_rows = list(reader)
        fieldnames = reader.fieldnames

    # Créer un set des IDs existants
    existing_ids = {row['id'] for row in existing_rows}

    print(f"Comptes existants: {len(existing_rows)}")

    # Ajouter les comptes manquants
    added_count = 0
    for account in required_accounts:
        if account['id'] not in existing_ids:
            new_row = {
                'id': account['id'],
                'name': account['name'],
                'code': account['code'],
                'account_type': account['account_type'],
                'tag_ids': '',
                'reconcile': account['reconcile'],
                'name@fr': account['name'],
            }
            existing_rows.append(new_row)
            added_count += 1
            print(f"✓ Ajouté: {account['id']} - {account['code']} - {account['name']}")
        else:
            print(f"- Existe déjà: {account['id']}")

    # Trier les lignes par code
    existing_rows.sort(key=lambda x: x['code'])

    # Écrire le fichier mis à jour
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)

    print(f"\n✓ {added_count} comptes ajoutés")
    print(f"✓ Total de comptes: {len(existing_rows)}")
    print(f"✓ Fichier mis à jour: {csv_file}")

if __name__ == '__main__':
    add_required_accounts()
