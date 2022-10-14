# Copyright 2017-2022 Tecnativa - Sergio Teruel
# Copyright 2017-2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models
from odoo.osv import expression


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    trailer_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        domain="[('vehicle_type', '=', 'trailer')]",
        string="Trailer",
    )
    task_count = fields.Integer(compute="_compute_task_count", string="Tasks")
    is_available = fields.Boolean(
        compute="_compute_task_count",
        string="Available",
    )
    next_checkpoint_ids = fields.One2many(
        comodel_name="project.task.checkpoint",
        compute="_compute_next_checkpoint_ids",
        string="Next Checkpoints",
    )
    company_owner_id = fields.Many2one(
        comodel_name="res.company",
        string="Company Owner",
    )
    is_own_vehicle = fields.Boolean(
        string="Own vehicle",
        compute="_compute_is_own_vehicle",
        search="_search_is_own_vehicle",
    )
    always_show_in_kanban = fields.Boolean(
        company_dependent=True,
    )

    def _compute_task_count(self):
        Task = self.env["project.task"]
        max_tasks = max(self.env.context.get("max_vehicle_tasks", [0]))
        # Keep only date fields to search vehicle tasks
        # TODO: Use expression when fix https://github.com/odoo/odoo/issues/103214
        TRUE_DOMAIN = ("id", "!=", False)  # expression.TRUE_DOMAIN
        task_domain = [
            TRUE_DOMAIN if (isinstance(t, (list, tuple)) and "date" not in t[0]) else t
            for t in self.env.context.get("task_domain", [])
        ]
        tasks_data = Task.read_group(
            domain=expression.AND([[("stage_id.is_closed", "=", False)], task_domain]),
            fields=["tractor_id", "trailer_id"],
            groupby=["tractor_id", "trailer_id"],
            lazy=False,
        )
        vehicle_task_dic = defaultdict(int)
        for group in tasks_data:
            if group["tractor_id"]:
                vehicle_task_dic[group["tractor_id"][0]] += group["__count"]
            if group["trailer_id"]:
                vehicle_task_dic[group["trailer_id"][0]] += group["__count"]
        for vehicle in self:
            vehicle.task_count = vehicle_task_dic[vehicle.id]
            vehicle.is_available = vehicle.task_count <= max_tasks

    def _compute_next_checkpoint_ids(self):
        """
        Search checkpoints in task in progress
        :return: dict with vehicle_id as key and checpoints as value
        """
        ProjectTaskCheckpoint = self.env["project.task.checkpoint"]
        tasks = self.env["project.task"].search(
            [
                ("stage_id.sequence", ">", 1),
                ("stage_id.is_closed", "=", False),
                ("tractor_id", "in", self.ids),
            ]
        )
        # TODO: Review
        vehicles_dic = {vehicle: ProjectTaskCheckpoint for vehicle in self}
        for task in tasks:
            vehicles_dic[task.tractor_id] |= task.checkpoint_ids
        for vehicle, checkpoints in vehicles_dic.items():
            vehicle.next_checkpoint_ids = checkpoints

    @api.depends("company_owner_id")
    def _compute_is_own_vehicle(self):
        for vehicle in self:
            vehicle.is_own_vehicle = vehicle.company_owner_id == self.env.company

    def _search_is_own_vehicle(self, operator, value):
        if operator == "=" and value or operator == "!=" and not value:
            return [("company_owner_id", "=", self.env.company.id)]
        else:
            return [
                "|",
                ("company_owner_id", "=", False),
                ("company_owner_id", "!=", self.env.company.id),
            ]

    def act_show_task(self):
        """This opens task view
        @return: the task view
        """
        self.ensure_one()
        action = self.env.ref("project.action_view_task").read()[0]
        task_field = "%s_id" % (self.vehicle_type or "tractor")
        action.update(
            context=dict(
                self.env.context,
                default_vehicle_id=self.id,
                search_default_pending=True,
            ),
            domain=[(task_field, "=", self.id)],
        )
        return action
