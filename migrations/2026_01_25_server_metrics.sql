-- ================================================
-- Server Metrics Table - Resource Monitoring
-- Date: 2026-01-25
-- Purpose: Track CPU, memory, network, player count
-- ================================================

-- Create server_metrics table
CREATE TABLE IF NOT EXISTS server_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    server_id INT NOT NULL,
    cpu_percent FLOAT NULL COMMENT 'Process CPU usage (0-100)',
    memory_mb FLOAT NULL COMMENT 'Process RSS memory in MB',
    network_in_mbps FLOAT NULL COMMENT 'Network read MB (cumulative)',
    network_out_mbps FLOAT NULL COMMENT 'Network write MB (cumulative)',
    process_status VARCHAR(20) NULL COMMENT 'Process status (running, sleeping, zombie)',
    player_count INT NOT NULL DEFAULT 0 COMMENT 'Players from A2S query',
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When metric was collected',

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    INDEX idx_metrics_server_id (server_id),
    INDEX idx_metrics_timestamp (timestamp),
    INDEX idx_metrics_server_time (server_id, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Sunucu kaynak kullanimi metrikleri';

-- Verify table creation
SELECT
    COUNT(*) as table_exists,
    'server_metrics' as table_name
FROM information_schema.tables
WHERE table_schema = DATABASE()
    AND table_name = 'server_metrics';

-- Show indexes
SELECT
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'server_metrics'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- Sample query for testing (after data is collected)
-- SELECT
--     server_id,
--     AVG(cpu_percent) as avg_cpu,
--     MAX(cpu_percent) as max_cpu,
--     AVG(memory_mb) as avg_memory,
--     MAX(memory_mb) as max_memory,
--     AVG(player_count) as avg_players,
--     MAX(player_count) as max_players,
--     COUNT(*) as data_points
-- FROM server_metrics
-- WHERE server_id = 1
--     AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
-- GROUP BY server_id;
