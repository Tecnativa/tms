# Copyright 2017-2022 Tecnativa - Sergio Teruel
# Copyright 2017-2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsGoods(models.Model):
    _name = "tms.goods"
    _description = "TMS Goods"

    name = fields.Char(required=True)
    adr_id = fields.Many2one(comodel_name="tms.goods.adr", string="ADR")
