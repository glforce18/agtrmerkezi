-- ============================================
-- AGTR v6.0 - Forum Badges Migration
-- Forum rozet sistemi icin tablo ve varsayilan veriler
-- ============================================

-- Forum Badge Table
CREATE TABLE IF NOT EXISTS forum_badges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    requirement_type VARCHAR(50),
    requirement_value INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_forum_badges_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Forum Badges Table (many-to-many)
CREATE TABLE IF NOT EXISTS user_forum_badges (
    user_id INT NOT NULL,
    badge_id INT NOT NULL,
    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES forum_badges(id) ON DELETE CASCADE,
    INDEX idx_user_badges_user (user_id),
    INDEX idx_user_badges_badge (badge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ensure users table has reputation column
-- (This may already exist based on the model, but adding for safety)
ALTER TABLE users ADD COLUMN IF NOT EXISTS reputation INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS forum_post_count INT DEFAULT 0;

-- Create index on reputation for leaderboard queries
CREATE INDEX IF NOT EXISTS idx_users_reputation ON users(reputation DESC);

-- Insert Default Badges
INSERT INTO forum_badges (name, slug, description, icon, color, requirement_type, requirement_value)
VALUES
    ('Ilk Adim', 'ilk-adim', 'Ilk konunu olustur', 'star', '#4CAF50', 'topics_count', 1),
    ('Yardimsever', 'yardimsever', '10 yanit yaz', 'heart', '#2196F3', 'replies_count', 10),
    ('Populer', 'populer', '100 begeni al', 'thumbs-up', '#FF9800', 'likes_received', 100),
    ('Uzman', 'uzman', '50 konu olustur', 'award', '#9C27B0', 'topics_count', 50),
    ('Efsane', 'efsane', '500 yanit yaz', 'crown', '#F44336', 'replies_count', 500)
ON DUPLICATE KEY UPDATE
    description = VALUES(description),
    icon = VALUES(icon),
    color = VALUES(color),
    requirement_type = VALUES(requirement_type),
    requirement_value = VALUES(requirement_value);

-- ============================================
-- Additional Gamification Badges
-- ============================================

-- Achievement badges for engagement milestones
INSERT INTO forum_badges (name, slug, description, icon, color, requirement_type, requirement_value)
VALUES
    ('Usta Yazici', 'usta-yazici', '100 konu olustur', 'edit', '#673AB7', 'topics_count', 100),
    ('Sosyal Kelebek', 'sosyal-kelebek', '50 yanit yaz', 'users', '#00BCD4', 'replies_count', 50),
    ('Topluluk Lideri', 'topluluk-lideri', '1000 yanit yaz', 'flag', '#E91E63', 'replies_count', 1000),
    ('Ikonik', 'ikonik', '500 begeni al', 'trophy', '#FFD700', 'likes_received', 500)
ON DUPLICATE KEY UPDATE
    description = VALUES(description),
    icon = VALUES(icon),
    color = VALUES(color),
    requirement_type = VALUES(requirement_type),
    requirement_value = VALUES(requirement_value);
