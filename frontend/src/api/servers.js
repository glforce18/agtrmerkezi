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
  }
}
