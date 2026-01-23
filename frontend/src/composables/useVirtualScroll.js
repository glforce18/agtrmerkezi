/**
 * AGTR Merkezi - Virtual Scroll Composable
 * Buyuk listeler icin performans optimizasyonu
 */

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

/**
 * Virtual scrolling hook for large lists
 * @param {Object} options - Configuration options
 * @param {Ref<Array>} options.items - Reactive array of all items
 * @param {number} options.itemHeight - Height of each item in pixels
 * @param {number} options.containerHeight - Height of the scroll container
 * @param {number} options.overscan - Number of extra items to render outside viewport (default: 5)
 */
export function useVirtualScroll(options) {
  const {
    items,
    itemHeight = 80,
    containerHeight = 600,
    overscan = 5
  } = options

  const scrollTop = ref(0)
  const containerRef = ref(null)

  // Calculate visible range
  const visibleRange = computed(() => {
    const itemCount = items.value?.length || 0
    if (itemCount === 0) return { start: 0, end: 0 }

    const visibleCount = Math.ceil(containerHeight / itemHeight)
    const start = Math.max(0, Math.floor(scrollTop.value / itemHeight) - overscan)
    const end = Math.min(itemCount, start + visibleCount + overscan * 2)

    return { start, end }
  })

  // Get visible items
  const visibleItems = computed(() => {
    if (!items.value || items.value.length === 0) return []
    const { start, end } = visibleRange.value
    return items.value.slice(start, end).map((item, index) => ({
      ...item,
      _virtualIndex: start + index
    }))
  })

  // Total height of the virtual container
  const totalHeight = computed(() => {
    return (items.value?.length || 0) * itemHeight
  })

  // Offset for positioning visible items
  const offsetY = computed(() => {
    return visibleRange.value.start * itemHeight
  })

  // Handle scroll events
  const handleScroll = (event) => {
    if (event?.target) {
      scrollTop.value = event.target.scrollTop
    }
  }

  // Throttled scroll handler for better performance
  let scrollTimeout = null
  const throttledScroll = (event) => {
    if (!scrollTimeout) {
      scrollTimeout = requestAnimationFrame(() => {
        handleScroll(event)
        scrollTimeout = null
      })
    }
  }

  // Scroll to specific index
  const scrollToIndex = (index) => {
    if (containerRef.value) {
      const targetScroll = index * itemHeight
      containerRef.value.scrollTop = targetScroll
      scrollTop.value = targetScroll
    }
  }

  // Scroll to top
  const scrollToTop = () => {
    scrollToIndex(0)
  }

  // Scroll to bottom
  const scrollToBottom = () => {
    if (items.value?.length > 0) {
      scrollToIndex(items.value.length - 1)
    }
  }

  // Setup and cleanup
  onMounted(() => {
    if (containerRef.value) {
      containerRef.value.addEventListener('scroll', throttledScroll, { passive: true })
    }
  })

  onUnmounted(() => {
    if (containerRef.value) {
      containerRef.value.removeEventListener('scroll', throttledScroll)
    }
    if (scrollTimeout) {
      cancelAnimationFrame(scrollTimeout)
    }
  })

  // Watch for container ref changes
  watch(containerRef, (newRef, oldRef) => {
    if (oldRef) {
      oldRef.removeEventListener('scroll', throttledScroll)
    }
    if (newRef) {
      newRef.addEventListener('scroll', throttledScroll, { passive: true })
    }
  })

  return {
    containerRef,
    visibleItems,
    totalHeight,
    offsetY,
    scrollToIndex,
    scrollToTop,
    scrollToBottom,
    visibleRange
  }
}

/**
 * Intersection observer based lazy loading for items
 */
export function useLazyLoad(options = {}) {
  const {
    rootMargin = '100px',
    threshold = 0.1
  } = options

  const observerRef = ref(null)
  const loadedItems = ref(new Set())

  const observe = (element, callback) => {
    if (!observerRef.value) {
      observerRef.value = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const itemId = entry.target.dataset.itemId
              if (itemId && !loadedItems.value.has(itemId)) {
                loadedItems.value.add(itemId)
                callback(itemId, entry.target)
              }
            }
          })
        },
        { rootMargin, threshold }
      )
    }
    observerRef.value.observe(element)
  }

  const unobserve = (element) => {
    if (observerRef.value) {
      observerRef.value.unobserve(element)
    }
  }

  const disconnect = () => {
    if (observerRef.value) {
      observerRef.value.disconnect()
      observerRef.value = null
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    observe,
    unobserve,
    disconnect,
    loadedItems
  }
}
