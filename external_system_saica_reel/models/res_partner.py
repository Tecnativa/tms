# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    saica_reel_ref = fields.Char(string="Ref. for Saica")
    saica_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Saica Product",
        domain=[("type", "=", "service")],
    )
