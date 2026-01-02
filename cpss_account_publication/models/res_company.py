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

    enable_publication_stock_tracking = fields.Boolean(
        string="Activer le suivi du stock publié/non publié",
        default=False,
        help="Si activé, le système suivra le stock publié et non publié séparément. "
             "Lors de la publication d'une facture, il vérifiera que suffisamment de stock publié est disponible."
    )

    @api.constrains('journal_publication_id')
    def _check_journal_publication(self):
        for company in self:
            if company.journal_publication_id and company.journal_publication_id.company_id != company:
                raise ValidationError(_("Le journal de publication doit appartenir à la même société."))