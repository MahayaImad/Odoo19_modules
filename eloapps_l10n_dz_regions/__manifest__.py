# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': '58 Wilayas - Algérie',
    'summary' : "Gestion par base de données relationnelles des adresses de vos contacts localisé en Algérie",
    'description' : "Gestion par base de données relationnelles des adresses de vos contacts localisé en Algérie",
    'version': '16.1.2.0',
    'category': 'Sales/CRM',

    'company': 'Elosys',
    'author' : 'Elosys',
    'maintainer': 'Elosys',

    
    'support' : "support@elosys.net",
    'website' : "http://www.elosys.net",
    'live_test_url' : "https://www.elosys.net/shop/wilayas-et-codes-postaux-algerie-4#attr=8",

    "contributors": [
        
        "1 <Chems Eddine SAHININE>"
        "2 <Youcef BENCHEHIDA>"
        "3 <Abdelhakim ABOURA>"
        "4 <Fatima MESSADI>"
    ],

    'license' : "OPL-1",
    'price' : "55",
    'currency' : 'Eur',


    'images' : ['images/banner.gif'],

    'depends': [
        'base',
        'contacts',
    ],
    
    'data': [
        'security/ir.model.access.csv',

        'data/res_country_state.xml',
        'data/res_country_commune.xml',
        'data/res_country_localite.xml',

        'views/res_country.xml',
        'views/res_bank.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
    ],
    
    'demo' : [
    ],
    
    'installable': True,
    'auto_install': False,
    "application": False,
}
