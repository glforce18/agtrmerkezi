-- ============================================
-- AGTR Merkezi - Safe Indexes Migration
-- Tarih: 2026-01-24
-- Aciklama: Only indexes for existing columns
-- ============================================

-- forum_drafts indexleri
CREATE INDEX IF NOT EXISTS idx_forum_drafts_user_updated
ON forum_drafts(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_forum_drafts_encrypted
ON forum_drafts(user_id, is_encrypted);

-- forum_reactions indexleri
CREATE INDEX IF NOT EXISTS idx_forum_reactions_content_created
ON forum_reactions(content_type, content_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_forum_reactions_user_content
ON forum_reactions(user_id, content_type, content_id);

-- forum_polls indexleri
CREATE INDEX IF NOT EXISTS idx_forum_polls_topic
ON forum_polls(topic_id);

CREATE INDEX IF NOT EXISTS idx_forum_polls_active
ON forum_polls(is_active, ends_at);

-- forum_poll_votes indexleri
CREATE INDEX IF NOT EXISTS idx_forum_poll_votes_poll
ON forum_poll_votes(poll_id, user_id);

-- forum_reputation_logs indexleri
CREATE INDEX IF NOT EXISTS idx_forum_reputation_logs_user_created
ON forum_reputation_logs(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_forum_reputation_logs_source
ON forum_reputation_logs(source_user_id, created_at DESC);

-- forum_bookmarks indexleri
CREATE INDEX IF NOT EXISTS idx_forum_bookmarks_user_updated
ON forum_bookmarks(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_forum_bookmarks_topic
ON forum_bookmarks(topic_id, user_id);

-- forum_subscriptions indexleri
CREATE INDEX IF NOT EXISTS idx_forum_subscriptions_user_active
ON forum_subscriptions(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_forum_subscriptions_topic_active
ON forum_subscriptions(topic_id, is_active);

-- forum_topics indexleri (Core)
CREATE INDEX IF NOT EXISTS idx_forum_topics_active_pinned_created
ON forum_topics(is_active, is_pinned DESC, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_forum_topics_category_active_created
ON forum_topics(category_id, is_active, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_forum_topics_author_active
ON forum_topics(author_id, is_active);

CREATE INDEX IF NOT EXISTS idx_forum_topics_slug_active
ON forum_topics(slug, is_active);

-- forum_replies indexleri
CREATE INDEX IF NOT EXISTS idx_forum_replies_topic_active_created
ON forum_replies(topic_id, is_active, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_forum_replies_user_active
ON forum_replies(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_forum_replies_parent
ON forum_replies(parent_reply_id, topic_id);

-- forum_reputation indexleri
CREATE INDEX IF NOT EXISTS idx_forum_reputation_points
ON forum_reputation(total_points DESC);

-- forum_badges indexleri
CREATE INDEX IF NOT EXISTS idx_forum_badges_active_rarity
ON forum_badges(is_active, rarity);

-- forum_topic_tags indexleri
CREATE INDEX IF NOT EXISTS idx_forum_topic_tags_tag
ON forum_topic_tags(tag_id);

CREATE INDEX IF NOT EXISTS idx_forum_topic_tags_topic
ON forum_topic_tags(topic_id);

-- forum_mentions indexleri
CREATE INDEX IF NOT EXISTS idx_forum_mentions_user_read
ON forum_mentions(mentioned_user_id, is_read);

CREATE INDEX IF NOT EXISTS idx_forum_mentions_created
ON forum_mentions(created_at DESC);

-- forum_reports indexleri
CREATE INDEX IF NOT EXISTS idx_forum_reports_content
ON forum_reports(content_type, content_id);

CREATE INDEX IF NOT EXISTS idx_forum_reports_status_created
ON forum_reports(status, created_at DESC);

-- forum_bans indexleri
CREATE INDEX IF NOT EXISTS idx_forum_bans_user_active
ON forum_bans(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_forum_bans_expires
ON forum_bans(expires_at, is_active);

-- forum_categories indexleri
CREATE INDEX IF NOT EXISTS idx_forum_categories_visible_order
ON forum_categories(is_visible, display_order);

-- forum_tags indexleri
CREATE INDEX IF NOT EXISTS idx_forum_tags_slug
ON forum_tags(slug);

-- forum_topic_templates indexleri
CREATE INDEX IF NOT EXISTS idx_forum_topic_templates_active_usage
ON forum_topic_templates(is_active, usage_count DESC);

-- Verify indexes created
SELECT
    'Migration completed' as status,
    COUNT(*) as indexes_created
FROM information_schema.statistics
WHERE table_schema = 'agtrmerkezi'
AND table_name LIKE 'forum%'
AND index_name LIKE 'idx_forum%';
