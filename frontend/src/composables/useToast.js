/**
 * AGTR Merkezi - Enhanced Toast Notifications
 * Action support, progress bar, and stacking
 */

import { ref, readonly, h } from 'vue'

const toasts = ref([])
let toastId = 0

const DEFAULT_DURATION = 5000
const MAX_TOASTS = 5

/**
 * Toast configuration
 */
const defaultConfig = {
  position: 'top-right', // top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
  maxToasts: MAX_TOASTS
}

/**
 * Create a new toast
 */
function createToast(options) {
  const id = ++toastId

  const toast = {
    id,
    type: options.type || 'info', // success, error, warning, info
    title: options.title || null,
    message: options.message || '',
    duration: options.duration ?? DEFAULT_DURATION,
    closable: options.closable ?? true,
    showProgress: options.showProgress ?? true,
    action: options.action || null, // { label: string, onClick: Function }
    icon: options.icon || null,
    createdAt: Date.now()
  }

  // Remove oldest toast if max reached
  if (toasts.value.length >= defaultConfig.maxToasts) {
    toasts.value.shift()
  }

  toasts.value.push(toast)

  // Auto dismiss
  if (toast.duration > 0) {
    setTimeout(() => {
      dismissToast(id)
    }, toast.duration)
  }

  return id
}

/**
 * Dismiss a toast
 */
function dismissToast(id) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

/**
 * Dismiss all toasts
 */
function dismissAll() {
  toasts.value = []
}

/**
 * Shorthand methods
 */
function success(message, options = {}) {
  return createToast({ ...options, type: 'success', message })
}

function error(message, options = {}) {
  return createToast({ ...options, type: 'error', message })
}

function warning(message, options = {}) {
  return createToast({ ...options, type: 'warning', message })
}

function info(message, options = {}) {
  return createToast({ ...options, type: 'info', message })
}

/**
 * Promise-based toast (loading -> success/error)
 */
async function promise(promise, options = {}) {
  const {
    loading = 'Yükleniyor...',
    success = 'Başarılı!',
    error = 'Bir hata oluştu'
  } = options

  const id = createToast({
    type: 'info',
    message: loading,
    duration: 0, // Don't auto-dismiss
    showProgress: false
  })

  try {
    const result = await promise
    dismissToast(id)
    createToast({
      type: 'success',
      message: typeof success === 'function' ? success(result) : success
    })
    return result
  } catch (err) {
    dismissToast(id)
    createToast({
      type: 'error',
      message: typeof error === 'function' ? error(err) : error
    })
    throw err
  }
}

/**
 * Composable
 */
export function useToast() {
  return {
    toasts: readonly(toasts),
    create: createToast,
    dismiss: dismissToast,
    dismissAll,
    success,
    error,
    warning,
    info,
    promise
  }
}

export default useToast
