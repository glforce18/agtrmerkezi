-- Migration: Add ram_mb and disk_gb columns to server_packages table
-- Date: 2026-01-30
-- Description: Adds resource specification columns for server packages

-- Add ram_mb column (default 512MB)
ALTER TABLE server_packages
ADD COLUMN IF NOT EXISTS ram_mb INT NOT NULL DEFAULT 512;

-- Add disk_gb column (default 10GB)
ALTER TABLE server_packages
ADD COLUMN IF NOT EXISTS disk_gb INT NOT NULL DEFAULT 10;

-- Update existing packages with reasonable defaults based on slots
UPDATE server_packages
SET ram_mb = CASE
    WHEN slots <= 12 THEN 512
    WHEN slots <= 20 THEN 1024
    WHEN slots <= 28 THEN 2048
    ELSE 4096
END
WHERE ram_mb = 512;

UPDATE server_packages
SET disk_gb = CASE
    WHEN slots <= 12 THEN 10
    WHEN slots <= 20 THEN 15
    WHEN slots <= 28 THEN 20
    ELSE 30
END
WHERE disk_gb = 10;

-- Add comment
COMMENT ON COLUMN server_packages.ram_mb IS 'RAM allocation in megabytes';
COMMENT ON COLUMN server_packages.disk_gb IS 'Disk allocation in gigabytes';
