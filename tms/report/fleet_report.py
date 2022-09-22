# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetReport(models.Model):
    _inherit = "fleet.vehicle.cost.report"

    vehicle_type = fields.Selection(
        selection_add=[
            ("tractor", "Tractor"),
            ("trailer", "Trailer"),
        ],
    )
