/**
 * AGTR Merkezi - HTTP Utilities
 * CSRF token, headers ve ortak HTTP işlemleri
 */

import { STORAGE_KEYS, COOKIE_KEYS } from '@/constants'

/**
 * Cookie'den değer al
 * @param {string} name - Cookie adı
 * @returns {string|null} Cookie değeri
 */
export function getCookie(name) {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [cookieName, cookieValue] = cookie.trim().split('=')
    if (cookieName === name) {
      return decodeURIComponent(cookieValue)
    }
  }
  return null
}

/**
 * CSRF token al
 * @returns {string|null} CSRF token
 */
export function getCsrfToken() {
  return getCookie(COOKIE_KEYS.CSRF_TOKEN)
}

/**
 * Access token al
 * @returns {string|null} Access token
 */
export function getAccessToken() {
  return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
}

/**
 * Access token kaydet
 * @param {string} token - Access token
 */
export function setAccessToken(token) {
  localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token)
}

/**
 * Access token sil
 */
export function removeAccessToken() {
  localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
}

/**
 * API istekleri için standart headers oluştur
 * @param {boolean} includeContentType - Content-Type header eklensin mi
 * @returns {Object} Headers objesi
 */
export function getApiHeaders(includeContentType = true) {
  const headers = {}

  // Content-Type
  if (includeContentType) {
    headers['Content-Type'] = 'application/json'
  }

  // Authorization
  const token = getAccessToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // CSRF Token
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }

  return headers
}

/**
 * Multipart form data için headers (file upload)
 * @returns {Object} Headers objesi
 */
export function getUploadHeaders() {
  const headers = {}

  // Authorization
  const token = getAccessToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // CSRF Token
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }

  // Content-Type multipart için eklenmez, browser otomatik ayarlar
  return headers
}

/**
 * API isteği yap (basitleştirilmiş fetch wrapper)
 * @param {string} url - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 */
export async function apiRequest(url, options = {}) {
  const defaultOptions = {
    headers: getApiHeaders(options.method !== 'GET')
  }

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  }

  const response = await fetch(url, mergedOptions)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Bir hata oluştu' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

/**
 * GET isteği
 */
export function apiGet(url, options = {}) {
  return apiRequest(url, { ...options, method: 'GET' })
}

/**
 * POST isteği
 */
export function apiPost(url, data, options = {}) {
  return apiRequest(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/**
 * PUT isteği
 */
export function apiPut(url, data, options = {}) {
  return apiRequest(url, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * DELETE isteği
 */
export function apiDelete(url, options = {}) {
  return apiRequest(url, { ...options, method: 'DELETE' })
}

export default {
  getCookie,
  getCsrfToken,
  getAccessToken,
  setAccessToken,
  removeAccessToken,
  getApiHeaders,
  getUploadHeaders,
  apiRequest,
  apiGet,
  apiPost,
  apiPut,
  apiDelete
}
