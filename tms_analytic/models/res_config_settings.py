# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tms_vehicles_analytic_plan_id = fields.Many2one(
        comodel_name="account.analytic.plan",
        string="Vehicles Analytic Plan",
        config_parameter="tms_analytic.vehicles_plan",
        domain=[("parent_id", "=", False)],
        help="Plan whose accounts represent the vehicles. The analytic lines of "
        "an account of this plan get the vehicle with that account in its "
        "analytic distribution as tractor or trailer.",
    )
