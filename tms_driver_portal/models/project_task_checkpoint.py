# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTaskCheckpoint(models.Model):
    _inherit = "project.task.checkpoint"

    def register_departure_time(self):
        self.ensure_one()
        if (
            self.env.context.get("check_equipment_required")
            and self.place_id == self.task_id.release_id
            and not self.task_id.equipment_id
        ):
            return self.task_id.action_project_task_equipment_wiz()
        return super().register_departure_time()
