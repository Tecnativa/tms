# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_lines(self):
        """The analytic line of a distribution key with the account of a vehicle
        (see ``fleet.vehicle._get_vehicle_by_analytic_account``) gets that
        vehicle as tractor or trailer, as a cost shared between several vehicles
        (fuel, leasing...) is not on a single one."""
        vals_list = super()._prepare_analytic_lines()
        if not vals_list:
            return vals_list
        plan = self.env["account.analytic.plan"]._get_vehicles_plan()
        if not plan:
            return vals_list
        column = plan._column_name()
        vehicle_by_account = self.env["fleet.vehicle"]._get_vehicle_by_analytic_account(
            {vals[column] for vals in vals_list if vals.get(column)}
        )
        for vals in vals_list:
            vehicle = vehicle_by_account.get(vals.get(column))
            if not vehicle:
                continue
            if vehicle.vehicle_type == "trailer":
                vals["trailer_id"] = vehicle.id
            else:
                vals["tractor_id"] = vehicle.id
        return vals_list
