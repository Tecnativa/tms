# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_vehicles_analytic_distribution(self):
        """Analytic distribution of the tractor and the trailer of the line."""
        self.ensure_one()
        return (self.tractor_id | self.trailer_id)._get_vehicles_analytic_distribution()

    @api.model
    def _merge_vehicles_analytic_distribution(self, distribution, to_add, to_remove):
        """The vehicles distribution is added to the one of the line, not
        replacing it: the line keeps its own analytic accounts (from the order
        type, the distribution models or set by hand) and the vehicle ones are
        on top of them, as separate keys.
        """
        precision = self.env["decimal.precision"].precision_get("Percentage Analytic")
        result = dict(distribution or {})
        for key, percentage in to_remove.items():
            result[key] = result.get(key, 0.0) - percentage
        for key, percentage in to_add.items():
            result[key] = result.get(key, 0.0) + percentage
        return {
            key: percentage
            for key, percentage in result.items()
            if float_compare(percentage, 0.0, precision_digits=precision) > 0
        } or False

    def _compute_analytic_distribution(self):
        """The vehicles part of the distribution, set from the task form, is taken
        out while the rest of the distribution is computed (distribution models,
        order type, project...) and added back afterwards, so it is neither lost
        nor altered. It is not added when it isn't in the distribution, as in 15.0
        the vehicles analytic tags were only set by the task form."""
        vehicles = {}
        for line in self:
            distribution = line.analytic_distribution or {}
            vehicles_distribution = line._get_vehicles_analytic_distribution()
            vehicles[line] = {
                key: min(percentage, distribution[key])
                for key, percentage in vehicles_distribution.items()
                if key in distribution
            }
            if vehicles[line]:
                line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                    distribution, {}, vehicles[line]
                )
        res = super()._compute_analytic_distribution()
        for line in self.filtered(lambda x: not x.display_type and vehicles[x]):
            line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                line.analytic_distribution, vehicles[line], {}
            )
        return res
