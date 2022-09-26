# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class TmsDriverReportXlsx(models.AbstractModel):
    _name = "report.tms_reporting.tms_driver_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "TMS Driver Report XLSX"

    def generate_xlsx_report(self, workbook, data, drivers):
        report_name = "Drivers_report"
        sheet = workbook.add_worksheet(report_name[:31])
        fields = drivers._fields.keys()
        for row, driver in enumerate(drivers):
            for col, field in enumerate(fields):
                sheet.write(
                    row,
                    col,
                    drivers._fields[field].convert_to_write(driver[field], driver),
                )
