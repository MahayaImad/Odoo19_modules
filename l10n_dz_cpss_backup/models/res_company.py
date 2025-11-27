# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re

GLOBAL_REGEXEX_NIS_NIF = "^[a-zA-Z0-9]{15}$"


class ResCompany(models.Model):
    _inherit = 'res.company'

    activity_code = fields.Many2many(
        "activity.code",
        string="Code d'activité",
        index=True,
        ondelete="cascade"
    )

    # Configurations pour l'affichage du code/secteur d'activité sur les rapports
    industry_id_in_invoice = fields.Boolean(string="Secteur d'activité")
    activity_code_in_invoice = fields.Boolean(string="Code d'activité")
    industry_id_in_quotation = fields.Boolean(string="Secteur d'activité")
    activity_code_in_quotation = fields.Boolean(string="Code d'activité")

    # Configuration taxe
    transfer_tax_journal = fields.Many2one(
        "account.journal",
        string="Journal de transfert de taxe",
        default=lambda self: self.env['account.journal'].search([('type', '=', 'general')], limit=1)
    )
    temporary_tax_account = fields.Many2one("account.account", string="Compte temporaire de taxe")
    based_on = fields.Selection(
        [('posted_invoices', 'Factures validées'),
         ('payment', 'Paiements des factures')],
        default="payment",
        string="Basé sur"
    )

    # Informations entreprise algérienne
    fax = fields.Char(string="Fax", size=64)
    capital_social = fields.Float(string="Capital Social", required=True, default=0.0)
    rc = fields.Char(string="N° RC")
    nis = fields.Char(string="N.I.S", size=15)
    ai = fields.Char(string="A.I", size=11)
    nif = fields.Char(string="N.I.F", size=15)
    forme_juridique = fields.Many2one('forme.juridique', string="Forme juridique")

    @api.constrains('nis')
    def _check_nis(self):
        for record in self:
            if record.nis and not re.match(GLOBAL_REGEXEX_NIS_NIF, record.nis):
                raise ValidationError(_("Le format du N.I.S doit être de 15 caractères alphanumériques."))

    @api.constrains('nif')
    def _check_nif(self):
        for record in self:
            if record.nif and not re.match(GLOBAL_REGEXEX_NIS_NIF, record.nif):
                raise ValidationError(_("Le format du N.I.F doit être de 15 caractères alphanumériques."))

    @api.model
    def verifier_juridique_records(self):
        """
        Fonction appelée lors de l'installation/mise à jour du module
        pour vérifier et nettoyer les données juridiques des sociétés
        """
        companies = self.search([])
        for company in companies:
            # Vérifier si l'entreprise est algérienne
            if company.country_id and company.country_id.code == 'DZ':
                # Nettoyer les champs NIS et NIF
                if company.nis:
                    company.nis = company.nis.strip().upper()
                if company.nif:
                    company.nif = company.nif.strip().upper()
                if company.ai:
                    company.ai = company.ai.strip().upper()

                # Configurer les paramètres par défaut pour les entreprises algériennes
                if not company.based_on:
                    company.based_on = 'payment'

                # Assigner une forme juridique par défaut si nécessaire
                if not company.forme_juridique:
                    default_forme = self.env['forme.juridique'].search([
                        ('name', 'ilike', 'SARL')
                    ], limit=1)
                    if default_forme:
                        company.forme_juridique = default_forme.id

        # Créer des données de base si elles n'existent pas
        self._create_default_activity_codes()
        self._create_default_formes_juridiques()

    @api.model
    def _create_default_activity_codes(self):
        """Créer des codes d'activité par défaut"""
        ActivityCode = self.env['activity.code']

        default_codes = [
            {'code': 47110, 'name': 'Commerce de détail en magasin non spécialisé'},
            {'code': 47190, 'name': 'Autre commerce de détail en magasin non spécialisé'},
            {'code': 62010, 'name': 'Programmation informatique'},
            {'code': 62020, 'name': 'Conseil en systèmes et logiciels informatiques'},
            {'code': 68200, 'name': 'Location et exploitation de biens immobiliers propres ou loués'},
        ]

        for code_data in default_codes:
            existing = ActivityCode.search([('code', '=', code_data['code'])], limit=1)
            if not existing:
                ActivityCode.create({
                    'code': code_data['code'],
                    'name': code_data['name'],
                    'regulation': 'none',
                    'company_id': False,  # Code global
                })

    @api.model
    def _create_default_formes_juridiques(self):
        """Créer des formes juridiques par défaut"""
        FormeJuridique = self.env['forme.juridique']

        default_formes = [
            {'code': 'SARL', 'name': 'Société à Responsabilité Limitée'},
            {'code': 'SPA', 'name': 'Société Par Actions'},
            {'code': 'SNC', 'name': 'Société en Nom Collectif'},
            {'code': 'SCS', 'name': 'Société en Commandite Simple'},
            {'code': 'EI', 'name': 'Entreprise Individuelle'},
            {'code': 'EURL', 'name': 'Entreprise Unipersonnelle à Responsabilité Limitée'},
        ]

        for forme_data in default_formes:
            existing = FormeJuridique.search([('code', '=', forme_data['code'])], limit=1)
            if not existing:
                FormeJuridique.create({
                    'code': forme_data['code'],
                    'name': forme_data['name'],
                    'company_id': False,  # Forme globale
                })

    @api.model
    def _setup_dz_accounting_defaults(self):
        """
        Configure les comptes par défaut pour les entreprises algériennes
        Appelé lors de l'installation du module
        """
        dz_companies = self.env['res.company'].search([
            ('country_id', '=', self.env.ref('base.dz').id)
        ])

        if not dz_companies:
            dz_companies = self.env['res.company'].search([])

        for company in dz_companies:
            company._configure_dz_accounts()

    def _configure_dz_accounts(self):
        """Configure les comptes par défaut pour cette entreprise"""
        # Récupérer les comptes de base
        try:
            receivable_account = self.env.ref('l10n_dz_cpss.pcg_411000', raise_if_not_found=False)
            payable_account = self.env.ref('l10n_dz_cpss.pcg_401000', raise_if_not_found=False)
            bank_account = self.env.ref('l10n_dz_cpss.pcg_512000', raise_if_not_found=False)
            cash_account = self.env.ref('l10n_dz_cpss.pcg_530000', raise_if_not_found=False)
            transfer_account = self.env.ref('l10n_dz_cpss.pcg_580000', raise_if_not_found=False)
            expense_account = self.env.ref('l10n_dz_cpss.pcg_601000', raise_if_not_found=False)
            income_account = self.env.ref('l10n_dz_cpss.pcg_701000', raise_if_not_found=False)

            # Configuration des comptes par défaut
            vals = {}
            if receivable_account:
                vals['account_default_pos_receivable_account_id'] = receivable_account.id
            if payable_account:
                vals['account_default_pos_payable_account_id'] = payable_account.id
            if expense_account:
                vals['default_expense_account_id'] = expense_account.id
            if income_account:
                vals['default_income_account_id'] = income_account.id

            if vals:
                self.write(vals)

            # Configuration des journaux bancaires avec les bons comptes
            if bank_account:
                bank_journals = self.env['account.journal'].search([
                    ('company_id', '=', self.id),
                    ('type', '=', 'bank')
                ])
                for journal in bank_journals:
                    if not journal.default_account_id:
                        journal.default_account_id = bank_account.id

            if cash_account:
                cash_journals = self.env['account.journal'].search([
                    ('company_id', '=', self.id),
                    ('type', '=', 'cash')
                ])
                for journal in cash_journals:
                    if not journal.default_account_id:
                        journal.default_account_id = cash_account.id

        except Exception as e:
            # Log l'erreur mais ne fait pas échouer l'installation
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f"Erreur lors de la configuration des comptes par défaut: {e}")

    @api.model
    def create_default_dz_chart(self):
        """
        Méthode appelée pour créer le plan comptable par défaut
        pour les nouvelles entreprises algériennes
        """
        companies = self.search([
            ('country_id', '=', self.env.ref('base.dz').id)
        ])

        for company in companies:
            # Créer les comptes de base si ils n'existent pas
            company._ensure_basic_accounts()
            company._configure_dz_accounts()

    def _ensure_basic_accounts(self):
        """S'assurer que les comptes de base existent pour cette entreprise"""
        accounts_to_create = [
            ('101000', 'Capital émis', 'equity'),
            ('401000', 'Fournisseurs', 'liability_payable'),
            ('411000', 'Clients', 'asset_receivable'),
            ('512000', 'Banques', 'asset_cash'),
            ('530000', 'Caisse', 'asset_cash'),
            ('601000', 'Achats de marchandises', 'expense'),
            ('701000', 'Ventes de marchandises', 'income'),
        ]

        for code, name, account_type in accounts_to_create:
            existing = self.env['account.account'].search([
                ('code', '=', code),
                ('company_id', '=', self.id)
            ], limit=1)

            if not existing:
                self.env['account.account'].create({
                    'code': code,
                    'name': name,
                    'account_type': account_type,
                    'company_id': self.id,
                    'reconcile': account_type in ['asset_receivable', 'liability_payable']
                })


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    industry_id_in_invoice = fields.Boolean(
        string="Secteur d'activité",
        related='company_id.industry_id_in_invoice',
        readonly=False
    )
    activity_code_in_invoice = fields.Boolean(
        string="Code d'activité",
        related='company_id.activity_code_in_invoice',
        readonly=False
    )
    industry_id_in_quotation = fields.Boolean(
        string="Secteur d'activité",
        related='company_id.industry_id_in_quotation',
        readonly=False
    )
    activity_code_in_quotation = fields.Boolean(
        string="Code d'activité",
        related='company_id.activity_code_in_quotation',
        readonly=False
    )
    transfer_tax_journal = fields.Many2one(
        "account.journal",
        string="Journal de transfert de taxe",
        related='company_id.transfer_tax_journal',
        readonly=False
    )
    temporary_tax_account = fields.Many2one(
        "account.account",
        string="Compte temporaire de taxe",
        related='company_id.temporary_tax_account',
        readonly=False
    )
    based_on = fields.Selection(
        [('posted_invoices', 'Factures validées'),
         ('payment', 'Paiements des factures')],
        string="Basé sur",
        related='company_id.based_on',
        readonly=False
    )