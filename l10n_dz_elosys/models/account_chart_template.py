# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Odoo 19 Note: The account.chart.template model no longer exists in Odoo 19.
# Chart of accounts setup is now handled differently.
# This file is kept for reference but the class is commented out to avoid errors.

# TODO: Implement post_init_hook to setup account groups hierarchy
# The logic below should be moved to a post-install hook function

"""
class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'


    def _load(self, company):
        res = super(AccountChartTemplate, self)._load(company)

        account_group_obj = self.env['account.group']
        # lié chaque compte au group (chapitre) parent
        for account_id in self.env['account.account'].search([]):
            # hierarchie des chapitres
            chapitre_niveau_4_code = account_id.code[0:4]
            chapitre_niveau_3_code = account_id.code[0:3]
            chapitre_niveau_2_code = account_id.code[0:2]
            code_par_niveau = [chapitre_niveau_4_code, chapitre_niveau_3_code, chapitre_niveau_2_code]
            code_index = 0

            while code_index < len(code_par_niveau):
                group_id = account_group_obj.search([('code_prefix_start', '=', code_par_niveau[code_index])], limit=1)
                if group_id:
                    account_id.write({'group_id': group_id.id})
                    break
                code_index += 1

        for group_id in account_group_obj.search([]):
            code_prefix_start = group_id.code_prefix_start

            if not group_id.parent_id:
                if code_prefix_start == '0':
                    pass
                elif code_prefix_start in ['Classes 1 à 5', 'Classes 6 à 7']:
                    group_id.write({'parent_id': account_group_obj.search([('code_prefix_start', '=', '0')])})
                elif code_prefix_start in ['Classe 1', 'Classe 2', 'Classe 3', 'Classe 4', 'Classe 5']:
                    group_id.write({'parent_id': account_group_obj.search([('code_prefix_start', '=', 'Classes 1 à 5')])})
                elif code_prefix_start in ['Classe 6', 'Classe 7']:
                    group_id.write({'parent_id': account_group_obj.search([('code_prefix_start', '=', 'Classes 6 à 7')])})
                elif len(code_prefix_start) >= 2:
                    found = False
                    while not found:
                        tmp_cps = code_prefix_start[0:len(code_prefix_start)-1]
                        if len(tmp_cps) == 1:
                            group_id.write({'parent_id': account_group_obj.search([('code_prefix_start', '=', 'Classe {}'.format(tmp_cps))])})
                            found = True
                        else:
                            res_group = account_group_obj.search([('code_prefix_start', '=', tmp_cps)])
                            if res_group:
                                group_id.write({'parent_id': res_group.id})
                                found = True
                            else:
                                code_prefix_start = tmp_cps

        return res
"""