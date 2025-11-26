# Plan Comptable Algérien - CPSS (Odoo 19)

Module de localisation comptable pour l'Algérie conforme au **Système Comptable et Financier (SCF)** algérien.

## 📋 Fonctionnalités

### Plan Comptable Complet
- **973 groupes de comptes** hiérarchiques
- **1183 comptes comptables** détaillés
- Conforme au SCF algérien (Classes 1 à 7)
- Structure hiérarchique complète

### Gestion des Informations Fiscales
- **Codes d'activité** (CNRC)
- **Formes juridiques** algériennes (SARL, EURL, SPA, SNC, SCS, SCPA, etc.)
- Champs fiscaux spécifiques :
  - NIS (Numéro d'Identification Statistique)
  - NIF (Numéro d'Identification Fiscale)
  - AI (Article d'Imposition)
  - RC (Registre du Commerce)
  - Capital Social
  - Fax

### Taxes et Positions Fiscales
- TVA 19% (standard)
- TVA 9% (réduit)
- Positions fiscales pour Import/Export
- Rapports fiscaux conformes

### Interface Adaptée
- Placeholder "Wilaya" au lieu de "État"
- Configuration d'affichage du secteur/code d'activité sur factures et devis
- Menus de rapports algériens

## 🚀 Installation

### 1. Copier le module
```bash
cp -r l10n_dz_cpss /chemin/vers/odoo/addons/
```

### 2. Mettre à jour la liste des modules
Dans Odoo :
- Aller dans **Apps**
- Cliquer sur **Mettre à jour la liste des applications**

### 3. Installer le module
- Rechercher "**Algérie - CPSS**" ou "**l10n_dz_cpss**"
- Cliquer sur **Installer**

OU via la ligne de commande :
```bash
odoo-bin -u l10n_dz_cpss -d votre_base_de_donnees
```

## 📊 Appliquer le Plan Comptable

### Méthode 1 : Nouvelle Société
1. Aller dans **Paramètres > Utilisateurs et Sociétés > Sociétés**
2. Créer une nouvelle société
3. Sélectionner **Pays : Algérie (DZ)**
4. Le plan comptable s'applique automatiquement

### Méthode 2 : Société Existante
1. Aller dans **Comptabilité > Configuration > Paramètres**
2. Section **Comptabilité fiscale**
3. Sélectionner **Pays fiscal : Algérie**
4. Cliquer sur **Installer le plan comptable**

### Méthode 3 : Configuration Manuelle
1. Aller dans **Comptabilité > Configuration > Plan comptable**
2. Cliquer sur **Importer depuis un modèle**
3. Sélectionner "**Algérie - CPSS**"

## 🔧 Configuration

### Codes d'Activité
Menu : **Comptabilité > Configuration > Code d'activité**
- Créer et gérer les codes d'activité CNRC
- Marquer le code principal
- Indiquer la réglementation

### Informations Société
Menu : **Paramètres > Sociétés**
- Remplir NIS, NIF, AI, RC
- Sélectionner la forme juridique
- Ajouter les codes d'activité
- Définir le capital social

### Informations Partenaires/Clients
Menu : **Contacts**
- Section **Information fiscale** (pour les sociétés)
- Ajouter NIS, NIF, AI, RC
- Codes d'activité
- Position fiscale

### Options d'Affichage
Menu : **Comptabilité > Configuration > Paramètres**
- Afficher secteur d'activité sur factures/devis
- Afficher code d'activité sur factures/devis

## 📁 Structure du Module

```
l10n_dz_cpss/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   ├── company_function.xml      # Initialisation formes juridiques
│   ├── tax_report.xml             # Rapports de taxes
│   └── template/
│       ├── account.account-dz.csv        # 1183 comptes
│       ├── account.group-dz.csv          # 973 groupes
│       ├── account.tax-dz.csv            # 168 taxes
│       ├── account.tax.group-dz.csv      # 3 groupes de taxes
│       └── account.fiscal.position-dz.csv # 4 positions fiscales
├── models/
│   ├── __init__.py
│   ├── template_dz.py            # Template du plan comptable
│   ├── activity_code.py          # Code d'activité
│   ├── forme_juridique.py        # Forme juridique
│   ├── res_company.py            # Extensions société
│   └── res_partner.py            # Extensions partenaire
├── views/
│   ├── activity_code.xml
│   ├── forme_juridique.xml
│   ├── res_company.xml
│   ├── res_partner.xml
│   └── configuration_settings.xml
├── security/
│   └── ir.model.access.csv
└── demo/
    └── demo_company.xml
```

## 🎯 Comptes Principaux

### Comptes de Bilan
- **10x** : Capitaux propres
- **15x-18x** : Dettes
- **20x-29x** : Immobilisations
- **30x-39x** : Stocks
- **40x-49x** : Tiers (clients/fournisseurs)
- **50x-59x** : Comptes financiers

### Comptes de Gestion
- **60x-68x** : Charges
- **70x-78x** : Produits

### Comptes par Défaut Configurés
- **401** : Fournisseurs (payable)
- **413** : Clients - Effets à recevoir (receivable)
- **412** : Clients - Retenues de garantie (POS)
- **31** : Matières premières et fournitures (stock)
- **512** : Banques (préfixe)
- **53** : Caisse (préfixe)
- **58** : Virements internes (préfixe)
- **600** : Achats de marchandises (expense)
- **700** : Ventes de marchandises (income)
- **666** : Pertes de change
- **766** : Gains de change

## 🐛 Dépannage

### Le plan comptable n'apparaît pas
1. Vérifier que le module est installé :
   - Apps > Rechercher "l10n_dz_cpss"
   - Statut : "Installé"

2. Mettre à jour le module :
   ```bash
   odoo-bin -u l10n_dz_cpss -d votre_base --stop-after-init
   ```

3. Redémarrer Odoo complètement

4. Vérifier les logs Odoo pour les erreurs

5. Exécuter le diagnostic :
   ```bash
   python3 diagnostic.py
   ```

### Erreurs lors de l'installation
- Vérifier que tous les modules dépendants sont installés :
  - `base_vat`
  - `account`
  - `sale`
  - `sale_management`

## 📝 Licence

LGPL-3

## 👥 Auteurs

- **CPSS** - Développement et maintenance
- **Osis** - Plan comptable initial (remerciements)

## 📧 Support

Pour toute question ou problème :
- Site web : https://www.cpss-dz.com
- Documentation Odoo : https://www.odoo.com/documentation/19.0/

## 🔄 Historique des Versions

### Version 19.0.1.0
- Plan comptable complet (973 groupes, 1183 comptes)
- Gestion des codes d'activité et formes juridiques
- Informations fiscales algériennes (NIS, NIF, AI, RC)
- Configuration d'affichage sur documents
- Interface adaptée au contexte algérien
