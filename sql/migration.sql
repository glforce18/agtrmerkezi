-- AGTR Merkezi v5.4 Database Migration
-- =====================================
-- Bu dosyayı çalıştırın: mysql -u root -p agtrmerkezi < migration.sql

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================
-- SITE ASSETS TABLE
-- Logo, görsel, animasyon yönetimi
-- =====================================
CREATE TABLE IF NOT EXISTS `site_assets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT 'Asset adı',
    `slug` VARCHAR(100) UNIQUE NOT NULL COMMENT 'URL-friendly slug',
    `description` TEXT COMMENT 'Açıklama',
    
    -- Dosya bilgileri
    `original_filename` VARCHAR(255) COMMENT 'Orijinal dosya adı',
    `original_path` VARCHAR(500) COMMENT 'Orijinal dosya yolu',
    `processed_path` VARCHAR(500) COMMENT 'İşlenmiş PNG yolu',
    `thumbnail_path` VARCHAR(500) COMMENT 'Thumbnail yolu',
    
    -- Metadata
    `asset_type` ENUM('logo', 'icon', 'banner', 'mascot', 'background', 'animation', 'other') DEFAULT 'other',
    `status` ENUM('processing', 'ready', 'failed') DEFAULT 'processing',
    `mime_type` VARCHAR(50),
    `file_size` INT UNSIGNED COMMENT 'Bytes',
    `width` INT UNSIGNED,
    `height` INT UNSIGNED,
    
    -- Arka plan silme
    `bg_removed` BOOLEAN DEFAULT FALSE COMMENT 'Arka plan silindi mi',
    `bg_color` VARCHAR(20) COMMENT 'Tespit edilen arka plan rengi',
    
    -- Animasyon
    `is_animated` BOOLEAN DEFAULT FALSE,
    `animation_type` VARCHAR(50) COMMENT 'bounce, pulse, rotate, float, glow, shake, swing, fade-pulse',
    `animation_duration` FLOAT DEFAULT 2.0 COMMENT 'Saniye',
    `animation_css` TEXT COMMENT 'Özel CSS animasyonu',
    
    -- Kullanım
    `usage_locations` JSON COMMENT '["header", "footer", "home_hero"]',
    
    -- Yönetim
    `is_active` BOOLEAN DEFAULT TRUE,
    `display_order` INT DEFAULT 0,
    `uploaded_by` INT COMMENT 'Yükleyen admin ID',
    
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_slug` (`slug`),
    INDEX `idx_type` (`asset_type`),
    INDEX `idx_status` (`status`),
    INDEX `idx_active` (`is_active`),
    CONSTRAINT `fk_asset_uploader` FOREIGN KEY (`uploaded_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================
-- FAQ ITEMS TABLE
-- Sıkça Sorulan Sorular
-- =====================================
CREATE TABLE IF NOT EXISTS `faq_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `question` VARCHAR(500) NOT NULL,
    `answer` TEXT NOT NULL,
    `category` VARCHAR(100) DEFAULT 'Genel',
    `icon` VARCHAR(50) COMMENT 'Emoji veya icon class',
    
    `is_active` BOOLEAN DEFAULT TRUE,
    `display_order` INT DEFAULT 0,
    `view_count` INT UNSIGNED DEFAULT 0,
    `helpful_count` INT UNSIGNED DEFAULT 0,
    
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_category` (`category`),
    INDEX `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================
-- STATIC PAGES TABLE
-- TOS, Privacy, vb statik sayfalar
-- =====================================
CREATE TABLE IF NOT EXISTS `static_pages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `slug` VARCHAR(100) UNIQUE NOT NULL COMMENT 'URL slug (tos, privacy, about)',
    `title` VARCHAR(200) NOT NULL,
    `content` LONGTEXT NOT NULL COMMENT 'HTML içerik',
    `meta_description` VARCHAR(300),
    
    `is_active` BOOLEAN DEFAULT TRUE,
    `show_in_footer` BOOLEAN DEFAULT TRUE,
    
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `updated_by` INT,
    
    INDEX `idx_slug` (`slug`),
    CONSTRAINT `fk_page_updater` FOREIGN KEY (`updated_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================
-- CONTACT MESSAGES TABLE
-- İletişim formu mesajları
-- =====================================
CREATE TABLE IF NOT EXISTS `contact_messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `subject` VARCHAR(200) NOT NULL,
    `message` TEXT NOT NULL,
    
    `ip_address` VARCHAR(45),
    `user_agent` VARCHAR(500),
    `user_id` INT COMMENT 'Giriş yapmış kullanıcı',
    
    `is_read` BOOLEAN DEFAULT FALSE,
    `is_replied` BOOLEAN DEFAULT FALSE,
    `replied_at` DATETIME,
    `replied_by` INT,
    `reply_content` TEXT,
    
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX `idx_read` (`is_read`),
    INDEX `idx_email` (`email`),
    CONSTRAINT `fk_contact_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_contact_replier` FOREIGN KEY (`replied_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================
-- VARSAYILAN FAQ VERİLERİ
-- =====================================
INSERT INTO `faq_items` (`question`, `answer`, `category`, `icon`, `display_order`) VALUES
('Nasıl kayıt olurum?', 
 'Sağ üstteki <strong>"Kayıt Ol"</strong> butonuna tıklayarak kayıt formunu doldurun.<br><br>
  <ol>
    <li>Kullanıcı adı seçin (3-20 karakter)</li>
    <li>Geçerli e-posta adresi girin</li>
    <li>Güçlü bir şifre belirleyin</li>
    <li>Kullanım şartlarını kabul edin</li>
  </ol>
  E-posta doğrulaması sonrası hesabınız aktif olur.', 
 'Hesap', '👤', 1),

('Sunucu nasıl kiralarım?', 
 '<a href="/servers">Sunucular</a> sayfasından istediğiniz paketi seçin:<br><br>
  <ol>
    <li>Oyun türü seçin (Half-Life, CS 1.6, AG)</li>
    <li>Slot sayısını belirleyin</li>
    <li>Süreyi seçin (1-12 ay)</li>
    <li>Bakiye yükleyin ve satın alın</li>
  </ol>
  Sunucunuz <strong>1-2 dakika</strong> içinde hazır!', 
 'Sunucu', '🖥️', 2),

('Ödeme yöntemleri nelerdir?', 
 'İki farklı ödeme yöntemi sunuyoruz:<br><br>
  <ul>
    <li><strong>Kredi/Banka Kartı:</strong> iyzico altyapısı ile güvenli ödeme</li>
    <li><strong>Havale/EFT:</strong> Banka havalesi ile ödeme (1-24 saat onay)</li>
  </ul>
  Tüm fiyatlarımız KDV dahildir.', 
 'Ödeme', '💳', 3),

('Şifremi unuttum ne yapmalıyım?', 
 'Şifrenizi sıfırlamak için:<br><br>
  <ol>
    <li><a href="/login">Giriş sayfasındaki</a> "Şifremi Unuttum" linkine tıklayın</li>
    <li>Kayıtlı e-posta adresinizi girin</li>
    <li>E-postanıza gelen linke tıklayın</li>
    <li>Yeni şifrenizi belirleyin</li>
  </ol>
  Link 1 saat geçerlidir.', 
 'Hesap', '🔑', 4),

('Anti-Cheat nasıl çalışır?', 
 'AGTR Anti-Cheat sistemi çok katmanlı koruma sağlar:<br><br>
  <ul>
    <li><strong>Process Tarama:</strong> Şüpheli programları tespit eder</li>
    <li><strong>DLL Kontrolü:</strong> Oyun dosyalarını doğrular</li>
    <li><strong>Screenshot:</strong> Oyun içi görüntü yakalar</li>
    <li><strong>Memory Scan:</strong> Bellek manipülasyonlarını tespit eder</li>
  </ul>
  Tespit edilen hile kullananlar <strong>otomatik banlanır</strong>.', 
 'Sunucu', '🛡️', 5),

('İade alabilir miyim?', 
 'İade politikamız:<br><br>
  <ul>
    <li><strong>İlk 24 saat:</strong> Kullanılmamış hizmetler için tam iade</li>
    <li><strong>24 saat sonrası:</strong> Durum bazlı değerlendirme</li>
    <li><strong>Kural ihlali:</strong> İade yapılmaz</li>
  </ul>
  İade talebi için <a href="/panel/tickets/new">destek talebi</a> açın.', 
 'Ödeme', '↩️', 6),

('2FA (İki Faktörlü Doğrulama) nasıl aktif edilir?', 
 'Hesabınızı korumak için 2FA''yı aktif edin:<br><br>
  <ol>
    <li><a href="/panel/settings">Panel > Ayarlar > Güvenlik</a> bölümüne gidin</li>
    <li>"2FA Aktif Et" butonuna tıklayın</li>
    <li>QR kodu Google Authenticator ile tarayın</li>
    <li>6 haneli kodu girin ve doğrulayın</li>
    <li><strong>Yedek kodlarınızı güvenli bir yere kaydedin!</strong></li>
  </ol>', 
 'Güvenlik', '🔐', 7),

('Sunucu ayarlarını nasıl değiştiririm?', 
 'Sunucu ayarlarını Panel > Sunucularım bölümünden değiştirebilirsiniz:<br><br>
  <ul>
    <li><strong>server.cfg:</strong> Temel sunucu ayarları</li>
    <li><strong>RCON:</strong> Uzaktan komut çalıştırma</li>
    <li><strong>Harita:</strong> Aktif haritayı değiştirme</li>
    <li><strong>Eklentiler:</strong> AMX Mod X pluginleri</li>
  </ul>', 
 'Sunucu', '⚙️', 8);


-- =====================================
-- VARSAYILAN STATİK SAYFALAR
-- =====================================
INSERT INTO `static_pages` (`slug`, `title`, `content`, `meta_description`, `show_in_footer`) VALUES
('tos', 'Kullanım Şartları', 
 '<section id="intro">
    <h2>1. Giriş</h2>
    <p>Bu Kullanım Şartları, AGTR Merkezi tarafından sunulan tüm hizmetlerin kullanımını düzenler.</p>
  </section>
  <section id="services">
    <h2>2. Hizmetler</h2>
    <p>Half-Life, Counter-Strike 1.6 ve türevleri için oyun sunucusu barındırma hizmeti sunuyoruz.</p>
  </section>
  <p><em>Bu içerik Admin Panel > Statik Sayfalar bölümünden düzenlenebilir.</em></p>', 
 'AGTR Merkezi kullanım şartları ve koşulları', TRUE),

('privacy', 'Gizlilik Politikası', 
 '<section>
    <h2>1. Toplanan Veriler</h2>
    <p>Hizmetlerimizi kullanırken aşağıdaki verileri topluyoruz:</p>
    <ul>
      <li>Hesap bilgileri (kullanıcı adı, e-posta)</li>
      <li>IP adresi ve tarayıcı bilgileri</li>
      <li>Ödeme bilgileri (güvenli şekilde iyzico tarafından işlenir)</li>
    </ul>
  </section>
  <section>
    <h2>2. Verilerin Kullanımı</h2>
    <p>Verileriniz sadece hizmet sunumu için kullanılır ve üçüncü taraflarla paylaşılmaz.</p>
  </section>
  <p><em>Bu içerik Admin Panel > Statik Sayfalar bölümünden düzenlenebilir.</em></p>', 
 'AGTR Merkezi gizlilik politikası', TRUE);


SET FOREIGN_KEY_CHECKS = 1;

-- =====================================
-- KONTROL
-- =====================================
SELECT 'site_assets' AS 'Tablo', COUNT(*) AS 'Kayıt' FROM site_assets
UNION ALL
SELECT 'faq_items', COUNT(*) FROM faq_items
UNION ALL
SELECT 'static_pages', COUNT(*) FROM static_pages
UNION ALL
SELECT 'contact_messages', COUNT(*) FROM contact_messages;

-- Başarı mesajı
SELECT '✅ Migration tamamlandı!' AS 'Durum';
