# Copyright 2019 Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import TestTMS


class TestTMSFlow(TestTMS):
    def test_sale_order_creation(self):
        # Create Product
        product = self.env["product.product"].create(
            {
                "product_tmpl_id": self.delivered_product_tmpl.id,
            }
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
            {
                "driver_id": self.driver.id,
                "tractor_id": self.vehicle.id,
            }
        )
        self.assertEqual(self.vehicle.task_count, 1)

        # Update Sale Order
        sale_order.write({"wagon": "TextWagonB", "vessel": "TestVesselB"})
        self.assertNotEqual(task.wagon, "TextWagon")
        self.assertNotEqual(task.vessel, "TestVessel")

    def test_vehicle_create_and_edit_from_many2one(self):
        # "Create and edit..." from a vehicle many2one sends the typed text
        # as default_name, which is a computed field on fleet.vehicle
        vehicle_form = Form(
            self.env["fleet.vehicle"].with_context(
                default_vehicle_type="tractor", default_name="1234-ABC"
            )
        )
        self.assertEqual(vehicle_form.license_plate, "1234-ABC")
        vehicle_form.model_id = self.vehicle_model
        vehicle = vehicle_form.save()
        self.assertEqual(vehicle.license_plate, "1234-ABC")

    def test_vehicle_quick_create_from_many2one(self):
        # "Create" from a vehicle many2one calls name_create with the typed text
        self.env["ir.default"].set("fleet.vehicle", "model_id", self.vehicle_model.id)
        vehicle_id, display_name = (
            self.env["fleet.vehicle"]
            .with_context(default_vehicle_type="tractor")
            .name_create("1234-ABC")
        )
        vehicle = self.env["fleet.vehicle"].browse(vehicle_id)
        self.assertEqual(vehicle.license_plate, "1234-ABC")
        self.assertEqual(vehicle.model_id, self.vehicle_model)
        self.assertEqual(display_name, vehicle.display_name)

    def test_vehicle_quick_create_default_model_by_type(self):
        trailer_model = self.env["fleet.vehicle.model"].create(
            {
                "name": "Test Trailer Model",
                "brand_id": self.vehicle_model_brand.id,
                "vehicle_type": "trailer",
            }
        )
        IrDefault = self.env["ir.default"]
        IrDefault.set("fleet.vehicle", "model_id", self.vehicle_model.id)
        Vehicle = self.env["fleet.vehicle"]
        # The generic default model is a tractor, so it is not used for a trailer
        with (
            self.assertRaises(IntegrityError),
            mute_logger("odoo.sql_db"),
            self.cr.savepoint(),
        ):
            Vehicle.with_context(default_vehicle_type="trailer").name_create("T-1")
        IrDefault.set(
            "fleet.vehicle",
            "model_id",
            trailer_model.id,
            condition="vehicle_type=trailer",
        )
        trailer_id = Vehicle.with_context(default_vehicle_type="trailer").name_create(
            "T-1"
        )[0]
        trailer = Vehicle.browse(trailer_id)
        self.assertEqual(trailer.model_id, trailer_model)
        self.assertEqual(trailer.vehicle_type, "trailer")
        tractor_id = Vehicle.with_context(default_vehicle_type="tractor").name_create(
            "T-2"
        )[0]
        self.assertEqual(Vehicle.browse(tractor_id).model_id, self.vehicle_model)
