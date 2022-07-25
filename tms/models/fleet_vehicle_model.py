# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"

    vehicle_type = fields.Selection(
        selection_add=[
            ("tractor", "Tractor"),
            ("trailer", "Trailer"),
        ],
        ondelete={"tractor": "set default", "trailer": "set default"},
    )
