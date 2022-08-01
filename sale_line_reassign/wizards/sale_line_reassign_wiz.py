# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018-2021 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import _, exceptions, fields, models


class SaleOrderLineReassignWiz(models.TransientModel):
    _name = "sale.order.line.reassign.wiz"
    _description = "Wizard to reassign sale order lines to other sale order"

    def _default_partner_id(self):
        active_ids = self.env.context.get("active_ids")
        lines = self.env["sale.order.line"].browse(active_ids)
        partner = lines[:1].order_id.partner_id
        if lines.filtered(lambda l: (l.invoice_lines or l.order_partner_id != partner)):
            raise exceptions.ValidationError(
                _("Selected line/s are invoiced or they have distinct " "customers")
            )
        return partner

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Move to sale",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        default=lambda self: self._default_partner_id(),
    )

    def action_apply(self):
        active_ids = self.env.context.get("active_ids")
        lines = self.env["sale.order.line"].browse(active_ids)
        project = self.sale_order_id.project_ids[:1]
        lines.update({"order_id": self.sale_order_id.id})
        # Update project in so lines and tasks after v12 changes
        project_so_lines = lines.filtered("project_id")
        if project_so_lines:
            # Repeat update to avoid rewrite first line
            if not project:
                project = project_so_lines[:1]._timesheet_create_project()
                project_so_lines[1:].update({"project_id": project.id})
            else:
                project_so_lines.update({"project_id": project.id})
            project_so_lines.mapped("task_id").update({"project_id": project.id})
        # If sale_order_line_vendor is installed
        if "purchase_line_ids" in lines:
            lines.mapped("purchase_line_ids").update(
                {"account_analytic_id": self.sale_order_id.analytic_account_id.id}
            )
        return lines
