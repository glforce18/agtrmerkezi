-- ============================================
-- AGTR Merkezi - Missing Indexes Migration
-- Tarih: 2026-01-24
-- Aciklama: Performans iyilestirme icin eksik indexler
-- ============================================

-- forum_drafts tablosu indexleri
-- Pagination icin updated_at (get_all_drafts query'sinde kullanilir)
CREATE INDEX IF NOT EXISTS idx_forum_drafts_user_updated
ON forum_drafts(user_id, updated_at DESC);

-- Device sync icin (device_id not stored in DB, validation happens in-memory)
-- CREATE INDEX IF NOT EXISTS idx_forum_drafts_device
-- ON forum_drafts(user_id, device_id);

-- forum_reactions tablosu indexleri
-- Sorting by newest reactions
CREATE INDEX IF NOT EXISTS idx_forum_reactions_content_created
ON forum_reactions(content_type, content_id, created_at DESC);

-- User's reactions lookup
CREATE INDEX IF NOT EXISTS idx_forum_reactions_user
ON forum_reactions(user_id, created_at DESC);

-- spam_logs tablosu indexleri
-- Admin dashboard queries
CREATE INDEX IF NOT EXISTS idx_spam_logs_created
ON spam_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_spam_logs_user_created
ON spam_logs(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_spam_logs_rule
ON spam_logs(rule_id, created_at DESC);

-- forum_mentions tablosu indexleri
-- Unread mentions query optimization
CREATE INDEX IF NOT EXISTS idx_forum_mentions_user_read
ON forum_mentions(user_id, is_read, created_at DESC);

-- forum_subscriptions tablosu indexleri
-- Check if user subscribed to topic
CREATE INDEX IF NOT EXISTS idx_forum_subscriptions_user_topic
ON forum_subscriptions(user_id, topic_id);

-- Get all topic subscribers
CREATE INDEX IF NOT EXISTS idx_forum_subscriptions_topic
ON forum_subscriptions(topic_id, user_id);

-- forum_bookmarks tablosu indexleri
-- User bookmarks pagination
CREATE INDEX IF NOT EXISTS idx_forum_bookmarks_user_created
ON forum_bookmarks(user_id, created_at DESC);

-- Check bookmark status
CREATE INDEX IF NOT EXISTS idx_forum_bookmarks_user_topic
ON forum_bookmarks(user_id, topic_id);

-- forum_polls tablosu indexleri
-- Get poll by topic
CREATE INDEX IF NOT EXISTS idx_forum_polls_topic
ON forum_polls(topic_id);

-- forum_poll_votes tablosu indexleri
-- User's votes on poll
CREATE INDEX IF NOT EXISTS idx_forum_poll_votes_poll_user
ON forum_poll_votes(poll_id, user_id);

-- Count distinct voters
CREATE INDEX IF NOT EXISTS idx_forum_poll_votes_poll
ON forum_poll_votes(poll_id, user_id);

-- forum_reputation_logs tablosu indexleri
-- User reputation history
CREATE INDEX IF NOT EXISTS idx_forum_reputation_logs_user_created
ON forum_reputation_logs(user_id, created_at DESC);

-- Reputation transactions by type
CREATE INDEX IF NOT EXISTS idx_forum_reputation_logs_user_reason
ON forum_reputation_logs(user_id, reason, created_at DESC);

-- forum_bans tablosu indexleri
-- Active bans lookup
CREATE INDEX IF NOT EXISTS idx_forum_bans_user_expires
ON forum_bans(user_id, expires_at);

-- moderation_logs tablosu indexleri
-- Moderator activity
CREATE INDEX IF NOT EXISTS idx_moderation_logs_moderator
ON moderation_logs(moderator_id, created_at DESC);

-- Content moderation history
CREATE INDEX IF NOT EXISTS idx_moderation_logs_content
ON moderation_logs(content_type, content_id, created_at DESC);

-- Target user actions
CREATE INDEX IF NOT EXISTS idx_moderation_logs_target
ON moderation_logs(target_user_id, created_at DESC);

-- forum_reports tablosu indexleri
-- Pending reports for admin dashboard
CREATE INDEX IF NOT EXISTS idx_forum_reports_status_created
ON forum_reports(status, created_at DESC);

-- Reports by content
CREATE INDEX IF NOT EXISTS idx_forum_reports_content
ON forum_reports(content_type, content_id);

-- forum_topic_templates tablosu indexleri
-- Category templates
CREATE INDEX IF NOT EXISTS idx_forum_topic_templates_category
ON forum_topic_templates(category_id, is_active);

-- Active templates
CREATE INDEX IF NOT EXISTS idx_forum_topic_templates_active
ON forum_topic_templates(is_active, created_at DESC);

-- forum_badges tablosu indexleri
-- Active badges
CREATE INDEX IF NOT EXISTS idx_forum_badges_active
ON forum_badges(is_active, display_order);

-- user_forum_badges tablosu indexleri
-- User's badges
CREATE INDEX IF NOT EXISTS idx_user_forum_badges_user
ON user_forum_badges(user_id, earned_at DESC);

-- Badge leaderboard (who has this badge)
CREATE INDEX IF NOT EXISTS idx_user_forum_badges_badge
ON user_forum_badges(badge_id, earned_at DESC);

-- forum_reputation tablosu indexleri
-- Leaderboard queries
CREATE INDEX IF NOT EXISTS idx_forum_reputation_points
ON forum_reputation(total_points DESC);

CREATE INDEX IF NOT EXISTS idx_forum_reputation_level
ON forum_reputation(level DESC, total_points DESC);

-- Weekly activity tracking
CREATE INDEX IF NOT EXISTS idx_forum_reputation_week
ON forum_reputation(week_start, total_points DESC);

-- ============================================
-- Verification Queries
-- ============================================

-- Check which indexes were created
SELECT
    'Index created successfully' as status,
    COUNT(*) as total_indexes
FROM information_schema.statistics
WHERE table_schema = DATABASE()
AND index_name LIKE 'idx_%'
AND table_name IN (
    'forum_drafts', 'forum_reactions', 'spam_logs', 'forum_mentions',
    'forum_subscriptions', 'forum_bookmarks', 'forum_polls', 'forum_poll_votes',
    'forum_reputation_logs', 'forum_bans', 'moderation_logs', 'forum_reports',
    'forum_topic_templates', 'forum_badges', 'user_forum_badges', 'forum_reputation'
);
