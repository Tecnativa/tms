# Copyright 2017-2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    tms_print_template_id = fields.Many2one(
        comodel_name="tms.print.template", string="Print Template",
    )
