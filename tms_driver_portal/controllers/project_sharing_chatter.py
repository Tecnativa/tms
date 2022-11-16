# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import Forbidden

from odoo.http import request

from odoo.addons.project.controllers.project_sharing_chatter import (
    ProjectSharingChatter,
)

from .portal import ProjectCustomerPortal


class ProjectSharingChatterTMS(ProjectSharingChatter):
    def _check_project_access_and_get_token(self, project_id, res_model, res_id, token):
        if not request.env.context.get("skip_project_check_tms", False):
            return super()._check_project_access_and_get_token(
                project_id, res_model, res_id, token
            )
        project_sudo = ProjectCustomerPortal._document_check_access(
            self, "project.project", project_id, token
        )
        can_access = (
            project_sudo
            and res_model == "project.task"
            and project_sudo.with_user(request.env.user)._check_project_sharing_access()
        )
        task = None
        if can_access:
            task = request.env["project.task"].sudo().search([("id", "=", res_id)])
        if not can_access or not task:
            raise Forbidden()
        return task[task._mail_post_token_field]
