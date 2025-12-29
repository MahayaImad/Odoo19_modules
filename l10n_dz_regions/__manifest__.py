# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Algeria - Regions (58 Wilayas)',
    'summary': "Gestion par base de données relationnelles des adresses de vos contacts localisés en Algérie avec noms arabes",
    'description': """
Algeria Regions Module
======================
This module provides comprehensive management of Algerian administrative regions:
* 58 Wilayas (provinces) with Arabic names
* Communes (municipalities)
* Localités (localities)
* Integration with partners, companies, and banks
* Automatic postal code assignment based on locality
    """,
    'version': '17.0.1.0.0',
    'category': 'Localization',

    'company': 'CPSS',
    'author': 'CPSS',
    'maintainer': 'CPSS',
    'website': 'https://cpss-dz.com',
    'support': 'contact@cpss-dz.com',

    'license': 'LGPL-3',

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

    'demo': [],

    'installable': True,
    'auto_install': False,
    'application': False,
    'pre_init_hook': 'pre_init_hook',
}
