# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_move am
        SET tms_print_template_id = ai.tms_print_template
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id""",
    )
