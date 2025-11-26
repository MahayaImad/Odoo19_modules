# Guide d'Application du Plan Comptable l10n_dz_cpss

## ⚠️ IMPORTANT À COMPRENDRE

Dans Odoo 19, **installer un module de localisation ≠ appliquer le plan comptable**.

- **Installer le module** : Rend le plan comptable disponible
- **Appliquer le template** : Crée les comptes dans votre société

## 📋 Étape par Étape

### Étape 1 : Installer le Module ✓

```bash
# Via ligne de commande
odoo-bin -u l10n_dz_cpss -d votre_base

# OU via l'interface
Apps > Rechercher "l10n_dz_cpss" > Installer
```

**Vérification :**
- Le module apparaît comme "Installé" dans Apps
- Pas d'erreur dans les logs Odoo

### Étape 2 : Configurer la Société

**Option A - Nouvelle Société (RECOMMANDÉE)**

1. Aller dans **Paramètres > Utilisateurs et Sociétés > Sociétés**
2. Cliquer sur **Créer**
3. Remplir les informations :
   - Nom de la société
   - **Pays : Algérie** ⬅️ CRUCIAL
4. Enregistrer

➡️ Le plan comptable s'applique **automatiquement** si le pays est Algérie

**Option B - Société Existante**

1. Aller dans la fiche de votre société
2. Modifier le **Pays : Algérie**
3. Enregistrer
4. Aller dans **Comptabilité > Configuration > Paramètres**
5. Chercher la section **Plan comptable**
6. Cliquer sur **Installer un plan comptable** ou **Changer de plan**
7. Sélectionner **Algérie - CPSS**

### Étape 3 : Vérifier l'Application

**Vérifiez que les comptes sont créés :**

1. Aller dans **Comptabilité > Configuration > Plan comptable**
2. Vous devriez voir les comptes :
   - 401 - Fournisseurs
   - 413 - Clients - Effets à recevoir
   - 512xxx - Banques
   - 600 - Achats de marchandises
   - 700 - Ventes de marchandises

**Si vous ne voyez PAS ces comptes :**
- Le template n'est pas encore appliqué
- Suivez la méthode ci-dessous

## 🔧 Méthode Manuelle (Si l'Automatique Ne Fonctionne Pas)

### Via l'Interface Développeur

1. Activer le **Mode Développeur** :
   - Paramètres > Activer le mode développeur

2. Aller dans **Comptabilité > Configuration**

3. Chercher l'option **"Plan comptable"** ou **"Chart of Accounts"**

4. Options possibles :
   - **"Install a Chart of Accounts"** (si aucun plan)
   - **"Change Chart Template"** (si vous avez déjà un plan)

5. Sélectionner **"Algérie - CPSS"** ou **"dz"**

### Via le Code Python (Shell Odoo)

```python
# Ouvrir le shell Odoo
odoo-bin shell -d votre_base

# Dans le shell Python :
env['account.chart.template'].try_loading('dz', env.company)
env.cr.commit()
```

## 🐛 Dépannage

### Le template n'apparaît pas dans les options

**Vérifications :**

1. **Le module est-il installé ?**
   ```
   Apps > Rechercher "l10n_dz_cpss"
   État : doit être "Installé"
   ```

2. **Le pays de la société est-il Algérie ?**
   ```
   Paramètres > Sociétés > Votre société
   Pays : DZ - Algérie
   ```

3. **Logs Odoo :**
   ```bash
   tail -f /var/log/odoo/odoo.log | grep -i "l10n_dz_cpss\|template"
   ```

   Cherchez la ligne :
   ```
   l10n_dz_cpss: post_init_hook appelé
   Template 'dz' enregistré pour le plan comptable algérien
   ```

4. **Réinstaller le module :**
   ```bash
   # Désinstaller
   Apps > l10n_dz_cpss > Désinstaller

   # Mettre à jour la liste
   Apps > Mettre à jour la liste des applications

   # Réinstaller
   Apps > l10n_dz_cpss > Installer
   ```

### Les comptes ne se créent pas

**Solution 1 - Forcer l'application :**

```python
# Shell Odoo
env['account.chart.template'].try_loading('dz', env.company, install_demo=False)
env.cr.commit()
```

**Solution 2 - Import Manuel des CSV :**

Si vraiment rien ne fonctionne, vous pouvez importer les comptes manuellement :

1. Aller dans **Comptabilité > Configuration > Plan comptable**
2. Importer > Sélectionner le fichier CSV
3. Utiliser : `l10n_dz_cpss/data/template/account.account-dz.csv`

### Erreurs courantes

**Erreur : "Template 'dz' not found"**
- Le module n'est pas correctement chargé
- Redémarrer Odoo après installation

**Erreur : "Country code 'DZ' not found"**
- Le module `base` n'est pas à jour
- Vérifier que l'Algérie existe dans les pays

**Erreur : "Comptes déjà existants"**
- Vous avez déjà un plan comptable
- Utiliser "Change Chart Template" au lieu de "Install"

## ✅ Validation Finale

Pour vérifier que tout fonctionne :

1. **Comptes créés :**
   - Comptabilité > Plan comptable
   - Minimum 1183 comptes visibles

2. **Comptes par défaut configurés :**
   - Paramètres > Comptabilité
   - Compte client : 413
   - Compte fournisseur : 401

3. **Taxes configurées :**
   - Comptabilité > Configuration > Taxes
   - TVA 19% vente
   - TVA 19% achat

4. **Groupes visibles :**
   - Comptabilité > Plan comptable > Vue Groupée
   - Classe 1 à Classe 7

## 📞 Support

Si après tout cela le template ne s'applique toujours pas :

1. Exécutez le script de diagnostic :
   ```bash
   cd l10n_dz_cpss
   python3 diagnostic.py
   ```

2. Partagez :
   - La sortie du diagnostic
   - Les logs Odoo (dernières 50 lignes)
   - La version exacte d'Odoo (19.0.x.x)

## 🎯 Résumé Rapide

```
1. Installer module : Apps > l10n_dz_cpss > Installer
2. Pays société : Algérie (DZ)
3. Le template s'applique automatiquement
4. Vérifier : Comptabilité > Plan comptable (1183 comptes)
```

Si ça ne marche pas : Mode développeur > Comptabilité > Install Chart of Accounts > Algérie - CPSS
