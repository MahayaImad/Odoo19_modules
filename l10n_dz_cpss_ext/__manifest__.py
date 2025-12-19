# -*- coding: utf-8 -*-
{
    'name': 'Algeria - CPSS Extensions',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations/Account Charts',
    'summary': 'Professional extensions for Algeria localization (CPSS compliant)',
    'description': '''
Algeria - Professional CPSS Extensions
======================================

This module extends the native Odoo l10n_dz (Algeria) localization with
professional features and comprehensive chart of accounts for CPSS compliance.

**Key Features:**

Chart of Accounts Extensions
-----------------------------
* 1,160 additional accounts beyond the 294 in native l10n_dz
* 973 account groups for detailed financial categorization
* Complete coverage of Algerian SCF (Système Comptable Financier)

Activity Code Management
-------------------------
* Full activity code system with regulation tracking
* Regulated, unauthorized, and unrestricted activity classification
* Integration with company and partner records
* Search by code or name with smart matching

Legal Forms (Formes Juridiques)
--------------------------------
* Complete Algerian legal form management
* SARL, EURL, SPA, SNC, SCS, SCPA, Groupement support
* Automatic initialization of standard legal forms
* Integration with company information

Algerian Company Information
-----------------------------
* N.I.S (Numéro d'Identification Statistique)
* N.I.F (Numéro d'Identification Fiscale)
* A.I (Article d'Imposition)
* N° RC (Numéro du Registre de Commerce)
* Capital Social with monetary tracking
* Fax number field
* Legal form selection

Partner Extensions
------------------
* Fiscal position assignment
* Activity code tracking
* Algerian identification numbers (NIS, NIF, AI, RC)
* Enhanced address formatting for Algerian wilayas

Configuration Options
---------------------
* Display activity sector on invoices/quotations
* Display activity code on invoices/quotations
* Tax transfer journal configuration
* Temporary tax account settings
* Payment vs invoice-based tax accounting

**Module Architecture:**

This module is designed as an EXTENSION of the native l10n_dz module:
* Depends on l10n_dz for base functionality
* Adds 1,160 accounts to the existing 294
* Does not duplicate or replace base features
* Follows Odoo best practices for modular design

**Installation:**

1. Install native l10n_dz first (usually auto-installed with accounting)
2. Install this module (l10n_dz_cpss_ext)
3. Configure company information in Settings > General Settings > Companies
4. Set up activity codes and legal forms as needed

**Compatibility:**

* Odoo 19.0+
* Works alongside native l10n_dz module
* Compatible with standard accounting workflows

**Support:**

For issues or questions, please contact the module maintainer.

    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'l10n_dz',          # Native Algeria localization (base)
        'account',          # Core accounting
        'base_vat',         # VAT number management
        'mail',             # For activity tracking
        'sale',             # Sales integration
        'sale_management',  # Advanced sales features
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data - Chart of Accounts Extensions
        # Note: Accounts are loaded via post_init_hook to avoid duplicates
        # See __init__.py for account loading logic

        # Data - Configuration
        'data/company_function.xml',

        # Views - Custom Models
        'views/activity_code.xml',
        'views/forme_juridique.xml',

        # Views - Extensions
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/configuration_settings.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
