# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

class ResPartner(models.Model):
    _inherit = 'res.partner'

    compte_tiers = fields.Char(
        string="Compte tiers",
    )

    @api.constrains('compte_tiers')
    def _check_compte_tiers_unique(self):
        """Vérifie que le compte tiers est unique"""
        for record in self:
            if record.compte_tiers:
                existing = self.search([
                    ('compte_tiers', '=', record.compte_tiers),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError(_('Le compte tiers "%s" existe déjà.') % record.compte_tiers)


    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        for partner in res:
            seq = ""
            if not partner.compte_tiers:
                if partner.customer and partner.supplier:
                    seq = self.env['ir.sequence'].next_by_code('res.partner.customer') or ""
                elif partner.customer:
                    seq = self.env['ir.sequence'].next_by_code('res.partner.customer') or ""
                elif partner.supplier:
                    seq = self.env['ir.sequence'].next_by_code('res.partner.supplier') or ""

                if seq:
                    partner.update({'compte_tiers': seq})

        return res

    def write(self, vals):
        res =  super(ResPartner, self).write(vals)
        for partner in self:
            seq = ""
            if not partner.compte_tiers:
                if partner.customer and partner.supplier:
                    seq = self.env['ir.sequence'].next_by_code('res.partner.customer') or ""
                elif partner.customer:
                    seq = self.env['ir.sequence'].next_by_code('res.partner.customer') or ""
                elif partner.supplier:
                    seq = self.env['ir.sequence'].next_by_code('res.partner.supplier') or ""

                if seq:
                    partner.update({'compte_tiers': seq})
        return res



    @api.depends('is_company', 'name', 'compte_tiers', 'parent_id.name', 'type', 'company_name')
    def _compute_display_name(self):
        super(ResPartner, self)._compute_display_name()
        for partner in self:
            if partner.compte_tiers:
                partner.display_name = '[' + partner.compte_tiers + '] ' + partner.display_name
