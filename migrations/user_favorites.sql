-- User Favorite Servers Migration
-- Kullanici favori sunuculari - cihazlar arasi senkronizasyon

CREATE TABLE IF NOT EXISTS user_favorite_servers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    server_id INT NOT NULL,
    server_ip VARCHAR(50),
    server_port INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_server_favorite (user_id, server_id),
    INDEX idx_user_favorites_user (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
