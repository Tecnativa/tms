# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsEquipment(models.Model):
    _inherit = "tms.equipment"

    sequence = fields.Integer(default=100)
    show_in_sheet = fields.Boolean(
        index=True, string="Show sheet", help="Show equipment in website sheet"
    )
