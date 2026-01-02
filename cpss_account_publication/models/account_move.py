# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    publication_state = fields.Selection(
        [
            ('not_published', 'Non publié'),
            ('published', 'Publié'),
        ],
        string="État de publication",
        default='not_published',
        tracking=True,
        copy=False,
        help="Indique si la facture a été publiée avec une séquence spécifique"
    )

    publication_number = fields.Char(
        string="Numéro de publication",
        copy=False,
        readonly=True,
        help="Numéro attribué lors de la publication de la facture"
    )

    publication_date = fields.Datetime(
        string="Date de publication",
        copy=False,
        readonly=True,
        help="Date à laquelle la facture a été publiée"
    )

    can_toggle_publication = fields.Boolean(
        compute='_compute_can_toggle_publication',
        string="Peut publier/dépublier"
    )

    @api.depends_context('uid')
    def _compute_can_toggle_publication(self):
        """Vérifie si l'utilisateur actuel peut publier/dépublier"""
        can_publish = self.env.user.has_group('account.group_account_manager')
        for move in self:
            move.can_toggle_publication = can_publish

    def action_publish(self):
        """Publie la facture avec une séquence spécifique"""
        for move in self:
            if not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Seuls les comptables peuvent publier des factures."))

            if move.publication_state == 'published':
                raise UserError(_("Cette facture est déjà publiée."))

            # Pour les factures clients, générer un numéro de séquence
            if move.move_type in ['out_invoice', 'out_refund']:
                # Utiliser la séquence de publication
                sequence_code = 'account.move.publication'
                publication_number = self.env['ir.sequence'].next_by_code(sequence_code)

                if not publication_number:
                    # Créer la séquence si elle n'existe pas
                    sequence = self.env['ir.sequence'].sudo().create({
                        'name': 'Factures publiées',
                        'code': sequence_code,
                        'prefix': 'PUB/%(year)s/',
                        'padding': 5,
                        'company_id': move.company_id.id,
                    })
                    publication_number = sequence.next_by_code(sequence_code)

                move.publication_number = publication_number

            # Pour les factures fournisseurs, utiliser le numéro du fournisseur
            elif move.move_type in ['in_invoice', 'in_refund']:
                if not move.ref:
                    raise UserError(
                        _("Veuillez saisir le numéro de facture fournisseur dans le champ 'Référence' avant de publier."))
                move.publication_number = move.ref

            move.write({
                'publication_state': 'published',
                'publication_date': fields.Datetime.now(),
            })

        return True

    def action_unpublish(self):
        """Dépublie la facture"""
        for move in self:
            if not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Seuls les comptables peuvent dépublier des factures."))

            if move.publication_state == 'not_published':
                raise UserError(_("Cette facture n'est pas publiée."))

            # Vérifier s'il y a des paiements liés
            if move.payment_state in ['paid', 'partial']:
                # Avertissement mais permettre la dépublication
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Attention'),
                        'message': _(
                            'Cette facture a des paiements enregistrés. La dépublication ne supprimera pas les paiements existants.'),
                        'type': 'warning',
                        'sticky': False,
                        'next': {
                            'type': 'ir.actions.act_window_close',
                        }
                    }
                }

            move.publication_state = 'not_published'
            # Ne pas effacer le numéro et la date pour garder l'historique

        return True

    def action_toggle_publication(self):
        """Bascule entre publié et non publié"""
        for move in self:
            if move.publication_state == 'not_published':
                return move.action_publish()
            else:
                return move.action_unpublish()

    @api.constrains('publication_state', 'state')
    def _check_publication_state(self):
        """Vérifie les contraintes de publication"""
        for move in self:
            # Empêcher la suppression d'une facture publiée
            if move.publication_state == 'published' and move.state == 'cancel':
                raise ValidationError(
                    _("Vous ne pouvez pas annuler une facture publiée. Veuillez d'abord la dépublier."))

    def unlink(self):
        """Surcharge pour empêcher la suppression de factures publiées"""
        for move in self:
            if move.publication_state == 'published':
                raise UserError(_("Vous ne pouvez pas supprimer une facture publiée. Veuillez d'abord la dépublier."))
        return super().unlink()

    def _get_payment_journal(self):
        """Retourne le journal de paiement approprié selon l'état de publication"""
        self.ensure_one()
        if self.publication_state == 'published' and self.company_id.journal_publication_id:
            return self.company_id.journal_publication_id
        return super()._get_payment_journal() if hasattr(super(), '_get_payment_journal') else False