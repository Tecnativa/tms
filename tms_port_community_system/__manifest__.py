# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Port Community System (PCS)",
    "summary": "Port Community System (PCS)",
    "version": "15.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "tms",
        "tms_sale_quick_input",
    ],
    "external_dependencies": {"python": ["suds-bis"]},
    "data": [
        "security/ir.model.access.csv",
        "data/tms_port_community_system_data.xml",
        "views/tms_pcs_view.xml",
        "views/sale_order_view.xml",
    ],
    "maintainers": ["sergio-teruel", "carlosdauden"],
}
