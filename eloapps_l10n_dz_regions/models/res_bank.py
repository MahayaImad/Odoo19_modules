# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResBank(models.Model):
    _inherit = 'res.bank'

    commune_id = fields.Many2one(
        "res.country.state.commune",
        string='Commune',
        domain="[('state_id', '=', state)]"
    )

    localite_id = fields.Many2one(
        "res.country.state.localite",
        string='Localité',
        domain="[('state_id', '=', state)]"
    )

    # Le champ country_id existe déjà dans res.bank, on l'étend seulement
    country_id = fields.Many2one(
        'res.country',
        string='Pays'
        # Attention: 'state' n'existe pas, utilisez 'state_id' si c'est ce que vous voulez
        #related='state_id.country_id'  # Décommentez si vous avez un champ state_id
    )

    # Le champ code existe déjà dans res.bank d'Odoo 19
    # On le redéfinit pour ajouter nos contraintes
    code = fields.Char(
        string='Code Banque',
        help='Le code de la banque (obligatoire).',
        required=True,
        # Le paramètre 'size' est obsolète en Odoo 19
        # Utilisez une contrainte si vous voulez limiter la taille
    )

    @api.constrains('code')
    def _check_code_length(self):
        """Vérifie que le code fait maximum 5 caractères"""
        for record in self:
            if record.code and len(record.code) > 5:
                raise ValidationError(_('Le code de la banque ne peut pas dépasser 5 caractères.'))

    @api.constrains('code')
    def _check_code_required(self):
        """S'assure que le code est toujours renseigné"""
        for record in self:
            if not record.code:
                raise ValidationError(_('Le code de la banque est obligatoire.'))

    # Set state_id to False if another country gets selected
    @api.onchange('country_id')
    def _onchange_country_empty_state(self):
        """Vide l'état quand le pays change"""
        if self.country_id:
            # Attention: vérifiez que le champ 'state' ou 'state_id' existe
            # Si c'est state_id:
            # self.state_id = False

            # Si c'est un champ personnalisé 'state':
            self.state = False
            self.commune_id = False
            self.localite_id = False

    # Set commune_id to False if another state gets selected
    @api.onchange('state')  # ou 'state_id' selon votre modèle
    def _onchange_state_empty_commune(self):
        """Vide la commune et localité quand l'état change"""
        if self.state:  # ou self.state_id
            self.commune_id = False
            self.localite_id = False

    # Check if localite_id, country_id and state are true and fill zip with localite_id.code
    @api.onchange('localite_id', 'country_id', 'state')  # ou 'state_id'
    def _onchange_localite_get_zip(self):
        """Met à jour le code postal basé sur la localité"""
        if self.country_id and self.state and self.localite_id:  # ou self.state_id
            if hasattr(self.localite_id, 'code') and self.localite_id.code:
                self.zip = self.localite_id.code
        else:
            self.zip = False

    @api.model
    def create(self, vals):
        """S'assure qu'un code est généré si manquant"""
        if not vals.get('code'):
            # Génère un code automatique si manquant
            vals['code'] = self._generate_bank_code(vals.get('name', ''))
        return super(ResBank, self).create(vals)

    def _generate_bank_code(self, bank_name):
        """Génère automatiquement un code de banque"""
        if not bank_name:
            bank_name = 'BANK'

        # Génère un code basé sur le nom
        code = ''.join(c for c in bank_name.upper() if c.isalnum())[:5]

        # S'assurer de l'unicité
        counter = 1
        original_code = code
        while self.search([('code', '=', code)]):
            code = f"{original_code[:3]}{counter:02d}"
            counter += 1
            if counter > 99:  # Évite les boucles infinies
                code = f"BK{self.env['ir.sequence'].next_by_code('res.bank') or '001'}"[:5]
                break

        return code