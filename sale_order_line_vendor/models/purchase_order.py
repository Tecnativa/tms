# Copyright 2017-2020 Tecnativa - Carlos Dauden
# Copyright 2017-2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, vals):
        if "price_unit" in vals and not self.env.context.get("write_from_sale"):
            self.mapped("sale_line_id").with_context(write_from_purchase=True).write(
                {
                    "vendor_price_unit": vals["price_unit"],
                }
            )
        return super().write(vals)
