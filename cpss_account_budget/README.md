# Gestion Budgétaire Algérie (CPSS)

## Description

Module de gestion budgétaire adapté aux normes comptables algériennes (SCF) pour Odoo 19 Community Edition.

## Fonctionnalités

### Positions Budgétaires
- Création de positions budgétaires liées aux comptes du plan comptable SCF
- Association multiple avec les comptes comptables
- Gestion multi-sociétés

### Budgets
- Définition de budgets avec période (année fiscale algérienne: janvier-décembre)
- Workflow de validation : Brouillon → Confirmé → Validé → Terminé
- Annulation possible
- Suivi par responsable

### Lignes Budgétaires
- Montant planifié par position et compte analytique
- **Calcul automatique du montant pratique** (dépenses réelles)
- **Calcul automatique du montant théorique** (proportionnel au temps écoulé)
- **Pourcentage de réalisation** en temps réel
- Date de paiement optionnelle

### Comptes Analytiques
- Suivi par département
- Suivi par projet
- Suivi par centre de coût
- Compatible avec la structure analytique algérienne

## Installation

### Prérequis

**Obligatoire :**
- `l10n_dz_cpss_ext` : Plan comptable SCF algérien
- `analytic` : Comptabilité analytique

**Recommandé :**
- `l10n_dz_on_timbre_fiscal` : Timbre fiscal
- `l10n_dz_code_cnrc` : Codes d'activité CNRC

### Installation

1. Copier le module dans le dossier `addons`
2. Mettre à jour la liste des modules
3. Installer `cpss_account_budget`

## Configuration

### 1. Créer des Positions Budgétaires

**Menu** : Comptabilité > Configuration > Positions Budgétaires

Exemples de positions pour l'Algérie :

```
Position: Charges de Personnel
Comptes: 631, 632, 633, 634, 635, 636, 637, 638

Position: Achats de Matières Premières
Comptes: 601, 602

Position: Services Extérieurs
Comptes: 611, 612, 613, 614, 615, 616, 617, 618

Position: Dotations aux Amortissements
Comptes: 681, 682

Position: Charges Financières
Comptes: 661, 662, 665, 666, 667, 668
```

### 2. Créer des Comptes Analytiques

**Menu** : Comptabilité > Configuration > Analytique > Comptes Analytiques

Exemples :
```
DEPT-PROD : Département Production
DEPT-COM  : Département Commercial
DEPT-ADM  : Département Administration
DEPT-RD   : Département R&D
PROJET-X  : Projet Construction Hangar
```

### 3. Créer un Budget

**Menu** : Comptabilité > Comptabilité > Budgets > Créer

1. Nom du budget : `Budget 2026 - Entreprise`
2. Responsable : Directeur Financier
3. Période : 01/01/2026 - 31/12/2026
4. Ajouter des lignes budgétaires :
   - Position budgétaire
   - Compte analytique
   - Période
   - Montant planifié

### 4. Workflow de Validation

1. **Brouillon** : Création et modification libre
2. **Confirmer** : Soumettre pour approbation
3. **Valider** : Approuver le budget (actif)
4. **Terminé** : Clôturer le budget en fin de période

## Utilisation

### Suivi Budgétaire

**Menu** : Comptabilité > Reporting > Lignes Budgétaires

Colonnes affichées :
- Budget
- Position budgétaire
- Compte analytique
- Période
- **Montant planifié** : Budget initial
- **Montant pratique** : Dépenses réelles (calculé automatiquement)
- **Montant théorique** : Budget proportionnel au temps écoulé
- **Pourcentage** : Pratique / Théorique × 100

### Interprétation du Pourcentage

- **< 80%** : Très bonne gestion (économie)
- **80-95%** : Bonne gestion
- **95-105%** : Normal (conforme)
- **105-115%** : Attention (léger dépassement)
- **> 115%** : Alerte (dépassement important)

### Exemple de Calcul

**Budget** : Frais de Déplacement - Juin 2026
- Montant planifié : 450 000 DZD
- Période : 01/06/2026 - 30/06/2026 (30 jours)

**Au 20 Juin** (20 jours écoulés) :
- Dépenses réelles : 260 000 DZD
- Montant théorique = 450 000 × (20/30) = 300 000 DZD
- Pourcentage = (260 000 / 300 000) × 100 = **86,67%**
- Statut : ✅ Sous budget (économie de 13,33%)

## Adaptation Algérienne

### Plan Comptable SCF

Le module est compatible avec le plan comptable SCF (Système Comptable Financier) algérien :

**Classes de comptes :**
- Classe 1 : Comptes de capitaux
- Classe 2 : Comptes d'immobilisations
- Classe 3 : Comptes de stocks
- Classe 4 : Comptes de tiers
- Classe 5 : Comptes financiers
- Classe 6 : Comptes de charges
- Classe 7 : Comptes de produits

### Année Fiscale

L'année fiscale algérienne est l'année civile :
- Début : 1er janvier
- Fin : 31 décembre
- Clôture fiscale : 30 avril N+1

### Organismes Publics

Pour les organismes publics algériens :
- Respect de la nomenclature budgétaire de l'État
- Suivi par chapitre/article/paragraphe
- Utilisation des comptes analytiques pour la structure budgétaire

## Formules de Calcul

### Montant Théorique

```python
if budget_en_cours:
    jours_écoulés = date_du_jour - date_début
    jours_totaux = date_fin - date_début
    montant_théorique = montant_planifié × (jours_écoulés / jours_totaux)
elif budget_terminé:
    montant_théorique = montant_planifié
else:  # budget_non_commencé
    montant_théorique = 0
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

```python
if montant_théorique != 0:
    pourcentage = (montant_pratique / montant_théorique) × 100
else:
    pourcentage = 0

# Limité entre 0% et 100%
pourcentage = max(0, min(100, pourcentage))
```

## Support

- **Développeur** : CPSS
- **Basé sur** : Module original de Cybrosys Technologies
- **Licence** : LGPL-3
- **Version** : 19.0.1.0.0

## Changelog

### Version 19.0.1.0.0 (2026-01-07)
- Adaptation initiale pour l'Algérie
- Traduction complète en français
- Intégration avec plan comptable SCF
- Documentation algérienne
- Dépendance obligatoire : l10n_dz_cpss_ext

## Crédits

- **Module original** : Cybrosys Technologies
- **Adaptation algérienne** : CPSS - 2026
- **Conformité** : Normes SCF et réglementation fiscale algérienne
