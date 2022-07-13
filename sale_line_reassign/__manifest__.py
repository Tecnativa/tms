# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Line Reassign",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale_timesheet",
    ],
    "data": [
        "wizards/sale_line_reassign_view.xml",
    ],
}
