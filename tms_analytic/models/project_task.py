# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticDimension(models.Model):
    _inherit = "account.analytic.dimension"

    @api.model
    def get_model_names(self):
        res = super().get_model_names()
        res.append("project.task")
        return res


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["analytic.dimension.line", "project.task"]
    _analytic_tag_field_name = "analytic_tag_ids"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        related="sale_line_id.analytic_tag_ids",
        string="Analytic Tags",
        readonly=False,
    )

    @api.onchange("tractor_id", "trailer_id")
    def _onchange_analytic_fields(self):
        for task in self:
            task.analytic_tag_ids = (
                task.tractor_id.analytic_tag_ids | task.trailer_id.analytic_tag_ids
            )
