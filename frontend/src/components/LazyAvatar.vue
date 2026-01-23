<template>
  <div
    ref="containerRef"
    class="lazy-avatar"
    :class="[sizeClass, { 'lazy-avatar--loaded': isLoaded, 'lazy-avatar--round': round }]"
    :style="containerStyle"
  >
    <!-- Placeholder/Skeleton while loading -->
    <div v-if="!isLoaded && !hasError" class="lazy-avatar__placeholder">
      <div class="lazy-avatar__skeleton"></div>
    </div>

    <!-- Fallback initials when image fails or no src -->
    <div
      v-if="(hasError || !src) && fallbackInitials"
      class="lazy-avatar__fallback"
      :style="fallbackStyle"
    >
      {{ initials }}
    </div>

    <!-- Actual image -->
    <img
      v-show="isLoaded && !hasError"
      :src="isIntersecting ? src : ''"
      :alt="alt"
      class="lazy-avatar__image"
      @load="handleLoad"
      @error="handleError"
      loading="lazy"
      decoding="async"
    />

    <!-- Online status indicator -->
    <span v-if="showStatus" :class="['lazy-avatar__status', statusClass]"></span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  src: {
    type: String,
    default: ''
  },
  alt: {
    type: String,
    default: 'Avatar'
  },
  size: {
    type: [Number, String],
    default: 40
  },
  round: {
    type: Boolean,
    default: true
  },
  fallbackInitials: {
    type: String,
    default: ''
  },
  fallbackColor: {
    type: String,
    default: '#f97316'
  },
  showStatus: {
    type: Boolean,
    default: false
  },
  status: {
    type: String,
    default: 'offline',
    validator: (v) => ['online', 'away', 'offline', 'busy'].includes(v)
  },
  // Enable/disable lazy loading
  lazy: {
    type: Boolean,
    default: true
  },
  // Root margin for intersection observer
  rootMargin: {
    type: String,
    default: '100px'
  }
})

const emit = defineEmits(['load', 'error'])

const containerRef = ref(null)
const isLoaded = ref(false)
const hasError = ref(false)
const isIntersecting = ref(!props.lazy) // If not lazy, start loading immediately

let observer = null

// Computed styles
const sizeClass = computed(() => {
  if (typeof props.size === 'string') {
    return `lazy-avatar--${props.size}`
  }
  return ''
})

const containerStyle = computed(() => {
  if (typeof props.size === 'number') {
    return {
      width: `${props.size}px`,
      height: `${props.size}px`
    }
  }
  return {}
})

const fallbackStyle = computed(() => ({
  backgroundColor: props.fallbackColor,
  fontSize: typeof props.size === 'number' ? `${props.size * 0.4}px` : undefined
}))

const statusClass = computed(() => `lazy-avatar__status--${props.status}`)

const initials = computed(() => {
  if (props.fallbackInitials) {
    return props.fallbackInitials.substring(0, 2).toUpperCase()
  }
  if (props.alt) {
    const parts = props.alt.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return props.alt.substring(0, 2).toUpperCase()
  }
  return '??'
})

// Event handlers
const handleLoad = () => {
  isLoaded.value = true
  hasError.value = false
  emit('load')
}

const handleError = () => {
  hasError.value = true
  isLoaded.value = false
  emit('error')
}

// Setup intersection observer for lazy loading
const setupObserver = () => {
  if (!props.lazy || !('IntersectionObserver' in window)) {
    isIntersecting.value = true
    return
  }

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          isIntersecting.value = true
          // Disconnect after first intersection
          observer?.disconnect()
        }
      })
    },
    {
      rootMargin: props.rootMargin,
      threshold: 0.01
    }
  )

  if (containerRef.value) {
    observer.observe(containerRef.value)
  }
}

// Watch for src changes to reset state
watch(() => props.src, () => {
  isLoaded.value = false
  hasError.value = false
})

onMounted(() => {
  setupObserver()
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.lazy-avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--forum-bg-hover, #2a2a3e);
  flex-shrink: 0;
}

.lazy-avatar--round {
  border-radius: 50%;
}

/* Size variants */
.lazy-avatar--sm {
  width: 24px;
  height: 24px;
}

.lazy-avatar--md {
  width: 40px;
  height: 40px;
}

.lazy-avatar--lg {
  width: 64px;
  height: 64px;
}

.lazy-avatar--xl {
  width: 96px;
  height: 96px;
}

/* Placeholder skeleton */
.lazy-avatar__placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lazy-avatar__skeleton {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--forum-bg-hover, #2a2a3e) 25%,
    var(--forum-bg-card, #1e1e2e) 50%,
    var(--forum-bg-hover, #2a2a3e) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Fallback initials */
.lazy-avatar__fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  text-transform: uppercase;
  user-select: none;
}

/* Image */
.lazy-avatar__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.lazy-avatar--loaded .lazy-avatar__image {
  opacity: 1;
}

/* Status indicator */
.lazy-avatar__status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 25%;
  height: 25%;
  min-width: 8px;
  min-height: 8px;
  max-width: 14px;
  max-height: 14px;
  border-radius: 50%;
  border: 2px solid var(--forum-bg-card, #1e1e2e);
}

.lazy-avatar__status--online {
  background: #22c55e;
}

.lazy-avatar__status--away {
  background: #eab308;
}

.lazy-avatar__status--busy {
  background: #ef4444;
}

.lazy-avatar__status--offline {
  background: #6b7280;
}
</style>
