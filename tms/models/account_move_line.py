# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "tms.analytic"]
    _name = "account.move.line"

    def _prepare_analytic_lines(self):
        # Super is ensure_one and returns one vals dict per analytic
        # distribution entry: apply the TMS dimensions to all of them
        vals_list = super()._prepare_analytic_lines()
        tms_vals = self.env["tms.analytic"].analytic_fields_vals(self)
        for vals in vals_list:
            vals.update(tms_vals)
        return vals_list
