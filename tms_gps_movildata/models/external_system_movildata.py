# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=missing-import-error

import logging
from datetime import datetime

import pytz
from zeep import Client

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ExternalSystem(models.Model):
    _inherit = "external.system"

    movildata_adapter_ids = fields.One2many(
        comodel_name="external.system.movildata",
        inverse_name="system_id",
        string="Adapter",
    )


class ExternalSystemMovildata(models.Model):
    """This is an Interface implementing the OS module.

    For the most part, this is just a sample of how to implement an external
    system interface. This is still a fully usable implementation, however.
    """

    _name = "external.system.movildata"
    _inherit = "external.system.adapter"
    _description = "External System GPS Movildata"

    last_time_log = fields.Datetime(
        string="Last time log", default="2017-09-01 00:00:00",
    )
    min_log_time = fields.Integer(
        string="Min Time Interval", help="Min interval to log in minutes", default=5,
    )
    min_log_position = fields.Integer(string="Min Position Interval", default=1,)

    @api.multi
    def external_get_client(self):
        """Return a usable client representing the remote system."""
        super(ExternalSystemMovildata, self).external_get_client()
        # imp = Import(
        #     'http://www.w3.org/2001/XMLSchema',
        #     location='http://www.w3.org/2001/XMLSchema.xsd')
        # imp.filter.add('http://tempuri.org/')
        # client = Client(self.host, doctor=ImportDoctor(imp))
        client = Client(self.host)
        return client

    @api.multi
    def external_destroy_client(self, client):
        """Perform any logic necessary to destroy the client connection.

        Args:
            client (mixed): The client that was returned by
             ``external_get_client``.
        """
        super(ExternalSystemMovildata, self).external_destroy_client(client)
        # TODO: Implement

    @api.multi
    def external_test_connection(self):
        """Adapters should override this method, then call super if valid.

        If the connection is invalid, adapters should raise an instance of
        ``odoo.ValidationError``.

        Raises:
            odoo.exceptions.UserError: In the event of a good connection.
        """
        client = self.external_get_client()
        with client.options(raw_response=True):
            response = client.service.getVehiculos(self.private_key)
            if response.status_code != 200:
                raise ValidationError(_("Connection Failed"))
        _logger.info(self.getVehiculos())
        super(ExternalSystemMovildata, self).external_test_connection()

    def getVehiculos(self):
        client = self.external_get_client()
        res = client.service.getVehiculos(apikey=self.private_key)
        vehicles = {}
        for table in res["_value_1"].getchildren()[0]:
            vehicles[table.find("matricula").text] = {
                "IMEI": table.find("IMEI").text,
            }
        return vehicles

    @api.model
    def vehicle_from_plate(self, plate=None):
        return self.env["fleet.vehicle"].search(
            [("license_plate", "=", plate)], limit=1
        )

    @api.model
    def date_utc_from_tz(self, date, tz="Europe/Madrid"):
        user_tz = pytz.timezone(tz)
        utc = pytz.utc
        return user_tz.localize(date).astimezone(utc)

    @api.model
    def date_tz_from_utc(self, date, tz="Europe/Madrid"):
        user_tz = pytz.timezone(tz)
        utc = pytz.utc
        return utc.localize(date).astimezone(user_tz)

    @api.model
    def date_tz_from_str(self, date_str, tz="Europe/Madrid"):
        date = fields.Datetime.from_string(date_str)
        return self.date_tz_from_utc(date, tz)

    def parse_line_vals(self, line):
        values = line.split("\t")
        position = tuple(values[3].split(","))
        return {
            "plate": values[1],
            "time_log": self.date_utc_from_tz(
                datetime.strptime(values[2], "%d/%m/%Y %H:%M:%S")
            ),
            "latitude": float(position[0]),
            "longitude": float(position[1]),
        }

    def skip_log(self, vals, last_vals, min_log_time, min_log_position):
        if not last_vals:
            return False
        time_diff = (vals["time_log"] - last_vals["time_log"]).total_seconds()
        pos_diff = max(
            abs(vals["latitude"] - last_vals["latitude"]),
            abs(vals["longitude"] - last_vals["longitude"]),
        )
        return time_diff < min_log_time or pos_diff < min_log_position

    def getGPSData(self, matricula, desde=None, hasta=None):
        FleetVehicleLogGps = self.env["fleet.vehicle.log.gps"]
        new_gps_logs = FleetVehicleLogGps
        client = self.external_get_client()
        try:
            data = client.service.getGPSData(
                apikey=self.private_key,
                matricula=matricula,
                desde=self.date_tz_from_str(
                    desde or self.last_time_log or "2017-09-01 00:00:00"
                ),
                hasta=self.date_tz_from_str(hasta or fields.Datetime.now()),
            )
        except Exception:
            _logger.error(_("Error to get GPS Data"))
            return new_gps_logs
        min_log_time = self.min_log_time * 60
        min_log_position = self.min_log_position / 100.0
        vehicle = self.vehicle_from_plate(matricula)
        last_vals = {}
        for line in data.split("\n")[1:]:
            if not line:
                continue
            vals = self.parse_line_vals(line)
            if self.skip_log(vals, last_vals, min_log_time, min_log_position):
                continue
            vals["vehicle_id"] = vehicle.id
            new_gps_logs |= FleetVehicleLogGps.create(vals)
            last_vals = vals
        if last_vals:
            self.last_time_log = fields.Datetime.to_string(last_vals["time_log"])
        return new_gps_logs

    @api.multi
    def import_gps_data(self):
        for adapter in self:
            vehicles = adapter.getVehiculos()
            for vehicle in vehicles.keys():
                adapter.getGPSData(matricula=vehicle)

    @api.model
    def cron_import_gps_data(self):
        self.search([]).import_gps_data()
