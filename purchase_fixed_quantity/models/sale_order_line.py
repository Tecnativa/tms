# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        """ Force fixed_purchase_qty if it's set in th product """
        return super()._purchase_service_prepare_line_values(
            purchase_order, quantity=self.product_id.fixed_purchase_qty or quantity
        )
