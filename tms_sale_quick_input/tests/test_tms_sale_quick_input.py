# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestTmsSaleQuickInput(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.shipping_origin = cls.env["res.partner"].create(
            {"name": "Test shipping origin"}
        )
        cls.shipping_destination = cls.env["res.partner"].create(
            {"name": "Test shipping destination"}
        )
        cls.package_1 = cls.env["tms.package"].create(
            {
                "name": "Test package",
                "partner_id": cls.partner.id,
                "pickup_date": "2021-10-21 12:00:00",
                "shipping_origin_id": cls.shipping_origin.id,
                "shipping_destination_id": cls.shipping_destination.id,
                "shipping_volume": 10,
                "shipping_lineal_length": 30,
                "shipping_weight": 20,
                "number_of_packages": 2,
                "pallet_qty": 1,
                "euro_pallet_qty": 1,
                "carrier_tracking_ref": "Reference",
            }
        )

    def test_01_computes_work(self):
        sale_order_line_form = Form(
            self.env["sale.order.line"],
            view="tms_sale_quick_input.view_sales_order_line_input_tree",
        )
        sale_order_line_form.order_partner_id = self.partner
        sale_order_line_form.product_id = self.product
        sale_order_line_form.tms_package_ids.add(self.package_1)
        sale_order_line_form.shipping_origin_id = self.shipping_origin
        sale_order_line = sale_order_line_form.save()
        self.assertEqual(sale_order_line.shipping_place_id, self.shipping_origin)
        self.assertEqual(sale_order_line.shipping_volume, 10)
        self.assertEqual(sale_order_line.shipping_lineal_length, 30)
        self.assertEqual(sale_order_line.shipping_weight, 20)
        self.assertEqual(sale_order_line.number_of_packages, 2)
        self.assertEqual(sale_order_line.pallet_qty, 1)
        self.assertEqual(sale_order_line.euro_pallet_qty, 1)
        self.assertEqual(sale_order_line.carrier_tracking_ref, "Reference")

    def _test_02_inverse_work(self):
        package_2 = self.env["tms.package"].create({"name": "Package 2"})
        sale_order_line_form = Form(
            self.env["sale.order.line"],
            view="tms_sale_quick_input.view_sales_order_line_input_tree",
        )
        sale_order_line_form.order_partner_id = self.partner
        sale_order_line_form.product_id = self.product
        sale_order_line_form.tms_package_ids.add(package_2)
        sale_order_line_form.shipping_place_id = self.shipping_origin
        sale_order_line_form.shipping_volume = 90
        sale_order_line_form.shipping_lineal_length = 100
        sale_order_line_form.shipping_weight = 150
        sale_order_line_form.number_of_packages = 30
        sale_order_line_form.pallet_qty = 2
        sale_order_line_form.euro_pallet_qty = 0
        sale_order_line_form.carrier_tracking_ref = "Reference 2"
        sale_order_line_form.acceptance_id = self.shipping_destination
        sale_order_line = sale_order_line_form.save()
        self.assertEqual(sale_order_line.shipping_origin_id, self.shipping_origin)
        self.assertEqual(
            sale_order_line.shipping_destination_id, self.shipping_destination
        )
        self.assertEqual(package_2.shipping_volume, 90)
        self.assertEqual(package_2.shipping_lineal_length, 100)
        self.assertEqual(package_2.shipping_weight, 150)
        self.assertEqual(package_2.number_of_packages, 30)
        self.assertEqual(package_2.pallet_qty, 2)
        self.assertEqual(package_2.euro_pallet_qty, 0)
        self.assertEqual(package_2.carrier_tracking_ref, "Reference 2")

    def test_03_inverse_multi_package_fail(self):
        package_2 = self.env["tms.package"].create({"name": "Package 2"})
        sale_order_line_form = Form(
            self.env["sale.order.line"],
            view="tms_sale_quick_input.view_sales_order_line_input_tree",
        )
        sale_order_line_form.order_partner_id = self.partner
        sale_order_line_form.product_id = self.product
        sale_order_line_form.tms_package_ids.add(self.package_1)
        sale_order_line_form.tms_package_ids.add(package_2)
        sale_order_line_form.shipping_origin_id = self.shipping_origin
        sale_order_line = sale_order_line_form.save()
        with self.assertRaises(UserError):
            sale_order_line.shipping_volume = 9

    def test_04_update_package(self):
        sale_order_line_form = Form(
            self.env["sale.order.line"].with_context(tms_quick_input=True),
            view="tms_sale_quick_input.view_sales_order_line_input_tree",
        )
        sale_order_line_form.order_partner_id = self.partner
        sale_order_line_form.product_id = self.product
        sale_order_line_form.shipping_origin_id = self.shipping_origin
        sale_order_line_form.carrier_tracking_ref = "Ref"
        sale_order_line = sale_order_line_form.save()
        sale_order_line._update_package()
        self.assertEqual(len(sale_order_line.tms_package_ids), 1)
        self.assertEqual(
            sale_order_line.tms_package_ids.shipping_origin_id,
            sale_order_line.shipping_origin_id,
        )
