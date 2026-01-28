"""Add scheduler tables

Revision ID: 004_scheduler
Revises: 003_audit_logs
Create Date: 2026-01-25

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = "004_scheduler"
down_revision = "003_audit_logs"
branch_labels = None
depends_on = None


def upgrade():
    # ServerScheduledTask table
    op.create_table(
        "server_scheduled_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("task_name", sa.String(100), nullable=False),
        sa.Column(
            "task_type",
            sa.Enum(
                "restart", "map_change", "backup", "announcement", "rcon_command", name="tasktype"
            ),
            nullable=False,
        ),
        sa.Column(
            "schedule_type",
            sa.Enum("cron", "interval", "one_time", name="scheduletype"),
            nullable=False,
        ),
        sa.Column("cron_minute", sa.String(20), nullable=True),
        sa.Column("cron_hour", sa.String(20), nullable=True),
        sa.Column("cron_day", sa.String(20), nullable=True),
        sa.Column("cron_month", sa.String(20), nullable=True),
        sa.Column("cron_day_of_week", sa.String(20), nullable=True),
        sa.Column("interval_value", sa.Integer(), nullable=True),
        sa.Column(
            "interval_unit", sa.Enum("minutes", "hours", "days", name="intervalunit"), nullable=True
        ),
        sa.Column("scheduled_time", sa.DateTime(), nullable=True),
        sa.Column("task_config", sa.JSON(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("last_run", sa.DateTime(), nullable=True),
        sa.Column("next_run", sa.DateTime(), nullable=True),
        sa.Column("apscheduler_job_id", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("apscheduler_job_id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # Indexes for efficient querying
    op.create_index("idx_scheduled_server", "server_scheduled_tasks", ["server_id"])
    op.create_index("idx_scheduled_enabled", "server_scheduled_tasks", ["is_enabled"])
    op.create_index("idx_scheduled_next_run", "server_scheduled_tasks", ["next_run"])

    # ScheduledTaskExecution table
    op.create_table(
        "scheduled_task_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("executed_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("result_message", sa.Text(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["task_id"], ["server_scheduled_tasks.id"], ondelete="CASCADE"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # Indexes for execution history
    op.create_index("idx_execution_task", "scheduled_task_executions", ["task_id"])
    op.create_index("idx_execution_time", "scheduled_task_executions", ["executed_at"])

    print("[MIGRATION] Scheduler tables created successfully")


def downgrade():
    op.drop_table("scheduled_task_executions")
    op.drop_table("server_scheduled_tasks")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS tasktype")
    op.execute("DROP TYPE IF EXISTS scheduletype")
    op.execute("DROP TYPE IF EXISTS intervalunit")

    print("[MIGRATION] Scheduler tables dropped")
