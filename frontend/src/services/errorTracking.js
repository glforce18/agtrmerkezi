/**
 * Error Tracking Service
 * Centralized error handling and reporting for AGTR Merkezi
 *
 * Can be extended to integrate with:
 * - Sentry (https://sentry.io)
 * - LogRocket
 * - Bugsnag
 * - Custom backend endpoint
 */

const isDev = import.meta.env.DEV
const API_BASE = '/api'

// Error categories
export const ErrorCategory = {
  NETWORK: 'network',
  API: 'api',
  VALIDATION: 'validation',
  AUTH: 'auth',
  UI: 'ui',
  UNKNOWN: 'unknown'
}

// Error severity levels
export const ErrorSeverity = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
}

// Error queue for batching
let errorQueue = []
let flushTimeout = null
const FLUSH_INTERVAL = 5000 // 5 seconds
const MAX_QUEUE_SIZE = 10

/**
 * Get user context for error reports
 */
const getUserContext = () => {
  try {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null

    return {
      isAuthenticated: !!token,
      userId: user?.id || null,
      username: user?.username || null,
      role: user?.role || null
    }
  } catch {
    return { isAuthenticated: false }
  }
}

/**
 * Get browser/environment context
 */
const getEnvironmentContext = () => ({
  url: window.location.href,
  userAgent: navigator.userAgent,
  language: navigator.language,
  screenSize: `${window.innerWidth}x${window.innerHeight}`,
  timestamp: new Date().toISOString(),
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
})

/**
 * Format error for logging/sending
 */
const formatError = (error, category = ErrorCategory.UNKNOWN, severity = ErrorSeverity.MEDIUM, extra = {}) => ({
  message: error?.message || String(error),
  stack: error?.stack || null,
  category,
  severity,
  user: getUserContext(),
  environment: getEnvironmentContext(),
  extra,
  fingerprint: generateFingerprint(error)
})

/**
 * Generate error fingerprint for deduplication
 */
const generateFingerprint = (error) => {
  const str = `${error?.message || ''}${error?.stack?.split('\n')[1] || ''}`
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash).toString(16)
}

/**
 * Log error to console in development
 */
const logToConsole = (formattedError) => {
  if (!isDev) return

  const style = {
    [ErrorSeverity.LOW]: 'color: #3b82f6',
    [ErrorSeverity.MEDIUM]: 'color: #f97316',
    [ErrorSeverity.HIGH]: 'color: #ef4444',
    [ErrorSeverity.CRITICAL]: 'color: #fff; background: #ef4444; padding: 2px 6px; border-radius: 3px'
  }

  console.group(`%c[${formattedError.severity.toUpperCase()}] ${formattedError.category}`, style[formattedError.severity])
  console.error('Message:', formattedError.message)
  if (formattedError.stack) console.error('Stack:', formattedError.stack)
  console.log('Context:', { user: formattedError.user, environment: formattedError.environment })
  if (Object.keys(formattedError.extra).length) console.log('Extra:', formattedError.extra)
  console.groupEnd()
}

/**
 * Send errors to backend (batched)
 */
const sendToBackend = async (errors) => {
  if (isDev || errors.length === 0) return

  try {
    const token = localStorage.getItem('access_token')
    await fetch(`${API_BASE}/errors/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ errors })
    })
  } catch (e) {
    // Silent fail - don't create infinite loop
    if (isDev) console.warn('Failed to send error report:', e)
  }
}

/**
 * Flush error queue
 */
const flushQueue = () => {
  if (errorQueue.length === 0) return

  const errors = [...errorQueue]
  errorQueue = []
  sendToBackend(errors)
}

/**
 * Add error to queue
 */
const queueError = (formattedError) => {
  errorQueue.push(formattedError)

  // Flush immediately if queue is full
  if (errorQueue.length >= MAX_QUEUE_SIZE) {
    flushQueue()
    return
  }

  // Schedule flush
  if (!flushTimeout) {
    flushTimeout = setTimeout(() => {
      flushTimeout = null
      flushQueue()
    }, FLUSH_INTERVAL)
  }
}

/**
 * Main tracking function
 */
export const trackError = (error, category = ErrorCategory.UNKNOWN, severity = ErrorSeverity.MEDIUM, extra = {}) => {
  const formattedError = formatError(error, category, severity, extra)

  // Only log to console in dev mode
  if (isDev) {
    logToConsole(formattedError)
  }

  // Queue for backend in production
  if (!isDev) {
    queueError(formattedError)
  }

  return formattedError
}

/**
 * Track API errors
 */
export const trackApiError = (error, endpoint, method = 'GET', extra = {}) => {
  const severity = error?.status >= 500 ? ErrorSeverity.HIGH : ErrorSeverity.MEDIUM
  return trackError(error, ErrorCategory.API, severity, {
    endpoint,
    method,
    status: error?.status,
    ...extra
  })
}

/**
 * Track network errors
 */
export const trackNetworkError = (error, url, extra = {}) => {
  return trackError(error, ErrorCategory.NETWORK, ErrorSeverity.HIGH, {
    url,
    online: navigator.onLine,
    ...extra
  })
}

/**
 * Track authentication errors
 */
export const trackAuthError = (error, action, extra = {}) => {
  return trackError(error, ErrorCategory.AUTH, ErrorSeverity.MEDIUM, {
    action,
    ...extra
  })
}

/**
 * Track UI/Component errors
 */
export const trackUIError = (error, component, extra = {}) => {
  return trackError(error, ErrorCategory.UI, ErrorSeverity.MEDIUM, {
    component,
    ...extra
  })
}

/**
 * Initialize global error handlers
 */
export const initErrorTracking = (app) => {
  // Vue error handler
  app.config.errorHandler = (err, instance, info) => {
    trackUIError(err, instance?.$options?.name || 'Unknown', { info })

    // Show user-friendly message
    if (window.$message) {
      window.$message.error('Bir hata oluştu. Lütfen sayfayı yenileyin.')
    }
  }

  // Vue warning handler (dev only)
  if (isDev) {
    app.config.warnHandler = (msg, instance, trace) => {
      console.warn(`[Vue warn]: ${msg}`, { component: instance?.$options?.name, trace })
    }
  }

  // Unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    trackError(
      event.reason || new Error('Unhandled Promise Rejection'),
      ErrorCategory.UNKNOWN,
      ErrorSeverity.HIGH,
      { type: 'unhandledrejection' }
    )
  })

  // Global JavaScript errors
  window.addEventListener('error', (event) => {
    // Ignore script loading errors
    if (event.target?.tagName === 'SCRIPT') {
      trackNetworkError(
        new Error(`Script load failed: ${event.target.src}`),
        event.target.src
      )
      return
    }

    trackError(
      event.error || new Error(event.message),
      ErrorCategory.UNKNOWN,
      ErrorSeverity.HIGH,
      {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }
    )
  })

  // Network status changes
  window.addEventListener('offline', () => {
    if (window.$message) {
      window.$message.warning('İnternet bağlantısı kesildi')
    }
  })

  window.addEventListener('online', () => {
    if (window.$message) {
      window.$message.success('İnternet bağlantısı yeniden sağlandı')
    }
    // Flush any queued errors
    flushQueue()
  })

  // Flush on page unload
  window.addEventListener('beforeunload', flushQueue)

  if (isDev) {
    console.log('%c[ErrorTracking] Initialized', 'color: #22c55e')
  }
}

export default {
  init: initErrorTracking,
  track: trackError,
  trackApi: trackApiError,
  trackNetwork: trackNetworkError,
  trackAuth: trackAuthError,
  trackUI: trackUIError,
  ErrorCategory,
  ErrorSeverity
}
