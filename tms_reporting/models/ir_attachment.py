# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _tms_qr_download_url(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return (
            f"{base_url}/web/content/{self.id}"
            f"?access_token={self.access_token}&download=true"
        )
