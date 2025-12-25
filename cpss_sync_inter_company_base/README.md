# CPSS Inter-Company Sync Base

Module Odoo 19 pour la synchronisation inter-sociétés en conformité avec les exigences fiscales algériennes.

## Compatibilité Odoo 19

Ce module a été mis à jour pour Odoo 19 avec les améliorations suivantes :
- ✅ Utilisation native du partage multi-company (`company_id = False`)
- ✅ Vérification automatique de cohérence multi-company (`_check_company_auto`)
- ✅ Migration complète des attributs `attrs` vers la nouvelle syntaxe (invisible, readonly, required)
- ✅ Attribut `check_company` sur les champs relationnels

## Fonctionnalités

### États de facture étendus
- **Brouillon** : Facture en cours de création
- **Validé** : Facture validée (ancien "Comptabilisé")
- **Proposé pour Sync** : Facture proposée pour synchronisation
- **Comptabilisé** : Facture synchronisée vers société fiscale

### Synchronisation complète
- Synchronisation automatique de toute la chaîne documentaire
- Liens bidirectionnels entre documents
- Traçabilité complète

### 🆕 Configuration du Partage de Données
- **Menu centralisé** pour définir quelles données fonctionnelles et fiscales doivent être partagées
- **Partage intelligent des taxes** : Les taxes sont partagées entre sociétés au lieu d'être dupliquées
- **Configuration granulaire** : Choisissez quelles données partager (taxes, conditions de paiement, produits, contacts, etc.)
- **Synchronisation du plan comptable** : Les comptes sont synchronisés automatiquement tout en restant spécifiques à chaque société

### 🎨 Personnalisation de la Barre de Navigation par Société
- **Couleurs personnalisées par société** : Chaque société peut avoir sa propre couleur de navbar
- **Distinction visuelle instantanée** : Identifiez en un coup d'œil dans quelle société vous travaillez
- **Changement automatique** : La navbar change de couleur en temps réel lors du changement de société
- **Compatible avec les couleurs Odoo** : Utilise le champ `primary_color` existant ou des couleurs personnalisées

## Installation

1. Copier le module dans addons/
2. Mettre à jour la liste des modules
3. Installer "CPSS Inter-Company Sync Base"
4. Configurer via Menu > Inter-Company Sync > Configuration

## Configuration

### Configuration Initiale
1. Aller à **Synchronisation Inter-Sociétés > Configuration > Sync Settings**
2. Définir société opérationnelle et fiscale
3. Configurer utilisateurs de notification
4. Tester la configuration

### 🆕 Configuration du Partage de Données
1. Aller à **Synchronisation Inter-Sociétés > Configuration > Company Data Sharing**
2. Activer/désactiver le partage pour chaque type de données :
   - ✅ **Taxes** (recommandé) : Partage les taxes entre sociétés - les mêmes taxes sont utilisées sur toutes les lignes de facture
   - ✅ **Conditions de paiement** : Partage les termes de paiement incluant les timbres
   - ✅ **Positions fiscales** : Partage les positions fiscales
   - ✅ **Produits** : Partage les produits entre sociétés
   - ✅ **Contacts** : Partage les clients et fournisseurs
   - ✅ **Synchronisation du plan comptable** : Copie automatiquement les comptes entre sociétés
3. Cliquer sur **"Apply Configuration"** pour appliquer les paramètres

### Avantages du Partage de Taxes
Lorsque le partage de taxes est activé :
- ✅ Les taxes sont définies **une seule fois** dans la société principale
- ✅ Elles apparaissent **automatiquement** dans toutes les sociétés configurées
- ✅ **Pas de mapping** nécessaire lors de la synchronisation
- ✅ **Cohérence garantie** entre les sociétés
- ✅ Les lignes de facture utilisent **directement** les mêmes taxes

### 🎨 Configuration des Couleurs de Navbar
1. Aller à **Paramètres > Utilisateurs & Sociétés > Sociétés**
2. Ouvrir la société que vous voulez personnaliser
3. Dans la section **"Navbar Customization"** :
   - ✅ Activer **"Use Custom Navbar Color"**
   - 🎨 Choisir **"Navbar Background Color"** (exemple: bleu pour société opérationnelle)
   - 🎨 Choisir **"Navbar Text Color"** (généralement blanc #ffffff)
4. Enregistrer

**Suggestions de couleurs :**
- **Société Opérationnelle** : Bleu (#1e40af) ou Vert (#059669)
- **Société Fiscale** : Orange (#ea580c) ou Rouge (#dc2626)
- **Production** : Vert foncé (#065f46)
- **Test/Staging** : Orange (#f59e0b)

## Utilisation

1. Créer et valider une facture
2. Marquer "À déclarer" = Vrai
3. Cliquer "Synchroniser vers Société Fiscale"
4. Vérifier la chaîne complète dans la société fiscale

## Notes Importantes

### Données Partagées vs Spécifiques
- **Partagées** (company_id = False) : Taxes, produits, contacts - définis une fois, visibles partout
- **Spécifiques** : Plan comptable - copié mais reste spécifique à chaque société pour conformité comptable

### Synchronisation du Plan Comptable
Le plan comptable est **synchronisé** mais reste **spécifique à chaque société** :
- Les comptes sont automatiquement copiés de la société opérationnelle vers la fiscale
- Chaque société garde son propre plan comptable pour la conformité
- Le mapping des comptes est fait automatiquement lors de la synchronisation