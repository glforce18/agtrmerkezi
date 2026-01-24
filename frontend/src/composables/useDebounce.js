/**
 * AGTR Merkezi - Debounce & Throttle Composables
 * Real-time validation ve sik tetiklenen islemler icin performans optimizasyonu
 */

import { ref, watch, onUnmounted } from 'vue'

/**
 * Debounce a reactive value
 * @param {Ref} value - Reactive value to debounce
 * @param {number} delay - Delay in milliseconds (default: 300)
 * @returns {Ref} - Debounced value
 */
export function useDebouncedRef(value, delay = 300) {
  const debouncedValue = ref(value.value)
  let timeoutId = null

  watch(value, (newValue) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    timeoutId = setTimeout(() => {
      debouncedValue.value = newValue
    }, delay)
  })

  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
  })

  return debouncedValue
}

/**
 * Create a debounced function
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in milliseconds (default: 300)
 * @param {Object} options - Options
 * @param {boolean} options.leading - Execute on leading edge (default: false)
 * @param {boolean} options.trailing - Execute on trailing edge (default: true)
 * @returns {Object} - { debouncedFn, cancel, flush, pending }
 */
export function useDebounce(fn, delay = 300, options = {}) {
  const { leading = false, trailing = true } = options

  let timeoutId = null
  let lastArgs = null
  let lastThis = null
  const pending = ref(false)

  const invoke = () => {
    if (lastArgs) {
      fn.apply(lastThis, lastArgs)
      lastArgs = null
      lastThis = null
    }
  }

  const debouncedFn = function (...args) {
    lastArgs = args
    lastThis = this
    pending.value = true

    const shouldCallNow = leading && !timeoutId

    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      timeoutId = null
      pending.value = false
      if (trailing && lastArgs) {
        invoke()
      }
    }, delay)

    if (shouldCallNow) {
      invoke()
    }
  }

  const cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
      pending.value = false
    }
    lastArgs = null
    lastThis = null
  }

  const flush = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
      pending.value = false
      invoke()
    }
  }

  onUnmounted(cancel)

  return {
    debouncedFn,
    cancel,
    flush,
    pending
  }
}

/**
 * Throttle a function - limits execution to once per interval
 * @param {Function} fn - Function to throttle
 * @param {number} interval - Minimum interval between executions in ms (default: 100)
 * @param {Object} options - Options
 * @param {boolean} options.leading - Execute on leading edge (default: true)
 * @param {boolean} options.trailing - Execute on trailing edge (default: true)
 * @returns {Object} - { throttledFn, cancel }
 */
export function useThrottle(fn, interval = 100, options = {}) {
  const { leading = true, trailing = true } = options

  let lastTime = 0
  let timeoutId = null
  let lastArgs = null
  let lastThis = null

  const invoke = () => {
    lastTime = Date.now()
    fn.apply(lastThis, lastArgs)
    lastArgs = null
    lastThis = null
  }

  const throttledFn = function (...args) {
    const now = Date.now()
    const remaining = interval - (now - lastTime)

    lastArgs = args
    lastThis = this

    if (remaining <= 0 || remaining > interval) {
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      if (leading) {
        invoke()
      }
    } else if (!timeoutId && trailing) {
      timeoutId = setTimeout(() => {
        timeoutId = null
        invoke()
      }, remaining)
    }
  }

  const cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
    lastTime = 0
    lastArgs = null
    lastThis = null
  }

  onUnmounted(cancel)

  return {
    throttledFn,
    cancel
  }
}

/**
 * Debounced validation for form inputs
 * @param {Function} validateFn - Async validation function
 * @param {number} delay - Debounce delay (default: 500)
 * @returns {Object} - { validate, validating, error, cancel }
 */
export function useDebouncedValidation(validateFn, delay = 500) {
  const validating = ref(false)
  const error = ref(null)

  const { debouncedFn, cancel, pending } = useDebounce(async (value) => {
    validating.value = true
    error.value = null
    try {
      const result = await validateFn(value)
      error.value = result
    } catch (e) {
      error.value = e.message || 'Doğrulama hatasi'
    } finally {
      validating.value = false
    }
  }, delay)

  const validate = (value) => {
    validating.value = pending.value
    debouncedFn(value)
  }

  return {
    validate,
    validating,
    error,
    cancel
  }
}

/**
 * Simple debounce function (non-reactive, for event handlers)
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} - Debounced function
 */
export function debounce(fn, delay = 300) {
  let timeoutId = null
  return function (...args) {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    timeoutId = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * Simple throttle function (non-reactive, for event handlers)
 * @param {Function} fn - Function to throttle
 * @param {number} interval - Minimum interval between executions
 * @returns {Function} - Throttled function
 */
export function throttle(fn, interval = 100) {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}
