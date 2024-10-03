# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    def check_start_actual_task(self):
        """Driver can not start a task while a previous task not closed yet."""
        if not self.env.context.get("check_start_actual_task"):
            return
        my_actual_task = self.search(
            [
                ("user_ids", "=", self.env.user.ids),
                ("stage_id.is_closed", "=", False),
            ],
            order="priority desc, planned_date_start, sequence, id desc",
            limit=1,
        )
        if my_actual_task != self:
            raise ValidationError(
                _("You can not start this task until the previous task is closed")
            )

    def action_start_task(self):
        self.ensure_one()
        self.check_start_actual_task()
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
            "planned_date_start",
            "pending_duration_estimated",
            "shipping_company_id",
            "distance_estimated",
            "odometer_start",
            "distance_traveled",
            "checkpoint_ids",
            "free_stoped_time",
            "odometer_stop",
            "stopped_time",
            "shipping_place_id",
            "release_id",
            "acceptance_id",
            "stage_id.is_closed",
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

    def write(self, vals):
        res = super().write(vals)
        if vals.get("user_ids", False):
            for project in self.mapped("project_id"):
                partners = self.filtered(lambda t: t.project_id == project).mapped(
                    "user_ids.partner_id"
                )
                project._add_collaborators(partners)
                project.message_subscribe(partner_ids=partners.ids)
        return res
