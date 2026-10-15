# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_lines(self):
        """The analytic line of a distribution key with the analytic account of
        a vehicle gets that vehicle as tractor or trailer, as a cost shared
        between several vehicles (fuel, leasing...) is not on a single one."""
        vals_list = super()._prepare_analytic_lines()
        if not vals_list:
            return vals_list
        # Posting is allowed to users without access to analytic plans
        plan_columns = {
            plan._column_name()
            for plan in self.env["account.analytic.plan"]
            .sudo()
            .search([("parent_id", "=", False)])
        }
        account_ids = {
            vals[column]
            for vals in vals_list
            for column in plan_columns
            if vals.get(column)
        }
        if not account_ids:
            return vals_list
        vehicles = (
            self.env["fleet.vehicle"]
            .with_context(active_test=False)
            .search([("analytic_account_id", "in", list(account_ids))])
        )
        vehicle_by_account = {
            vehicle.analytic_account_id.id: vehicle for vehicle in vehicles
        }
        for vals in vals_list:
            for column in plan_columns:
                vehicle = vehicle_by_account.get(vals.get(column))
                if not vehicle:
                    continue
                if vehicle.vehicle_type == "trailer":
                    vals["trailer_id"] = vehicle.id
                else:
                    vals["tractor_id"] = vehicle.id
        return vals_list
