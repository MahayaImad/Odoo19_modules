from . import models

def post_init_hook(cr, registry):
    """Hook exécuté après l'installation du module"""
    import logging
    from odoo import api, SUPERUSER_ID

    _logger = logging.getLogger(__name__)



    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        try:
            # 1. Configuration des données partagées
            _logger.info("Configuration des données partagées...")
            config = env['cpss.sync.config'].search([], limit=1)
            if config:
                config.configurer_donnees_partagees()

            # 2. Message de confirmation
            _logger.info("✅ Module CPSS Sync installé avec succès !")
            _logger.info("- Société fiscale créée automatiquement")
            _logger.info("- Utilisateur technique configuré")
            _logger.info("- Données partagées entre sociétés")
            _logger.info("- Configuration de synchronisation prête")


        except Exception as e:
            _logger.error("❌ Erreur lors de la configuration post-installation : %s", str(e))







