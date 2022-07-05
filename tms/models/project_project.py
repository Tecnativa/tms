# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def _get_shipment_type_selection(self):
        return [("maritime", "Maritime")]

    shipment_type = fields.Selection(
        selection=lambda x: x._get_shipment_type_selection(), string="Shipment Type"
    )
    shipper_id = fields.Many2one(
        comodel_name="res.partner",
        string="Shipper",
    )
    consigner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Consigner",
    )
    freight_forwarder_id = fields.Many2one(
        comodel_name="res.partner", string="Freight Forwarder"
    )
    shipment_ref = fields.Char(string="Shipment Ref.")
    load_harbor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Load Harbor",
    )
    load_terminal = fields.Char(string="Load Terminal")
    discharge_harbor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Discharge Harbor",
    )
    discharge_terminal = fields.Char(string="Discharge Terminal")
    vessel = fields.Char(string="Vessel")
    vessel_flag = fields.Char(string="Vessel Flag")
