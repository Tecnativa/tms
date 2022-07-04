# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardSaleLineHistoryPrice(models.TransientModel):
    _inherit = "wizard.sale.line.history.price"

    shipping_origin_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_shipping_place", "=", True)],
        context={"default_is_shipping_place": True,},
        string="Shipping Origin",
    )
    shipping_destination_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_shipping_place", "=", True)],
        context={"default_is_shipping_place": True,},
        string="Shipping Destination",
    )
    search_by_proximity = fields.Boolean()
    origin_proximity = fields.Integer()
    destination_proximity = fields.Integer()

    def _domain_sale_line(self):
        domain = super()._domain_sale_line()
        if self.shipping_origin_id:
            if self.search_by_proximity and self.origin_proximity:
                origin_prox = self.origin_proximity / 10.0
                domain.extend(
                    [
                        (
                            "shipping_origin_id.partner_latitude",
                            ">",
                            self.shipping_origin_id.partner_latitude - origin_prox,
                        ),
                        (
                            "shipping_origin_id.partner_latitude",
                            "<",
                            self.shipping_origin_id.partner_latitude + origin_prox,
                        ),
                        (
                            "shipping_origin_id.partner_longitude",
                            ">",
                            self.shipping_origin_id.partner_longitude - origin_prox,
                        ),
                        (
                            "shipping_origin_id.partner_longitude",
                            "<",
                            self.shipping_origin_id.partner_longitude + origin_prox,
                        ),
                    ]
                )
            else:
                domain.append(("shipping_origin_id", "=", self.shipping_origin_id.id))
        if self.shipping_destination_id:
            if self.search_by_proximity and self.destination_proximity:
                place_id = self.shipping_destination_id
                destination_prox = self.destination_proximity / 10.0
                domain.extend(
                    [
                        (
                            "shipping_destination_id.partner_latitude",
                            ">",
                            place_id.partner_latitude - destination_prox,
                        ),
                        (
                            "shipping_destination_id.partner_latitude",
                            "<",
                            place_id.partner_latitude + destination_prox,
                        ),
                        (
                            "shipping_destination_id.partner_longitude",
                            ">",
                            place_id.partner_longitude - destination_prox,
                        ),
                        (
                            "shipping_destination_id.partner_longitude",
                            "<",
                            place_id.partner_longitude + destination_prox,
                        ),
                    ]
                )
            else:
                domain.append(
                    ("shipping_destination_id", "=", self.shipping_destination_id.id)
                )
        return domain

    @api.depends(
        "partner_id",
        "product_id",
        "shipping_origin_id",
        "shipping_destination_id",
        "origin_proximity",
        "destination_proximity",
    )
    def _compute_sale_line_ids(self):
        return super()._compute_sale_line_ids()

    def _prepare_default_values(self, sale_line):
        res = super()._prepare_default_values(sale_line)
        res.update(
            {
                "shipping_origin_id": sale_line.shipping_origin_id.id,
                "shipping_destination_id": sale_line.shipping_destination_id.id,
            }
        )
        return res
