-- AGTR Merkezi v6.2 - Sample Plugin Catalog
-- Popular AMXModX/Metamod plugins for Half-Life servers
-- Date: 2026-01-25

-- Clear existing plugins (optional)
-- DELETE FROM server_plugins;
-- DELETE FROM plugins;

-- Sample Plugins for Counter-Strike 1.6
INSERT INTO plugins (name, slug, description, version, author, filename, file_path, file_size, game_type, category, is_active, is_default, requires_config, config_template)
VALUES
-- Admin Tools
('Admin Menu', 'admin-menu', 'Comprehensive admin menu with player management, server control, and voting features', '1.8.3', 'AMXX Dev Team', 'adminmenu.amxx', '/var/www/agtrmerkezi/static/plugins/adminmenu.amxx', 45000, 'cs16', 'admin', TRUE, TRUE, FALSE, NULL),

('Admin Commands', 'admin-commands', 'Essential admin commands: kick, ban, slay, slap, and more', '1.8.3', 'AMXX Dev Team', 'admincmd.amxx', '/var/www/agtrmerkezi/static/plugins/admincmd.amxx', 38000, 'cs16', 'admin', TRUE, TRUE, FALSE, NULL),

('Admin Chat', 'admin-chat', 'Admin-only chat and player communication tools', '1.8.3', 'AMXX Dev Team', 'adminchat.amxx', '/var/www/agtrmerkezi/static/plugins/adminchat.amxx', 15000, 'cs16', 'admin', TRUE, TRUE, FALSE, NULL),

-- Fun Plugins
('GunGame', 'gungame', 'Progressive weapon upgrade system - kill with each weapon to win', '5.1', 'GunGame Community', 'gungame.amxx', '/var/www/agtrmerkezi/static/plugins/gungame.amxx', 125000, 'cs16', 'fun', TRUE, FALSE, TRUE, 'gg_mode 1\ngg_start_level 1\ngg_max_level 18'),

('DeathMatch', 'deathmatch', 'Free-for-all deathmatch mode with instant respawn', '2.1', 'AMXX Community', 'csdm.amxx', '/var/www/agtrmerkezi/static/plugins/csdm.amxx', 89000, 'cs16', 'fun', TRUE, FALSE, TRUE, 'csdm_enabled 1\ncsdm_respawn_wait 2.0'),

('Zombie Plague', 'zombie-plague', 'Humans vs Zombies survival mode with classes and upgrades', '4.3', 'MeRcyLeZZ', 'zombieplague.amxx', '/var/www/agtrmerkezi/static/plugins/zombieplague.amxx', 215000, 'cs16', 'fun', TRUE, FALSE, TRUE, 'zp_zombie_health 2500\nzp_human_health 100'),

('Parachute', 'parachute', 'Allows players to deploy parachute mid-air', '1.3', 'KRoT@L', 'parachute.amxx', '/var/www/agtrmerkezi/static/plugins/parachute.amxx', 18000, 'cs16', 'fun', TRUE, FALSE, FALSE, NULL),

('Hook', 'hook', 'Grappling hook for advanced movement', '2.0', 'OneEyed', 'hook.amxx', '/var/www/agtrmerkezi/static/plugins/hook.amxx', 32000, 'cs16', 'fun', TRUE, FALSE, FALSE, NULL),

-- Stats & Tracking
('Stats Me', 'stats-me', 'Real-time player statistics and rankings', '1.8.3', 'AMXX Dev Team', 'statscfg.amxx', '/var/www/agtrmerkezi/static/plugins/statscfg.amxx', 25000, 'cs16', 'stats', TRUE, TRUE, FALSE, NULL),

('Top 15', 'top15', 'Display top 15 players on scoreboard', '1.8.3', 'AMXX Dev Team', 'stats.amxx', '/var/www/agtrmerkezi/static/plugins/stats.amxx', 42000, 'cs16', 'stats', TRUE, FALSE, FALSE, NULL),

('Rank System', 'rank-system', 'Advanced ranking with XP and levels', '3.0', 'ConnorMcLeod', 'rank_system.amxx', '/var/www/agtrmerkezi/static/plugins/rank_system.amxx', 68000, 'cs16', 'stats', TRUE, FALSE, TRUE, 'rank_max_level 100\nrank_xp_kill 50'),

-- Anti-Cheat
('Anti-Cheat Lite', 'anticheat-lite', 'Basic anti-cheat protection against common exploits', '1.5', 'AMXX Community', 'anticheat.amxx', '/var/www/agtrmerkezi/static/plugins/anticheat.amxx', 52000, 'cs16', 'anticheat', TRUE, FALSE, FALSE, NULL),

('Speed Hack Detector', 'speedhack-detector', 'Detects and blocks speed hack attempts', '2.1', 'ConnorMcLeod', 'speedhack_detector.amxx', '/var/www/agtrmerkezi/static/plugins/speedhack_detector.amxx', 28000, 'cs16', 'anticheat', TRUE, FALSE, FALSE, NULL),

-- Utility
('Map Manager', 'map-manager', 'Advanced map rotation and voting system', '2.6', 'AMXX Dev Team', 'mapmanager.amxx', '/var/www/agtrmerkezi/static/plugins/mapmanager.amxx', 95000, 'cs16', 'utility', TRUE, TRUE, TRUE, 'mapm_vote_enabled 1\nmapm_cycles 3'),

('Advertisements', 'advertisements', 'Display server messages and advertisements', '1.0', 'AMXX Community', 'admessage.amxx', '/var/www/agtrmerkezi/static/plugins/admessage.amxx', 12000, 'cs16', 'utility', TRUE, FALSE, TRUE, 'amx_message_interval 120'),

('Server Info', 'server-info', 'Display server information in HUD', '1.2', 'AMXX Community', 'serverinfo.amxx', '/var/www/agtrmerkezi/static/plugins/serverinfo.amxx', 18000, 'cs16', 'utility', TRUE, FALSE, FALSE, NULL),

-- Anti-Flood
('Anti-Flood', 'antiflood', 'Prevents chat and voice spam', '1.4', 'AMXX Dev Team', 'antiflood.amxx', '/var/www/agtrmerkezi/static/plugins/antiflood.amxx', 22000, 'cs16', 'utility', TRUE, TRUE, FALSE, NULL),

-- Plugins for Adrenaline Gamer (AG)
('AG Admin', 'ag-admin', 'Admin commands optimized for AG mod', '6.6', 'AGHL Community', 'ag_admin.amxx', '/var/www/agtrmerkezi/static/plugins/ag_admin.amxx', 35000, 'ag', 'admin', TRUE, TRUE, FALSE, NULL),

('AG Stats', 'ag-stats', 'Statistics tracking for AG competitive matches', '6.6', 'AGHL Community', 'ag_stats.amxx', '/var/www/agtrmerkezi/static/plugins/ag_stats.amxx', 48000, 'ag', 'stats', TRUE, FALSE, FALSE, NULL),

('AG Match Mode', 'ag-match-mode', 'Competitive match mode with ready system', '6.6', 'AGHL Community', 'ag_match.amxx', '/var/www/agtrmerkezi/static/plugins/ag_match.amxx', 62000, 'ag', 'utility', TRUE, FALSE, TRUE, 'ag_match_warmup 60\nag_match_overtime 1'),

-- Plugins for Half-Life DM
('HLDM Admin', 'hldm-admin', 'Admin menu for Half-Life Deathmatch', '1.0', 'Valve', 'hldm_admin.amxx', '/var/www/agtrmerkezi/static/plugins/hldm_admin.amxx', 28000, 'hldm', 'admin', TRUE, TRUE, FALSE, NULL),

('HLDM Weapons', 'hldm-weapons', 'Enhanced weapon balance for HLDM', '2.0', 'HLDM Community', 'hldm_weapons.amxx', '/var/www/agtrmerkezi/static/plugins/hldm_weapons.amxx', 45000, 'hldm', 'fun', TRUE, FALSE, FALSE, NULL);

-- Update created_at timestamp
UPDATE plugins SET created_at = NOW(), updated_at = NOW();

-- Output
SELECT 'Plugin catalog seeded successfully!' as message, COUNT(*) as total_plugins FROM plugins;
