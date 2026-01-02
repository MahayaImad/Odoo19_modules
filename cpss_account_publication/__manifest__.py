# -*- coding: utf-8 -*-
{
    'name': 'Gestion des Factures Publiées',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Gestion des factures avec statut de publication et séquence spécifique',
    'description': """
        Module de gestion des factures publiées
        ========================================

        Ce module ajoute la fonctionnalité de publication des factures avec :
        - Un état de publication (publié/non publié)
        - Une séquence spécifique pour les factures publiées
        - Un journal dédié pour les paiements des factures publiées
        - Gestion des permissions pour la publication
    """,
    'author': 'CPSS',
    'website': 'https://www.cpss.dz',
    'depends': [
        'account',
        'base',
    ],
    'data': [
        # Sécurité
        'security/security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/ir_sequence_data.xml',

        # Vues
        'views/account_move_views.xml',
        'views/res_company_views.xml',
       # 'views/publication_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}