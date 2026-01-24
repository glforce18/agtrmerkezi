<template>
  <div class="infinite-scroll-container" ref="containerRef">
    <!-- Content Slot -->
    <slot :items="items" :loading="loading" :error="error"></slot>

    <!-- Loading Indicator -->
    <div ref="sentinelRef" class="scroll-sentinel">
      <n-spin v-if="loading && hasMore" size="small">
        <template #description>Yukleniyor...</template>
      </n-spin>

      <div v-else-if="!hasMore && items.length > 0" class="end-message">
        {{ endMessage }}
      </div>

      <div v-else-if="error" class="error-message">
        <n-button size="small" @click="retry">Tekrar Dene</n-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { NSpin, NButton } from 'naive-ui'

const props = defineProps({
  loadMore: {
    type: Function,
    required: true
  },
  initialCursor: {
    type: String,
    default: null
  },
  threshold: {
    type: Number,
    default: 200 // pixels from bottom
  },
  endMessage: {
    type: String,
    default: 'Tum icerikler yuklendi'
  },
  resetTrigger: {
    type: [String, Number, Object],
    default: null
  }
})

const emit = defineEmits(['loaded', 'error'])

// State
const items = ref([])
const cursor = ref(props.initialCursor)
const loading = ref(false)
const hasMore = ref(true)
const error = ref(null)

// Refs
const containerRef = ref(null)
const sentinelRef = ref(null)

// Intersection Observer
let observer = null

// Methods
const loadItems = async () => {
  if (loading.value || !hasMore.value) return

  loading.value = true
  error.value = null

  try {
    const result = await props.loadMore(cursor.value)

    if (result.items && result.items.length > 0) {
      items.value = [...items.value, ...result.items]
    }

    cursor.value = result.nextCursor
    hasMore.value = result.hasMore

    emit('loaded', {
      items: items.value,
      newItems: result.items,
      hasMore: hasMore.value
    })
  } catch (err) {
    error.value = err.message || 'Yukleme hatasi'
    emit('error', err)
  } finally {
    loading.value = false
  }
}

const retry = () => {
  loadItems()
}

const reset = () => {
  items.value = []
  cursor.value = props.initialCursor
  hasMore.value = true
  error.value = null
  loadItems()
}

// Setup Intersection Observer
const setupObserver = () => {
  if (observer) {
    observer.disconnect()
  }

  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry.isIntersecting && !loading.value && hasMore.value) {
        loadItems()
      }
    },
    {
      root: null,
      rootMargin: `${props.threshold}px`,
      threshold: 0
    }
  )

  if (sentinelRef.value) {
    observer.observe(sentinelRef.value)
  }
}

// Watch for reset trigger
watch(() => props.resetTrigger, () => {
  reset()
})

// Lifecycle
onMounted(() => {
  setupObserver()
  loadItems()
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

// Expose methods
defineExpose({
  reset,
  retry,
  items,
  loading,
  hasMore
})
</script>

<style scoped>
.infinite-scroll-container {
  min-height: 100px;
}

.scroll-sentinel {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  min-height: 60px;
}

.end-message {
  text-align: center;
  color: var(--n-text-color-3);
  font-size: 14px;
}

.error-message {
  text-align: center;
}
</style>
