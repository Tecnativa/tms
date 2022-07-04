# Copyright 2019 Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestTMSEquipment(common.SavepointCase):
    def test_create_equipment_invalid_name(self):
        # Check Enabled
        equipment = False
        with self.assertRaises(ValidationError):
            equipment = self.env["tms.equipment"].create(
                {"name": "ZZZZ0000000", "iso6346_ok": True,}
            )
        self.assertFalse(equipment)

        # Check Disabled
        equipment_b = False
        equipment_b = self.env["tms.equipment"].create(
            {"name": "ZZZZ0000000", "iso6346_ok": False,}
        )
        self.assertTrue(equipment_b)
        equipment_b.write(
            {"name": "ZZZZ0000001",}
        )

    def test_create_equipment_valid_name(self):
        equipment = self.env["tms.equipment"].create(
            {"name": "CSQU3054383", "iso6346_ok": True,}
        )
        self.assertTrue(equipment)
        equipment.write(
            {"name": "HLBU1509039",}
        )
        with self.assertRaises(ValidationError):
            equipment.write(
                {"name": "ZZZZ0000000",}
            )
