# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
    )

    @api.constrains("analytic_tag_ids")
    def _check_analytic_dimension(self):
        for vehicle in self:
            vehicle.analytic_tag_ids._check_analytic_dimension()
