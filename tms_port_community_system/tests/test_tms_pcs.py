# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date
from unittest import mock

from odoo.tests import TransactionCase, tagged

DUT = """<DUT>
<MessageHeader>
    <Number>TEST-PCS-1</Number>
    <Function>{function}</Function>
    <DateAndTime>2023-07-03T10:23:15</DateAndTime>
</MessageHeader>
<DocumentDetails>
    <ClosingTimeValidDate>2023-07-10T18:00:00</ClosingTimeValidDate>
    <References><PCSDocumentNumber>TEST-ORIGIN-1</PCSDocumentNumber></References>
    <Parties>
        <Type>CONTRACTING_PARTY</Type>
        <Name>Test PCS Forwarder</Name>
        <PCSCode>TESTPCS1</PCSCode>
    </Parties>
    <OperationType>IMPORT</OperationType>
    <UnloadingVesselDetails>
        <VesselName>{vessel}</VesselName>
        <VoyageNumber>V1</VoyageNumber>
    </UnloadingVesselDetails>
    <Remarks><Remark>{remark}</Remark></Remarks>
</DocumentDetails>
<Containers>
    <Goods><Description>Test goods</Description></Goods>
    <ContainerDetails>
        <ItemNumber>1</ItemNumber>
        <PlateNumber>TEST1234567</PlateNumber>
        <FullOrEmptyState><Release>FULL</Release></FullOrEmptyState>
        <LoadingUnloadingDetails>
            <LocationName>Test Place</LocationName>
            <DatesAndTimes>
                <ProposedByContractingCompany>2023-07-04T08:00:00</ProposedByContractingCompany>
            </DatesAndTimes>
        </LoadingUnloadingDetails>
    </ContainerDetails>
</Containers>
</DUT>"""


@tagged("post_install", "-at_install")
class TestTmsPcs(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test PCS transport", "type": "service"}
        )
        cls.backend = cls.env["tms.pcs.backend"].create(
            {
                "name": "Test PCS",
                "product_id": cls.product.id,
                "service_code": "TRANS",
                "message_direction": "In",
                "session_ticket": "TICKET",
            }
        )

    def _process(self, function, vessel, remark, file_name):
        doc = DUT.format(function=function, vessel=vessel, remark=remark)
        return self.backend._create_sale_order(b"", file_name, doc.encode(), "DUTv2")

    def test_create_and_replace_sale_order(self):
        order = self._process(
            "ORIGINAL", "VESSEL A", "First", "SIMTRANS-DUTv2-TEST-20230703102315.XML"
        )
        self.assertEqual(order.validity_date, date(2023, 7, 10))
        self.assertEqual(order.vessel, "VESSEL A")
        self.assertEqual(order.order_line.equipment_id.name, "TEST1234567")
        # The replacement updates the same order, the remarks too
        replaced = self._process(
            "REPLACE", "VESSEL B", "Second", "SIMTRANS-DUTv2-TEST-20230703112315.XML"
        )
        self.assertEqual(replaced, order)
        self.assertEqual(order.vessel, "VESSEL B")
        self.assertIn("Second", order.note)
        tracking = order.message_ids.tracking_value_ids.filtered(
            lambda value: value.field_id.name == "vessel"
        )
        self.assertEqual(
            (tracking.old_value_char, tracking.new_value_char),
            ("VESSEL A", "VESSEL B"),
        )

    def test_list_messages_by_service(self):
        service = mock.MagicMock()
        with mock.patch.object(
            type(self.backend), "get_transport_service", return_value=service
        ):
            self.backend.pcs_list_messages_by_service()
        service.service.ListMessagesByService.assert_called_once_with(
            "TRANS", "Pending", "In", "TICKET"
        )
