# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticPlan(models.Model):
    _inherit = "account.analytic.plan"

    @api.model
    def _get_vehicles_plan(self):
        """Plan whose accounts represent the vehicles, set as
        ``tms_analytic.vehicles_plan`` in the system parameters."""
        plan_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("tms_analytic.vehicles_plan", 0)
        )
        return self.sudo().browse(int(plan_id)).exists()
