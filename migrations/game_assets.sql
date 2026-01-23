-- AGTR Merkezi - Game Assets Migration
-- Tarih: 2026-01-22
-- Oyun gorselleri, harita resimleri ve animasyonlar icin tablolar

-- Game Assets tablosu
CREATE TABLE IF NOT EXISTS game_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_slug VARCHAR(50) NOT NULL,
    game_name VARCHAR(100),
    asset_type ENUM('banner', 'hero', 'logo', 'icon', 'grid', 'screenshot', 'map', 'weapon', 'skin', 'team_logo') NOT NULL,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500),
    original_filename VARCHAR(200),
    file_size INT,
    width INT,
    height INT,
    mime_type VARCHAR(50),
    source VARCHAR(50),
    source_url VARCHAR(500),
    source_id VARCHAR(100),
    tags JSON DEFAULT NULL,
    is_animated BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_game_slug (game_slug),
    INDEX idx_asset_type (asset_type),
    INDEX idx_is_active (is_active),
    INDEX idx_is_featured (is_featured)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Animation Assets tablosu
CREATE TABLE IF NOT EXISTS animation_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    description TEXT,
    category ENUM('loading', 'success', 'error', 'game', 'ui', 'celebration') NOT NULL,
    file_format ENUM('lottie', 'gif', 'webp', 'mp4') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    preview_path VARCHAR(500),
    file_size INT,
    duration_ms INT,
    width INT,
    height INT,
    `loop` BOOLEAN DEFAULT TRUE,
    source VARCHAR(50),
    source_url VARCHAR(500),
    author VARCHAR(100),
    license VARCHAR(100),
    tags JSON DEFAULT NULL,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    use_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_file_format (file_format),
    INDEX idx_is_active (is_active),
    INDEX idx_use_count (use_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Map Assets tablosu (CS 1.6, Half-Life haritalari)
CREATE TABLE IF NOT EXISTS map_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_slug VARCHAR(50) NOT NULL,
    map_name VARCHAR(100) NOT NULL,
    map_slug VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    description TEXT,
    map_type VARCHAR(20),
    thumbnail_path VARCHAR(500),
    overview_path VARCHAR(500),
    screenshots JSON DEFAULT NULL,
    source VARCHAR(50),
    source_url VARCHAR(500),
    popularity_score INT DEFAULT 0,
    is_official BOOLEAN DEFAULT FALSE,
    is_competitive BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_game_slug (game_slug),
    INDEX idx_map_type (map_type),
    INDEX idx_popularity (popularity_score),
    INDEX idx_is_active (is_active),
    UNIQUE KEY unique_game_map (game_slug, map_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
