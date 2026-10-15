# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    tractor_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Tractor",
        readonly=True,
    )
    trailer_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Trailer",
        readonly=True,
    )
    driver_id = fields.Many2one(
        comodel_name="res.partner",
        string="Driver",
        readonly=True,
    )
    division_id = fields.Many2one(
        comodel_name="tms.division",
        string="Division",
        readonly=True,
    )

    def _select(self):
        return SQL(
            "%s, %s",
            super()._select(),
            SQL(", ").join(
                SQL("line.%s", SQL.identifier(field))
                for field in self.env["tms.analytic"].analytic_fields()
            ),
        )
