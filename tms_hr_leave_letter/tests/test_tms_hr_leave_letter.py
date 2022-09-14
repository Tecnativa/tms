# Copyright 2021 Tecnativa - Carlos Roca
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date

from odoo.tests import Form, TransactionCase, new_test_user
from odoo.tests.common import users


class TestTmsHrLeaveLetter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(cls.env, login="test-user")
        cls.leave_type = cls._create_leave_type(cls)
        cls.department_model = cls.env["hr.department"].with_context(
            tracking_disable=True
        )
        cls.department = cls.department_model.create({"name": "Department test"})
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "user_id": cls.user.id,
                "department_id": cls.department.id,
            }
        )

    def _create_leave_type(self):
        leave_type_form = Form(self.env["hr.leave.type"])
        leave_type_form.name = "Test Leave Type"
        leave_type_form.leave_letter_type = "holidays_leave"
        leave_type_form.responsible_id = self.user
        leave_type_form.requires_allocation = "no"
        return leave_type_form.save()

    def _create_leave(self):
        leave_form = Form(
            self.env["hr.leave"].with_context(default_employee_id=self.employee.id)
        )
        leave_form.holiday_status_id = self.leave_type
        leave_form.request_date_from = date(2019, 9, 2)
        leave_form.request_date_to = date(2019, 9, 2)
        leave_form.request_unit_half = True
        leave_form.request_date_from_period = "am"
        return leave_form.save()

    @users("test-user")
    def test_create_leave_letter(self):
        leave = self._create_leave()
        self.assertEqual(leave.employee_id, self.employee)

    def test_print_leave_letter(self):
        leave = self._create_leave()
        report = self.env["ir.actions.report"]._get_report_from_name(
            "tms_hr_leave_letter.report_tms_hr_leave_letter"
        )
        res = report._render_qweb_html(leave.ids)[0].decode("utf-8").split("\n")
        self.assertRegex(str(res), self.employee.name)
