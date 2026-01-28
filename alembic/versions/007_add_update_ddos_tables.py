"""add update and ddos protection tables

Revision ID: 007
Revises: 006
Create Date: 2026-01-25

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "007_update_ddos"
down_revision = "006_plugin_status"
branch_labels = None
depends_on = None


def upgrade():
    """Create tables for auto-update and DDoS protection systems"""

    # ServerUpdateLog table
    op.create_table(
        "server_update_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "component", sa.String(50), nullable=False, comment="CS 1.6, AMXModX, Metamod, Plugin"
        ),
        sa.Column(
            "status", sa.String(20), nullable=False, comment="started, completed, failed, error"
        ),
        sa.Column("message", sa.Text(), nullable=True, comment="Update message or error details"),
        sa.Column("version_before", sa.String(50), nullable=True, comment="Version before update"),
        sa.Column("version_after", sa.String(50), nullable=True, comment="Version after update"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_update_server_status", "server_update_logs", ["server_id", "status"])
    op.create_index("idx_update_component", "server_update_logs", ["component"])
    op.create_index("ix_server_update_logs_server_id", "server_update_logs", ["server_id"])

    # DDoSAttackLog table
    op.create_table(
        "ddos_attack_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column(
            "attack_type", sa.String(50), nullable=False, comment="SYN flood, UDP flood, etc."
        ),
        sa.Column(
            "peak_packets_per_second", sa.Integer(), nullable=True, comment="Peak PPS during attack"
        ),
        sa.Column("peak_gbps", sa.Float(), nullable=True, comment="Peak bandwidth in Gbps"),
        sa.Column("duration_seconds", sa.Integer(), nullable=True, comment="Attack duration"),
        sa.Column(
            "blocked_ips_count", sa.Integer(), server_default="0", comment="Number of IPs blocked"
        ),
        sa.Column("detected_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "mitigated",
            sa.Boolean(),
            server_default="0",
            comment="Was attack successfully mitigated",
        ),
        sa.Column(
            "mitigation_method", sa.String(100), nullable=True, comment="IP block, rate limit, etc."
        ),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ddos_server_detected", "ddos_attack_logs", ["server_id", "detected_at"])
    op.create_index("idx_ddos_mitigated", "ddos_attack_logs", ["mitigated"])
    op.create_index("ix_ddos_attack_logs_server_id", "ddos_attack_logs", ["server_id"])

    # IPBlockList table
    op.create_table(
        "ip_block_list",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False, comment="IPv4 or IPv6 address"),
        sa.Column("reason", sa.String(200), nullable=False, comment="Reason for blocking"),
        sa.Column("blocked_by", sa.Integer(), nullable=True, comment="Admin who blocked"),
        sa.Column("blocked_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True, comment="NULL = permanent block"),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("unblocked_at", sa.DateTime(), nullable=True, comment="When IP was unblocked"),
        sa.Column(
            "server_id", sa.Integer(), nullable=True, comment="Specific server or NULL for global"
        ),
        sa.Column(
            "auto_blocked",
            sa.Boolean(),
            server_default="0",
            comment="Automatically blocked by DDoS detection",
        ),
        sa.ForeignKeyConstraint(["blocked_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["server_id"], ["game_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ip_active", "ip_block_list", ["ip_address", "is_active"])
    op.create_index("idx_ip_expires", "ip_block_list", ["expires_at"])
    op.create_index("ix_ip_block_list_ip_address", "ip_block_list", ["ip_address"])
    op.create_index("ix_ip_block_list_is_active", "ip_block_list", ["is_active"])
    op.create_index("ix_ip_block_list_server_id", "ip_block_list", ["server_id"])


def downgrade():
    """Drop auto-update and DDoS protection tables"""

    # Drop IPBlockList table
    op.drop_index("ix_ip_block_list_server_id", "ip_block_list")
    op.drop_index("ix_ip_block_list_is_active", "ip_block_list")
    op.drop_index("ix_ip_block_list_ip_address", "ip_block_list")
    op.drop_index("idx_ip_expires", "ip_block_list")
    op.drop_index("idx_ip_active", "ip_block_list")
    op.drop_table("ip_block_list")

    # Drop DDoSAttackLog table
    op.drop_index("ix_ddos_attack_logs_server_id", "ddos_attack_logs")
    op.drop_index("idx_ddos_mitigated", "ddos_attack_logs")
    op.drop_index("idx_ddos_server_detected", "ddos_attack_logs")
    op.drop_table("ddos_attack_logs")

    # Drop ServerUpdateLog table
    op.drop_index("ix_server_update_logs_server_id", "server_update_logs")
    op.drop_index("idx_update_component", "server_update_logs")
    op.drop_index("idx_update_server_status", "server_update_logs")
    op.drop_table("server_update_logs")
