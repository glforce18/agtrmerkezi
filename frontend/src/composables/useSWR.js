/**
 * AGTR Merkezi - SWR (Stale-While-Revalidate) Pattern
 * Cache-first data fetching with background revalidation
 */

import { ref, readonly, watch, onMounted, onUnmounted } from 'vue'

// In-memory cache
const cache = new Map()
const cacheTimestamps = new Map()

// Default config
const DEFAULT_CONFIG = {
  ttl: 5 * 60 * 1000, // 5 minutes
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  dedupingInterval: 2000, // 2 seconds
  retryCount: 3,
  retryDelay: 1000
}

// Deduplication: track ongoing requests
const ongoingRequests = new Map()

/**
 * SWR Composable
 * @param {string|Function} key - Cache key or function returning key
 * @param {Function} fetcher - Async function to fetch data
 * @param {Object} options - Configuration options
 */
export function useSWR(key, fetcher, options = {}) {
  const config = { ...DEFAULT_CONFIG, ...options }

  const data = ref(null)
  const error = ref(null)
  const isLoading = ref(false)
  const isValidating = ref(false)

  // Get cache key
  const getCacheKey = () => {
    return typeof key === 'function' ? key() : key
  }

  // Check if cache is fresh
  const isCacheFresh = (cacheKey) => {
    const timestamp = cacheTimestamps.get(cacheKey)
    if (!timestamp) return false
    return Date.now() - timestamp < config.ttl
  }

  // Fetch with retry logic
  const fetchWithRetry = async (retries = config.retryCount) => {
    try {
      return await fetcher()
    } catch (err) {
      if (retries > 0) {
        await new Promise(r => setTimeout(r, config.retryDelay))
        return fetchWithRetry(retries - 1)
      }
      throw err
    }
  }

  // Main revalidate function
  const revalidate = async () => {
    const cacheKey = getCacheKey()
    if (!cacheKey) return

    // Deduplication: return existing request if in progress
    if (ongoingRequests.has(cacheKey)) {
      return ongoingRequests.get(cacheKey)
    }

    isValidating.value = true

    const request = (async () => {
      try {
        const freshData = await fetchWithRetry()

        // Update cache
        cache.set(cacheKey, freshData)
        cacheTimestamps.set(cacheKey, Date.now())

        // Update reactive data
        data.value = freshData
        error.value = null

        return freshData
      } catch (err) {
        error.value = err
        throw err
      } finally {
        isValidating.value = false
        ongoingRequests.delete(cacheKey)
      }
    })()

    ongoingRequests.set(cacheKey, request)
    return request
  }

  // Initial load
  const load = async () => {
    const cacheKey = getCacheKey()
    if (!cacheKey) return

    // Check cache first
    const cachedData = cache.get(cacheKey)
    if (cachedData !== undefined) {
      data.value = cachedData

      // If cache is fresh, don't revalidate
      if (isCacheFresh(cacheKey)) {
        return
      }
    }

    // Show loading only if no cached data
    if (!cachedData) {
      isLoading.value = true
    }

    try {
      await revalidate()
    } finally {
      isLoading.value = false
    }
  }

  // Mutate cache manually
  const mutate = (newData, shouldRevalidate = true) => {
    const cacheKey = getCacheKey()
    if (!cacheKey) return

    if (typeof newData === 'function') {
      const currentData = cache.get(cacheKey)
      newData = newData(currentData)
    }

    // Update cache and reactive data
    cache.set(cacheKey, newData)
    cacheTimestamps.set(cacheKey, Date.now())
    data.value = newData

    // Optionally revalidate
    if (shouldRevalidate) {
      revalidate()
    }
  }

  // Event handlers for revalidation
  const handleFocus = () => {
    if (config.revalidateOnFocus && document.visibilityState === 'visible') {
      revalidate()
    }
  }

  const handleOnline = () => {
    if (config.revalidateOnReconnect) {
      revalidate()
    }
  }

  // Setup
  onMounted(() => {
    load()

    if (config.revalidateOnFocus) {
      document.addEventListener('visibilitychange', handleFocus)
    }
    if (config.revalidateOnReconnect) {
      window.addEventListener('online', handleOnline)
    }
  })

  // Cleanup
  onUnmounted(() => {
    document.removeEventListener('visibilitychange', handleFocus)
    window.removeEventListener('online', handleOnline)
  })

  // Watch key changes
  watch(getCacheKey, () => {
    load()
  })

  return {
    data: readonly(data),
    error: readonly(error),
    isLoading: readonly(isLoading),
    isValidating: readonly(isValidating),
    revalidate,
    mutate
  }
}

/**
 * Optimistic mutation helper
 */
export function useOptimistic(swrResult, updateFn) {
  const { data, mutate, revalidate } = swrResult

  const optimisticUpdate = async (newValue, asyncFn) => {
    // Store original data for rollback
    const originalData = data.value

    try {
      // Optimistically update UI
      mutate(updateFn(data.value, newValue), false)

      // Perform actual update
      await asyncFn()

      // Revalidate to ensure consistency
      await revalidate()
    } catch (error) {
      // Rollback on error
      mutate(originalData, false)
      throw error
    }
  }

  return { optimisticUpdate }
}

/**
 * Clear cache utilities
 */
export function clearCache(key) {
  if (key) {
    cache.delete(key)
    cacheTimestamps.delete(key)
  } else {
    cache.clear()
    cacheTimestamps.clear()
  }
}

export function prefetch(key, fetcher) {
  return fetcher().then(data => {
    cache.set(key, data)
    cacheTimestamps.set(key, Date.now())
    return data
  })
}

export default useSWR
