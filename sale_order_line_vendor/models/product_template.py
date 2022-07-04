# Copyright 2022 Tecnativa - Carlos Dauden
# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_line_cost_zero = fields.Boolean(
        help="If set, The sale order line cost will be zero",
    )
