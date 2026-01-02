# -*- coding: utf-8 -*-

{
    'name': "Nomenclature des Activités Économiques CNRC - Algérie",
    'description': """ Intégration des codes d'activité algériens. """,
    'summary': """ Nomenclature des Activités Économique CNRC """,


    'category': 'Accounting/accounting',
    'version': '19.0.1.0',

    "contributors": [
        "1 <Chems Eddine SAHININE>",
        "2 <Fatima MESSADI>",
    ],

    'sequence': 1,

    
    'author': 'Elosys',
    'website': 'https://www.elosys.net',
    'live_test_url':"https://www.elosys.net/shop/comptabilite-et-factures-algerie-2?category=6#attr=4",

    "license": "LGPL-3",
    "price": 27.50,
    "currency": 'EUR',


    
    'depends': [
        'base',
        'l10n_dz_cpss_ext',
    ],

    'data': [
      
        'data/activity_code_data.xml',

    ],


    'images': ['images/banner.gif'],
   
    'installable': True,
    'auto_install': False,
    'application':False,
}
