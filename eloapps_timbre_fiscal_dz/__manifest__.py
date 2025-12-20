# -*- coding: utf-8 -*-
# Original module by Elosys (http://www.elosys.net)
# Adapted and maintained for Odoo 19 by CPSS
{
    'name': "Droit de timbre client - Algérie",
    'summary': """Gestion des droits de timbre pour les paiements en espèce sur les factures et avoirs clients""",
    'description': """
Droit de Timbre Client - Algérie
=================================

Ce module permet de gérer les droits de timbre fiscal pour les paiements
en espèce (liquide) sur les factures et avoirs clients en Algérie.

Fonctionnalités:
----------------
* Application automatique du droit de timbre sur paiements espèce
* Configuration du montant du timbre par société
* Affichage du timbre sur les factures et avoirs
* Gestion des modes de paiement
* Compatible avec la réglementation algérienne

Module Original:
----------------
* Auteur original: Elosys
* Contributeurs: Yassamine CHENAFA, Fatima MESSADI
* Website: http://www.elosys.net

Adaptation Odoo 19:
-------------------
* Maintenu par: CPSS
* Version: 19.0.2.1
* Corrections de compatibilité Odoo 19
* Suppression du paramètre obsolète 'digits'
* Correction du champ 'discount_percentage'
    """,

    'version': '19.0.2.1',
    'category': 'Accounting/Accounting',

    # Crédits
    'author': 'Elosys, CPSS',  # Auteur original + Mainteneur
    'company': 'CPSS',
    'maintainer': 'CPSS',

    # Contributeurs originaux
    "contributors": [
        "Yassamine CHENAFA (Elosys)",
        "Fatima MESSADI (Elosys)",
    ],

    # Contacts
    'website': 'https://www.cpss.dz',

    # Licence - Conservée de l'original
    "license": "OPL-1",

    # Dépendances
    'depends': [
        'base',
        'account'
    ],

    "sequence": 1,

    # Données
    'data': [
        'security/ir.model.access.csv',

        'data/paymment_mode.xml',

        'views/configuration_timbre.xml',
        'views/account_move.xml',
        'views/account_move_report.xml',
        'views/account_payment.xml',
    ],

    'images': ['images/banner.gif'],

    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': "post_init_hook",

    # Odoo 19 compatibility
    'odoo_version': '19.0',
}
