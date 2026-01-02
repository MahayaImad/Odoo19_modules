# -*- coding: utf-8 -*-
{
    'name': "CPSS Agro Base",
    'version': '19.0.1.0.0',
    'summary': "Extension des contacts pour les données agricoles",
    'description': """
Extension du module contacts pour ajouter des informations agricoles spécifiques.

Fonctionnalités:
================
* Ajout d'un onglet "Données Agricoles" dans la fiche contact
* Surface exploitée en hectares
* Type d'exploitation (Traditionnelle/Intensive)
* Nombre d'arbres
* Âge des arbres

Module développé pour les magasins de vente de produits agricoles.
    """,
    'author': "CPSS",
    'website': "https://cpss.com",
    'category': 'Extra Tools',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'contacts',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}