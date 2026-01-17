-- ============================================================================
-- COMPREHENSIVE DATABASE INDEX CREATION SCRIPT
-- AGTR Merkezi - Performance Optimization
-- Created: 2026-01-16
-- ============================================================================
--
-- This script creates 200+ indexes across all database models
-- Execute during low-traffic period (recommended: maintenance window)
--
-- Estimated execution time: 5-15 minutes depending on data size
-- Estimated disk space required: ~200MB for indexes
--
-- IMPORTANT: Create a backup before executing!
-- ============================================================================

-- ==================== HIGH PRIORITY INDEXES ====================
-- These indexes have the most significant performance impact

-- -------------------- USER MODEL --------------------
CREATE INDEX ix_users_role ON users(role);
CREATE INDEX ix_users_status ON users(status);
CREATE INDEX ix_users_created_at ON users(created_at);
CREATE INDEX ix_users_last_login ON users(last_login);
CREATE INDEX ix_users_email_verified ON users(email_verified);
CREATE INDEX ix_users_status_role ON users(status, role);
CREATE INDEX ix_users_elo_desc ON users(elo DESC);
CREATE INDEX ix_users_kd_ratio_desc ON users(kd_ratio DESC);

-- -------------------- USER SESSIONS --------------------
CREATE INDEX ix_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX ix_user_sessions_token_hash ON user_sessions(token_hash);
CREATE INDEX ix_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX ix_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX ix_user_sessions_user_active ON user_sessions(user_id, is_active, expires_at);
CREATE INDEX ix_user_sessions_last_activity ON user_sessions(last_activity);

-- -------------------- SERVER PACKAGES --------------------
CREATE INDEX ix_server_packages_game_type ON server_packages(game_type);
CREATE INDEX ix_server_packages_is_active ON server_packages(is_active);
CREATE INDEX ix_server_packages_is_popular ON server_packages(is_popular);
CREATE INDEX ix_server_packages_active_game ON server_packages(is_active, game_type, display_order);

-- -------------------- GAME SERVERS --------------------
CREATE INDEX ix_game_servers_owner_id ON game_servers(owner_id);
CREATE INDEX ix_game_servers_status ON game_servers(status);
CREATE INDEX ix_game_servers_game_type ON game_servers(game_type);
CREATE INDEX ix_game_servers_package_id ON game_servers(package_id);
CREATE INDEX ix_game_servers_expires_at ON game_servers(expires_at);
CREATE INDEX ix_game_servers_created_at ON game_servers(created_at);
CREATE INDEX ix_game_servers_owner_status ON game_servers(owner_id, status);
CREATE INDEX ix_game_servers_status_expires ON game_servers(status, expires_at);
CREATE INDEX ix_game_servers_auto_renew ON game_servers(auto_renew, expires_at);
CREATE INDEX ix_game_servers_expiring_soon ON game_servers(status, expires_at, owner_id);

-- -------------------- SERVER ACTIONS --------------------
CREATE INDEX ix_server_actions_server_id ON server_actions(server_id);
CREATE INDEX ix_server_actions_user_id ON server_actions(user_id);
CREATE INDEX ix_server_actions_action ON server_actions(action);
CREATE INDEX ix_server_actions_created_at ON server_actions(created_at);
CREATE INDEX ix_server_actions_server_created ON server_actions(server_id, created_at);

-- -------------------- PAYMENTS --------------------
CREATE INDEX ix_payments_user_id ON payments(user_id);
CREATE INDEX ix_payments_status ON payments(status);
CREATE INDEX ix_payments_method ON payments(method);
CREATE INDEX ix_payments_server_id ON payments(server_id);
CREATE INDEX ix_payments_created_at ON payments(created_at);
CREATE INDEX ix_payments_external_id ON payments(external_id);
CREATE INDEX ix_payments_coupon_id ON payments(coupon_id);
CREATE INDEX ix_payments_status_created ON payments(status, created_at);
CREATE INDEX ix_payments_user_status ON payments(user_id, status);
CREATE INDEX ix_payments_completed_at ON payments(completed_at);

-- -------------------- BANK TRANSFERS --------------------
CREATE INDEX ix_bank_transfers_payment_id ON bank_transfers(payment_id);
CREATE INDEX ix_bank_transfers_approved_by ON bank_transfers(approved_by);
CREATE INDEX ix_bank_transfers_created_at ON bank_transfers(created_at);

-- -------------------- FORUM CATEGORIES --------------------
CREATE INDEX ix_forum_categories_parent_id ON forum_categories(parent_id);
CREATE INDEX ix_forum_categories_is_visible ON forum_categories(is_visible);
CREATE INDEX ix_forum_categories_display_order ON forum_categories(display_order);
CREATE INDEX ix_forum_categories_visible_order ON forum_categories(is_visible, display_order);

-- -------------------- FORUM TOPICS --------------------
CREATE INDEX ix_forum_topics_category_id ON forum_topics(category_id);
CREATE INDEX ix_forum_topics_author_id ON forum_topics(author_id);
CREATE INDEX ix_forum_topics_last_post_by ON forum_topics(last_post_by);
CREATE INDEX ix_forum_topics_is_pinned ON forum_topics(is_pinned);
CREATE INDEX ix_forum_topics_is_locked ON forum_topics(is_locked);
CREATE INDEX ix_forum_topics_is_featured ON forum_topics(is_featured);
CREATE INDEX ix_forum_topics_created_at ON forum_topics(created_at);
CREATE INDEX ix_forum_topics_last_post_at ON forum_topics(last_post_at);
CREATE INDEX ix_forum_topics_category_pinned_lastpost ON forum_topics(category_id, is_pinned, last_post_at DESC);
CREATE INDEX ix_forum_topics_view_count_desc ON forum_topics(view_count DESC);

-- -------------------- FORUM POSTS --------------------
CREATE INDEX ix_forum_posts_topic_id ON forum_posts(topic_id);
CREATE INDEX ix_forum_posts_author_id ON forum_posts(author_id);
CREATE INDEX ix_forum_posts_created_at ON forum_posts(created_at);
CREATE INDEX ix_forum_posts_edited_by ON forum_posts(edited_by);
CREATE INDEX ix_forum_posts_is_first_post ON forum_posts(is_first_post);
CREATE INDEX ix_forum_posts_topic_created ON forum_posts(topic_id, created_at);

-- -------------------- FORUM POST LIKES --------------------
CREATE INDEX ix_forum_post_likes_post_id ON forum_post_likes(post_id);
CREATE INDEX ix_forum_post_likes_user_id ON forum_post_likes(user_id);
CREATE INDEX ix_forum_post_likes_created_at ON forum_post_likes(created_at);

-- -------------------- FORUM REPLIES --------------------
CREATE INDEX ix_forum_replies_topic_id ON forum_replies(topic_id);
CREATE INDEX ix_forum_replies_user_id ON forum_replies(user_id);
CREATE INDEX ix_forum_replies_is_active ON forum_replies(is_active);
CREATE INDEX ix_forum_replies_created_at ON forum_replies(created_at);
CREATE INDEX ix_forum_replies_topic_active ON forum_replies(topic_id, is_active, created_at);

-- -------------------- SUPPORT TICKETS --------------------
CREATE INDEX ix_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX ix_support_tickets_status ON support_tickets(status);
CREATE INDEX ix_support_tickets_priority ON support_tickets(priority);
CREATE INDEX ix_support_tickets_category ON support_tickets(category);
CREATE INDEX ix_support_tickets_server_id ON support_tickets(server_id);
CREATE INDEX ix_support_tickets_assigned_to ON support_tickets(assigned_to);
CREATE INDEX ix_support_tickets_created_at ON support_tickets(created_at);
CREATE INDEX ix_support_tickets_status_priority ON support_tickets(status, priority, created_at);
CREATE INDEX ix_support_tickets_assigned_status ON support_tickets(assigned_to, status);

-- -------------------- TICKET MESSAGES --------------------
CREATE INDEX ix_ticket_messages_ticket_id ON ticket_messages(ticket_id);
CREATE INDEX ix_ticket_messages_user_id ON ticket_messages(user_id);
CREATE INDEX ix_ticket_messages_is_staff_reply ON ticket_messages(is_staff_reply);
CREATE INDEX ix_ticket_messages_is_read ON ticket_messages(is_read);
CREATE INDEX ix_ticket_messages_created_at ON ticket_messages(created_at);
CREATE INDEX ix_ticket_messages_ticket_read ON ticket_messages(ticket_id, is_read);


-- ==================== MEDIUM PRIORITY INDEXES ====================
-- These indexes improve secondary operations and reporting

-- -------------------- SYSTEM LOGS --------------------
CREATE INDEX ix_system_logs_level ON system_logs(level);
CREATE INDEX ix_system_logs_category ON system_logs(category);
CREATE INDEX ix_system_logs_user_id ON system_logs(user_id);
CREATE INDEX ix_system_logs_created_at ON system_logs(created_at);
CREATE INDEX ix_system_logs_level_category_created ON system_logs(level, category, created_at);

-- -------------------- ANNOUNCEMENTS --------------------
CREATE INDEX ix_announcements_is_active ON announcements(is_active);
CREATE INDEX ix_announcements_show_on_homepage ON announcements(show_on_homepage);
CREATE INDEX ix_announcements_created_by ON announcements(created_by);
CREATE INDEX ix_announcements_created_at ON announcements(created_at);
CREATE INDEX ix_announcements_expires_at ON announcements(expires_at);
CREATE INDEX ix_announcements_active_homepage ON announcements(is_active, show_on_homepage, created_at);

-- -------------------- AUDIT LOGS --------------------
CREATE INDEX ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX ix_audit_logs_action ON audit_logs(action);
CREATE INDEX ix_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX ix_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX ix_audit_logs_entity_type_id ON audit_logs(entity_type, entity_id, created_at);

-- -------------------- PLUGINS --------------------
CREATE INDEX ix_plugins_game_type ON plugins(game_type);
CREATE INDEX ix_plugins_category ON plugins(category);
CREATE INDEX ix_plugins_is_active ON plugins(is_active);
CREATE INDEX ix_plugins_is_default ON plugins(is_default);
CREATE INDEX ix_plugins_created_by ON plugins(created_by);
CREATE INDEX ix_plugins_active_game_category ON plugins(is_active, game_type, category);

-- -------------------- SERVER PLUGINS --------------------
CREATE INDEX ix_server_plugins_server_id ON server_plugins(server_id);
CREATE INDEX ix_server_plugins_plugin_id ON server_plugins(plugin_id);
CREATE INDEX ix_server_plugins_is_enabled ON server_plugins(is_enabled);
CREATE INDEX ix_server_plugins_installed_by ON server_plugins(installed_by);
CREATE INDEX ix_server_plugins_server_enabled ON server_plugins(server_id, is_enabled);

-- -------------------- SCHEDULED TASKS --------------------
CREATE INDEX ix_scheduled_tasks_server_id ON scheduled_tasks(server_id);
CREATE INDEX ix_scheduled_tasks_user_id ON scheduled_tasks(user_id);
CREATE INDEX ix_scheduled_tasks_task_type ON scheduled_tasks(task_type);
CREATE INDEX ix_scheduled_tasks_is_enabled ON scheduled_tasks(is_enabled);
CREATE INDEX ix_scheduled_tasks_next_run ON scheduled_tasks(next_run);
CREATE INDEX ix_scheduled_tasks_enabled_nextrun ON scheduled_tasks(is_enabled, next_run);

-- -------------------- TASK LOGS --------------------
CREATE INDEX ix_task_logs_task_id ON task_logs(task_id);
CREATE INDEX ix_task_logs_status ON task_logs(status);
CREATE INDEX ix_task_logs_created_at ON task_logs(created_at);

-- -------------------- NOTIFICATIONS --------------------
CREATE INDEX ix_notifications_user_id ON notifications(user_id);
CREATE INDEX ix_notifications_type ON notifications(type);
CREATE INDEX ix_notifications_is_read ON notifications(is_read);
CREATE INDEX ix_notifications_is_email_sent ON notifications(is_email_sent);
CREATE INDEX ix_notifications_user_unread ON notifications(user_id, is_read, created_at);

-- -------------------- RESOURCE LOGS --------------------
CREATE INDEX ix_resource_logs_server_id ON resource_logs(server_id);
CREATE INDEX ix_resource_logs_server_created ON resource_logs(server_id, created_at);

-- -------------------- BACKUP LOGS --------------------
CREATE INDEX ix_backup_logs_server_id ON backup_logs(server_id);
CREATE INDEX ix_backup_logs_backup_type ON backup_logs(backup_type);
CREATE INDEX ix_backup_logs_status ON backup_logs(status);
CREATE INDEX ix_backup_logs_created_at ON backup_logs(created_at);
CREATE INDEX ix_backup_logs_expires_at ON backup_logs(expires_at);

-- -------------------- RCON LOGS --------------------
CREATE INDEX ix_rcon_logs_server_id ON rcon_logs(server_id);
CREATE INDEX ix_rcon_logs_user_id ON rcon_logs(user_id);
CREATE INDEX ix_rcon_logs_server_created ON rcon_logs(server_id, created_at);

-- -------------------- CONFIG HISTORY --------------------
CREATE INDEX ix_config_history_server_id ON config_history(server_id);
CREATE INDEX ix_config_history_user_id ON config_history(user_id);
CREATE INDEX ix_config_history_config_type ON config_history(config_type);
CREATE INDEX ix_config_history_created_at ON config_history(created_at);
CREATE INDEX ix_config_history_server_type_created ON config_history(server_id, config_type, created_at);

-- -------------------- USER FAVORITES --------------------
CREATE INDEX ix_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX ix_user_favorites_server_id ON user_favorites(server_id);

-- -------------------- USER PREFERENCES --------------------
CREATE INDEX ix_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX ix_user_preferences_theme ON user_preferences(theme);
CREATE INDEX ix_user_preferences_language ON user_preferences(language);

-- -------------------- COUPONS --------------------
CREATE INDEX ix_coupons_is_active ON coupons(is_active);
CREATE INDEX ix_coupons_valid_from ON coupons(valid_from);
CREATE INDEX ix_coupons_valid_until ON coupons(valid_until);
CREATE INDEX ix_coupons_active_valid ON coupons(is_active, valid_from, valid_until);

-- -------------------- INVOICES --------------------
CREATE INDEX ix_invoices_payment_id ON invoices(payment_id);
CREATE INDEX ix_invoices_user_id ON invoices(user_id);
CREATE INDEX ix_invoices_status ON invoices(status);
CREATE INDEX ix_invoices_created_at ON invoices(created_at);

-- -------------------- TRANSACTIONS --------------------
CREATE INDEX ix_transactions_type ON transactions(type);
CREATE INDEX ix_transactions_payment_id ON transactions(payment_id);
CREATE INDEX ix_transactions_created_at ON transactions(created_at);
CREATE INDEX ix_transactions_user_created ON transactions(user_id, created_at);

-- -------------------- BANNERS --------------------
CREATE INDEX ix_banners_type ON banners(type);
CREATE INDEX ix_banners_position ON banners(position);
CREATE INDEX ix_banners_is_active ON banners(is_active);
CREATE INDEX ix_banners_start_date ON banners(start_date);
CREATE INDEX ix_banners_end_date ON banners(end_date);
CREATE INDEX ix_banners_created_by ON banners(created_by);
CREATE INDEX ix_banners_active_position_order ON banners(is_active, position, display_order);
CREATE INDEX ix_banners_active_dates ON banners(is_active, start_date, end_date);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify all indexes were created
SELECT
    TABLE_NAME,
    INDEX_NAME,
    SEQ_IN_INDEX,
    COLUMN_NAME,
    INDEX_TYPE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
    AND INDEX_NAME LIKE 'ix_%'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- Check index sizes
SELECT
    TABLE_NAME,
    INDEX_NAME,
    ROUND(STAT_VALUE * @@innodb_page_size / 1024 / 1024, 2) AS size_mb
FROM mysql.innodb_index_stats
WHERE database_name = DATABASE()
    AND INDEX_NAME LIKE 'ix_%'
ORDER BY STAT_VALUE DESC
LIMIT 20;

-- Count total indexes created
SELECT
    COUNT(DISTINCT CONCAT(TABLE_NAME, '.', INDEX_NAME)) AS total_indexes
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
    AND INDEX_NAME LIKE 'ix_%';

-- ============================================================================
-- POST-CREATION MAINTENANCE
-- ============================================================================

-- Analyze all tables to update statistics (run after index creation)
ANALYZE TABLE
    users, user_sessions, server_packages, game_servers, server_actions,
    payments, bank_transfers, forum_categories, forum_topics, forum_posts,
    forum_post_likes, forum_replies, support_tickets, ticket_messages,
    system_logs, announcements, audit_logs, plugins, server_plugins,
    scheduled_tasks, task_logs, notifications, resource_logs, backup_logs,
    rcon_logs, config_history, user_favorites, user_preferences,
    coupons, invoices, transactions, banners;

-- ============================================================================
-- PERFORMANCE TESTING QUERIES
-- ============================================================================

-- Test 1: User login query (should use ix_users_email)
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com' AND status = 'active';

-- Test 2: Server listing (should use ix_game_servers_owner_status)
EXPLAIN SELECT * FROM game_servers WHERE owner_id = 1 AND status = 'running';

-- Test 3: Payment history (should use ix_payments_user_status)
EXPLAIN SELECT * FROM payments WHERE user_id = 1 AND status = 'completed' ORDER BY created_at DESC;

-- Test 4: Forum topic listing (should use ix_forum_topics_category_pinned_lastpost)
EXPLAIN SELECT * FROM forum_topics WHERE category_id = 1 ORDER BY is_pinned DESC, last_post_at DESC;

-- Test 5: Support ticket queue (should use ix_support_tickets_status_priority)
EXPLAIN SELECT * FROM support_tickets WHERE status = 'open' ORDER BY priority DESC, created_at ASC;

-- Test 6: Unread notifications (should use ix_notifications_user_unread)
EXPLAIN SELECT * FROM notifications WHERE user_id = 1 AND is_read = 0 ORDER BY created_at DESC;

-- Test 7: Expiring servers (should use ix_game_servers_expiring_soon)
EXPLAIN SELECT * FROM game_servers WHERE status = 'running' AND expires_at < DATE_ADD(NOW(), INTERVAL 7 DAY);

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

/*
-- WARNING: This will drop all indexes created by this script
-- Only use if you need to completely rollback the changes

DROP INDEX ix_users_role ON users;
DROP INDEX ix_users_status ON users;
DROP INDEX ix_users_created_at ON users;
DROP INDEX ix_users_last_login ON users;
DROP INDEX ix_users_email_verified ON users;
DROP INDEX ix_users_status_role ON users;
DROP INDEX ix_users_elo_desc ON users;
DROP INDEX ix_users_kd_ratio_desc ON users;

-- ... (continue for all indexes)

-- See the migration file downgrade() function for complete rollback script
*/

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
