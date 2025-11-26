# -*- coding: utf-8 -*-
{
    'name': "Droit de Timbre sur Facture et sur Paiement Fournisseur- Algérie",
    
    'summary': """ Gestion de droit de timbre sur les factures et les paiements fournisseur""",
    'description': """ Gestion de droit de timbre sur les factures et les paiements fournisseur""",



    'category': 'Accounting',
    'version': '19.0.1.0',


    "contributors": [
        "1 <Chems Eddine SAHININE>",
        "2 <Fatima MESSADI>",
    
    ],
    'sequence': 1,


    
    
    'author': 'Elosys',


    'website': 'https://www.elosys.net/',
    'support'     : "support@elosys.net",
    'live_test_url':"https://www.elosys.net/shop/comptabilite-et-factures-algerie-2?category=6#attr=3",

    "license": "LGPL-3",
    "price": 27.50,
    "currency": 'EUR',


    
    'depends': [
        'base',
        'eloapps_timbre_fiscal_dz',
    ],


    'data': [
        "data/timbre_journal.xml",
        "views/configuration_settings.xml",
        "views/account_move.xml",
        "views/account_payment.xml",
        "views/account_payment_register.xml",
        "views/account_journal.xml",
        

        
    ],


    'images': ['images/banner.gif'],

    'installable': True,
    'auto_install': False,
    'application':False,
    'post_init_hook': "post_init_hook_t",
}
