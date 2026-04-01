# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    georoute_provider_openrouteservice_key = fields.Char(
        string="Open Route Service API Key",
        related="company_id.openrouteservice_api_key",
        help="Visit https://openrouteservice.org/services/ for more information.",
        readonly=False,
    )
