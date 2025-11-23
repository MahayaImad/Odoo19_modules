# Changelog - l10n_dz_elosys

## Version 19.0.1.0 (2025)

### Migration vers Odoo 19.0
Module mis à niveau depuis la version 16.0.5.1 vers 19.0.1.0 avec prise en charge complète des nouvelles fonctionnalités d'Odoo 17, 18 et 19.

### Changements majeurs

#### Python / Backend
- **Suppression de l'API obsolète `decimal_precision`** : Remplacement de `odoo.addons.decimal_precision` par l'utilisation du champ `Monetary`
- **Modernisation du champ `capital_social`** : Migration de `Float` avec `digits=dp.get_precision('Account')` vers `Monetary` avec `currency_field='currency_id'`
- **Suppression du paramètre `size`** : Retrait du paramètre `size` obsolète des champs `Char` dans tous les modèles
- **Nettoyage des imports** : Suppression des imports inutilisés et organisation optimale des imports

#### JavaScript / Frontend
- **Migration complète vers Owl Framework** : Réécriture du fichier `many_tags_link.js` pour utiliser l'API Odoo 17+
- **Utilisation du système de modules ES6** : Adoption de `@odoo-module` au lieu de l'ancien `odoo.define`
- **Patch moderne** : Utilisation de `patch()` au lieu de l'ancien système `.include()`
- **Services modernes** : Intégration avec `useService()` pour l'accès aux services Odoo
- **Gestion d'actions améliorée** : Utilisation de `action.doAction()` avec callbacks asynchrones

#### XML / Vues
- **Migration des attributs `attrs`** : Remplacement de l'attribut obsolète `attrs` par les modifiers modernes `invisible`, `required`, etc.
- **Syntaxe moderne pour les conditions** : Utilisation de la nouvelle syntaxe Python dans les attributs de vue (ex: `invisible="regulation != 'regulated_activity'"`)
- **Compatibilité avec les nouvelles versions** : Adaptation de toutes les vues pour Odoo 19

### Détails techniques

#### Fichiers modifiés
- `__manifest__.py` : Version mise à jour vers 19.0.1.0
- `models/res_company.py` : Modernisation des champs et suppression des API obsolètes
- `models/res_partner.py` : Nettoyage des paramètres obsolètes
- `views/activity_code.xml` : Migration des attributs `attrs` vers modifiers modernes
- `views/res_partner.xml` : Migration des attributs `attrs` vers modifiers modernes
- `static/src/js/many_tags_link.js` : Réécriture complète pour Owl framework

#### Nouvelles fonctionnalités d'Odoo 17/18/19 supportées
- Support complet du framework Owl (Odoo 17+)
- Utilisation des services modernes via hooks
- Compatibilité avec le nouveau système de champs monétaires
- Support des nouveaux modifiers de vue
- Meilleure performance grâce aux optimisations du framework

### Compatibilité
- ✅ Odoo 19.0
- ✅ Python 3.10+
- ✅ Framework Owl
- ✅ Nouveau système de modules JavaScript

### Notes de migration
Si vous migrez depuis une version antérieure :
1. Vérifiez que vos personnalisations JavaScript sont compatibles avec Owl
2. Les champs `capital_social` utilisent maintenant le type `Monetary`
3. Les vues XML utilisent les nouveaux modifiers au lieu de `attrs`

### Contributeurs
- Migration Odoo 19 : Claude AI Assistant
- Module original : Elosys (Soufyane AMRAOUI, Chems Eddine SAHININE, Fatima MESSADI)
