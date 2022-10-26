# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTaskCheckpoint(models.Model):
    _name = "project.task.checkpoint"
    _description = "Checkpoint"
    _order = "sequence, id"

    name = fields.Char(
        related="place_id.name",
        store=True,
    )
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        index=True,
    )
    sequence = fields.Integer()
    automatic = fields.Boolean()
    place_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
            "partner_show_only_name": True,
        },
        required=True,
        string="Place",
    )
    distance_estimated = fields.Float(
        digits="TMS Distance",
    )
    duration_estimated = fields.Float()
    arrival_time = fields.Datetime(string="Arrival")
    departure_time = fields.Datetime(string="Departure")
    stopped_time = fields.Float(
        compute="_compute_stopped_time",
        inverse=lambda x: x,  # Trick to allow modify field
        store=True,
    )
    package_origin_ids = fields.Many2many(
        comodel_name="tms.package",
        relation="project_task_checkpoint_tms_package_origin_rel",
        column1="checkpoint_id",
        column2="package_id",
        string="Packages Origin",
    )
    package_destination_ids = fields.Many2many(
        comodel_name="tms.package",
        relation="project_task_checkpoint_tms_package_destination_rel",
        column1="checkpoint_id",
        column2="package_id",
        string="Packages Destination",
    )

    @api.depends("arrival_time", "departure_time")
    def _compute_stopped_time(self):
        for checkpoint in self:
            if not checkpoint.arrival_time or not checkpoint.departure_time:
                continue
            checkpoint.stopped_time = (
                checkpoint.departure_time - checkpoint.arrival_time
            ).total_seconds() / 3600

    def register_arrival_time(self):
        self.ensure_one()
        self.arrival_time = fields.Datetime.now()

    def register_departure_time(self):
        self.ensure_one()
        self.departure_time = fields.Datetime.now()
