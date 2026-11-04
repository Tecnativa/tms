# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """The analytic account of the vehicle is gone: its plan becomes the vehicles
    plan and the account is added to the vehicle analytic distribution, which now
    represents the vehicle."""
    if not openupgrade.column_exists(env.cr, "fleet_vehicle", "analytic_account_id"):
        return
    env.cr.execute(
        """
        SELECT id, analytic_account_id FROM fleet_vehicle
        WHERE analytic_account_id IS NOT NULL
        """
    )
    rows = env.cr.fetchall()
    accounts = env["account.analytic.account"].browse({x[1] for x in rows}).exists()
    params = env["ir.config_parameter"].sudo()
    if len(accounts.root_plan_id) == 1 and not params.get_param(
        "tms_analytic.vehicles_plan"
    ):
        params.set_param("tms_analytic.vehicles_plan", accounts.root_plan_id.id)
    vehicles = env["fleet.vehicle"].with_context(active_test=False)
    for vehicle_id, account_id in rows:
        account = accounts.browse(account_id)
        if account in accounts:
            vehicles.browse(vehicle_id)._add_analytic_account(account)
