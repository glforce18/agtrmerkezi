/**
 * AGTR Merkezi - Security Utilities
 * XSS prevention, input sanitization, and validation
 */

/**
 * Sanitize HTML to prevent XSS attacks
 * @param {string} html - Raw HTML string
 * @returns {string} Sanitized string
 */
export function sanitizeHtml(html) {
  if (!html || typeof html !== 'string') return ''

  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
    '`': '&#x60;',
    '=': '&#x3D;'
  }

  return html.replace(/[&<>"'`=/]/g, char => map[char])
}

/**
 * Sanitize input for safe display (removes dangerous characters)
 * @param {string} input - User input
 * @returns {string} Sanitized input
 */
export function sanitizeInput(input) {
  if (!input || typeof input !== 'string') return ''

  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<[^>]*>/g, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .trim()
}

/**
 * Validate and sanitize URL
 * @param {string} url - URL to validate
 * @param {Array} allowedHosts - List of allowed hostnames
 * @returns {string|null} Sanitized URL or null if invalid
 */
export function sanitizeUrl(url, allowedHosts = []) {
  if (!url || typeof url !== 'string') return null

  try {
    const parsed = new URL(url, window.location.origin)

    // Block javascript: and data: protocols
    if (['javascript:', 'data:', 'vbscript:'].includes(parsed.protocol)) {
      return null
    }

    // Check allowed hosts if specified
    if (allowedHosts.length > 0 && !allowedHosts.includes(parsed.hostname)) {
      return null
    }

    return parsed.href
  } catch {
    // If URL parsing fails, check if it's a relative path
    if (url.startsWith('/') && !url.startsWith('//')) {
      return url
    }
    return null
  }
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email) && email.length <= 254
}

/**
 * Validate username format
 * @param {string} username - Username to validate
 * @returns {object} { valid: boolean, error: string|null }
 */
export function validateUsername(username) {
  if (!username || typeof username !== 'string') {
    return { valid: false, error: 'Kullanici adi gerekli' }
  }

  const trimmed = username.trim()

  if (trimmed.length < 3) {
    return { valid: false, error: 'Kullanici adi en az 3 karakter olmali' }
  }

  if (trimmed.length > 32) {
    return { valid: false, error: 'Kullanici adi en fazla 32 karakter olmali' }
  }

  if (!/^[a-zA-Z0-9_]+$/.test(trimmed)) {
    return { valid: false, error: 'Kullanici adi sadece harf, rakam ve alt cizgi icermeli' }
  }

  return { valid: true, error: null }
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} { valid: boolean, strength: number, errors: Array }
 */
export function validatePassword(password) {
  const errors = []
  let strength = 0

  if (!password || typeof password !== 'string') {
    return { valid: false, strength: 0, errors: ['Sifre gerekli'] }
  }

  if (password.length >= 8) strength++
  else errors.push('En az 8 karakter')

  if (/[A-Z]/.test(password)) strength++
  else errors.push('En az 1 buyuk harf')

  if (/[a-z]/.test(password)) strength++
  else errors.push('En az 1 kucuk harf')

  if (/[0-9]/.test(password)) strength++
  else errors.push('En az 1 rakam')

  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++
  else errors.push('En az 1 ozel karakter')

  return {
    valid: errors.length === 0,
    strength,
    errors
  }
}

/**
 * Rate limiter for client-side protection
 */
class RateLimiter {
  constructor(maxAttempts = 5, windowMs = 60000) {
    this.attempts = new Map()
    this.maxAttempts = maxAttempts
    this.windowMs = windowMs
  }

  /**
   * Check if action is allowed
   * @param {string} key - Unique identifier for the action
   * @returns {object} { allowed: boolean, remainingAttempts: number, resetIn: number }
   */
  check(key) {
    const now = Date.now()
    const record = this.attempts.get(key)

    if (!record || now - record.firstAttempt > this.windowMs) {
      this.attempts.set(key, { count: 1, firstAttempt: now })
      return { allowed: true, remainingAttempts: this.maxAttempts - 1, resetIn: 0 }
    }

    if (record.count >= this.maxAttempts) {
      const resetIn = Math.ceil((record.firstAttempt + this.windowMs - now) / 1000)
      return { allowed: false, remainingAttempts: 0, resetIn }
    }

    record.count++
    return {
      allowed: true,
      remainingAttempts: this.maxAttempts - record.count,
      resetIn: 0
    }
  }

  /**
   * Reset attempts for a key
   * @param {string} key - Key to reset
   */
  reset(key) {
    this.attempts.delete(key)
  }

  /**
   * Clear all attempts
   */
  clear() {
    this.attempts.clear()
  }
}

// Export singleton rate limiters for common use cases
export const loginRateLimiter = new RateLimiter(5, 60000) // 5 attempts per minute
export const registerRateLimiter = new RateLimiter(3, 300000) // 3 attempts per 5 minutes
export const apiRateLimiter = new RateLimiter(100, 60000) // 100 requests per minute

/**
 * CSRF token management
 */
export function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]')
  return meta?.getAttribute('content') || ''
}

/**
 * Check if running in secure context (HTTPS)
 * @returns {boolean}
 */
export function isSecureContext() {
  return window.isSecureContext || window.location.protocol === 'https:'
}

/**
 * Generate random string for nonces
 * @param {number} length - Length of string
 * @returns {string}
 */
export function generateNonce(length = 16) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  const array = new Uint8Array(length)
  crypto.getRandomValues(array)
  for (let i = 0; i < length; i++) {
    result += chars[array[i] % chars.length]
  }
  return result
}

/**
 * Debounce function to limit rapid calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function}
 */
export function debounce(func, wait = 300) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function to limit call frequency
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit in ms
 * @returns {Function}
 */
export function throttle(func, limit = 1000) {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

export default {
  sanitizeHtml,
  sanitizeInput,
  sanitizeUrl,
  isValidEmail,
  validateUsername,
  validatePassword,
  loginRateLimiter,
  registerRateLimiter,
  apiRateLimiter,
  getCsrfToken,
  isSecureContext,
  generateNonce,
  debounce,
  throttle
}
