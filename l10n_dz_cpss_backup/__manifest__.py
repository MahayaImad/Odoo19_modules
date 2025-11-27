# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': "Comptabilité - Algérie CPSS",
    'summary': """ Plan comptable aux normes algériennes - Version CPSS. """,
    'description': """
Plan comptable algérien CPSS - Odoo 18
======================================

Ce module fournit :
* Plan comptable conforme aux normes algériennes (PCG)
* Comptes de base organisés par classes
* Taxes algériennes (TVA, TAP, etc.)
* Positions fiscales
* Codes d'activité
* Formes juridiques
* Champs spécifiques aux entreprises algériennes (NIS, NIF, RC, AI)
* Configuration automatique des comptes par défaut

Adapté pour Odoo 18.0 - Nouvelle architecture comptable
""",

    'category': 'Accounting/Localizations/Account Charts',
    'version': '18.0.1.1',

    "contributors": [
        "Migration Odoo 18 - CPSS Version",
    ],
    'sequence': 1,

    'author': 'CPSS Solutions',
    'website': 'https://www.cpss.com',

    "license": "LGPL-3",
    "price": 0.0,
    "currency": 'EUR',

    'depends': [
        'base',
        'account',
        'sale',
        'sale_management',
    ],

    'data': [
        # Sécurité d'abord
        'security/ir.model.access.csv',
        'security/rules.xml',

        # Données de base (ordre important)
        'data/default_data.xml',
        #'data/l10n_dz_base_chart_data.xml',  # Groupes et tags
        #'data/account_accounts_base_data.xml',  # Comptes de base
        #'data/account_tax_data.xml',
        #'data/account_fiscal_position_template_data.xml',
        #'data/company_defaults.xml',  # Configuration par défaut

        # Vues
        "views/forme_juridique.xml",
        "views/activity_code.xml",
        "views/res_company.xml",
        "views/res_partner.xml",
        "views/configuration_settings.xml",
    ],

    'images': ['images/banner.gif'],

    #'post_init_hook': '_l10n_dz_post_init',

    'installable': True,
    'auto_install': False,
    'application': False,
}