# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    """
    Extension of native l10n_dz chart template to add additional accounts.

    This module extends the native 'dz' template with additional accounts
    and features for professional Algerian accounting (CPSS compliant).
    """
    _inherit = 'account.chart.template'

    # Load additional accounts as part of the 'dz' template
    # The CSV files will be loaded automatically via data in __manifest__.py
