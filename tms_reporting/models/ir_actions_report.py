# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import hashlib
import io
import re

from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import fields, models

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

    def _tms_pdf_datetime(self, value):
        """Format a naive UTC datetime as a PDF date string in the acting
        user's timezone (same ``context_timestamp`` used for the attachment
        name in ``project_task._tms_transport_order_attachment_name``), so
        the metadata reads the local time the document was signed, not UTC.
        """
        localized = fields.Datetime.context_timestamp(self, value)
        offset_minutes = int(localized.utcoffset().total_seconds() // 60)
        sign = "+" if offset_minutes >= 0 else "-"
        hours, minutes = divmod(abs(offset_minutes), 60)
        return "D:%s%s%02d'%02d'" % (
            localized.strftime("%Y%m%d%H%M%S"),
            sign,
            hours,
            minutes,
        )

    def _tms_stamp_pdf_dates(self, pdf_content, creation_date, mod_date):
        """Overwrite /CreationDate and /ModDate on the rendered PDF.

        wkhtmltopdf only stamps /CreationDate, and stamps it with the render
        time of this particular snapshot rather than the task's original
        document date. The BOE electronic transport-document rules require
        both dates: /CreationDate must stay the time of the very first PDF
        generated for the task, /ModDate must be the time of the snapshot
        being generated now. Only this report needs this.
        """
        reader = PdfFileReader(io.BytesIO(pdf_content))
        info = reader.getDocumentInfo() or {}
        metadata = {str(key): str(value) for key, value in info.items()}
        metadata["/CreationDate"] = self._tms_pdf_datetime(creation_date)
        metadata["/ModDate"] = self._tms_pdf_datetime(mod_date)
        writer = PdfFileWriter()
        for page_number in range(reader.getNumPages()):
            writer.addPage(reader.getPage(page_number))
        writer.addMetadata(metadata)
        buffer = io.BytesIO()
        writer.write(buffer)
        return buffer.getvalue()

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
            now = fields.Datetime.now()
            creation_dates = {}
            for task in tasks_to_generate:
                pdf_content, _report_type = super(
                    IrActionsReport,
                    self.with_context(tms_transport_order_qr_urls=qr_urls),
                )._render_qweb_pdf(res_ids=[task.id], data=data)
                creation_date = task.tms_transport_order_creation_date or now
                creation_dates[task.id] = creation_date
                pdf_by_task[task.id] = self._tms_stamp_pdf_dates(
                    pdf_content, creation_date, now
                )
            tasks_to_generate._tms_transport_order_finalize_attachments(
                attachments, pdf_by_task, fingerprints, creation_dates
            )

        if len(pdf_by_task) == 1:
            return list(pdf_by_task.values())[0], "pdf"
        streams = [io.BytesIO(pdf_by_task[task.id]) for task in tasks]
        return self._merge_pdfs(streams), "pdf"
