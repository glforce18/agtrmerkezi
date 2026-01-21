<template>
  <div
    ref="containerRef"
    class="pull-to-refresh-container"
    @touchstart="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- Pull indicator -->
    <div
      class="pull-indicator"
      :class="{ visible: pullDistance > 0, refreshing: isRefreshing }"
      :style="{ transform: `translateY(${indicatorOffset}px)` }"
    >
      <div class="pull-icon" :style="{ transform: `rotate(${rotation}deg)` }">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 19V5M5 12l7-7 7 7" />
        </svg>
      </div>
      <span class="pull-text">{{ statusText }}</span>
    </div>

    <!-- Content -->
    <div
      class="pull-content"
      :style="{ transform: `translateY(${contentOffset}px)` }"
    >
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['refresh'])

const props = defineProps({
  threshold: {
    type: Number,
    default: 80
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const containerRef = ref(null)
const startY = ref(0)
const pullDistance = ref(0)
const isRefreshing = ref(false)
const isPulling = ref(false)

const indicatorOffset = computed(() => {
  if (isRefreshing.value) return props.threshold
  return Math.min(pullDistance.value, props.threshold * 1.5) - 60
})

const contentOffset = computed(() => {
  if (isRefreshing.value) return props.threshold
  return Math.min(pullDistance.value, props.threshold * 1.5)
})

const rotation = computed(() => {
  if (isRefreshing.value) return 0
  const progress = Math.min(pullDistance.value / props.threshold, 1)
  return progress * 180
})

const statusText = computed(() => {
  if (isRefreshing.value) return 'Yenileniyor...'
  if (pullDistance.value >= props.threshold) return 'Bırakın'
  return 'Yenilemek için çekin'
})

function canPull() {
  if (props.disabled || isRefreshing.value) return false
  // Check if at top of scroll
  const scrollTop = containerRef.value?.scrollTop || window.scrollY
  return scrollTop <= 0
}

function onTouchStart(e) {
  if (!canPull()) return
  startY.value = e.touches[0].clientY
  isPulling.value = true
}

function onTouchMove(e) {
  if (!isPulling.value || !canPull()) return

  const currentY = e.touches[0].clientY
  const diff = currentY - startY.value

  if (diff > 0) {
    // Apply resistance
    pullDistance.value = diff * 0.5
    e.preventDefault()
  }
}

async function onTouchEnd() {
  if (!isPulling.value) return
  isPulling.value = false

  if (pullDistance.value >= props.threshold) {
    isRefreshing.value = true
    pullDistance.value = 0

    try {
      await emit('refresh')
    } finally {
      isRefreshing.value = false
    }
  } else {
    pullDistance.value = 0
  }
}
</script>

<style scoped>
.pull-to-refresh-container {
  position: relative;
  overflow: hidden;
}

.pull-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60px;
  opacity: 0;
  transition: opacity 0.2s;
  color: var(--text-secondary);
}

.pull-indicator.visible {
  opacity: 1;
}

.pull-indicator.refreshing .pull-icon {
  animation: spin 1s linear infinite;
}

.pull-icon {
  transition: transform 0.1s;
}

.pull-text {
  font-size: 12px;
  margin-top: 4px;
}

.pull-content {
  transition: transform 0.2s ease-out;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Only enable on touch devices */
@media (hover: hover) {
  .pull-to-refresh-container {
    touch-action: auto;
  }
  .pull-indicator {
    display: none;
  }
}
</style>
