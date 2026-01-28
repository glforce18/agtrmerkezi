-- ================================================
-- Command Quotas Table - Daily Command Limits
-- Date: 2026-01-25
-- Purpose: Track daily RCON command usage per user
-- ================================================

-- Create command_quotas table
CREATE TABLE IF NOT EXISTS command_quotas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    command_type VARCHAR(50) NOT NULL COMMENT 'ban, kick, restart, etc.',
    usage_count INT NOT NULL DEFAULT 0 COMMENT 'Commands used today',
    quota_date DATE NOT NULL DEFAULT (CURRENT_DATE) COMMENT 'Date of quota (UTC)',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_command_date (user_id, command_type, quota_date),
    INDEX idx_quota_date (quota_date),
    INDEX idx_user_command (user_id, command_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Daily command usage quotas per user';

-- Verify table creation
SELECT
    COUNT(*) as table_exists,
    'command_quotas' as table_name
FROM information_schema.tables
WHERE table_schema = DATABASE()
    AND table_name = 'command_quotas';

-- Show table structure
DESCRIBE command_quotas;
