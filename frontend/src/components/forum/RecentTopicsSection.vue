<template>
  <section class="recent-topics-section">
    <div class="section-header">
      <div class="section-title">
        <span class="title-icon">
          <ClockIcon class="w-6 h-6" />
        </span>
        <h2>Son Konular</h2>
      </div>
      <div class="header-actions">
        <button
          v-for="filter in filters"
          :key="filter.value"
          class="filter-btn"
          :class="{ active: activeFilter === filter.value }"
          @click="setFilter(filter.value)"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="topics-list">
      <div v-for="i in 8" :key="i" class="topic-item-skeleton">
        <div class="skeleton skeleton-avatar" style="width: 36px; height: 36px;"></div>
        <div class="skeleton-content">
          <div class="skeleton skeleton-text medium"></div>
          <div class="skeleton skeleton-text short"></div>
        </div>
        <div class="skeleton skeleton-badge" style="width: 40px;"></div>
      </div>
    </div>

    <!-- Topics List -->
    <div v-else class="topics-list stagger-children" :class="{ visible: !loading }">
      <article
        v-for="topic in topics"
        :key="topic.id"
        class="topic-item hover-lift"
        :class="{ unread: topic.isUnread }"
        @click="goToTopic(topic)"
      >
        <!-- Unread Indicator -->
        <div v-if="topic.isUnread" class="unread-dot"></div>

        <!-- Author Avatar -->
        <div class="topic-avatar">
          <img
            :src="getAvatarUrl(topic.author?.avatar)"
            :alt="topic.author?.username"
          />
        </div>

        <!-- Topic Info -->
        <div class="topic-info">
          <div class="topic-title-row">
            <h3 class="topic-title">{{ topic.title }}</h3>
            <span v-if="topic.isPinned" class="pinned-badge">
              <PinIcon class="w-3 h-3" />
            </span>
            <span v-if="topic.isSolved" class="solved-badge">
              <CheckCircleIcon class="w-3 h-3" />
            </span>
          </div>
          <div class="topic-meta">
            <span class="author">{{ topic.author?.username }}</span>
            <span class="separator">in</span>
            <span class="category" :style="getCategoryColor(topic.category)">
              {{ topic.category?.name }}
            </span>
            <span class="time">{{ formatTimeAgo(topic.createdAt) }}</span>
          </div>
        </div>

        <!-- Stats -->
        <div class="topic-stats">
          <div class="stat replies" :class="{ 'has-new': topic.hasNewReplies }">
            <MessageSquareIcon class="w-4 h-4" />
            <span>{{ topic.replyCount || 0 }}</span>
          </div>
        </div>
      </article>
    </div>

    <!-- Load More -->
    <div v-if="!loading && hasMore" class="load-more">
      <button class="load-more-btn" @click="loadMore" :disabled="loadingMore">
        <template v-if="loadingMore">
          <span class="loading-spinner"></span>
          Yükleniyor...
        </template>
        <template v-else>
          Daha Fazla Göster
          <ChevronDownIcon class="w-4 h-4" />
        </template>
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ClockIcon,
  MessageSquareIcon,
  PinIcon,
  CheckCircleIcon,
  ChevronDownIcon
} from 'lucide-vue-next'
import api from '@/services/api'

const router = useRouter()
const topics = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const activeFilter = ref('newest')
const page = ref(1)
const hasMore = ref(true)

const filters = [
  { label: 'En Yeni', value: 'newest' },
  { label: 'En Aktif', value: 'popular' },
  { label: 'Cevapsız', value: 'unanswered' }
]

const fetchTopics = async (reset = false) => {
  try {
    if (reset) {
      loading.value = true
      page.value = 1
      topics.value = []
    } else {
      loadingMore.value = true
    }

    const params = {
      sort: activeFilter.value,
      limit: 8,
      page: page.value
    }

    if (activeFilter.value === 'unanswered') {
      params.sort = 'newest'
      params.has_replies = false
    }

    const response = await api.get('/forum/topics', { params })

    // Güvenli response kontrolü
    if (response?.data?.success) {
      const newTopics = response.data.topics || []
      if (reset) {
        topics.value = newTopics
      } else {
        topics.value = [...topics.value, ...newTopics]
      }
      hasMore.value = newTopics.length === 8
    } else if (response?.data?.topics) {
      // success alanı olmadan direkt topics
      const newTopics = response.data.topics
      if (reset) {
        topics.value = newTopics
      } else {
        topics.value = [...topics.value, ...newTopics]
      }
      hasMore.value = newTopics.length === 8
    }
  } catch (error) {
    // Sessiz hata - skeleton yerine boş göster
    console.debug('Topics not available:', error?.message || error)
    if (reset) {
      topics.value = []
    }
    hasMore.value = false
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const setFilter = (filter) => {
  if (activeFilter.value !== filter) {
    activeFilter.value = filter
    fetchTopics(true)
  }
}

const loadMore = () => {
  page.value++
  fetchTopics(false)
}

const getAvatarUrl = (avatar) => {
  if (!avatar) return '/default-avatar.png'
  if (avatar.startsWith('http')) return avatar
  return avatar.startsWith('/') ? avatar : `/static/images/avatars/${avatar}`
}

const getCategoryColor = (category) => {
  const colors = {
    'duyurular': '#f97316',
    'genel-sohbet': '#3b82f6',
    'sunucu-destek': '#22c55e',
    'teknik-yardim': '#8b5cf6'
  }
  return { color: colors[category?.slug] || '#64748b' }
}

const formatTimeAgo = (date) => {
  if (!date) return ''
  const now = new Date()
  const then = new Date(date)
  const diff = Math.floor((now - then) / 1000)

  if (diff < 60) return 'Az önce'
  if (diff < 3600) return `${Math.floor(diff / 60)} dk önce`
  if (diff < 86400) return `${Math.floor(diff / 3600)} saat önce`
  if (diff < 604800) return `${Math.floor(diff / 86400)} gün önce`
  return then.toLocaleDateString('tr-TR')
}

const goToTopic = (topic) => {
  router.push(`/forum/topic/${topic.id}`)
}

onMounted(() => {
  fetchTopics(true)
})
</script>

<style scoped>
.recent-topics-section {
  margin-bottom: 48px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.section-title h2 {
  font-size: 24px;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

/* Filter Buttons */
.header-actions {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #f8fafc;
}

.filter-btn.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

/* Topics List */
.topics-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  overflow: hidden;
}

/* Topic Item */
.topic-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: transparent;
  cursor: pointer;
  position: relative;
  transition: background 0.2s ease;
}

.topic-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.topic-item:not(:last-child) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.topic-item.unread {
  background: rgba(59, 130, 246, 0.05);
}

/* Unread Dot */
.unread-dot {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Avatar */
.topic-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.08);
}

/* Topic Info */
.topic-info {
  flex: 1;
  min-width: 0;
}

.topic-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.topic-title {
  font-size: 15px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pinned-badge,
.solved-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  flex-shrink: 0;
}

.pinned-badge {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.solved-badge {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

/* Meta */
.topic-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
}

.author {
  color: #94a3b8;
  font-weight: 500;
}

.separator {
  color: #475569;
}

.category {
  font-weight: 500;
}

.time {
  margin-left: auto;
  color: #64748b;
  font-size: 12px;
}

/* Stats */
.topic-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  font-size: 13px;
}

.stat.has-new {
  color: #f97316;
  font-weight: 600;
}

/* Skeleton */
.topic-item-skeleton {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
}

.topic-item-skeleton:not(:last-child) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Load More */
.load-more {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.load-more-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(249, 115, 22, 0.2);
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Mobile */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .filter-btn {
    white-space: nowrap;
  }

  .topic-item {
    padding: 14px 16px;
  }

  .topic-meta .time {
    display: none;
  }

  .topic-avatar img {
    width: 36px;
    height: 36px;
  }
}
</style>
