# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import hashlib
import io
import re

from odoo import models

TRANSPORT_ORDER_REPORT_NAME = "tms_reporting.tms_transportation_order"

# The "dd-mm-yyyy hh:mm:ss" timestamps the report stamps on itself (footer
# sign date, stinsa_custom's stamp) must be excluded from the content
# fingerprint below, or it would never match between two prints even when
# nothing else changed.
_TIMESTAMP_RE = re.compile(rb"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}")


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _tms_transport_order_fingerprint(self, task_id, data):
        """Hash of the report's rendered HTML for one task, without a QR
        (no QR context is set for this probe render) and with the report's
        own timestamps blanked out, so it only changes when the underlying
        data actually changes.
        """
        html, _report_type = self._render_qweb_html([task_id], data=data)
        if isinstance(html, str):
            html = html.encode()
        html = _TIMESTAMP_RE.sub(b"", html)
        return hashlib.sha256(html).hexdigest()

    def _render_qweb_pdf(self, res_ids=None, data=None):
        if self.report_name != TRANSPORT_ORDER_REPORT_NAME or not res_ids:
            return super()._render_qweb_pdf(res_ids=res_ids, data=data)

        tasks = self.env["project.task"].browse(res_ids)
        pdf_by_task = {}
        fingerprints = {}
        tasks_to_generate = self.env["project.task"]
        for task in tasks:
            fingerprint = self._tms_transport_order_fingerprint(task.id, data)
            fingerprints[task.id] = fingerprint
            reusable = task.tms_transport_order_attachment_id
            if (
                reusable
                and reusable.exists()
                and task.tms_transport_order_fingerprint == fingerprint
            ):
                pdf_by_task[task.id] = base64.b64decode(reusable.sudo().datas)
            else:
                tasks_to_generate += task

        if tasks_to_generate:
            attachments = tasks_to_generate._tms_transport_order_prepare_attachments()
            qr_urls = {
                task_id: attachment._tms_qr_download_url()
                for task_id, attachment in attachments.items()
            }
            for task in tasks_to_generate:
                pdf_content, _report_type = super(
                    IrActionsReport,
                    self.with_context(tms_transport_order_qr_urls=qr_urls),
                )._render_qweb_pdf(res_ids=[task.id], data=data)
                pdf_by_task[task.id] = pdf_content
            tasks_to_generate._tms_transport_order_finalize_attachments(
                attachments, pdf_by_task, fingerprints
            )

        if len(pdf_by_task) == 1:
            return list(pdf_by_task.values())[0], "pdf"
        streams = [io.BytesIO(pdf_by_task[task.id]) for task in tasks]
        return self._merge_pdfs(streams), "pdf"
