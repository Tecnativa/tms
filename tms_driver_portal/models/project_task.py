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

    @property
    def SELF_READABLE_FIELDS(self):
        fields = super().SELF_READABLE_FIELDS
        fields |= {
            "tractor_id",
            "trailer_id",
            "progress_status",
            "shipping_origin_id",
            "equipment_size_type_id",
            "shipping_destination_id",
            "unload_service",
            "trailer_requirement_ids",
            "is_private",
            "date_start",
            "pending_duration_estimated",
            "shipping_company_id",
            "distance_estimated",
            "odometer_start",
            "distance_traveled",
            "checkpoint_ids",
            "free_stoped_time",
            "odometer_stop",
            "stopped_time",
        }
        return fields

    @property
    def SELF_WRITABLE_FIELDS(self):
        fields = super().SELF_WRITABLE_FIELDS
        fields |= {
            "equipment_id",
            "seal",
        }
        return fields

    def action_project_task_equipment_wiz(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "tms_driver_portal.action_project_task_equipment_wiz"
        )
        action["context"] = {
            "default_task_id": self.id,
            "default_equipment_id": self.equipment_id.id,
            "default_equipment_size_type_id": self.equipment_size_type_id.id,
        }
        return action
