# -*- encoding: utf-8 -*-

from . import models
from . import controllers

def _preserve_tag_on_taxes(cr):
    from odoo.addons.account.models.chart_template import preserve_existing_tags_on_taxes
    preserve_existing_tags_on_taxes(cr, 'l10n_dz_elosys')


