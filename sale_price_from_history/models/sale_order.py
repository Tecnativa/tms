# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    price_history = fields.Boolean()

    @api.onchange("price_history")
    def _onchage_base_price_history(self):
        for order in self:
            order.mapped("order_line").update(
                {"price_history": order.price_history,}
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_history = fields.Boolean(index=True)
    order_partner_id = fields.Many2one(index=True)

    def _get_history_line_domain(self):
        return [
            ("order_partner_id", "=", self.order_partner_id.id),
            ("product_id", "=", self.product_id.id),
            ("price_history", "=", True),
        ]

    def _get_display_price(self, product):
        if self.product_id.price_history:
            line_history_price = self.search(
                self._get_history_line_domain(), limit=1, order="id DESC"
            )
            if line_history_price:
                return line_history_price.price_unit
        return super()._get_display_price(product)

    def set_price(self):
        self.ensure_one()
        self.browse(
            self.env.context["to_set_price_line_id"]
        ).price_unit = self.price_unit
