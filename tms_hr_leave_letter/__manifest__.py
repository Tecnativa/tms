# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "TMS Hr Leave Letter",
    "summary": "Transport Management System (TMS) HR Leave Letter",
    "version": "13.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_holidays",
    ],
    "data": [
        "views/hr_leave_type_views.xml",
        "views/report_leave_letter.xml",
        "reports/tms_hr_leave_letter_report.xml",
    ],
}
