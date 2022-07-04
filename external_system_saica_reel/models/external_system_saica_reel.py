# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from collections import defaultdict

import dicttoxml
import pytz
import xmltodict
from lxml import objectify
from requests import Session
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import ormcache

_logger = logging.getLogger(__name__)


class ExternalSystem(models.Model):
    _inherit = "external.system"

    saica_reel_adapter_ids = fields.One2many(
        comodel_name="external.system.saica.reel",
        inverse_name="system_id",
        string="Adapter",
    )


class ExternalSystemSaicaReel(models.Model):
    _name = "external.system.saica.reel"
    _inherit = "external.system.adapter"
    _description = "External System Saica reel"
    _sn_lenght = 7

    @api.model
    def _default_incoming_picking_type_id(self):
        picking_type = self.env.ref(
            "external_system_saica_reel.picking_type_saica_reel_in"
        )
        return picking_type

    @api.model
    def _default_outgoing_picking_type_id(self):
        picking_type = self.env.ref(
            "external_system_saica_reel.picking_type_saica_reel_out"
        )
        return picking_type

    last_time_log = fields.Datetime(
        string="Last time log", default="2017-09-01 00:00:00",
    )
    # For receptions
    incoming_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type Receptions",
        required=True,
        default=_default_incoming_picking_type_id,
    )
    # For expeditions
    outgoing_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type Expeditions",
        required=True,
        default=_default_outgoing_picking_type_id,
    )
    saica_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Stock Location",
        default=lambda x: x.env.ref(
            "external_system_saica_reel.stock_location_saica_reel"
        ).id,
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner",)
    # Product for make so lines in expeditions pickings
    order_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product for sale orders",
        domain=[("type", "=", "service")],
    )
    shipping_origin_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_shipping_place", "=", True)],
        string="Shipping Origin",
        context={"default_is_shipping_place": True,},
    )
    saica_company = fields.Char(default="100")
    saica_warehouse = fields.Char(default="8")
    saica_delivered_from = fields.Char(default="8")
    saica_delivered_to = fields.Char(default="17903")

    def external_get_client(self):
        """Return a usable client representing the remote system."""
        super().external_get_client()
        session = Session()
        session.verify = False
        transport = Transport(session=session)
        client = Client(self.host, transport=transport)
        return client

    def external_destroy_client(self, client):
        """Perform any logic necessary to destroy the client connection.

        Args:
            client (mixed): The client that was returned by
             ``external_get_client``.
        """
        super().external_destroy_client(client)
        # TODO: Implement

    def external_test_connection(self):
        """Adapters should override this method, then call super if valid.

        If the connection is invalid, adapters should raise an instance of
        ``odoo.ValidationError``.

        Raises:
            odoo.exceptions.UserError: In the event of a good connection.
        """
        client = self.external_get_client()
        with client.options(raw_response=True):
            response = client.service.GetPendingReceptionsList(
                self.username, self.password, self.saica_company
            )
            _logger.info(response.content)
            if response.status_code != 200:
                raise ValidationError(_("Connection Failed"))
        super().external_test_connection()

    @api.model
    @ormcache("external_ref")
    def get_destination(self, external_ref, name=None):
        Partner = self.env["res.partner"]
        partner = Partner.search([("saica_reel_ref", "=", external_ref)])
        if not partner:
            partner = Partner.create(
                {"saica_reel_ref": external_ref, "name": name, "is_company": True,}
            )
        return partner

    @api.model
    @ormcache("key")
    def get_product_attribute(self, key):
        attribute = self.env.ref(
            "external_system_saica_reel.product_attribute_%s" % key
        )
        return attribute

    @api.model
    @ormcache()
    def get_product_template_saica(self):
        return self.env.ref("external_system_saica_reel.product_template_saica_reel")

    def create_variant(self, product_tmpl, p_attribute_values, **kwargs):
        Product = self.env["product.product"]
        product = Product.create(
            {
                "product_tmpl_id": product_tmpl.id,
                "product_template_attribute_value_ids": [
                    (4, x.ids) for x in p_attribute_values
                ],
                "default_code": "%s%s%s%s"
                % (
                    kwargs["papercode"],
                    kwargs["basisweight"],
                    kwargs["width"].replace(".", ""),
                    kwargs["diameter"],
                ),
            }
        )
        ProductAttributeLine = self.env["product.template.attribute.line"]
        attributes = self.env["product.attribute"]
        for key in kwargs:
            attributes |= self.get_product_attribute(key)
        for attribute in attributes:
            values = p_attribute_values.filtered(lambda x: x.attribute_id == attribute)
            values_to_add = values - product.attribute_line_ids.mapped("value_ids")
            for new_value in values_to_add:
                product_attribute = product.attribute_line_ids.filtered(
                    lambda x: x.attribute_id == new_value.attribute_id
                )
                if not product_attribute:
                    vals = attribute._convert_to_write(attribute._cache)
                    _logger.debug(vals)
                    ProductAttributeLine.create(
                        {
                            "product_tmpl_id": product_tmpl.id,
                            "attribute_id": attribute.id,
                            "value_ids": [(4, new_value.id)],
                        }
                    )
                else:
                    product_attribute.value_ids = [(4, new_value.id)]
        return product

    def get_product_from_attributes(self, **kwargs):
        """
        kwards: attributte values dictionay
        :return:
        """
        ProductAttributeValue = self.env["product.attribute.value"]
        product_tmpl = self.get_product_template_saica()
        attribute_value_ids = []
        p_attribute_values = ProductAttributeValue
        for key in kwargs:
            attribute = self.get_product_attribute(key)
            product_attribute_value = ProductAttributeValue.search(
                [("attribute_id", "=", attribute.id), ("name", "=", kwargs[key]),],
                limit=1,
            )
            if not product_attribute_value:
                # Crate new attribute value
                product_attribute_value = ProductAttributeValue.create(
                    {"attribute_id": attribute.id, "name": kwargs[key],}
                )
            attribute_value_ids.append(product_attribute_value.id)
            p_attribute_values |= product_attribute_value
        product_domain = [("product_tmpl_id", "=", product_tmpl.id)]
        product_domain.extend(
            ("product_template_attribute_value_ids", "in", x)
            for x in attribute_value_ids
        )
        product = self.env["product.product"].search(product_domain)
        if not product:
            # Create a variant for saica reel template
            product = self.create_variant(product_tmpl, p_attribute_values, **kwargs)
            _logger.info("New variant created: %s" % product.name)
        return product

    def get_product_lot(self, reel, product=None):
        Lot = self.env["stock.production.lot"]
        serial_number = reel.ReelCode.text.zfill(self._sn_lenght)
        lot = Lot.search([("name", "=", serial_number)])
        lot_vals = {
            "saica_weight": float(reel.Weight.Value),
            "saica_length": float(reel.Length.Value),
        }
        if lot:
            lot.write(lot_vals)
        else:
            lot_vals.update(
                {
                    "name": serial_number,
                    "product_id": product.id,
                    "create_date": fields.Datetime.now(),
                    "saica_year": reel.ReelYear.text,
                }
            )
            lot = Lot.create(lot_vals)
        return lot

    def get_attributes_value(self, object_item):
        attribute_values = {
            # 'year': object_item.Year.text,
            # 'weight': object_item.Weight.text,
            "papercode": object_item.PaperCode.text,
            "basisweight": object_item.BasisWeight.text,
            "diameter": object_item.Diameter.text,
            "width": str(int(float(object_item.Width.text.replace(",", ".")) * 10)),
            # 'length': object_item.Length.text,
        }
        return attribute_values

    def xml2date(self, object_item, time=False):
        if object_item.Date.Year:
            res = "%s-%s-%s" % (
                object_item.Date.Year.text,
                object_item.Date.Month.text,
                object_item.Date.Day.text,
            )
            if time:
                res = res + " %s:%s:%s" % (
                    object_item.Time.Hour.text,
                    object_item.Time.Minute.text,
                    object_item.Time.Second.text,
                )
        else:
            res = ""
        return res

    def GetPendingReceptionsList(self):
        client = self.external_get_client()
        reception_list = client.service.GetPendingReceptionsList(
            self.username, self.password, self.saica_company
        )
        self.ProcessPendingReceptionsList(reception_list)

    def ProcessPendingReceptionsList(self, reception_list):
        ExternalWarehouses = objectify.fromstring(reception_list)
        # with open('../extra/saica-sql/receptionlist.xml', 'r') as res:
        #     reception_list = res.read()
        #     ExternalWarehouses = objectify.fromstring(reception_list)
        pend_dic = xmltodict.parse(reception_list)
        if (not pend_dic["ExternalWarehouses"]["Receptions"]) or (
            pend_dic["ExternalWarehouses"]["Receptions"]["ReceptionItem"][0]["State"]
            == "CAR"
        ):
            return False
        client = self.external_get_client()
        for reception in ExternalWarehouses.Receptions.ReceptionItem:
            if reception.State.text == "TRA":
                picking = self.env["stock.picking"].search(
                    [("origin", "=", reception.LoadCode.text),]
                )
                if picking:
                    continue
                final_destination = self.get_destination(
                    reception.FinalDestination.text, reception.FinalDestinationName.text
                )
                picking_vals = {
                    # 'name': 'SAI' % reception.LoadCode.text,
                    "origin": reception.LoadCode.text,
                    "forecast_arrival_date": self.xml2date(
                        reception.ForecastArrivalDate
                    ),
                    "delivery_date": self.xml2date(reception.DeliveryDate, time=True),
                    "picking_type_id": self.incoming_picking_type_id.id,
                    "partner_id": self.partner_id.id,
                    "company_id": self.company_ids[:1].id,
                    "tractor_plate": reception.NumberPlate.text,
                    "saica_final_destination_id": final_destination.id,
                    "saica_reel_count": int(reception.ReelsCount.text),
                    "saica_load_type": reception.LoadType.text,
                    "saica_weight": float(reception.Weight.text.replace(",", ".")),
                    "move_lines": [],
                }
                # TODO: make onchage picking_type:
                content_list = client.service.GetPendingReceptionsContent(
                    self.username,
                    self.password,
                    reception.LoadCode.text,
                    self.saica_company,
                )
                content_dic = objectify.fromstring(content_list)
                # For testing
                # with open('../extra/saica-sql/ReceptionsContent.xml',
                #           'r') as res:
                #     content_dic = res.read()
                #     content_dic = objectify.fromstring(content_dic)

                if content_dic.CodError:
                    raise ValidationError(_("Incorrect content loads"))
                lot_vals = defaultdict(list)
                for content in content_dic.ReceptionItem.Reel:
                    attribute_values = self.get_attributes_value(content)
                    product = self.get_product_from_attributes(**attribute_values)
                    picking_type = self.incoming_picking_type_id
                    picking_vals["move_lines"].append(
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "name": reception.LoadCode.text,
                                "company_id": self.company_ids[:1].id,
                                "product_uom_qty": 1.0,
                                "product_uom": product.uom_id.id,
                                "location_id": picking_type.default_location_src_id.id,
                                "location_dest_id": (
                                    picking_type.default_location_dest_id.id
                                ),
                            },
                        )
                    )
                    lot = self.env["stock.production.lot"].create(
                        {
                            "name": content.Code.text.zfill(self._sn_lenght),
                            "product_id": product.id,
                            "saica_weight": float(content.Weight.text),
                            "saica_length": float(content.Length.text),
                            "saica_year": content.Year.text,
                        }
                    )
                    lot_vals[product.id].append(lot)
                picking = (
                    self.env["stock.picking"]
                    .with_context(
                        default_picking_type_id=self.incoming_picking_type_id.id
                    )
                    .create(picking_vals)
                )
                picking.action_confirm()
                # Assign lots
                for move in picking.move_lines:
                    move_line_ids_vals = [
                        (
                            0,
                            0,
                            {
                                "lot_id": x.id,
                                "lot_name": x.name,
                                "qty_done": 1.0,
                                "product_uom_qty": 1.0,
                                "product_uom": move.product.uom_id.id,
                                "location_id": move.location_id.id,
                                "location_dest_id": move.location_dest_id.id,
                            },
                        )
                        for x in lot_vals[move.product_id.id]
                    ]
                picking.write({"move_line_ids": move_line_ids_vals})

    def info_reception_saica(self, pickings):
        """Update SAICA that the moves has been received OK"""
        item_list = []
        for picking in pickings:
            item_vals = {
                "ReceptionItem": {
                    "LoadCode": picking.origin,
                    "NumberPlate": picking.tractor_plate,
                    "NumberReel": "%d" % sum(picking.mapped("move_line_ids.qty_done")),
                    "StoreCode": self.saica_warehouse,
                    "Comments": "",
                    "ReceptionDate": self.date_to_dic(picking.date_done),
                }
            }
            item_list.append(item_vals)
        confirm_rec_dic = {"ReceptionsConfirmation": item_list}
        xml = dicttoxml.dicttoxml(
            confirm_rec_dic, attr_type=False, custom_root="ExternalWarehouses"
        )
        xml = xml.replace("<item>", "").replace("</item>", "")
        return self.send_receptions_confirmation(xml)

    def send_receptions_confirmation(self, xml):
        client = self.external_get_client()
        confirm = client.service.ConfirmReceptions(
            self.username, self.password, self.saica_company, xml
        )
        result = xmltodict.parse(confirm)
        if result["ExternalWarehouses"]["CodError"]:
            return (False, result["ExternalWarehouses"]["Info"])
        else:
            return (True,)

    def action_get_inventory(self):
        client = self.external_get_client()
        stock_list = client.service.GetStock(
            self.username, self.password, self.saica_company
        )
        # with open('../extra/saica-sql/stock.xml', 'r') as inventory_file:
        #     pass
        #     stock_list = inventory_file.read()
        #     doc = etree.fromstring(stock_list)
        root = objectify.fromstring(stock_list)
        if not root.Stock:
            return True
        StockInventory = self.env["stock.inventory"]
        inventory_vals = {
            "name": "Saica Inventory",
            "state": "confirm",
        }
        inv_line_vals = []
        for stock_item in root.Stock.StockItem:
            _logger.info(
                "Processing Reel: %s %s"
                % (stock_item.PaperCode.text, str(stock_item.BasisWeight.Value))
            )
            attribute_values = {
                # 'weight': str(stock_item.Weight.Value),
                "papercode": stock_item.PaperCode.text,
                "basisweight": str(stock_item.BasisWeight.Value),
                "diameter": str(stock_item.Diameter.Value),
                "width": str(stock_item.Width.Value).replace(".", ""),
            }
            for reel in stock_item.Reels.ReelItem:
                # This is each unitary reel item
                # attribute_values.update({
                #     'year': reel.ReelYear.text,
                #     'length': str(reel.Length.Value),
                # })
                product = self.get_product_from_attributes(**attribute_values)
                # serial = reel.ReelBarcode.text.zfill(self._sn_lenght)
                inv_line_vals.append(
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "prod_lot_id": self.get_product_lot(reel, product).id,
                            "location_id": self.saica_location_id.id,
                            "product_qty": 1,
                        },
                    )
                )
        inventory_vals["line_ids"] = inv_line_vals
        StockInventory.create(inventory_vals)
        return True

    def info_expedition_saica(self, pickings):
        item_list = []
        for picking in pickings:
            item_vals = {
                "ReceptionItem": {
                    "LoadCode": picking.origin,
                    "NumberPlate": picking.number_plate,
                    "NumberReel": "%d"
                    % sum(picking.mapped("pack_operation_ids.qty_done")),
                    "StoreCode": self.saica_warehouse,
                    "Comments": "",
                    "ReceptionDate": self.date_to_dic(picking.date),
                }
            }
            item_list.append(item_vals)
        confirm_rec_dic = {"ReceptionsConfirmation": item_list}
        xml = dicttoxml.dicttoxml(
            confirm_rec_dic, attr_type=False, custom_root="ExternalWarehouses"
        )
        xml = xml.replace("<item>", "").replace("</item>", "")
        # *************
        for picking in pickings:
            reel_list = []
            reel_count = 0
            for lot in picking.pack_operation_ids.mapped("pack_lot_ids.lot_id"):
                reel_list.append(
                    {"ReelItem": {"ReelCode": lot.name, "ReelYear": lot.saica_year,}}
                )
                reel_count += 1
            item = {
                "DeliveredFrom": self.saica_delivered_from,
                "LoadCode": picking.origin,
                "DeliveredTo": (
                    picking.partner_id.saica_reel_ref or self.saica_delivered_to
                ),
                "Reference": picking.name,
                "NumberPlateTractor": picking.tractor_plate,
                "NumberPlateTow": picking.trailer_plate,
                "DeliveryDate": self.date_to_dic(picking.date_done),
                "Comments": "",
                "ReelsCount": reel_count,
                "Reels": reel_list,
            }
        # item_list.append(item)
        confirm_rec_dic = {"Delivery": item}
        xml = dicttoxml.dicttoxml(
            confirm_rec_dic, attr_type=False, custom_root="ExternalWarehouses"
        )
        xml = xml.replace("<item>", "").replace("</item>", "")
        _logger.debug(xml)
        return self.send_delivery_confirmation(xml)

    def send_delivery_confirmation(self, xml):
        client = self.external_get_client()
        _logger.debug("Voy a confirmar")
        confirm = client.service.ConfirmDelivery(
            self.username, self.password, self.saica_company, xml
        )
        _logger.debug(confirm)
        result = xmltodict.parse(confirm)
        if result["ExternalWarehouses"]["CodError"]:
            return (False, result["ExternalWarehouses"]["Info"])
        else:
            return (True,)

    def date_to_dic(self, date):
        if isinstance(date, str):
            date = fields.Datetime.from_string(date)
        date_dic = {"Day": date.day, "Month": date.month, "Year": date.year}
        time_dic = {"Hour": date.hour, "Minute": date.minute, "Second": date.second}
        return {"Date": date_dic, "Time": time_dic}

    @api.model
    def date_utc_from_tz(self, date, tz="Europe/Madrid"):
        user_tz = pytz.timezone(tz)
        utc = pytz.utc
        return user_tz.localize(date).astimezone(utc)

    @api.model
    def date_tz_from_utc(self, date, tz="Europe/Madrid"):
        user_tz = pytz.timezone(tz)
        utc = pytz.utc
        return utc.localize(date).astimezone(user_tz)

    @api.model
    def date_tz_from_str(self, date_str, tz="Europe/Madrid"):
        date = fields.Datetime.from_string(date_str)
        return self.date_tz_from_utc(date, tz)

    def import_saica_reel_data(self):
        for adapter in self:
            adapter.GetPendingReceptionsList()

    @api.model
    def cron_import_saica_reel_data(self):
        self.search([]).import_saica_reel_data()
