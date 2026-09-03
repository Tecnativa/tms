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
            if wizard.template_id != template or wizard.model != "project.task":
                continue
            res_ids = wizard._evaluate_res_ids()
            if len(res_ids) != 1:
                continue
            wizard.env["ir.actions.report"].with_context(
                tms_transport_order_skip_chatter_post=True
            )._render_qweb_pdf(TRANSPORT_ORDER_REPORT_XMLID, res_ids=res_ids)
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

    def _action_send_mail(self, auto_commit=False):
        self._tms_attach_transport_order_pdf()
        return super()._action_send_mail(auto_commit=auto_commit)
