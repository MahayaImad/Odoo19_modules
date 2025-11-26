#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier la configuration du module l10n_dz_cpss
"""

import os
import csv

def check_csv_format(csv_file):
    """Vérifier le format du CSV"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            row_count = sum(1 for row in reader)
            return True, headers, row_count
    except Exception as e:
        return False, str(e), 0

def main():
    print("="*70)
    print("DIAGNOSTIC DU MODULE l10n_dz_cpss")
    print("="*70)

    # 1. Vérifier la structure des répertoires
    print("\n1. STRUCTURE DES RÉPERTOIRES")
    print("-" * 70)
    required_dirs = [
        'models',
        'data',
        'data/template',
        'views',
        'security',
    ]
    for dir_name in required_dirs:
        exists = os.path.isdir(dir_name)
        status = "✓" if exists else "✗"
        print(f"  {status} {dir_name}")

    # 2. Vérifier les fichiers Python
    print("\n2. FICHIERS PYTHON DU TEMPLATE")
    print("-" * 70)
    if os.path.exists('models/template_dz.py'):
        print("  ✓ models/template_dz.py existe")
        with open('models/template_dz.py', 'r') as f:
            content = f.read()
            if "@template('dz')" in content:
                print("  ✓ Décorateur @template('dz') trouvé")
            else:
                print("  ✗ Décorateur @template('dz') MANQUANT")

            if "_get_dz_template_data" in content:
                print("  ✓ Méthode _get_dz_template_data trouvée")
            else:
                print("  ✗ Méthode _get_dz_template_data MANQUANTE")
    else:
        print("  ✗ models/template_dz.py MANQUANT")

    # 3. Vérifier les fichiers CSV
    print("\n3. FICHIERS CSV DU TEMPLATE")
    print("-" * 70)
    csv_files = {
        'account.group-dz.csv': 'Groupes de comptes',
        'account.account-dz.csv': 'Comptes comptables',
        'account.tax-dz.csv': 'Taxes',
        'account.tax.group-dz.csv': 'Groupes de taxes',
        'account.fiscal.position-dz.csv': 'Positions fiscales',
    }

    os.chdir('data/template')

    for csv_file, description in csv_files.items():
        if os.path.exists(csv_file):
            valid, headers, count = check_csv_format(csv_file)
            if valid:
                print(f"  ✓ {csv_file}")
                print(f"    - {description}: {count} enregistrements")
                print(f"    - Colonnes: {', '.join(headers)}")
            else:
                print(f"  ✗ {csv_file} - ERREUR: {headers}")
        else:
            print(f"  ✗ {csv_file} MANQUANT")

    os.chdir('../..')

    # 4. Vérifier les comptes requis
    print("\n4. COMPTES REQUIS PAR LE TEMPLATE")
    print("-" * 70)
    required_accounts = {
        'l10n_dz_401': 'Fournisseurs (payable)',
        'l10n_dz_413': 'Clients (receivable)',
        'l10n_dz_412': 'Clients POS',
        'l10n_dz_31': 'Stock',
        'l10n_dz_600': 'Achats (expense)',
        'l10n_dz_700': 'Ventes (income)',
        'l10n_dz_601': 'Stock expense',
        'l10n_dz_603': 'Stock variation',
        'l10n_dz_609': 'Rabais obtenus',
        'l10n_dz_657': 'Écarts de caisse (charge)',
        'l10n_dz_666': 'Pertes de change',
        'l10n_dz_709': 'Rabais accordés',
        'l10n_dz_758': 'Écarts de caisse (produit)',
        'l10n_dz_766': 'Gains de change',
    }

    with open('data/template/account.account-dz.csv', 'r', encoding='utf-8') as f:
        content = f.read()
        for xml_id, description in required_accounts.items():
            if xml_id + ',' in content:
                print(f"  ✓ {xml_id} - {description}")
            else:
                print(f"  ✗ {xml_id} - {description} MANQUANT")

    # 5. Vérifier le manifest
    print("\n5. CONFIGURATION DU MANIFEST")
    print("-" * 70)
    with open('__manifest__.py', 'r') as f:
        manifest_content = f.read()

        checks = [
            ("'name':", "Nom du module"),
            ("'countries': ['dz']", "Pays: Algérie"),
            ("'category': 'Accounting/Localizations/Account Charts'", "Catégorie correcte"),
            ("'auto_install': False", "Auto-install: False"),
            ("'installable': True", "Installable: True"),
        ]

        for check, description in checks:
            if check in manifest_content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} - Vérifier la configuration")

    # 6. Recommandations
    print("\n6. INSTRUCTIONS POUR ACTIVER LE PLAN COMPTABLE")
    print("="*70)
    print("""
Pour que le plan comptable soit détectable dans Odoo 19 :

1. INSTALLER/METTRE À JOUR le module :
   odoo-bin -u l10n_dz_cpss -d votre_base --stop-after-init

2. REDÉMARRER Odoo complètement

3. VÉRIFIER l'installation :
   - Aller dans Apps
   - Rechercher "l10n_dz_cpss"
   - Le module doit être marqué comme "Installé"

4. APPLIQUER le plan comptable :

   MÉTHODE A - Nouvelle société :
   - Paramètres > Utilisateurs et Sociétés > Sociétés
   - Créer une nouvelle société
   - Pays: Algérie
   - Le plan comptable devrait s'appliquer automatiquement

   MÉTHODE B - Société existante :
   - Comptabilité > Configuration > Paramètres
   - Section "Comptabilité fiscale"
   - Pays fiscal: Algérie
   - Installer le plan comptable

   MÉTHODE C - Configuration manuelle :
   - Comptabilité > Configuration > Plan comptable
   - Importer depuis un modèle
   - Sélectionner "Algérie - CPSS"

ATTENTION : Si le plan comptable n'apparaît toujours pas :
- Vérifier les logs Odoo pour les erreurs
- Vérifier que le module est dans le addons_path
- S'assurer qu'il n'y a pas d'erreurs Python au chargement
    """)

if __name__ == '__main__':
    main()
