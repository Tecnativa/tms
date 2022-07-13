# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models, tools


class TmsDriverReport(models.Model):
    _name = "tms.driver.report"
    _description = "Driver Statistics"
    _auto = False
    _rec_name = "date"
    _order = "date desc"

    driver_id = fields.Many2one(
        comodel_name="res.partner", string="Driver", readonly=True
    )
    date = fields.Datetime(readonly=True)
    nbr_order = fields.Integer(string="# of Orders", readonly=True)
    nbr_order_line = fields.Integer(string="# of Order Lines", readonly=True)
    nbr_partner_12 = fields.Integer(string="# of Partner 12", readonly=True)
    price_subtotal = fields.Float(string="Subtotal", readonly=True)

    def _select(self):
        select_str = """
            SELECT sub.id, sub.driver_id, sub.date, sub.nbr_order,
                sub.nbr_order_line, sub.price_subtotal, sub.nbr_partner_12
        """
        return select_str

    def _sub_select(self):
        select_str = """
            SELECT sol.id,
                sol.driver_id,
                so.date_order as date,
                COUNT(so.id) AS nbr_order,
                COUNT(sol.id) AS nbr_order_line,
                SUM(sol.price_subtotal) AS price_subtotal,
                CASE WHEN sol.order_partner_id = 12
                    THEN 1 ELSE 0 END AS nbr_partner_12
        """
        return select_str

    def _from(self):
        from_str = """
            FROM sale_order_line sol
                LEFT JOIN res_partner p ON sol.driver_id = p.id
                LEFT JOIN sale_order so ON so.id = sol.order_id
        """
        return from_str

    def _where(self):
        where_str = """
            WHERE p.is_driver = true
        """
        return where_str

    def _group_by(self):
        group_by_str = """
            GROUP BY sol.id, p.name, so.date_order
        """
        return group_by_str

    def _view_sql(self):
        return "%s FROM (%s %s %s %s) AS sub" % (
            self._select(),
            self._sub_select(),
            self._from(),
            self._where(),
            self._group_by(),
        )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW %s AS (%s)",
            (AsIs(self._table), AsIs(self._view_sql())),
        )

    @api.model
    def _report_xls_fields(self):
        return [
            "driver_id",
            "date",
            "nbr_order",
            "nbr_order_line",
            "price_subtotal",
        ]

    # Change/Add Template entries
    @api.model
    def _report_xls_template(self):
        """
        Template updates, e.g.

        my_change = {
            'move':{
                'header': [1, 20, 'text', _('My Move Title')],
                'lines': [1, 0, 'text', _render("line.move_id.name or ''")],
                'totals': [1, 0, 'text', None]},
        }
        return my_change
        """
        return {}
