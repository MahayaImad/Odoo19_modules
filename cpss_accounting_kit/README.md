# Kit Comptable Complet Algérie (CPSS)

## Description

Kit comptable complet pour Odoo 19 Community Edition, adapté aux normes comptables et fiscales algériennes (SCF - Système Comptable Financier).

Suite complète de fonctionnalités comptables avancées comprenant : rapports, gestion d'actifs, PDC, relances, et plus encore.

## Fonctionnalités

### 1. Rapports Comptables (15 rapports)

#### Rapports Financiers
- **Rapport Financier** : Personnalisable pour Bilan et Compte de Résultat SCF
- **Flux de Trésorerie** : Tableau des flux conforme au SCF

#### Grands Livres et Balances
- **Grand Livre Général** : Détail complet des écritures par compte
- **Grand Livre Partenaire** : Suivi clients/fournisseurs
- **Balance de Vérification** : Soldes débit/crédit par compte
- **Balance Âgée** : Créances/dettes par ancienneté (30j, 60j, 90j, 120j, +120j)

#### Livres Auxiliaires
- **Livre de Banque** : Opérations bancaires (comptes 512)
- **Livre de Caisse** : Opérations espèces (comptes 53)
- **Livre de Jour** : Journal chronologique quotidien

#### Rapports d'Analyse
- **Audit de Journal** : Contrôle par journal comptable
- **Rapport de Taxes** : TVA et taxes (pour déclaration G50)
- **Rapport d'Actifs** : Immobilisations et amortissements

### 2. Gestion des Actifs et Amortissements

**Fonctionnalités complètes** :
- Création et suivi des immobilisations
- Méthodes d'amortissement :
  * **Linéaire** : Conforme fiscalité algérienne
  * **Dégressif** : Avec facteur configurable
- Calcul automatique des dotations
- Génération des écritures d'amortissement
- Catégories d'actifs pré-configurées
- Prorata temporis
- Cessions d'actifs
- Rapport VNC (Valeur Nette Comptable)

**Comptes SCF utilisés** :
- Classe 2 : Immobilisations (21, 22, 23, 24, etc.)
- Compte 28 : Amortissements cumulés
- Compte 681 : Dotations aux amortissements

### 3. PDC - Chèques Différés

**Gestion complète des chèques à échéance** (très utilisés en Algérie) :
- PDC clients (entrées)
- PDC fournisseurs (sorties)
- Suivi par date d'effet
- Référence bancaire
- Référence du chèque
- Impression de chèques pré-numérotés
- Rapprochement bancaire PDC

**Utilisation** :
- Enregistrement de paiements avec date future
- Suivi des chèques non encore encaissés
- Rapprochement avec relevés bancaires

### 4. Relances Clients (Follow-ups)

**Système automatisé de relances** :
- Plans de relance configurables
- Niveaux de relance multiples
- Génération automatique
- Templates de communication personnalisables
- Suivi des impayés par ancienneté
- Historique des relances

### 5. Limite de Crédit

**Contrôle du risque client** :
- Définition de limites par client
- **Étape d'avertissement** : Alerte avant blocage
- **Étape de blocage** : Blocage automatique des factures
- Affichage du montant dû
- Activation par partenaire
- Gestion des exceptions

### 6. Écritures Récurrentes

**Automatisation des écritures périodiques** :
- Loyers
- Abonnements
- Charges fixes
- Planification via cron jobs
- Référence de récurrence
- Génération automatique

### 7. Import Bancaire

**Import de relevés** :
- Format OFX
- Format QIF
- Format Excel
- Rapprochement automatique
- Matching intelligent

## Installation

### Prérequis

**Obligatoires** :
- `l10n_dz_cpss_ext` : Plan comptable SCF algérien
- `cpss_account_budget` : Gestion budgétaire
- `account` : Comptabilité de base
- `sale` : Ventes
- `analytic` : Comptabilité analytique

**Recommandées** :
- `l10n_dz_on_timbre_fiscal` : Timbre fiscal algérien
- `l10n_dz_code_cnrc` : Codes d'activité CNRC

**Dépendances Python** :
```bash
pip install openpyxl ofxparse qifparse
```

### Installation

1. Installer les dépendances Python
2. Copier le module dans le dossier `addons`
3. Mettre à jour la liste des modules
4. Installer `cpss_accounting_kit`

## Configuration

### 1. Catégories d'Actifs (SCF Algérie)

**Menu** : Comptabilité > Configuration > Catégories d'Actifs

Exemples de catégories conformes à la fiscalité algérienne :

```
Bâtiments
---------
Compte actif : 213 (Bâtiments)
Compte amortissement : 2813
Compte charge : 681
Méthode : Linéaire
Durée : 20 ans (5%)

Matériel et Outillage
--------------------
Compte actif : 215
Compte amortissement : 2815
Compte charge : 681
Méthode : Linéaire
Durée : 5 ans (20%)

Matériel de Transport
--------------------
Compte actif : 218
Compte amortissement : 2818
Compte charge : 681
Méthode : Linéaire
Durée : 5 ans (20%)

Matériel de Bureau
-----------------
Compte actif : 2184
Compte amortissement : 28184
Compte charge : 681
Méthode : Linéaire
Durée : 10 ans (10%)

Matériel Informatique
--------------------
Compte actif : 2183
Compte amortissement : 28183
Compte charge : 681
Méthode : Linéaire
Durée : 3 ans (33,33%)
```

### 2. Configuration PDC

**Menu** : Comptabilité > Configuration > Journaux

1. Créer un journal pour PDC clients
2. Créer un journal pour PDC fournisseurs
3. Configurer les comptes par défaut

### 3. Plans de Relance

**Menu** : Comptabilité > Configuration > Relances > Plans de Relance

Exemple de plan :

```
Niveau 1 : +15 jours
---------
Type : Avertissement
Action : Email automatique
Message : "Rappel aimable de paiement"

Niveau 2 : +30 jours
---------
Type : Relance
Action : Email + Lettre
Message : "Relance de paiement"

Niveau 3 : +45 jours
---------
Type : Dernière relance
Action : Email + Courrier recommandé
Message : "Dernière relance avant action juridique"

Niveau 4 : +60 jours
---------
Type : Mise en demeure
Action : Courrier recommandé
Message : "Mise en demeure de payer"
```

### 4. Limite de Crédit

**Menu** : Comptabilité > Clients > Client > Onglet Comptabilité

Pour chaque client :
```
Activer la limite de crédit : ✓
Étape d'avertissement : 500 000 DZD
Étape de blocage : 1 000 000 DZD
```

## Utilisation

### Gestion des Actifs

#### Créer un Actif

1. **Menu** : Comptabilité > Comptabilité > Actifs > Créer
2. Remplir les informations :
   - Nom de l'actif
   - Catégorie (sélectionner)
   - Valeur brute
   - Date d'acquisition
   - Méthode d'amortissement
   - Nombre d'amortissements
3. **Confirmer** l'actif
4. Les écritures d'amortissement seront générées automatiquement

#### Exemple : Achat d'un Véhicule

```
Nom : Véhicule Renault Symbol
Catégorie : Matériel de Transport
Valeur brute : 3 500 000 DZD
Date : 01/03/2026
Méthode : Linéaire
Durée : 5 ans (60 mois)
Valeur résiduelle : 500 000 DZD

Calcul :
Montant amortissable : 3 500 000 - 500 000 = 3 000 000 DZD
Dotation annuelle : 3 000 000 / 5 = 600 000 DZD
Dotation mensuelle : 600 000 / 12 = 50 000 DZD
```

### Rapports

#### Grand Livre Général

**Menu** : Comptabilité > Rapports > Grand Livre Général

Options :
- Période : Date début - Date fin
- Tri : Par date ou par journal/partenaire
- Affichage : Tous / Avec mouvements / Solde non nul
- Solde initial : Oui/Non
- Filtres : Journaux, Comptes

#### Balance Âgée

**Menu** : Comptabilité > Rapports > Balance Âgée

Configuration :
- Type : Clients ou Fournisseurs
- Date de référence
- Période : 30 jours (modifiable)

Résultat :
```
Client XYZ
----------
Non échu : 150 000 DZD
1-30 j : 80 000 DZD
31-60 j : 45 000 DZD
61-90 j : 30 000 DZD
91-120 j : 0 DZD
+120 j : 25 000 DZD
Total : 330 000 DZD
```

#### Flux de Trésorerie (SCF)

**Menu** : Comptabilité > Rapports > Flux de Trésorerie

Catégories SCF :
1. **Activités Opérationnelles**
   - Encaissements clients
   - Décaissements fournisseurs
   - Charges de personnel

2. **Activités d'Investissement**
   - Acquisitions d'immobilisations
   - Cessions d'actifs

3. **Activités de Financement**
   - Emprunts
   - Remboursements
   - Dividendes

### PDC - Utilisation

#### Enregistrer un PDC Client

1. **Menu** : Comptabilité > Clients > Paiements > Créer
2. Type de paiement : Entrant
3. Méthode : PDC (Post-Dated Cheque)
4. Remplir :
   - Montant
   - Référence bancaire
   - Référence du chèque
   - **Date d'effet** : Date future d'encaissement
5. Confirmer

#### Enregistrer un PDC Fournisseur

1. **Menu** : Comptabilité > Fournisseurs > Paiements > Créer
2. Type de paiement : Sortant
3. Méthode : PDC
4. Remplir les informations
5. **Date d'effet** : Date de l'encaissement du chèque

## Adaptation Algérienne

### Plan Comptable SCF

Compatible avec tous les comptes SCF :

**Classes de comptes** :
- Classe 1 : Capitaux permanents
- Classe 2 : Immobilisations
- Classe 3 : Stocks et en-cours
- Classe 4 : Comptes de tiers
- Classe 5 : Comptes financiers
- Classe 6 : Charges
- Classe 7 : Produits

### Normes Fiscales

**Amortissements** :
- Taux fiscaux déductibles respectés
- Démarrage au 1er du mois d'acquisition
- Prorata temporis automatique

**TVA** :
- Taux normal : 19%
- Taux réduit : 9%
- TVA sur encaissement supportée
- Rapport TVA pour déclaration G50

**Conservation** :
- Documents conservés 10 ans minimum
- Tous les rapports exportables PDF

### États Financiers SCF

**Bilan** :
- Actif non courant
- Actif courant
- Passif non courant
- Passif courant
- Capitaux propres

**Compte de Résultat** :
- Produits d'exploitation
- Charges d'exploitation
- Résultat opérationnel
- Produits financiers
- Charges financières
- Résultat net

**Tableau des Flux** :
- Flux opérationnels
- Flux d'investissement
- Flux de financement
- Variation de trésorerie

## Déclarations Fiscales Algériennes

### Déclaration TVA (G50)

**Rapport** : Rapport de Taxes

Informations fournies :
- TVA collectée par taux
- TVA déductible sur immobilisations
- TVA déductible sur autres biens et services
- TVA à payer (ou crédit)

### Liasse Fiscale (Série G)

**Rapports utilisés** :
- Grand Livre Général
- Balance de Vérification
- Rapport Financier (Bilan + Compte de Résultat)
- Tableau des Flux de Trésorerie
- Rapport d'Actifs (Immobilisations)

### Déclaration Annuelle

**Documents générés** :
- Bilan fiscal (G n°4)
- Compte de résultat fiscal (G n°5)
- Tableau des amortissements (G n°7)
- Tableau des provisions (G n°8)

## Dépendances Techniques

### Modules Odoo

```python
depends = [
    'account',                    # Base comptable
    'sale',                       # Ventes
    'account_check_printing',     # Impression chèques
    'analytic',                   # Comptabilité analytique
    'contacts',                   # Partenaires
    'cpss_account_budget',        # Gestion budgétaire CPSS
    'l10n_dz_cpss_ext',          # Plan comptable SCF - OBLIGATOIRE
    'l10n_dz_on_timbre_fiscal',  # Timbre fiscal - RECOMMANDÉ
]
```

### Bibliothèques Python

```bash
pip install openpyxl    # Import/Export Excel
pip install ofxparse    # Import relevés OFX
pip install qifparse    # Import relevés QIF
```

## Support

- **Développeur** : CPSS
- **Basé sur** : Module original de Cybrosys Technologies
- **Licence** : LGPL-3
- **Version** : 19.0.2.0.0
- **Pays** : Algérie (DZ)

## Changelog

### Version 19.0.2.0.0 (2026-01-07)
- Adaptation initiale pour l'Algérie
- Traduction complète en français (4133 lignes)
- Intégration avec plan comptable SCF
- Documentation algérienne complète
- Dépendances adaptées aux modules algériens
- Configuration par défaut pour normes SCF
- Exemples et cas d'usage algériens

## Crédits

- **Module original** : Cybrosys Technologies
- **Adaptation algérienne** : CPSS - 2026
- **Conformité** : Normes SCF, Code des impôts, Loi de finances algérienne
- **Traduction** : Interface complète en français

## Licence

LGPL-3 (GNU Lesser General Public License version 3)

Ce module peut être librement utilisé, modifié et distribué selon les termes de la licence LGPL-3.

## Ressources

- [Système Comptable Financier (SCF)](http://www.finances.gov.dz)
- [Direction Générale des Impôts (DGI)](http://www.mfdgi.gov.dz)
- [Code des impôts directs et taxes assimilées](http://www.mfdgi.gov.dz)
- [Documentation Odoo](https://www.odoo.com/documentation/19.0)
