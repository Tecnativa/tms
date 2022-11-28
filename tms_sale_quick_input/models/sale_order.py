# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        """default_type_id passed in context do not work because type_id is a field
        computed, writable and has a default method.
        So we force inject into vals.
        """
        if "type_id" not in vals and "default_type_id" in self.env.context:
            vals["type_id"] = self.env.context["default_type_id"]
        return super(SaleOrder, self).create(vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    shipping_place_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_shipping_place", "=", True)],
        string="Place",
        context={
            "default_is_shipping_place": True,
            "partner_show_only_name": True,
        },
        compute="_compute_shipping_place_id",
        readonly=False,
    )
    # Related with sale_order
    client_order_ref = fields.Char(
        related="order_id.client_order_ref",
        string="Customer Ref.",
        readonly=False,
    )
    release_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.release_id",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
            "partner_show_only_name": True,
        },
        string="Release",
        readonly=False,
    )
    acceptance_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.acceptance_id",
        domain=[("is_shipping_place", "=", True)],
        context={
            "default_is_shipping_place": True,
            "partner_show_only_name": True,
        },
        string="Acceptance",
        readonly=False,
    )
    # Related with tms_package_ids
    shipping_volume = fields.Float(
        digits="TMS Volume",
        string="Volume for Shipping",
        compute="_compute_shipping_volume",
        inverse="_inverse_shipping_volume",
    )
    shipping_weight = fields.Float(
        digits="TMS Weight",
        string="Weight for Shipping",
        compute="_compute_shipping_weight",
        inverse="_inverse_shipping_weight",
    )
    number_of_packages = fields.Integer(
        string="Number of Packages",
        compute="_compute_number_of_packages",
        inverse="_inverse_number_of_packages",
    )
    pallet_qty = fields.Integer(
        string="Pallets",
        compute="_compute_pallet_qty",
        inverse="_inverse_pallet_qty",
    )
    euro_pallet_qty = fields.Integer(
        string="Euro Pallets",
        compute="_compute_euro_pallet_qty",
        inverse="_inverse_euro_pallet_qty",
    )
    goods_id = fields.Many2one(
        comodel_name="tms.goods",
        string="Goods",
        ondelete="restrict",
        related="tms_package_ids.goods_id",
        readonly=False,
    )
    carrier_tracking_ref = fields.Char(
        string="Tracking Reference",
        compute="_compute_carrier_tracking_ref",
        inverse="_inverse_carrier_tracking_ref",
    )
    note = fields.Text(
        string="Comments",
        related="tms_package_ids.note",
        readonly=False,
    )
    requested_date = fields.Datetime(
        string="Requested Date",
        related="tms_package_ids.requested_date",
        readonly=False,
    )
    customer_ref = fields.Char(
        related="tms_package_ids.customer_ref",
        string="Package Ref.",
        readonly=False,
    )
    unload_service = fields.Boolean(
        string="Unload",
        related="order_id.unload_service",
        readonly=False,
    )
    editable_package_rel = fields.Boolean(compute="_compute_editable_package_rel")
    sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        related="order_id.type_id",
        readonly=False,
    )
    shipping_company_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.shipping_company_id",
        readonly=False,
    )
    final_destination_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.final_destination_id",
        readonly=False,
    )

    # unload_service not included to avoid compute shipping_place_id before
    # _onchange_unload_service assignaments
    @api.depends("shipping_origin_id", "shipping_destination_id")
    def _compute_shipping_place_id(self):
        for line in self:
            line.shipping_place_id = (
                line.unload_service
                and line.shipping_destination_id
                or line.shipping_origin_id
            )

    @api.depends("tms_package_ids.shipping_volume")
    def _compute_shipping_volume(self):
        self.get_field_from_packages_numeric("shipping_volume")

    def _inverse_shipping_volume(self):
        self.set_field_to_packages("shipping_volume")

    @api.depends("tms_package_ids.shipping_weight")
    def _compute_shipping_weight(self):
        self.get_field_from_packages_numeric("shipping_weight")

    def _inverse_shipping_weight(self):
        self.set_field_to_packages("shipping_weight")

    @api.depends("tms_package_ids.number_of_packages")
    def _compute_number_of_packages(self):
        self.get_field_from_packages_numeric("number_of_packages")

    def _inverse_number_of_packages(self):
        self.set_field_to_packages("number_of_packages")

    @api.depends("tms_package_ids.pallet_qty")
    def _compute_pallet_qty(self):
        self.get_field_from_packages_numeric("pallet_qty")

    def _inverse_pallet_qty(self):
        self.set_field_to_packages("pallet_qty")

    @api.depends("tms_package_ids.euro_pallet_qty")
    def _compute_euro_pallet_qty(self):
        self.get_field_from_packages_numeric("euro_pallet_qty")

    def _inverse_euro_pallet_qty(self):
        self.set_field_to_packages("euro_pallet_qty")

    @api.depends("tms_package_ids.carrier_tracking_ref")
    def _compute_carrier_tracking_ref(self):
        self.get_field_from_packages_text("carrier_tracking_ref")

    def _inverse_carrier_tracking_ref(self):
        self.set_field_to_packages("carrier_tracking_ref")

    @api.depends("tms_package_ids")
    def _compute_editable_package_rel(self):
        for line in self:
            line.editable_package_rel = not len(line.tms_package_ids) > 1

    def get_field_from_packages_text(self, field_name):
        for line in self:
            ref_list = []
            for package in line.tms_package_ids:
                if package[field_name]:
                    ref_list.append(package[field_name])
            line[field_name] = ", ".join(ref_list)

    def get_field_from_packages_numeric(self, field_name):
        for line in self:
            line[field_name] = sum(line.tms_package_ids.mapped(field_name))

    def set_field_to_packages(self, field_name):
        for line in self:
            if not line[field_name]:
                continue
            if len(line.tms_package_ids) == 1:
                line.tms_package_ids[field_name] = line[field_name]
            else:
                raise UserError(_("Go to packages to change data %s") % field_name)

    @api.onchange("unload_service")
    def _onchange_unload_service(self):
        for line in self:
            if line.unload_service:
                line.shipping_destination_id = line.shipping_place_id
                line.shipping_origin_id = line.release_id
            else:
                line.shipping_origin_id = line.shipping_place_id
                line.shipping_destination_id = line.acceptance_id

    @api.onchange("release_id")
    def _onchange_release_id(self):
        if self.unload_service:
            self.shipping_origin_id = self.release_id

    @api.onchange("acceptance_id")
    def _onchange_acceptance_id(self):
        if not self.unload_service:
            self.shipping_destination_id = self.acceptance_id

    def _update_package(self):
        if not self.carrier_tracking_ref and not self.goods_id:
            return
        packages = self.tms_package_ids
        vals = {
            "shipping_origin_id": self.shipping_origin_id.id,
            "shipping_destination_id": self.shipping_destination_id.id,
            "carrier_tracking_ref": self.carrier_tracking_ref,
            "goods_id": self.goods_id.id,
        }
        if not packages:
            vals.update(
                {
                    "name": "/",
                    "partner_id": self.order_partner_id.id,
                    "pickup_date": self.pickup_date,
                }
            )
            packages = packages.create(vals)
            self.tms_package_ids = packages
        else:
            packages.write(vals)

    # Use onchange instead of inverse to avoid this https://github.com/odoo/odoo/blob/
    # 4c2d3e1bd07ab17e5e45796e2ec7da962d93bea0/odoo/models.py#L3846-L3858
    @api.onchange("shipping_place_id")
    def onchange_shipping_place_id(self):
        if self.unload_service:
            self.shipping_destination_id = self.shipping_place_id
        else:
            self.shipping_origin_id = self.shipping_place_id
        self._update_package()

    @api.onchange("customer_ref")
    def onchange_customer_ref(self):
        self._update_package()

    @api.onchange("carrier_tracking_ref")
    def onchange_carrier_tracking_ref(self):
        self._update_package()

    @api.onchange("sale_type_id")
    def onchange_sale_type_id(self):
        self.order_id.onchange_type_id()

    @api.onchange("goods_id")
    def onchange_goods_id(self):
        self._update_package()

    @api.onchange("order_partner_id")
    def _onchange_order_partner_id(self):
        """The module sal_line_quick_input not depends on sale_order_type, in
        create method of sale order has not type_id in vals.
        """
        return super(
            SaleOrderLine,
            self.with_context(default_type_id=self.order_partner_id.sale_type.id),
        )._onchange_order_partner_id()

    def write(self, vals):
        res = super().write(vals)
        if "final_destination_id" in vals:
            orders = self.mapped("order_id")
            for order in orders:
                order.onchange_final_destination_id()
            # Recompute taxes when the fiscal position is changed on the SO
            orders._compute_tax_id()
        return res
