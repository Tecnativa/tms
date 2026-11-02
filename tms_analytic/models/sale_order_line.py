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
        on top of them, as separate keys. Only the part of the previous vehicles
        still in the distribution is removed and a key of the new vehicles already
        in it is not added again, so applying the same change twice (task form and
        sale order line write) gives the same result.
        """
        precision = self.env["decimal.precision"].precision_get("Percentage Analytic")
        result = dict(distribution or {})
        for key, percentage in to_remove.items():
            if key in result:
                result[key] -= min(percentage, result[key])
        for key, percentage in to_add.items():
            if (
                float_compare(result.get(key, 0.0), 0.0, precision_digits=precision)
                <= 0
            ):
                result[key] = percentage
        return {
            key: percentage
            for key, percentage in result.items()
            if float_compare(percentage, 0.0, precision_digits=precision) > 0
        } or False

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines.filtered(
            lambda x: not x.display_type and (x.tractor_id or x.trailer_id)
        ):
            line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                line.analytic_distribution,
                line._get_vehicles_analytic_distribution(),
                {},
            )
        return lines

    def write(self, vals):
        """Any change of the tractor or the trailer (sale order line, task form,
        planning kanban, timeline...) replaces the distribution of the previous
        vehicles by the one of the new ones."""
        if "tractor_id" not in vals and "trailer_id" not in vals:
            return super().write(vals)
        lines = self.filtered(lambda x: not x.display_type)
        previous = {line: line._get_vehicles_analytic_distribution() for line in lines}
        res = super().write(vals)
        for line in lines:
            line.analytic_distribution = self._merge_vehicles_analytic_distribution(
                line.analytic_distribution,
                line._get_vehicles_analytic_distribution(),
                previous[line],
            )
        return res

    def _compute_analytic_distribution(self):
        """The vehicles part of the distribution is taken
        out while the rest of the distribution is computed (distribution models,
        order type, project...) and added back afterwards, so it is neither lost
        nor altered."""
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
