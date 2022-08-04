# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase


class TestPurchaseFixedQuantity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test vendor"})
        cls.client = cls.env["res.partner"].create({"name": "Test client"})
        service_form = Form(cls.env["product.product"])
        service_form.name = "Test Service"
        service_form.detailed_type = "service"
        service_form.fixed_purchase_qty = 90
        service_form.service_to_purchase = True
        with service_form.seller_ids.new() as seller:
            seller.name = cls.vendor
            seller.price = 20
        cls.service = service_form.save()

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
