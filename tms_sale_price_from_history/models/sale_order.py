# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_history_line_domain(self):
        res = super()._get_history_line_domain()
        if not self.product_id.price_history_location:
            return res
        if self.shipping_origin_id:
            res.append(("shipping_origin_id", "=", self.shipping_origin_id.id))
        if self.shipping_destination_id:
            res.append(
                ("shipping_destination_id", "=", self.shipping_destination_id.id)
            )
        return res

    @api.onchange("shipping_origin_id", "shipping_destination_id")
    def shipping_location_change(self):
        if self.product_id.price_history_location:
            self.product_uom_change()
