# CPSS Inter-Company Sync Base

Module Odoo 16 pour la synchronisation inter-sociétés en conformité avec les exigences fiscales algériennes.

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

## Installation

1. Copier le module dans addons/
2. Mettre à jour la liste des modules
3. Installer "CPSS Inter-Company Sync Base"
4. Configurer via Menu > Inter-Company Sync > Configuration

## Configuration

1. Définir société opérationnelle et fiscale
2. Configurer utilisateurs de notification
3. Tester la configuration
4. Marquer les factures avec "À déclarer"

## Utilisation

1. Créer et valider une facture
2. Marquer "À déclarer" = Vrai
3. Cliquer "Synchroniser vers Société Fiscale"
4. Vérifier la chaîne complète dans la société fiscale