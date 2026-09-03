# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io

from odoo import models

TRANSPORT_ORDER_REPORT_NAME = "tms_reporting.tms_transportation_order"


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, res_ids=None, data=None):
        if self.report_name != TRANSPORT_ORDER_REPORT_NAME or not res_ids:
            return super()._render_qweb_pdf(res_ids=res_ids, data=data)
        tasks = self.env["project.task"].browse(res_ids)
        attachments = tasks._tms_transport_order_prepare_attachments()
        qr_urls = {
            task_id: attachment._tms_qr_download_url()
            for task_id, attachment in attachments.items()
        }
        pdf_by_task = {}
        for task in tasks:
            pdf_content, _report_type = super(
                IrActionsReport, self.with_context(tms_transport_order_qr_urls=qr_urls)
            )._render_qweb_pdf(res_ids=[task.id], data=data)
            pdf_by_task[task.id] = pdf_content
        tasks._tms_transport_order_finalize_attachments(attachments, pdf_by_task)
        if len(pdf_by_task) == 1:
            return list(pdf_by_task.values())[0], "pdf"
        streams = [io.BytesIO(pdf) for pdf in pdf_by_task.values()]
        return self._merge_pdfs(streams), "pdf"
