# Copyright 2017-2021 Tecnativa - Carlos Dauden
# Copyright 2017-2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    vendor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        copy=False,
        context={
            "default_supplier_rank": 1,
            "default_customer_rank": 0,
        },
    )
    vendor_price_unit = fields.Float(
        string="Cost Price",
        digits="Product Price",
        compute="_compute_vendor_price_unit",
        store=True,
        readonly=False,
    )
    vendor_price_subtotal = fields.Monetary(
        compute="_compute_amount_vendor",
        string="Cost Subtotal",
        store=True,
    )

    # product_id.sale_line_cost_zero is not added to depends to avoid
    # recompute if this field change
    @api.depends("product_uom_qty", "product_uom", "vendor_id")
    def _compute_vendor_price_unit(self):
        for line in self:
            if (
                line.vendor_id
                and line.product_id
                and not line.product_id.sale_line_cost_zero
            ):
                suplierinfo = line.product_id._select_seller(
                    partner_id=line.vendor_id,
                    quantity=line.product_uom_qty,
                    uom_id=line.product_uom,
                )
                line.vendor_price_unit = suplierinfo.price
            else:
                line.vendor_price_unit = 0.0

    def _purchase_service_create(self, quantity=False):
        unprocessed_lines = self.browse()
        sale_line_purchase_map = {}
        for line in self:
            if line.vendor_id:
                sale_line_purchase_map.update(
                    super(
                        SaleOrderLine, line.with_context(force_vendor_sale_line=line)
                    )._purchase_service_create(quantity=quantity)
                )
            else:
                unprocessed_lines |= line
        process_map = super(SaleOrderLine, unprocessed_lines)._purchase_service_create(
            quantity=quantity
        )
        # Update vendor and price in lines with service_to_purchase products
        for so_line, purchase_line in process_map.items():
            vendor = purchase_line.order_id.partner_id
            if vendor:
                so_line.update(
                    {
                        "vendor_id": vendor.id,
                        "vendor_price_unit": purchase_line.price_unit,
                    }
                )
        sale_line_purchase_map.update(process_map)
        return sale_line_purchase_map

    def _get_vendor_qty(self):
        return self.product_uom_qty

    @api.depends("product_uom_qty", "vendor_id", "vendor_price_unit")
    def _compute_amount_vendor(self):
        for line in self.filtered("vendor_id"):
            line.vendor_price_subtotal = line._get_vendor_qty() * line.vendor_price_unit

    def _purchase_decrease_ordered_qty(self, new_qty, origin_values):
        # Remove PO lines and PO in draft state when qty to buy is zero
        pending_lines = self
        po_to_check = self.env["purchase.order"]
        if new_qty == 0.0:
            for line in self:
                po_lines = line.purchase_line_ids.filtered(lambda l: l.state == "draft")
                if po_lines:
                    po_to_check |= po_lines.mapped("order_id")
                    po_lines.unlink()
                    pending_lines -= line
            no_lines_po = po_to_check.filtered(lambda p: not p.order_line)
            no_lines_po.button_cancel()
            no_lines_po.unlink()
        super(SaleOrderLine, pending_lines)._purchase_decrease_ordered_qty(
            new_qty, origin_values
        )

    def _purchase_service_generation(self):
        # reprocess lines with vendor and without purchase
        sale_line_purchase_map = super()._purchase_service_generation()
        for line in self:
            if (
                line not in sale_line_purchase_map
                and line.vendor_id
                and not line.purchase_line_count
            ):
                sale_line_purchase_map.update(line._purchase_service_create())
        return sale_line_purchase_map

    def write(self, vals):
        res = super().write(vals)
        if "vendor_price_unit" in vals and not self.env.context.get(
            "write_from_purchase"
        ):
            self.mapped("purchase_line_ids").filtered(
                lambda pl: not pl.qty_invoiced
            ).with_context(write_from_sale=True).write(
                {"price_unit": vals["vendor_price_unit"]}
            )
        # Discard check state because related field compute don't come here
        if "vendor_id" in vals:
            to_process = self.browse()
            for line in self.filtered(lambda sol: sol.state == "sale"):
                line._purchase_decrease_ordered_qty(
                    0.0, {line.id: line.product_uom_qty}
                )
                # Force purchase service if vendor set line or product has
                # set service_to_purchase check
                if vals["vendor_id"] or line.product_id.service_to_purchase:
                    to_process |= line
            if to_process:
                to_process._purchase_service_create()
        return res
