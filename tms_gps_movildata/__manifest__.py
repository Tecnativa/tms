# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "TMS GPS Moviltada",
    "summary": "TMS GPS Moviltada",
    "version": "10.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": False,
    "external_dependencies": {"python": ["zeep",],},
    "depends": ["tms", "base_external_system",],
    "data": [
        "security/ir.model.access.csv",
        "data/tms_gps_movildata.xml",
        "views/external_system_view.xml",
    ],
}
