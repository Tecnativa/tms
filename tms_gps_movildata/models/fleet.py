# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleLogGps(models.Model):
    _name = "fleet.vehicle.log.gps"

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehicle",)
    plate = fields.Char()
    latitude = fields.Float(string="Latitude", digits=(16, 5))
    longitude = fields.Float(string="Longitude", digits=(16, 5))
    time_log = fields.Datetime(string="Log Time")
