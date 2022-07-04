# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "tms.analytic"]
    _name = "account.move.line"

    def _prepare_analytic_line(self):
        TmsAnalytic = self.env["tms.analytic"]
        vals_list = super()._prepare_analytic_line()
        for index, move_line in enumerate(self):
            vals = vals_list[index]
            vals.update(TmsAnalytic.analytic_fields_vals(move_line))
        return vals_list
