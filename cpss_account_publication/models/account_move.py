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
        help="Numéro de publication séparé (FC/AC/FF/AF) attribué lors de la publication"
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

    def _get_publication_sequence_code(self, move_type):
        """
        Retourne le code de séquence pour la publication selon le type de facture

        Séquences de publication:
        - Facture client: FC/year (Facture Client)
        - Avoir client: AC/year (Avoir Client)
        - Facture fournisseur: FF/year (Facture Fournisseur)
        - Avoir fournisseur: AF/year (Avoir Fournisseur)
        """
        sequence_mapping = {
            'out_invoice': 'account.move.out_invoice.published',   # FC
            'out_refund': 'account.move.out_refund.published',     # AC
            'in_invoice': 'account.move.in_invoice.published',     # FF
            'in_refund': 'account.move.in_refund.published',       # AF
        }
        return sequence_mapping.get(move_type)

    def _get_standard_sequence_code(self, move_type):
        """
        Retourne le code de séquence standard (non publié) selon le type de facture

        Séquences standards (toujours utilisées pour name):
        - Facture client: BLC/year (Bon de Livraison Client)
        - Avoir client: AVC/year (Avoir Client)
        - Facture fournisseur: BLF/year (Bon de Livraison Fournisseur)
        - Avoir fournisseur: AVF/year (Avoir Fournisseur)
        """
        sequence_mapping = {
            'out_invoice': 'account.move.out_invoice.unpublished',  # BLC
            'out_refund': 'account.move.out_refund.unpublished',    # AVC
            'in_invoice': 'account.move.in_invoice.unpublished',    # BLF
            'in_refund': 'account.move.in_refund.unpublished',      # AVF
        }
        return sequence_mapping.get(move_type)

    def _get_sequence(self):
        """
        Surcharge pour utiliser nos séquences BL personnalisées
        Le numéro de facture (name) utilise TOUJOURS les séquences BL
        """
        self.ensure_one()

        # Pour les factures gérées par notre module, utiliser les séquences BL
        if self.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
            sequence_code = self._get_standard_sequence_code(self.move_type)

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

    def _check_stock_availability_for_publication(self):
        """
        Vérifie si le stock publié est suffisant pour permettre la publication
        Uniquement si la fonctionnalité est activée dans la configuration
        """
        self.ensure_one()

        # Vérifier si la fonctionnalité est activée
        if not self.company_id.enable_publication_stock_tracking:
            return True

        # Ne vérifier que pour les factures de vente
        if self.move_type not in ['out_invoice', 'out_refund']:
            return True

        # Parcourir les lignes de la facture
        insufficient_products = []
        for line in self.invoice_line_ids.filtered(lambda l: l.product_id.type == 'product'):
            product = line.product_id
            quantity = line.quantity

            # Calculer le stock publié disponible pour ce produit
            quants = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal'),
                ('company_id', '=', self.company_id.id)
            ])

            qty_published_available = sum(quants.mapped('qty_published'))

            # Vérifier si suffisant
            if self.move_type == 'out_invoice' and qty_published_available < quantity:
                insufficient_products.append({
                    'product': product.display_name,
                    'required': quantity,
                    'available': qty_published_available,
                    'missing': quantity - qty_published_available
                })

        if insufficient_products:
            message = _("Stock publié insuffisant pour les produits suivants:\n")
            for item in insufficient_products:
                message += _("\n• %s: Requis: %.2f, Disponible: %.2f, Manquant: %.2f") % (
                    item['product'],
                    item['required'],
                    item['available'],
                    item['missing']
                )
            raise UserError(message)

        return True

    def action_publish(self):
        """Publie la facture avec un numéro de publication séparé"""
        for move in self:
            if not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Seuls les comptables peuvent publier des factures."))

            if move.publication_state == 'published':
                raise UserError(_("Cette facture est déjà publiée."))

            if move.state != 'posted':
                raise UserError(_("Vous ne pouvez publier qu'une facture comptabilisée."))

            # Vérifier la disponibilité du stock publié si activé
            move._check_stock_availability_for_publication()

            # Générer le numéro de publication (FC/AC/FF/AF)
            sequence_code = move._get_publication_sequence_code(move.move_type)

            if sequence_code:
                publication_number = self.env['ir.sequence'].next_by_code(sequence_code)

                if not publication_number:
                    raise UserError(_(
                        "La séquence de publication '%s' n'existe pas. Veuillez vérifier la configuration du module.") % sequence_code)

                # Mettre à jour uniquement le numéro de publication
                # Le numéro de facture (name) reste inchangé (BLC/AVC/BLF/AVF)
                move.write({
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

            # Dépublier (garder publication_number et publication_date pour l'historique)
            move.write({'publication_state': 'not_published'})

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
