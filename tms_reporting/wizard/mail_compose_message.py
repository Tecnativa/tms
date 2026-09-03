# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models

TRANSPORT_ORDER_EMAIL_TEMPLATE_XMLID = "tms_reporting.transport_order_email"
TRANSPORT_ORDER_REPORT_XMLID = "tms_reporting.report_tms_transportation_order"


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _tms_attach_transport_order_pdf(self):
        """Generate a fresh Transport Order PDF and attach it to the outgoing
        email, right before it is actually sent (not on template preview).

        Only handles the single-task case: this wizard is meant to be used
        from a single project.task (the "Send Transport Order" action), and
        each task needs its own PDF, so a batch send is deliberately skipped.
        """
        template = self.env.ref(
            TRANSPORT_ORDER_EMAIL_TEMPLATE_XMLID, raise_if_not_found=False
        )
        if not template:
            return
        for wizard in self:
            res_ids = wizard.env.context.get("active_ids") or (
                [wizard.res_id] if wizard.res_id else []
            )
            if (
                wizard.template_id != template
                or wizard.model != "project.task"
                or len(res_ids) != 1
            ):
                continue
            report = wizard.env.ref(TRANSPORT_ORDER_REPORT_XMLID)
            report.with_context(
                tms_transport_order_skip_chatter_post=True
            )._render_qweb_pdf(res_ids=res_ids)
            attachment = wizard.env["ir.attachment"].search(
                [
                    ("res_model", "=", "project.task"),
                    ("res_id", "=", res_ids[0]),
                    ("name", "like", "Transport order%"),
                ],
                order="create_date desc, id desc",
                limit=1,
            )
            if attachment:
                wizard.attachment_ids = [(4, attachment.id)]

    def action_send_mail(self):
        self._tms_attach_transport_order_pdf()
        return super().action_send_mail()
