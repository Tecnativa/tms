# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    price_history_location = fields.Boolean()

    @api.onchange("price_history_location")
    def _onchange_price_history_location(self):
        if not self.price_history:
            self.price_history = self.price_history_location
