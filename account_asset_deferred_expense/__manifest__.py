# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Asset Deferred Expense",
    "summary": "This module extends asset to allow deferred expenses",
    "version": "13.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["account_asset_management",],
    "data": [
        "views/account_asset_profile_views.xml",
        "views/account_asset_views.xml",
        "wizards/asset_depreciation_confirmation_wizard_views.xml",
    ],
    "uninstall_hook": "uninstall_hook",
}
