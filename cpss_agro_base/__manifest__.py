# -*- coding: utf-8 -*-
{
    'name': "CPSS Agro Base",
    'version': '19.0.1.0.0',
    'summary': "Extension des contacts pour les données agricoles et gestion des subdivisions",
    'description': """
Extension du module contacts pour ajouter des informations agricoles spécifiques.

Fonctionnalités:
================
* Ajout d'un onglet "Données Agricoles" dans la fiche contact
* Surface exploitée en hectares
* Type d'exploitation (Traditionnelle/Intensive)
* Nombre d'arbres
* Âge des arbres
* Gestion des subdivisions agricoles
* Gestion des daïras (ensemble de communes)
* Numéro d'agrément pour les sociétés

Module développé pour les magasins de vente de produits agricoles.
    """,
    'author': "CPSS",
    'website': "https://cpss.com",
    'category': 'Extra Tools',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'contacts',
        'eloapps_l10n_dz_regions',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/subdivision_views.xml',
        'views/daira_views.xml',
        'views/res_country_views.xml',
        'views/res_partner_views.xml',
        'views/menus.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}