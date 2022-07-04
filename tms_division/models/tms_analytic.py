# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsAnalytic(models.AbstractModel):
    _inherit = "tms.analytic"

    division_id = fields.Many2one(
        comodel_name="tms.division", string="Division", ondelete="restrict",
    )
