# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class TestSaleLineReassign(TransactionCase):
    def test_reassign(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Partner Test",
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Product Test",
            }
        )
        sale_from = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "price_unit": 150.00,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                        },
                    )
                ],
            }
        )
        sale_to = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
            }
        )
        pl_reassign = (
            self.env["sale.order.line.reassign.wiz"]
            .with_context(active_ids=sale_from.order_line.ids)
            .create(
                {
                    "sale_order_id": sale_to.id,
                }
            )
        )
        pl_reassign.action_apply()
        self.assertFalse(len(sale_from.order_line))
        self.assertTrue(len(sale_to.order_line))

    def test_merge_analytic_distribution(self):
        Plan = self.env["account.analytic.plan"]
        Account = self.env["account.analytic.account"]
        line_plan = Plan.create({"name": "Business lines"})
        tag_plan = Plan.create({"name": "Tags"})
        vehicle_plan = Plan.create({"name": "Vehicles"})
        line_1, line_2 = (
            Account.create({"name": name, "plan_id": line_plan.id})
            for name in ("Line 1", "Line 2")
        )
        tag_1, tag_2 = (
            Account.create({"name": name, "plan_id": tag_plan.id})
            for name in ("Tag 1", "Tag 2")
        )
        vehicle_1, vehicle_2 = (
            Account.create({"name": name, "plan_id": vehicle_plan.id})
            for name in ("Vehicle 1", "Vehicle 2")
        )
        merge = self.env["sale.order.line.reassign.wiz"]._merge_analytic_distribution
        # The tag is kept with the new business line
        self.assertEqual(
            merge({f"{line_1.id},{tag_1.id}": 100}, {str(line_2.id): 100}),
            {f"{line_2.id},{tag_1.id}": 100},
        )
        # A split distribution keeps its percentages
        self.assertEqual(
            merge(
                {f"{line_1.id},{vehicle_1.id}": 40, f"{line_1.id},{vehicle_2.id}": 60},
                {str(line_2.id): 100},
            ),
            {f"{line_2.id},{vehicle_1.id}": 40, f"{line_2.id},{vehicle_2.id}": 60},
        )
        # The plans of the new distribution prevail
        self.assertEqual(
            merge({f"{line_1.id},{tag_1.id}": 100}, {f"{line_2.id},{tag_2.id}": 100}),
            {f"{line_2.id},{tag_2.id}": 100},
        )
        # Nothing to keep
        self.assertEqual(
            merge({str(line_1.id): 100}, {str(line_2.id): 100}),
            {str(line_2.id): 100},
        )
