from . import models

def _l10n_dz_post_init(env):
    """
    Hook d'installation pour configurer le plan comptable algérien
    """
    try:
        # Configuration des comptes par défaut pour les entreprises algériennes
        env['res.company']._setup_dz_accounting_defaults()

        # Créer les données de base si nécessaire
        env['res.company'].create_default_dz_chart()

        # Log de succès
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info("Module l10n_dz_cpss installé avec succès - Configuration comptable algérienne appliquée")

    except Exception as e:
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning(f"Erreur lors de la post-installation du module l10n_dz_cpss: {e}")
        # Ne pas faire échouer l'installation