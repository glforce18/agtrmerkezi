import apiClient from './client'

/**
 * Admin API Service
 * Admin-only endpoints for server approval, user management, payments, and statistics
 * @requires Admin role authentication
 */
export default {
  // Server Approval
  /**
   * Get list of pending server approval requests
   * @returns {Promise<{data: Array}>} Pending servers awaiting approval
   * @throws {Error} If request fails or user is not admin
   */
  getPendingServers() {
    return apiClient.get('/admin/server-approval/pending-servers')
  },

  /**
   * Approve or reject a server
   * @param {number} serverId - Server ID to approve/reject
   * @param {boolean} approved - True to approve, false to reject
   * @param {string|null} reason - Optional reason for rejection
   * @returns {Promise} Approval result
   * @throws {Error} If request fails
   */
  approveServer(serverId, approved, reason = null) {
    return apiClient.post('/admin/server-approval/approve', {
      server_id: serverId,
      approved,
      reason
    })
  },

  // User Management
  /**
   * Get paginated list of users
   * @param {object} params - Query parameters (page, per_page, search, role, status)
   * @returns {Promise<{data: Array, pagination: Object}>} Users with pagination
   * @throws {Error} If request fails
   */
  getUsers(params) {
    return apiClient.get('/admin/users', { params })
  },

  /**
   * Get single user by ID
   * @param {number} userId - User ID
   * @returns {Promise<{data: Object}>} User details
   * @throws {Error} If request fails or user not found
   */
  getUser(userId) {
    return apiClient.get(`/admin/users/${userId}`)
  },

  /**
   * Update user details
   * @param {number} userId - User ID
   * @param {object} data - User data to update (role, status, balance, etc.)
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updateUser(userId, data) {
    return apiClient.put(`/admin/users/${userId}`, data)
  },

  // Stats
  /**
   * Get admin dashboard statistics
   * @returns {Promise<{data: Object}>} Dashboard stats (users, servers, revenue, etc.)
   * @throws {Error} If request fails
   */
  getDashboardStats() {
    return apiClient.get('/admin/dashboard/stats')
  },

  // Payments
  /**
   * Get payment statistics
   * @returns {Promise<{data: Object}>} Payment stats (pending, completed, total revenue)
   * @throws {Error} If request fails
   */
  getPaymentsStats() {
    return apiClient.get('/admin/payments/stats')
  },

  /**
   * Get pending payments awaiting approval
   * @returns {Promise<{data: Array}>} Pending payments
   * @throws {Error} If request fails
   */
  getPaymentsPending() {
    return apiClient.get('/admin/commerce/payments/pending')
  },

  /**
   * Get paginated list of all payments
   * @param {object} params - Query parameters (page, per_page, status)
   * @returns {Promise<{data: Array, pagination: Object}>} Payments with pagination
   * @throws {Error} If request fails
   */
  getPaymentsList(params) {
    return apiClient.get('/admin/commerce/payments', { params })
  },

  /**
   * Approve a payment
   * @param {number} paymentId - Payment ID to approve
   * @returns {Promise} Approval result
   * @throws {Error} If request fails
   */
  approvePayment(paymentId) {
    return apiClient.post(`/admin/commerce/payments/${paymentId}/approve`)
  },

  /**
   * Reject a payment with reason
   * @param {number} paymentId - Payment ID to reject
   * @param {string} reason - Rejection reason
   * @returns {Promise} Rejection result
   * @throws {Error} If request fails
   */
  rejectPayment(paymentId, reason) {
    return apiClient.post(`/admin/commerce/payments/${paymentId}/reject`, { reason })
  },

  // Servers
  /**
   * Get server statistics
   * @returns {Promise<{data: Object}>} Server stats (total, active, pending, suspended)
   * @throws {Error} If request fails
   */
  getServersStats() {
    return apiClient.get('/admin/servers/stats')
  },

  /**
   * Get paginated list of all servers
   * @param {object} params - Query parameters (page, per_page, status, game_type)
   * @returns {Promise<{data: Array, pagination: Object}>} Servers with pagination
   * @throws {Error} If request fails
   */
  getServersList(params) {
    return apiClient.get('/admin/servers', { params })
  },

  /**
   * Update server status
   * @param {number} serverId - Server ID
   * @param {string} status - New status (running, stopped, suspended, etc.)
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updateServerStatus(serverId, status) {
    return apiClient.put(`/admin/servers/${serverId}/status`, { status })
  },

  // Packages
  /**
   * Get paginated list of server packages
   * @param {object} params - Query parameters (page, per_page, game_type)
   * @returns {Promise<{data: Array, pagination: Object}>} Packages with pagination
   * @throws {Error} If request fails
   */
  getPackagesList(params) {
    return apiClient.get('/admin/commerce/packages', { params })
  },

  /**
   * Update server package
   * @param {number} packageId - Package ID
   * @param {object} data - Package data (name, price, slots, features, etc.)
   * @returns {Promise} Update result
   * @throws {Error} If request fails
   */
  updatePackage(packageId, data) {
    return apiClient.put(`/admin/commerce/packages/${packageId}`, data)
  },

  /**
   * Create new server package
   * @param {object} data - Package data (name, price, slots, game_type, etc.)
   * @returns {Promise} Created package
   * @throws {Error} If request fails or validation error
   */
  createPackage(data) {
    return apiClient.post('/admin/commerce/packages', data)
  },

  /**
   * Delete server package
   * @param {number} packageId - Package ID to delete
   * @returns {Promise} Deletion result
   * @throws {Error} If request fails or package is in use
   */
  deletePackage(packageId) {
    return apiClient.delete(`/admin/commerce/packages/${packageId}`)
  },

  // Shared System Management
  /**
   * Get shared installation system status
   * @returns {Promise<{data: Object}>} Shared templates status, disk usage, savings
   * @throws {Error} If request fails
   */
  getSharedSystemStatus() {
    return apiClient.get('/admin/shared-system/status')
  },

  /**
   * Get detailed disk usage analytics with caching
   * @param {boolean} forceRefresh - Force cache refresh
   * @returns {Promise<{data: Object}>} Disk usage breakdown per server
   * @throws {Error} If request fails
   */
  getDiskUsageAnalytics(forceRefresh = false) {
    return apiClient.get('/admin/shared-system/disk-usage', {
      params: { force_refresh: forceRefresh }
    })
  },

  /**
   * Validate template integrity
   * @param {string} templateName - Template name (e.g., 'ag_base', 'hlds_base')
   * @returns {Promise<{data: Object}>} Validation result with issues
   * @throws {Error} If request fails or template not found
   */
  validateTemplate(templateName) {
    return apiClient.post(`/admin/shared-system/validate-template/${templateName}`)
  },

  /**
   * Find and optionally delete orphaned server directories
   * @param {boolean} confirm - If true, actually delete orphans. If false, preview only.
   * @returns {Promise<{data: Object}>} Orphan list and deletion results
   * @throws {Error} If request fails
   */
  cleanupOrphans(confirm = false) {
    return apiClient.post('/admin/shared-system/cleanup-orphans', null, {
      params: { confirm }
    })
  },

  /**
   * Get installation progress and logs for a server
   * @param {number} serverId - Server ID
   * @param {number} lines - Number of log lines to return (10-500)
   * @returns {Promise<{data: Object}>} Installation logs and errors
   * @throws {Error} If request fails or server not found
   */
  getInstallationLog(serverId, lines = 50) {
    return apiClient.get(`/admin/shared-system/servers/${serverId}/installation-log`, {
      params: { lines }
    })
  },

  /**
   * Clear disk usage cache
   * @returns {Promise} Cache clear result
   * @throws {Error} If request fails
   */
  clearDiskCache() {
    return apiClient.post('/admin/shared-system/cache/clear')
  },

  /**
   * Get list of servers (for installation monitor)
   * @param {object} params - Query parameters (status_filter, page, per_page)
   * @returns {Promise<{data: Array}>} Servers matching filter
   * @throws {Error} If request fails
   */
  getServers(params) {
    return apiClient.get('/admin/servers', { params })
  }
}
