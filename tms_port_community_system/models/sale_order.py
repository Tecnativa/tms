# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pcs_message_number = fields.Char()
    pcs_message_function = fields.Selection(
        [
            ("ORIGINAL", "ORIGINAL"),
            ("REPLACE", "REPLACE"),
            ("CANCELLATION", "CANCELLATION"),
            ("CHANGE_ITD", "CHANGE_ITD"),
            ("CHANGE_REL_CONF", "CHANGE_REL_CONF"),
            ("CHANGE_ACC_CONF", "CHANGE_ACC_CONF"),
            ("CHANGE_RO_IN", "CHANGE_RO_IN"),
            ("CHANGE_AO_IN", "CHANGE_AO_IN"),
            ("CHANGE_ROAO_IN", "CHANGE_ROAO_IN"),
            ("CHANGE_RO_OUT", "CHANGE_RO_OUT"),
            ("CHANGE_AO_OUT", "CHANGE_AO_OUT"),
            ("CHANGE_ROAO_OUT", "CHANGE_ROAO_OUT"),
        ],
        string="Last PCS Message",
    )

    def reprocess_attach_file(self):
        IrAttachment = self.env["ir.attachment"]
        pcs_backend = self.env["tms.pcs.backend"].search(
            [
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        for order in self:
            attachment = IrAttachment.search(
                [
                    ("res_model", "=", "sale.order"),
                    ("res_id", "=", order.id),
                ],
                order="name DESC",
            )[:1]
            pcs_backend.with_context(pcs_skip_store_attachment=True)._create_sale_order(
                attachment.datas,
                attachment.name,
                base64.b64decode(attachment.datas),
                "",
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pcs_item_number = fields.Integer()
    pcs_message_function = fields.Selection(
        related="order_id.pcs_message_function",
    )
