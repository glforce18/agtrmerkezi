-- ============================================
-- AGTR Merkezi - Core Indexes Migration
-- Tarih: 2026-01-24
-- Aciklama: Essential indexes only
-- ============================================

-- forum_topics - Most important for forum performance
CREATE INDEX IF NOT EXISTS idx_forum_topics_created_at
ON forum_topics(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_forum_topics_category
ON forum_topics(category_id);

CREATE INDEX IF NOT EXISTS idx_forum_topics_author
ON forum_topics(author_id);

-- forum_replies - Critical for topic view performance
CREATE INDEX IF NOT EXISTS idx_forum_replies_topic_created
ON forum_replies(topic_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_forum_replies_user
ON forum_replies(user_id);

-- forum_reactions - For reaction counts
CREATE INDEX IF NOT EXISTS idx_forum_reactions_content
ON forum_reactions(content_type, content_id);

CREATE INDEX IF NOT EXISTS idx_forum_reactions_user
ON forum_reactions(user_id);

-- forum_reputation_logs - For reputation calculations
CREATE INDEX IF NOT EXISTS idx_forum_reputation_logs_user
ON forum_reputation_logs(user_id, created_at DESC);

-- forum_drafts - For draft retrieval
CREATE INDEX IF NOT EXISTS idx_forum_drafts_user
ON forum_drafts(user_id, updated_at DESC);

-- forum_bookmarks - For bookmark lists
CREATE INDEX IF NOT EXISTS idx_forum_bookmarks_user
ON forum_bookmarks(user_id, updated_at DESC);

-- forum_subscriptions - For notification queries
CREATE INDEX IF NOT EXISTS idx_forum_subscriptions_user
ON forum_subscriptions(user_id);

CREATE INDEX IF NOT EXISTS idx_forum_subscriptions_topic
ON forum_subscriptions(topic_id);

-- Verification
SELECT 'Core indexes created successfully' as status;
