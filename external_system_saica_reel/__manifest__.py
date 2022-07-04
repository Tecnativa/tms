# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "External System Saica Reel",
    "summary": "External System Saica Reel",
    "version": "13.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base_external_system",
        "base_geolocalize",
        "crm_claim_type",
        "queue_job",
        "sale_stock",
        "tms",
    ],
    "external_dependencies": {"python": ["dicttoxml", "xmltodict", "zeep",],},
    "data": [
        "security/ir.model.access.csv",
        "data/external_system_saica_reel.xml",
        "data/product_data.xml",
        "data/crm_claim_type.xml",
        "views/external_system_view.xml",
        "views/res_partner_view.xml",
        "views/stock_picking_view.xml",
        "views/crm_claim_view.xml",
    ],
}
