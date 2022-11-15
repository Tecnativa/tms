# Copyright 2022 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def map_task2vehicle_fields(self):
        res = super().map_task2vehicle_fields()
        res["division_id"] = "division_id"
        return res
