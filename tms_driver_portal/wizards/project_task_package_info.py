# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTaskPackageInfoWiz(models.TransientModel):
    _name = "project.task.package.info.wiz"
    _description = "Fill project task packages wizard"

    checkpoint_id = fields.Many2one(comodel_name="project.task.checkpoint")
    line_ids = fields.One2many(
        comodel_name="project.task.package.line.info.wiz", inverse_name="wizard_id"
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if (
            self.env.context.get("active_id")
            and self.env.context.get("active_model") == "project.task.checkpoint"
        ):
            checkpoint = self.env["project.task.checkpoint"].browse(
                self.env.context.get("active_id")
            )
            if checkpoint.exists() and checkpoint.package_origin_ids:
                res.update(
                    {
                        "line_ids": [
                            (0, 0, {"package_id": p.id})
                            for p in checkpoint.package_origin_ids
                        ]
                    }
                )
        return res

    def action_apply(self):
        return True


class ProjectTaskPackageLineInfoWiz(models.TransientModel):
    _name = "project.task.package.line.info.wiz"
    _description = "Package lines for project task packages wizard"

    wizard_id = fields.Many2one(
        comodel_name="project.task.package.info.wiz", required=True
    )
    package_id = fields.Many2one(comodel_name="tms.package", required=True)
    carrier_tracking_ref = fields.Char(
        related="package_id.carrier_tracking_ref", string="Ref."
    )
    shipping_weight = fields.Float(
        related="package_id.shipping_weight",
        readonly=False,
        string="Weight",
        related_sudo=True,
    )
    shipping_volume = fields.Float(
        related="package_id.shipping_volume",
        readonly=False,
        string="Volume",
        related_sudo=True,
    )
