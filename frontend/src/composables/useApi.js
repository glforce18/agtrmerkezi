import { ref } from 'vue'
import { useUIStore } from '@/stores/ui'

// Error types for better distinction
export const ApiErrorType = {
  NETWORK: 'NETWORK',
  TIMEOUT: 'TIMEOUT',
  SERVER: 'SERVER',
  AUTH: 'AUTH',
  VALIDATION: 'VALIDATION',
  NOT_FOUND: 'NOT_FOUND',
  RATE_LIMIT: 'RATE_LIMIT',
  UNKNOWN: 'UNKNOWN'
}

// Classify error type based on error and response
function classifyError(err) {
  // Network errors (fetch failed)
  if (err instanceof TypeError && err.message.includes('fetch')) {
    return ApiErrorType.NETWORK
  }

  // Timeout errors
  if (err.name === 'AbortError' || err.message?.includes('timeout')) {
    return ApiErrorType.TIMEOUT
  }

  const status = err.response?.status

  if (status) {
    if (status === 401 || status === 403) return ApiErrorType.AUTH
    if (status === 404) return ApiErrorType.NOT_FOUND
    if (status === 422 || status === 400) return ApiErrorType.VALIDATION
    if (status === 429) return ApiErrorType.RATE_LIMIT
    if (status >= 500) return ApiErrorType.SERVER
  }

  return ApiErrorType.UNKNOWN
}

// Get user-friendly error message
function getErrorMessage(err, errorType) {
  const messages = {
    [ApiErrorType.NETWORK]: 'Ag baglantisi hatasi. Lutfen internet baglantinizi kontrol edin.',
    [ApiErrorType.TIMEOUT]: 'Istek zaman asimina ugradi. Lutfen tekrar deneyin.',
    [ApiErrorType.SERVER]: 'Sunucu hatasi. Lutfen daha sonra tekrar deneyin.',
    [ApiErrorType.AUTH]: 'Oturum suresi doldu. Lutfen tekrar giriş yapin.',
    [ApiErrorType.VALIDATION]: err.response?.data?.detail || 'Girdi hatasi. Lutfen bilgileri kontrol edin.',
    [ApiErrorType.NOT_FOUND]: 'Istenen kaynak bulunamadi.',
    [ApiErrorType.RATE_LIMIT]: 'Cok fazla istek gönderildi. Lutfen biraz bekleyin.',
    [ApiErrorType.UNKNOWN]: err.response?.data?.detail || err.message || 'Bir hata olustu.'
  }

  return messages[errorType] || messages[ApiErrorType.UNKNOWN]
}

// Check if error is retryable
function isRetryable(errorType) {
  return [ApiErrorType.NETWORK, ApiErrorType.TIMEOUT, ApiErrorType.SERVER].includes(errorType)
}

// Sleep utility for retry delay
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

export function useApi(apiCall, options = {}) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    retryBackoff = true,
    showNotification = true
  } = options

  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const errorType = ref(null)
  const retryCount = ref(0)
  const uiStore = useUIStore()

  const execute = async (...args) => {
    loading.value = true
    error.value = null
    errorType.value = null
    retryCount.value = 0

    let lastError = null

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await apiCall(...args)
        data.value = response
        return response
      } catch (err) {
        lastError = err
        const errType = classifyError(err)

        // If not retryable or last attempt, throw
        if (!isRetryable(errType) || attempt === maxRetries) {
          errorType.value = errType
          error.value = getErrorMessage(err, errType)

          if (showNotification) {
            uiStore.addNotification({
              type: 'error',
              message: error.value
            })
          }

          throw err
        }

        // Wait before retry with optional exponential backoff
        retryCount.value = attempt + 1
        const delay = retryBackoff ? retryDelay * Math.pow(2, attempt) : retryDelay
        console.warn(`API call failed, retrying in ${delay}ms... (attempt ${attempt + 1}/${maxRetries})`)
        await sleep(delay)
      }
    }

    // Should not reach here, but just in case
    throw lastError
  }

  return {
    data,
    loading,
    error,
    errorType,
    retryCount,
    execute
  }
}
