# Comptes par Défaut - Plan Comptable Algérien (CPSS)

## Vue d'ensemble

Le module `l10n_dz_cpss` configure automatiquement les comptes par défaut nécessaires au bon fonctionnement d'Odoo avec le plan comptable algérien. Cette configuration est effectuée lors de l'installation du module via le `post_init_hook`.

## Comptes par Défaut de la Société

### 1. Comptes Clients et Fournisseurs

- **Compte Client par défaut** : `411100` - Clients - Ventes de biens ou de prestations de services
- **Compte Fournisseur par défaut** : `401310` - Fournisseurs de stocks : Compte fournisseur par défaut

Ces comptes sont utilisés automatiquement lors de la création de nouveaux partenaires (clients/fournisseurs).

### 2. Comptes de Vente et d'Achat sur les Produits

Les comptes suivants sont configurés sur la catégorie racine "All" des produits, permettant à tous les produits d'hériter automatiquement de ces comptes :

- **Compte de Vente (Revenus)** : `700000` - Ventes de marchandises
- **Compte d'Achat (Dépenses)** : `700000` - Achats de marchandises vendues

**Important** : Avec cette configuration, vous n'avez plus besoin de définir manuellement le compte sur chaque ligne de facture. Le compte sera automatiquement rempli en fonction de la catégorie du produit.

### 3. Comptes de Stock

- **Compte de Stock Sortie** : `355000` - Produits finis
- **Compte de Stock Entrée** : `380000` - Achat de matières premières et fournitures stockées
- **Compte de Valorisation Stock** : `355000` - Produits finis

### 4. Comptes de TVA

- **Taxe de Vente par défaut** : TVA 19% Production de biens (l10n_dz_vat_sale_19_prod)
- **Taxe d'Achat par défaut** : TVA 19% Achats (l10n_dz_vat_purchase_19)

### 5. Autres Comptes Spéciaux

- **Compte de Créances POS** : `413` - Clients - Effet à recevoir
- **Compte Gain de Change** : `766` - Gains de change
- **Compte Perte de Change** : `666` - Pertes de change
- **Compte Gain de Caisse** : `758` - Produits divers de gestion courante
- **Compte Perte de Caisse** : `657` - Charges diverses de gestion courante
- **Compte Gain Escompte** : `609` - Rabais, remises et ristournes obtenus sur achats
- **Compte Perte Escompte** : `709` - Rabais, remises et ristournes accordés

## Comment Personnaliser les Comptes par Défaut

### 1. Via l'Interface Odoo

Allez dans **Comptabilité > Configuration > Paramètres** pour modifier :
- Les taxes par défaut
- Les comptes de différence de caisse
- Les comptes de change

### 2. Sur les Catégories de Produits

Pour définir des comptes spécifiques pour certaines catégories de produits :

1. Allez dans **Inventaire > Configuration > Catégories de produits**
2. Sélectionnez une catégorie
3. Dans l'onglet "Propriétés du compte" :
   - **Compte de Revenus** : pour les ventes
   - **Compte de Dépenses** : pour les achats
   - **Comptes de Stock** : pour la valorisation du stock

**Note** : Les catégories enfants héritent des comptes de leurs catégories parentes.

### 3. Sur les Produits Individuels

Pour un produit spécifique nécessitant un compte différent :

1. Allez dans le produit
2. Onglet "Comptabilité"
3. Définissez les comptes spécifiques (ils remplaceront ceux de la catégorie)

## Résolution de Problèmes

### Problème : Le compte n'est pas rempli automatiquement sur les lignes de facture

**Solutions** :
1. Vérifiez que le produit appartient à une catégorie ayant des comptes définis
2. Vérifiez que la catégorie racine "All" a bien les comptes par défaut (voir ci-dessus)
3. Réinstallez le module si nécessaire pour réappliquer le `post_init_hook`

### Problème : Les écritures comptables sont incorrectes

**Solutions** :
1. Vérifiez que les bonnes taxes sont appliquées sur les produits
2. Assurez-vous que les comptes de TVA collectée (4457) et TVA déductible (4456) sont correctement configurés dans les taxes
3. Vérifiez les positions fiscales si vous traitez avec l'export/import

## Comptes Recommandés selon le Type d'Activité

### Commerce (Négoce)
- **Ventes** : `700000` - Ventes de marchandises
- **Achats** : `600000` - Achats de marchandises vendues

### Production
- **Ventes** : `701000` - Ventes de produits finis
- **Achats** : `601000` - Matières premières et fournitures consommées

### Services
- **Ventes** : `706000` - Prestations de services
- **Achats** : `604000` - Achats d'études et prestations de services

Vous pouvez personnaliser ces comptes dans les catégories de produits selon votre activité.

## Support

Pour plus d'informations sur le plan comptable algérien, consultez :
- Le Système Comptable et Financier (SCF) algérien
- La documentation CPSS sur https://www.cpss-dz.com
