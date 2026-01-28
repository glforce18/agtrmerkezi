"""Add advanced stats tables

Revision ID: 005_stats
Revises: 004_scheduler
Create Date: 2026-01-25

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = "005_stats"
down_revision = "004_scheduler"
branch_labels = None
depends_on = None


def upgrade():
    # ServerStatsDaily table
    op.create_table(
        "server_stats_daily",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("total_players", sa.Integer(), default=0),
        sa.Column("unique_players", sa.Integer(), default=0),
        sa.Column("avg_players", sa.Float(), default=0.0),
        sa.Column("max_players", sa.Integer(), default=0),
        sa.Column("peak_hour", sa.Integer(), nullable=True),
        sa.Column("total_playtime_minutes", sa.Integer(), default=0),
        sa.Column("avg_session_minutes", sa.Float(), default=0.0),
        sa.Column("most_played_map", sa.String(64), nullable=True),
        sa.Column("map_playtime_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # Indexes for daily stats
    op.create_index("idx_daily_server", "server_stats_daily", ["server_id"])
    op.create_index("idx_daily_date", "server_stats_daily", ["date"])
    op.create_index("idx_server_date", "server_stats_daily", ["server_id", "date"], unique=True)

    # ServerStatsWeekly table
    op.create_table(
        "server_stats_weekly",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("week_start", sa.DateTime(), nullable=False),
        sa.Column("total_players", sa.Integer(), default=0),
        sa.Column("unique_players", sa.Integer(), default=0),
        sa.Column("avg_players", sa.Float(), default=0.0),
        sa.Column("max_players", sa.Integer(), default=0),
        sa.Column("total_playtime_hours", sa.Float(), default=0.0),
        sa.Column("avg_session_minutes", sa.Float(), default=0.0),
        sa.Column("retention_rate", sa.Float(), nullable=True),
        sa.Column("new_players", sa.Integer(), default=0),
        sa.Column("returning_players", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # Indexes for weekly stats
    op.create_index("idx_weekly_server", "server_stats_weekly", ["server_id"])
    op.create_index("idx_weekly_week", "server_stats_weekly", ["week_start"])
    op.create_index(
        "idx_server_week", "server_stats_weekly", ["server_id", "week_start"], unique=True
    )

    # PlayerSession table
    op.create_table(
        "player_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("player_name", sa.String(100), nullable=True),
        sa.Column("steam_id", sa.String(50), nullable=True),
        sa.Column("join_time", sa.DateTime(), nullable=False),
        sa.Column("leave_time", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("map_name", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # Indexes for player sessions
    op.create_index("idx_session_server", "player_sessions", ["server_id"])
    op.create_index("idx_session_steam", "player_sessions", ["steam_id"])
    op.create_index("idx_session_time", "player_sessions", ["server_id", "join_time"])

    print("[MIGRATION] Advanced stats tables created successfully")


def downgrade():
    op.drop_table("player_sessions")
    op.drop_table("server_stats_weekly")
    op.drop_table("server_stats_daily")

    print("[MIGRATION] Advanced stats tables dropped")
