-- AGTR Merkezi v6.0 - Server Panel Migration
-- Date: 2026-01-23
-- Description: Sunucu yonetim paneli icin yeni tablolar ve kolonlar

-- =====================================================
-- PHASE 1: game_servers tablosuna yeni kolonlar ekle
-- =====================================================

-- Unique server code (AGTR-2026-00001 formati)
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS unique_code VARCHAR(20) UNIQUE;

-- Mod type (ag, ag_openag, cstrike, valve, valvenewvalve)
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS mod_type VARCHAR(50);

-- Server dizin yolu
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS server_path VARCHAR(500);

-- Screen session adi
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS screen_name VARCHAR(50);

-- Process ID
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS process_pid INT;

-- Son heartbeat zamani
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS last_heartbeat DATETIME;

-- Kurulum ID referansi
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS installation_id INT;

-- Owner Steam ID for quick lookup (denormalized)
ALTER TABLE game_servers ADD COLUMN IF NOT EXISTS owner_steam_id VARCHAR(50);

-- Index for unique_code
CREATE INDEX IF NOT EXISTS idx_game_servers_unique_code ON game_servers(unique_code);

-- Index for status + owner
CREATE INDEX IF NOT EXISTS idx_game_servers_owner_status ON game_servers(owner_id, status);

-- Index for owner Steam ID
CREATE INDEX IF NOT EXISTS idx_game_servers_owner_steam_id ON game_servers(owner_steam_id);

-- Populate owner_steam_id from users table (run once after migration)
UPDATE game_servers gs
SET owner_steam_id = (SELECT steam_id FROM users WHERE id = gs.owner_id)
WHERE owner_steam_id IS NULL;


-- =====================================================
-- PHASE 2: Yeni tablolar olustur
-- =====================================================

-- Server Installations - Kurulum takibi
CREATE TABLE IF NOT EXISTS server_installations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    user_id INT NOT NULL,
    unique_code VARCHAR(20) NOT NULL,
    status ENUM('pending', 'installing', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    progress_percent INT DEFAULT 0,
    current_step VARCHAR(100),
    total_steps INT DEFAULT 8,
    error_message TEXT,
    template_type VARCHAR(50),
    celery_task_id VARCHAR(100),
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    UNIQUE KEY uq_installation_code (unique_code),
    INDEX idx_installation_server (server_id),
    INDEX idx_installation_user (user_id),
    INDEX idx_installation_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Server Ownership History - Sahiplik gecmisi
CREATE TABLE IF NOT EXISTS server_ownership_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    user_id INT NOT NULL,
    unique_code VARCHAR(20),
    action ENUM('created', 'transferred', 'expired', 'deleted', 'renewed', 'suspended', 'unsuspended') NOT NULL,
    details JSON,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_ownership_server (server_id),
    INDEX idx_ownership_user (user_id),
    INDEX idx_ownership_action (action),
    INDEX idx_ownership_date (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Server Admin Entries - AMXModX adminleri
CREATE TABLE IF NOT EXISTS server_admin_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    steam_id VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    flags VARCHAR(50) DEFAULT 'abcdefghijklmnopqrstu',
    password VARCHAR(100),
    access_level INT DEFAULT 0,
    auth_type ENUM('steam', 'ip', 'name') DEFAULT 'steam',
    added_by INT,
    expires_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL,

    UNIQUE KEY uq_server_admin (server_id, steam_id),
    INDEX idx_admin_server (server_id),
    INDEX idx_admin_active (server_id, is_active),
    INDEX idx_admin_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Server Bans - Sunucu banlari
CREATE TABLE IF NOT EXISTS server_bans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    steam_id VARCHAR(50),
    ip_address VARCHAR(45),
    name VARCHAR(100),
    reason VARCHAR(500),
    banned_by INT,
    banned_by_admin VARCHAR(100),
    duration_minutes INT DEFAULT 0,
    expires_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    ban_type ENUM('steam', 'ip', 'both') DEFAULT 'steam',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (banned_by) REFERENCES users(id) ON DELETE SET NULL,

    INDEX idx_ban_server (server_id),
    INDEX idx_ban_active (server_id, is_active),
    INDEX idx_ban_steam (steam_id),
    INDEX idx_ban_ip (ip_address),
    INDEX idx_ban_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Server Console History - RCON komut gecmisi
CREATE TABLE IF NOT EXISTS server_console_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    user_id INT NOT NULL,
    command VARCHAR(500) NOT NULL,
    response TEXT,
    command_type ENUM('rcon', 'console', 'scheduled', 'system') DEFAULT 'rcon',
    execution_time_ms INT,
    ip_address VARCHAR(45),
    is_success BOOLEAN DEFAULT TRUE,
    error_message VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_console_server (server_id),
    INDEX idx_console_user (user_id),
    INDEX idx_console_date (server_id, created_at),
    INDEX idx_console_type (command_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Server Stats Hourly - Saatlik istatistikler
CREATE TABLE IF NOT EXISTS server_stats_hourly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    hour_timestamp DATETIME NOT NULL,
    avg_players FLOAT DEFAULT 0,
    max_players INT DEFAULT 0,
    min_players INT DEFAULT 0,
    unique_players INT DEFAULT 0,
    total_joins INT DEFAULT 0,
    total_leaves INT DEFAULT 0,
    map_changes INT DEFAULT 0,
    most_played_map VARCHAR(64),
    cpu_usage_avg FLOAT,
    ram_usage_avg FLOAT,
    uptime_percent FLOAT DEFAULT 100,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,

    UNIQUE KEY uq_server_hour (server_id, hour_timestamp),
    INDEX idx_stats_server (server_id),
    INDEX idx_stats_hour (hour_timestamp),
    INDEX idx_stats_server_hour (server_id, hour_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Server Quick Commands - Hizli komutlar
CREATE TABLE IF NOT EXISTS server_quick_commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    command VARCHAR(500) NOT NULL,
    description VARCHAR(255),
    icon VARCHAR(50),
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,

    INDEX idx_quick_cmd_server (server_id),
    INDEX idx_quick_cmd_active (server_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Server Map Pools - Harita havuzlari
CREATE TABLE IF NOT EXISTS server_map_pools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    maps JSON NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    rotation_type ENUM('sequential', 'random', 'vote') DEFAULT 'sequential',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,

    INDEX idx_map_pool_server (server_id),
    INDEX idx_map_pool_active (server_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- PHASE 3: Varsayilan veriler
-- =====================================================

-- Varsayilan hizli komutlar (her yeni sunucu icin kopyalanacak)
CREATE TABLE IF NOT EXISTS default_quick_commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_type VARCHAR(50),
    name VARCHAR(100) NOT NULL,
    command VARCHAR(500) NOT NULL,
    description VARCHAR(255),
    icon VARCHAR(50),
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Varsayilan komutlari ekle
INSERT IGNORE INTO default_quick_commands (game_type, name, command, description, icon, display_order) VALUES
('all', 'Sunucu Durumu', 'status', 'Sunucu durumunu goster', 'info', 1),
('all', 'Oyuncu Listesi', 'users', 'Baglikoyunculari listele', 'users', 2),
('all', 'Harita Degistir', 'changelevel {map}', 'Haritayi degistir', 'map', 3),
('all', 'Tum Oyunculara Mesaj', 'say {message}', 'Tum oyunculara mesaj gonder', 'chat', 4),
('all', 'Sunucuyu Yeniden Baslat', 'restart', 'Sunucuyu yeniden baslat', 'refresh', 5),
('hldm', 'Fraglimit Ayarla', 'mp_fraglimit {value}', 'Frag limitini ayarla', 'target', 10),
('hldm', 'Timelimit Ayarla', 'mp_timelimit {value}', 'Zaman limitini ayarla', 'clock', 11),
('cs16', 'Round Yeniden Baslat', 'sv_restart 1', 'Round''u yeniden baslat', 'refresh', 10),
('cs16', 'Para Ver', 'amx_givemoney {player} {amount}', 'Oyuncuya para ver', 'money', 11),
('ag', 'Match Baslat', 'agstart', 'AG match baslat', 'play', 10),
('ag', 'Match Durdur', 'agabort', 'AG match durdur', 'stop', 11);


-- =====================================================
-- Migration tamamlandi
-- =====================================================
