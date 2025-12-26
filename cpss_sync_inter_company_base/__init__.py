from . import models

def post_init_hook(env):
    """Hook exécuté après l'installation du module - Odoo 19"""
    import logging

    _logger = logging.getLogger(__name__)

    try:
        # 1. Configuration des données partagées
        _logger.info("Configuration des données partagées...")
        config = env['cpss.sync.config'].search([], limit=1)
        if config:
            config.configurer_donnees_partagees()

        # 2. Message de confirmation
        _logger.info("✅ Module CPSS Sync installé avec succès !")
        _logger.info("- Service comptabilité créé automatiquement")
        _logger.info("- Utilisateur technique configuré")
        _logger.info("- Données partagées entre sociétés")
        _logger.info("- Configuration de synchronisation prête")

    except Exception as e:
        _logger.error("❌ Erreur lors de la configuration post-installation : %s", str(e))