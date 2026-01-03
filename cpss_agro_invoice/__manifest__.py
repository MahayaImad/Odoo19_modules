# -*- coding: utf-8 -*-
{
    'name': 'CPSS Agro - Facturation Subventionnée FNDIA',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Gestion des subventions FNDIA pour les factures de vente d\'engrais',
    'description': """
        Module de gestion des subventions FNDIA
        ========================================

        Ce module ajoute la gestion des subventions FNDIA pour les factures de vente :
        - Champ "Subventionné FNDIA" sur les factures de vente (oui/non)
        - Calcul automatique du montant de subvention basé sur le montant de soutien de la catégorie produit
        - Montant FNDIA = prix_soutien × quantité pour chaque ligne
        - Montant à payer = montant total - montant FNDIA
        - Enregistrement de la subvention dans un compte client séparé
        - Calcul du timbre fiscal sur le montant à payer uniquement
    """,
    'author': 'CPSS',
    'website': 'https://www.cpss.dz',
    'depends': [
        'account',
        'cpss_product_categories',  # Pour accéder au champ prix_soutien
        'l10n_dz',  # Pour le timbre fiscal algérien
    ],
    'data': [
        # Données
        'data/account_account_data.xml',

        # Vues
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
