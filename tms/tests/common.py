# Copyright 2019 Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestTMS(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Generic Data
        cls.iso6346_length = cls.env.ref("tms.iso6346_length_1")
        cls.iso6346_type = cls.env.ref("tms.iso6346_type_G0")
        cls.iso6346_second_size = cls.env.ref("tms.iso6346_second_size_0")

        cls.size_type = cls.env["iso6346.size.type"].create(
            {
                "name": "Test Code",
                "code": "1234",
                "length_id": cls.iso6346_length.id,
                "second_size_id": cls.iso6346_second_size.id,
                "type_id": cls.iso6346_type.id,
            }
        )

        cls.goods_adr = cls.env["tms.goods.adr"].create(
            {
                "name": "Test ADR",
                "un_number": "1234",
            }
        )
        cls.goods = cls.env["tms.goods"].create(
            {
                "name": "Tests Goods",
                "adr_id": cls.goods_adr.id,
            }
        )

        cls.equipment = cls.env["tms.equipment"].create(
            {
                "name": "CSQU3054383",
                "size_type_id": cls.size_type.id,
                "goods_ids": [(4, cls.goods.id)],
            }
        )

        # Driver
        cls.driver = cls.env["res.partner"].create(
            {"name": "Destination Test", "company_type": "person", "is_driver": True}
        )

        # Customer
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Customer Test",
                "company_type": "company",
            }
        )

        # Origin Location
        cls.partner_origin = cls.env["res.partner"].create(
            {
                "name": "Origin Test",
                "is_shipping_place": True,
            }
        )

        # Destination Location
        cls.partner_destination = cls.env["res.partner"].create(
            {
                "name": "Destination Test",
                "is_shipping_place": True,
            }
        )

        # Vehicle
        cls.vehicle_model_brand = cls.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Test Brand",
            }
        )
        cls.vehicle_model = cls.env["fleet.vehicle.model"].create(
            {
                "name": "Test Model",
                "brand_id": cls.vehicle_model_brand.id,
                "vehicle_type": "tractor",
            }
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.vehicle_model.id,
                "license_plate": "Test-Vehicle",
                "driver_id": cls.driver.id,
            }
        )

        cls.project = cls.env["project.project"].create({"name": "Some test project"})

        # Ordered Product Template
        cls.delivered_product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product Delivery",
                "type": "service",
                "service_policy": "delivered_timesheet",
                "service_tracking": "task_in_project",
                "invoicing_finished_task": True,
            }
        )

        # Ordered Product Template
        cls.ordered_product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product Order",
                "type": "service",
                "service_policy": "ordered_timesheet",
                "service_tracking": "task_in_project",
                "invoicing_finished_task": True,
            }
        )
