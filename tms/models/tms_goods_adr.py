# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class TmsGoodsAdrClass(models.Model):
    _name = "tms.goods.adr.class"
    _description = "TMS Goods ADR Class"

    code = fields.Char(required=True)
    name = fields.Char(translate=True)

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("code", "=ilike", name.split(" ")[0] + "%"),
                ("name", operator, name),
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ["&", "!"] + domain[1:]
        return self._search(
            expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid
        )

    def name_get(self):
        result = []
        for adr_class in self:
            name = "({}) {}".format(adr_class.code, adr_class.name)
            result.append((adr_class.id, name))
        return result


class TmsGoodsAdr(models.Model):
    _name = "tms.goods.adr"
    _description = "TMS Goods ADR"

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

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("un_number", "=ilike", name.split(" ")[0] + "%"),
                ("name", operator, name),
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ["&", "!"] + domain[1:]
        return self._search(
            expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid
        )

    def name_get(self):
        result = []
        for adr in self:
            name = "[{}] {} ({})".format(adr.un_number, adr.name, adr.adr_class.code)
            result.append((adr.id, name))
        return result
