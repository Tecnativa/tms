# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_vehicles_analytic_distribution(self):
        """Analytic distribution of the tractor and the trailer of the line."""
        self.ensure_one()
        distribution = {}
        for vehicle in self.tractor_id | self.trailer_id:
            for key, percentage in (vehicle.analytic_distribution or {}).items():
                distribution[key] = distribution.get(key, 0.0) + percentage
        return distribution

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
        """The vehicles part is taken out while the rest of the distribution is
        computed (distribution models, order type, project...) and added back
        afterwards, so it is neither lost nor altered."""
        vehicles = {line: line._get_vehicles_analytic_distribution() for line in self}
        for line in self:
            if vehicles[line] and line.analytic_distribution:
                line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                    line.analytic_distribution, {}, vehicles[line]
                )
        res = super()._compute_analytic_distribution()
        for line in self.filtered(lambda x: not x.display_type and vehicles[x]):
            line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                line.analytic_distribution, vehicles[line], {}
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        # A distribution given on creation is not computed: add the vehicles one
        for line, vals in zip(lines, vals_list, strict=True):
            if (
                vals.get("analytic_distribution")
                and not line.display_type
                and {"tractor_id", "trailer_id"} & vals.keys()
            ):
                line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                    line.analytic_distribution,
                    line._get_vehicles_analytic_distribution(),
                    {},
                )
        return lines

    def write(self, vals):
        if not {"tractor_id", "trailer_id"} & vals.keys():
            return super().write(vals)
        previous = {line: line._get_vehicles_analytic_distribution() for line in self}
        res = super().write(vals)
        for line in self.filtered(lambda x: not x.display_type):
            vehicles_distribution = line._get_vehicles_analytic_distribution()
            if vehicles_distribution != previous[line]:
                line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                    line.analytic_distribution,
                    vehicles_distribution,
                    previous[line],
                )
        return res
