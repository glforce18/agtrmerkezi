<template>
  <section class="popular-topics-section">
    <div class="section-header">
      <div class="section-title">
        <span class="title-icon">
          <TrendingUpIcon class="w-6 h-6" />
        </span>
        <h2>Popüler Konular</h2>
        <span class="badge-count">{{ topics.length }}</span>
      </div>
      <router-link to="/forum" class="view-all-link">
        Tümünü Gör
        <ChevronRightIcon class="w-4 h-4" />
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="topics-grid">
      <div v-for="i in 6" :key="i" class="topic-card-skeleton">
        <div class="skeleton skeleton-avatar"></div>
        <div class="skeleton-content">
          <div class="skeleton skeleton-text medium"></div>
          <div class="skeleton skeleton-text short"></div>
          <div class="skeleton-meta">
            <div class="skeleton skeleton-badge"></div>
            <div class="skeleton skeleton-badge"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Topics Grid -->
    <div v-else class="topics-grid stagger-children" :class="{ visible: !loading }">
      <article
        v-for="topic in topics"
        :key="topic.id"
        class="topic-card card-enhanced"
        @click="goToTopic(topic)"
      >
        <!-- Hot Badge -->
        <div v-if="topic.isHot" class="badge-hot">
          <FlameIcon class="w-3 h-3" />
          HOT
        </div>

        <!-- Author Avatar -->
        <div class="topic-avatar">
          <img
            :src="getAvatarUrl(topic.author?.avatar)"
            :alt="topic.author?.username"
            class="avatar-img"
          />
          <span v-if="topic.author?.isOnline" class="online-dot"></span>
        </div>

        <!-- Topic Content -->
        <div class="topic-content">
          <h3 class="topic-title">{{ topic.title }}</h3>
          <p class="topic-preview">{{ getPreview(topic.content) }}</p>

          <!-- Meta Info -->
          <div class="topic-meta">
            <span class="author-name">{{ topic.author?.username || 'Anonim' }}</span>
            <span class="meta-dot">·</span>
            <span class="category-badge" :style="getCategoryStyle(topic.category)">
              {{ topic.category?.name }}
            </span>
          </div>
        </div>

        <!-- Stats -->
        <div class="topic-stats">
          <div class="stat-item">
            <EyeIcon class="w-4 h-4" />
            <span>{{ formatNumber(topic.views) }}</span>
          </div>
          <div class="stat-item">
            <MessageSquareIcon class="w-4 h-4" />
            <span>{{ topic.replyCount || 0 }}</span>
          </div>
          <div class="stat-item">
            <HeartIcon class="w-4 h-4" />
            <span>{{ topic.likes || 0 }}</span>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <button class="quick-action-btn" title="Beğen" @click.stop="likeTopic(topic)">
            <HeartIcon class="w-4 h-4" />
          </button>
          <button class="quick-action-btn" title="Kaydet" @click.stop="bookmarkTopic(topic)">
            <BookmarkIcon class="w-4 h-4" />
          </button>
          <button class="quick-action-btn" title="Paylaş" @click.stop="shareTopic(topic)">
            <ShareIcon class="w-4 h-4" />
          </button>
        </div>
      </article>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && topics.length === 0" class="empty-state">
      <MessageSquareIcon class="w-12 h-12" />
      <p>Henüz konu yok</p>
      <router-link to="/forum" class="btn-primary">Forum'a Git</router-link>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  TrendingUpIcon,
  ChevronRightIcon,
  EyeIcon,
  MessageSquareIcon,
  HeartIcon,
  BookmarkIcon,
  ShareIcon,
  FlameIcon
} from 'lucide-vue-next'
import api from '@/services/api'

const router = useRouter()
const topics = ref([])
const loading = ref(true)

const fetchPopularTopics = async () => {
  try {
    loading.value = true
    const response = await api.get('/forum/topics', {
      params: { sort: 'popular', limit: 6 }
    })
    // Güvenli response kontrolü
    if (response?.data?.success) {
      topics.value = response.data.topics || []
    } else if (response?.data?.topics) {
      // success alanı olmadan direkt topics
      topics.value = response.data.topics
    }
  } catch (error) {
    // Sessiz hata - skeleton yerine boş göster
    console.debug('Popular topics not available:', error?.message || error)
    topics.value = []
  } finally {
    loading.value = false
  }
}

const getAvatarUrl = (avatar) => {
  if (!avatar) return '/default-avatar.png'
  if (avatar.startsWith('http')) return avatar
  return avatar.startsWith('/') ? avatar : `/static/images/avatars/${avatar}`
}

const getPreview = (content) => {
  if (!content) return ''
  const text = content.replace(/<[^>]*>/g, '').replace(/\n/g, ' ')
  return text.length > 80 ? text.slice(0, 80) + '...' : text
}

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const getCategoryStyle = (category) => {
  const colors = {
    'duyurular': '#f97316',
    'genel-sohbet': '#3b82f6',
    'sunucu-destek': '#22c55e',
    'teknik-yardim': '#8b5cf6',
    'default': '#64748b'
  }
  const color = colors[category?.slug] || colors.default
  return {
    background: `${color}20`,
    color: color,
    borderColor: `${color}40`
  }
}

const goToTopic = (topic) => {
  router.push(`/forum/topic/${topic.id}`)
}

const likeTopic = (topic) => {
  // Implement like functionality
}

const bookmarkTopic = (topic) => {
  // Implement bookmark functionality
}

const shareTopic = (topic) => {
  if (navigator.share) {
    navigator.share({
      title: topic.title,
      url: `${window.location.origin}/forum/topic/${topic.id}`
    })
  } else {
    navigator.clipboard.writeText(`${window.location.origin}/forum/topic/${topic.id}`)
  }
}

onMounted(() => {
  fetchPopularTopics()
})
</script>

<style scoped>
.popular-topics-section {
  margin-bottom: 48px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
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
  background: linear-gradient(135deg, #f97316, #ea580c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
}

.section-title h2 {
  font-size: 24px;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

.badge-count {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.view-all-link {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease;
}

.view-all-link:hover {
  color: #f97316;
}

/* Topics Grid */
.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

/* Topic Card */
.topic-card {
  position: relative;
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  cursor: pointer;
  overflow: hidden;
}

.topic-card:hover {
  background: rgba(255, 255, 255, 0.04);
}

.badge-hot {
  position: absolute;
  top: 12px;
  right: 12px;
}

/* Avatar */
.topic-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-img {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.online-dot {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #22c55e;
  border: 2px solid #0f172a;
  border-radius: 50%;
}

/* Content */
.topic-content {
  flex: 1;
  min-width: 0;
}

.topic-title {
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.topic-preview {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.author-name {
  color: #94a3b8;
  font-weight: 500;
}

.meta-dot {
  color: #475569;
}

.category-badge {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid;
}

/* Stats */
.topic-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 16px;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 13px;
}

.stat-item svg {
  width: 14px;
  height: 14px;
}

/* Skeleton */
.topic-card-skeleton {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-meta {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #64748b;
  text-align: center;
}

.empty-state svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin-bottom: 20px;
}

.btn-primary {
  padding: 10px 24px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  border-radius: 10px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
}

/* Mobile */
@media (max-width: 768px) {
  .topics-grid {
    grid-template-columns: 1fr;
  }

  .topic-card {
    flex-direction: column;
  }

  .topic-stats {
    flex-direction: row;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-left: 0;
    padding-top: 12px;
    margin-top: 12px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
