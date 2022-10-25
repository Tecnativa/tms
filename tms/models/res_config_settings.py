# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    georoute_provider_id = fields.Many2one(
        comodel_name="base.geo_provider",
        string="API Route",
        config_parameter="base_geolocalize.georoute_provider",
        # default=lambda x: x.env['base.geocoder']._get_provider()
    )
    georoute_provider_techname = fields.Char(
        related="georoute_provider_id.tech_name", readonly=1
    )
    georoute_provider_openrouteservice_key = fields.Char(
        string="Open Route Service API Key",
        config_parameter="base_geolocalize.openrouteservice_api_key",
        help="Visit https://openrouteservice.org/services/ for more information.",
    )
