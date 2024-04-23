# Copyright 2018 Carlos Dauden - <carlos.dauden@tecnativa.com>
# Copyright 2018 Sergio Teruel - <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "TMS Analytic Distribution",
    "summary": "Adds analytic fields in analytic distribution",
    "version": "15.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "analytic",
        "tms",
    ],
    "data": [
        "views/account_analytic_distribution_view.xml",
    ],
    "installable": True,
    "maintainers": ["sergio-teruel", "carlosdauden"],
}
