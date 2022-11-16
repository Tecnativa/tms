# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def action_start_task(self):
        self.ensure_one()
        stage = self.project_id.type_ids.filtered(lambda t: not t.is_closed)[1:2]
        self.stage_id = stage

    def action_finish_task(self):
        self.ensure_one()
        stage = self.project_id.type_ids.filtered("is_closed")[:1]
        self.stage_id = stage
