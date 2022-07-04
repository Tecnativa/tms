# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Transport Management System Reporting(TMS)",
    "summary": "Transport Management System Reporting(TMS)",
    "version": "13.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/tms",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "report_xlsx",
        "sale_order_line_vendor",
        "tms_sale_quick_input",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/report_paperformat.xml",
        "views/account_invoice_view.xml",
        "views/layout_templates.xml",
        "views/report_transport_order.xml",
        "reports/tms_driver_report_views.xml",
        "reports/tms_driver_report_xls_views.xml",
        "reports/package_datail_report.xml",
        "views/report_package_detail.xml",
        "views/project_task_view.xml",
        "views/report_account_invoice.xml",
        "views/res_partner_view.xml",
        "views/product_view.xml",
        "views/tms_print_template.xml",
        "data/tms_mail_template_data.xml",
    ],
}
