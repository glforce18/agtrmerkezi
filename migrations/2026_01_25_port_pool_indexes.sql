-- ================================================
-- Port Pool Management - Database Indexes
-- Date: 2026-01-25
-- Purpose: Optimize IP load balancing queries
-- ================================================

-- Check if index exists before creating
SET @exist := (SELECT COUNT(*) FROM information_schema.statistics
               WHERE table_schema = DATABASE()
               AND table_name = 'game_servers'
               AND index_name = 'idx_server_ip_status');

SET @sqlstmt := IF(@exist > 0,
                   'SELECT ''Index idx_server_ip_status already exists'' AS Info',
                   'CREATE INDEX idx_server_ip_status ON game_servers(ip_address, status)');

PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verify unique constraint on (ip_address, port) exists
-- This should already exist from initial schema, but verify
SET @exist := (SELECT COUNT(*) FROM information_schema.table_constraints
               WHERE table_schema = DATABASE()
               AND table_name = 'game_servers'
               AND constraint_type = 'UNIQUE'
               AND constraint_name LIKE '%ip%port%');

SELECT IF(@exist > 0,
    'VERIFIED: Unique constraint on (ip_address, port) exists',
    'WARNING: Unique constraint on (ip_address, port) NOT FOUND - Add manually!'
) AS ConstraintCheck;

-- Analyze table for query optimizer
ANALYZE TABLE game_servers;

-- Show index information
SELECT
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    NON_UNIQUE,
    INDEX_TYPE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'game_servers'
    AND INDEX_NAME IN ('idx_server_ip_status', 'PRIMARY', 'uq_server_ip_port')
ORDER BY INDEX_NAME, SEQ_IN_INDEX;
