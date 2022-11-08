# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsValenciaportsBackend(models.Model):
    _inherit = "tms.pcs.backend"

    sale_order_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Order Type",
    )

    def _parse_dut(self, doc):
        res = super()._parse_dut(doc)
        if self.sale_order_type_id:
            res["type_id"] = self.sale_order_type_id.id
        return res
