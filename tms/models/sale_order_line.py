# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "tms.analytic"]
    _name = "sale.order.line"

    level = fields.Integer()
    parent_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        compute="_compute_parent_line_id",
        store=True,
    )
    equipment_size_type_id = fields.Many2one(
        comodel_name="iso6346.size.type", string="Size Type", ondelete="restrict"
    )
    equipment_id = fields.Many2one(
        comodel_name="tms.equipment",
        string="Equipment",
    )
    seal = fields.Char()
    tms_package_ids = fields.Many2many(
        comodel_name="tms.package",
        relation="sale_order_line_tms_package_rel",
        column1="sale_order_line_id",
        column2="tms_package_id",
        string="Packages",
        copy=False,
    )
    pickup_date = fields.Datetime(
        string="Pick Up Date",
    )
    forecast_unload_date = fields.Datetime()
    shipping_origin_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_shipping_place", "=", True)],
        string="Shipping Origin",
        context={
            "default_is_shipping_place": True,
            "partner_show_only_name": True,
        },
    )
    shipping_destination_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_shipping_place", "=", True)],
        string="Shipping Destination",
        context={
            "default_is_shipping_place": True,
            "partner_show_only_name": True,
        },
    )
    shipping_origin_zip = fields.Char(
        string="OZIP", store=True, related="shipping_origin_id.zip"
    )
    shipping_destination_zip = fields.Char(
        string="DZIP", store=True, related="shipping_destination_id.zip"
    )

    @api.depends("order_id.order_line.sequence", "order_id.order_line.level")
    def _compute_parent_line_id(self):
        for line in self.filtered("level"):
            parent_line = line.order_id.order_line.filtered(
                lambda x: x.level < line.level and x.sequence <= line.sequence
            )
            line.parent_line_id = parent_line[-1:]

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if not self.level:
            self.level = self.product_id.level
        return res

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals.update(self.env["tms.analytic"].analytic_fields_vals(self))
        return vals

    @api.model
    def task_sync_field_list(self):
        task_fields = list(self.env["tms.analytic"].analytic_fields())
        task_fields.extend(
            [
                "shipping_origin_id",
                "shipping_destination_id",
                "tms_package_ids",
                "equipment_size_type_id",
                "equipment_id",
                "seal",
            ]
        )
        return task_fields

    def _timesheet_create_task_prepare_values(self, project):
        vals = super()._timesheet_create_task_prepare_values(project)
        # Sale Order Values
        so_task_vals = {
            field: self.order_id._fields[field].convert_to_write(
                self.order_id[field], self.order_id
            )
            for field in self.order_id.task_sync_field_list()
            if field in self.order_id
        }
        vals.update(so_task_vals)
        # Sale Order Line Values
        sol_task_vals = {
            field: self._fields[field].convert_to_write(self[field], self)
            for field in self.task_sync_field_list()
            if field in self
        }
        vals.update(sol_task_vals)
        vals.update(
            {
                # TODO: Check if (5,0,0) is needed
                "user_ids": False,
                "date_start": self.pickup_date,
                "date_deadline": fields.Date.to_string(
                    fields.Datetime.context_timestamp(
                        self, fields.Datetime.from_string(self.pickup_date)
                    )
                )
                if self.pickup_date
                else False,
                "color": self.level,
            }
        )
        # Analytic
        vals.update(self.env["tms.analytic"].analytic_fields_vals(self))
        # Extra
        if self.parent_line_id:
            vals["parent_id"] = self.parent_line_id.task_id.id
            vals["sequence"] = 50
        else:
            vals.update(
                {
                    "release_id": self.order_id.release_id.id,
                    "release_locator": self.order_id.release_locator,
                    "acceptance_id": self.order_id.acceptance_id.id,
                    "acceptance_locator": self.order_id.acceptance_locator,
                }
            )
        return vals

    def write_task_fields(self, vals):
        if "write_from_task" in self.env.context:
            return
        task_vals = {
            field: vals[field]
            for field in self.task_sync_field_list()
            if field in vals.keys()
        }
        tasks = self.mapped("task_ids")
        if any(task_vals) and any(tasks):
            tasks.with_context(write_from_so_line=True).write(task_vals)

    def write(self, vals):
        self.write_task_fields(vals)
        return super().write(vals)

    def action_tms_package_form(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "tms.action_order_line_tms_package"
        )
        form = self.env.ref("tms.view_order_line_tms_package")
        action["views"] = [(form.id, "form")]
        action["res_id"] = self.id
        return action
