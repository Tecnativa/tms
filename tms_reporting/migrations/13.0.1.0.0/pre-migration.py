# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_field_renames = [
    (
        "product.template",
        "product_template",
        "tms_print_template",
        "tms_print_template_id",
    ),
    (
        "product.product",
        "product_product",
        "tms_print_template",
        "tms_print_template_id",
    ),
    ("res.partner", "res_partner", "tms_print_template", "tms_print_template_id"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
