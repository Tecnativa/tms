# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    auto_confirm = fields.Boolean()
    booking_number = fields.Char()
    wagon = fields.Char()
    vessel = fields.Char()
    voyage_number = fields.Char()
    dua_ref = fields.Char(
        string="DUA",
    )
    release_id = fields.Many2one(
        comodel_name="res.partner",
        string="Release",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
        },
    )
    release_locator = fields.Char()
    acceptance_id = fields.Many2one(
        comodel_name="res.partner",
        string="Acceptance",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
        },
    )
    acceptance_locator = fields.Char()
    # This is the origin port
    port_id = fields.Many2one(
        comodel_name="res.partner",
        string="Origin Port",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
        },
    )
    shipment_port_id = fields.Many2one(
        comodel_name="res.partner",
        string="Shipment Port",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
        },
    )
    loading_port_id = fields.Many2one(
        comodel_name="res.partner",
        string="Loading Port",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
        },
    )
    unloading_port_id = fields.Many2one(
        comodel_name="res.partner",
        string="Unloading Port",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
        },
    )
    unload_service = fields.Boolean(string="Unload")

    def task_sync_field_list(self):
        return [
            "booking_number",
            "wagon",
            "vessel",
            "voyage_number",
            "release_id",
            "release_locator",
            "acceptance_id",
            "acceptance_locator",
            "shipment_port_id",
            "port_id",
            "loading_port_id",
            "unloading_port_id",
            "unload_service",
        ]

    def write_task_fields(self, vals):
        task_vals = {
            field: vals[field]
            for field in self.task_sync_field_list()
            if field in vals.keys()
        }
        tasks = self.mapped("tasks_ids")
        if (
            any(task_vals)
            and any(tasks)
            and "write_from_so_line" not in self.env.context
        ):
            tasks.with_context(write_from_so_line=True).write(task_vals)

    def write(self, vals):
        self.write_task_fields(vals)
        return super().write(vals)
