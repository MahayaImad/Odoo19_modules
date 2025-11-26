#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour tester si le template l10n_dz_cpss est enregistré dans Odoo
À exécuter depuis l'interface Odoo (mode développeur)
"""

import odoo
from odoo import api, SUPERUSER_ID

# Connexion à la base
db_name = 'votre_base'  # Remplacer par le nom de votre base
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    print("="*70)
    print("TEST DU TEMPLATE l10n_dz_cpss")
    print("="*70)

    # 1. Vérifier si le module est installé
    print("\n1. VÉRIFICATION DE L'INSTALLATION")
    print("-"*70)
    module = env['ir.module.module'].search([('name', '=', 'l10n_dz_cpss')])
    if module:
        print(f"✓ Module trouvé: {module.name}")
        print(f"  État: {module.state}")
        print(f"  Version: {module.latest_version}")
    else:
        print("✗ Module non trouvé dans ir.module.module")

    # 2. Vérifier le pays
    print("\n2. VÉRIFICATION DU PAYS")
    print("-"*70)
    country = env['res.country'].search([('code', '=', 'DZ')])
    if country:
        print(f"✓ Pays trouvé: {country.name} ({country.code})")
    else:
        print("✗ Pays Algérie (DZ) non trouvé")

    # 3. Vérifier si le template est chargé
    print("\n3. VÉRIFICATION DU TEMPLATE")
    print("-"*70)
    try:
        template_model = env['account.chart.template']
        print(f"✓ Modèle account.chart.template accessible")

        # Essayer d'obtenir le template
        if hasattr(template_model, '_get_chart_template_data'):
            try:
                template_data = template_model._get_chart_template_data('dz')
                print(f"✓ Template 'dz' trouvé")
                print(f"  Données: {template_data}")
            except Exception as e:
                print(f"✗ Erreur lors de la récupération du template: {e}")
        else:
            print("  Méthode _get_chart_template_data non disponible")

    except Exception as e:
        print(f"✗ Erreur: {e}")

    # 4. Vérifier les comptes créés
    print("\n4. VÉRIFICATION DES COMPTES")
    print("-"*70)
    required_accounts = ['401', '413', '412', '31', '600', '700']
    for code in required_accounts:
        account = env['account.account'].search([('code', '=', code)], limit=1)
        if account:
            print(f"✓ Compte {code}: {account.name}")
        else:
            # Essayer de trouver avec l'XML ID
            try:
                account = env.ref(f'l10n_dz_cpss.l10n_dz_{code}', raise_if_not_found=False)
                if account:
                    print(f"✓ Compte {code} (via XML ID): {account.name}")
                else:
                    print(f"✗ Compte {code} non trouvé")
            except:
                print(f"✗ Compte {code} non trouvé")

    # 5. Lister tous les templates disponibles
    print("\n5. TEMPLATES DISPONIBLES")
    print("-"*70)
    try:
        # Cette méthode liste tous les templates enregistrés
        templates = template_model._get_chart_template_mapping()
        if templates:
            print("Templates enregistrés:")
            for country_code, template_name in templates.items():
                print(f"  - {country_code}: {template_name}")
        else:
            print("Aucun template trouvé")
    except Exception as e:
        print(f"Impossible de lister les templates: {e}")

    print("\n" + "="*70)
    print("FIN DU TEST")
    print("="*70)
