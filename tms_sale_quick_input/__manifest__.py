# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "TMS Sale Order Quick Input",
    "summary": "",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "tms",
        "sale_order_line_input",
    ],
    "data": [
        "views/sale_view.xml",
    ],
    "maintainers": ["sergio-teruel", "carlosdauden"],
}
