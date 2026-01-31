"""add 30 webpanel features - tables and columns

Revision ID: 009
Revises: 008
Create Date: 2026-01-31

Adds 15 new tables for advanced WebPanel features:
- Plugin management (dependencies, marketplace, performance, logs)
- Config management (templates, MOTD)
- Statistics (player stats, match history, server analytics)
- File management (custom maps, models, sounds)
- Admin management (VIP members, player actions log)
- Map management (voting, rotation schedules)
"""

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGTEXT

from alembic import op

# revision identifiers, used by Alembic.
revision = "009_webpanel_features"
down_revision = "008_panel_features"
branch_labels = None
depends_on = None


def upgrade():
    """Create tables for 30 WebPanel features"""

    # =========================
    # PLUGIN MANAGEMENT TABLES
    # =========================

    # 1. Plugin Dependencies
    op.create_table(
        "plugin_dependencies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "plugin_filename", sa.String(100), nullable=False, comment="Plugin .amxx filename"
        ),
        sa.Column(
            "dependency_type",
            sa.Enum("module", "plugin", name="dependency_type"),
            nullable=False,
            comment="module (.so) or plugin (.amxx)",
        ),
        sa.Column("dependency_name", sa.String(100), nullable=False, comment="Required dependency"),
        sa.Column("is_optional", sa.Boolean(), server_default="0", comment="Optional dependency"),
        sa.Column("min_version", sa.String(20), nullable=True, comment="Minimum required version"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_plugin_deps", "plugin_dependencies", ["plugin_filename", "dependency_type"]
    )

    # 2. Plugin Marketplace
    op.create_table(
        "plugin_marketplace",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False, comment="Plugin name"),
        sa.Column(
            "filename", sa.String(100), nullable=False, unique=True, comment=".amxx filename"
        ),
        sa.Column("description", sa.Text(), nullable=True, comment="Plugin description"),
        sa.Column("category", sa.String(50), nullable=False, comment="admin, fun, gameplay, etc."),
        sa.Column("author", sa.String(100), nullable=True, comment="Plugin author"),
        sa.Column("version", sa.String(20), nullable=True, comment="Plugin version"),
        sa.Column("file_url", sa.String(500), nullable=False, comment="Download URL"),
        sa.Column("file_size", sa.Integer(), nullable=True, comment="File size in bytes"),
        sa.Column(
            "file_hash", sa.String(64), nullable=True, comment="SHA256 hash for verification"
        ),
        sa.Column("source_url", sa.String(500), nullable=True, comment=".sma source URL"),
        sa.Column("homepage_url", sa.String(500), nullable=True, comment="Plugin homepage"),
        sa.Column("dependencies", sa.JSON(), nullable=True, comment="Required modules/plugins"),
        sa.Column("compatible_games", sa.JSON(), nullable=True, comment='["AG", "HLDM", "CS16"]'),
        sa.Column("install_count", sa.Integer(), server_default="0", comment="Times installed"),
        sa.Column("rating", sa.Float(), server_default="0.0", comment="Average rating 0-5"),
        sa.Column("rating_count", sa.Integer(), server_default="0", comment="Number of ratings"),
        sa.Column("is_verified", sa.Boolean(), server_default="0", comment="AGTR verified"),
        sa.Column(
            "is_active", sa.Boolean(), server_default="1", comment="Available in marketplace"
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_marketplace_category", "plugin_marketplace", ["category", "is_active"])
    op.create_index("idx_marketplace_rating", "plugin_marketplace", ["rating", "is_active"])

    # 3. Plugin Performance
    op.create_table(
        "plugin_performance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("plugin_filename", sa.String(100), nullable=False),
        sa.Column("cpu_usage_percent", sa.Float(), nullable=True, comment="CPU usage %"),
        sa.Column("memory_kb", sa.Integer(), nullable=True, comment="Memory usage KB"),
        sa.Column("tick_time_ms", sa.Float(), nullable=True, comment="Average tick time ms"),
        sa.Column(
            "error_count", sa.Integer(), server_default="0", comment="Errors since last check"
        ),
        sa.Column("last_error", sa.Text(), nullable=True, comment="Last error message"),
        sa.Column("checked_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_plugin_perf", "plugin_performance", ["server_id", "plugin_filename", "checked_at"]
    )

    # 4. Plugin Logs
    op.create_table(
        "plugin_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column(
            "plugin_filename", sa.String(100), nullable=True, comment="NULL for general AMXModX"
        ),
        sa.Column(
            "log_level",
            sa.Enum("ERROR", "WARNING", "INFO", name="plugin_log_level"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False, comment="Log message"),
        sa.Column("stack_trace", sa.Text(), nullable=True, comment="Stack trace if error"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_plugin_logs", "plugin_logs", ["server_id", "log_level", "created_at"])

    # =========================
    # CONFIG MANAGEMENT TABLES
    # =========================

    # 5. Config Templates
    op.create_table(
        "config_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False, comment="Template name"),
        sa.Column("description", sa.Text(), nullable=True, comment="Template description"),
        sa.Column("game_type", sa.Enum("HLDM", "AG", "CS16", name="gametype"), nullable=False),
        sa.Column(
            "preset_type",
            sa.String(50),
            nullable=False,
            comment="competitive, casual, training, etc.",
        ),
        sa.Column("config_content", LONGTEXT(), nullable=False, comment="server.cfg content"),
        sa.Column("cvars", sa.JSON(), nullable=True, comment="Parsed CVARs for quick editing"),
        sa.Column(
            "is_official", sa.Boolean(), server_default="0", comment="AGTR official template"
        ),
        sa.Column("is_public", sa.Boolean(), server_default="1", comment="Available to all users"),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("use_count", sa.Integer(), server_default="0", comment="Times applied"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_config_templates", "config_templates", ["game_type", "preset_type", "is_public"]
    )

    # 6. MOTD Templates
    op.create_table(
        "motd_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False, comment="Template name"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("html_content", LONGTEXT(), nullable=False, comment="MOTD HTML content"),
        sa.Column("is_official", sa.Boolean(), server_default="0", comment="AGTR official"),
        sa.Column("is_public", sa.Boolean(), server_default="1"),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("use_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_motd_templates", "motd_templates", ["is_public", "is_official"])

    # =========================
    # STATISTICS TABLES
    # =========================

    # 7. Player Statistics
    op.create_table(
        "player_statistics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("steam_id", sa.String(32), nullable=False),
        sa.Column("player_name", sa.String(100), nullable=True, comment="Last known name"),
        sa.Column("total_playtime_seconds", sa.Integer(), server_default="0"),
        sa.Column("total_kills", sa.Integer(), server_default="0"),
        sa.Column("total_deaths", sa.Integer(), server_default="0"),
        sa.Column("total_headshots", sa.Integer(), server_default="0"),
        sa.Column("total_score", sa.Integer(), server_default="0"),
        sa.Column("total_rounds", sa.Integer(), server_default="0"),
        sa.Column("wins", sa.Integer(), server_default="0"),
        sa.Column("losses", sa.Integer(), server_default="0"),
        sa.Column("elo_rating", sa.Integer(), server_default="1000", comment="ELO rating"),
        sa.Column("rank", sa.Integer(), nullable=True, comment="Server rank"),
        sa.Column("favorite_weapon", sa.String(50), nullable=True),
        sa.Column("favorite_map", sa.String(64), nullable=True),
        sa.Column("first_seen", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("last_seen", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("server_id", "steam_id", name="uq_player_stats"),
    )
    op.create_index(
        "idx_player_stats_leaderboard",
        "player_statistics",
        ["server_id", "elo_rating", "last_seen"],
    )
    op.create_index("idx_player_stats_steam", "player_statistics", ["steam_id"])

    # 8. Match History
    op.create_table(
        "match_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("match_date", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("map_name", sa.String(64), nullable=False),
        sa.Column(
            "match_type", sa.String(50), nullable=True, comment="deathmatch, teamplay, ag, etc."
        ),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("team1_score", sa.Integer(), nullable=True),
        sa.Column("team2_score", sa.Integer(), nullable=True),
        sa.Column("winner_team", sa.Integer(), nullable=True, comment="1 or 2"),
        sa.Column("total_kills", sa.Integer(), server_default="0"),
        sa.Column("total_deaths", sa.Integer(), server_default="0"),
        sa.Column("player_count", sa.Integer(), nullable=True, comment="Players in match"),
        sa.Column("match_data", sa.JSON(), nullable=True, comment="Full match JSON data"),
        sa.Column("log_file_path", sa.String(500), nullable=True, comment="Path to log file"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_match_history", "match_history", ["server_id", "match_date"])
    op.create_index("idx_match_map", "match_history", ["map_name"])

    # 9. Server Analytics
    op.create_table(
        "server_analytics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("cpu_usage_percent", sa.Float(), nullable=True),
        sa.Column("memory_usage_mb", sa.Float(), nullable=True),
        sa.Column("network_in_mbps", sa.Float(), nullable=True),
        sa.Column("network_out_mbps", sa.Float(), nullable=True),
        sa.Column("disk_usage_mb", sa.Float(), nullable=True),
        sa.Column("player_count", sa.Integer(), nullable=True),
        sa.Column("tick_rate", sa.Float(), nullable=True, comment="Server tickrate"),
        sa.Column("fps", sa.Float(), nullable=True, comment="Server FPS"),
        sa.Column("ping_avg", sa.Float(), nullable=True, comment="Average player ping"),
        sa.Column("ping_max", sa.Float(), nullable=True, comment="Max player ping"),
        sa.Column("current_map", sa.String(64), nullable=True),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_server_analytics", "server_analytics", ["server_id", "recorded_at"])

    # =========================
    # FILE MANAGEMENT TABLES
    # =========================

    # 10. Custom Maps
    op.create_table(
        "custom_maps",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("map_name", sa.String(64), nullable=False, comment="Map name without .bsp"),
        sa.Column("display_name", sa.String(100), nullable=True, comment="Friendly display name"),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True, comment="SHA256 hash"),
        sa.Column(
            "thumbnail_url", sa.String(500), nullable=True, comment="Map thumbnail/screenshot"
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("author", sa.String(100), nullable=True),
        sa.Column("upload_date", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("play_count", sa.Integer(), server_default="0", comment="Times played"),
        sa.Column("last_played", sa.DateTime(), nullable=True),
        sa.Column("has_nav_file", sa.Boolean(), server_default="0"),
        sa.Column("has_res_file", sa.Boolean(), server_default="0"),
        sa.Column("has_txt_file", sa.Boolean(), server_default="0"),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("server_id", "map_name", name="uq_custom_map"),
    )
    op.create_index("idx_custom_maps", "custom_maps", ["server_id", "upload_date"])

    # 11. Custom Models
    op.create_table(
        "custom_models",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False, comment="Model filename"),
        sa.Column(
            "model_type", sa.String(50), nullable=False, comment="player, weapon, world, etc."
        ),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("preview_url", sa.String(500), nullable=True, comment="Preview image"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("upload_date", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_custom_models", "custom_models", ["server_id", "model_type"])

    # 12. Custom Sounds
    op.create_table(
        "custom_sounds",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("sound_name", sa.String(100), nullable=False, comment="Sound filename"),
        sa.Column(
            "sound_type", sa.String(50), nullable=False, comment="weapon, ambient, voice, etc."
        ),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("upload_date", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_custom_sounds", "custom_sounds", ["server_id", "sound_type"])

    # =========================
    # ADMIN MANAGEMENT TABLES
    # =========================

    # 13. VIP Members
    op.create_table(
        "vip_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("steam_id", sa.String(32), nullable=False),
        sa.Column("player_name", sa.String(100), nullable=True),
        sa.Column("vip_flags", sa.String(50), nullable=False, comment="AMXModX VIP flags"),
        sa.Column("password", sa.String(100), nullable=True, comment="Optional password"),
        sa.Column("expires_at", sa.DateTime(), nullable=True, comment="NULL = permanent"),
        sa.Column("is_active", sa.Boolean(), server_default="1"),
        sa.Column("added_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("server_id", "steam_id", name="uq_vip_member"),
    )
    op.create_index("idx_vip_members", "vip_members", ["server_id", "is_active"])
    op.create_index("idx_vip_steam", "vip_members", ["steam_id"])

    # 14. Player Actions Log
    op.create_table(
        "player_actions_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=True, comment="Admin who performed action"),
        sa.Column(
            "target_steam_id", sa.String(32), nullable=True, comment="Target player Steam ID"
        ),
        sa.Column("target_name", sa.String(100), nullable=True, comment="Target player name"),
        sa.Column(
            "action_type",
            sa.Enum("kick", "ban", "slay", "unban", "mute", "unmute", name="player_action_type"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True, comment="Ban/mute duration"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_player_actions", "player_actions_log", ["server_id", "action_type", "created_at"]
    )
    op.create_index("idx_player_actions_steam", "player_actions_log", ["target_steam_id"])

    # =========================
    # MAP MANAGEMENT TABLES
    # =========================

    # 15. Map Votes
    op.create_table(
        "map_votes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("vote_title", sa.String(200), nullable=False, comment="Vote description"),
        sa.Column("map_options", sa.JSON(), nullable=False, comment='["map1", "map2", "map3"]'),
        sa.Column("vote_results", sa.JSON(), nullable=True, comment='{"map1": 5, "map2": 3}'),
        sa.Column("winning_map", sa.String(64), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), server_default="1", comment="Currently accepting votes"
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("ends_at", sa.DateTime(), nullable=True, comment="Vote end time"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_map_votes", "map_votes", ["server_id", "is_active", "created_at"])

    # 16. Map Rotation Schedules
    op.create_table(
        "map_rotation_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("schedule_name", sa.String(100), nullable=False, comment="Schedule display name"),
        sa.Column("maps_rotation", sa.JSON(), nullable=False, comment='["map1", "map2", ...]'),
        sa.Column(
            "rotation_mode", sa.String(50), nullable=False, comment="sequential, random, time-based"
        ),
        sa.Column("time_per_map_minutes", sa.Integer(), nullable=True, comment="Minutes per map"),
        sa.Column(
            "time_schedule", sa.JSON(), nullable=True, comment='{"00:00": "map1", "12:00": "map2"}'
        ),
        sa.Column(
            "is_active", sa.Boolean(), server_default="0", comment="Currently active schedule"
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_map_rotation", "map_rotation_schedules", ["server_id", "is_active"])

    # =========================
    # COLUMN ADDITIONS
    # =========================

    # Add columns to game_servers
    op.add_column(
        "game_servers",
        sa.Column("vip_enabled", sa.Boolean(), server_default="0", comment="VIP system enabled"),
    )

    # Add columns to server_plugins
    op.add_column(
        "server_plugins",
        sa.Column(
            "last_performance_check",
            sa.DateTime(),
            nullable=True,
            comment="Last performance metrics check",
        ),
    )


def downgrade():
    """Drop WebPanel feature tables and columns"""

    # Drop column additions
    op.drop_column("server_plugins", "last_performance_check")
    op.drop_column("game_servers", "vip_enabled")

    # Drop tables in reverse order
    op.drop_index("idx_map_rotation", "map_rotation_schedules")
    op.drop_table("map_rotation_schedules")

    op.drop_index("idx_map_votes", "map_votes")
    op.drop_table("map_votes")

    op.drop_index("idx_player_actions_steam", "player_actions_log")
    op.drop_index("idx_player_actions", "player_actions_log")
    op.drop_table("player_actions_log")

    op.drop_index("idx_vip_steam", "vip_members")
    op.drop_index("idx_vip_members", "vip_members")
    op.drop_table("vip_members")

    op.drop_index("idx_custom_sounds", "custom_sounds")
    op.drop_table("custom_sounds")

    op.drop_index("idx_custom_models", "custom_models")
    op.drop_table("custom_models")

    op.drop_index("idx_custom_maps", "custom_maps")
    op.drop_table("custom_maps")

    op.drop_index("idx_server_analytics", "server_analytics")
    op.drop_table("server_analytics")

    op.drop_index("idx_match_map", "match_history")
    op.drop_index("idx_match_history", "match_history")
    op.drop_table("match_history")

    op.drop_index("idx_player_stats_steam", "player_statistics")
    op.drop_index("idx_player_stats_leaderboard", "player_statistics")
    op.drop_table("player_statistics")

    op.drop_index("idx_motd_templates", "motd_templates")
    op.drop_table("motd_templates")

    op.drop_index("idx_config_templates", "config_templates")
    op.drop_table("config_templates")

    op.drop_index("idx_plugin_logs", "plugin_logs")
    op.drop_table("plugin_logs")

    op.drop_index("idx_plugin_perf", "plugin_performance")
    op.drop_table("plugin_performance")

    op.drop_index("idx_marketplace_rating", "plugin_marketplace")
    op.drop_index("idx_marketplace_category", "plugin_marketplace")
    op.drop_table("plugin_marketplace")

    op.drop_index("idx_plugin_deps", "plugin_dependencies")
    op.drop_table("plugin_dependencies")
