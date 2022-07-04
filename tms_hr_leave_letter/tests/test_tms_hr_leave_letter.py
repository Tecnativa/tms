# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date

from odoo.tests import Form, SavepointCase


class TestTmsHrLeaveLetter(SavepointCase):
    def test_print_leave_letter(self):
        user = self.env.user
        leave_type_form = Form(self.env["hr.leave.type"])
        leave_type_form.name = "Test Leave Type"
        leave_type_form.leave_letter_type = "holidays_leave"
        leave_type_form.responsible_id = user
        leave_type = leave_type_form.save()
        department = (
            self.env["hr.department"]
            .with_context(tracking_disable=True)
            .create({"name": "Department test"})
        )
        employee = self.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "user_id": user.id,
                "department_id": department.id,
            }
        )
        leave_form = Form(self.env["hr.leave"])
        leave_form.employee_id = employee
        leave_form.holiday_status_id = leave_type
        leave_form.request_date_from = date(2019, 9, 2)
        leave_form.request_date_to = date(2019, 9, 2)
        leave_form.request_unit_half = True
        leave_form.request_date_from_period = "am"
        leave = leave_form.save()
        self.env.ref("tms_hr_leave_letter.tms_hr_leave_letter").render_qweb_html(
            leave.ids
        )