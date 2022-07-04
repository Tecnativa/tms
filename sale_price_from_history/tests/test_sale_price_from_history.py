# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, SavepointCase


class TestSalePriceFromHistory(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test service", "type": "service"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.other_partner = cls.env["res.partner"].create(
            {"name": "Test other partner"}
        )
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        with sale_order_form.order_line.new() as line:
            line.product_id = cls.product
            line.price_unit = 70
        sale_order_form.price_history = True
        sale_order_form.save()
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        with sale_order_form.order_line.new() as line:
            line.product_id = cls.product
            line.price_unit = 50
        sale_order_form.save()
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.other_partner
        with sale_order_form.order_line.new() as line:
            line.product_id = cls.product
            line.price_unit = 30
        sale_order_form.save()

    def test_01_wizard_correct_lines(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line:
            line.product_id = self.product
        sale_order = sale_order_form.save()
        wiz_form = Form(
            self.env["wizard.sale.line.history.price"].with_context(
                active_id=sale_order.order_line.id
            )
        )
        wiz = wiz_form.save()
        self.assertEqual(len(wiz.sale_line_ids), 2)
        wiz.partner_id = False
        self.assertEqual(len(wiz.sale_line_ids), 3)
        for line in wiz.sale_line_ids:
            if line.price_unit == 70:
                self.assertTrue(line.price_history)
            else:
                self.assertFalse(line.price_history)

    def test_02_aply_selected_price(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line:
            line.product_id = self.product
            line.price_unit = 2
        sale_order = sale_order_form.save()
        wiz_form = Form(
            self.env["wizard.sale.line.history.price"].with_context(
                active_id=sale_order.order_line.id
            )
        )
        wiz = wiz_form.save()
        line_history = wiz.sale_line_ids.filtered("price_history")
        line_history.with_context(to_set_price_line_id=wiz.sale_line_id.id).set_price()
        self.assertEqual(sale_order.order_line.price_unit, 70)
