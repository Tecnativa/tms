# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    division_id = fields.Many2one(
        comodel_name="tms.division",
        string="Division",
        ondelete="restrict",
        check_company=True,
    )
