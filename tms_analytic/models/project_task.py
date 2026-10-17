# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    analytic_distribution = fields.Json(
        related="sale_line_id.analytic_distribution",
        readonly=False,
    )
    # Read by the analytic_distribution widget of the form, as in analytic.mixin
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env["decimal.precision"].precision_get(
            "Percentage Analytic"
        ),
    )

    @api.onchange("tractor_id", "trailer_id")
    def _onchange_vehicles_analytic_distribution(self):
        """Replace the distribution of the previous vehicles by the one of the new
        ones, as the vehicles analytic tags were set in 15.0. Only from the form, so
        the tractor assigned from the planning kanban doesn't change it."""
        for task in self.filtered("sale_line_id"):
            origin = task._origin
            task.analytic_distribution = self.env[
                "sale.order.line"
            ]._merge_vehicles_analytic_distribution(
                origin.analytic_distribution,
                (
                    task.tractor_id | task.trailer_id
                )._get_vehicles_analytic_distribution(),
                (
                    origin.tractor_id | origin.trailer_id
                )._get_vehicles_analytic_distribution(),
            )
