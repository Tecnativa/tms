# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form, tagged

from odoo.addons.tms.tests.common import TestTMS


@tagged("post_install", "-at_install")
class TestTmsAnalytic(TestTMS):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The task form only shows the distribution with analytic accounting
        cls.env.user.groups_id |= cls.env.ref("analytic.group_analytic_accounting")
        Plan = cls.env["account.analytic.plan"]
        Account = cls.env["account.analytic.account"]
        # As in the instances where the project plan holds the business lines,
        # so the project analytic account is not added to the distributions
        business_plan, _other_plans = Plan._get_all_plans()
        vehicles_plan = Plan.create({"name": "Vehicles"})
        cls.account_business = Account.create(
            {"name": "Road transport", "plan_id": business_plan.id}
        )
        cls.account_tractors = Account.create(
            {"name": "Tractors", "plan_id": business_plan.id}
        )
        cls.account_tractor = Account.create(
            {"name": "1111-AAA", "plan_id": vehicles_plan.id}
        )
        cls.account_tractor_2 = Account.create(
            {"name": "2222-BBB", "plan_id": vehicles_plan.id}
        )
        cls.account_trailer = Account.create(
            {"name": "R-3333-CCC", "plan_id": vehicles_plan.id}
        )
        cls.key_tractor = f"{cls.account_tractors.id},{cls.account_tractor.id}"
        cls.key_tractor_2 = f"{cls.account_tractors.id},{cls.account_tractor_2.id}"
        cls.key_trailer = f"{cls.account_tractors.id},{cls.account_trailer.id}"
        cls.vehicle.write(
            {
                "analytic_account_id": cls.account_tractor.id,
                "analytic_distribution": {cls.key_tractor: 100.0},
            }
        )
        cls.vehicle_2 = cls.vehicle.copy(
            {
                "license_plate": "Test-Vehicle-2",
                "analytic_account_id": cls.account_tractor_2.id,
                "analytic_distribution": {cls.key_tractor_2: 100.0},
            }
        )
        trailer_model = cls.vehicle_model.copy({"vehicle_type": "trailer"})
        cls.trailer = cls.env["fleet.vehicle"].create(
            {
                "model_id": trailer_model.id,
                "license_plate": "Test-Trailer",
                "analytic_account_id": cls.account_trailer.id,
                # Shared between several vehicles
                "analytic_distribution": {cls.key_trailer: 50.0},
            }
        )
        # Both tractors usually pull the same trailer
        (cls.vehicle | cls.vehicle_2).trailer_id = cls.trailer
        cls.product = cls.ordered_product_tmpl.product_variant_id
        cls.business_distribution = {str(cls.account_business.id): 100.0}

    def _create_sale_order(self, **line_vals):
        return self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        dict(
                            {
                                "product_id": self.product.id,
                                "pickup_date": fields.Datetime.now(),
                                "shipping_origin_id": self.partner_origin.id,
                                "shipping_destination_id": (
                                    self.partner_destination.id
                                ),
                                "analytic_distribution": self.business_distribution,
                            },
                            **line_vals,
                        ),
                    )
                ],
            }
        )

    def test_task_vehicles_distribution(self):
        order = self._create_sale_order()
        order.action_confirm()
        line = order.order_line
        task = line.task_id
        self.assertTrue(task)
        self.assertEqual(task.analytic_distribution, self.business_distribution)
        # The dispatcher assigns the tractor on the task, which brings its trailer
        with Form(task) as task_form:
            task_form.tractor_id = self.vehicle
        self.assertEqual(line.tractor_id, self.vehicle)
        self.assertEqual(line.trailer_id, self.trailer)
        self.assertEqual(
            line.analytic_distribution,
            {
                str(self.account_business.id): 100.0,
                self.key_tractor: 100.0,
                self.key_trailer: 50.0,
            },
        )
        self.assertEqual(task.analytic_distribution, line.analytic_distribution)
        # Change of tractor: the distribution of the previous one goes away
        with Form(task) as task_form:
            task_form.tractor_id = self.vehicle_2
        self.assertEqual(
            line.analytic_distribution,
            {
                str(self.account_business.id): 100.0,
                self.key_tractor_2: 100.0,
                self.key_trailer: 50.0,
            },
        )
        with Form(task) as task_form:
            task_form.tractor_id = self.env["fleet.vehicle"]
            task_form.trailer_id = self.env["fleet.vehicle"]
        self.assertEqual(line.analytic_distribution, self.business_distribution)

    def test_task_vehicles_without_form(self):
        order = self._create_sale_order()
        order.action_confirm()
        line = order.order_line
        # As the planning kanban, that doesn't run the form onchange
        line.task_id.tractor_id = self.vehicle
        self.assertEqual(line.tractor_id, self.vehicle)
        self.assertEqual(line.analytic_distribution, self.business_distribution)

    def test_sale_line_with_tractor(self):
        # The vehicles distribution is only set from the task form
        order = self._create_sale_order(tractor_id=self.vehicle.id)
        self.assertEqual(
            order.order_line.analytic_distribution, self.business_distribution
        )

    def test_order_type_distribution_with_tractor(self):
        order_type = self.env["sale.order.type"].create(
            {
                "name": "Road transport",
                "analytic_distribution": self.business_distribution,
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "type_id": order_type.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "pickup_date": fields.Datetime.now(),
                            "tractor_id": self.vehicle.id,
                        },
                    )
                ],
            }
        )
        line = order.order_line
        self.assertEqual(line.analytic_distribution, self.business_distribution)
        # The vehicle part set from the task form
        line.analytic_distribution = {
            str(self.account_business.id): 100.0,
            self.key_tractor: 100.0,
        }
        # A change of the type resets the line distribution, keeping the tractor
        other_account = self.account_business.copy({"name": "Containers"})
        other_type = order_type.copy(
            {"analytic_distribution": {str(other_account.id): 100.0}}
        )
        order.type_id = other_type
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(other_account.id): 100.0, self.key_tractor: 100.0},
        )

    def test_invoice_report_vehicles(self):
        self.product = self.env["product.product"].create(
            {"name": "Transport", "type": "service", "invoice_policy": "order"}
        )
        order = self._create_sale_order(tractor_id=self.vehicle.id)
        order.action_confirm()
        invoice = order._create_invoices()
        invoice.action_post()
        self.env.flush_all()
        report_lines = self.env["account.invoice.report"].search(
            [("move_id", "=", invoice.id), ("tractor_id", "=", self.vehicle.id)]
        )
        self.assertTrue(report_lines)
