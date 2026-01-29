-- ============================================
-- AGTR Merkezi - Wallet System Migration
-- Adds dual wallet system (TL + Armor Coin)
-- ============================================

-- 1. Add balance columns to users table
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `balance` FLOAT DEFAULT 0.0 COMMENT 'TL bakiye (gerçek para)',
ADD COLUMN IF NOT EXISTS `balance_coin` FLOAT DEFAULT 0.0 COMMENT 'Armor bakiye (sanal para)';

-- 2. Create transactions table
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `wallet_type` ENUM('real', 'coin') NOT NULL DEFAULT 'real',
  `type` VARCHAR(50) NOT NULL COMMENT 'deposit, withdraw, payment, refund, bonus, transfer, etc.',
  `amount` FLOAT NOT NULL,
  `description` VARCHAR(500),
  `reference_id` VARCHAR(100) COMMENT 'Payment ID, server ID, etc.',
  `reference_type` VARCHAR(50) COMMENT 'payment, server, transfer, etc.',

  -- Ledger fields
  `balance_before` FLOAT DEFAULT 0,
  `balance_after` FLOAT DEFAULT 0,

  -- Transfer fields
  `target_user_id` INT DEFAULT NULL,

  -- Meta info
  `ip_address` VARCHAR(45),
  `user_agent` VARCHAR(500),
  `extra_data` JSON,

  -- Timestamps
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,

  -- Indexes
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_reference_id` (`reference_id`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_wallet_type` (`wallet_type`),

  -- Foreign keys
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`target_user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Wallet transactions ledger - dual wallet system';

-- 3. Initialize existing users with 0 balance (if column was just added)
UPDATE `users` SET `balance` = 0.0 WHERE `balance` IS NULL;
UPDATE `users` SET `balance_coin` = 0.0 WHERE `balance_coin` IS NULL;

-- ============================================
-- Test Data (optional - for development)
-- ============================================

-- Give test users some initial balance
-- UPDATE `users` SET `balance` = 100.0, `balance_coin` = 10000.0 WHERE `id` = 1;

-- ============================================
-- Verification Queries
-- ============================================

-- Check users table
SELECT 'Users with balance columns:' AS status;
DESCRIBE users;

-- Check transactions table
SELECT 'Transactions table created:' AS status;
DESCRIBE transactions;

-- Count records
SELECT
  'Migration Complete!' AS status,
  COUNT(*) AS total_users,
  SUM(balance) AS total_tl,
  SUM(balance_coin) AS total_armor
FROM users;
