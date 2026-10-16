# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):
    _name = "fleet.vehicle"
    _inherit = ["fleet.vehicle", "analytic.mixin"]

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        check_company=True,
        help="Analytic account that represents this vehicle in the analytic "
        "reports.",
    )

    def _get_vehicles_analytic_distribution(self):
        """Analytic distribution of the vehicles, the percentages of a key shared
        by several of them added up."""
        distribution = {}
        for vehicle in self:
            for key, percentage in (vehicle.analytic_distribution or {}).items():
                distribution[key] = distribution.get(key, 0.0) + percentage
        return distribution
