# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import OrderedSet


class TmsAnalytic(models.AbstractModel):
    _name = "tms.analytic"
    _description = "TMS Analityc"

    tractor_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Tractor",
        ondelete="restrict",
        domain=[("vehicle_type", "=", "tractor")],
        context={"default_vehicle_type": "tractor"},
        index=True,
        copy=False,
    )
    trailer_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Trailer",
        ondelete="restrict",
        domain=[("vehicle_type", "=", "trailer")],
        context={"default_vehicle_type": "trailer"},
        index=True,
        copy=False,
    )
    driver_id = fields.Many2one(
        comodel_name="res.partner",
        string="Driver",
        context={"default_is_driver": True},
        index=True,
        copy=False,
        help="Driver of the vehicle",
    )

    # @api.model
    # def _proper_fields(self):
    #     return OrderedSet({"tractor_id", "trailer_id", "driver_id"})

    @api.model
    def analytic_fields(self):
        return OrderedSet({"tractor_id", "trailer_id", "driver_id"})
        # return proper_fields - {"display_name", "__last_update", "id"}

    @api.model
    def analytic_fields_vals(self, record):
        vals = {}
        for field in self.analytic_fields():
            value = record._fields[field].convert_to_write(record[field], record)
            if value:
                vals[field] = value
        return vals

    @api.onchange("tractor_id")
    def _onchange_tractor_id(self):
        if self.env.context.get("skip_tractor_onchange"):
            return
        self.update(
            {
                "trailer_id": self.tractor_id.trailer_id.id,
                "driver_id": self.tractor_id.driver_id.id,
            }
        )

    @api.onchange("driver_id")
    def _onchange_driver_id(self):
        if (
            self.env.context.get("skip_driver_onchange")
            or "vendor_id" not in self._fields
        ):
            return
        # Evaluate if driver is from my company or other to assign as vendor
        commercial_partner = self.driver_id.commercial_partner_id
        self.vendor_id = (
            commercial_partner
            if self.env.company not in commercial_partner.ref_company_ids
            else False
        )
