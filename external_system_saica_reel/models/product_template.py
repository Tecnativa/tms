# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _create_variant_ids(self):
        if self.env.context.get("no_create_variants", False):
            return True
        return super()._create_variant_ids()
