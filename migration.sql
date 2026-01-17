-- ============================================
-- AGTR v6.0 - Forum Database Migration
-- ============================================

-- Forum Kategorileri
CREATE TABLE IF NOT EXISTS forum_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'fas fa-folder',
    order_index INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_slug (slug),
    INDEX idx_order (order_index),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Forum Konuları
CREATE TABLE IF NOT EXISTS forum_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(280) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES forum_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_category (category_id),
    INDEX idx_user (user_id),
    INDEX idx_slug (slug),
    INDEX idx_pinned (is_pinned),
    INDEX idx_active (is_active),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Forum Yanıtları
CREATE TABLE IF NOT EXISTS forum_replies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES forum_topics(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_topic (topic_id),
    INDEX idx_user (user_id),
    INDEX idx_active (is_active),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Örnek Kategoriler
-- ============================================

INSERT INTO forum_categories (name, slug, description, icon, order_index, is_active) VALUES
('Duyurular', 'duyurular', 'Sunucu duyuruları ve önemli haberler', 'fas fa-bullhorn', 0, TRUE),
('Genel Tartışma', 'genel-tartisma', 'Her konuda serbest tartışma alanı', 'fas fa-comments', 1, TRUE),
('Teknik Destek', 'teknik-destek', 'Teknik sorunlar ve çözümler', 'fas fa-headset', 2, TRUE),
('Öneriler', 'oneriler', 'Sunucu için önerileriniz', 'fas fa-lightbulb', 3, TRUE),
('Oyun Rehberleri', 'oyun-rehberleri', 'Half-Life ve CS 1.6 rehberleri', 'fas fa-book', 4, TRUE),
('Takım Bulma', 'takim-bulma', 'Takım arkadaşı arayışı', 'fas fa-users', 5, TRUE),
('Off-Topic', 'off-topic', 'Oyun dışı sohbetler', 'fas fa-coffee', 6, TRUE)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- ============================================
-- Hoşgeldin Konusu (Opsiyonel)
-- ============================================

-- Admin user ID'sini kontrol et (genellikle 1)
INSERT INTO forum_topics (category_id, user_id, title, slug, content, is_pinned, is_active)
SELECT 
    (SELECT id FROM forum_categories WHERE slug = 'duyurular' LIMIT 1),
    1,
    'AGTR Forum''a Hoş Geldiniz!',
    'agtr-foruma-hos-geldiniz',
    'Merhaba AGTR Ailesi!\n\nYeni forum sistemimize hoş geldiniz. Burada oyun deneyimlerinizi paylaşabilir, sorularınızı sorabilir ve diğer oyuncularla iletişim kurabilirsiniz.\n\nKurallarımız:\n- Saygılı olun\n- Spam yapmayın\n- Doğru kategoride konu açın\n\nİyi eğlenceler!',
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM forum_topics WHERE slug = 'agtr-foruma-hos-geldiniz');

-- ============================================
-- Migration tamamlandı
-- ============================================
SELECT 'Forum migration tamamlandı!' AS status;
SELECT COUNT(*) AS kategori_sayisi FROM forum_categories;
SELECT COUNT(*) AS konu_sayisi FROM forum_topics;
