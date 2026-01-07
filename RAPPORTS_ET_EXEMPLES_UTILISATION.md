# Rapports et Exemples d'Utilisation des Modules Comptables

## Date : 2026-01-07

---

# PARTIE 1 : RAPPORTS GÉNÉRÉS PAR base_accounting_kit

## 📊 Vue d'Ensemble

Le module `base_accounting_kit` génère **15 rapports comptables** complets, organisés en 5 catégories principales.

---

## 1. RAPPORTS FINANCIERS (États Financiers)

### 1.1 Rapport Financier (Financial Report)
- **Fichier** : `report_financial.py`
- **Nom technique** : `report.base_accounting_kit.report_financial`
- **Description** : Rapport financier configurable et hiérarchique

**Fonctionnalités** :
- Structure hiérarchique des comptes
- Types de rapports :
  * **Sum** (Vue/Total)
  * **Accounts** (Comptes spécifiques)
  * **Account Type** (Type de compte)
  * **Account Report** (Valeur de rapport)
- Configuration du signe (normal ou inversé)
- Niveaux d'affichage (avec ou sans hiérarchie)
- Styles personnalisables

**Utilisation en Algérie** :
- Génération du **Bilan** (Actif/Passif)
- **Compte de Résultat** par nature
- États financiers conformes au SCF

**Paramètres** :
- Période (Date début - Date fin)
- Filtres de comparaison
- Affichage débit/crédit
- Comptes cibles

---

### 1.2 Rapport de Flux de Trésorerie (Cash Flow Report)
- **Fichier** : `cash_flow_report.py`
- **Nom technique** : `report.base_accounting_kit.report_cash_flow`
- **Description** : Tableau des flux de trésorerie

**Catégories de flux** :
1. **Activités Opérationnelles**
   - Encaissements d'exploitation (cash_in_from_operation)
   - Décaissements d'exploitation (cash_out_operation)

2. **Activités de Financement**
   - Entrées financières (cash_in_financial)
   - Sorties financières (cash_out_financial)

3. **Activités d'Investissement**
   - Encaissements d'investissement (cash_in_investing)
   - Décaissements d'investissement (cash_out_investing)

**Calculs** :
- Solde = Débit - Crédit (selon le type)
- Comparaison période N vs N-1
- Agrégation par type de compte

**Utilisation en Algérie** :
- Conforme aux exigences SCF
- Tableau des flux de trésorerie obligatoire
- Analyse de la liquidité

---

## 2. GRANDS LIVRES ET BALANCES

### 2.1 Grand Livre Général (General Ledger)
- **Fichier** : `general_ledger_report.py`
- **Nom technique** : `report.base_accounting_kit.report_general_ledger`
- **Description** : Grand livre comptable détaillé

**Informations affichées** :
- Code et nom du compte
- Date, libellé, référence
- Débit, crédit, solde
- Partenaire (client/fournisseur)
- Numéro de pièce (move_name)
- Devise et montant en devise

**Options** :
- **Solde initial** : Affichage du solde d'ouverture
- **Tri** :
  * Par date (sort_date)
  * Par journal et partenaire (sort_journal_partner)
- **Affichage des comptes** :
  * Tous (all)
  * Avec mouvements (movement)
  * Solde non nul (not_zero)
- **Filtres** : Journaux, comptes, partenaires

**Utilisation en Algérie** :
- Document obligatoire pour contrôle fiscal
- Conservation pendant 10 ans minimum
- Base pour déclarations fiscales

---

### 2.2 Grand Livre Partenaire (Partner Ledger)
- **Fichier** : `report_partner_ledger.py`
- **Nom technique** : `report.base_accounting_kit.report_partnerledger`
- **Description** : Grand livre par client/fournisseur

**Fonctionnalités** :
- Détail par partenaire
- Comptes clients (411...)
- Comptes fournisseurs (401...)
- Solde par partenaire
- Analyse du crédit client

**Utilisation** :
- Suivi des créances et dettes
- Lettrage des comptes
- Relance clients
- Contrôle fournisseurs

---

### 2.3 Balance de Vérification (Trial Balance)
- **Fichier** : `report_trial_balance.py`
- **Nom technique** : `report.base_accounting_kit.report_trial_balance`
- **Description** : Balance comptable (tous comptes)

**Colonnes** :
- Code compte
- Nom du compte
- Débit total
- Crédit total
- Solde (Débit - Crédit)

**Calcul** :
```sql
SELECT account_id,
       SUM(debit) AS debit,
       SUM(credit) AS credit,
       (SUM(debit) - SUM(credit)) AS balance
FROM account_move_line
WHERE ...
GROUP BY account_id
```

**Options d'affichage** :
- **all** : Tous les comptes
- **not_zero** : Comptes avec solde ≠ 0
- **movement** : Comptes avec mouvements

**Utilisation en Algérie** :
- Document de contrôle périodique
- Vérification de l'équilibre comptable
- Préparation des états financiers
- Base pour la balance âgée

---

### 2.4 Balance Âgée (Aged Partner Balance)
- **Fichier** : `report_aged_partner.py`
- **Nom technique** : `report.base_accounting_kit.report_agedpartnerbalance`
- **Description** : Balance par ancienneté de créances/dettes

**Périodes d'ancienneté** (configurable) :
- 1-30 jours
- 31-60 jours
- 61-90 jours
- 91-120 jours
- +120 jours (> 4 mois)
- Non échu

**Calculs** :
- Date de référence : Date du rapport
- Période = Date échéance - Date de référence
- Classification automatique par tranche
- Prise en compte du lettrage partiel

**Types** :
- **Customer** : Créances clients (compte 411)
- **Supplier** : Dettes fournisseurs (compte 401)
- **Both** : Les deux

**Utilisation** :
- Gestion du crédit client
- Suivi des impayés
- Analyse du BFR (Besoin en Fonds de Roulement)
- Relances automatiques

---

## 3. LIVRES AUXILIAIRES

### 3.1 Livre de Banque (Bank Book)
- **Fichier** : `account_bank_book.py`
- **Nom technique** : `report.base_accounting_kit.report_bank_book`
- **Description** : Journal des opérations bancaires

**Contenu** :
- Toutes les écritures des comptes bancaires
- Solde initial
- Débit/Crédit
- Solde cumulé
- Référence bancaire
- Partenaire

**Sélection automatique** :
- Journaux de type "Banque"
- Comptes bancaires (compte 512xxx)

**Utilisation** :
- Rapprochement bancaire
- Suivi de trésorerie
- Contrôle des relevés bancaires

---

### 3.2 Livre de Caisse (Cash Book)
- **Fichier** : `account_cash_book.py`
- **Nom technique** : `report.base_accounting_kit.report_cash_book`
- **Description** : Journal des opérations de caisse

**Contenu** :
- Écritures des comptes de caisse
- Encaissements
- Décaissements
- Solde de caisse

**Comptes concernés** :
- 53xxx : Caisse

**Utilisation** :
- Contrôle quotidien de caisse
- Arrêté de caisse
- Justification des espèces

---

### 3.3 Journal/Livre de Jour (Day Book)
- **Fichier** : `account_day_book.py`
- **Nom technique** : `report.base_accounting_kit.report_day_book`
- **Description** : Journal chronologique quotidien

**Affichage** :
- Toutes les écritures d'une période
- Ordre chronologique
- Par journal
- Numéro de pièce
- Libellé complet

**Utilisation** :
- Vue d'ensemble quotidienne
- Contrôle de saisie
- Audit des écritures

---

## 4. RAPPORTS D'ANALYSE

### 4.1 Audit de Journal (Journal Audit)
- **Fichier** : `report_journal_audit.py`
- **Nom technique** : `report.base_accounting_kit.report_journal_audit`
- **Description** : Rapport d'audit par journal comptable

**Fonctionnalités** :
- Analyse par journal
- Détail des écritures
- Totaux par journal
- Vérification de l'équilibre

**Utilisation** :
- Contrôle interne
- Audit comptable
- Revue périodique

---

### 4.2 Rapport de Taxes (Tax Report)
- **Fichier** : `report_tax.py`
- **Nom technique** : `report.base_accounting_kit.report_tax`
- **Description** : Rapport des taxes (TVA, etc.)

**Informations** :
- Base taxable
- Montant de taxe
- Par type de taxe
- Par période

**Utilisation en Algérie** :
- Préparation déclaration TVA (G50)
- Contrôle des taxes déductibles/collectées
- Calcul TVA à payer
- TVA sur encaissement vs facturation

---

### 4.3 Rapport d'Actifs (Asset Report)
- **Fichier** : `account_asset_report.py`
- **Nom technique** : Rapport des immobilisations
- **Description** : État des actifs et amortissements

**Informations** :
- Liste des actifs
- Valeur brute
- Amortissements cumulés
- Valeur nette comptable (VNC)
- État des cessions

**Utilisation** :
- Inventaire des immobilisations
- Calcul des dotations
- Déclarations fiscales (série G)

---

## 5. RAPPORTS SPÉCIAUX

### 5.1 Factures Multiples (Multiple Invoice Report)
- **Fichier** : `multiple_invoice_report.py`
- **Description** : Impression groupée de factures

**Fonctionnalités** :
- Layouts personnalisables
- Templates multiples
- Impression en masse

---

### 5.2 Rapport Commun Comptes (Common Account Report)
- **Fichier** : `account_report_common_account.py`
- **Description** : Classe de base pour les rapports comptables

**Fonction** :
- Héritage pour autres rapports
- Méthodes communes
- Filtres standards

---

# PARTIE 2 : base_account_budget - EXEMPLES D'UTILISATION

## 🎯 Concepts Fondamentaux

### Architecture du Module

```
Budget (budget.budget)
    │
    ├─► Lignes de Budget (budget.lines)
    │       │
    │       ├─► Position Budgétaire (account.budget.post)
    │       │       └─► Comptes Comptables (account.account)
    │       │
    │       └─► Compte Analytique (account.analytic.account)
    │
    └─► Workflow : Draft → Confirm → Validate → Done
```

---

## 📋 EXEMPLE 1 : Budget Annuel d'une Entreprise Algérienne

### Contexte
**Entreprise** : SARL "Industrie du Nord"
**Activité** : Fabrication de pièces métalliques
**Année fiscale** : 2026 (01/01/2026 - 31/12/2026)
**Objectif** : Contrôler les dépenses par département

### Étape 1 : Créer les Positions Budgétaires

#### Position 1 : Charges de Personnel
```
Nom : Charges de Personnel
Comptes associés :
  - 631 : Salaires et traitements
  - 632 : Charges sociales
  - 633 : Autres charges de personnel
```

#### Position 2 : Achats de Matières Premières
```
Nom : Achats Matières Premières
Comptes associés :
  - 601 : Achats de matières premières
  - 608 : Achats d'emballages
```

#### Position 3 : Charges Externes
```
Nom : Charges Externes
Comptes associés :
  - 611 : Sous-traitance générale
  - 613 : Locations
  - 615 : Entretien et réparations
  - 616 : Primes d'assurance
  - 618 : Services extérieurs
```

#### Position 4 : Dotations aux Amortissements
```
Nom : Dotations aux Amortissements
Comptes associés :
  - 681 : Dotations aux amortissements
```

### Étape 2 : Créer les Comptes Analytiques (Centres de Coûts)

```
Département Production :
  - Code : DEPT-PROD
  - Nom : Département Production

Département Commercial :
  - Code : DEPT-COM
  - Nom : Département Commercial

Département Administratif :
  - Code : DEPT-ADM
  - Nom : Département Administratif
```

### Étape 3 : Créer le Budget Principal

**Navigation** : Comptabilité → Comptabilité → Budgets → Créer

```
Nom du Budget : Budget 2026 - Industrie du Nord
Responsable : Directeur Financier
Période :
  - Date début : 01/01/2026
  - Date fin : 31/12/2026
État : Brouillon
```

### Étape 4 : Définir les Lignes Budgétaires

#### Ligne 1 : Charges de Personnel - Production
```
Position Budgétaire : Charges de Personnel
Compte Analytique : DEPT-PROD (Production)
Période : 01/01/2026 - 31/12/2026
Montant Planifié : 8 400 000 DZD
  (15 employés × 35 000 DZD/mois × 16 mois avec charges)

Calcul automatique :
  - Montant Pratique : (calculé en temps réel)
  - Montant Théorique : (proportionnel au temps écoulé)
  - Pourcentage : (Pratique / Théorique × 100)
```

#### Ligne 2 : Charges de Personnel - Commercial
```
Position Budgétaire : Charges de Personnel
Compte Analytique : DEPT-COM (Commercial)
Période : 01/01/2026 - 31/12/2026
Montant Planifié : 2 100 000 DZD
```

#### Ligne 3 : Achats Matières Premières - Production
```
Position Budgétaire : Achats Matières Premières
Compte Analytique : DEPT-PROD (Production)
Période : 01/01/2026 - 31/12/2026
Montant Planifié : 12 000 000 DZD
```

#### Ligne 4 : Charges Externes - Administratif
```
Position Budgétaire : Charges Externes
Compte Analytique : DEPT-ADM (Administratif)
Période : 01/01/2026 - 31/12/2026
Montant Planifié : 1 800 000 DZD
```

### Étape 5 : Workflow de Validation

#### 1. Confirmer le Budget
**Action** : Bouton "Confirm"
**État** : Draft → Confirm
**Effet** : Le budget est soumis pour approbation

#### 2. Approuver le Budget
**Action** : Bouton "Approve"
**État** : Confirm → Validate
**Effet** : Le budget est validé et actif

#### 3. Clôturer le Budget
**Action** : Bouton "Done" (en fin d'année)
**État** : Validate → Done
**Effet** : Le budget est terminé et archivé

---

## 📊 EXEMPLE 2 : Suivi Budgétaire Trimestriel

### Contexte
**Période** : T1 2026 (01/01/2026 - 31/03/2026)
**Objectif** : Budget trimestriel avec suivi mensuel

### Configuration du Budget

```
Nom : Budget T1 2026 - Marketing
Responsable : Directeur Marketing
Période : 01/01/2026 - 31/03/2026
```

### Lignes Budgétaires Mensuelles

#### Janvier 2026 - Publicité
```
Position Budgétaire : Charges Externes (compte 623 - Publicité)
Compte Analytique : DEPT-COM
Période : 01/01/2026 - 31/01/2026
Montant Planifié : 500 000 DZD
```

#### Février 2026 - Publicité
```
Position Budgétaire : Charges Externes
Compte Analytique : DEPT-COM
Période : 01/02/2026 - 28/02/2026
Montant Planifié : 600 000 DZD
```

#### Mars 2026 - Publicité
```
Position Budgétaire : Charges Externes
Compte Analytique : DEPT-COM
Période : 01/03/2026 - 31/03/2026
Montant Planifié : 700 000 DZD
```

### Simulation de Suivi (au 15 Février 2026)

#### Ligne Janvier (Terminée)
```
Montant Planifié : 500 000 DZD
Montant Pratique : 485 000 DZD (dépenses réelles)
Montant Théorique : 500 000 DZD (période terminée)
Pourcentage : 97% (485k / 500k)
✅ Statut : Économie de 15 000 DZD
```

#### Ligne Février (En cours)
```
Montant Planifié : 600 000 DZD
Montant Pratique : 420 000 DZD (dépenses au 15/02)
Montant Théorique : 321 429 DZD
  Calcul : 600 000 × (15 jours / 28 jours)
Pourcentage : 130,7% (420k / 321k)
⚠️ Statut : Dépassement de 30,7% !
```

#### Ligne Mars (Pas commencée)
```
Montant Planifié : 700 000 DZD
Montant Pratique : 0 DZD
Montant Théorique : 0 DZD (pas encore commencé)
Pourcentage : 0%
```

---

## 📈 EXEMPLE 3 : Budget de Projet

### Contexte
**Projet** : Construction d'un nouveau hangar
**Durée** : 6 mois (01/03/2026 - 31/08/2026)
**Budget** : 15 000 000 DZD

### Compte Analytique Projet
```
Code : PROJET-HANGAR-2026
Nom : Construction Hangar - 2026
Type : Projet
```

### Positions Budgétaires Spécifiques

#### Position : Travaux de Construction
```
Nom : Travaux de Construction
Comptes :
  - 222 : Bâtiments
  - 605 : Achats de matériaux
```

#### Position : Honoraires et Études
```
Nom : Honoraires et Études
Comptes :
  - 622 : Honoraires (architecte, ingénieur)
```

### Budget du Projet

```
Nom : Projet Hangar 2026
Responsable : Chef de Projet
Période : 01/03/2026 - 31/08/2026
```

### Lignes Budgétaires

#### Phase 1 : Études et Autorisations (Mars)
```
Position : Honoraires et Études
Compte Analytique : PROJET-HANGAR-2026
Période : 01/03/2026 - 31/03/2026
Montant Planifié : 800 000 DZD
```

#### Phase 2 : Fondations (Avril-Mai)
```
Position : Travaux de Construction
Compte Analytique : PROJET-HANGAR-2026
Période : 01/04/2026 - 31/05/2026
Montant Planifié : 5 000 000 DZD
```

#### Phase 3 : Structure (Juin-Juillet)
```
Position : Travaux de Construction
Compte Analytique : PROJET-HANGAR-2026
Période : 01/06/2026 - 31/07/2026
Montant Planifié : 7 000 000 DZD
```

#### Phase 4 : Finitions (Août)
```
Position : Travaux de Construction
Compte Analytique : PROJET-HANGAR-2026
Période : 01/08/2026 - 31/08/2026
Montant Planifié : 2 200 000 DZD
```

**Total Budget** : 15 000 000 DZD

---

## 🔍 EXEMPLE 4 : Analyse des Écarts Budgétaires

### Cas Pratique : Département Commercial (Juin 2026)

#### Données du Budget
```
Ligne Budgétaire : Frais de Déplacement
Position : Charges Externes (compte 625)
Compte Analytique : DEPT-COM
Période : 01/06/2026 - 30/06/2026 (30 jours)
Montant Planifié : 450 000 DZD
```

#### Situation au 20 Juin 2026 (20 jours écoulés)

**Calcul du Montant Théorique** :
```
Jours écoulés : 20 jours
Jours totaux : 30 jours
Montant Théorique = 450 000 × (20/30) = 300 000 DZD
```

**Dépenses Réelles** :
```
05/06 : Déplacement Alger-Oran : 45 000 DZD
08/06 : Mission Constantine : 75 000 DZD
12/06 : Frais hôtel : 30 000 DZD
15/06 : Carburant : 25 000 DZD
18/06 : Déplacement Annaba : 85 000 DZD
Total : 260 000 DZD
```

**Résultats Affichés** :
```
Montant Planifié : 450 000 DZD
Montant Pratique : 260 000 DZD
Montant Théorique : 300 000 DZD
Pourcentage : 86,67% (260k / 300k)
```

**Interprétation** :
- ✅ **Sous budget** : 13,33% d'économie
- Projection fin de mois : 390 000 DZD (260k × 30/20)
- Économie prévue : 60 000 DZD

#### Cas de Dépassement

**Situation au 25 Juin (25 jours écoulés)** :
```
Dépenses cumulées : 470 000 DZD

Montant Théorique = 450 000 × (25/30) = 375 000 DZD
Pourcentage = 470 000 / 375 000 = 125,3%
```

**Alerte** :
- ⚠️ **Dépassement de 25,3%**
- Dépassement absolu : 95 000 DZD
- Projection fin de mois : 564 000 DZD
- Dépassement prévu : 114 000 DZD

**Actions correctives** :
1. Limiter les déplacements non essentiels
2. Privilégier les visioconférences
3. Demande d'ajustement budgétaire

---

## 💡 EXEMPLE 5 : Budget Multi-Départements

### Contexte
**Entreprise** : Groupe "TechnoSud"
**Départements** : 4 centres de profit
**Période** : Semestre 1 2026

### Structure Analytique

```
└─ Groupe TechnoSud
    ├─ Production (DEPT-PROD)
    ├─ Commercial (DEPT-COM)
    ├─ R&D (DEPT-RD)
    └─ Administration (DEPT-ADM)
```

### Budget Global

```
Nom : Budget S1 2026 - Groupe TechnoSud
Période : 01/01/2026 - 30/06/2026
Responsable : DAF
```

### Répartition par Département

#### Production
```
Ligne 1 : Matières Premières
  - Position : Achats MP
  - Analytique : DEPT-PROD
  - Montant : 18 000 000 DZD

Ligne 2 : Charges de Personnel
  - Position : Personnel
  - Analytique : DEPT-PROD
  - Montant : 6 000 000 DZD

Ligne 3 : Maintenance
  - Position : Charges Externes
  - Analytique : DEPT-PROD
  - Montant : 1 200 000 DZD

Total Production : 25 200 000 DZD
```

#### Commercial
```
Ligne 4 : Salaires Commerciaux
  - Position : Personnel
  - Analytique : DEPT-COM
  - Montant : 2 400 000 DZD

Ligne 5 : Marketing & Publicité
  - Position : Charges Externes
  - Analytique : DEPT-COM
  - Montant : 1 800 000 DZD

Ligne 6 : Commissions
  - Position : Personnel (633)
  - Analytique : DEPT-COM
  - Montant : 3 000 000 DZD

Total Commercial : 7 200 000 DZD
```

#### R&D
```
Ligne 7 : Salaires Ingénieurs
  - Position : Personnel
  - Analytique : DEPT-RD
  - Montant : 3 600 000 DZD

Ligne 8 : Matériel de Labo
  - Position : Achats Équipements
  - Analytique : DEPT-RD
  - Montant : 800 000 DZD

Total R&D : 4 400 000 DZD
```

#### Administration
```
Ligne 9 : Personnel Administratif
  - Position : Personnel
  - Analytique : DEPT-ADM
  - Montant : 1 800 000 DZD

Ligne 10 : Frais Généraux
  - Position : Charges Externes
  - Analytique : DEPT-ADM
  - Montant : 1 200 000 DZD

Total Administration : 3 000 000 DZD
```

**BUDGET TOTAL** : 39 800 000 DZD

### Tableau de Bord (Fin Mars 2026)

| Département | Budget S1 | Réalisé T1 | Théorique T1 | % Réal. | Statut |
|-------------|-----------|------------|--------------|---------|--------|
| Production | 25 200 000 | 12 100 000 | 12 600 000 | 96% | ✅ OK |
| Commercial | 7 200 000 | 4 500 000 | 3 600 000 | 125% | ⚠️ Alerte |
| R&D | 4 400 000 | 2 000 000 | 2 200 000 | 91% | ✅ OK |
| Administration | 3 000 000 | 1 400 000 | 1 500 000 | 93% | ✅ OK |
| **TOTAL** | **39 800 000** | **20 000 000** | **19 900 000** | **100,5%** | ⚠️ |

**Analyse** :
- Production : Légère économie
- **Commercial : Dépassement de 25%** → Action requise
- R&D : Économie de 9%
- Administration : Conforme

---

## 🎓 BONNES PRATIQUES

### 1. Structuration des Budgets

✅ **À FAIRE** :
- Créer des positions budgétaires par nature de dépense
- Utiliser les comptes analytiques pour les centres de coûts
- Définir des périodes cohérentes (mois, trimestre, année)
- Valider le budget avant le début de la période

❌ **À ÉVITER** :
- Mélanger plusieurs types de dépenses dans une ligne
- Créer des lignes budgétaires trop courtes (< 1 mois)
- Modifier un budget validé sans traçabilité

### 2. Suivi Budgétaire

✅ **Fréquence recommandée** :
- **Hebdomadaire** : Projets critiques
- **Mensuel** : Budgets opérationnels
- **Trimestriel** : Budgets stratégiques

### 3. Seuils d'Alerte

```
Pourcentage < 80%  : ✅ Très bon (économie)
80% ≤ % < 95%     : ✅ Bon
95% ≤ % ≤ 105%    : 🟡 Normal
105% < % ≤ 115%   : ⚠️ Attention
% > 115%          : 🔴 Dépassement critique
```

### 4. Actions Correctives

**Si dépassement > 10%** :
1. Analyser les causes (dérive des prix, volumes, etc.)
2. Identifier les postes problématiques
3. Mettre en place un plan d'action
4. Demander un ajustement budgétaire si nécessaire

### 5. Rapports Budgétaires

**Accès aux lignes budgétaires** :
- Menu : Comptabilité → Reporting → Lignes Budgétaires
- Filtres : Par compte analytique, période, position
- Export Excel pour analyses approfondies

---

## 📌 FORMULES DE CALCUL

### Montant Théorique

#### Si budget en cours :
```
Jours écoulés = Date du jour - Date début
Jours totaux = Date fin - Date début
Montant Théorique = Montant Planifié × (Jours écoulés / Jours totaux)
```

#### Si budget terminé :
```
Montant Théorique = Montant Planifié
```

#### Si budget non commencé :
```
Montant Théorique = 0
```

### Montant Pratique

```sql
SELECT SUM(amount)
FROM account_analytic_line
WHERE account_id = <compte_analytique>
  AND date BETWEEN <date_début> AND <date_fin>
  AND general_account_id IN (<comptes_position_budgétaire>)
```

### Pourcentage de Réalisation

```
Pourcentage = (Montant Pratique / Montant Théorique) × 100

Avec limite : MAX(0%, MIN(100%, pourcentage))
```

---

## 🔗 INTÉGRATION AVEC COMPTABILITÉ ALGÉRIENNE

### Comptes SCF Typiques

#### Charges d'Exploitation
```
60 : Achats consommés
  601 : Matières premières
  602 : Autres approvisionnements

61-62 : Services extérieurs
  611 : Sous-traitance
  613 : Locations
  615 : Entretien
  623 : Publicité
  625 : Déplacements

63 : Charges de personnel
  631 : Salaires
  632 : Charges sociales
```

#### Dotations aux Amortissements
```
68 : Dotations
  681 : Dotations aux amortissements
  686 : Dotations aux provisions
```

#### Charges Financières
```
66 : Charges financières
  661 : Charges d'intérêts
  665 : Charges sur cessions VMP
```

### Exemple de Mapping Budget-PCN

| Position Budgétaire | Comptes SCF | Usage |
|---------------------|-------------|-------|
| Achats Matières | 601, 602 | Approvisionnements |
| Services Externes | 611-618 | Sous-traitance, locations |
| Personnel | 631-638 | Salaires et charges |
| Amortissements | 681 | Dotations annuelles |
| Charges Financières | 661-668 | Intérêts, agios |

---

## 📞 CONCLUSION

### Avantages de base_account_budget

✅ **Simplicité** : Interface intuitive
✅ **Flexibilité** : Multi-périodes, multi-départements
✅ **Temps réel** : Calculs automatiques
✅ **Traçabilité** : Workflow de validation
✅ **Analytique** : Intégration comptes analytiques
✅ **Alertes** : Pourcentages visuels

### Complémentarité avec base_accounting_kit

Les rapports de `base_accounting_kit` (Grand Livre, Balance) fournissent les données sources pour l'analyse budgétaire.

**Workflow recommandé** :
1. Définir le budget dans `base_account_budget`
2. Saisir les opérations comptables normalement
3. Générer les rapports avec `base_accounting_kit`
4. Analyser les écarts budgétaires
5. Prendre des actions correctives

---

**Document préparé le** : 2026-01-07
**Version** : 1.0
**Pour** : Odoo 19 Community - Modules Comptables Algérie
