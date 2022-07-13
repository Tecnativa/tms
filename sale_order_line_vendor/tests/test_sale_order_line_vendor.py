# Copyright 2019 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import Form, common


class TestSaleOrderLineVendor(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Test Vendor",
                "supplier_rank": 1,
            }
        )
        cls.supplier2 = cls.env["res.partner"].create(
            {
                "name": "Test Vendor 2",
                "supplier_rank": 1,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "service_to_purchase": True,
                "seller_ids": [
                    (
                        0,
                        False,
                        {
                            "name": cls.supplier.id,
                            "price": 80.0,
                        },
                    )
                ],
            }
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "customer_rank": 1,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": cls.product.id,
                            "name": "Order Line Test",
                            "product_uom_qty": 1.0,
                            "vendor_id": cls.supplier.id,
                            "vendor_price_unit": 150.0,
                        },
                    )
                ],
            }
        )

    def _generate_procurement(self):
        self.assertEqual(len(self.sale_order.order_line), 1)
        sale_line = self.sale_order.order_line[0]
        self.sale_order.action_confirm()
        self.assertEqual(len(sale_line.purchase_line_ids), 1)
        purchase_line = sale_line.purchase_line_ids[0]
        return (sale_line, purchase_line)

    def test_change_vendor(self):
        sale_line, purchase_line = self._generate_procurement()
        self.assertEqual(purchase_line.order_id.partner_id, self.supplier)
        sale_line.write({"vendor_id": self.supplier2.id})
        self.assertFalse(purchase_line.exists())
        purchase_line = sale_line.purchase_line_ids[0]
        self.assertEqual(purchase_line.order_id.partner_id, self.supplier2)

    def test_change_sale_order_line_price(self):
        sale_line, purchase_line = self._generate_procurement()
        self.assertEqual(purchase_line.price_unit, 150.0)
        sale_line.write({"vendor_price_unit": 666.0})
        self.assertEqual(purchase_line.price_unit, 666.0)

    def test_change_purchase_order_line_price(self):
        sale_line, purchase_line = self._generate_procurement()
        self.assertEqual(sale_line.vendor_price_unit, 150.0)
        purchase_line.write({"price_unit": 666.0})
        self.assertEqual(sale_line.vendor_price_unit, 666.0)

    def test_set_vendor_and_vendor_price_unit(self):
        sale_line = self.sale_order.order_line[0]
        self.assertEqual(sale_line.vendor_price_unit, 150.0)
        self.sale_order.action_confirm()
        purchase_line = sale_line.purchase_line_ids[0]
        self.assertEqual(sale_line.vendor_price_unit, 150.0)
        self.assertEqual(purchase_line.price_unit, 150.0)
        self.assertEqual(purchase_line.order_id.partner_id, self.supplier)

        sale_line.vendor_id = self.supplier2
        self.assertFalse(purchase_line.exists())
        purchase_line = sale_line.purchase_line_ids[0]
        self.assertEqual(sale_line.vendor_price_unit, 0.0)
        self.assertEqual(purchase_line.price_unit, 0.0)
        self.assertEqual(purchase_line.order_id.partner_id, self.supplier2)

        sale_line.vendor_id = self.supplier
        self.assertFalse(purchase_line.exists())
        purchase_line = sale_line.purchase_line_ids[0]
        self.assertEqual(sale_line.vendor_price_unit, 80.0)
        self.assertEqual(purchase_line.price_unit, 80.0)
        self.assertEqual(purchase_line.order_id.partner_id, self.supplier)

        purchase_line.price_unit = 92.0
        self.assertEqual(sale_line.vendor_price_unit, 92.0)

        sale_line.vendor_price_unit = 77.0
        self.assertEqual(purchase_line.price_unit, 77.0)

    def test_set_vendor_and_vendor_price_unit_unconfirmed(self):
        with Form(self.sale_order) as sale_order_form:
            with sale_order_form.order_line.edit(0) as sale_line:
                sale_line.vendor_id = self.supplier2
                self.assertEqual(sale_line.vendor_price_unit, 0.0)
                sale_line.vendor_id = self.supplier
                self.assertEqual(sale_line.vendor_price_unit, 80.0)
                sale_line.vendor_id = self.supplier2
                sale_line.vendor_price_unit = 77.0
                self.assertEqual(sale_line.vendor_price_unit, 77.0)
        self.sale_order.action_confirm()
        self.assertEqual(
            self.sale_order.order_line[:1].purchase_line_ids.price_unit, 77.0
        )
