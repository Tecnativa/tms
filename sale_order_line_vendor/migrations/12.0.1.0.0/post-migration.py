# Copyright 2020 Tecnativa - Sergio Teruel
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return
    # Change field sale_line_ids to sale_line_id
    env.cr.execute(
        """
        UPDATE purchase_order_line pol
            SET sale_line_id = (
                SELECT MAX(sprel.sale_line_id)
                FROM sale_order_line_purchase_order_line_rel sprel
                WHERE (pol.id = sprel.purchase_line_id)
            );
        """
    )
