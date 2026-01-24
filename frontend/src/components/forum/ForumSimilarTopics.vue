<template>
  <n-collapse-transition :show="topics.length > 0">
    <n-card size="small" class="similar-topics-card">
      <template #header>
        <n-icon><LightbulbOutlined /></n-icon>
        <span>Benzer Konular</span>
      </template>
      <template #header-extra>
        <n-button text size="small" @click="emit('dismiss')">
          Gizle
        </n-button>
      </template>

      <div class="similar-list">
        <div
          v-for="topic in topics"
          :key="topic.id"
          class="similar-item"
          @click="goToTopic(topic.id)"
        >
          <div class="topic-title">
            <n-icon v-if="topic.is_solved" color="#18a058" size="14">
              <CheckCircle />
            </n-icon>
            {{ topic.title }}
          </div>
          <div class="topic-meta">
            <span>{{ topic.reply_count }} yanit</span>
            <span>{{ topic.author_username }}</span>
          </div>
        </div>
      </div>

      <div class="similar-hint">
        Sorunuz zaten cevaplanmis olabilir!
      </div>
    </n-card>
  </n-collapse-transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NCollapseTransition, NButton, NIcon } from 'naive-ui'
import { LightbulbIcon, CheckCircleIcon } from 'lucide-vue-next'
import { searchApi } from '@/services/forumAdvanced.js'

const LightbulbOutlined = LightbulbIcon
const CheckCircle = CheckCircleIcon
import { useDebounceFn } from '@vueuse/core'

const router = useRouter()

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  content: {
    type: String,
    default: ''
  },
  minLength: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['dismiss', 'topic-click'])

// State
const topics = ref([])
const loading = ref(false)

// Search for similar topics with debounce
const findSimilar = useDebounceFn(async () => {
  const searchText = (props.title + ' ' + props.content).trim()
  if (searchText.length < props.minLength) {
    topics.value = []
    return
  }

  loading.value = true
  try {
    const { data } = await searchApi.findSimilar(props.title, props.content)
    if (data.success) {
      topics.value = data.similar_topics || []
    }
  } catch (err) {
    topics.value = []
  } finally {
    loading.value = false
  }
}, 1000) // 1 second debounce

// Navigation
const goToTopic = (topicId) => {
  emit('topic-click', topicId)
  router.push(`/forum/topic/${topicId}`)
}

// Watch for changes
watch([() => props.title, () => props.content], () => {
  findSimilar()
})
</script>

<style scoped>
.similar-topics-card {
  margin-bottom: 16px;
  border-color: var(--n-info-color);
}

.similar-topics-card :deep(.n-card-header) {
  padding: 12px 16px;
}

.similar-topics-card :deep(.n-card-header__main) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--n-info-color);
}

.similar-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.similar-item {
  padding: 8px 12px;
  border-radius: 6px;
  background: var(--n-color);
  cursor: pointer;
  transition: all 0.2s;
}

.similar-item:hover {
  background: var(--n-color-hover);
}

.topic-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.topic-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--n-text-color-3);
}

.similar-hint {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--n-border-color);
  font-size: 12px;
  color: var(--n-text-color-3);
  text-align: center;
}
</style>
