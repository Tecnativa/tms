# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class TestSaleLineReassign(TransactionCase):
    def test_reassign(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Partner Test",
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Product Test",
            }
        )
        sale_from = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "price_unit": 150.00,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                        },
                    )
                ],
            }
        )
        sale_to = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
            }
        )
        pl_reassign = (
            self.env["sale.order.line.reassign.wiz"]
            .with_context(active_ids=sale_from.order_line.ids)
            .create(
                {
                    "sale_order_id": sale_to.id,
                }
            )
        )
        pl_reassign.action_apply()
        self.assertFalse(len(sale_from.order_line))
        self.assertTrue(len(sale_to.order_line))
