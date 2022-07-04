# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    """ Remove domain added in account_asset_management actions """
    env = api.Environment(cr, SUPERUSER_ID, {})
    action = env.ref("account_asset_management.account_asset_profile_action")
    action.domain = []
    action = env.ref("account_asset_management.account_asset_action")
    action.domain = []
