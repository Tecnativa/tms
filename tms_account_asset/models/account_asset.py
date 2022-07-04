# Copyright 2018-2020 Carlos Dauden - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAsset(models.Model):
    _inherit = ["account.asset", "tms.analytic"]
    _name = "account.asset"


class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"

    def _setup_move_line_data(self, depreciation_date, account, ml_type, move):
        vals = super()._setup_move_line_data(depreciation_date, account, ml_type, move)
        vals.update(
            {
                "tractor_id": self.asset_id.tractor_id.id,
                "trailer_id": self.asset_id.trailer_id.id,
                # "driver_id": self.asset_id.driver_id.id,
                "partner_id": self.asset_id.driver_id.id,
            }
        )
        return vals
