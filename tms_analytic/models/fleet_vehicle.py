# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, models


class FleetVehicle(models.Model):
    _name = "fleet.vehicle"
    _inherit = ["fleet.vehicle", "analytic.mixin"]

    def _get_vehicles_analytic_distributions(self):
        """Analytic distribution of each vehicle, in the order of the records."""
        return [
            vehicle.analytic_distribution
            for vehicle in self
            if vehicle.analytic_distribution
        ]

    @api.model
    def _get_vehicle_by_analytic_account(self, account_ids):
        """Vehicle represented by each account of the vehicles plan: the one with
        that account in its analytic distribution. An account in the distribution
        of several vehicles is left out, as it is not known which one it is."""
        # Posting is allowed to users without access to analytic plans
        plan = self.env["account.analytic.plan"]._get_vehicles_plan()
        accounts = (
            self.env["account.analytic.account"]
            .sudo()
            .browse(account_ids)
            .exists()
            .filtered(lambda account: account.root_plan_id == plan)
        )
        if not accounts:
            return {}
        vehicles_by_account = defaultdict(set)
        for vehicle in (
            self.sudo()
            .with_context(active_test=False)
            .search([("analytic_distribution", "in", accounts.ids)])
        ):
            for key in vehicle.analytic_distribution:
                for account_id in map(int, key.split(",")):
                    if account_id in accounts.ids:
                        vehicles_by_account[account_id].add(vehicle)
        return {
            account_id: vehicles.pop()
            for account_id, vehicles in vehicles_by_account.items()
            if len(vehicles) == 1
        }

    def _add_analytic_account(self, account):
        """Add the account to every key of the analytic distribution, unless it
        already has one of the same plan (a vehicle split between plans keeps its
        percentages)."""
        for vehicle in self:
            distribution = vehicle.analytic_distribution or {}
            plan_accounts = (
                self.env["account.analytic.account"]
                .browse({int(x) for key in distribution for x in key.split(",")})
                .exists()
                .filtered(lambda x: x.root_plan_id == account.root_plan_id)
            )
            if plan_accounts:
                continue
            vehicle.analytic_distribution = {
                f"{key},{account.id}": percentage
                for key, percentage in distribution.items()
            } or {str(account.id): 100.0}
