/**
 * Debounce composable to prevent rapid function calls
 */
import { ref } from 'vue'

export function useDebounce() {
  const timeoutId = ref(null)

  const debounce = (func, delay = 300) => {
    return (...args) => {
      if (timeoutId.value) {
        clearTimeout(timeoutId.value)
      }
      timeoutId.value = setTimeout(() => {
        func(...args)
      }, delay)
    }
  }

  return { debounce }
}

/**
 * Throttle function - allows only one call per interval
 */
export function useThrottle() {
  const isThrottled = ref(false)

  const throttle = (func, delay = 300) => {
    return (...args) => {
      if (isThrottled.value) return

      isThrottled.value = true
      func(...args)

      setTimeout(() => {
        isThrottled.value = false
      }, delay)
    }
  }

  return { throttle, isThrottled }
}
