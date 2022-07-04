# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CrmClaim(models.Model):
    _inherit = "crm.claim"

    picking_id = fields.Many2one(comodel_name="stock.picking", string="Picking",)
    move_line_id = fields.Many2one(
        comodel_name="stock.move.line", string="Detail operation",
    )
