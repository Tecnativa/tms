# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase


class TestPurchaseFixedQuantity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test vendor"})
        cls.client = cls.env["res.partner"].create({"name": "Test client"})
        cls.service = cls.env["product.product"].create(
            {
                "name": "Test service",
                "type": "service",
                "fixed_purchase_qty": 90,
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor.id,
                "product_tmpl_id": cls.service.product_tmpl_id.id,
                "min_qty": 1,
            }
        )
        cls.service.service_to_purchase = True

    def test_01_purchase_service_from_sale(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.client
        with sale_order_form.order_line.new() as line:
            line.product_id = self.service
            line.product_uom_qty = 20
        sale_order = sale_order_form.save()
        sale_order.action_confirm()
        purchase_line = sale_order.order_line.purchase_line_ids
        self.assertEqual(purchase_line.product_qty, 90)
