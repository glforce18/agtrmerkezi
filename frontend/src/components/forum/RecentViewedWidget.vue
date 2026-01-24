<template>
  <div class="recent-viewed-widget" v-if="recentTopics.length > 0">
    <div class="recent-viewed-title">
      <ClockIcon class="w-4 h-4" />
      Son Göruntulenenler
    </div>
    <div class="recent-viewed-list">
      <div
        v-for="topic in recentTopics"
        :key="topic.id"
        class="recent-viewed-item"
        @click="goToTopic(topic.id)"
      >
        <MessageSquareIcon class="w-3 h-3" style="flex-shrink: 0; opacity: 0.5;" />
        <span>{{ topic.title }}</span>
        <span class="recent-viewed-time">{{ topic.time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ClockIcon, MessageSquareIcon } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const recentTopics = ref([])

const STORAGE_KEY = 'forum_recent_viewed'
const MAX_ITEMS = 5

// Load from localStorage
const loadRecent = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      recentTopics.value = JSON.parse(stored)
    }
  } catch (e) {
    console.error('Failed to load recent topics:', e)
  }
}

// Add topic to recent
const addToRecent = (topic) => {
  // Remove if already exists
  recentTopics.value = recentTopics.value.filter(t => t.id !== topic.id)

  // Add to beginning
  recentTopics.value.unshift({
    ...topic,
    time: 'Az once'
  })

  // Keep only MAX_ITEMS
  recentTopics.value = recentTopics.value.slice(0, MAX_ITEMS)

  // Save to localStorage
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(recentTopics.value))
  } catch (e) {
    console.error('Failed to save recent topics:', e)
  }
}

const goToTopic = (id) => {
  router.push(`/forum/topic/${id}`)
}

// Expose addToRecent for parent components
defineExpose({ addToRecent })

onMounted(() => {
  loadRecent()
})
</script>

<style scoped>
.recent-viewed-widget {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
}

.recent-viewed-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #a1a1aa);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.recent-viewed-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-viewed-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-primary, #fff);
  cursor: pointer;
  transition: all 0.2s ease;
}

.recent-viewed-item:hover {
  background: rgba(249, 115, 22, 0.1);
}

.recent-viewed-item span {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-viewed-time {
  font-size: 10px !important;
  color: var(--text-secondary, #a1a1aa) !important;
  flex: 0 0 auto !important;
}
</style>
