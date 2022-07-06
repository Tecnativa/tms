# Copyright 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, values, po, partner
    ):
        vals = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner
        )
        sale_line_id = self.env["sale.order.line"].browse(values.get("sale_line_id"))
        if sale_line_id:
            vals.update(self.env["tms.analytic"].analytic_fields_vals(sale_line_id))
        return vals
