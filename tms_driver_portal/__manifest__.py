# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "TMS Driver Portal",
    "summary": "Access portal to TMS Self employee drivers",
    "version": "15.0.1.0.0",
    "category": "Transport Management system",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "portal",
        "tms",
    ],
    "data": [
        # TODO: Try remove for display in views portal
        "security/ir.model.access.csv",
        # Keep order
        "views/portal_templates.xml",
        "views/project_task_views.xml",
        "views/project_sharing_views.xml",
        "views/project_sharing_templates.xml",
        "wizards/project_task_equipment_views.xml",
        "wizards/project_task_package_info_views.xml",
    ],
    "maintainers": ["sergio-teruel", "carlosdauden"],
}
