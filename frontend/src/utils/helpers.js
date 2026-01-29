/**
 * UI Helper Utilities
 * Reusable functions for status badges, game names, and UI formatting
 */

/**
 * Get badge CSS class for status
 * @param {string} status - Server or payment status
 * @returns {string} Badge CSS class
 */
export function getStatusBadge(status) {
  const statusLower = status?.toLowerCase() || ''
  const badges = {
    running: 'badge-success',
    stopped: 'badge-neutral',
    pending: 'badge-warning',
    suspended: 'badge-error',
    error: 'badge-error',
    installing: 'badge-info',
    rejected: 'badge-error',
    creating: 'badge-info',
    completed: 'badge-success',
    cancelled: 'badge-error',
    active: 'badge-success',
    inactive: 'badge-neutral'
  }
  return badges[statusLower] || 'badge-neutral'
}

/**
 * Get localized status text
 * @param {string} status - Server or payment status
 * @returns {string} Localized status text
 */
export function getStatusText(status) {
  const statusLower = status?.toLowerCase() || ''
  const texts = {
    running: 'Aktif',
    stopped: 'Kapalı',
    pending: 'Beklemede',
    suspended: 'Askıda',
    error: 'Hata',
    installing: 'Kuruluyor',
    rejected: 'Reddedildi',
    creating: 'Oluşturuluyor',
    completed: 'Tamamlandı',
    cancelled: 'İptal Edildi',
    active: 'Aktif',
    inactive: 'Pasif'
  }
  return texts[statusLower] || status
}

/**
 * Get localized game type name
 * @param {string} gameType - Game type code
 * @returns {string} Localized game name
 */
export function getGameName(gameType) {
  const gameUpper = gameType?.toUpperCase() || ''
  const names = {
    'CS16': 'CS 1.6',
    'HLDM': 'Half-Life DM',
    'AG': 'Adrenaline Gamer',
    'CSTRIKE': 'CS 1.6',
    'CZERO': 'Condition Zero',
    'VALVE': 'Half-Life',
    'TFC': 'Team Fortress Classic',
    'DOD': 'Day of Defeat',
    'DMC': 'Deathmatch Classic',
    'RICOCHET': 'Ricochet',
    'HL': 'Half-Life'
  }
  return names[gameUpper] || gameType
}

/**
 * Get localized payment method name
 * @param {string} method - Payment method code
 * @returns {string} Localized payment method
 */
export function getPaymentMethod(method) {
  const methods = {
    bank_transfer: 'Banka Havalesi',
    credit_card: 'Kredi Kartı',
    balance: 'Bakiye',
    papara: 'Papara',
    paypal: 'PayPal',
    crypto: 'Kripto Para'
  }
  return methods[method] || method || 'N/A'
}

/**
 * Format date to localized string
 * @param {string|Date} dateString - Date to format
 * @param {boolean} includeTime - Include time in output
 * @returns {string} Formatted date
 */
export function formatDate(dateString, includeTime = true) {
  if (!dateString) return 'N/A'

  const date = new Date(dateString)
  const options = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }

  if (includeTime) {
    options.hour = '2-digit'
    options.minute = '2-digit'
  }

  return date.toLocaleDateString('tr-TR', options)
}

/**
 * Format currency (Turkish Lira)
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency
 */
export function formatCurrency(amount) {
  if (amount === null || amount === undefined) return '₺0.00'
  return `₺${Number(amount).toFixed(2)}`
}

/**
 * Format number with thousands separator
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return Number(num).toLocaleString('tr-TR')
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 100) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
