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
    'name': 'Kit Comptable Complet Algérie (CPSS)',
    'version': '19.0.2.0.0',
    'category': 'Accounting/Accounting',
    'summary': """Kit comptable complet pour Odoo 19 - Adaptation normes algériennes SCF - Rapports, Actifs, PDC, Relances""",
    'description': """
Kit Comptable Complet Adapté aux Normes Algériennes
====================================================

Module comptable complet pour Odoo 19 Community Edition, adapté aux normes
comptables et fiscales algériennes (SCF - Système Comptable Financier).

Ce module fournit une suite complète de fonctionnalités comptables avancées
compatibles avec la réglementation algérienne.

Fonctionnalités Principales
----------------------------

**1. Rapports Comptables (15 rapports)**
* Grand Livre Général conforme SCF
* Grand Livre Partenaire (clients/fournisseurs)
* Balance de Vérification
* Balance Âgée (créances par ancienneté)
* Livre de Banque
* Livre de Caisse
* Livre de Jour (Journal)
* Rapport Financier personnalisable (Bilan, Compte de Résultat SCF)
* Flux de Trésorerie (Tableau SCF)
* Rapport de Taxes (TVA pour déclaration G50)
* Audit de Journal
* Balance Générale

**2. Gestion des Actifs et Amortissements**
* Création et suivi des immobilisations
* Amortissement linéaire (conforme fiscalité algérienne)
* Amortissement dégressif
* Calcul automatique des dotations
* Génération des écritures d'amortissement
* Rapport des actifs et valeurs nettes comptables
* Catégories d'actifs pré-configurées
* Prorata temporis
* Cessions d'actifs

**3. PDC - Chèques Différés (Post-Dated Cheques)**
* Gestion des chèques à échéance (très utilisés en Algérie)
* PDC clients (entrées)
* PDC fournisseurs (sorties)
* Suivi par date d'effet
* Impression de chèques
* Rapprochement bancaire PDC

**4. Relances Clients (Follow-ups)**
* Plans de relance configurables
* Niveaux de relance multiples
* Génération automatique
* Templates de communication
* Suivi des impayés

**5. Limite de Crédit**
* Définition de limites par client
* Étape d'avertissement
* Étape de blocage
* Blocage automatique des factures
* Affichage du montant dû

**6. Écritures Récurrentes**
* Génération automatique périodique
* Loyers, abonnements, etc.
* Planification via cron

**7. Import Bancaire**
* Import OFX, QIF, Excel
* Rapprochement automatique

Adaptation Algérienne
--------------------
* **Plan Comptable SCF** : Intégration complète avec l10n_dz_cpss_ext
* **Année Fiscale** : Janvier à décembre (année civile)
* **Rapports fiscaux** : Adaptés pour déclarations algériennes
* **TVA** : Taux algériens (19%, 9%)
* **Timbre Fiscal** : Compatible avec l10n_dz_on_timbre_fiscal
* **Mentions légales** : NIF, NIS, RC sur documents
* **Interface française** : Traduction complète
* **Documentation** : Contexte algérien

Dépendances Algériennes
-----------------------
**Obligatoires :**
* l10n_dz_cpss_ext : Plan comptable SCF algérien
* cpss_account_budget : Gestion budgétaire

**Recommandées :**
* l10n_dz_on_timbre_fiscal : Timbre fiscal obligatoire
* l10n_dz_code_cnrc : Codes d'activité CNRC

**Standards :**
* account : Comptabilité de base
* sale : Ventes
* account_check_printing : Impression chèques
* analytic : Comptabilité analytique
* contacts : Partenaires

Conformité Réglementaire Algérienne
------------------------------------
* **SCF** : Système Comptable Financier
* **Code des impôts** : Taxes et TVA algériennes
* **Déclarations fiscales** : G50 (TVA), Série G (bilan fiscal)
* **Conservation** : Documents conservés 10 ans minimum
* **Formats officiels** : États financiers conformes au SCF

Dépendances Python
------------------
* openpyxl : Import/Export Excel
* ofxparse : Import relevés bancaires OFX
* qifparse : Import relevés QIF

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
        'account',
        'sale',
        'account_check_printing',
        'analytic',
        'contacts',
        'cpss_account_budget',      # Gestion budgétaire CPSS
        'l10n_dz_cpss_ext',         # Plan comptable SCF algérien - OBLIGATOIRE
        'l10n_dz_on_timbre_fiscal', # Timbre fiscal algérien - RECOMMANDÉ
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/account_financial_report_data.xml',
        'data/cash_flow_data.xml',
        'data/followup_levels.xml',
        'data/multiple_invoice_data.xml',
        'data/recurring_entry_cron.xml',
        'data/account_pdc_data.xml',
        'views/reports_config_view.xml',
        'views/accounting_menu.xml',
        'views/account_group.xml',
        'views/credit_limit_view.xml',
        'views/account_configuration.xml',
        'views/res_config_settings_views.xml',
        'views/account_followup.xml',
        'views/followup_line_views.xml',
        'views/followup_report.xml',
        'wizard/asset_depreciation_confirmation_views.xml',
        'wizard/asset_modify_views.xml',
        'views/account_asset_asset_views.xml',
        'views/account_asset_category_views.xml',
        'views/account_move_views.xml',
        'views/product_template_views.xml',
        'views/multiple_invoice_layout_view.xml',
        'views/multiple_invoice_form.xml',
        'views/account_journal_views.xml',
        'views/res_partner_views.xml',
        'wizard/financial_report_views.xml',
        'wizard/account_report_general_ledger_views.xml',
        'wizard/account_report_partner_ledger_views.xml',
        'wizard/kit_account_tax_report_views.xml',
        'wizard/account_balance_report_views.xml',
        'wizard/account_aged_trial_balance_views.xml',
        'wizard/account_print_journal_views.xml',
        'wizard/cash_flow_report_views.xml',
        'wizard/account_bank_book_report_views.xml',
        'wizard/account_cash_book_report_views.xml',
        'wizard/account_day_book_report_views.xml',
        'report/report_financial_template.xml',
        'report/general_ledger_report_template.xml',
        'report/report_journal_audit_template.xml',
        'report/report_aged_partner_template.xml',
        'report/report_trial_balance_template.xml',
        'report/report_tax_template.xml',
        'report/report_partner_ledger_template.xml',
        'report/cash_flow_report_template.xml',
        'report/account_bank_book_template.xml',
        'report/account_cash_book_template.xml',
        'report/account_day_book_template.xml',
        'report/account_asset_report_views.xml',
        'report/report.xml',
        'report/multiple_invoice_layouts.xml',
        'report/multiple_invoice_report_template.xml',
        'report/res_partner_reports.xml',
        'report/res_partner_templates.xml',
        'views/account_recurring_payments_view.xml',
        'views/account_move_line_views.xml',
        'views/account_bank_statement_views.xml',
        'views/account_bank_statement_line_views.xml',
        'views/account_payment_view.xml',
        'wizard/account_lock_date_views.xml',
        'wizard/import_bank_statement_views.xml',
    ],
    'external_dependencies': {
            'python': ['openpyxl', 'ofxparse', 'qifparse']
        },
    'assets': {
        'web.assets_backend': [
            'cpss_accounting_kit/static/src/scss/style.scss',
            'cpss_accounting_kit/static/src/scss/bank_rec_widget.css',
            'cpss_accounting_kit/static/src/js/bank_reconcile_form_list_widget.js',
            'cpss_accounting_kit/static/src/js/KanbanController.js',
            'cpss_accounting_kit/static/src/js/ListController.js',
            'cpss_accounting_kit/static/src/js/bank_reconcile_form_lines_widget.js',
            'cpss_accounting_kit/static/src/js/action_manager.js',
            'cpss_accounting_kit/static/src/xml/bank_rec_widget.xml',
            'cpss_accounting_kit/static/src/xml/bank_reconcile_widget.xml',
        ]
    },
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 5,
    'country': 'DZ',  # Code pays Algérie (ISO 3166-1 alpha-2)
}
