# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.queue_job.job import job


class StockPicking(models.Model):
    _inherit = "stock.picking"

    saica_system = fields.Boolean()
    forecast_arrival_date = fields.Date()
    delivery_date = fields.Datetime()
    number_plate = fields.Char()
    saica_weight = fields.Float(string="Weight")
    saica_reel_count = fields.Integer(string="Reels Count")
    saica_load_type = fields.Char(string="Load Type")
    saica_final_destination_id = fields.Many2one(
        comodel_name="res.partner", ondelete="restrict", string="Final Destination",
    )
    saica_sale_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        relation="saica_stock_picking_sale_order_line_rel",
        column1="picking_id",
        column2="sale_line_id",
    )
    tractor_id = fields.Many2one(comodel_name="fleet.vehicle", string="Tractor",)
    trailer_id = fields.Many2one(comodel_name="fleet.vehicle", string="Trailer",)
    tractor_plate = fields.Char()
    trailer_plate = fields.Char()

    @api.onchange("tractor_id")
    def _onchange_tractor_id(self):
        self.update(
            {
                "tractor_plate": self.tractor_id.license_plate,
                "trailer_id": self.tractor_id.trailer_id,
            }
        )

    @api.onchange("trailer_id")
    def _onchange_trailer_id(self):
        self.trailer_plate = self.trailer_id.license_plate

    @job
    def _saica_confirm_reception(self):
        external_system = self.env.ref(
            "external_system_saica_reel.external_system_saica_reel"
        )
        pickings = self.filtered(
            lambda x: x.picking_type_id == external_system.incoming_picking_type_id
        )
        res = external_system.info_reception_saica(pickings)
        if not res[0]:
            raise ValidationError(
                _("Error to confirm reception to Saica System: %s" % res[1])
            )
        return res

    def launch_confirm_to_saica(self):
        picking_type_reception = self.env.ref(
            "external_system_saica_reel.picking_type_saica_reel_in"
        )
        picking_type_expedition = self.env.ref(
            "external_system_saica_reel.picking_type_saica_reel_out"
        )
        for picking in self:
            if picking.picking_type_id == picking_type_reception:
                picking.queue_confirm_reception()
            elif picking.picking_type_id == picking_type_expedition:
                picking.queue_confirm_expedition()

    def action_confirm_reception(self):
        self.queue_confirm_reception()

    def queue_confirm_reception(self):
        for picking in self:
            picking.with_delay()._saica_confirm_reception()

    def queue_confirm_expedition(self):
        for picking in self:
            picking.with_delay()._saica_confirm_expedition()

    @job
    def _saica_confirm_expedition(self):
        external_system = self.env.ref(
            "external_system_saica_reel.external_system_saica_reel"
        )
        pickings = self.filtered(
            lambda x: x.picking_type_id == external_system.outgoing_picking_type_id
        )
        res = external_system.info_expedition_saica(pickings)
        if not res[0]:
            raise ValidationError(
                _("Error to confirm expedition to Saica System: %s" % res[1])
            )
        return res

    def action_confirm_expedition(self):
        self.queue_confirm_expedition()

    @api.model
    def _prepare_sale_order(self):
        base_external = self.env.ref(
            "external_system_saica_reel.external_system_saica_reel"
        )
        SaleOrder = self.env["sale.order"]
        order = SaleOrder.new(
            {"partner_id": base_external.partner_id.id, "origin": self.wave_id.name,}
        )
        order.onchange_partner_id()
        return order._convert_to_write(order._cache)

    @api.model
    def _prepare_sale_order_line(self, order, product, picking, base_external):
        return {
            "product_id": product.id,
            "product_uom_qty": sum(self.move_line_ids.mapped("lot_id.saica_weight")),
            "order_id": order.id,
            "shipping_origin_id": base_external.shipping_origin_id.id,
            "shipping_destination_id": picking.partner_id.id,
            "tractor_id": picking.tractor_id.id,
            "trailer_id": picking.trailer_id.id,
        }

    # @ormcache('wave')
    def sale_order_from_picking(self, picking):
        SaleOrder = self.env["sale.order"]
        order = SaleOrder.search(
            [
                ("procurement_group_id", "=", picking.group_id.id),
                ("procurement_group_id", "!=", False),
            ]
        )
        if not order:
            order = SaleOrder.create(self._prepare_sale_order())
            order.action_confirm()
        return order

    def action_create_so(self):
        # Create one so for each wave and one line for each picking
        # included in a wave
        picking_type_expedition = self.env.ref(
            "external_system_saica_reel.picking_type_saica_reel_out"
        )
        base_external = self.env.ref(
            "external_system_saica_reel.external_system_saica_reel"
        )
        for picking in self.filtered(
            lambda x: x.picking_type_id == picking_type_expedition
        ):
            product = (
                picking.partner_id.saica_product_id or base_external.order_product_id
            )
            if not product:
                raise UserError(
                    _("The partner has not a product to create a " "sale order")
                )
            order = self.sale_order_from_picking(picking)
            vals = self._prepare_sale_order_line(order, product, picking, base_external)
            order_line = order.order_line.create(vals)
            picking.update(
                {
                    "group_id": order.procurement_group_id,
                    "saica_sale_line_ids": [(6, 0, order_line.ids)],
                }
            )
        return True

    # TODO: Review flow when use, only 9 claim records at 20200629. Removed
    def action_done(self):
        res = super().action_done()
        self.launch_confirm_to_saica()
        return res
