# Algeria - CPSS Extensions (l10n_dz_cpss_ext)

Professional extensions for Odoo's native Algeria localization module, providing comprehensive CPSS (Plan Comptable Système Comptable Financier) compliance and advanced features.

## Overview

This module **extends** the native `l10n_dz` module with:
- **1,160 additional accounts** (total: 1,454 accounts including native 294)
- **973 account groups** for detailed categorization
- **Activity code management** with regulation tracking
- **Legal forms (formes juridiques)** management
- **Algerian company identifiers** (NIS, NIF, AI, RC)
- **Enhanced partner information** for Algerian businesses
- **French translations** for tax names

## Architecture

Unlike the standalone `l10n_dz_cpss` module that replaces the native localization, this module follows a **modular extension pattern**:

```
l10n_dz (native)          →  294 accounts, basic features
    ↓ extends
l10n_dz_cpss_ext (this)   →  +1,160 accounts, advanced features
    ↓ result
Complete CPSS Solution    →  1,454 accounts, full functionality
```

## Key Features

### 📊 Enhanced Chart of Accounts

- **Native l10n_dz**: 294 accounts (basic SCF)
- **With extensions**: 1,454 accounts (full CPSS)
- Complete coverage of Algerian financial accounting standards
- Detailed expense, revenue, asset, liability, and equity accounts
- **Note**: Uses native account groups (68 groups) - accounts auto-assign based on code prefixes

### 🏢 Activity Code Management

Create and manage Algerian activity codes with:
- **Code and name** tracking
- **Regulation status**: Regulated, Unauthorized, or Unrestricted
- **Principal activity** designation
- Integration with company and partner records

### ⚖️ Legal Forms (Formes Juridiques)

Pre-configured legal forms:
- SARL (Société à responsabilité limitée)
- EURL (Société unipersonnelle à responsabilité limitée)
- SPA (Société par actions)
- SNC (Société en nom collectif)
- SCS (Société en commandite simple)
- SCPA (Société en commandite par actions)
- Groupement
- Entreprise Individuelle

### 🆔 Algerian Identifiers

Company and partner support for:
- **N.I.S** (Numéro d'Identification Statistique)
- **N.I.F** (Numéro d'Identification Fiscale)
- **A.I** (Article d'Imposition)
- **N° RC** (Numéro du Registre de Commerce)
- **Capital Social** with monetary tracking
- **Fax** number

### ⚙️ Configuration Options

- Display activity sector on invoices
- Display activity code on invoices and quotations
- Tax transfer journal selection
- Temporary tax account configuration
- Choose between invoice-based or payment-based tax accounting

## Installation

1. **Install prerequisites**:
   ```bash
   # Native Algeria localization (usually auto-installed)
   # Ensure l10n_dz is installed
   ```

2. **Install this module**:
   ```bash
   # Via Odoo Apps menu:
   Apps > Search "Algeria - CPSS Extensions" > Install

   # Or via command line:
   odoo-bin -d your_database -i l10n_dz_cpss_ext
   ```

3. **Configure company information**:
   - Settings > General Settings > Companies
   - Fill in NIS, NIF, AI, RC, Capital Social
   - Select Legal Form
   - Assign Activity Codes

## Usage

### Setting Up Activity Codes

1. Navigate to **Accounting > Configuration > Activity Codes**
2. Create activity codes with:
   - Code (numeric)
   - Name
   - Regulation status
   - Principal activity flag
3. Assign to companies and partners

### Configuring Legal Forms

Legal forms are automatically created on installation. To customize:

1. Navigate to **Accounting > Configuration > Legal Forms**
2. Add or modify legal forms as needed

### Assigning Company Information

1. **Settings > General Settings > Companies > Edit**
2. Fill in the **Algerian Information** section:
   - N.I.S: 15-character alphanumeric
   - N.I.F: 15-character alphanumeric
   - A.I: 11-character alphanumeric
   - N° RC: Commercial register number
   - Capital Social: Company capital
   - Legal Form: Select from dropdown
   - Activity Codes: Assign one or more

### Partner Extensions

When creating/editing partners:

1. **Fiscal Information** tab includes:
   - Fiscal Position
   - Activity Codes
   - NIS, NIF, AI, RC
   - Fax

## File Structure

```
l10n_dz_cpss_ext/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── activity_code.py        # Activity code management
│   ├── forme_juridique.py      # Legal forms
│   ├── res_company.py          # Company extensions
│   ├── res_partner.py          # Partner extensions
│   └── template_dz.py          # Chart template extensions
├── data/
│   ├── template/
│   │   └── account.account-dz.csv   # 1,160 additional accounts
│   └── company_function.xml         # Legal forms initialization
├── views/
│   ├── activity_code.xml
│   ├── forme_juridique.xml
│   ├── res_company.xml
│   ├── res_partner.xml
│   └── configuration_settings.xml
├── security/
│   └── ir.model.access.csv
└── i18n/
    └── fr.po                        # French translations
```

## Technical Details

### Models

| Model | Type | Description |
|-------|------|-------------|
| `activity.code` | New | Activity code management with tracking |
| `forme.juridique` | New | Legal form definitions |
| `res.company` | Inherit | Add Algerian fields and settings |
| `res.partner` | Inherit | Add Algerian fields |
| `account.chart.template` | Inherit | Load additional accounts |

### Dependencies

- `l10n_dz` - Native Algeria localization (base)
- `account` - Core accounting module
- `base_vat` - VAT number management
- `mail` - Activity tracking
- `sale` - Sales integration
- `sale_management` - Advanced sales features

## Comparison: l10n_dz_cpss vs l10n_dz_cpss_ext

| Feature | l10n_dz_cpss | l10n_dz_cpss_ext |
|---------|--------------|------------------|
| **Approach** | Replacement | Extension |
| **Depends on l10n_dz** | ❌ No | ✅ Yes |
| **Total Accounts** | 1,176 | 1,454 (294+1,160) |
| **Account Groups** | 973 custom | 68 native (reused) |
| **Tax Report** | Custom (142 records) | Native (simpler) |
| **Post-Init Hook** | ✅ Complex | ❌ None (simple) |
| **Modularity** | Standalone | Modular |
| **Use Case** | Full replacement | Extend native |

## Upgrade Path

### From l10n_dz_cpss to l10n_dz_cpss_ext

⚠️ **Warning**: This is a significant change. Test thoroughly in a staging environment.

1. **Backup your database**
2. Uninstall `l10n_dz_cpss`
3. Install native `l10n_dz` (if not already installed)
4. Install `l10n_dz_cpss_ext`
5. Verify account mappings
6. Test all accounting workflows

## Support & Contributions

For issues, questions, or contributions:
- Create an issue in the project repository
- Contact: support@yourcompany.com

## License

LGPL-3

## Credits

**Author**: Your Company
**Maintainer**: Your Name
**Version**: 19.0.1.0.0
**Odoo Version**: 19.0+

---

**Note**: This module extends the native Algeria localization. For a standalone replacement, use `l10n_dz_cpss` instead.
