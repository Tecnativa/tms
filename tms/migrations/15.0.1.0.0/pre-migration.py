from openupgradelib import openupgrade


def _prefill_project_task_progress_status(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE project_task ADD progress_status VARCHAR"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task pt
        SET progress_status = CASE
            WHEN ptt.is_closed THEN 'closed'
            WHEN ptt.sequence = 1 THEN 'not_started'
            ELSE 'in_progress'
            END
        FROM project_task_type ptt
        WHERE ptt.id = pt.stage_id
        """,
    )


def _prefill_project_task_pending_duration_estimated(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE project_task ADD pending_duration_estimated NUMERIC"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task pt
        SET pending_duration_estimated = 0
        WHERE progress_status = 'closed'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            SELECT task_id,
                SUM(duration_estimated) AS duration_estimated
            FROM project_task_checkpoint
            WHERE departure_time IS NOT NULL
            GROUP BY task_id
        )
        UPDATE project_task pt
        SET pending_duration_estimated = sub.duration_estimated
        FROM sub
        WHERE sub.task_id = pt.id
            AND pt.progress_status <> 'closed'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _prefill_project_task_progress_status(env)
    _prefill_project_task_pending_duration_estimated(env)
