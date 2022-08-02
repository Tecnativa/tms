# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "TMS Website Reporting",
    "summary": "Transport Management System Reporting(TMS)",
    "version": "13.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "tms",
        "hr_holidays",
        "website",
    ],
    "data": [
        "views/assets.xml",
        "views/website_tms_reporting_driver_template.xml",
        "views/website_tms_reporting_equipment_template.xml",
        "views/res_partner_view.xml",
        "views/tms_equipment_view.xml",
        "views/website_tms_reporting_views.xml",
    ],
}
