# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    @api.depends("project_ids")
    def _compute_user_id(self):
        """Every sale order has its own project linked to the shared stages,
        so core reading project_ids loads every project of the stage each
        time an order is confirmed. Ask the database for the stages with any
        project instead."""
        new_stages = self.filtered(lambda stage: not stage.id)
        new_stages.sudo().filtered("project_ids").user_id = False
        stages = self - new_stages
        if stages:
            self.sudo().search(
                [("id", "in", stages.ids), ("project_ids", "!=", False)]
            ).user_id = False
