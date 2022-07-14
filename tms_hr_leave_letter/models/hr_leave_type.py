# Copyright 2018-2020 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    leave_letter_type = fields.Selection(
        selection=[
            ("sick_leave", "Sick Leave"),
            ("holidays_leave", "Holidays Leave"),
            ("rest_leave", "Rest Leave"),
            ("no_regulation_leave", "No Regulation Leave"),
            ("do_other_work", "Do other work"),
            ("available", "Was available"),
        ],
    )
