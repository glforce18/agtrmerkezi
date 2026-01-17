"""Add 2FA and security features

Revision ID: 002_2fa_security
Revises: 001_indexes
Create Date: 2026-01-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '002_2fa_security'
down_revision = '001_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Two-Factor Authentication table
    op.create_table(
        'two_factor_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('secret', sa.String(255), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), default=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('backup_codes_generated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_2fa_user', 'two_factor_auth', ['user_id'], unique=True)

    # Backup Codes table
    op.create_table(
        'backup_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(255), nullable=False),
        sa.Column('is_used', sa.Boolean(), default=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_backup_codes_user', 'backup_codes', ['user_id'])
    op.create_index('idx_backup_codes_used', 'backup_codes', ['is_used'])

    # OAuth Accounts table
    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),  # steam, discord, google
        sa.Column('provider_id', sa.String(255), nullable=False),
        sa.Column('provider_username', sa.String(255), nullable=True),
        sa.Column('provider_email', sa.String(255), nullable=True),
        sa.Column('provider_avatar', sa.String(500), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),  # Encrypted
        sa.Column('refresh_token', sa.Text(), nullable=True),  # Encrypted
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('linked_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('provider', 'provider_id', name='uq_oauth_provider_id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_oauth_user', 'oauth_accounts', ['user_id'])
    op.create_index('idx_oauth_provider', 'oauth_accounts', ['provider', 'provider_id'])

    # Security Events table (for suspicious activity tracking)
    op.create_table(
        'security_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),  # failed_login, suspicious_ip, etc.
        sa.Column('severity', sa.String(20), nullable=False),  # low, medium, high, critical
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('geo_location', sa.JSON(), nullable=True),  # Country, city, etc.
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), default=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_security_events_user', 'security_events', ['user_id'])
    op.create_index('idx_security_events_type', 'security_events', ['event_type'])
    op.create_index('idx_security_events_severity', 'security_events', ['severity'])
    op.create_index('idx_security_events_created', 'security_events', ['created_at'])

    # Login History table (enhanced)
    op.create_table(
        'login_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('login_type', sa.String(50), nullable=False),  # password, oauth, 2fa
        sa.Column('provider', sa.String(50), nullable=True),  # For OAuth logins
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),  # mobile, desktop, tablet
        sa.Column('os', sa.String(100), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('geo_location', sa.JSON(), nullable=True),
        sa.Column('is_successful', sa.Boolean(), default=True),
        sa.Column('failure_reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_login_history_user', 'login_history', ['user_id'])
    op.create_index('idx_login_history_created', 'login_history', ['created_at'])
    op.create_index('idx_login_history_success', 'login_history', ['is_successful'])

    # Device Sessions table (for trusted devices)
    op.create_table(
        'device_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=False),  # Unique device identifier
        sa.Column('device_name', sa.String(255), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('os', sa.String(100), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('is_trusted', sa.Boolean(), default=False),
        sa.Column('trusted_at', sa.DateTime(), nullable=True),
        sa.Column('last_active_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'device_id', name='uq_user_device'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_device_sessions_user', 'device_sessions', ['user_id'])
    op.create_index('idx_device_sessions_device', 'device_sessions', ['device_id'])

    # GDPR Data Requests table
    op.create_table(
        'gdpr_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('request_type', sa.String(50), nullable=False),  # export, delete, anonymize
        sa.Column('status', sa.String(50), nullable=False),  # pending, processing, completed, failed
        sa.Column('request_data', sa.JSON(), nullable=True),
        sa.Column('result_file_path', sa.String(500), nullable=True),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ondelete='SET NULL'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_gdpr_requests_user', 'gdpr_requests', ['user_id'])
    op.create_index('idx_gdpr_requests_status', 'gdpr_requests', ['status'])

    print("[MIGRATION] 2FA and security tables created successfully")


def downgrade():
    op.drop_table('gdpr_requests')
    op.drop_table('device_sessions')
    op.drop_table('login_history')
    op.drop_table('security_events')
    op.drop_table('oauth_accounts')
    op.drop_table('backup_codes')
    op.drop_table('two_factor_auth')

    print("[MIGRATION] 2FA and security tables dropped")
