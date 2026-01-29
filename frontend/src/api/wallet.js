import apiClient from './client'

/**
 * Wallet API Service
 * Manages TL (Turkish Lira) balance and Armor (coin) transactions
 */
export default {
  // Balance
  /**
   * Get current wallet balance (TL and Armor)
   * @returns {Promise} Balance data
   */
  getBalance() {
    return apiClient.get('/wallet/balance')
  },

  // TL Packages
  /**
   * Get available TL top-up packages
   * @returns {Promise} List of TL packages
   */
  getPackages() {
    return apiClient.get('/wallet/packages')
  },

  /**
   * Purchase a TL package
   * @param {number} packageId - Package ID to purchase
   * @returns {Promise} Purchase result
   */
  purchasePackage(packageId) {
    return apiClient.post('/wallet/purchase', { package_id: packageId })
  },

  // Armor (Coin) Packages
  /**
   * Get available Armor packages
   * @returns {Promise} List of Armor packages
   */
  getArmorPackages() {
    return apiClient.get('/wallet/armor-packages')
  },

  /**
   * Buy an Armor package
   * @param {number} packageId - Armor package ID to purchase
   * @returns {Promise} Purchase result
   */
  buyArmorPackage(packageId) {
    return apiClient.post('/wallet/armor/purchase', { package_id: packageId })
  },

  // Transactions
  /**
   * Get wallet transaction history
   * @param {object} params - Query parameters (page, per_page, type, etc.)
   * @returns {Promise} Transaction list with pagination
   */
  getTransactions(params = {}) {
    return apiClient.get('/wallet/transactions', { params })
  },

  // Money Operations
  /**
   * Transfer money to another user
   * @param {object} data - Transfer data (recipient, amount, etc.)
   * @returns {Promise} Transfer result
   */
  transfer(data) {
    return apiClient.post('/wallet/transfer', data)
  },

  /**
   * Exchange TL to Armor coins
   * @param {object} data - Exchange data (amount, etc.)
   * @returns {Promise} Exchange result
   */
  exchange(data) {
    return apiClient.post('/wallet/exchange', data)
  },

  /**
   * Deposit TL to wallet
   * @param {object} data - Deposit data (amount, method, etc.)
   * @returns {Promise} Deposit result
   */
  deposit(data) {
    return apiClient.post('/wallet/deposit', data)
  }
}
