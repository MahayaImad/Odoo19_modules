# -*- coding: utf-8 -*-
"""
Extension avancée pour gérer les cas particuliers des paiements sur factures publiées
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveAdvanced(models.Model):
    _inherit = 'account.move'

    has_publication_conflict = fields.Boolean(
        compute='_compute_has_publication_conflict',
        string="Conflit de publication"
    )

    @api.depends('publication_state', 'payment_state')
    def _compute_has_publication_conflict(self):
        """Détecte s'il y a un conflit entre l'état de publication et les paiements"""
        for move in self:
            move.has_publication_conflict = (
                    move.publication_state == 'published' and
                    move.payment_state in ['paid', 'partial'] and
                    move.company_id.journal_publication_id and
                    any(
                        payment.journal_id != move.company_id.journal_publication_id
                        for payment in move._get_reconciled_payments()
                    )
            )

    def action_publish_with_payment_handling(self):
        """
        Publication avancée qui gère les paiements existants.
        Propose de migrer les paiements vers le journal de publication ou de les dissocier.
        """
        self.ensure_one()

        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("Seuls les comptables peuvent publier des factures."))

        if self.publication_state == 'published':
            raise UserError(_("Cette facture est déjà publiée."))

        # Vérifier s'il y a des paiements existants
        if self.payment_state in ['paid', 'partial']:
            payments = self._get_reconciled_payments()
            if payments and self.company_id.journal_publication_id:
                # Demander à l'utilisateur ce qu'il veut faire
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Gestion des paiements existants'),
                    'res_model': 'account.move.publication.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_move_id': self.id,
                        'default_payment_ids': [(6, 0, payments.ids)],
                        'default_action': 'migrate',
                    }
                }

        # Si pas de paiements, publication normale
        return self.action_publish()

    def migrate_payments_to_publication_journal(self):
        """
        Migre les paiements existants vers le journal de publication.
        Cette méthode créé de nouvelles écritures pour transférer les montants.
        """
        self.ensure_one()

        if not self.company_id.journal_publication_id:
            raise UserError(_("Aucun journal de publication n'est configuré."))

        payments = self._get_reconciled_payments()
        publication_journal = self.company_id.journal_publication_id

        for payment in payments:
            if payment.journal_id == publication_journal:
                continue  # Déjà dans le bon journal

            # Créer une écriture de transfert
            transfer_move = self.env['account.move'].create({
                'move_type': 'entry',
                'journal_id': payment.journal_id.id,
                'date': fields.Date.today(),
                'ref': _('Transfert vers journal de publication - %s') % self.name,
                'line_ids': [
                    (0, 0, {
                        'name': _('Transfert sortant - %s') % payment.name,
                        'account_id': payment.destination_account_id.id,
                        'debit': 0,
                        'credit': payment.amount,
                        'partner_id': self.partner_id.id,
                    }),
                    (0, 0, {
                        'name': _('Transfert sortant - %s') % payment.name,
                        'account_id': payment.journal_id.default_account_id.id,
                        'debit': payment.amount,
                        'credit': 0,
                        'partner_id': self.partner_id.id,
                    }),
                    (0, 0, {
                        'name': _('Transfert entrant - %s') % payment.name,
                        'account_id': publication_journal.default_account_id.id,
                        'debit': 0,
                        'credit': payment.amount,
                        'partner_id': self.partner_id.id,
                    }),
                    (0, 0, {
                        'name': _('Transfert entrant - %s') % payment.name,
                        'account_id': payment.destination_account_id.id,
                        'debit': payment.amount,
                        'credit': 0,
                        'partner_id': self.partner_id.id,
                    }),
                ],
            })

            transfer_move.action_post()

        return True

    def _get_reconciled_payments(self):
        """Retourne les paiements réconciliés avec cette facture"""
        self.ensure_one()

        reconciled_lines = self.line_ids.filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
        reconciled_amls = reconciled_lines.mapped('matched_debit_ids.debit_move_id') + \
                          reconciled_lines.mapped('matched_credit_ids.credit_move_id')

        payments = reconciled_amls.mapped('payment_id')
        return payments


class AccountMovePublicationWizard(models.TransientModel):
    """Wizard pour gérer les conflits lors de la publication"""
    _name = 'account.move.publication.wizard'
    _description = 'Assistant de publication avec gestion des paiements'

    move_id = fields.Many2one(
        'account.move',
        string='Facture',
        required=True,
        readonly=True
    )

    payment_ids = fields.Many2many(
        'account.payment',
        string='Paiements existants',
        readonly=True
    )

    action = fields.Selection([
        ('migrate', 'Migrer les paiements vers le journal de publication'),
        ('dissociate', 'Dissocier les paiements de la facture'),
        ('keep', 'Conserver les paiements dans leur journal actuel'),
    ], string='Action à effectuer', default='migrate', required=True)

    def action_confirm(self):
        """Confirme l'action choisie et publie la facture"""
        self.ensure_one()

        if self.action == 'migrate':
            self.move_id.migrate_payments_to_publication_journal()
        elif self.action == 'dissociate':
            # Délier les paiements (annuler la réconciliation)
            self._dissociate_payments()
        # Si 'keep', on ne fait rien de spécial

        # Publier la facture
        self.move_id.action_publish()

        return {'type': 'ir.actions.act_window_close'}

    def _dissociate_payments(self):
        """Dissocie les paiements de la facture"""
        for payment in self.payment_ids:
            # Trouver les lignes réconciliées
            reconciled_lines = payment.move_id.line_ids.filtered(
                lambda l: l.matched_debit_ids or l.matched_credit_ids
            )

            # Annuler la réconciliation
            for line in reconciled_lines:
                if line.matched_debit_ids:
                    line.matched_debit_ids.unlink()
                if line.matched_credit_ids:
                    line.matched_credit_ids.unlink()

        return True