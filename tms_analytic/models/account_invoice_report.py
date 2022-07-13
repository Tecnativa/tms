# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    tractor_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Tractor",
    )
    trailer_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Trailer",
    )
    driver_id = fields.Many2one(
        comodel_name="res.partner",
        string="Driver",
    )
    division_id = fields.Many2one(
        comodel_name="tms.division",
        string="Division",
    )

    def _get_dimension_fields(self):
        res = super()._get_dimension_fields()
        res.extend(list(self.env["tms.analytic"].analytic_fields()))
        return res
