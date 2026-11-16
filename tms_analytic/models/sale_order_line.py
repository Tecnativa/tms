# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "tms.analytic.distribution"]

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._tms_analytic_create()
        return lines

    def write(self, vals):
        """Also from the task form, the planning kanban, the timeline..., as the
        task writes its vehicles on the sale order line."""
        return self._tms_analytic_write(vals, super().write)

    def _compute_analytic_distribution(self):
        return self._tms_analytic_compute(super()._compute_analytic_distribution)
