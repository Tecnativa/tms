# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TmsGoodsAdrClass(models.Model):
    _name = "tms.goods.adr.class"
    _description = "TMS Goods ADR Class"
    _rec_names_search = ["code", "name"]

    code = fields.Char(required=True)
    name = fields.Char(translate=True)

    @api.depends("code", "name")
    def _compute_display_name(self):
        for adr_class in self:
            adr_class.display_name = f"({adr_class.code}) {adr_class.name or ''}"


class TmsGoodsAdr(models.Model):
    _name = "tms.goods.adr"
    _description = "TMS Goods ADR"
    _rec_names_search = ["un_number", "name"]

    name = fields.Char(
        translate=True, required=True, help="Name of the substance or article"
    )
    un_number = fields.Char(string="UN No.", required=True)
    adr_class = fields.Many2one(comodel_name="tms.goods.adr.class", string="Class")
    classification_code = fields.Char()
    packing_group = fields.Selection(
        selection=[("I", "I"), ("II", "II"), ("III", "III")]
    )
    adr_tag = fields.Char(string="Tag")

    @api.depends("un_number", "name", "adr_class.code")
    def _compute_display_name(self):
        for adr in self:
            adr.display_name = f"[{adr.un_number}] {adr.name} ({adr.adr_class.code})"
