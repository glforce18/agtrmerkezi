-- ============================================
-- AGTR Merkezi - Draft Encryption Migration
-- Tarih: 2026-01-24
-- Aciklama: Draft encryption support
-- ============================================

-- Add is_encrypted column to forum_drafts
ALTER TABLE forum_drafts
ADD COLUMN IF NOT EXISTS is_encrypted BOOLEAN DEFAULT FALSE
COMMENT 'Whether draft content is encrypted';

-- Add index for encrypted drafts query
CREATE INDEX IF NOT EXISTS idx_forum_drafts_encrypted
ON forum_drafts(user_id, is_encrypted);

-- Verify
SELECT
    'Migration completed' as status,
    COUNT(*) as total_drafts,
    SUM(CASE WHEN is_encrypted = TRUE THEN 1 ELSE 0 END) as encrypted_drafts
FROM forum_drafts;
