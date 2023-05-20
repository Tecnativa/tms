# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_sellers(self, params):
        so_line = self.env.context.get("force_vendor_sale_line")
        if not so_line:
            return super()._prepare_sellers(params)
        return self.env["product.supplierinfo"].new(
            {
                "name": so_line.vendor_id.id,
                "price": so_line.purchase_price,
                "product_tmpl_id": so_line.product_id.product_tmpl_id.id,
                "product_id": so_line.product_id.id,
                "product_uom": so_line.product_uom.id,
            }
        )
