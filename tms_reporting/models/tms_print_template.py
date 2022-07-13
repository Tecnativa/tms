# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsPrintTemplate(models.Model):
    _name = "tms.print.template"
    _description = "Dynamic template options to print reports"

    name = fields.Char()
    print_template_type = fields.Selection(
        selection=[
            ("dynamic", "Dynamic"),
        ],
        string="Type",
        default="dynamic",
    )
    field_order = fields.Selection(
        [("order_id", "Sale Order"), ("pickup_date", "Pickup Date")],
        default="order_id",
    )
    display_order = fields.Boolean()
    display_date = fields.Boolean()
    display_client_ref = fields.Boolean()
    display_description = fields.Boolean()
    display_vehicle = fields.Boolean()
    display_equipment = fields.Boolean()
    display_wagon = fields.Boolean()
    display_vessel = fields.Boolean()
    display_voyage_number = fields.Boolean()
    display_booking_number = fields.Boolean()
    display_port = fields.Boolean()
    display_shipment_port = fields.Boolean()
    display_loading_port = fields.Boolean()
    display_unloading_port = fields.Boolean()
    display_dua_ref = fields.Boolean()
    display_tracking_ref = fields.Boolean()
    display_goods = fields.Boolean()
    display_weight = fields.Boolean()
    display_release = fields.Boolean()
    display_origin_zip = fields.Boolean()
    display_origin_city = fields.Boolean()
    display_origin = fields.Boolean()
    display_destination_zip = fields.Boolean()
    display_destination_city = fields.Boolean()
    display_destination = fields.Boolean()
    display_shipping_place_zip = fields.Boolean()
    display_shipping_place_city = fields.Boolean()
    display_shipping_place = fields.Boolean()
    display_acceptance = fields.Boolean()
    display_quantity = fields.Boolean()
    display_price = fields.Boolean()
    display_discount = fields.Boolean()
    display_taxes = fields.Boolean()
    display_total = fields.Boolean()
