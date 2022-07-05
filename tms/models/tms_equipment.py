# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

try:
    from stdnum import iso6346
except (ImportError, IOError) as err:
    logging.info(err)


class ISO6346Length(models.Model):
    _name = "iso6346.length"
    _rec_name = "code"
    _description = "iso6346 Length"

    code = fields.Char()
    name = fields.Char()
    length = fields.Float()  # pylint: disable=W8105

    _sql_constraints = [("uniq_code", "unique(code)", _("The code must be unique !"))]


class ISO6346SecondSize(models.Model):
    _name = "iso6346.second.size"
    _rec_name = "code"
    _description = "iso6346 Second Size"

    code = fields.Char()
    name = fields.Char()
    height = fields.Float()
    width = fields.Float()

    _sql_constraints = [("uniq_code", "unique(code)", _("The code must be unique !"))]


class ISO6346Type(models.Model):
    _name = "iso6346.type"
    _rec_name = "code"
    _description = "iso6346 Type"

    code = fields.Char()
    name = fields.Char()

    _sql_constraints = [("uniq_code", "unique(code)", _("The code must be unique !"))]


class ISO6346SizeType(models.Model):
    _name = "iso6346.size.type"
    _rec_name = "code"
    _description = "iso6346 Size Type"

    code = fields.Char(
        size=4,
    )
    name = fields.Char()
    length_id = fields.Many2one(
        comodel_name="iso6346.length",
        string="Length",
        ondelete="restrict",
    )
    second_size_id = fields.Many2one(
        comodel_name="iso6346.second.size",
        string="Second Size",
        ondelete="restrict",
    )
    type_id = fields.Many2one(
        comodel_name="iso6346.type",
        string="Type",
        ondelete="restrict",
    )

    _sql_constraints = [("uniq_code", "unique(code)", _("The code must be unique !"))]

    @api.onchange("code")
    def _onchange_code(self):
        for size in self:
            if not size.code or len(size.code) < 4:
                continue
            size.update(
                {
                    "length_id": size.length_id.search(
                        [("code", "=", size.code[0])]
                    ).id,
                    "second_size_id": size.second_size_id.search(
                        [("code", "=", size.code[1])]
                    ).id,
                    "type_id": size.type_id.search([("code", "=", size.code[2:4])]).id,
                }
            )


class TmsEquipment(models.Model):
    _name = "tms.equipment"
    _description = "TMS Equipment"

    name = fields.Char(required=True)
    equipment_type = fields.Selection(
        [
            ("container", "Container"),
            ("jail", "Jail"),
        ],
        string="Type",
        default="container",
    )
    size_type_id = fields.Many2one(
        comodel_name="iso6346.size.type", string="Size Type", ondelete="restrict"
    )
    goods_ids = fields.Many2many(
        comodel_name="tms.goods",
        string="Goodss",
        help="Adapted for goodss",
        ondelete="restrict",
    )
    iso6346_ok = fields.Boolean(
        string="ISO6346 Validation",
        default=True,
    )

    _sql_constraints = [("uniq_name", "unique(name)", _("The name must be unique !"))]

    def _verify_iso6346(self, vals):
        name = vals.get("name", self.name).replace(" ", "").replace("-", "")
        try:
            vals["name"] = iso6346.validate(name)
        except Exception as error:
            raise ValidationError(_("The name is invalid: %s" % str(error)))
        return vals

    def write(self, vals):
        if vals.get("iso6346_ok", self.iso6346_ok):
            vals = self._verify_iso6346(vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("iso6346_ok", True):
                vals = self._verify_iso6346(vals)
        return super().create(vals_list)
