# Copyright 2018-2020 Carlos Dauden - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    is_expense_type = fields.Boolean(string="Is expense type",)

    @api.model
    def create(self, vals):
        profile = self.env["account.asset.profile"].browse(vals["profile_id"])
        vals["is_expense_type"] = profile.is_expense_type
        return super().create(vals)
