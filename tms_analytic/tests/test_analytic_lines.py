# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, fields
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestTmsAnalyticLines(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Plan = cls.env["account.analytic.plan"]
        Account = cls.env["account.analytic.account"]
        business_plan, _other_plans = Plan._get_all_plans()
        vehicles_plan = Plan.create({"name": "Vehicles"})
        cls.account_tractors = Account.create(
            {"name": "Tractors", "plan_id": business_plan.id}
        )
        brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Test brand"})
        tractor_model = cls.env["fleet.vehicle.model"].create(
            {"name": "Tractor", "brand_id": brand.id, "vehicle_type": "tractor"}
        )
        trailer_model = tractor_model.copy({"vehicle_type": "trailer"})
        cls.vehicles = cls.env["fleet.vehicle"]
        for plate, model in (
            ("1111-AAA", tractor_model),
            ("2222-BBB", tractor_model),
            ("R-3333-CCC", trailer_model),
        ):
            cls.vehicles |= cls.env["fleet.vehicle"].create(
                {
                    "model_id": model.id,
                    "license_plate": plate,
                    "analytic_account_id": Account.create(
                        {"name": plate, "plan_id": vehicles_plan.id}
                    ).id,
                }
            )

    def test_cost_shared_between_vehicles(self):
        tractor, tractor_2, trailer = self.vehicles
        distribution = {
            f"{self.account_tractors.id},{vehicle.analytic_account_id.id}": percentage
            for vehicle, percentage in zip(
                self.vehicles, (50.0, 30.0, 20.0), strict=True
            )
        }
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_a.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Fuel",
                            "price_unit": 300.0,
                            "tax_ids": [Command.clear()],
                            "analytic_distribution": distribution,
                        }
                    )
                ],
            }
        )
        bill.action_post()
        analytic_lines = bill.invoice_line_ids.analytic_line_ids
        self.assertEqual(len(analytic_lines), 3)
        self.assertEqual(analytic_lines.tractor_id, tractor | tractor_2)
        trailer_line = analytic_lines.filtered("trailer_id")
        self.assertEqual(trailer_line.trailer_id, trailer)
        self.assertFalse(trailer_line.tractor_id)
        self.assertEqual(
            analytic_lines.filtered(lambda x: x.tractor_id == tractor).amount, -150.0
        )

    def test_post_without_analytic_access(self):
        user = new_test_user(
            self.env,
            login="tms_analytic_billing",
            groups="account.group_account_invoice",
            company_id=self.env.company.id,
        )
        invoice = self.init_invoice("out_invoice", amounts=[100.0], post=False)
        invoice.with_user(user).action_post()
        self.assertEqual(invoice.state, "posted")
