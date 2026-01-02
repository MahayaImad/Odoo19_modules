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

    unpublished_number = fields.Char(
        string="Numéro avant publication",
        copy=False,
        readonly=True,
        help="Numéro de la facture avant publication (BL)"
    )

    @api.depends_context('uid')
    def _compute_can_toggle_publication(self):
        """Vérifie si l'utilisateur actuel peut publier/dépublier"""
        can_publish = self.env.user.has_group('account.group_account_manager')
        for move in self:
            move.can_toggle_publication = can_publish

    def _get_sequence_code_for_move_type(self, move_type, is_published):
        """
        Retourne le code de séquence approprié selon le type de facture et l'état de publication

        Séquences:
        - Facture client non publiée: BLC/year (Bon de Livraison Client)
        - Facture client publiée: FC/year (Facture Client)
        - Avoir client non publié: AVC/year (Avoir Client)
        - Avoir client publié: AC/year (Avoir Client Publié)
        - Facture fournisseur non publiée: BLF/year (Bon de Livraison Fournisseur)
        - Facture fournisseur publiée: FF/year (Facture Fournisseur)
        - Avoir fournisseur non publié: AVF/year
        - Avoir fournisseur publié: AF/year
        """
        sequence_mapping = {
            'out_invoice': {
                False: 'account.move.out_invoice.unpublished',  # BLC
                True: 'account.move.out_invoice.published',      # FC
            },
            'out_refund': {
                False: 'account.move.out_refund.unpublished',   # AVC
                True: 'account.move.out_refund.published',       # AC
            },
            'in_invoice': {
                False: 'account.move.in_invoice.unpublished',   # BLF
                True: 'account.move.in_invoice.published',       # FF
            },
            'in_refund': {
                False: 'account.move.in_refund.unpublished',    # AVF
                True: 'account.move.in_refund.published',        # AF
            },
        }

        return sequence_mapping.get(move_type, {}).get(is_published)

    def _get_sequence(self):
        """
        Surcharge de la méthode standard pour utiliser nos séquences personnalisées
        selon le type de facture et l'état de publication
        """
        self.ensure_one()

        # Vérifier si c'est un type de facture géré par notre module
        if self.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
            is_published = self.publication_state == 'published'
            sequence_code = self._get_sequence_code_for_move_type(self.move_type, is_published)

            if sequence_code:
                sequence = self.env['ir.sequence'].search([
                    ('code', '=', sequence_code),
                    '|',
                    ('company_id', '=', False),
                    ('company_id', '=', self.company_id.id)
                ], limit=1)

                if sequence:
                    return sequence

        # Sinon utiliser la séquence standard d'Odoo
        return super()._get_sequence()

    def _set_next_sequence(self):
        """
        Surcharge pour gérer les numéros de séquence selon l'état de publication
        """
        self.ensure_one()

        # Si la facture est déjà numérotée et qu'on change son statut de publication
        # on garde le numéro actuel dans unpublished_number ou publication_number
        if self.name and self.name != '/':
            if self.publication_state == 'published' and not self.publication_number:
                # On publie: sauvegarder le numéro BL et générer un nouveau numéro F
                self.unpublished_number = self.name
            elif self.publication_state == 'not_published' and self.unpublished_number:
                # On dépublie: restaurer le numéro BL
                self.name = self.unpublished_number
                return

        # Générer le nouveau numéro selon la séquence appropriée
        return super()._set_next_sequence()

    def action_publish(self):
        """Publie la facture avec une séquence spécifique"""
        for move in self:
            if not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Seuls les comptables peuvent publier des factures."))

            if move.publication_state == 'published':
                raise UserError(_("Cette facture est déjà publiée."))

            if move.state != 'posted':
                raise UserError(_("Vous ne pouvez publier qu'une facture comptabilisée."))

            # Sauvegarder le numéro actuel (BL) avant de publier
            if move.name and move.name != '/':
                move.unpublished_number = move.name

            # Générer le nouveau numéro de publication
            sequence_code = move._get_sequence_code_for_move_type(move.move_type, True)

            if sequence_code:
                publication_number = self.env['ir.sequence'].next_by_code(sequence_code)

                if not publication_number:
                    raise UserError(_(
                        "La séquence '%s' n'existe pas. Veuillez vérifier la configuration du module.") % sequence_code)

                # Mettre à jour avec le nouveau numéro publié
                move.write({
                    'name': publication_number,
                    'publication_number': publication_number,
                    'publication_state': 'published',
                    'publication_date': fields.Datetime.now(),
                })
            else:
                # Pour les autres types de factures, juste changer le statut
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
                raise UserError(_(
                    "Vous ne pouvez pas dépublier une facture qui a des paiements enregistrés. "
                    "Veuillez d'abord annuler les paiements."))

            # Restaurer le numéro non publié (BL) si disponible
            values = {'publication_state': 'not_published'}

            if move.unpublished_number:
                values['name'] = move.unpublished_number
            else:
                # Si pas de numéro BL sauvegardé, générer un nouveau
                sequence_code = move._get_sequence_code_for_move_type(move.move_type, False)
                if sequence_code:
                    new_number = self.env['ir.sequence'].next_by_code(sequence_code)
                    if new_number:
                        values['name'] = new_number

            move.write(values)
            # Garder publication_number et publication_date pour l'historique

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
            # Empêcher l'annulation d'une facture publiée
            if move.publication_state == 'published' and move.state == 'cancel':
                raise ValidationError(
                    _("Vous ne pouvez pas annuler une facture publiée. Veuillez d'abord la dépublier."))

    def unlink(self):
        """Surcharge pour empêcher la suppression de factures publiées"""
        for move in self:
            if move.publication_state == 'published':
                raise UserError(_("Vous ne pouvez pas supprimer une facture publiée. Veuillez d'abord la dépublier."))
        return super().unlink()

    def button_draft(self):
        """Empêcher le passage en brouillon des factures publiées"""
        for move in self:
            if move.publication_state == 'published':
                raise UserError(_("Vous ne pouvez pas repasser en brouillon une facture publiée. Veuillez d'abord la dépublier."))
        return super().button_draft()

    def _get_payment_journal(self):
        """Retourne le journal de paiement approprié selon l'état de publication"""
        self.ensure_one()
        if self.publication_state == 'published' and self.company_id.journal_publication_id:
            return self.company_id.journal_publication_id
        return super()._get_payment_journal() if hasattr(super(), '_get_payment_journal') else False
