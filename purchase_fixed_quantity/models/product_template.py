# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fixed_purchase_qty = fields.Float(
        string="Fixed Purchase Quantity",
        digits="Product Unit of Measure",
        help="Not zero value to fix units in purchase order line. "
        "If zero normal quantity assignament",
    )
