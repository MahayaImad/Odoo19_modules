# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import models


def post_init_hook(env):
    """
    Hook appelé après l'installation du module
    S'assure que le template est bien enregistré et configure le compte equity_unaffected
    """
    import logging
    _logger = logging.getLogger(__name__)

    # Forcer le rechargement du template
    env['account.chart.template'].flush_model()

    # Gérer le compte equity_unaffected (120000 au lieu de 999999)
    # Rechercher et supprimer le compte 999999 auto-généré par Odoo s'il existe
    account_999999 = env['account.account'].search([
        ('code', '=', '999999'),
        ('account_type', '=', 'equity_unaffected')
    ], limit=1)

    if account_999999:
        _logger.info("Suppression du compte 999999 auto-généré")
        # Vérifier qu'il n'y a pas d'écritures sur ce compte avant de le supprimer
        if not env['account.move.line'].search_count([('account_id', '=', account_999999.id)]):
            account_999999.unlink()
            _logger.info("Compte 999999 supprimé avec succès")
        else:
            _logger.warning("Impossible de supprimer le compte 999999 car il contient des écritures")

    # Vérifier que le compte 120000 existe et est bien de type equity_unaffected
    account_120000 = env.ref('l10n_dz_cpss.l10n_dz_120000', raise_if_not_found=False)
    if account_120000:
        if account_120000.account_type != 'equity_unaffected':
            account_120000.account_type = 'equity_unaffected'
            _logger.info("Compte 120000 configuré comme equity_unaffected")

    # Configurer le pays pour les groupes de taxes
    try:
        country_dz = env.ref('base.dz', raise_if_not_found=False)
        if country_dz:
            tax_groups = env['account.tax.group'].search([
                ('id', 'in', [
                    env.ref('l10n_dz_cpss.l10n_dz_tax_group_vat_0', raise_if_not_found=False).id,
                    env.ref('l10n_dz_cpss.l10n_dz_tax_group_vat_9', raise_if_not_found=False).id,
                    env.ref('l10n_dz_cpss.l10n_dz_tax_group_vat_19', raise_if_not_found=False).id,
                ]),
                ('country_id', '=', False)
            ])
            if tax_groups:
                tax_groups.write({'country_id': country_dz.id})
                _logger.info(f"Pays (Algérie) configuré pour {len(tax_groups)} groupes de taxes")
        else:
            _logger.warning("Pays 'base.dz' (Algérie) non trouvé")
    except Exception as e:
        _logger.warning(f"Erreur lors de la configuration du pays pour les groupes de taxes: {e}")

    # Configurer les comptes par défaut de la société
    try:
        companies = env['res.company'].search([('chart_template', '=', 'dz_cpss')])
        for company in companies:
            vals = {}
            # Comptes de base
            if env.ref('l10n_dz_cpss.l10n_dz_413', raise_if_not_found=False):
                vals['account_default_pos_receivable_account_id'] = env.ref('l10n_dz_cpss.l10n_dz_413').id
            if env.ref('l10n_dz_cpss.l10n_dz_766', raise_if_not_found=False):
                vals['income_currency_exchange_account_id'] = env.ref('l10n_dz_cpss.l10n_dz_766').id
            if env.ref('l10n_dz_cpss.l10n_dz_666', raise_if_not_found=False):
                vals['expense_currency_exchange_account_id'] = env.ref('l10n_dz_cpss.l10n_dz_666').id
            if env.ref('l10n_dz_cpss.l10n_dz_709', raise_if_not_found=False):
                vals['account_journal_early_pay_discount_loss_account_id'] = env.ref('l10n_dz_cpss.l10n_dz_709').id
            if env.ref('l10n_dz_cpss.l10n_dz_609', raise_if_not_found=False):
                vals['account_journal_early_pay_discount_gain_account_id'] = env.ref('l10n_dz_cpss.l10n_dz_609').id
            if env.ref('l10n_dz_cpss.l10n_dz_758', raise_if_not_found=False):
                vals['default_cash_difference_income_account_id'] = env.ref('l10n_dz_cpss.l10n_dz_758').id
            if env.ref('l10n_dz_cpss.l10n_dz_657', raise_if_not_found=False):
                vals['default_cash_difference_expense_account_id'] = env.ref('l10n_dz_cpss.l10n_dz_657').id

            # Taxes par défaut
            if env.ref('l10n_dz_cpss.l10n_dz_vat_sale_19_prod', raise_if_not_found=False):
                vals['account_sale_tax_id'] = env.ref('l10n_dz_cpss.l10n_dz_vat_sale_19_prod').id
            if env.ref('l10n_dz_cpss.l10n_dz_vat_purchase_19', raise_if_not_found=False):
                vals['account_purchase_tax_id'] = env.ref('l10n_dz_cpss.l10n_dz_vat_purchase_19').id

            if vals:
                company.write(vals)
                _logger.info(f"Comptes et taxes par défaut configurés pour la société {company.name}")
    except Exception as e:
        _logger.warning(f"Erreur lors de la configuration des comptes: {e}")

    _logger.info("=" * 70)
    _logger.info("l10n_dz_cpss: post_init_hook appelé")
    _logger.info("Template 'dz_cpss' enregistré pour le plan comptable algérien")
    _logger.info("=" * 70)
