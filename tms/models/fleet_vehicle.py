# Copyright 2017-2022 Tecnativa - Sergio Teruel
# Copyright 2017-2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models
from odoo.osv import expression

from odoo.addons.project.models.project_task import CLOSED_STATES


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
        compute_sudo=True,
        search="_search_is_own_vehicle",
    )
    always_show_in_kanban = fields.Boolean(
        company_dependent=True,
    )
    sale_type_ids = fields.Many2many(
        comodel_name="sale.order.type",
        string="Sale Order Types",
    )
    task_pending_duration_estimated = fields.Float(compute="_compute_task_count")

    def _compute_task_count(self):
        Task = self.env["project.task"]
        max_tasks = max(self.env.context.get("max_vehicle_tasks", [0]))
        task_domain = [
            expression.TRUE_DOMAIN
            if (isinstance(t, (list | tuple)) and "date" not in t[0])
            else t
            for t in self.env.context.get("task_domain", [])
        ]
        tasks_data = Task._read_group(
            domain=expression.AND(
                [[("state", "not in", list(CLOSED_STATES.keys()))], task_domain]
            ),
            groupby=["tractor_id", "trailer_id"],
            aggregates=["__count", "pending_duration_estimated:sum"],
        )
        vehicle_task_dic = defaultdict(lambda: {"count": 0, "duration": 0.0})
        for tractor_id, trailer_id, count, pending_duration_sum in tasks_data:
            if tractor_id:
                vehicle_task_dic[tractor_id.id]["count"] += count
                vehicle_task_dic[tractor_id.id]["duration"] += pending_duration_sum
            if trailer_id:
                vehicle_task_dic[trailer_id.id]["count"] += count
                vehicle_task_dic[trailer_id.id]["duration"] += pending_duration_sum
        for vehicle in self:
            vehicle.task_count = vehicle_task_dic[vehicle.id]["count"]
            vehicle.is_available = vehicle.task_count <= max_tasks
            vehicle.task_pending_duration_estimated = vehicle_task_dic[vehicle.id][
                "duration"
            ]

    def _compute_next_checkpoint_ids(self):
        """
        Search checkpoints in task in progress
        :return: dict with vehicle_id as key and checkpoints as value
        """
        ProjectTaskCheckpoint = self.env["project.task.checkpoint"]
        tasks = self.env["project.task"].search(
            [
                ("stage_id.sequence", ">", 1),
                ("state", "not in", list(CLOSED_STATES.keys())),
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
