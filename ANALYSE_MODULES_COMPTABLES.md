# Analyse des Modules Comptables : base_account_budget et base_accounting_kit

## Date d'analyse : 2026-01-07

---

## 1. MODULE: base_account_budget

### 1.1 Informations Générales
- **Version**: 19.0.1.0.0
- **Catégorie**: Accounting
- **Auteur**: Cybrosys Techno Solutions
- **Licence**: LGPL-3
- **Dépendances**: base, account

### 1.2 Fonctionnalités Principales

#### A. Gestion des Budgets
Le module `base_account_budget` offre un système complet de gestion budgétaire pour Odoo 19 Community Edition.

**Modèles Principaux:**

1. **account.budget.post (Positions Budgétaires)**
   - Création de positions budgétaires
   - Association avec plusieurs comptes comptables
   - Gestion par entreprise
   - Contrainte: Au moins un compte doit être associé

2. **budget.budget (Budget)**
   - Nom du budget
   - Responsable (utilisateur)
   - Dates de début et fin
   - États du workflow:
     * Draft (Brouillon)
     * Confirm (Confirmé)
     * Validate (Validé)
     * Done (Terminé)
     * Cancel (Annulé)
   - Lignes budgétaires (One2many)
   - Suivi par mail (mail.thread)

3. **budget.lines (Lignes Budgétaires)**
   - Montant planifié
   - Montant pratique (calculé automatiquement)
   - Montant théorique (calculé en fonction du temps écoulé)
   - Pourcentage de réalisation
   - Dates de début et fin
   - Association avec compte analytique
   - Position budgétaire
   - Date de paiement

**Calculs Automatiques:**

- **Montant Pratique**: Calculé à partir des lignes analytiques réelles pour les comptes associés
- **Montant Théorique**: Calculé proportionnellement au temps écoulé:
  - Si le budget n'a pas commencé: 0
  - Si le budget est terminé: montant planifié complet
  - Si en cours: montant proportionnel aux jours écoulés
- **Pourcentage de Réalisation**: (Montant Pratique / Montant Théorique) × 100

### 1.3 Compatibilité avec la Comptabilité Algérienne

#### ✅ Points Compatibles:
1. **Structure générique**: Le module n'impose pas de plan comptable spécifique
2. **Multi-entreprises**: Gestion par société conforme aux besoins algériens
3. **Comptes analytiques**: Compatible avec le système SCF (Système Comptable Financier)
4. **Workflow de validation**: Conforme aux procédures de contrôle budgétaire algériennes

#### ⚠️ Points à Considérer:
1. **Pas de conflit majeur** avec les normes algériennes
2. Le module fonctionne avec n'importe quel plan comptable
3. Compatible avec les modules l10n_dz existants dans votre système

---

## 2. MODULE: base_accounting_kit

### 2.1 Informations Générales
- **Version**: 19.0.2.0.0
- **Catégorie**: Accounting
- **Auteur**: Cybrosys Techno Solutions
- **Licence**: LGPL-3
- **Dépendances**: account, sale, account_check_printing, analytic, base_account_budget, contacts
- **Dépendances Python**: openpyxl, ofxparse, qifparse

### 2.2 Fonctionnalités Principales

#### A. Gestion des Actifs et Amortissements

**Modèle: account.asset.asset**

Fonctionnalités complètes:
- Gestion des actifs avec amortissement
- Méthodes d'amortissement:
  * **Linéaire (Linear)**: Valeur Brute / Nombre d'Amortissements
  * **Dégressif (Declining)**: Valeur Résiduelle × Facteur Dégressif
- Calcul prorata temporis
- Catégories d'actifs avec configuration pré-définie
- États du workflow: Draft, Running, Close, Cancelled
- Génération automatique des écritures d'amortissement
- Lignes d'amortissement avec:
  * Montant d'amortissement
  * Valeur résiduelle
  * Valeur amortie
  * Date d'amortissement
- Comptabilisation automatique des actifs depuis les factures

**Comptes utilisés:**
- Compte d'actif (Asset Account)
- Compte d'amortissement (Depreciation Account)
- Compte de charge d'amortissement (Expense Account)

#### B. Gestion des Relances (Follow-ups)

**Modèle: account.followup**

- Création de plans de relance
- Niveaux de relance configurables (followup.line)
- Gestion automatique des relances clients
- Templates de communication
- Suivi par entreprise

#### C. Gestion PDC (Post-Dated Cheques)

**Extension du modèle account.payment:**

- Gestion des chèques différés
- Champs ajoutés:
  * Référence bancaire (bank_reference)
  * Référence du chèque (cheque_reference)
  * Date d'effet (effective_date)
- Méthodes de paiement PDC:
  * PDC entrant (pdc_in)
  * PDC sortant (pdc_out)
- Impression des chèques pré-numérotés
- Rapprochement bancaire

#### D. Limite de Crédit

**Extension du modèle account.move:**

- Gestion des limites de crédit client
- Étapes configurables:
  * Étape d'avertissement (warning_stage)
  * Étape de blocage (blocking_stage)
- Blocage automatique des factures si dépassement
- Affichage du montant dû
- Activation par partenaire

#### E. Rapports Comptables Avancés

**Rapports inclus:**

1. **Rapports Financiers**
   - Bilan (Balance Sheet)
   - Compte de résultat (Profit & Loss)
   - Rapports financiers personnalisables

2. **Grands Livres**
   - Grand livre général (General Ledger)
   - Grand livre partenaire (Partner Ledger)
   - Balance âgée (Aged Trial Balance)

3. **Livres Auxiliaires**
   - Livre de banque (Bank Book)
   - Livre de caisse (Cash Book)
   - Journal (Day Book)

4. **Autres Rapports**
   - Rapport de taxes (Tax Report)
   - Rapport d'audit des journaux (Journal Audit)
   - Balance de vérification (Trial Balance)
   - Flux de trésorerie (Cash Flow Report)
   - Rapport d'actifs (Asset Report)

#### F. Autres Fonctionnalités

1. **Écritures Récurrentes**
   - Génération automatique d'écritures périodiques
   - Configuration via cron jobs
   - Référence de récurrence

2. **Factures Multiples**
   - Impression multiple de factures
   - Layouts personnalisables
   - Templates multiples

3. **Import Bancaire**
   - Import de relevés bancaires
   - Formats supportés: OFX, QIF, Excel

4. **Verrouillage Comptable**
   - Date de verrouillage des écritures
   - Protection des périodes clôturées

### 2.3 Compatibilité avec la Comptabilité Algérienne

#### ✅ Points Compatibles:

1. **Gestion des Actifs**
   - Conforme aux normes SCF algériennes
   - Méthodes d'amortissement conformes
   - Le système SCF permet les amortissements linéaires et dégressifs

2. **Rapports Comptables**
   - Structure des rapports compatible avec les exigences algériennes
   - Grand livre général conforme aux obligations fiscales
   - Balance et états financiers adaptables

3. **PDC (Chèques Différés)**
   - Très utile pour le contexte algérien où les chèques différés sont courants
   - Compatible avec les pratiques bancaires locales

4. **Limite de Crédit**
   - Pratique courante en Algérie
   - Aucun conflit réglementaire

#### ⚠️ Points à Adapter/Vérifier:

1. **Plan Comptable**
   - Le module utilise des comptes génériques
   - **RECOMMANDATION**: Utiliser avec le module `l10n_dz_cpss_ext` qui contient le plan comptable SCF
   - Vérifier que les comptes d'actifs, d'amortissement et de charges sont correctement configurés selon le PCN (Plan Comptable National)

2. **Méthode d'Amortissement**
   - En Algérie, l'amortissement linéaire est le plus courant
   - L'amortissement dégressif existe mais avec des règles fiscales spécifiques
   - **ATTENTION**: Vérifier les taux d'amortissement avec la réglementation fiscale algérienne

3. **Rapports Fiscaux**
   - Les rapports standards peuvent nécessiter des adaptations pour:
     * Déclaration G50 (série G)
     * États financiers selon le format SCF
     * Liasse fiscale algérienne
   - **RECOMMANDATION**: Compléter avec des rapports spécifiques Algérie

4. **TVA et Taxes**
   - Le module gère les taxes de manière générique
   - **IMPORTANT**: Doit être configuré avec les taux de TVA algériens (19%, 9%)
   - Vérifier la compatibilité avec le timbre fiscal (module `l10n_dz_on_timbre_fiscal` présent)

5. **Factures et Mentions Légales**
   - Les factures doivent contenir les mentions obligatoires algériennes:
     * NIF (Numéro d'Identification Fiscale)
     * NIS (Numéro d'Identification Statistique)
     * RC (Registre de Commerce)
     * Article (Article d'imposition)
   - **RECOMMANDATION**: Personnaliser les templates de factures

6. **Année Fiscale**
   - En Algérie, l'année fiscale correspond à l'année civile (1er janvier - 31 décembre)
   - Vérifier la configuration dans les paramètres de la société

#### ❌ Conflits Potentiels:

1. **Aucun conflit majeur identifié** entre les modules et la réglementation algérienne

2. **Complémentarité avec modules DZ**:
   - `base_accounting_kit` est compatible avec:
     * `l10n_dz_cpss_ext` (Plan comptable SCF)
     * `l10n_dz_on_timbre_fiscal` (Timbre fiscal)
     * `l10n_dz_code_cnrc` (Codes d'activité)

---

## 3. RECOMMANDATIONS D'IMPLÉMENTATION

### 3.1 Ordre d'Installation

1. **Modules de base Algérie:**
   ```
   l10n_dz_cpss_ext          # Plan comptable SCF
   l10n_dz_on_timbre_fiscal  # Timbre fiscal
   l10n_dz_code_cnrc         # Codes d'activité CNRC
   ```

2. **Modules comptables avancés:**
   ```
   base_account_budget       # Gestion budgétaire
   base_accounting_kit       # Kit comptable complet
   ```

### 3.2 Configuration Recommandée

#### A. Configuration de la Société
- Définir l'année fiscale: 1er janvier - 31 décembre
- Configurer les informations légales:
  * NIF
  * NIS
  * RC
  * Article d'imposition
  * Code activité CNRC

#### B. Plan Comptable
- Utiliser le plan comptable SCF (l10n_dz_cpss_ext)
- Créer les comptes d'actifs selon la nomenclature algérienne:
  * Classe 2: Immobilisations
  * 21: Immobilisations incorporelles
  * 22: Terrains
  * 23: Bâtiments
  * 24: Matériel et outillage
  * 28: Amortissements

#### C. Catégories d'Actifs
Créer des catégories d'actifs avec les durées d'amortissement conformes:
- Bâtiments: 20-25 ans (4-5%)
- Matériel et outillage: 5-10 ans (10-20%)
- Matériel de transport: 4-5 ans (20-25%)
- Mobilier et matériel de bureau: 5-10 ans (10-20%)
- Matériel informatique: 3-5 ans (20-33%)

#### D. TVA
Configurer les taux de TVA:
- TVA 19% (taux normal)
- TVA 9% (taux réduit)
- TVA 0% (exonéré)

#### E. Positions Budgétaires
Organiser par:
- Départements/Services
- Projets
- Nature de dépense (fonctionnement, investissement)

### 3.3 Points de Vigilance

#### A. Amortissements
- **Règle fiscale**: L'amortissement démarre au premier jour du mois d'acquisition
- Activer le prorata temporis si nécessaire
- Vérifier les taux fiscalement déductibles

#### B. Clôture d'Exercice
- Respecter les dates de clôture fiscale algérienne (30 avril N+1)
- Générer les états financiers selon le format SCF:
  * Bilan (actif/passif)
  * Compte de résultat par nature
  * Tableau des flux de trésorerie
  * Tableau de variation des capitaux propres

#### C. Conservation des Documents
- Obligation de conservation: 10 ans minimum
- Archiver tous les rapports et justificatifs

#### D. Déclarations Fiscales
- Les rapports du module doivent être complétés par:
  * Déclaration mensuelle de TVA (G50)
  * Déclaration annuelle des revenus (série G)
  * Bilan fiscal

---

## 4. SYNTHÈSE

### 4.1 Avantages des Modules

**base_account_budget:**
- Contrôle budgétaire efficace
- Suivi en temps réel
- Compatible multi-sociétés
- Workflow de validation

**base_accounting_kit:**
- Suite comptable complète
- Gestion des actifs conforme SCF
- PDC pour pratiques algériennes
- Rapports variés et détaillés
- Limite de crédit pour gestion du risque

### 4.2 Compatibilité Globale

| Aspect | base_account_budget | base_accounting_kit |
|--------|---------------------|---------------------|
| Plan comptable SCF | ✅ Compatible | ✅ Compatible |
| Normes SCF | ✅ Conforme | ✅ Conforme* |
| Règles fiscales DZ | ✅ Neutre | ⚠️ À configurer |
| Modules l10n_dz | ✅ Compatible | ✅ Compatible |
| Pratiques locales | ✅ Adapté | ✅ Très adapté (PDC) |

*Avec configuration appropriée

### 4.3 Conclusion

**Les deux modules sont compatibles avec la comptabilité algérienne** sous réserve d'une configuration appropriée:

1. ✅ **Aucun conflit structurel** avec les normes SCF
2. ✅ **Complémentaires** aux modules l10n_dz existants
3. ⚠️ **Configuration requise** pour:
   - Taux d'amortissement fiscaux
   - Templates de rapports fiscaux
   - Mentions légales sur factures
4. ✅ **Recommandé** pour une gestion comptable complète en Algérie

### 4.4 Actions Recommandées

1. **Tester en environnement de développement**
2. **Configurer le plan comptable SCF** (l10n_dz_cpss_ext)
3. **Créer les catégories d'actifs** avec taux algériens
4. **Personnaliser les templates** de factures et rapports
5. **Former les utilisateurs** aux workflows de validation
6. **Valider avec un expert-comptable** algérien

---

## 5. RESSOURCES COMPLÉMENTAIRES

### Modules Algérie Déjà Présents
- `l10n_dz_cpss_ext`: Plan comptable SCF complet
- `l10n_dz_on_timbre_fiscal`: Gestion du timbre fiscal
- `l10n_dz_code_cnrc`: Codes d'activité CNRC

### Réglementation de Référence
- Système Comptable Financier (SCF) - Algérie
- Code des impôts directs et taxes assimilées
- Code de la TVA
- Loi de finances (annuelle)

---

**Document généré le**: 2026-01-07
**Version**: 1.0
**Analyste**: Claude Code Assistant
