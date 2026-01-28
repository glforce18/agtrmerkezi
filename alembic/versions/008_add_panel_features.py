"""add panel enhancement features

Revision ID: 008
Revises: 007
Create Date: 2026-01-25

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "008_panel_features"
down_revision = "007_update_ddos"
branch_labels = None
depends_on = None


def upgrade():
    """Create tables for panel enhancement features"""

    # PlayerHistory table
    op.create_table(
        "player_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("steam_id", sa.String(32), nullable=False, comment="Steam ID"),
        sa.Column("name", sa.String(100), nullable=False, comment="Player name at connection"),
        sa.Column("ip_address", sa.String(45), nullable=True, comment="IP address"),
        sa.Column("connected_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "disconnected_at", sa.DateTime(), nullable=True, comment="NULL if still connected"
        ),
        sa.Column("duration_seconds", sa.Integer(), nullable=True, comment="Session duration"),
        sa.Column("map_played", sa.String(64), nullable=True, comment="Map during session"),
        sa.Column("kills", sa.Integer(), server_default="0"),
        sa.Column("deaths", sa.Integer(), server_default="0"),
        sa.Column("score", sa.Integer(), server_default="0"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_player_steam", "player_history", ["steam_id", "server_id"])
    op.create_index("idx_player_date", "player_history", ["connected_at"])
    op.create_index("ix_player_history_server_id", "player_history", ["server_id"])
    op.create_index("ix_player_history_steam_id", "player_history", ["steam_id"])

    # PlayerNote table
    op.create_table(
        "player_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("steam_id", sa.String(32), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_note_player", "player_notes", ["steam_id", "server_id"])
    op.create_index("ix_player_notes_server_id", "player_notes", ["server_id"])
    op.create_index("ix_player_notes_steam_id", "player_notes", ["steam_id"])

    # PlayerTag table
    op.create_table(
        "player_tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("steam_id", sa.String(32), nullable=False),
        sa.Column("tag", sa.String(50), nullable=False, comment="VIP, Skilled, Toxic, etc."),
        sa.Column("color", sa.String(7), server_default="#3b82f6", comment="Hex color"),
        sa.Column("added_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("server_id", "steam_id", "tag", name="uq_player_tag"),
    )
    op.create_index("idx_tag_player", "player_tags", ["steam_id", "server_id"])
    op.create_index("ix_player_tags_server_id", "player_tags", ["server_id"])
    op.create_index("ix_player_tags_steam_id", "player_tags", ["steam_id"])

    # ServerTemplate table
    op.create_table(
        "server_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False, comment="Template name"),
        sa.Column("description", sa.Text(), nullable=True, comment="Template description"),
        sa.Column("game_type", sa.Enum("HLDM", "AG", "CS16", name="gametype"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default="0", comment="Available to all users"),
        sa.Column(
            "is_official", sa.Boolean(), server_default="0", comment="Official AGTR template"
        ),
        sa.Column("config_data", sa.JSON(), nullable=True, comment="server.cfg content"),
        sa.Column("plugins", sa.JSON(), nullable=True, comment="List of plugins to install"),
        sa.Column("maps", sa.JSON(), nullable=True, comment="Map list"),
        sa.Column("cvars", sa.JSON(), nullable=True, comment="Console variables"),
        sa.Column("addons", sa.JSON(), nullable=True, comment="Additional addons/mods"),
        sa.Column("use_count", sa.Integer(), server_default="0", comment="Times used"),
        sa.Column("rating", sa.Float(), server_default="0.0", comment="Average rating"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_template_game", "server_templates", ["game_type", "is_public"])
    op.create_index("idx_template_official", "server_templates", ["is_official"])

    # UserPreference - Add new columns to existing table
    op.add_column(
        "user_preferences",
        sa.Column("panel_layout", sa.JSON(), nullable=True, comment="Custom panel layout"),
    )
    op.add_column(
        "user_preferences",
        sa.Column("tab_order", sa.JSON(), nullable=True, comment="Preferred tab order"),
    )
    op.add_column(
        "user_preferences",
        sa.Column("hidden_tabs", sa.JSON(), nullable=True, comment="Hidden tabs"),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "theme_schedule", sa.JSON(), nullable=True, comment="Auto theme switching schedule"
        ),
    )
    op.add_column(
        "user_preferences",
        sa.Column("quick_actions", sa.JSON(), nullable=True, comment="FAB quick actions"),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "notification_settings", sa.JSON(), nullable=True, comment="Notification preferences"
        ),
    )
    op.add_column(
        "user_preferences", sa.Column("timezone", sa.String(50), server_default="Europe/Istanbul")
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "tour_completed", sa.Boolean(), server_default="0", comment="Tour guide completed"
        ),
    )
    op.add_column(
        "user_preferences", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now())
    )

    # AdminActivity table
    op.create_table(
        "admin_activities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column(
            "action_type",
            sa.String(50),
            nullable=False,
            comment="viewing_console, editing_config, etc.",
        ),
        sa.Column("current_tab", sa.String(50), nullable=True, comment="Active tab"),
        sa.Column("details", sa.JSON(), nullable=True, comment="Additional activity details"),
        sa.Column("started_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "last_active",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_activity_server", "admin_activities", ["server_id", "last_active"])
    op.create_index("idx_activity_user", "admin_activities", ["user_id", "server_id"])
    op.create_index("ix_admin_activities_user_id", "admin_activities", ["user_id"])
    op.create_index("ix_admin_activities_server_id", "admin_activities", ["server_id"])


def downgrade():
    """Drop panel enhancement tables"""

    # Drop AdminActivity table
    op.drop_index("ix_admin_activities_server_id", "admin_activities")
    op.drop_index("ix_admin_activities_user_id", "admin_activities")
    op.drop_index("idx_activity_user", "admin_activities")
    op.drop_index("idx_activity_server", "admin_activities")
    op.drop_table("admin_activities")

    # Drop new UserPreference columns
    op.drop_column("user_preferences", "created_at")
    op.drop_column("user_preferences", "tour_completed")
    op.drop_column("user_preferences", "timezone")
    op.drop_column("user_preferences", "notification_settings")
    op.drop_column("user_preferences", "quick_actions")
    op.drop_column("user_preferences", "theme_schedule")
    op.drop_column("user_preferences", "hidden_tabs")
    op.drop_column("user_preferences", "tab_order")
    op.drop_column("user_preferences", "panel_layout")

    # Drop ServerTemplate table
    op.drop_index("idx_template_official", "server_templates")
    op.drop_index("idx_template_game", "server_templates")
    op.drop_table("server_templates")

    # Drop PlayerTag table
    op.drop_index("ix_player_tags_steam_id", "player_tags")
    op.drop_index("ix_player_tags_server_id", "player_tags")
    op.drop_index("idx_tag_player", "player_tags")
    op.drop_table("player_tags")

    # Drop PlayerNote table
    op.drop_index("ix_player_notes_steam_id", "player_notes")
    op.drop_index("ix_player_notes_server_id", "player_notes")
    op.drop_index("idx_note_player", "player_notes")
    op.drop_table("player_notes")

    # Drop PlayerHistory table
    op.drop_index("ix_player_history_steam_id", "player_history")
    op.drop_index("ix_player_history_server_id", "player_history")
    op.drop_index("idx_player_date", "player_history")
    op.drop_index("idx_player_steam", "player_history")
    op.drop_table("player_history")
