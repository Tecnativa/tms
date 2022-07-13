# Copyright 2018 Carlos Dauden - <carlos.dauden@tecnativa.com>
# Copyright 2018 Sergio Teruel - <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountAnalyticDistribution(models.Model):
    _inherit = ["account.analytic.distribution", "tms.analytic"]
    _name = "account.analytic.distribution"
