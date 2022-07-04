# Copyright 2018 Carlos Dauden - <carlos.dauden@tecnativa.com>
# Copyright 2018 Sergio Teruel - <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_distribution_line(self, distribution):
        res = super()._prepare_analytic_distribution_line(distribution)
        res.update(self.env["tms.analytic"].analytic_fields_vals(distribution))
        return res
