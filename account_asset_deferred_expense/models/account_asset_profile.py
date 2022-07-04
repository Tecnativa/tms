# Copyright 2018-2021 Carlos Dauden - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"

    is_expense_type = fields.Boolean(string="Is expense type",)

    @api.onchange("account_asset_id")
    def onchange_account_asset_id(self):
        if self.is_expense_type:
            self.account_depreciation_id = self.account_asset_id

    @api.onchange("is_expense_type")
    def onchange_is_expense_type(self):
        if self.is_expense_type:
            self.update(
                {"method_period": "month", "method_number": 12, "open_asset": True}
            )
