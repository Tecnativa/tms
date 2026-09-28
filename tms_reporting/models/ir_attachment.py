# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _tms_qr_download_url(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return "%s/web/content/%s?access_token=%s&download=true" % (
            base_url,
            self.id,
            self.access_token,
        )
