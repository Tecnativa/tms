# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare, float_round


class TmsAnalyticDistribution(models.AbstractModel):
    """Lines with a tractor or a trailer and an analytic distribution (sale order,
    purchase order and journal item lines): the distribution of the vehicles is
    added to the one of the line on any create or write of them (forms, imports,
    RPC...), replacing the one of the previous vehicles.

    The models that inherit it call ``_tms_analytic_create``,
    ``_tms_analytic_write`` and ``_tms_analytic_compute`` from their own
    ``create``, ``write`` and ``_compute_analytic_distribution``, as the methods
    of an abstract model inherited after the core one would come after it in the
    MRO, and the core compute doesn't call super.
    """

    _name = "tms.analytic.distribution"
    _description = "Vehicles in the analytic distribution of TMS lines"

    def _get_vehicles_analytic_lines(self):
        """Lines that get the distribution of their vehicles."""
        return self.filtered(lambda x: not x.display_type)

    def _get_vehicles_analytic_distributions(self):
        """Analytic distribution of the tractor and of the trailer of the line."""
        self.ensure_one()
        return (
            self.tractor_id | self.trailer_id
        )._get_vehicles_analytic_distributions()

    @api.model
    def _get_analytic_key_plans(self, accounts):
        """Root plans of the accounts of a distribution key."""
        # Users without access to analytic plans also change the vehicles
        return (
            self.env["account.analytic.account"]
            .sudo()
            .browse(accounts)
            .exists()
            .root_plan_id
        )

    @api.model
    def _merge_vehicles_analytic_distribution(self, distribution, to_add, to_remove):
        """The distribution of each vehicle (``to_add`` and ``to_remove`` are lists
        of them) is added to the one of the line, not replacing it: the line keeps
        its own analytic accounts (from the order type, the distribution models or
        set by hand).

        The accounts of the vehicle go into the keys of the line that have none
        of their plans, so the widget shows them in the same row, when those
        keys add up to 100%: a key at ``p`` and a vehicle key at ``q`` give
        their union at ``p * q / 100``, and the key keeps the rest of ``p`` if
        the vehicle is not at 100%. Otherwise (no such keys, as the second
        vehicle when the first one already took the vehicles plan) the vehicle
        keys are added on their own.

        Only the previous vehicles are removed: their accounts are taken out of
        the keys that have them. A vehicle already in the distribution is not
        added again, so applying the same change twice (task form and sale
        order line write, sale order line and the purchase or invoice line made
        from it) gives the same result.
        """
        precision = self.env["decimal.precision"].precision_get("Percentage Analytic")
        # Keys by their accounts, as the order of the ids is not relevant
        result = {}
        for key, percentage in (distribution or {}).items():
            accounts = frozenset(map(int, key.split(",")))
            result[accounts] = result.get(accounts, 0.0) + percentage

        def _add(accounts, percentage):
            result[accounts] = result.get(accounts, 0.0) + percentage

        for vehicle_distribution in to_remove:
            for key, percentage in vehicle_distribution.items():
                vehicle_accounts = frozenset(map(int, key.split(",")))
                if vehicle_accounts in result:
                    result[vehicle_accounts] -= min(
                        percentage, result[vehicle_accounts]
                    )
                for accounts in [x for x in result if x > vehicle_accounts]:
                    _add(accounts - vehicle_accounts, result.pop(accounts))
        result = {
            accounts: percentage
            for accounts, percentage in result.items()
            if float_compare(percentage, 0.0, precision_digits=precision) > 0
        }
        for vehicle_distribution in to_add:
            missing = {}
            for key, percentage in vehicle_distribution.items():
                vehicle_accounts = frozenset(map(int, key.split(",")))
                if not any(accounts >= vehicle_accounts for accounts in result):
                    missing[vehicle_accounts] = percentage
            if not missing:
                continue
            vehicle_plans = self._get_analytic_key_plans(list(set().union(*missing)))
            free = [
                accounts
                for accounts in result
                if not self._get_analytic_key_plans(list(accounts)) & vehicle_plans
            ]
            total = sum(missing.values())
            if (
                float_compare(
                    sum(result[x] for x in free), 100.0, precision_digits=precision
                )
                or float_compare(total, 100.0, precision_digits=precision) > 0
            ):
                for vehicle_accounts, percentage in missing.items():
                    result[vehicle_accounts] = percentage
                continue
            for accounts in free:
                line_percentage = result.pop(accounts)
                for vehicle_accounts, percentage in missing.items():
                    _add(
                        accounts | vehicle_accounts, line_percentage * percentage / 100
                    )
                _add(accounts, line_percentage * (100 - total) / 100)
        return {
            ",".join(map(str, sorted(accounts))): float_round(
                percentage, precision_digits=precision
            )
            for accounts, percentage in result.items()
            if float_compare(percentage, 0.0, precision_digits=precision) > 0
        } or False

    def _set_vehicles_analytic_distribution(self, to_add, to_remove):
        """Write the merged distribution only when it changes, as writing it on a
        journal item rebuilds its analytic lines."""
        self.ensure_one()
        distribution = self._merge_vehicles_analytic_distribution(
            self.analytic_distribution, to_add, to_remove
        )
        current = self._merge_vehicles_analytic_distribution(
            self.analytic_distribution, [], []
        )
        if distribution != current:
            self.analytic_distribution = distribution

    def _tms_analytic_create(self):
        """Add the distribution of the vehicles of the new lines."""
        for line in self._get_vehicles_analytic_lines().filtered(
            lambda x: x.tractor_id or x.trailer_id
        ):
            line._set_vehicles_analytic_distribution(
                line._get_vehicles_analytic_distributions(), []
            )

    def _tms_analytic_write(self, vals, write):
        """Any change of the tractor or the trailer replaces the distribution of
        the previous vehicles by the one of the new ones. ``write`` is the super
        call of the model."""
        if "tractor_id" not in vals and "trailer_id" not in vals:
            return write(vals)
        lines = self._get_vehicles_analytic_lines()
        previous = {line: line._get_vehicles_analytic_distributions() for line in lines}
        res = write(vals)
        for line in lines:
            line._set_vehicles_analytic_distribution(
                line._get_vehicles_analytic_distributions(), previous[line]
            )
        return res

    def _tms_analytic_compute(self, compute):
        """The vehicles in the distribution are taken out while the rest of it is
        computed (distribution models, order type, project...) and added back
        afterwards, so they are neither lost nor altered. ``compute`` is the
        super call of the model."""
        vehicles = {}
        for line in self:
            distribution = line.analytic_distribution or {}
            accounts = [frozenset(map(int, key.split(","))) for key in distribution]
            vehicles[line] = [
                vehicle_distribution
                for vehicle_distribution in line._get_vehicles_analytic_distributions()
                if all(
                    any(x >= frozenset(map(int, key.split(","))) for x in accounts)
                    for key in vehicle_distribution
                )
            ]
            if vehicles[line]:
                line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                    distribution, [], vehicles[line]
                )
        res = compute()
        for line in self._get_vehicles_analytic_lines().filtered(lambda x: vehicles[x]):
            line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                line.analytic_distribution, vehicles[line], []
            )
        return res
