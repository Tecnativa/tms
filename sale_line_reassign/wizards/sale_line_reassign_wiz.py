# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018-2021 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from collections import defaultdict

from odoo import _, api, exceptions, fields, models


class SaleOrderLineReassignWiz(models.TransientModel):
    _name = "sale.order.line.reassign.wiz"
    _description = "Wizard to reassign sale order lines to other sale order"

    def _default_partner_id(self):
        active_ids = self.env.context.get("active_ids")
        lines = self.env["sale.order.line"].browse(active_ids)
        partner = lines[:1].order_id.partner_id
        if lines.filtered(
            lambda line: (line.invoice_lines or line.order_partner_id != partner)
        ):
            raise exceptions.ValidationError(
                _("Selected line/s are invoiced or they have distinct " "customers")
            )
        return partner

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Move to sale",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        default=lambda self: self._default_partner_id(),
    )

    @api.model
    def _merge_analytic_distribution(self, old_distribution, new_distribution):
        """Add to the new distribution the accounts of the old one from the plans
        it doesn't set. Before the analytic plans the analytic account came from the
        order and the analytic tags from the line, so moving a line changed its
        account but kept its tags."""
        Account = self.env["account.analytic.account"]

        def accounts(distribution):
            return Account.browse(
                {
                    int(account_id)
                    for key in distribution or {}
                    for account_id in key.split(",")
                }
            ).exists()

        new_plans = accounts(new_distribution).root_plan_id
        kept_accounts = accounts(old_distribution).filtered(
            lambda account: account.root_plan_id not in new_plans
        )
        if not kept_accounts:
            return new_distribution
        kept = defaultdict(float)
        for key, percentage in old_distribution.items():
            key_ids = [
                account_id
                for account_id in key.split(",")
                if int(account_id) in kept_accounts.ids
            ]
            if key_ids:
                kept[",".join(key_ids)] += percentage
        if not new_distribution:
            return dict(kept)
        merged = defaultdict(float)
        for new_key, new_percentage in new_distribution.items():
            for kept_key, kept_percentage in kept.items():
                merged[f"{new_key},{kept_key}"] += (
                    new_percentage * kept_percentage / 100
                )
        return dict(merged)

    def action_apply(self):
        active_ids = self.env.context.get("active_ids")
        lines = self.env["sale.order.line"].browse(active_ids)
        project = self.sale_order_id.project_ids[:1]
        old_distributions = {line: line.analytic_distribution for line in lines}
        lines.update({"order_id": self.sale_order_id.id})
        for line in lines.filtered(lambda line: old_distributions[line]):
            distribution = self._merge_analytic_distribution(
                old_distributions[line], line.analytic_distribution or {}
            )
            if distribution != line.analytic_distribution:
                line.analytic_distribution = distribution
        # Update project in so lines and tasks after v12 changes
        project_so_lines = lines.filtered("project_id")
        if project_so_lines:
            # Repeat update to avoid rewrite first line
            if not project:
                project = project_so_lines[:1]._timesheet_create_project()
                project_so_lines[1:].update({"project_id": project.id})
            else:
                project_so_lines.update({"project_id": project.id})
            project_so_lines.mapped("task_id").update({"project_id": project.id})
        # If sale_order_line_vendor is installed
        if "purchase_line_ids" in lines:
            for line in lines:
                line.purchase_line_ids.update(
                    {"analytic_distribution": line.analytic_distribution}
                )
        return lines
