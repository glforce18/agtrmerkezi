import apiClient from './client'

/**
 * Server API Service - Unified API v3
 * Manages user servers, packages, and server operations
 * Uses /api/servers endpoints (merged from servers.py + server_v2.py)
 */
export default {
  // Server List & Details
  /**
   * Get user's servers with pagination
   * @param {object} params - Query parameters (page, per_page)
   * @returns {Promise<{data: Array, pagination: Object}>} User's servers
   * @throws {Error} If request fails or user not authenticated
   */
  getMyServers(params = {}) {
    return apiClient.get('/servers/my-servers', { params })
  },

  /**
   * Get single server details by ID
   * @param {number} id - Server ID
   * @returns {Promise<{data: Object}>} Server details
   * @throws {Error} If request fails or server not found
   */
  getServer(id) {
    return apiClient.get(`/servers/${id}`)
  },

  // Server Control
  /**
   * Start a server
   * @param {number} id - Server ID
   * @returns {Promise} Start operation result
   * @throws {Error} If request fails or server cannot be started
   */
  startServer(id) {
    return apiClient.post(`/servers/${id}/start`)
  },

  /**
   * Stop a server
   * @param {number} id - Server ID
   * @returns {Promise} Stop operation result
   * @throws {Error} If request fails or server cannot be stopped
   */
  stopServer(id) {
    return apiClient.post(`/servers/${id}/stop`)
  },

  /**
   * Restart a server
   * @param {number} id - Server ID
   * @returns {Promise} Restart operation result
   * @throws {Error} If request fails
   */
  restartServer(id) {
    return apiClient.post(`/servers/${id}/restart`)
  },

  // RCON
  /**
   * Execute RCON command on server
   * @param {number} id - Server ID
   * @param {string} command - RCON command to execute
   * @returns {Promise<{data: {output: string}}>} Command output
   * @throws {Error} If request fails or RCON unavailable
   */
  executeRCON(id, command) {
    return apiClient.post(`/servers/${id}/rcon`, { command })
  },

  // Players
  /**
   * Get list of players on server
   * @param {number} id - Server ID
   * @returns {Promise<{data: Array}>} Player list
   * @throws {Error} If request fails
   */
  getPlayers(id) {
    return apiClient.get(`/servers/${id}/players`)
  },

  /**
   * Kick a player from server
   * @param {number} id - Server ID
   * @param {number} slot - Player slot number
   * @param {string} reason - Kick reason (optional)
   * @returns {Promise} Kick operation result
   * @throws {Error} If request fails
   */
  kickPlayer(id, slot, reason = '') {
    return apiClient.post(`/servers/${id}/players/${slot}/kick`, { reason })
  },

  // Packages
  /**
   * Get available server packages
   * @returns {Promise<{data: Array}>} Available packages
   * @throws {Error} If request fails
   */
  getPackages() {
    return apiClient.get('/servers/packages')
  },

  // Order Server
  /**
   * Order a new server with package
   * @param {object} data - Order data (package_id, months, payment_method, etc.)
   * @returns {Promise} Order result with server details
   * @throws {Error} If request fails or validation error
   */
  orderServer(data) {
    return apiClient.post('/servers/order', data)
  },

  /**
   * Order server package using wallet balance
   * @param {object} data - Order data (package_id, months, etc.)
   * @returns {Promise} Order result
   * @throws {Error} If request fails or insufficient balance
   */
  orderPackageWallet(data) {
    return apiClient.post('/servers/order/package-wallet', data)
  },

  // Plugin Management
  /**
   * Get all plugins (server + user plugins)
   * @param {number} id - Server ID
   * @returns {Promise<{data: {server_plugins: Array, user_plugins: Array, stats: Object}}>}
   * @throws {Error} If request fails
   */
  getAllPlugins(id) {
    return apiClient.get(`/servers/${id}/plugins/all`)
  },

  /**
   * Upload a plugin file
   * @param {number} id - Server ID
   * @param {object} data - {filename: string, content_base64: string}
   * @returns {Promise} Upload result
   * @throws {Error} If request fails or validation error
   */
  uploadPlugin(id, data) {
    return apiClient.post(`/servers/${id}/plugins/upload`, data)
  },

  /**
   * Delete a plugin
   * @param {number} id - Server ID
   * @param {string} filename - Plugin filename
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deletePlugin(id, filename) {
    return apiClient.delete(`/servers/${id}/plugins/${filename}`)
  },

  /**
   * Toggle plugin enable/disable
   * @param {number} id - Server ID
   * @param {string} filename - Plugin filename
   * @param {boolean} enable - True to enable, false to disable
   * @returns {Promise} Toggle result
   * @throws {Error} If request fails
   */
  togglePlugin(id, filename, enable) {
    return apiClient.post(`/servers/${id}/plugins/${filename}/toggle`, null, {
      params: { enable }
    })
  },

  // Config Management
  /**
   * Get server.cfg parsed into CVARs
   * @param {number} id - Server ID
   * @returns {Promise<{data: {cvars: Object, categorized: Object}}>}
   * @throws {Error} If request fails
   */
  getServerConfig(id) {
    return apiClient.get(`/servers/${id}/config/server`)
  },

  /**
   * Update server.cfg CVARs
   * @param {number} id - Server ID
   * @param {object} data - {cvars: {cvar_name: value}}
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updateServerConfig(id, data) {
    return apiClient.put(`/servers/${id}/config/server`, data)
  },

  /**
   * Get mapcycle.txt map list
   * @param {number} id - Server ID
   * @returns {Promise<{data: {maps: Array}}>}
   * @throws {Error} If request fails
   */
  getMapcycle(id) {
    return apiClient.get(`/servers/${id}/config/mapcycle`)
  },

  /**
   * Update mapcycle.txt map list
   * @param {number} id - Server ID
   * @param {Array<string>} maps - List of map names
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updateMapcycle(id, maps) {
    return apiClient.put(`/servers/${id}/config/mapcycle`, maps)
  },

  // File Browser
  /**
   * Browse server files
   * @param {number} id - Server ID
   * @param {string} path - Directory path
   * @returns {Promise<{data: {files: Array, current_path: string}}>}
   * @throws {Error} If request fails
   */
  browseFiles(id, path = '') {
    return apiClient.get(`/servers/${id}/files/browse`, { params: { path } })
  },

  // Admin Management
  /**
   * Get admin users from users.ini
   * @param {number} id - Server ID
   * @returns {Promise<{data: {admins: Array}}>}
   * @throws {Error} If request fails
   */
  getAdminUsers(id) {
    return apiClient.get(`/servers/${id}/admin/users`)
  },

  /**
   * Add admin user
   * @param {number} id - Server ID
   * @param {object} data - {steam_id, flags, password, connection_flags}
   * @returns {Promise} Add result
   * @throws {Error} If request fails
   */
  addAdminUser(id, data) {
    return apiClient.post(`/servers/${id}/admin/users`, data)
  },

  /**
   * Delete admin user
   * @param {number} id - Server ID
   * @param {string} steamId - Steam ID
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deleteAdminUser(id, steamId) {
    return apiClient.delete(`/servers/${id}/admin/users/${steamId}`)
  },

  /**
   * Get ban list
   * @param {number} id - Server ID
   * @returns {Promise<{data: {bans: Array}}>}
   * @throws {Error} If request fails
   */
  getBans(id) {
    return apiClient.get(`/servers/${id}/admin/bans`)
  },

  /**
   * Add ban
   * @param {number} id - Server ID
   * @param {object} data - {ban_type, value, duration}
   * @returns {Promise} Add result
   * @throws {Error} If request fails
   */
  addBan(id, data) {
    return apiClient.post(`/servers/${id}/admin/bans`, data)
  },

  /**
   * Delete ban
   * @param {number} id - Server ID
   * @param {string} banType - "ip" or "steam_id"
   * @param {string} value - IP or Steam ID
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deleteBan(id, banType, value) {
    return apiClient.delete(`/servers/${id}/admin/bans/${banType}/${value}`)
  },

  // Player Actions (RCON)
  /**
   * Kick player via RCON
   * @param {number} id - Server ID
   * @param {number} slot - Player slot
   * @param {object} data - {reason}
   * @returns {Promise} Kick result
   * @throws {Error} If request fails
   */
  kickPlayerRcon(id, slot, data) {
    return apiClient.post(`/servers/${id}/players/${slot}/kick`, data)
  },

  /**
   * Slay player via RCON
   * @param {number} id - Server ID
   * @param {number} slot - Player slot
   * @param {object} data - {}
   * @returns {Promise} Slay result
   * @throws {Error} If request fails
   */
  slayPlayerRcon(id, slot, data) {
    return apiClient.post(`/servers/${id}/players/${slot}/slay`, data)
  },

  // Map Management
  /**
   * Get map library (all maps)
   * @param {number} id - Server ID
   * @returns {Promise<{data: {maps: Array, base_count: number, custom_count: number}}>}
   * @throws {Error} If request fails
   */
  getMapLibrary(id) {
    return apiClient.get(`/servers/${id}/maps/library`)
  },

  /**
   * Get mapcycle list
   * @param {number} id - Server ID
   * @returns {Promise<{data: {maps: Array}}>}
   * @throws {Error} If request fails
   */
  getMapcycleList(id) {
    return apiClient.get(`/servers/${id}/maps/mapcycle`)
  },

  /**
   * Update mapcycle list
   * @param {number} id - Server ID
   * @param {object} data - {maps: Array}
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updateMapcycleList(id, data) {
    return apiClient.put(`/servers/${id}/maps/mapcycle`, data)
  },

  // Backup Management
  /**
   * Get backup list
   * @param {number} id - Server ID
   * @param {string} type - Filter by type (config, full, database)
   * @returns {Promise<{data: {backups: Array, count: number, total_size: number}}>}
   * @throws {Error} If request fails
   */
  getBackups(id, type = null) {
    return apiClient.get(`/servers/${id}/backups`, { params: { backup_type: type } })
  },

  /**
   * Create backup
   * @param {number} id - Server ID
   * @param {string} type - Backup type (config or full)
   * @returns {Promise} Create result
   * @throws {Error} If request fails
   */
  createBackup(id, type) {
    return apiClient.post(`/servers/${id}/backups/create`, null, { params: { backup_type: type } })
  },

  /**
   * Restore from backup
   * @param {number} id - Server ID
   * @param {string} filename - Backup filename
   * @returns {Promise} Restore result
   * @throws {Error} If request fails
   */
  restoreBackup(id, filename) {
    return apiClient.post(`/servers/${id}/backups/${filename}/restore`)
  },

  /**
   * Delete backup
   * @param {number} id - Server ID
   * @param {string} filename - Backup filename
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deleteBackup(id, filename) {
    return apiClient.delete(`/servers/${id}/backups/${filename}`)
  },

  /**
   * Get backup schedule
   * @param {number} id - Server ID
   * @returns {Promise<{data: {schedule: Object}}>}
   * @throws {Error} If request fails
   */
  getBackupSchedule(id) {
    return apiClient.get(`/servers/${id}/backups/schedule`)
  },

  // Plugin Compiler (Phase 2)
  /**
   * Compile .sma plugin to .amxx
   * @param {number} id - Server ID
   * @param {object} data - {source_code: string, plugin_name: string}
   * @returns {Promise<{data: {compiled_data: string, filename: string, warnings: Array, output: string}}>}
   * @throws {Error} If request fails
   */
  compilePlugin(id, data) {
    return apiClient.post(`/servers/${id}/plugins/compile`, data).then(r => r.data)
  },

  /**
   * Validate plugin syntax
   * @param {number} id - Server ID
   * @param {object} data - {source_code: string, plugin_name: string}
   * @returns {Promise<{data: {valid: boolean, errors: string, warnings: Array}}>}
   * @throws {Error} If request fails
   */
  validatePluginSyntax(id, data) {
    return apiClient.post(`/servers/${id}/plugins/validate`, data).then(r => r.data)
  },

  /**
   * Get compiler info
   * @param {number} id - Server ID
   * @returns {Promise<{data: {available: boolean, version: string, compiler_path: string}}>}
   * @throws {Error} If request fails
   */
  getCompilerInfo(id) {
    return apiClient.get(`/servers/${id}/plugins/compiler-info`).then(r => r.data)
  },

  // Plugin Config Editor (Phase 2)
  /**
   * List plugin config files
   * @param {number} id - Server ID
   * @returns {Promise<{data: {configs: Array, count: number}}>}
   * @throws {Error} If request fails
   */
  listPluginConfigs(id) {
    return apiClient.get(`/servers/${id}/plugins/configs/list`).then(r => r.data)
  },

  /**
   * Get plugin config content
   * @param {number} id - Server ID
   * @param {string} filename - Config filename
   * @returns {Promise<{data: {filename: string, content: string, parsed: Object, size: number}}>}
   * @throws {Error} If request fails
   */
  getPluginConfig(id, filename) {
    return apiClient.get(`/servers/${id}/plugins/configs/${filename}`).then(r => r.data)
  },

  /**
   * Update plugin config
   * @param {number} id - Server ID
   * @param {string} filename - Config filename
   * @param {object} data - {content: string}
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updatePluginConfig(id, filename, data) {
    return apiClient.put(`/servers/${id}/plugins/configs/${filename}`, data).then(r => r.data)
  },

  // Plugin Logs Viewer (Phase 2)
  /**
   * List plugin log files
   * @param {number} id - Server ID
   * @returns {Promise<{data: {logs: Array, count: number}}>}
   * @throws {Error} If request fails
   */
  listPluginLogs(id) {
    return apiClient.get(`/servers/${id}/plugins/logs/list`).then(r => r.data)
  },

  /**
   * Get plugin log content
   * @param {number} id - Server ID
   * @param {string} filename - Log filename
   * @param {object} params - {lines: number, level: string, search: string}
   * @returns {Promise<{data: {entries: Array, total_lines: number, filtered_lines: number}}>}
   * @throws {Error} If request fails
   */
  getPluginLog(id, filename, params = {}) {
    return apiClient.get(`/servers/${id}/plugins/logs/${filename}`, { params }).then(r => r.data)
  },

  /**
   * Delete plugin log
   * @param {number} id - Server ID
   * @param {string} filename - Log filename
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deletePluginLog(id, filename) {
    return apiClient.delete(`/servers/${id}/plugins/logs/${filename}`).then(r => r.data)
  },

  // Config Templates (Phase 2)
  /**
   * Get config templates
   * @param {number} id - Server ID
   * @returns {Promise<{data: {templates: Array, count: number}}>}
   * @throws {Error} If request fails
   */
  getConfigTemplates(id) {
    return apiClient.get(`/servers/${id}/config/templates`).then(r => r.data)
  },

  /**
   * Apply config template
   * @param {number} id - Server ID
   * @param {object} data - {template_name: string}
   * @returns {Promise} Apply result
   * @throws {Error} If request fails
   */
  applyConfigTemplate(id, data) {
    return apiClient.post(`/servers/${id}/config/apply-template`, data).then(r => r.data)
  },

  // Config Backup & Restore (Phase 2)
  /**
   * Get config backup history
   * @param {number} id - Server ID
   * @returns {Promise<{data: {backups: Array, count: number}}>}
   * @throws {Error} If request fails
   */
  getConfigBackups(id) {
    return apiClient.get(`/servers/${id}/config/backups`).then(r => r.data)
  },

  /**
   * Create config backup
   * @param {number} id - Server ID
   * @returns {Promise} Create result
   * @throws {Error} If request fails
   */
  createConfigBackup(id) {
    return apiClient.post(`/servers/${id}/config/backup`).then(r => r.data)
  },

  /**
   * Get diff between current and backup
   * @param {number} id - Server ID
   * @param {string} filename - Backup filename
   * @returns {Promise<{data: {diff: Array, has_changes: boolean}}>}
   * @throws {Error} If request fails
   */
  getConfigDiff(id, filename) {
    return apiClient.get(`/servers/${id}/config/backups/${filename}/diff`).then(r => r.data)
  },

  /**
   * Restore from backup
   * @param {number} id - Server ID
   * @param {string} filename - Backup filename
   * @returns {Promise} Restore result
   * @throws {Error} If request fails
   */
  restoreConfigBackup(id, filename) {
    return apiClient.post(`/servers/${id}/config/backups/${filename}/restore`).then(r => r.data)
  },

  /**
   * Delete config backup
   * @param {number} id - Server ID
   * @param {string} filename - Backup filename
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deleteConfigBackup(id, filename) {
    return apiClient.delete(`/servers/${id}/config/backups/${filename}`).then(r => r.data)
  },

  // MOTD Editor (Phase 2)
  /**
   * Get MOTD content
   * @param {number} id - Server ID
   * @returns {Promise<{data: {content: string, size: number}}>}
   * @throws {Error} If request fails
   */
  getMotd(id) {
    return apiClient.get(`/servers/${id}/config/motd`).then(r => r.data)
  },

  /**
   * Update MOTD content
   * @param {number} id - Server ID
   * @param {object} data - {content: string}
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updateMotd(id, data) {
    return apiClient.put(`/servers/${id}/config/motd`, data).then(r => r.data)
  },

  // Player Statistics (Feature #17)
  /**
   * Get player leaderboard
   * @param {number} id - Server ID
   * @param {object} params - {sort_by, limit, min_playtime}
   * @returns {Promise<{data: {leaderboard: Array, total_players: number}}>}
   * @throws {Error} If request fails
   */
  getPlayerLeaderboard(id, params = {}) {
    return apiClient.get(`/servers/${id}/stats/leaderboard`, { params }).then(r => r.data)
  },

  /**
   * Get individual player statistics
   * @param {number} id - Server ID
   * @param {string} steamId - Player Steam ID
   * @returns {Promise<{data: Object}>}
   * @throws {Error} If request fails
   */
  getPlayerStats(id, steamId) {
    return apiClient.get(`/servers/${id}/stats/player/${steamId}`).then(r => r.data)
  },

  /**
   * Get top players in different categories
   * @param {number} id - Server ID
   * @param {number} limit - Number of top players per category
   * @returns {Promise<{data: {top_elo, top_kd, top_kills, top_headshots}}>}
   * @throws {Error} If request fails
   */
  getTopPlayers(id, limit = 5) {
    return apiClient.get(`/servers/${id}/stats/top-players`, { params: { limit } }).then(r => r.data)
  },

  /**
   * Get recent match history
   * @param {number} id - Server ID
   * @param {number} limit - Max results
   * @returns {Promise<{data: {matches: Array, total: number}}>}
   * @throws {Error} If request fails
   */
  getRecentMatches(id, limit = 20) {
    return apiClient.get(`/servers/${id}/stats/matches`, { params: { limit } }).then(r => r.data)
  },

  /**
   * Get player activity chart data
   * @param {number} id - Server ID
   * @param {number} days - Number of days
   * @returns {Promise<{data: {labels: Array, data: Array}}>}
   * @throws {Error} If request fails
   */
  getPlayerActivityChart(id, days = 30) {
    return apiClient.get(`/servers/${id}/stats/activity-chart`, { params: { days } }).then(r => r.data)
  },

  // Server Performance Metrics (Feature #18)
  /**
   * Get current server performance metrics
   * @param {number} id - Server ID
   * @returns {Promise<{data: Object}>}
   * @throws {Error} If request fails
   */
  getCurrentPerformance(id) {
    return apiClient.get(`/servers/${id}/performance/current`).then(r => r.data)
  },

  /**
   * Get performance metrics history
   * @param {number} id - Server ID
   * @param {object} params - {hours, interval}
   * @returns {Promise<{data: {history: Array, total_points: number}}>}
   * @throws {Error} If request fails
   */
  getPerformanceHistory(id, params = {}) {
    return apiClient.get(`/servers/${id}/performance/history`, { params }).then(r => r.data)
  },

  /**
   * Get performance metrics summary
   * @param {number} id - Server ID
   * @param {number} hours - Time range in hours
   * @returns {Promise<{data: Object}>}
   * @throws {Error} If request fails
   */
  getPerformanceSummary(id, hours = 24) {
    return apiClient.get(`/servers/${id}/performance/summary`, { params: { hours } }).then(r => r.data)
  },

  // Custom Map Uploader (Feature #19)
  /**
   * Upload custom map
   * @param {number} id - Server ID
   * @param {FormData} formData - Form data with file and metadata
   * @returns {Promise} Upload result
   * @throws {Error} If request fails
   */
  uploadCustomMap(id, formData) {
    return apiClient.post(`/servers/${id}/maps/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(r => r.data)
  },

  /**
   * Get custom uploaded maps
   * @param {number} id - Server ID
   * @returns {Promise<{data: {maps: Array, total: number}}>}
   * @throws {Error} If request fails
   */
  getCustomMaps(id) {
    return apiClient.get(`/servers/${id}/maps/custom`).then(r => r.data)
  },

  /**
   * Delete custom map
   * @param {number} id - Server ID
   * @param {number} mapId - Map ID
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deleteCustomMap(id, mapId) {
    return apiClient.delete(`/servers/${id}/maps/custom/${mapId}`).then(r => r.data)
  },

  // VIP System Manager (Feature #20)
  /**
   * Get VIP members list
   * @param {number} id - Server ID
   * @returns {Promise<{data: {vips: Array, total: number, active: number}}>}
   * @throws {Error} If request fails
   */
  getVIPMembers(id) {
    return apiClient.get(`/servers/${id}/vip/members`).then(r => r.data)
  },

  /**
   * Add VIP member
   * @param {number} id - Server ID
   * @param {object} data - VIP data
   * @returns {Promise} Add result
   * @throws {Error} If request fails
   */
  addVIPMember(id, data) {
    return apiClient.post(`/servers/${id}/vip/members`, data).then(r => r.data)
  },

  /**
   * Update VIP member
   * @param {number} id - Server ID
   * @param {number} vipId - VIP ID
   * @param {object} data - VIP data
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updateVIPMember(id, vipId, data) {
    return apiClient.put(`/servers/${id}/vip/members/${vipId}`, data).then(r => r.data)
  },

  /**
   * Delete VIP member
   * @param {number} id - Server ID
   * @param {number} vipId - VIP ID
   * @returns {Promise} Delete result
   * @throws {Error} If request fails
   */
  deleteVIPMember(id, vipId) {
    return apiClient.delete(`/servers/${id}/vip/members/${vipId}`).then(r => r.data)
  },

  /**
   * Toggle VIP status
   * @param {number} id - Server ID
   * @param {number} vipId - VIP ID
   * @returns {Promise} Toggle result
   * @throws {Error} If request fails
   */
  toggleVIPStatus(id, vipId) {
    return apiClient.post(`/servers/${id}/vip/members/${vipId}/toggle`).then(r => r.data)
  }
}
