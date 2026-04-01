# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    openrouteservice_api_key = fields.Char(
        string="OpenRouteService API Key", help="API key for OpenRouteService geocoding"
    )
