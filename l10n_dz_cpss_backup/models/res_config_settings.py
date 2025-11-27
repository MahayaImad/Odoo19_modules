# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    industry_id_in_invoice = fields.Boolean(
        string="Secteur d'activité sur factures",  # Label unique
        related='company_id.industry_id_in_invoice',
        readonly=False,
        help="Afficher le secteur d'activité sur les factures"
    )
    activity_code_in_invoice = fields.Boolean(
        string="Code d'activité sur factures",  # Label unique
        related='company_id.activity_code_in_invoice',
        readonly=False,
        help="Afficher le code d'activité sur les factures"
    )
    industry_id_in_quotation = fields.Boolean(
        string="Secteur d'activité sur devis",  # Label unique
        related='company_id.industry_id_in_quotation',
        readonly=False,
        help="Afficher le secteur d'activité sur les devis"
    )
    activity_code_in_quotation = fields.Boolean(
        string="Code d'activité sur devis",  # Label unique
        related='company_id.activity_code_in_quotation',
        readonly=False,
        help="Afficher le code d'activité sur les devis"
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