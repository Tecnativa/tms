# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    vendor_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_line_id.vendor_id",
        string="Vendor",
        copy=False,
        context={
            "default_supplier_rank": 1,
            "default_customer_rank": 0,
        },
        readonly=False,
        store=True,
    )

    def _tms_transport_order_attachment_name(self):
        self.ensure_one()
        order_name = self.sale_line_id.order_id.name or self.name
        timestamp = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return "%s - %s - %s.pdf" % (
            _("Transport order"),
            order_name,
            timestamp.strftime("%Y%m%d%H%M%S"),
        )

    def _tms_transport_order_prepare_attachments(self):
        """Pre-create one placeholder attachment per task, before the report
        is rendered, so its id/access_token are already known and the QWeb
        template can embed a QR pointing to its own future download URL.
        """
        attachment_model = self.env["ir.attachment"].sudo()
        attachments = {}
        for task in self:
            attachment = attachment_model.create(
                {
                    "name": task._tms_transport_order_attachment_name(),
                    "res_model": "project.task",
                    "res_id": task.id,
                    "type": "binary",
                    "raw": b" ",
                }
            )
            attachment.generate_access_token()
            attachments[task.id] = attachment
        return attachments

    def _tms_transport_order_finalize_attachments(self, attachments, pdf_by_task):
        """Fill each pre-created attachment with the actual rendered PDF.

        Only posts it to the task's chatter thread when the report was
        generated to be printed. When it is generated to be emailed
        (``tms_transport_order_skip_chatter_post`` in context), the outgoing
        email itself already logs a chatter message with the attachment, so
        posting it here too would show it twice.
        """
        skip_chatter_post = self.env.context.get(
            "tms_transport_order_skip_chatter_post"
        )
        for task in self:
            attachment = attachments.get(task.id)
            pdf_content = pdf_by_task.get(task.id)
            if not attachment or not pdf_content:
                continue
            attachment.sudo().write({"raw": pdf_content})
            if not skip_chatter_post:
                task.message_post(
                    body=_("Transport order generated."),
                    attachment_ids=[attachment.id],
                )
