# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict
from datetime import datetime, timedelta

from dateutil import tz
from dateutil.relativedelta import relativedelta

from odoo import _, fields, http
from odoo.http import request


class WebsiteTMSReporting(http.Controller):
    def month_list(self):
        return [
            ("01", _("January")),
            ("02", _("February")),
            ("03", _("March")),
            ("04", _("April")),
            ("05", _("May")),
            ("06", _("June")),
            ("07", _("July")),
            ("08", _("August")),
            ("09", _("September")),
            ("10", _("October")),
            ("11", _("November")),
            ("12", _("December")),
        ]

    def datetime_to_tz(self, value):
        if isinstance(value, datetime):
            value = fields.Datetime.context_timestamp(request, value)
        else:
            value = datetime.combine(value, datetime.min.time())
        return fields.Datetime.to_string(value)

    def daterange(self, start_date, end_date, tz_utc, tz_user):
        if isinstance(start_date, datetime):
            start_date = start_date.replace(tzinfo=tz_utc).astimezone(tz_user)
        if isinstance(end_date, datetime):
            end_date = end_date.replace(tzinfo=tz_utc).astimezone(tz_user)
        for n in range(int((end_date - start_date).days) + 1):
            day = start_date + timedelta(n)
            yield (fields.Date.to_string(day), day.isoweekday())

    @http.route(["/tms/drivers/sheet"], type="http", auth="user", website=True)
    def drivers_sheet(self, **post):
        user = request.env.user
        tz_utc = tz.tzutc()
        tz_user = tz.gettz(user.tz)
        today = fields.Date.context_today(request)
        month = post.get("month") or today.month
        year = post.get("year") or today.year
        date_from = fields.Date.to_date("%s-%s-01" % (year, month))
        date_to = date_from + relativedelta(day=31)
        range_days = [
            (x, y) for x, y in self.daterange(date_from, date_to, tz_utc, tz_user)
        ]

        drivers = request.env["res.partner"].search(
            [("is_driver", "=", True), ("show_in_sheet", "=", True)]
        )
        drivers_info = {}
        total_amount = 0.0
        for driver in drivers:
            drivers_info[driver.id] = {
                "driver": driver,
                "driver_total": 0.0,
                "count": 0,
                "absences_total": 0,
                "groupages": 0,
                "reuses": 0,
                "distance_estimated": 0.0,
                "distance_traveled": 0.0,
                "partners": defaultdict(int),
                "days_dict": defaultdict(
                    lambda: {
                        "subtotal": 0.0,
                        "count": 0,
                    }
                ),
            }

        partners = request.env["res.partner"].search(
            [
                ("customer_rank", ">", 0),
                ("show_in_sheet", "=", True),
                ("is_driver", "=", False),
            ]
        )

        domain = [
            ("driver_id", "in", drivers.ids),
            ("pickup_date", ">=", "%s 00:00:00" % (date_from)),
            ("pickup_date", "<=", "%s 23:59:59" % (date_to)),
        ]
        so_lines = request.env["sale.order.line"].search(
            domain, order="driver_id, pickup_date"
        )
        last_driver_id = False
        last_equipment = False
        for line in so_lines:
            driver_id = line.driver_id.id
            days_dict = drivers_info[driver_id]["days_dict"]
            # TO REMOVE if field type changes to Date
            pickup_date = line.pickup_date
            pickup_date = pickup_date.replace(tzinfo=tz_utc)
            day = fields.Date.to_string(pickup_date.astimezone(tz_user))
            days_dict[day]["subtotal"] += line.price_subtotal
            days_dict[day]["count"] += 1
            drivers_info[driver_id]["driver_total"] += line.price_subtotal
            drivers_info[driver_id]["count"] += 1
            total_amount += line.price_subtotal

            if line.order_partner_id in partners:
                drivers_info[driver_id]["partners"][line.order_partner_id.id] += 1
            if len(line.tms_package_ids) > 2:
                drivers_info[driver_id]["groupages"] += 1

            # Equipment
            if last_driver_id == driver_id and line.equipment_id == last_equipment:
                drivers_info[driver_id]["reuses"] += 1
                last_equipment = line.equipment_id

            drivers_info[driver_id]["distance_estimated"] += sum(
                line.mapped("task_ids.distance_estimated")
            )
            drivers_info[driver_id]["distance_traveled"] += sum(
                line.mapped("task_ids.distance_traveled")
            )
            last_driver_id = driver_id

        for driver_id in drivers_info.keys():
            drivers_info[driver_id]["percentage"] = (
                total_amount
                and (drivers_info[driver_id]["driver_total"] / total_amount) * 100
                or 0.0
            )

        employees = request.env["hr.employee"].search(
            [("user_id.partner_id", "in", drivers.ids)]
        )
        absences = request.env["hr.leave"].search(
            [
                ("employee_id", "in", employees.ids),
                "|",
                "&",
                ("date_from", ">=", date_from),
                ("date_from", "<=", date_to),
                "&",
                ("date_to", ">=", date_from),
                ("date_to", "<=", date_to),
            ]
        )

        absences_dict = defaultdict(lambda: defaultdict(lambda: False))
        for absence in absences:
            driver_id = absence.employee_id.user_id.partner_id.id

            days = self.daterange(
                absence.date_from, min(absence.date_to, date_to), tz_utc, tz_user
            )
            for day, _weekday in days:
                absences_dict[driver_id][day] = {
                    "name": absence.holiday_status_id.name[:2],
                    "color": absence.holiday_status_id.color_name,
                }
                drivers_info[driver_id]["absences_total"] += 1

        vals = {
            "drivers_info": drivers_info.values(),
            "days": range_days,
            "partners": partners,
            "absences": absences_dict,
            "company": user.company_id,
            "currency": user.company_id.currency_id,
            "month": month,
            "year": year,
            "month_list": self.month_list(),
        }
        return request.render("website_tms_reporting.drivers_sheet", vals)

    @http.route(["/tms/equipments/sheet"], type="http", auth="user", website=True)
    def equipments_sheet(self, **post):
        user = request.env.user
        tz_utc = tz.tzutc()
        tz_user = tz.gettz(user.tz)
        today = fields.Date.today()
        date_from = (
            post.get("date_from")
            and fields.Date.to_date(post.get("date_from"))
            or today + relativedelta(days=-20)
        )
        date_to = (
            post.get("date_to")
            and fields.Date.to_date(post.get("date_to"))
            or today + relativedelta(days=20)
        )
        range_days = [
            (x, y) for x, y in self.daterange(date_from, date_to, tz_utc, tz_user)
        ]

        equipments = request.env["tms.equipment"].search(
            [("show_in_sheet", "=", True)], order="sequence"
        )

        equipments_info = {}
        for equipment in equipments:
            equipments_info[equipment.id] = {
                "days_dict": defaultdict(str),
            }
        domain = [
            ("equipment_id", "in", equipments.ids),
            ("date_start", ">=", "%s 00:00:00" % (date_from)),
            ("date_start", "<=", "%s 23:59:59" % (date_to)),
        ]
        tasks = request.env["project.task"].search(
            domain, order="equipment_id, date_start"
        )
        for task in tasks:
            date_tz = self.datetime_to_tz(task.date_start)[:10]
            equipments_info[task.equipment_id.id]["days_dict"][date_tz] = task.name

        vals = {
            "equipments_info": equipments_info,
            "equipments": equipments,
            "days": range_days,
            "date_from": date_from,
            "date_to": date_to,
        }
        return request.render("website_tms_reporting.equipment_sheet", vals)
