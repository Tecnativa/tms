# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Order Line Vendor",
    "summary": "Get vendor and cost directly from sale order line",
    "version": "15.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_purchase",
    ],
    "data": [
        "views/product_view.xml",
        "views/purchase_view.xml",
        "views/sale_view.xml",
    ],
    "maintainers": ["sergio-teruel", "carlosdauden"],
}
