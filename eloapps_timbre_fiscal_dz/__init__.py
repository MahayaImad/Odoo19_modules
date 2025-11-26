from . import models

import odoo
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    company = env.company
    
    if not company.sale_timbre  :
        
        account_id = env['account.account'].search([('code','=','445750')],limit=1).id
        
        account_purchase_id = env['account.account'].search([('code','=','645700')],limit=1).id

    company.write({
    		'tranche': 100.0,
			'prix': 1.0,
			'mnt_min': 500.0,
			'mnt_max': 1000000.0,
			'sale_timbre': account_id,
			'montant_en_lettre':True,
    		})

    
