# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    vendor_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_line_id.vendor_id",
        string="Vendor",
        copy=False,
        context={
            "default_supplier_rank": 1,
            "default_customer_rank": 0,
        },
        readonly=False,
        store=True,
    )
