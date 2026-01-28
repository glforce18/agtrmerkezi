-- AGTR Merkezi v6.1 - System Alerts Table
-- Migration for system_alerts table
-- Date: 2026-01-25

CREATE TABLE IF NOT EXISTS system_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    level VARCHAR(20) NOT NULL COMMENT 'info, warning, error, critical',
    title VARCHAR(255) NOT NULL COMMENT 'Alert title',
    message TEXT NOT NULL COMMENT 'Alert message',
    server_id INT NULL COMMENT 'Related server',
    user_id INT NULL COMMENT 'Related user',
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Alert resolved',
    resolved_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,

    INDEX idx_alert_level_created (level, created_at),
    INDEX idx_alert_server (server_id),
    INDEX idx_alert_resolved (is_resolved, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='System alerts and notifications';
