# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    journal_publication_id = fields.Many2one(
        'account.journal',
        string='Journal des factures publiées',
        domain="[('type', 'in', ['bank', 'cash'])]",
        help="Journal utilisé pour enregistrer les paiements des factures publiées"
    )

    publication_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Séquence des factures publiées',
        help="Séquence utilisée pour numéroter les factures publiées"
    )

    @api.constrains('journal_publication_id')
    def _check_journal_publication(self):
        for company in self:
            if company.journal_publication_id and company.journal_publication_id.company_id != company:
                raise ValidationError(_("Le journal de publication doit appartenir à la même société."))