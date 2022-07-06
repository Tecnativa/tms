# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsGoods(models.Model):
    _name = "tms.goods"
    _description = "TMS Goods"

    name = fields.Char()
    adr_id = fields.Many2one(comodel_name="tms.goods.adr", string="ADR")


class TmsGoodsAdr(models.Model):
    _name = "tms.goods.adr"
    _description = "TMS Goods Adr"

    name = fields.Char()
