
{
    "name": "CPSS Sync Inter Company Base",
    "summary": "Base module for synchronization between operational and fiscal companies",
    "version": "19.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/cpss/odoo-modules",
    "author": "CPSS",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base",
        "mail",
        "account",
        "sale",
        "purchase",
        "stock",
        #"l10n_dz_cpss",
    ],
    "data": [
        # Security
        "security/sync_security.xml",
        "security/ir_rules_sync.xml",
        "security/ir.model.access.csv",

        # Data
        "data/auto_setup_data.xml",
        "data/company_data_config_data.xml",

        # Views
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
        'views/cpss_sync_log_views.xml',
        'views/cpss_company_data_config_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/sync_menus.xml',
    ],

    "assets": {
        "web.assets_backend": [
            "cpss_sync_inter_company_base/static/src/scss/navbar_color.scss",
            "cpss_sync_inter_company_base/static/src/js/navbar_color.js",
        ],
    },

    "external_dependencies": {
        "python": [],
    },
    "post_init_hook": "post_init_hook",
}
