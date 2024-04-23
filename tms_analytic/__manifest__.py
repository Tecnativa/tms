# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "TMS Analytic",
    "summary": "Analytic for Transport Management System (TMS)",
    "version": "15.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "analytic_tag_dimension",
        "tms_division",
    ],
    "data": [
        "views/project_task_view.xml",
        "views/fleet_view.xml",
    ],
    "maintainers": ["sergio-teruel", "carlosdauden"],
}
