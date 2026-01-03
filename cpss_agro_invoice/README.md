# CPSS Agro - Facturation Subventionnée FNDIA

## Description

Ce module gère les subventions FNDIA (Fonds National de Développement de l'Investissement Agricole) pour les factures de vente d'engrais.

## Fonctionnalités

### 1. Champ "Subventionné FNDIA"
- Booléen ajouté sur les factures de vente
- **Activé par défaut** pour les factures client (out_invoice)
- Désactivé par défaut pour les autres types de documents

### 2. Calcul automatique du montant FNDIA
Pour chaque ligne de facture :
- Récupère le `prix_soutien` depuis la catégorie du produit (champ ajouté par le module `cpss_product_categories`)
- Calcule : **Montant FNDIA = prix_soutien × quantité**

Exemple :
- Produit : Engrais Azotés
- Catégorie : Engrais Azotés (prix_soutien = 3 737,00 DA)
- Quantité facturée : 5 tonnes
- **Montant FNDIA = 3 737 × 5 = 18 685,00 DA**

### 3. Montant à payer
- **Montant à Payer = Montant Total TTC - Montant FNDIA**
- Affiché clairement dans le formulaire de facture
- C'est ce montant que le client doit réellement payer

### 4. Écritures comptables
La subvention FNDIA est enregistrée dans un **compte client séparé** :
- Compte par défaut : `411200 - Subvention FNDIA - Client`
- Type : Compte client (asset_receivable)
- Reconciliable : Oui

Écritures générées :
```
Débit  411000 (Client)          : Montant à Payer
Débit  411200 (FNDIA)           : Montant FNDIA
Crédit 707000 (Vente)           : Montant HT
Crédit 445700 (TVA Collectée)   : Montant TVA
```

### 5. Timbre fiscal
Le **timbre fiscal est calculé uniquement sur le montant à payer** et non sur le montant total de la facture.

## Configuration

1. Aller dans **Facturation > Configuration > Paramètres**
2. Section **Subvention FNDIA**
3. Sélectionner le compte comptable pour les subventions FNDIA
   - Par défaut : `411200 - Subvention FNDIA - Client`
   - Vous pouvez changer ce compte si nécessaire

## Utilisation

### Créer une facture subventionnée

1. Créer une nouvelle facture client
2. Le champ **"Subventionné FNDIA"** est activé par défaut
3. Ajouter des produits dont la catégorie a un `prix_soutien` défini
4. Le système calcule automatiquement :
   - Montant FNDIA par ligne
   - Montant FNDIA total
   - Montant à payer

### Désactiver la subvention pour une facture

Décocher le champ **"Subventionné FNDIA"** :
- Les montants FNDIA seront à zéro
- Le montant à payer = montant total
- Pas de compte FNDIA dans les écritures

## Dépendances

- `account` : Module de comptabilité Odoo
- `cpss_product_categories` : Pour le champ `prix_soutien` sur les catégories de produits
- `l10n_dz` : Localisation algérienne (pour le timbre fiscal)

## Données créées

- Compte comptable : `411200 - Subvention FNDIA - Client`

## Vues modifiées

- Formulaire de facture : Ajout des champs FNDIA et totaux
- Liste des factures : Ajout des colonnes FNDIA
- Recherche : Ajout de filtres pour factures subventionnées
- Paramètres : Configuration du compte FNDIA

## Notes techniques

- Les montants FNDIA sont stockés (`store=True`) pour les performances
- Contraintes de validation pour éviter les montants négatifs ou supérieurs au total
- Le calcul du timbre est modifié via la méthode `_recompute_stamp_tax_on_fndia_amount()`
- Les écritures comptables sont ajoutées via `_recompute_dynamic_lines()`

## Auteur

CPSS - Centre des Produits de Soutien Spécialisés

## License

LGPL-3
