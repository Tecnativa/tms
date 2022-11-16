# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.portal.controllers.portal import CustomerPortal


class ProjectCustomerPortal(CustomerPortal):

    # @route()
    # def home(self, **kw):
    #     if request.env.user.partner_id.is_driver:
    #         return request.redirect("/my/alltasks")
    #     return super().home(**kw)

    @route(["/my/alltasks"], type="http", auth="user", website=True)
    def portal_all_tasks_tms(self):
        return request.render("tms_driver_portal.project_sharing_portal_tms")

    @route("/my/alltasks/sharing", type="http", auth="user", methods=["GET"])
    def render_all_task_backend_view(self):
        user_task = request.env["project.task"].search(
            [
                ("user_ids", "in", request.env.user.ids),
            ],
            limit=1,
            order="id DESC",
        )
        project = user_task.sudo().project_id
        if (
            not project.exists()
            or not project.with_user(request.env.user)._check_project_sharing_access()
        ):
            return request.not_found()

        session_info = self._prepare_project_sharing_session_info(project)
        session_info[
            "action_name"
        ] = "tms_driver_portal.project_sharing_all_task_action"
        request.session.context["skip_project_check_tms"] = True
        return request.render(
            "project.project_sharing_embed",
            {"session_info": session_info},
        )
