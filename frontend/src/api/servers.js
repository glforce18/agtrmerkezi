import apiClient from './client'

/**
 * Server API Service - Updated for Unified API v3
 * Uses /api/servers endpoints (merged from servers.py + server_v2.py)
 */
export default {
  // Get my servers
  getMyServers() {
    return apiClient.get('/servers/my')  // Updated to unified endpoint
  },

  // Get server by ID
  getServer(id) {
    return apiClient.get(`/servers/${id}`)  // Updated to unified endpoint
  },

  // Server control
  startServer(id) {
    return apiClient.post(`/servers/${id}/start`)  // Updated to unified endpoint
  },

  stopServer(id) {
    return apiClient.post(`/servers/${id}/stop`)  // Updated to unified endpoint
  },

  restartServer(id) {
    return apiClient.post(`/servers/${id}/restart`)  // Updated to unified endpoint
  },

  // RCON
  executeRCON(id, command) {
    return apiClient.post(`/servers/${id}/rcon`, { command })  // Updated to unified endpoint
  },

  // Players
  getPlayers(id) {
    return apiClient.get(`/servers/${id}/players`)  // Updated to unified endpoint
  },

  kickPlayer(id, slot, reason = '') {
    return apiClient.post(`/servers/${id}/players/${slot}/kick`, { reason })  // Updated to unified endpoint
  },

  // Packages
  getPackages() {
    return apiClient.get('/servers/packages')
  },

  // Order server
  orderServer(data) {
    return apiClient.post('/servers/order', data)
  },

  // Legacy wallet order
  orderPackageWallet(data) {
    return apiClient.post('/servers/order/package-wallet', data)
  }
}
