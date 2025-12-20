# -*- coding: utf-8 -*-
{
    'name': "Timbre fiscal",
    'summary': "Timbre fiscal",
    'description': "Module de calcule du timbre fiscal selon la LF 2025 algérie",
    'author': "OPENNEXT Technology",
    'website': "http://www.opennext-dz.com",
    'category': 'Accounting',
    'version': '18.0.0.1.0',

    'depends': ['base',
                'account',
                'sale_management',
                'purchase'
                ],

    'data': [
        'security/ir.model.access.csv',
        'data/timbre_data.xml',
        'views/account_move_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/res_config_settings_views.xml',
        'views/report_invoice_inherit.xml',
    ],
    
    'images': [
        'static/description//banner.png',         
        'static/description//icone.ico',
    ],

    "license": "LGPL-3",
    'price': 0.0,
    'currency': 'USD',
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
