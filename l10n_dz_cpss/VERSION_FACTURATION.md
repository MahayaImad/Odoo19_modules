# Version Facturation Seulement (Sans Comptabilité)

## Différence entre les versions

### Version COMPLÈTE (actuelle - l10n_dz_cpss)
**Nécessite :** Module Comptabilité (account)

**Fonctionnalités :**
- ✅ Plan comptable complet (1183 comptes)
- ✅ Groupes de comptes hiérarchiques
- ✅ Écritures comptables
- ✅ Journaux comptables
- ✅ Rapports comptables
- ✅ Codes d'activité
- ✅ Formes juridiques
- ✅ Informations fiscales (NIS, NIF, AI, RC)
- ✅ Taxes algériennes

### Version FACTURATION (à créer - l10n_dz_cpss_light)
**Nécessite :** Module Facturation seulement

**Fonctionnalités :**
- ❌ Plan comptable complet (pas disponible en Facturation)
- ❌ Groupes de comptes
- ❌ Écritures comptables avancées
- ❌ Journaux comptables
- ❌ Rapports comptables
- ✅ Codes d'activité
- ✅ Formes juridiques
- ✅ Informations fiscales (NIS, NIF, AI, RC)
- ✅ Taxes algériennes (TVA 19%, 9%)

## Recommandation

### Pour une VRAIE Comptabilité Algérienne
➡️ **Installer le module Comptabilité** puis l10n_dz_cpss

Le module Comptabilité est **GRATUIT** dans Odoo Community !

### Pour Facturation Simple
➡️ Utiliser l10n_dz_cpss_light (version simplifiée)

## Comment Installer la Comptabilité

### Vérifier si la Comptabilité est disponible

```bash
# Dans Odoo
Apps > Supprimer tous les filtres
Rechercher : "Comptabilité" ou "Accounting"
```

**Si vous voyez le module :**
- Cliquer sur "Installer"
- Attendre l'installation
- Redémarrer Odoo
- Le menu "Comptabilité" apparaîtra

**Si le module n'existe pas :**
- Vous avez une version d'Odoo très limitée
- Utiliser la version Facturation seulement

### Installation via ligne de commande

```bash
# Installer Comptabilité
odoo-bin -i account -d votre_base --stop-after-init

# Puis installer l10n_dz_cpss
odoo-bin -i l10n_dz_cpss -d votre_base --stop-after-init

# Redémarrer
sudo systemctl restart odoo
```

## Créer la Version Facturation

Si vous voulez vraiment seulement Facturation, je peux créer :

**Module : l10n_dz_cpss_light**

```python
{
    'name': 'Algérie - CPSS (Facturation)',
    'depends': [
        'account_invoicing',  # Ou 'account' si disponible
        'sale',
    ],
    # Pas de template de plan comptable
    # Seulement taxes et infos fiscales
}
```

**Inclus :**
- Modèles : activity_code, forme_juridique, res_company, res_partner
- Vues : Formulaires société et partenaires
- Taxes : TVA 19%, TVA 9%
- Données : Formes juridiques par défaut

**Exclu :**
- template_dz.py (plan comptable)
- account.group CSV
- account.account CSV
- Fonctionnalités comptables avancées

## Que Faire Maintenant ?

### Option A : Installer Comptabilité (RECOMMANDÉ)

```
1. Apps > Rechercher "Comptabilité"
2. Installer
3. Le module l10n_dz_cpss fonctionnera complètement
```

### Option B : Version Facturation Seulement

```
1. Me confirmer que vous voulez la version light
2. Je vais créer l10n_dz_cpss_light
3. Désinstaller l10n_dz_cpss
4. Installer l10n_dz_cpss_light
```

### Option C : Vérifier d'abord

```bash
# Vérifier si account est installé
odoo-bin shell -d votre_base
>>> env['ir.module.module'].search([('name', '=', 'account')])
>>> # Si ça retourne un module, il existe !
```

## Questions Fréquentes

**Q: Le module Comptabilité est-il gratuit ?**
A: OUI ! Dans Odoo Community, c'est totalement gratuit.

**Q: La Comptabilité va ralentir Odoo ?**
A: Non, impact minimal. Vous pouvez l'installer même si vous l'utilisez peu.

**Q: Puis-je passer de Facturation à Comptabilité plus tard ?**
A: OUI ! Vous pouvez installer Comptabilité à tout moment.

**Q: Ai-je besoin de la Comptabilité pour facturer ?**
A: NON pour facturer basique, OUI pour un vrai suivi comptable.

## Conclusion

**Pour l'Algérie, je recommande fortement d'installer la Comptabilité** car :
- Le SCF algérien nécessite une vraie comptabilité
- Les déclarations fiscales nécessitent les journaux
- C'est gratuit dans Odoo Community
- Vous aurez toutes les fonctionnalités de l10n_dz_cpss
