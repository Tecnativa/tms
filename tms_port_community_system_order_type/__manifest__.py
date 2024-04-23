# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Port Community System (PCS) Sale order type",
    "summary": "Port Community System (PCS) Sale order type",
    "version": "15.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "tms_port_community_system",
        "sale_order_type",
    ],
    "data": [
        "views/tms_pcs_view.xml",
    ],
    "maintainers": ["sergio-teruel", "carlosdauden"],
}
