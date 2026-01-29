-- ==================================================================================
-- AGTR Merkezi - Subscription System Migration
-- Date: 2026-01-29
-- Description: Adds automatic billing and subscription management tables
-- ==================================================================================

-- ==================================================================================
-- BACKUP INSTRUCTIONS
-- ==================================================================================
-- Before running this migration, backup your database:
-- mysqldump -u agtrmerkezi_user -p agtrmerkezi > backup_pre_subscription_$(date +%Y%m%d_%H%M%S).sql
-- ==================================================================================

-- Start transaction
START TRANSACTION;

-- ==================================================================================
-- 1. CREATE SUBSCRIPTION TABLES
-- ==================================================================================

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,

    -- Foreign keys
    game_server_id INT NOT NULL,
    user_id INT NOT NULL,

    -- Billing configuration
    billing_period ENUM('monthly', 'quarterly', 'biannual', 'annual') NOT NULL DEFAULT 'monthly',
    auto_renew_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    payment_method ENUM('real', 'coin') NOT NULL DEFAULT 'real',

    -- Billing dates
    next_billing_date DATE NOT NULL,
    last_billing_date DATE,
    grace_period_started_at DATETIME,
    suspended_at DATETIME,
    cancelled_at DATETIME,

    -- Status
    status ENUM('active', 'cancelled', 'suspended', 'expired', 'grace_period') NOT NULL DEFAULT 'active',

    -- Notification flags (to track which notifications have been sent)
    notification_7days_sent BOOLEAN NOT NULL DEFAULT FALSE,
    notification_3days_sent BOOLEAN NOT NULL DEFAULT FALSE,
    notification_1day_sent BOOLEAN NOT NULL DEFAULT FALSE,

    -- Billing metadata
    failure_count INT NOT NULL DEFAULT 0,
    last_failure_reason VARCHAR(500),
    monthly_amount DECIMAL(10, 2) NOT NULL,

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Constraints
    FOREIGN KEY (game_server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_subscription_server (game_server_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create indexes for performance
CREATE INDEX idx_subscriptions_next_billing ON subscriptions(next_billing_date, auto_renew_enabled, status);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id, status);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_expiry_notifications ON subscriptions(
    next_billing_date,
    notification_7days_sent,
    notification_3days_sent,
    notification_1day_sent
);

-- Subscription billing history table
CREATE TABLE IF NOT EXISTS subscription_billing_history (
    id INT PRIMARY KEY AUTO_INCREMENT,

    -- Foreign keys
    subscription_id INT NOT NULL,
    user_id INT NOT NULL,
    game_server_id INT NOT NULL,

    -- Billing attempt details
    billing_date DATE NOT NULL,
    billing_period ENUM('monthly', 'quarterly', 'biannual', 'annual') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('real', 'coin') NOT NULL,

    -- Result
    status ENUM('success', 'failed', 'cancelled', 'retrying') NOT NULL,
    failure_reason VARCHAR(500),
    retry_count INT NOT NULL DEFAULT 0,

    -- Wallet snapshots
    balance_before DECIMAL(10, 2),
    balance_after DECIMAL(10, 2),

    -- Related records
    transaction_id INT,
    payment_id INT,

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,

    -- Constraints
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create indexes
CREATE INDEX idx_billing_history_subscription ON subscription_billing_history(subscription_id, billing_date DESC);
CREATE INDEX idx_billing_history_user ON subscription_billing_history(user_id, billing_date DESC);
CREATE INDEX idx_billing_history_status ON subscription_billing_history(status, created_at DESC);

-- ==================================================================================
-- 2. MIGRATE EXISTING DATA
-- ==================================================================================

-- Create subscriptions for all existing active game servers
INSERT INTO subscriptions (
    game_server_id,
    user_id,
    billing_period,
    auto_renew_enabled,
    payment_method,
    next_billing_date,
    last_billing_date,
    status,
    monthly_amount,
    created_at,
    updated_at
)
SELECT
    gs.id AS game_server_id,
    gs.owner_id AS user_id,
    'monthly' AS billing_period,
    gs.auto_renew AS auto_renew_enabled,
    'real' AS payment_method,
    DATE(gs.expires_at) AS next_billing_date,
    NULL AS last_billing_date,
    CASE
        WHEN gs.status = 'running' AND gs.expires_at > NOW() THEN 'active'
        WHEN gs.status = 'expired' THEN 'expired'
        WHEN gs.status = 'suspended' THEN 'suspended'
        ELSE 'active'
    END AS status,
    gs.monthly_price AS monthly_amount,
    gs.created_at,
    NOW() AS updated_at
FROM game_servers gs
WHERE gs.status NOT IN ('deleted', 'cancelled')
  AND gs.expires_at IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM subscriptions s WHERE s.game_server_id = gs.id
  );

-- ==================================================================================
-- 3. UPDATE EXISTING TABLES (if needed)
-- ==================================================================================

-- Add subscription_id column to payments table for tracking (optional)
-- This is non-destructive and allows linking payments to subscriptions
ALTER TABLE payments
ADD COLUMN subscription_id INT AFTER server_id,
ADD FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL;

-- Add last_payment_date to game_servers for UI display
ALTER TABLE game_servers
ADD COLUMN last_payment_date DATETIME AFTER expires_at;

-- Update last_payment_date from payment history
UPDATE game_servers gs
SET last_payment_date = (
    SELECT MAX(p.completed_at)
    FROM payments p
    WHERE p.server_id = gs.id
      AND p.status = 'completed'
);

-- ==================================================================================
-- 4. DATA INTEGRITY VERIFICATION
-- ==================================================================================

-- Verify migration counts
SELECT 'Game Servers (not deleted)' AS metric, COUNT(*) AS count
FROM game_servers
WHERE status NOT IN ('deleted', 'cancelled')
  AND expires_at IS NOT NULL
UNION ALL
SELECT 'Subscriptions Created' AS metric, COUNT(*) AS count
FROM subscriptions
UNION ALL
SELECT 'Subscriptions Active' AS metric, COUNT(*) AS count
FROM subscriptions
WHERE status = 'active';

-- Check for servers without subscriptions (should be 0 for active servers)
SELECT
    'Servers without subscriptions' AS issue,
    COUNT(*) AS count
FROM game_servers gs
WHERE gs.status NOT IN ('deleted', 'cancelled')
  AND gs.expires_at IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM subscriptions s WHERE s.game_server_id = gs.id
  );

-- ==================================================================================
-- 5. COMMIT TRANSACTION
-- ==================================================================================

-- If everything looks good, commit
COMMIT;

-- ==================================================================================
-- ROLLBACK SCRIPT
-- ==================================================================================
-- If you need to rollback this migration, run:
--
-- START TRANSACTION;
--
-- -- Remove foreign key constraints first
-- ALTER TABLE payments DROP FOREIGN KEY payments_ibfk_subscription;
-- ALTER TABLE payments DROP COLUMN subscription_id;
-- ALTER TABLE game_servers DROP COLUMN last_payment_date;
--
-- -- Drop tables in reverse order (child tables first)
-- DROP TABLE IF EXISTS subscription_billing_history;
-- DROP TABLE IF EXISTS subscriptions;
--
-- COMMIT;
--
-- ==================================================================================

-- ==================================================================================
-- POST-MIGRATION TASKS
-- ==================================================================================
-- After running this migration:
-- 1. Deploy new backend code with Subscription models
-- 2. Deploy SubscriptionService and related services
-- 3. Deploy and start scheduled jobs (billing_job, expiry_notification_job)
-- 4. Monitor logs for any issues
-- 5. Test billing process on staging with test users
-- ==================================================================================
