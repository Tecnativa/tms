# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "tms.analytic.distribution"]

    def _get_vehicles_analytic_lines(self):
        """Not the tax, payment term... lines of the invoices. In the journal
        entries every line is a product one."""
        return self.filtered(lambda x: x.display_type == "product")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._tms_analytic_create()
        return lines

    def write(self, vals):
        return self._tms_analytic_write(vals, super().write)

    def _compute_analytic_distribution(self):
        return self._tms_analytic_compute(super()._compute_analytic_distribution)

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
