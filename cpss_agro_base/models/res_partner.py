# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # === Champs agricoles ===
    surface_exploitee = fields.Float(
        string="Surface exploitée (ha)",
        help="Surface exploitée en hectares",
        digits=(8, 2)
    )

    type_exploitation = fields.Selection([
        ('traditionnelle', 'Traditionnelle'),
        ('intensive', 'Intensive'),
    ], string="Type d'exploitation")

    nombre_arbres = fields.Integer(
        string="Nombre d'arbres",
        help="Nombre total d'arbres sur l'exploitation"
    )

    age_arbres = fields.Integer(
        string="Âge des arbres (années)",
        help="Âge moyen des arbres en années"
    )

    # === Champs calculés ===
    densite_arbres = fields.Float(
        string="Densité (arbres/ha)",
        compute='_compute_densite_arbres',
        store=True,
        digits=(8, 0),
        help="Nombre d'arbres par hectare"
    )

    @api.depends('nombre_arbres', 'surface_exploitee')
    def _compute_densite_arbres(self):
        """Calcule la densité d'arbres par hectare"""
        for partner in self:
            if partner.surface_exploitee and partner.surface_exploitee > 0:
                partner.densite_arbres = partner.nombre_arbres / partner.surface_exploitee
            else:
                partner.densite_arbres = 0

    @api.constrains('surface_exploitee')
    def _check_surface_exploitee(self):
        """Vérifie que la surface exploitée est positive"""
        for partner in self:
            if partner.surface_exploitee and partner.surface_exploitee < 0:
                raise ValidationError("La surface exploitée ne peut pas être négative.")

    @api.constrains('nombre_arbres')
    def _check_nombre_arbres(self):
        """Vérifie que le nombre d'arbres est positif"""
        for partner in self:
            if partner.nombre_arbres and partner.nombre_arbres < 0:
                raise ValidationError("Le nombre d'arbres ne peut pas être négatif.")

    @api.constrains('age_arbres')
    def _check_age_arbres(self):
        """Vérifie que l'âge des arbres est positif"""
        for partner in self:
            if partner.age_arbres and partner.age_arbres < 0:
                raise ValidationError("L'âge des arbres ne peut pas être négatif.")