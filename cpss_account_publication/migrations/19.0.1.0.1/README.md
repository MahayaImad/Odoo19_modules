# Migration 19.0.1.0.1

## Objectif
Cette migration ajoute le support pour le suivi du stock publié/non publié et corrige les codes de séquence.

## Modifications
- Ajout du champ `enable_publication_stock_tracking` à `res.company`
- Migration des codes de séquence de `.unpublished` à `.standard`

## Script de pré-migration (pre.py)
Le script `pre.py` ajoute la colonne `enable_publication_stock_tracking` à la table `res_company` avant le chargement du module pour éviter les erreurs PostgreSQL lors de la mise à jour.

## Comment mettre à jour
1. Redémarrer Odoo avec l'option de mise à jour du module :
   ```bash
   odoo-bin -u cpss_account_publication -d nom_base_de_donnees
   ```

2. Ou via l'interface Odoo :
   - Aller dans Applications
   - Rechercher "cpss_account_publication"
   - Cliquer sur "Mettre à jour"
