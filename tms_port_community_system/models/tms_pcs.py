# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64
import logging
from datetime import datetime

import pytz
from lxml import etree, objectify
from suds.client import Client  # TODO: See if suds-jurko works the same way in P3

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PortCommunitySystem(object):
    def login(self, user, password, organization, test=False):
        Login = self.service_wsdl("Login", test)
        return Login.service.Login(user, password, organization)

    def login_guid(self, user, password, organization, test=False):
        session = self.login(user, password, organization, test)
        return session.diffgram.UserSession.UserSession.TicketGUID

    def service_wsdl(self, service, test=False):
        url = "{}.valenciaportpcs.net/services/{}.asmx?wsdl".format(
            test and "http://test" or "https://www", service
        )
        _logger.info("Pcs URL login: {}".format(url))
        return Client(url)

    def list_messages(self, ticket, state="Pending", direction="In", test=False):
        TransportService = self.service_wsdl("TransportService", test)
        messages = TransportService.service.ListMessages(state, direction, ticket)
        return messages.diffgram and messages.diffgram.MessageData.Messages or []

    def list_messages_by_date(
        self,
        from_date="2020-01-12T11:06:05.083+02:00",
        to_date="2020-01-13T18:06:05.083+02:00",
        message_type="DUTv2",
        service_code="TRANS",
        state="All",
        direction="In",
        ticket="",
    ):
        TransportService = self.service_wsdl("TransportService")
        messages_xml = TransportService.service.ListMessagesByDate(
            from_date, to_date, message_type, service_code, state, direction, ticket
        )
        messages = objectify.fromstring(messages_xml)
        return messages.getchildren()

    def list_messages_by_type(
        self,
        message_type="DUTv2",
        service_code="TRANS",
        state="All",
        direction="In",
        ticket="",
    ):
        TransportService = self.service_wsdl("TransportService")
        messages = TransportService.service.ListMessagesByMessageType(
            message_type, service_code, state, direction, ticket
        )
        return messages.diffgram and messages.diffgram.MessageData.Messages or []


class TmsValenciaportsBackend(models.Model):
    _name = "tms.pcs.backend"
    _description = "TMS Valencia ports backend"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company.id,
    )
    url = fields.Char()
    environment_test = fields.Boolean(default=False)
    user = fields.Char()
    password = fields.Char()
    company_code = fields.Char()
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="PCS Product",
        required=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
    )

    @api.onchange("warehouse_id")
    def _onchange_warehouse_id(self):
        if self.warehouse_id.company_id:
            self.company_id = self.warehouse_id.company_id.id

    def xml_element(self, element, key):
        value = element.find(key)
        return value is not None and value or False

    def xml_value(self, element, key):
        value = element.find(key)
        return value is not None and value.text or False

    def xml_value_time(self, element, key):
        value = self.xml_value(element, key)
        if value:
            value_datetime = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            value_utc = (
                pytz.timezone("Europe/Madrid")
                .localize(value_datetime, is_dst=None)
                .astimezone(pytz.utc)
            )
            value = fields.Datetime.to_string(value_utc)
        return value

    def _search_or_create_partner(
        self, name, vat=False, ref=False, street=False, vals=None
    ):
        vals = dict(vals or {})
        Partner = self.env["res.partner"]
        partner = Partner.browse()
        if vat and len(vat) < 10:
            vat = "ES%s" % vat
            partner = Partner.search([("vat", "=", vat)], limit=1, order="id")
            vals["vat"] = vat
        else:
            vat = False
        if not partner and ref:
            partner = Partner.search([("ref", "=", ref)], limit=1)
            vals["ref"] = ref
        if not partner:
            domain = [("name", "=", name)]
            if street:
                domain.append(("street", "=", street))
                vals["street"] = street
            partner = Partner.search(domain, limit=1)
            vals["name"] = name
        if not partner:
            vals["company_id"] = False
            partner = Partner.create(vals)
        return partner

    def _partner_from_party(self, party):
        name = self.xml_value(party, "Name")
        vat = self.xml_value(party, "NationalIdentityNumber")
        ref = self.xml_value(party, "PCSCode")
        return self._search_or_create_partner(name, vat, ref, vals={})

    def _partner_from_place(self, place):
        name = self.xml_value(place, "LocationName")
        street = self.xml_value(place, "StreetAddress")
        vals = {
            "city": self.xml_value(place, "City"),
            "zip": self.xml_value(place, "PostalCode"),
            "customer_rank": 0,
        }
        return self._search_or_create_partner(name, street=street, vals=vals)

    def _partner_from_port(self, port):
        name = self.xml_value(port, "Name")
        ref = self.xml_value(port, "UNLOCODE")
        vals = {
            "customer_rank": 0,
        }
        return self._search_or_create_partner(name, ref=ref, vals=vals)

    def _search_or_create_goods(self, name):
        Goods = self.env["tms.goods"]
        if not name:
            return Goods.browse()
        goods = Goods.search([("name", "=", name)], limit=1)
        if not goods:
            goods = Goods.create({"name": name})
        return goods

    def _search_or_create_container_type(self, name, iso_type):
        SizeType = self.env["iso6346.size.type"]
        if not iso_type:
            return SizeType.browse()
        size_type = SizeType.search([("code", "=", iso_type)], limit=1)
        if not size_type:
            size_type = SizeType.new(
                {
                    "code": iso_type,
                    "name": name,
                }
            )
            size_type._onchange_code()
            size_type = SizeType.create(size_type._convert_to_write(size_type._cache))
        return size_type

    def _search_or_create_equipment(self, name, size_type):
        Equipment = self.env["tms.equipment"]
        if not name:
            return Equipment.browse()
        equipment = Equipment.search([("name", "=", name)], limit=1)
        if not equipment:
            equipment = Equipment.create(
                {
                    "name": name,
                    "size_type_id": size_type.id,
                }
            )
        return equipment

    def get_file_from_attach(self, file_name, sale):
        attachments = self.env["ir.attachment"].search(
            [
                ("name", "ilike", file_name[:-30]),
                ("res_model", "=", "sale.order"),
                ("res_id", "=", sale.id),
            ],
            order="name DESC",
        )
        for attach in attachments:
            if attach.name < file_name:
                return base64.b64decode(attach.datas)
        return ""

    def _attach_file(self, file_content, file_name, sale_order, number):
        data_attach = {
            "datas": file_content,
            "name": file_name,
            "res_model": "sale.order",
            "res_id": sale_order.id,
            "type": "binary",
        }
        self.env["ir.attachment"].create(data_attach)
        # email.write({'attachment_ids': [(6, 0, attachments.ids)]})

    def _clean_false_vals(self, vals):
        return {k: v for k, v in vals.items() if v}

    def _parse_dut(self, doc):  # noqa
        so_vals = {
            "warehouse_id": self.warehouse_id.id,
            "company_id": self.company_id.id,
        }
        sol_list = []
        # MessageHeader
        so_vals["pcs_message_number"] = self.xml_value(doc, "MessageHeader/Number")
        so_vals["date_order"] = self.xml_value_time(doc, "MessageHeader/DateAndTime")
        # DocumentDetails
        valid_date = self.xml_value_time(doc, "DocumentDetails/ClosingTimeValidDate")
        so_vals["validity_date"] = valid_date and valid_date[:10] or False
        # References
        so_vals["origin"] = self.xml_value(
            doc, "DocumentDetails/References/PCSDocumentNumber"
        )
        so_vals["client_order_ref"] = self.xml_value(
            doc, "DocumentDetails/References/ForwarderFileNumber"
        )
        so_vals["booking_number"] = self.xml_value(
            doc, "DocumentDetails/References/BookingNumber"
        )
        # Parties
        parties = doc.findall("DocumentDetails/Parties")
        for party in parties:
            party_type = self.xml_value(party, "Type")
            if party_type == "CONTRACTING_PARTY":
                so_vals["partner_id"] = self._partner_from_party(party).id
                # Rewrite if contracting party has a reference
                client_ref = self.xml_value(party, "DocumentReference")
                if client_ref:
                    so_vals["client_order_ref"] = client_ref
            elif party_type == "RELEASE_COMPANY":
                so_vals["release_id"] = self._partner_from_party(party).id
            elif party_type == "ACCEPTANCE_COMPANY":
                so_vals["acceptance_id"] = self._partner_from_party(party).id
        operation_type = self.xml_value(doc, "DocumentDetails/OperationType")
        # LoadingVesselDetails
        # UnloadingVesselDetails
        if operation_type == "EXPORT":
            so_vals["vessel"] = self.xml_value(
                doc, "DocumentDetails/LoadingVesselDetails/VesselName"
            )
        else:
            so_vals["vessel"] = self.xml_value(
                doc, "DocumentDetails/UnloadingVesselDetails/VesselName"
            )
        so_vals["voyage_number"] = self.xml_value(
            doc, "DocumentDetails/UnloadingVesselDetails/VoyageNumber"
        )
        # Ports
        ports = doc.findall("DocumentDetails/Ports")
        for port in ports:
            port_function = self.xml_value(port, "Function")
            if not port_function:
                continue
            if port_function == "DESTINATION":
                so_vals["shipment_port_id"] = self._partner_from_port(port).id
            elif port_function == "ORIGIN":
                so_vals["port_id"] = self._partner_from_port(port).id
            elif port_function == "LOADING":
                so_vals["loading_port_id"] = self._partner_from_port(port).id
            elif port_function == "DISCHARGE":
                so_vals["unloading_port_id"] = self._partner_from_port(port).id
        # Remarks
        remarks = doc.findall("DocumentDetails/Remarks")
        remark_note = ""
        for remark in remarks:
            # Ignore remark type at this time
            # remark_type = self.xml_value(remark, 'Type')
            remark_note += self.xml_value(remark, "Remark")
        if remark_note:
            so_vals["note"] = remark_note
        # Containers
        containers = doc.findall("Containers")
        for container in containers:
            # Goods only the first
            good = self.xml_value(container, "Goods/Description")
            nbr_packages = self.xml_value(container, "Goods/NumberOfPackages")
            goods = self._search_or_create_goods(good)
            # ContainerDetails
            # ItemNumber
            item_number = self.xml_value(container, "ContainerDetails/ItemNumber")
            # ISOType
            iso_type = self.xml_value(container, "ContainerDetails/ISOType")
            iso_description = self.xml_value(
                container, "ContainerDetails/ISODescription"
            )
            size_type = self._search_or_create_container_type(iso_description, iso_type)
            # PlateNumber
            container_plate = self.xml_value(container, "ContainerDetails/PlateNumber")
            equipment = self._search_or_create_equipment(container_plate, size_type)
            # FullOrEmptyState
            state_release = self.xml_value(
                container, "ContainerDetails/FullOrEmptyState/Release"
            )
            unload_service = state_release == "FULL"
            # Weights
            # tare = self.xml_value(container, 'ContainerDetails/Weights/Tare')
            gross = self.xml_value(container, "ContainerDetails/Weights/Gross")

            # ReleaseDetails
            release_company = container.find("ReleaseDetails/ReleaseCompany")
            if release_company is not None:
                release_name = self.xml_value(release_company, "Name")
                vat = self.xml_value(release_company, "NationalIdentityNumber")
                so_vals["release_id"] = self._search_or_create_partner(
                    release_name, vat, vals={"customer_rank": 0}
                ).id
            so_vals["release_locator"] = self.xml_value(
                container, "ReleaseDetails/References/LocatorCode"
            )
            release_seal = self.xml_value(container, "ReleaseDetails/Seals/Value")
            # AcceptanceDetails
            acceptance_company = container.find("AcceptanceDetails/AcceptanceCompany")
            if acceptance_company is not None:
                acceptance_name = self.xml_value(acceptance_company, "Name")
                vat = self.xml_value(acceptance_company, "NationalIdentityNumber")
                so_vals["acceptance_id"] = self._search_or_create_partner(
                    acceptance_name, vat, vals={"customer_rank": 0}
                ).id
            so_vals["acceptance_locator"] = self.xml_value(
                container, "AcceptanceDetails/References/LocatorCode"
            )
            # LoadingUnloadingDetails
            places = container.findall("ContainerDetails/LoadingUnloadingDetails")
            for place in places:
                partner_place = self._partner_from_place(place)
                pickup_date = self.xml_value_time(
                    place, "DatesAndTimes/ProposedByContractingCompany"
                )
                sol_vals = {
                    "product_id": self.product_id.id,
                    "shipping_origin_id": unload_service
                    and so_vals.get("release_id", False)
                    or partner_place.id,
                    "shipping_destination_id": unload_service
                    and partner_place.id
                    or so_vals.get("acceptance_id", False),
                    "equipment_size_type_id": size_type.id,
                    "equipment_id": equipment.id,
                    "pickup_date": pickup_date,
                    "seal": release_seal,
                    "pcs_item_number": item_number,
                }
                package_vals = {
                    "company_id": so_vals["company_id"],
                    "name": "/",
                    "partner_id": so_vals["partner_id"],
                    "pickup_date": sol_vals["pickup_date"],
                    "shipping_origin_id": sol_vals["shipping_origin_id"],
                    "shipping_destination_id": sol_vals["shipping_destination_id"],
                    "shipping_weight": gross or 0.0,
                    "number_of_packages": nbr_packages or 0,
                    "goods_id": goods.id,
                }
                sol_vals["tms_package_ids"] = [(0, 0, dict(package_vals))]
                sol_list.append((0, 0, dict(sol_vals)))
        so_vals["order_line"] = sol_list
        return so_vals

    def _create_sale_order(self, file_bin, file_name, doc_str, msg_type):  # noqa: C901
        SaleOrder = self.env["sale.order"]
        doc_xml = etree.fromstring(doc_str)
        so_vals = self._parse_dut(doc_xml)
        # so_vals = self._prepare_sale_order(doc_xml, msg_type)
        if not so_vals.get("partner_id", False):
            return SaleOrder
        # ORIGINAL / REPLACE / CANCELLATION
        msg_function = self.xml_value(doc_xml, "MessageHeader/Function")
        so_vals["pcs_message_function"] = msg_function
        doc_number = self.xml_value(doc_xml, "MessageHeader/Number")
        origin = self.xml_value(doc_xml, "DocumentDetails/References/PCSDocumentNumber")
        domain = [("company_id", "=", so_vals["company_id"])]
        if origin and msg_function != "ORIGINAL":
            domain.extend(
                ["|", ("pcs_message_number", "=", doc_number), ("origin", "=", origin)]
            )
        else:
            domain.extend([("pcs_message_number", "=", doc_number)])
        sale_order = SaleOrder.search(domain, limit=1, order="id DESC")
        if not sale_order:
            sale_order = SaleOrder.with_context(
                force_company=so_vals["company_id"],
            ).create(so_vals)
        else:
            sol_list = so_vals.pop("order_line", [])
            new_vals = self._clean_false_vals(so_vals)
            original_doc_xml = etree.fromstring(
                self.get_file_from_attach(file_name, sale_order)
            )
            original_vals = self._clean_false_vals(self._parse_dut(original_doc_xml))
            original_sol_list = original_vals.pop("order_line", [])
            key_vals_to_remove = []
            for k, v in new_vals.items():
                if k in original_vals and original_vals[k] == v:
                    key_vals_to_remove.append(k)
            # To avoid change size dictionary in iteration
            for key in key_vals_to_remove:
                new_vals.pop(key)
            if new_vals:
                fields_tracking = {}
                new_vals_tracking = {}
                for k, v in sale_order.fields_get().items():
                    if k in new_vals:
                        fields_tracking[k] = v
                        new_vals_tracking[k] = new_vals[k]
                        if v["type"] == "many2one":
                            record = self.env[v["relation"]].browse(new_vals[k])
                            new_vals_tracking[k] = record
                sale_order.message_track(
                    fields_tracking, {sale_order.id: new_vals_tracking}
                )
                sale_order.write(new_vals)
            if len(sol_list) == 1 and len(sale_order.order_line or []) <= 1:
                line = sale_order.order_line
                sol_vals = self._clean_false_vals(sol_list[0][2])
                original_sol_vals = self._clean_false_vals(original_sol_list[0][2])
                key_vals_to_remove = []
                for k, v in sol_vals.items():
                    if k in original_sol_vals and original_sol_vals[k] == v:
                        key_vals_to_remove.append(k)
                # To avoid change size dictionary in iteration
                for key in key_vals_to_remove:
                    sol_vals.pop(key)
                if sol_vals:
                    if line:
                        package_list = sol_vals.pop("tms_package_ids", [])
                        line.write(sol_vals)
                        if (
                            len(package_list) == 1
                            and len(line.tms_package_ids or []) <= 1
                        ):
                            package_vals = self._clean_false_vals(package_list[0][2])
                            if line.tms_package_ids:
                                package_vals.pop("name", False)
                                line.tms_package_ids.write(package_vals)
                            else:
                                line.tms_package_ids = package_list
                    else:
                        sale_order.order_line = sol_list
        if not self.env.context.get("pcs_skip_store_attachment", False):
            self._attach_file(file_bin, file_name, sale_order, doc_number)
        return sale_order

    def import_sale_orders(self):
        # Re-process a file already downloaded
        # attachment = self.env["ir.attachment"].browse(182576)
        # file_bin = attachment.datas
        # doc_xml = base64.b64decode(file_bin)
        # self._create_sale_order(
        #     file_bin, attachment.name, doc_xml, "DUTv2"
        # )
        # return

        pcs = PortCommunitySystem()
        ticket = pcs.login_guid(
            self.user, self.password, self.company_code, self.environment_test
        )
        # messages = pcs.list_messages_by_date(
        #     message_type='DUTv2', ticket=ticket)
        # messages = pcs.list_messages(ticket=ticket)
        messages = pcs.list_messages_by_type(message_type="DUTv2", ticket=ticket)
        TransportService = pcs.service_wsdl("TransportService")
        if not isinstance(messages, list):
            messages = [messages]
        for msg in messages:
            # text needed if list_messages_by_date objectify
            # message_guid = msg.MessageGUID.text
            message_guid = msg.MessageGUID
            file_bin = TransportService.service.Download(message_guid, ticket)
            doc_xml = base64.b64decode(file_bin)
            if msg.MessageType in ["DUTv2", "ReleaseOrderv2", "AcceptanceOrderv2"]:
                self._create_sale_order(
                    file_bin, message_guid, doc_xml, msg.MessageType
                )

    @api.model
    def import_sale_orders_planned(self):
        for backend in self.search([]):
            backend.import_sale_orders()
