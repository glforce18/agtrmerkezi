import apiClient from './client'

export default {
  // ===== SERVER DISCOVERY & LISTING =====

  // Get all public servers (v1)
  getServers(params = {}) {
    return apiClient.get('/servers', { params })
  },

  // Get live servers for homepage
  getLiveServers(limit = 10) {
    return apiClient.get('/servers/live', { params: { limit } })
  },

  // Get my servers (v1)
  getMyServers() {
    return apiClient.get('/servers/my-servers')
  },

  // Get my servers (v2)
  getMyServersV2(params = {}) {
    return apiClient.get('/v2/servers/my', { params })
  },

  // Get server by ID (v2)
  getServer(id) {
    return apiClient.get(`/v2/servers/${id}`)
  },

  // Search servers by Steam ID
  searchBySteamId(steamId) {
    return apiClient.get(`/v2/servers/search/steam/${steamId}`)
  },

  // Search servers by unique code
  searchByCode(code) {
    return apiClient.get(`/v2/servers/search/code/${code}`)
  },

  // ===== SERVER PACKAGES & ORDERING =====

  // Get available packages
  getPackages() {
    return apiClient.get('/servers/packages')
  },

  // Calculate custom package price
  calculatePrice(data) {
    return apiClient.post('/servers/calculate-price', data)
  },

  // Order package (pay later)
  orderPackage(data) {
    return apiClient.post('/servers/order/package', data)
  },

  // Order package with wallet
  orderPackageWallet(data) {
    return apiClient.post('/servers/order/package-wallet', data)
  },

  // Create server (v2)
  createServer(data) {
    return apiClient.post('/v2/servers/create', data)
  },

  // Delete server (v2)
  deleteServer(id) {
    return apiClient.delete(`/v2/servers/${id}`)
  },

  // ===== SERVER CONTROL =====

  // Server action (start, stop, restart) - v1
  serverAction(id, action) {
    return apiClient.post(`/servers/my-servers/${id}/action`, { action })
  },

  // Start server (v2)
  startServer(id) {
    return apiClient.post(`/v2/servers/${id}/start`)
  },

  // Stop server (v2)
  stopServer(id, force = false) {
    return apiClient.post(`/v2/servers/${id}/stop`, { force })
  },

  // Restart server (v2)
  restartServer(id) {
    return apiClient.post(`/v2/servers/${id}/restart`)
  },

  // Get server status
  getServerStatus(id) {
    return apiClient.get(`/servers/my-servers/${id}/status`)
  },

  // Get server status (v2)
  getServerStatusV2(id) {
    return apiClient.get(`/v2/servers/${id}/status`)
  },

  // Get installation progress
  getInstallation(id) {
    return apiClient.get(`/v2/servers/${id}/installation`)
  },

  // Complete server setup
  configureServer(id) {
    return apiClient.post(`/servers/my-servers/${id}/configure`)
  },

  // ===== RCON COMMANDS =====

  // Execute RCON command (v1)
  executeRCON(id, command) {
    return apiClient.post(`/servers/my-servers/${id}/rcon`, { command })
  },

  // Execute RCON command (v2)
  executeRCONV2(id, command) {
    return apiClient.post(`/v2/servers/${id}/rcon`, { command })
  },

  // Get RCON history (v1)
  getRCONHistory(id) {
    return apiClient.get(`/servers/my-servers/${id}/rcon-history`)
  },

  // Get RCON history (v2)
  getRCONHistoryV2(id, params = {}) {
    return apiClient.get(`/v2/servers/${id}/rcon/history`, { params })
  },

  // ===== PLAYER MANAGEMENT =====

  // Get active players (v1)
  getPlayers(id) {
    return apiClient.get(`/servers/my-servers/${id}/players`)
  },

  // Get active players (v2)
  getPlayersV2(id) {
    return apiClient.get(`/v2/servers/${id}/players`)
  },

  // Kick player
  kickPlayer(id, slot, reason = '') {
    return apiClient.post(`/v2/servers/${id}/players/${slot}/kick`, { reason })
  },

  // Ban player
  banPlayer(id, data) {
    return apiClient.post(`/v2/servers/${id}/players/ban`, data)
  },

  // Get bans
  getBans(id, activeOnly = true) {
    return apiClient.get(`/v2/servers/${id}/bans`, { params: { active_only: activeOnly } })
  },

  // Unban player
  unbanPlayer(id, banId) {
    return apiClient.delete(`/v2/servers/${id}/bans/${banId}`)
  },

  // ===== ADMIN MANAGEMENT =====

  // Get admins
  getAdmins(id, includeInactive = false) {
    return apiClient.get(`/v2/servers/${id}/admins`, { params: { include_inactive: includeInactive } })
  },

  // Add admin
  addAdmin(id, data) {
    return apiClient.post(`/v2/servers/${id}/admins`, data)
  },

  // Update admin
  updateAdmin(id, adminId, data) {
    return apiClient.put(`/v2/servers/${id}/admins/${adminId}`, data)
  },

  // Remove admin
  removeAdmin(id, adminId) {
    return apiClient.delete(`/v2/servers/${id}/admins/${adminId}`)
  },

  // Sync admins to server
  syncAdmins(id) {
    return apiClient.post(`/v2/servers/${id}/admins/sync`)
  },

  // Sync owner as admin
  syncOwnerAdmin(id) {
    return apiClient.post(`/v2/servers/${id}/admins/sync-owner`)
  },

  // ===== SERVER CONFIGURATION =====

  // Set server password
  setPassword(id, password) {
    return apiClient.post(`/servers/my-servers/${id}/password`, { password })
  },

  // Get available maps
  getMaps(id) {
    return apiClient.get(`/servers/my-servers/${id}/maps`)
  },

  // Change map
  changeMap(id, map) {
    return apiClient.post(`/servers/my-servers/${id}/change-map`, { map })
  },

  // Get config file
  getConfig(id, filename) {
    return apiClient.get(`/servers/my-servers/${id}/config`, { params: { filename } })
  },

  // Update config file
  updateConfig(id, data) {
    return apiClient.put(`/servers/my-servers/${id}/config`, data)
  },

  // ===== FILE MANAGEMENT =====

  // List server files
  getFiles(id, path = '') {
    return apiClient.get(`/servers/my-servers/${id}/files`, { params: { path } })
  },

  // View file content
  viewFile(id, path) {
    return apiClient.get(`/servers/my-servers/${id}/files/view`, { params: { path } })
  },

  // ===== PLUGIN MANAGEMENT =====

  // Get installed plugins
  getPlugins(id) {
    return apiClient.get(`/servers/my-servers/${id}/plugins`)
  },

  // Upload custom plugin
  uploadPlugin(id, file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post(`/servers/my-servers/${id}/plugins/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // Toggle plugin
  togglePlugin(id, pluginId, enabled) {
    return apiClient.put(`/servers/my-servers/${id}/plugins/${pluginId}/toggle`, { enabled })
  },

  // Delete custom plugin
  deletePlugin(id, pluginId) {
    return apiClient.delete(`/servers/my-servers/${id}/plugins/${pluginId}`)
  },

  // ===== LOGS & MONITORING =====

  // Get server logs
  getLogs(id) {
    return apiClient.get(`/servers/my-servers/${id}/logs`)
  },

  // Get resource usage
  getResources(id) {
    return apiClient.get(`/servers/my-servers/${id}/resources`)
  },

  // Verify panel password
  verifyPanelPassword(id, password) {
    return apiClient.post(`/v2/servers/${id}/verify-panel-password`, { password })
  }
}
