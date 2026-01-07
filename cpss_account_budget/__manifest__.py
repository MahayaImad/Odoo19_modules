# -*- coding: utf-8 -*-
#############################################################################
#
#    CPSS - Centre de Prestation des Soins de Santé
#
#    Copyright (C) 2026-TODAY CPSS (<https://cpss.dz>)
#    Basé sur le module original de Cybrosys Technologies
#    Original Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#    Adaptation algérienne: CPSS
#
#    Vous pouvez modifier ce module selon les termes de la licence
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    Ce programme est distribué dans l'espoir qu'il sera utile,
#    mais SANS AUCUNE GARANTIE; sans même la garantie implicite de
#    COMMERCIALISATION ou D'ADÉQUATION À UN OBJECTIF PARTICULIER. Voir la
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) pour plus de détails.
#
#    Vous devriez avoir reçu une copie de la GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) avec ce programme.
#    Si ce n'est pas le cas, voir <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Gestion Budgétaire Algérie (CPSS)',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': """Gestion budgétaire pour Odoo 19 - Adaptation normes algériennes SCF""",
    'description': """
Gestion Budgétaire Adaptée aux Normes Algériennes
==================================================

Ce module permet aux comptables de gérer les budgets analytiques conformément
aux normes comptables et fiscales algériennes (SCF).

Une fois les budgets définis (dans Comptabilité/Comptabilité/Budgets),
les chefs de projet peuvent définir le montant prévu sur chaque compte analytique.

Le comptable a la possibilité de voir le total du montant prévu pour
chaque budget afin de s'assurer que le total planifié n'est pas supérieur/inférieur
à ce qu'il a prévu pour ce budget.

Fonctionnalités Principales
----------------------------
* Création de positions budgétaires liées aux comptes SCF
* Définition de budgets avec dates de début et fin (année fiscale algérienne)
* Lignes budgétaires avec comptes analytiques
* Calcul automatique des montants pratiques et théoriques
* Pourcentage de réalisation en temps réel
* Workflow de validation (Brouillon → Confirmé → Validé → Terminé)
* Suivi budgétaire par département/projet/centre de coût
* Vue graphique des budgets
* Compatible avec le plan comptable algérien (SCF)

Adaptation Algérienne
--------------------
* Intégration avec le plan comptable SCF (l10n_dz_cpss_ext)
* Année fiscale algérienne (janvier à décembre)
* Interface entièrement en français
* Documentation adaptée au contexte algérien
* Compatible avec les modules fiscaux algériens (timbre fiscal, etc.)
* Respect des normes de gestion budgétaire des organismes publics algériens

Dépendances Algériennes
-----------------------
* l10n_dz_cpss_ext : Plan comptable SCF obligatoire
* analytic : Comptabilité analytique

Crédits
-------
Module original développé par Cybrosys Technologies
Adaptation algérienne par CPSS - 2026
    """,
    'author': 'CPSS (Basé sur Cybrosys Techno Solutions)',
    'company': 'CPSS',
    'maintainer': 'CPSS',
    'website': 'https://cpss.dz',
    'depends': [
        'base',
        'account',
        'analytic',
        'l10n_dz_cpss_ext',  # Plan comptable SCF algérien - OBLIGATOIRE
    ],
    'data': [
        'security/account_budget_security.xml',
        'security/ir.model.access.csv',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
    ],
    'post_init_hook': 'enable_analytic_accounting',
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 10,
    'country': 'DZ',  # Code pays Algérie (ISO 3166-1 alpha-2)
}
