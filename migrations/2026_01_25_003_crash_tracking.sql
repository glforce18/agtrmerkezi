-- ================================================
-- Crash Tracking & Respawn Storm Detection
-- Date: 2026-01-25
-- Purpose: Add restart_backoff_until column
-- ================================================

-- Add restart_backoff_until column (if not exists)
SET @exist := (SELECT COUNT(*) FROM information_schema.COLUMNS
               WHERE table_schema = DATABASE()
               AND table_name = 'game_servers'
               AND column_name = 'restart_backoff_until');

SET @sqlstmt := IF(@exist > 0,
                   'SELECT ''Column restart_backoff_until already exists'' AS Info',
                   'ALTER TABLE game_servers ADD COLUMN restart_backoff_until DATETIME NULL COMMENT ''Exponential backoff timer for crashed servers''');

PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verify columns exist
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'game_servers'
    AND COLUMN_NAME IN ('crash_count', 'last_crash', 'restart_backoff_until', 'auto_restart')
ORDER BY COLUMN_NAME;
