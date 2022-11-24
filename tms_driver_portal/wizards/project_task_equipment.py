# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTaskEquipmentWiz(models.TransientModel):
    _name = "project.task.equipment.wiz"
    _description = "Fill project task equipment wizard"

    task_id = fields.Many2one(comodel_name="project.task")
    equipment_id = fields.Many2one(comodel_name="tms.equipment")
    equipment_size_type_id = fields.Many2one(comodel_name="iso6346.size.type")
    equipment = fields.Char()
    seal = fields.Char(related="task_id.seal", readonly=False)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if (
            self.env.context.get("active_id")
            and self.env.context.get("active_model") == "project.task"
        ):
            task = self.env["project.task"].browse(self.env.context.get("active_id"))
            if task.exists() and task.equipment_id:
                res.update({"equipment": task.equipment_id.name})
        return res

    def action_apply(self):
        if self.equipment:
            Equipment = self.env["tms.equipment"]
            equipment_id = Equipment.search([("name", "=", self.equipment)])
            if not equipment_id:
                equipment_id = Equipment.sudo().create(
                    {
                        "size_type_id": self.equipment_size_type_id.id,
                        "name": self.equipment,
                    }
                )
            if equipment_id:
                self.task_id.equipment_id = equipment_id
        else:
            self.task_id.equipment_id = False
