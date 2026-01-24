<template>
  <div class="pinned-topics-section" v-if="topics.length > 0">
    <div class="pinned-topics-header">
      <div class="pinned-topics-title">
        <PinIcon class="w-3 h-3" />
        Sabitlenmiş Konular
      </div>
      <span
        v-if="topics.length > maxShow"
        class="pinned-see-all"
        @click="showAll = !showAll"
      >
        {{ showAll ? 'Daralt' : `Tümunu gör (${topics.length})` }}
      </span>
    </div>
    <div class="pinned-topics-list">
      <div
        v-for="topic in displayedTopics"
        :key="topic.id"
        class="pinned-topic-item"
        @click="goToTopic(topic.id)"
      >
        <PinIcon class="w-3 h-3" style="color: #f97316; flex-shrink: 0;" />
        <span class="pinned-topic-title">{{ topic.title }}</span>
        <div class="pinned-topic-stats">
          <span><MessageSquareIcon class="w-3 h-3" /> {{ topic.replies || 0 }}</span>
          <span><EyeIcon class="w-3 h-3" /> {{ formatNumber(topic.views || 0) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { PinIcon, MessageSquareIcon, EyeIcon } from 'lucide-vue-next'

const props = defineProps({
  topics: {
    type: Array,
    default: () => []
  },
  maxShow: {
    type: Number,
    default: 3
  }
})

const router = useRouter()
const showAll = ref(false)

const displayedTopics = computed(() => {
  if (showAll.value) return props.topics
  return props.topics.slice(0, props.maxShow)
})

const goToTopic = (id) => {
  router.push(`/forum/topic/${id}`)
}

const formatNumber = (num) => {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num
}
</script>

<style scoped>
.pinned-topics-section {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.05), rgba(139, 92, 246, 0.03));
  border: 1px solid rgba(249, 115, 22, 0.15);
  border-radius: 10px;
  padding: 8px;
  margin-bottom: 10px;
}

.pinned-topics-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  margin-bottom: 4px;
}

.pinned-topics-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #f97316;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.pinned-see-all {
  font-size: 11px;
  color: var(--text-secondary, #a1a1aa);
  cursor: pointer;
  transition: color 0.2s ease;
}

.pinned-see-all:hover {
  color: #f97316;
}

.pinned-topics-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pinned-topic-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.pinned-topic-item:hover {
  background: rgba(249, 115, 22, 0.1);
}

.pinned-topic-title {
  flex: 1;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary, #fff);
}

.pinned-topic-stats {
  display: flex;
  gap: 8px;
  font-size: 10px;
  color: var(--text-secondary, #a1a1aa);
}

.pinned-topic-stats span {
  display: flex;
  align-items: center;
  gap: 3px;
}
</style>
