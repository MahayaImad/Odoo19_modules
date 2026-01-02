# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    journal_publication_id = fields.Many2one(
        'account.journal',
        string='Journal des factures publiées',
        related='company_id.journal_publication_id',
        readonly=False,
        domain="[('type', 'in', ['bank', 'cash']), ('company_id', '=', company_id)]",
        help="Journal utilisé pour enregistrer les paiements des factures publiées"
    )

    publication_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Séquence des factures publiées',
        related='company_id.publication_sequence_id',
        readonly=False,
        help="Séquence utilisée pour numéroter les factures publiées"
    )

    def action_open_company_form(self):
        """Ouvre le formulaire de configuration de la société"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Configuration de la société'),
            'res_model': 'res.company',
            'res_id': self.company_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        }