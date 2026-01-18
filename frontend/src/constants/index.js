/**
 * AGTR Merkezi - Merkezi Sabitler
 * Tüm sabit değerler burada tanımlanır
 */

// ==================== STORAGE KEYS ====================
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  DARK_MODE: 'agtr-dark-mode',
  LANGUAGE: 'agtr-language',
  USER_PREFERENCES: 'agtr-user-prefs'
}

// ==================== COOKIE KEYS ====================
export const COOKIE_KEYS = {
  CSRF_TOKEN: 'csrf_token',
  SESSION: 'session_id'
}

// ==================== API CONFIG ====================
export const API_CONFIG = {
  BASE_URL: '/api',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
}

// ==================== USER ROLES ====================
export const USER_ROLES = {
  USER: 'user',
  MODERATOR: 'moderator',
  ADMIN: 'admin',
  SUPERADMIN: 'superadmin'
}

export const ADMIN_ROLES = [USER_ROLES.ADMIN, USER_ROLES.SUPERADMIN]

// ==================== USER STATUS ====================
export const USER_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  BANNED: 'banned',
  SUSPENDED: 'suspended'
}

// ==================== PAGINATION ====================
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZES: [10, 20, 50, 100]
}

// ==================== WALLET ====================
export const WALLET = {
  ARMOR_RATE: 100, // 1 TL = 100 Armor
  MIN_DEPOSIT: 10,
  MAX_DEPOSIT: 10000
}

// ==================== VALIDATION ====================
export const VALIDATION = {
  USERNAME_MIN: 3,
  USERNAME_MAX: 20,
  PASSWORD_MIN: 8,
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
}

export default {
  STORAGE_KEYS,
  COOKIE_KEYS,
  API_CONFIG,
  USER_ROLES,
  ADMIN_ROLES,
  USER_STATUS,
  PAGINATION,
  WALLET,
  VALIDATION
}
