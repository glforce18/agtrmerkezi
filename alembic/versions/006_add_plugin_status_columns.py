"""add plugin status columns

Revision ID: 006
Revises: 005
Create Date: 2026-01-25

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "006_plugin_status"
down_revision = "005_stats"
branch_labels = None
depends_on = None


def upgrade():
    """Add status tracking columns to server_plugins table"""

    # Add new columns to server_plugins table
    op.add_column("server_plugins", sa.Column("status", sa.String(20), server_default="active"))
    op.add_column("server_plugins", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column("server_plugins", sa.Column("last_checked", sa.DateTime(), nullable=True))
    op.add_column("server_plugins", sa.Column("error_count", sa.Integer(), server_default="0"))

    # Update existing rows to have 'active' status if enabled, 'inactive' if disabled
    op.execute(
        """
        UPDATE server_plugins
        SET status = CASE
            WHEN is_enabled = 1 THEN 'active'
            ELSE 'inactive'
        END
    """
    )

    # Create index for faster status queries
    op.create_index("ix_server_plugins_status", "server_plugins", ["status"])


def downgrade():
    """Remove status tracking columns from server_plugins table"""

    # Drop index
    op.drop_index("ix_server_plugins_status", "server_plugins")

    # Drop columns
    op.drop_column("server_plugins", "error_count")
    op.drop_column("server_plugins", "last_checked")
    op.drop_column("server_plugins", "last_error")
    op.drop_column("server_plugins", "status")
