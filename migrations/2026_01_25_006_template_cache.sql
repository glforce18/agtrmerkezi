-- AGTR Merkezi v6.2 - Template Cache Table
-- Migration for template_cache table
-- Date: 2026-01-25

CREATE TABLE IF NOT EXISTS template_cache (
    id INT PRIMARY KEY AUTO_INCREMENT,
    mod_type VARCHAR(50) NOT NULL UNIQUE COMMENT 'ag, cs16, hldm, etc.',
    template_name VARCHAR(100) NOT NULL COMMENT 'Display name',
    version VARCHAR(50) NULL COMMENT 'Template version',
    file_path VARCHAR(500) NOT NULL COMMENT 'Path to cached tar.gz',
    file_size_mb FLOAT NULL COMMENT 'Archive size in MB',
    checksum VARCHAR(64) NULL COMMENT 'SHA256 checksum',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Template is ready to use',
    last_validated DATETIME NULL COMMENT 'Last validation check',
    last_updated DATETIME NULL COMMENT 'Last cache update',
    download_url VARCHAR(500) NULL COMMENT 'Optional: external download URL',
    extra_data JSON NULL COMMENT 'Extra template info',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_template_active (is_active, mod_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Cached game server templates for fast installation';
