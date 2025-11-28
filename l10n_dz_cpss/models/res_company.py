# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re

GLOBAL_REGEXEX_NIS_NIF = "^[a-zA-Z0-9]{15}$"

class ResCompany(models.Model):
    _inherit = 'res.company'

    activity_code = fields.Many2many("activity.code", string="Code d'activité", index=True, ondelete="cascade")

    # Les configurations qui permettent d'afficher le code/secteur d'activité sur les rapports (Devis/Facture)
    industry_id_in_invoice = fields.Boolean(string="Secteur d'activité")
    activity_code_in_invoice = fields.Boolean(string="Code d'activité")

    industry_id_in_quotation = fields.Boolean(string="Secteur d'activité")
    activity_code_in_quotation = fields.Boolean(string="Code d'activité")


    transfer_tax_journal = fields.Many2one("account.journal", string="Journal de transfert de taxe", default=lambda self: self.env['account.journal'].search([('type', '=', 'general')], limit=1).id)
    temporary_tax_account = fields.Many2one("account.account", string="Compte temporaire de taxe")
    based_on = fields.Selection(
        [('posted_invoices', 'Factures validées'),
         ('payment', 'Paiements des factures')], default="payment", string="Basé sur")




    fax = fields.Char(
        string="Fax"
    )

    capital_social = fields.Monetary(
        string="Capital Social",
        currency_field='currency_id',
        required=True,
        default=0.0
    )

    rc = fields.Char(
        string="N° RC"
    )

    nis = fields.Char(
        string="N.I.S"
    )

    ai = fields.Char(
        string="A.I"
    )

    nif = fields.Char(
        string="N.I.F"
    )

    forme_juridique = fields.Many2one(
        comodel_name='forme.juridique',
        string="Forme juridique"
    )




    @api.model
    def verifer_juridique_records(self):
        jur = self.env['forme.juridique']
        vals = []
        vals.append({
            'code': 'SARL',
            'name': 'Société à responsabilité limitée',
            })
        vals.append({
            'code': 'EURL',
            'name': 'Société unipersonnelle à responsabilité limitée',
            })
        vals.append({
            'code': 'Entreprise Individuelle',
            'name': 'Entreprise Individuelle',
            })
        vals.append({
            'code': 'SPA',
            'name': 'Société par actions',
            })
        vals.append({
            'code': 'SNC',
            'name': 'Société en nom collectif',
            })
        vals.append({
            'code': 'SCS',
            'name': 'Société en commandite simple',
            })
        vals.append({
            'code': 'SCPA',
            'name': 'Société en commandite par actions',
            })
        vals.append({
            'code': 'Groupement',
            'name': 'Groupement',
            })
        for val in vals:
            if not jur.search([('code', '=', val['code'])]):
                jur.create(val)


class BaseDocumentLayout2(models.TransientModel):
    _inherit = 'base.document.layout'

    street = fields.Char(
        string='Street',
    )

    street2 = fields.Char(
        string='Street 2',
    )

    zip = fields.Char(
        string='Zip',
    )

    city = fields.Char(
        string='City',
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='State',
    )

    country_id = fields.Many2one(
        'res.country',
        string='Country',
    )


    fax = fields.Char(
        string="Fax"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related='company_id.currency_id',
        readonly=True
    )

    capital_social = fields.Monetary(
        string="Capital Social",
        currency_field='currency_id',
        required=True,
        default=0.0
    )

    rc = fields.Char(
        string="N° RC"
    )

    nis = fields.Char(
        string="N.I.S"
    )

    ai = fields.Char(
        string="A.I"
    )

    nif = fields.Char(
        string="N.I.F"
    )

    forme_juridique = fields.Many2one(
        comodel_name='forme.juridique',
        string="Forme juridique"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    industry_id_in_invoice = fields.Boolean(string="Secteur d'activité")
    activity_code_in_invoice = fields.Boolean(string="Code d'activité")

    industry_id_in_quotation = fields.Boolean(string="Secteur d'activité")
    activity_code_in_quotation = fields.Boolean(string="Code d'activité")


    transfer_tax_journal = fields.Many2one("account.journal", string="Journal de transfert de taxe")
    temporary_tax_account = fields.Many2one("account.account", string="Compte temporaire de taxe")
    based_on = fields.Selection(
        [('posted_invoices', 'Factures validées'),
         ('payment', 'Paiements des factures')], default="payment", string="Basé sur")




    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.env.company

        company and res.update(

            transfer_tax_journal=company.transfer_tax_journal,
            temporary_tax_account=company.temporary_tax_account,
            based_on=company.based_on,
            industry_id_in_invoice=company.industry_id_in_invoice,
            activity_code_in_invoice=company.activity_code_in_invoice,
            industry_id_in_quotation=company.industry_id_in_quotation,
            activity_code_in_quotation=company.activity_code_in_quotation,



        )
        return res


    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        company = self.env.company
        company and company.write({

            'transfer_tax_journal': self.transfer_tax_journal,
            'temporary_tax_account': self.temporary_tax_account,
            'based_on': self.based_on,
            'industry_id_in_invoice': self.industry_id_in_invoice,
            'activity_code_in_invoice': self.activity_code_in_invoice,
            'industry_id_in_quotation': self.industry_id_in_quotation,
            'activity_code_in_quotation': self.activity_code_in_quotation,




        })
        return res
