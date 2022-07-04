# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TmsPackage(models.Model):
    _name = "tms.package"
    _order = "id DESC"
    _description = "TMS Package"

    name = fields.Char(required=True, default="/")
    partner_id = fields.Many2one(
        comodel_name="res.partner", index=True, string="Partner",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        string="Company",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("ready", "Ready"),
            ("progress", "In Progress"),
            ("loading", "Loading"),
            ("transit", "In Transit"),
            ("unloading", "Unloading"),
            ("done", "Finished"),
            ("cancel", "Cancelled"),
        ],
        compute="_compute_state",
        store=True,
        index=True,
    )
    pickup_date = fields.Datetime(string="Pick Up Date",)
    forecast_unload_date = fields.Datetime(string="Forecast Unload Date",)
    shipping_origin_id = fields.Many2one(
        comodel_name="res.partner",
        string="Origin",
        domain=[("is_shipping_place", "=", True)],
        context={"default_is_shipping_place": True,},
    )
    shipping_destination_id = fields.Many2one(
        comodel_name="res.partner",
        string="Destination",
        domain=[("is_shipping_place", "=", True)],
        context={"default_is_shipping_place": True,},
    )
    length = fields.Float(digits="TMS Volume")  # pylint: disable=W8105
    height = fields.Float(digits="TMS Volume")
    wide = fields.Float(digits="TMS Volume")
    shipping_volume = fields.Float(digits="TMS Volume", string="Volume",)
    shipping_weight = fields.Float(digits="TMS Weight", string="Weight",)
    number_of_packages = fields.Integer(string="Lumps")
    pallet_qty = fields.Integer(string="Pallets")
    euro_pallet_qty = fields.Integer(string="Euro Pallets")
    goods_id = fields.Many2one(
        comodel_name="tms.goods", string="Goods", ondelete="restrict",
    )
    carrier_tracking_ref = fields.Char(string="Tracking Reference",)
    note = fields.Text(string="Comments")
    unload_note = fields.Text(string="Unload Comments")
    requested_date = fields.Datetime(
        default=fields.Datetime.now, string="Requested Date",
    )
    customer_ref = fields.Char()
    checkpoint_origin_ids = fields.Many2many(
        comodel_name="project.task.checkpoint",
        relation="project_task_checkpoint_tms_package_origin_rel",
        column1="package_id",
        column2="checkpoint_id",
        string="Checkpoints Origin",
    )
    checkpoint_destination_ids = fields.Many2many(
        comodel_name="project.task.checkpoint",
        relation="project_task_checkpoint_tms_package_destination_rel",
        column1="package_id",
        column2="checkpoint_id",
        string="Checkpoints Destination",
    )
    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="project_task_tms_package_rel",
        column1="tms_package_id",
        column2="project_task_id",
        string="Tasks",
    )
    sale_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        relation="sale_order_line_tms_package_rel",
        column1="tms_package_id",
        column2="sale_order_line_id",
        string="Sale Lines",
    )
    sequence = fields.Integer(string="Sequence", default=100)

    _sql_constraints = [
        ("name_unique", "unique(name)", "Name for this package already exists!"),
    ]

    @api.depends(
        "checkpoint_destination_ids",
        "checkpoint_destination_ids.departure_time",
        "checkpoint_destination_ids.arrival_time",
        "checkpoint_origin_ids",
        "checkpoint_origin_ids.departure_time",
        "checkpoint_origin_ids.arrival_time",
        "task_ids.timesheet_ids",
        "task_ids.stage_id.fold",
    )
    def _compute_state(self):
        for package in self:
            if not package.task_ids:
                package.state = "draft"
            elif any(package.checkpoint_destination_ids.mapped("departure_time")):
                package.state = "done"
            elif any(package.checkpoint_destination_ids.mapped("arrival_time")):
                package.state = "unloading"
            elif any(package.checkpoint_origin_ids.mapped("departure_time")):
                package.state = "transit"
            elif any(package.checkpoint_origin_ids.mapped("arrival_time")):
                package.state = "loading"
            elif any(package.task_ids.mapped("timesheet_ids")):
                package.state = "progress"
            elif package.checkpoint_origin_ids and package.checkpoint_destination_ids:
                package.state = "ready"
            # TODO: Find better cancel state check
            elif all(package.task_ids.mapped("stage_id.fold")):
                package.state = "cancel"
            else:
                package.state = "pending"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" in vals and vals["name"] == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("tms.package") or "/"
                )
        return super().create(vals_list)
