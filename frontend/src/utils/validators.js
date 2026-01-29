/**
 * Response Validation Utilities
 * Validate API response structures to prevent runtime errors
 */

/**
 * Validate user response structure
 * @param {object} data - User data from API
 * @returns {boolean} True if valid
 */
export function validateUserResponse(data) {
  if (!data || typeof data !== 'object') return false
  return !!(data.id && data.username && data.email)
}

/**
 * Validate server response structure
 * @param {object} data - Server data from API
 * @returns {boolean} True if valid
 */
export function validateServerResponse(data) {
  if (!data || typeof data !== 'object') return false
  return !!(data.id && data.name && data.ip_address && data.port)
}

/**
 * Validate array response structure
 * @param {any} data - Data to validate
 * @returns {boolean} True if valid array
 */
export function validateArrayResponse(data) {
  return Array.isArray(data)
}

/**
 * Validate paginated response structure
 * @param {object} data - Response data
 * @returns {boolean} True if valid
 */
export function validatePaginatedResponse(data) {
  if (!data || typeof data !== 'object') return false
  return !!(
    Array.isArray(data.data) &&
    data.pagination &&
    typeof data.pagination.page === 'number' &&
    typeof data.pagination.total === 'number'
  )
}

/**
 * Validate package response structure
 * @param {object} data - Package data from API
 * @returns {boolean} True if valid
 */
export function validatePackageResponse(data) {
  if (!data || typeof data !== 'object') return false
  return !!(data.id && data.name && typeof data.price === 'number')
}

/**
 * Validate payment response structure
 * @param {object} data - Payment data from API
 * @returns {boolean} True if valid
 */
export function validatePaymentResponse(data) {
  if (!data || typeof data !== 'object') return false
  return !!(data.id && data.amount && data.status)
}

/**
 * Validate forum topic response structure
 * @param {object} data - Topic data from API
 * @returns {boolean} True if valid
 */
export function validateTopicResponse(data) {
  if (!data || typeof data !== 'object') return false
  return !!(data.id && data.title && data.author_id)
}

/**
 * Validate forum post response structure
 * @param {object} data - Post data from API
 * @returns {boolean} True if valid
 */
export function validatePostResponse(data) {
  if (!data || typeof data !== 'object') return false
  return !!(data.id && data.content && data.author_id)
}

/**
 * Safe data extractor with validation
 * @param {object} response - API response
 * @param {Function} validator - Validation function
 * @param {any} defaultValue - Default value if validation fails
 * @returns {any} Validated data or default
 */
export function safeExtract(response, validator, defaultValue = null) {
  try {
    const data = response?.data
    if (validator(data)) {
      return data
    }
    console.warn('Response validation failed:', data)
    return defaultValue
  } catch (error) {
    console.error('Failed to extract response data:', error)
    return defaultValue
  }
}

/**
 * Safe array extractor for paginated responses
 * @param {object} response - API response
 * @param {string} dataKey - Key containing array (default: 'data')
 * @returns {Array} Array data or empty array
 */
export function safeArrayExtract(response, dataKey = 'data') {
  try {
    const data = response?.data?.[dataKey]
    if (Array.isArray(data)) {
      return data
    }
    // Fallback for non-paginated responses
    if (Array.isArray(response?.data)) {
      return response.data
    }
    return []
  } catch (error) {
    console.error('Failed to extract array data:', error)
    return []
  }
}

/**
 * Safe pagination extractor
 * @param {object} response - API response
 * @returns {object} Pagination object with defaults
 */
export function safePaginationExtract(response) {
  const defaultPagination = {
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  }

  try {
    const pagination = response?.data?.pagination
    if (!pagination) return defaultPagination

    return {
      page: pagination.page || defaultPagination.page,
      per_page: pagination.per_page || defaultPagination.per_page,
      total: pagination.total || defaultPagination.total,
      pages: pagination.pages || defaultPagination.pages
    }
  } catch (error) {
    console.error('Failed to extract pagination:', error)
    return defaultPagination
  }
}
