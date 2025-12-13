# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Algérie - CPSS',
    'summary': """Plan comptable aux normes algériennes - CPSS""",
    'website': 'https://www.cpss-dz.com',
    'icon': '/account/static/description/l10n.png',
    'countries': ['dz'],
    'version': '19.0.1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Plan Comptable Algérien - Module CPSS
======================================
Ce module fournit le plan comptable algérien conforme au Système Comptable
et Financier (SCF) avec des fonctionnalités avancées pour les entreprises
algériennes.

Fonctionnalités principales :
- Plan comptable complet (973 groupes de comptes, 1169 comptes)
- Gestion des codes d'activité
- Gestion des formes juridiques
- Informations fiscales (NIS, NIF, AI, RC)
- Rapports fiscaux conformes aux normes algériennes

Remerciements :
Ce module est basé sur les travaux de Osis et de la communauté Odoo Algérie.
""",
    'author': 'CPSS',
    'contributors': [
        'Osis (plan comptable initial)',
    ],
    'depends': [
        'base_vat',
        'account',
        'mail',
        'sale',
        'sale_management',
    ],
    'auto_install': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/template/account.group-dz.csv',
        'data/template/account.account-dz.csv',
        'data/template/account.tax.group-dz.csv',
        'data/template/account.fiscal.position-dz.csv',
        'data/template/account.tax-dz.xml',
        'data/company_function.xml',
        'data/tax_report.xml',
        'views/forme_juridique.xml',
        'views/activity_code.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/configuration_settings.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'post_init_hook': 'post_init_hook',

}
