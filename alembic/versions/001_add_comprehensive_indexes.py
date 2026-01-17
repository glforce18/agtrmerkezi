"""Add comprehensive database indexes for performance optimization

Revision ID: 001_indexes
Revises:
Create Date: 2026-01-16

This migration adds a comprehensive set of indexes to optimize query performance
across all database models based on common query patterns and foreign key relationships.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Add all indexes to improve query performance.

    Priority levels:
    - HIGH: Frequently queried fields, foreign keys, status fields
    - MEDIUM: Secondary filters, date ranges, counts
    - LOW: Rarely filtered fields, metadata
    """

    # ==================== HIGH PRIORITY INDEXES ====================

    # USER MODEL - Already has some indexes, adding missing ones
    # Note: username, email, steam_id already indexed in model
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_status', 'users', ['status'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    op.create_index('ix_users_last_login', 'users', ['last_login'])
    op.create_index('ix_users_email_verified', 'users', ['email_verified'])
    # Composite index for active users by role
    op.create_index('ix_users_status_role', 'users', ['status', 'role'])
    # Composite index for leaderboard queries
    op.create_index('ix_users_elo_desc', 'users', [sa.text('elo DESC')])
    op.create_index('ix_users_kd_ratio_desc', 'users', [sa.text('kd_ratio DESC')])

    # USER SESSIONS - Critical for authentication
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_token_hash', 'user_sessions', ['token_hash'])
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    op.create_index('ix_user_sessions_is_active', 'user_sessions', ['is_active'])
    # Composite for active session lookup
    op.create_index('ix_user_sessions_user_active', 'user_sessions', ['user_id', 'is_active', 'expires_at'])
    op.create_index('ix_user_sessions_last_activity', 'user_sessions', ['last_activity'])

    # SERVER PACKAGES
    op.create_index('ix_server_packages_game_type', 'server_packages', ['game_type'])
    op.create_index('ix_server_packages_is_active', 'server_packages', ['is_active'])
    op.create_index('ix_server_packages_is_popular', 'server_packages', ['is_popular'])
    # Composite for active packages by game type
    op.create_index('ix_server_packages_active_game', 'server_packages', ['is_active', 'game_type', 'display_order'])

    # GAME SERVERS - Most frequently queried
    op.create_index('ix_game_servers_owner_id', 'game_servers', ['owner_id'])
    op.create_index('ix_game_servers_status', 'game_servers', ['status'])
    op.create_index('ix_game_servers_game_type', 'game_servers', ['game_type'])
    op.create_index('ix_game_servers_package_id', 'game_servers', ['package_id'])
    op.create_index('ix_game_servers_expires_at', 'game_servers', ['expires_at'])
    op.create_index('ix_game_servers_created_at', 'game_servers', ['created_at'])
    # Composite indexes for common queries
    op.create_index('ix_game_servers_owner_status', 'game_servers', ['owner_id', 'status'])
    op.create_index('ix_game_servers_status_expires', 'game_servers', ['status', 'expires_at'])
    op.create_index('ix_game_servers_auto_renew', 'game_servers', ['auto_renew', 'expires_at'])
    # For expiring servers check
    op.create_index('ix_game_servers_expiring_soon', 'game_servers', ['status', 'expires_at', 'owner_id'])

    # SERVER ACTIONS - Audit logging
    op.create_index('ix_server_actions_server_id', 'server_actions', ['server_id'])
    op.create_index('ix_server_actions_user_id', 'server_actions', ['user_id'])
    op.create_index('ix_server_actions_action', 'server_actions', ['action'])
    op.create_index('ix_server_actions_created_at', 'server_actions', ['created_at'])
    # Composite for server action history
    op.create_index('ix_server_actions_server_created', 'server_actions', ['server_id', 'created_at'])

    # PAYMENTS - Critical for financial queries
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_method', 'payments', ['method'])
    op.create_index('ix_payments_server_id', 'payments', ['server_id'])
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])
    op.create_index('ix_payments_external_id', 'payments', ['external_id'])
    op.create_index('ix_payments_coupon_id', 'payments', ['coupon_id'])
    # Composite indexes for payment reports
    op.create_index('ix_payments_status_created', 'payments', ['status', 'created_at'])
    op.create_index('ix_payments_user_status', 'payments', ['user_id', 'status'])
    op.create_index('ix_payments_completed_at', 'payments', ['completed_at'])

    # BANK TRANSFERS
    op.create_index('ix_bank_transfers_payment_id', 'bank_transfers', ['payment_id'])
    op.create_index('ix_bank_transfers_approved_by', 'bank_transfers', ['approved_by'])
    op.create_index('ix_bank_transfers_created_at', 'bank_transfers', ['created_at'])

    # FORUM CATEGORIES
    op.create_index('ix_forum_categories_parent_id', 'forum_categories', ['parent_id'])
    op.create_index('ix_forum_categories_is_visible', 'forum_categories', ['is_visible'])
    op.create_index('ix_forum_categories_display_order', 'forum_categories', ['display_order'])
    # Composite for visible categories
    op.create_index('ix_forum_categories_visible_order', 'forum_categories', ['is_visible', 'display_order'])

    # FORUM TOPICS - High traffic
    op.create_index('ix_forum_topics_category_id', 'forum_topics', ['category_id'])
    op.create_index('ix_forum_topics_author_id', 'forum_topics', ['author_id'])
    op.create_index('ix_forum_topics_last_post_by', 'forum_topics', ['last_post_by'])
    op.create_index('ix_forum_topics_is_pinned', 'forum_topics', ['is_pinned'])
    op.create_index('ix_forum_topics_is_locked', 'forum_topics', ['is_locked'])
    op.create_index('ix_forum_topics_is_featured', 'forum_topics', ['is_featured'])
    op.create_index('ix_forum_topics_created_at', 'forum_topics', ['created_at'])
    op.create_index('ix_forum_topics_last_post_at', 'forum_topics', ['last_post_at'])
    # Composite for topic listing (pinned first, then by last post)
    op.create_index('ix_forum_topics_category_pinned_lastpost', 'forum_topics',
                   ['category_id', 'is_pinned', sa.text('last_post_at DESC')])
    # For trending topics
    op.create_index('ix_forum_topics_view_count_desc', 'forum_topics', [sa.text('view_count DESC')])

    # FORUM POSTS
    op.create_index('ix_forum_posts_topic_id', 'forum_posts', ['topic_id'])
    op.create_index('ix_forum_posts_author_id', 'forum_posts', ['author_id'])
    op.create_index('ix_forum_posts_created_at', 'forum_posts', ['created_at'])
    op.create_index('ix_forum_posts_edited_by', 'forum_posts', ['edited_by'])
    op.create_index('ix_forum_posts_is_first_post', 'forum_posts', ['is_first_post'])
    # Composite for post listing
    op.create_index('ix_forum_posts_topic_created', 'forum_posts', ['topic_id', 'created_at'])

    # FORUM POST LIKES
    op.create_index('ix_forum_post_likes_post_id', 'forum_post_likes', ['post_id'])
    op.create_index('ix_forum_post_likes_user_id', 'forum_post_likes', ['user_id'])
    op.create_index('ix_forum_post_likes_created_at', 'forum_post_likes', ['created_at'])

    # FORUM REPLIES
    op.create_index('ix_forum_replies_topic_id', 'forum_replies', ['topic_id'])
    op.create_index('ix_forum_replies_user_id', 'forum_replies', ['user_id'])
    op.create_index('ix_forum_replies_is_active', 'forum_replies', ['is_active'])
    op.create_index('ix_forum_replies_created_at', 'forum_replies', ['created_at'])
    # Composite for active replies
    op.create_index('ix_forum_replies_topic_active', 'forum_replies', ['topic_id', 'is_active', 'created_at'])

    # SUPPORT TICKETS
    op.create_index('ix_support_tickets_user_id', 'support_tickets', ['user_id'])
    op.create_index('ix_support_tickets_status', 'support_tickets', ['status'])
    op.create_index('ix_support_tickets_priority', 'support_tickets', ['priority'])
    op.create_index('ix_support_tickets_category', 'support_tickets', ['category'])
    op.create_index('ix_support_tickets_server_id', 'support_tickets', ['server_id'])
    op.create_index('ix_support_tickets_assigned_to', 'support_tickets', ['assigned_to'])
    op.create_index('ix_support_tickets_created_at', 'support_tickets', ['created_at'])
    # Composite for ticket queue
    op.create_index('ix_support_tickets_status_priority', 'support_tickets', ['status', 'priority', 'created_at'])
    op.create_index('ix_support_tickets_assigned_status', 'support_tickets', ['assigned_to', 'status'])

    # TICKET MESSAGES
    op.create_index('ix_ticket_messages_ticket_id', 'ticket_messages', ['ticket_id'])
    op.create_index('ix_ticket_messages_user_id', 'ticket_messages', ['user_id'])
    op.create_index('ix_ticket_messages_is_staff_reply', 'ticket_messages', ['is_staff_reply'])
    op.create_index('ix_ticket_messages_is_read', 'ticket_messages', ['is_read'])
    op.create_index('ix_ticket_messages_created_at', 'ticket_messages', ['created_at'])
    # Composite for unread messages
    op.create_index('ix_ticket_messages_ticket_read', 'ticket_messages', ['ticket_id', 'is_read'])

    # ==================== MEDIUM PRIORITY INDEXES ====================

    # SYSTEM LOGS
    op.create_index('ix_system_logs_level', 'system_logs', ['level'])
    op.create_index('ix_system_logs_category', 'system_logs', ['category'])
    op.create_index('ix_system_logs_user_id', 'system_logs', ['user_id'])
    op.create_index('ix_system_logs_created_at', 'system_logs', ['created_at'])
    # Composite for log filtering
    op.create_index('ix_system_logs_level_category_created', 'system_logs', ['level', 'category', 'created_at'])

    # ANNOUNCEMENTS - Already has slug index
    op.create_index('ix_announcements_is_active', 'announcements', ['is_active'])
    op.create_index('ix_announcements_show_on_homepage', 'announcements', ['show_on_homepage'])
    op.create_index('ix_announcements_created_by', 'announcements', ['created_by'])
    op.create_index('ix_announcements_created_at', 'announcements', ['created_at'])
    op.create_index('ix_announcements_expires_at', 'announcements', ['expires_at'])
    # Composite for active announcements
    op.create_index('ix_announcements_active_homepage', 'announcements', ['is_active', 'show_on_homepage', 'created_at'])

    # AUDIT LOGS - Already has created_at index
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    # Composite for entity audit trail
    op.create_index('ix_audit_logs_entity_type_id', 'audit_logs', ['entity_type', 'entity_id', 'created_at'])

    # PLUGINS
    op.create_index('ix_plugins_game_type', 'plugins', ['game_type'])
    op.create_index('ix_plugins_category', 'plugins', ['category'])
    op.create_index('ix_plugins_is_active', 'plugins', ['is_active'])
    op.create_index('ix_plugins_is_default', 'plugins', ['is_default'])
    op.create_index('ix_plugins_created_by', 'plugins', ['created_by'])
    # Composite for active plugins by game
    op.create_index('ix_plugins_active_game_category', 'plugins', ['is_active', 'game_type', 'category'])

    # SERVER PLUGINS
    op.create_index('ix_server_plugins_server_id', 'server_plugins', ['server_id'])
    op.create_index('ix_server_plugins_plugin_id', 'server_plugins', ['plugin_id'])
    op.create_index('ix_server_plugins_is_enabled', 'server_plugins', ['is_enabled'])
    op.create_index('ix_server_plugins_installed_by', 'server_plugins', ['installed_by'])
    # Composite for enabled plugins
    op.create_index('ix_server_plugins_server_enabled', 'server_plugins', ['server_id', 'is_enabled'])

    # SCHEDULED TASKS
    op.create_index('ix_scheduled_tasks_server_id', 'scheduled_tasks', ['server_id'])
    op.create_index('ix_scheduled_tasks_user_id', 'scheduled_tasks', ['user_id'])
    op.create_index('ix_scheduled_tasks_task_type', 'scheduled_tasks', ['task_type'])
    op.create_index('ix_scheduled_tasks_is_enabled', 'scheduled_tasks', ['is_enabled'])
    op.create_index('ix_scheduled_tasks_next_run', 'scheduled_tasks', ['next_run'])
    # Composite for task execution
    op.create_index('ix_scheduled_tasks_enabled_nextrun', 'scheduled_tasks', ['is_enabled', 'next_run'])

    # TASK LOGS
    op.create_index('ix_task_logs_task_id', 'task_logs', ['task_id'])
    op.create_index('ix_task_logs_status', 'task_logs', ['status'])
    op.create_index('ix_task_logs_created_at', 'task_logs', ['created_at'])

    # NOTIFICATIONS - Already has created_at index
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_is_email_sent', 'notifications', ['is_email_sent'])
    # Composite for unread notifications
    op.create_index('ix_notifications_user_unread', 'notifications', ['user_id', 'is_read', 'created_at'])

    # RESOURCE LOGS - Already has created_at index
    op.create_index('ix_resource_logs_server_id', 'resource_logs', ['server_id'])
    # Composite for time-series queries
    op.create_index('ix_resource_logs_server_created', 'resource_logs', ['server_id', 'created_at'])

    # BACKUP LOGS
    op.create_index('ix_backup_logs_server_id', 'backup_logs', ['server_id'])
    op.create_index('ix_backup_logs_backup_type', 'backup_logs', ['backup_type'])
    op.create_index('ix_backup_logs_status', 'backup_logs', ['status'])
    op.create_index('ix_backup_logs_created_at', 'backup_logs', ['created_at'])
    op.create_index('ix_backup_logs_expires_at', 'backup_logs', ['expires_at'])

    # RCON LOGS - Already has created_at index
    op.create_index('ix_rcon_logs_server_id', 'rcon_logs', ['server_id'])
    op.create_index('ix_rcon_logs_user_id', 'rcon_logs', ['user_id'])
    # Composite for server rcon history
    op.create_index('ix_rcon_logs_server_created', 'rcon_logs', ['server_id', 'created_at'])

    # CONFIG HISTORY
    op.create_index('ix_config_history_server_id', 'config_history', ['server_id'])
    op.create_index('ix_config_history_user_id', 'config_history', ['user_id'])
    op.create_index('ix_config_history_config_type', 'config_history', ['config_type'])
    op.create_index('ix_config_history_created_at', 'config_history', ['created_at'])
    # Composite for config audit trail
    op.create_index('ix_config_history_server_type_created', 'config_history',
                   ['server_id', 'config_type', 'created_at'])

    # USER FAVORITES
    op.create_index('ix_user_favorites_user_id', 'user_favorites', ['user_id'])
    op.create_index('ix_user_favorites_server_id', 'user_favorites', ['server_id'])

    # USER PREFERENCES
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])
    op.create_index('ix_user_preferences_theme', 'user_preferences', ['theme'])
    op.create_index('ix_user_preferences_language', 'user_preferences', ['language'])

    # COUPONS - Already has code index
    op.create_index('ix_coupons_is_active', 'coupons', ['is_active'])
    op.create_index('ix_coupons_valid_from', 'coupons', ['valid_from'])
    op.create_index('ix_coupons_valid_until', 'coupons', ['valid_until'])
    # Composite for valid coupons
    op.create_index('ix_coupons_active_valid', 'coupons', ['is_active', 'valid_from', 'valid_until'])

    # INVOICES
    op.create_index('ix_invoices_payment_id', 'invoices', ['payment_id'])
    op.create_index('ix_invoices_user_id', 'invoices', ['user_id'])
    op.create_index('ix_invoices_status', 'invoices', ['status'])
    op.create_index('ix_invoices_created_at', 'invoices', ['created_at'])

    # TRANSACTIONS - Already has user_id index
    op.create_index('ix_transactions_type', 'transactions', ['type'])
    op.create_index('ix_transactions_payment_id', 'transactions', ['payment_id'])
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'])
    # Composite for user transaction history
    op.create_index('ix_transactions_user_created', 'transactions', ['user_id', 'created_at'])

    # BANNERS
    op.create_index('ix_banners_type', 'banners', ['type'])
    op.create_index('ix_banners_position', 'banners', ['position'])
    op.create_index('ix_banners_is_active', 'banners', ['is_active'])
    op.create_index('ix_banners_start_date', 'banners', ['start_date'])
    op.create_index('ix_banners_end_date', 'banners', ['end_date'])
    op.create_index('ix_banners_created_by', 'banners', ['created_by'])
    # Composite for active banners by position
    op.create_index('ix_banners_active_position_order', 'banners',
                   ['is_active', 'position', 'display_order'])
    # Composite for date-based filtering
    op.create_index('ix_banners_active_dates', 'banners', ['is_active', 'start_date', 'end_date'])


def downgrade():
    """Remove all indexes created in upgrade()"""

    # USER MODEL
    op.drop_index('ix_users_role', 'users')
    op.drop_index('ix_users_status', 'users')
    op.drop_index('ix_users_created_at', 'users')
    op.drop_index('ix_users_last_login', 'users')
    op.drop_index('ix_users_email_verified', 'users')
    op.drop_index('ix_users_status_role', 'users')
    op.drop_index('ix_users_elo_desc', 'users')
    op.drop_index('ix_users_kd_ratio_desc', 'users')

    # USER SESSIONS
    op.drop_index('ix_user_sessions_user_id', 'user_sessions')
    op.drop_index('ix_user_sessions_token_hash', 'user_sessions')
    op.drop_index('ix_user_sessions_expires_at', 'user_sessions')
    op.drop_index('ix_user_sessions_is_active', 'user_sessions')
    op.drop_index('ix_user_sessions_user_active', 'user_sessions')
    op.drop_index('ix_user_sessions_last_activity', 'user_sessions')

    # SERVER PACKAGES
    op.drop_index('ix_server_packages_game_type', 'server_packages')
    op.drop_index('ix_server_packages_is_active', 'server_packages')
    op.drop_index('ix_server_packages_is_popular', 'server_packages')
    op.drop_index('ix_server_packages_active_game', 'server_packages')

    # GAME SERVERS
    op.drop_index('ix_game_servers_owner_id', 'game_servers')
    op.drop_index('ix_game_servers_status', 'game_servers')
    op.drop_index('ix_game_servers_game_type', 'game_servers')
    op.drop_index('ix_game_servers_package_id', 'game_servers')
    op.drop_index('ix_game_servers_expires_at', 'game_servers')
    op.drop_index('ix_game_servers_created_at', 'game_servers')
    op.drop_index('ix_game_servers_owner_status', 'game_servers')
    op.drop_index('ix_game_servers_status_expires', 'game_servers')
    op.drop_index('ix_game_servers_auto_renew', 'game_servers')
    op.drop_index('ix_game_servers_expiring_soon', 'game_servers')

    # SERVER ACTIONS
    op.drop_index('ix_server_actions_server_id', 'server_actions')
    op.drop_index('ix_server_actions_user_id', 'server_actions')
    op.drop_index('ix_server_actions_action', 'server_actions')
    op.drop_index('ix_server_actions_created_at', 'server_actions')
    op.drop_index('ix_server_actions_server_created', 'server_actions')

    # PAYMENTS
    op.drop_index('ix_payments_user_id', 'payments')
    op.drop_index('ix_payments_status', 'payments')
    op.drop_index('ix_payments_method', 'payments')
    op.drop_index('ix_payments_server_id', 'payments')
    op.drop_index('ix_payments_created_at', 'payments')
    op.drop_index('ix_payments_external_id', 'payments')
    op.drop_index('ix_payments_coupon_id', 'payments')
    op.drop_index('ix_payments_status_created', 'payments')
    op.drop_index('ix_payments_user_status', 'payments')
    op.drop_index('ix_payments_completed_at', 'payments')

    # BANK TRANSFERS
    op.drop_index('ix_bank_transfers_payment_id', 'bank_transfers')
    op.drop_index('ix_bank_transfers_approved_by', 'bank_transfers')
    op.drop_index('ix_bank_transfers_created_at', 'bank_transfers')

    # FORUM CATEGORIES
    op.drop_index('ix_forum_categories_parent_id', 'forum_categories')
    op.drop_index('ix_forum_categories_is_visible', 'forum_categories')
    op.drop_index('ix_forum_categories_display_order', 'forum_categories')
    op.drop_index('ix_forum_categories_visible_order', 'forum_categories')

    # FORUM TOPICS
    op.drop_index('ix_forum_topics_category_id', 'forum_topics')
    op.drop_index('ix_forum_topics_author_id', 'forum_topics')
    op.drop_index('ix_forum_topics_last_post_by', 'forum_topics')
    op.drop_index('ix_forum_topics_is_pinned', 'forum_topics')
    op.drop_index('ix_forum_topics_is_locked', 'forum_topics')
    op.drop_index('ix_forum_topics_is_featured', 'forum_topics')
    op.drop_index('ix_forum_topics_created_at', 'forum_topics')
    op.drop_index('ix_forum_topics_last_post_at', 'forum_topics')
    op.drop_index('ix_forum_topics_category_pinned_lastpost', 'forum_topics')
    op.drop_index('ix_forum_topics_view_count_desc', 'forum_topics')

    # FORUM POSTS
    op.drop_index('ix_forum_posts_topic_id', 'forum_posts')
    op.drop_index('ix_forum_posts_author_id', 'forum_posts')
    op.drop_index('ix_forum_posts_created_at', 'forum_posts')
    op.drop_index('ix_forum_posts_edited_by', 'forum_posts')
    op.drop_index('ix_forum_posts_is_first_post', 'forum_posts')
    op.drop_index('ix_forum_posts_topic_created', 'forum_posts')

    # FORUM POST LIKES
    op.drop_index('ix_forum_post_likes_post_id', 'forum_post_likes')
    op.drop_index('ix_forum_post_likes_user_id', 'forum_post_likes')
    op.drop_index('ix_forum_post_likes_created_at', 'forum_post_likes')

    # FORUM REPLIES
    op.drop_index('ix_forum_replies_topic_id', 'forum_replies')
    op.drop_index('ix_forum_replies_user_id', 'forum_replies')
    op.drop_index('ix_forum_replies_is_active', 'forum_replies')
    op.drop_index('ix_forum_replies_created_at', 'forum_replies')
    op.drop_index('ix_forum_replies_topic_active', 'forum_replies')

    # SUPPORT TICKETS
    op.drop_index('ix_support_tickets_user_id', 'support_tickets')
    op.drop_index('ix_support_tickets_status', 'support_tickets')
    op.drop_index('ix_support_tickets_priority', 'support_tickets')
    op.drop_index('ix_support_tickets_category', 'support_tickets')
    op.drop_index('ix_support_tickets_server_id', 'support_tickets')
    op.drop_index('ix_support_tickets_assigned_to', 'support_tickets')
    op.drop_index('ix_support_tickets_created_at', 'support_tickets')
    op.drop_index('ix_support_tickets_status_priority', 'support_tickets')
    op.drop_index('ix_support_tickets_assigned_status', 'support_tickets')

    # TICKET MESSAGES
    op.drop_index('ix_ticket_messages_ticket_id', 'ticket_messages')
    op.drop_index('ix_ticket_messages_user_id', 'ticket_messages')
    op.drop_index('ix_ticket_messages_is_staff_reply', 'ticket_messages')
    op.drop_index('ix_ticket_messages_is_read', 'ticket_messages')
    op.drop_index('ix_ticket_messages_created_at', 'ticket_messages')
    op.drop_index('ix_ticket_messages_ticket_read', 'ticket_messages')

    # SYSTEM LOGS
    op.drop_index('ix_system_logs_level', 'system_logs')
    op.drop_index('ix_system_logs_category', 'system_logs')
    op.drop_index('ix_system_logs_user_id', 'system_logs')
    op.drop_index('ix_system_logs_created_at', 'system_logs')
    op.drop_index('ix_system_logs_level_category_created', 'system_logs')

    # ANNOUNCEMENTS
    op.drop_index('ix_announcements_is_active', 'announcements')
    op.drop_index('ix_announcements_show_on_homepage', 'announcements')
    op.drop_index('ix_announcements_created_by', 'announcements')
    op.drop_index('ix_announcements_created_at', 'announcements')
    op.drop_index('ix_announcements_expires_at', 'announcements')
    op.drop_index('ix_announcements_active_homepage', 'announcements')

    # AUDIT LOGS
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')
    op.drop_index('ix_audit_logs_action', 'audit_logs')
    op.drop_index('ix_audit_logs_entity_type', 'audit_logs')
    op.drop_index('ix_audit_logs_entity_id', 'audit_logs')
    op.drop_index('ix_audit_logs_entity_type_id', 'audit_logs')

    # PLUGINS
    op.drop_index('ix_plugins_game_type', 'plugins')
    op.drop_index('ix_plugins_category', 'plugins')
    op.drop_index('ix_plugins_is_active', 'plugins')
    op.drop_index('ix_plugins_is_default', 'plugins')
    op.drop_index('ix_plugins_created_by', 'plugins')
    op.drop_index('ix_plugins_active_game_category', 'plugins')

    # SERVER PLUGINS
    op.drop_index('ix_server_plugins_server_id', 'server_plugins')
    op.drop_index('ix_server_plugins_plugin_id', 'server_plugins')
    op.drop_index('ix_server_plugins_is_enabled', 'server_plugins')
    op.drop_index('ix_server_plugins_installed_by', 'server_plugins')
    op.drop_index('ix_server_plugins_server_enabled', 'server_plugins')

    # SCHEDULED TASKS
    op.drop_index('ix_scheduled_tasks_server_id', 'scheduled_tasks')
    op.drop_index('ix_scheduled_tasks_user_id', 'scheduled_tasks')
    op.drop_index('ix_scheduled_tasks_task_type', 'scheduled_tasks')
    op.drop_index('ix_scheduled_tasks_is_enabled', 'scheduled_tasks')
    op.drop_index('ix_scheduled_tasks_next_run', 'scheduled_tasks')
    op.drop_index('ix_scheduled_tasks_enabled_nextrun', 'scheduled_tasks')

    # TASK LOGS
    op.drop_index('ix_task_logs_task_id', 'task_logs')
    op.drop_index('ix_task_logs_status', 'task_logs')
    op.drop_index('ix_task_logs_created_at', 'task_logs')

    # NOTIFICATIONS
    op.drop_index('ix_notifications_user_id', 'notifications')
    op.drop_index('ix_notifications_type', 'notifications')
    op.drop_index('ix_notifications_is_read', 'notifications')
    op.drop_index('ix_notifications_is_email_sent', 'notifications')
    op.drop_index('ix_notifications_user_unread', 'notifications')

    # RESOURCE LOGS
    op.drop_index('ix_resource_logs_server_id', 'resource_logs')
    op.drop_index('ix_resource_logs_server_created', 'resource_logs')

    # BACKUP LOGS
    op.drop_index('ix_backup_logs_server_id', 'backup_logs')
    op.drop_index('ix_backup_logs_backup_type', 'backup_logs')
    op.drop_index('ix_backup_logs_status', 'backup_logs')
    op.drop_index('ix_backup_logs_created_at', 'backup_logs')
    op.drop_index('ix_backup_logs_expires_at', 'backup_logs')

    # RCON LOGS
    op.drop_index('ix_rcon_logs_server_id', 'rcon_logs')
    op.drop_index('ix_rcon_logs_user_id', 'rcon_logs')
    op.drop_index('ix_rcon_logs_server_created', 'rcon_logs')

    # CONFIG HISTORY
    op.drop_index('ix_config_history_server_id', 'config_history')
    op.drop_index('ix_config_history_user_id', 'config_history')
    op.drop_index('ix_config_history_config_type', 'config_history')
    op.drop_index('ix_config_history_created_at', 'config_history')
    op.drop_index('ix_config_history_server_type_created', 'config_history')

    # USER FAVORITES
    op.drop_index('ix_user_favorites_user_id', 'user_favorites')
    op.drop_index('ix_user_favorites_server_id', 'user_favorites')

    # USER PREFERENCES
    op.drop_index('ix_user_preferences_user_id', 'user_preferences')
    op.drop_index('ix_user_preferences_theme', 'user_preferences')
    op.drop_index('ix_user_preferences_language', 'user_preferences')

    # COUPONS
    op.drop_index('ix_coupons_is_active', 'coupons')
    op.drop_index('ix_coupons_valid_from', 'coupons')
    op.drop_index('ix_coupons_valid_until', 'coupons')
    op.drop_index('ix_coupons_active_valid', 'coupons')

    # INVOICES
    op.drop_index('ix_invoices_payment_id', 'invoices')
    op.drop_index('ix_invoices_user_id', 'invoices')
    op.drop_index('ix_invoices_status', 'invoices')
    op.drop_index('ix_invoices_created_at', 'invoices')

    # TRANSACTIONS
    op.drop_index('ix_transactions_type', 'transactions')
    op.drop_index('ix_transactions_payment_id', 'transactions')
    op.drop_index('ix_transactions_created_at', 'transactions')
    op.drop_index('ix_transactions_user_created', 'transactions')

    # BANNERS
    op.drop_index('ix_banners_type', 'banners')
    op.drop_index('ix_banners_position', 'banners')
    op.drop_index('ix_banners_is_active', 'banners')
    op.drop_index('ix_banners_start_date', 'banners')
    op.drop_index('ix_banners_end_date', 'banners')
    op.drop_index('ix_banners_created_by', 'banners')
    op.drop_index('ix_banners_active_position_order', 'banners')
    op.drop_index('ix_banners_active_dates', 'banners')
