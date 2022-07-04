# Copyright 2019 Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields

from .common import TestTMS


class TestTMSFlow(TestTMS):
    def test_sale_order_creation(self):
        # Create Product
        product = self.env["product.product"].create(
            {"product_tmpl_id": self.delivered_product_tmpl.id,}
        )

        # Create Package
        package = self.env["tms.package"].create(
            {
                "shipping_origin_id": self.partner_origin.id,
                "shipping_destination_id": self.partner_destination.id,
                "pickup_date": fields.Datetime.now(),
                "partner_id": self.customer.id,
            }
        )
        # Create Sale Order
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "wagon": "TestWagon",
                "vessel": "TestVessel",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": product.id,
                            "pickup_date": fields.Datetime.now(),
                            "shipping_origin_id": self.partner_origin.id,
                            "shipping_destination_id": self.partner_destination.id,
                            "tms_package_ids": [(6, False, [package.id])],
                            "equipment_id": self.equipment.id,
                        },
                    )
                ],
            }
        )

        sale_order.action_confirm()
        sale_order._compute_tasks_ids()
        self.assertEqual(sale_order.tasks_count, 1)
        self.assertTrue(sale_order.tasks_ids)

        # Verify task
        task = sale_order.tasks_ids[0]
        self.assertTrue(task)
        self.assertEqual(len(task.tms_package_ids), 1)
        self.assertEqual(task.wagon, "TestWagon")
        self.assertEqual(task.vessel, "TestVessel")
        # Update Task
        task.write(
            {"driver_id": self.driver.id, "tractor_id": self.vehicle.id,}
        )
        self.assertEqual(self.vehicle.task_count, 1)

        # Update Sale Order
        sale_order.write({"wagon": "TextWagonB", "vessel": "TestVesselB"})
        self.assertNotEqual(task.wagon, "TextWagon")
        self.assertNotEqual(task.vessel, "TestVessel")
