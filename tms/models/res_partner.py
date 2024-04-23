# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.misc import format_duration


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_shipping_place = fields.Boolean(string="Shipping Place")
    is_driver = fields.Boolean(string="Driver")
    zone_id = fields.Many2one(comodel_name="res.partner.zone", string="Zone")
    trailer_tag_ids = fields.Many2many(
        comodel_name="fleet.vehicle.tag",
        relation="res_partner_fleet_trailer_tag_rel",
        string="Trailer Requirements",
    )
    schedule_ids = fields.One2many(
        comodel_name="res.partner.schedule",
        inverse_name="partner_id",
        string="Schedule",
    )

    def _get_name(self):
        """Extend to allow use partner_show_only_name context"""
        if self.env.context.get("partner_show_only_name"):
            return self.name or self.commercial_company_name or ""
        return super()._get_name()


# TODO: Use OCA modules
class ResPartnerZone(models.Model):
    _name = "res.partner.zone"
    _description = "Partner Zone"

    name = fields.Char()


class ResPartnerSchedule(models.Model):
    _name = "res.partner.schedule"
    _description = "Partner Schedule"

    name = fields.Char(compute="_compute_name", store=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        ondelete="cascade",
    )
    hour_from = fields.Float(string="From")
    hour_to = fields.Float(string="To")

    @api.depends("hour_from", "hour_to")
    def _compute_name(self):
        for schedule in self:
            hour_from = format_duration(schedule.hour_from)
            hour_to = format_duration(schedule.hour_to)
            schedule.name = "%s -> %s" % (hour_from, hour_to)
