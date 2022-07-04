# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardSaleLineHistoryPrice(models.TransientModel):
    _name = "wizard.sale.line.history.price"
    _description = "Wizard to show sale line history prices"

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        default=lambda x: x.env.context.get("active_id", False),
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    sale_line_ids = fields.One2many(
        comodel_name="sale.order.line",
        compute="_compute_sale_line_ids",
        # inverse=lambda x: x,
        string="Price History",
    )

    def _domain_sale_line(self):
        domain = [("id", "!=", self.sale_line_id.id)]
        if self.product_id:
            domain.append(("product_id", "=", self.product_id.id))
        if self.partner_id:
            domain.append(("order_partner_id", "=", self.partner_id.id))
        return domain

    @api.depends("partner_id", "product_id")
    def _compute_sale_line_ids(self):
        SaleOrderLine = self.env["sale.order.line"]
        for wiz in self:
            wiz.sale_line_ids = SaleOrderLine.search(
                wiz._domain_sale_line(), limit=15, order="id DESC"
            )

    def _prepare_default_values(self, sale_line):
        return {
            "partner_id": sale_line.order_partner_id.id,
            "product_id": sale_line.product_id.id,
        }

    @api.onchange("sale_line_id")
    def _onchage_sale_line_id(self):
        for wiz in self:
            wiz.update(wiz._prepare_default_values(wiz.sale_line_id))
