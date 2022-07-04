# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "TMS Sale Price From History",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_price_from_history", "tms",],
    "data": ["views/product_view.xml", "wizards/wizard_price_history_view.xml",],
    "auto_install": True,
}
