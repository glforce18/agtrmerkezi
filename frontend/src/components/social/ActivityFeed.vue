<template>
  <div class="activity-feed" :class="{ compact }">
    <!-- Header -->
    <div v-if="showHeader" class="feed-header">
      <h3 class="feed-title">
        <Activity class="w-5 h-5" />
        <span>{{ title }}</span>
        <span v-if="isConnected" class="live-indicator">
          <span class="pulse-dot"></span>
          Canlı
        </span>
      </h3>

      <div class="feed-actions">
        <n-dropdown
          v-if="showFilters"
          :options="filterOptions"
          trigger="click"
          @select="handleFilterSelect"
        >
          <n-button size="tiny" quaternary>
            <template #icon><Filter class="w-4 h-4" /></template>
          </n-button>
        </n-dropdown>

        <n-button
          size="tiny"
          quaternary
          @click="refresh"
          :loading="loading"
        >
          <template #icon><RefreshCw class="w-4 h-4" /></template>
        </n-button>
      </div>
    </div>

    <!-- Content -->
    <div class="feed-content" ref="feedContent">
      <!-- Loading -->
      <div v-if="loading && activities.length === 0" class="loading-state">
        <n-spin size="small" />
        <span>Aktiviteler yükleniyor...</span>
      </div>

      <!-- Empty State -->
      <div v-else-if="displayedActivities.length === 0" class="empty-state">
        <Activity class="w-10 h-10" />
        <p>Henüz aktivite yok</p>
      </div>

      <!-- Activity List -->
      <TransitionGroup v-else name="activity" tag="div" class="activity-list">
        <div
          v-for="activity in displayedActivities"
          :key="activity.id"
          class="activity-item"
          :class="{ highlighted: activity.highlighted }"
          @click="handleActivityClick(activity)"
        >
          <!-- User Avatar (if not compact) -->
          <div v-if="!compact && activity.user" class="activity-avatar">
            <router-link :to="`/profile/${activity.user.id}`">
              <n-avatar :size="36" :src="activity.user.avatar" round>
                {{ activity.user.username?.charAt(0).toUpperCase() }}
              </n-avatar>
            </router-link>
          </div>

          <!-- Activity Icon -->
          <div
            class="activity-icon"
            :style="{ background: getActivityColor(activity.type) + '20', color: getActivityColor(activity.type) }"
          >
            <span>{{ getActivityIcon(activity.type) }}</span>
          </div>

          <!-- Content -->
          <div class="activity-content">
            <p class="activity-message">
              <router-link
                v-if="activity.user"
                :to="`/profile/${activity.user.id}`"
                class="user-link"
              >
                {{ activity.user.username }}
              </router-link>
              <span>{{ getMessageWithoutUser(activity) }}</span>
            </p>
            <span class="activity-time">{{ formatTime(activity.created_at) }}</span>
          </div>

          <!-- Action (if any) -->
          <div v-if="activity.action_url" class="activity-action">
            <ChevronRight class="w-4 h-4" />
          </div>
        </div>
      </TransitionGroup>

      <!-- Load More -->
      <div v-if="!compact && pagination.hasMore && activities.length > 0" class="load-more">
        <n-button
          size="small"
          quaternary
          block
          :loading="loading"
          @click="loadMore"
        >
          Daha Fazla Yükle
        </n-button>
      </div>
    </div>

    <!-- Footer (compact mode) -->
    <div v-if="compact && activities.length > 0" class="feed-footer">
      <router-link to="/activity" class="view-all-link">
        Tümünü Gör
        <ChevronRight class="w-4 h-4" />
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, h } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Activity, Filter, RefreshCw, ChevronRight } from 'lucide-vue-next'
import { NIcon } from 'naive-ui'
import { useActivityStore, ActivityType } from '@/stores/activity'

const props = defineProps({
  title: {
    type: String,
    default: 'Aktivite Akışı'
  },
  compact: {
    type: Boolean,
    default: false
  },
  limit: {
    type: Number,
    default: 10
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  userId: {
    type: [String, Number],
    default: null
  },
  friendsOnly: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const activityStore = useActivityStore()

const {
  activities,
  loading,
  isConnected,
  pagination,
  filteredActivities
} = storeToRefs(activityStore)

const {
  getActivityIcon,
  getActivityColor,
  formatActivityMessage
} = activityStore

const feedContent = ref(null)
const activeFilter = ref(null)

// Filter options
const filterOptions = [
  { label: 'Tümü', key: 'all' },
  { type: 'divider' },
  { label: '👥 Sosyal', key: 'social' },
  { label: '🎮 Oyun', key: 'gaming' },
  { label: '💬 Forum', key: 'forum' },
  { label: '📣 Sistem', key: 'system' }
]

// Computed
const displayedActivities = computed(() => {
  let result = filteredActivities.value

  if (props.compact) {
    result = result.slice(0, props.limit)
  }

  return result
})

// Methods
const getMessageWithoutUser = (activity) => {
  const message = formatActivityMessage(activity)
  const username = activity.user?.username
  if (username && message.startsWith(username)) {
    return message.substring(username.length).trim()
  }
  return message
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (seconds < 30) return 'Şimdi'
  if (minutes < 1) return `${seconds}sn`
  if (minutes < 60) return `${minutes}dk`
  if (hours < 24) return `${hours}s`
  if (days < 7) return `${days}g`

  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

const handleFilterSelect = (key) => {
  activeFilter.value = key

  let types = []

  switch (key) {
    case 'social':
      types = [
        ActivityType.USER_JOINED,
        ActivityType.FRIEND_ADDED,
        ActivityType.CLAN_JOINED,
        ActivityType.CLAN_CREATED
      ]
      break
    case 'gaming':
      types = [
        ActivityType.USER_LEVEL_UP,
        ActivityType.USER_ACHIEVEMENT,
        ActivityType.TOURNAMENT_CREATED,
        ActivityType.TOURNAMENT_WIN,
        ActivityType.MATCH_PLAYED,
        ActivityType.KILLSTREAK,
        ActivityType.SERVER_ONLINE
      ]
      break
    case 'forum':
      types = [
        ActivityType.TOPIC_CREATED,
        ActivityType.POST_CREATED,
        ActivityType.POST_LIKED
      ]
      break
    case 'system':
      types = [
        ActivityType.ANNOUNCEMENT,
        ActivityType.PURCHASE,
        ActivityType.VIP_ACTIVATED
      ]
      break
    default:
      types = []
  }

  activityStore.setFilters({ types })
}

const handleActivityClick = (activity) => {
  if (activity.action_url) {
    router.push(activity.action_url)
  } else if (activity.user?.id) {
    router.push(`/profile/${activity.user.id}`)
  }
}

const refresh = () => {
  activityStore.fetchActivities({ reset: true })
}

const loadMore = () => {
  activityStore.loadMore()
}

// Initialize with filters if provided
watch(() => props.userId, (newUserId) => {
  if (newUserId) {
    activityStore.setFilters({ userId: newUserId })
  }
}, { immediate: true })

watch(() => props.friendsOnly, (newValue) => {
  activityStore.setFilters({ friendsOnly: newValue })
}, { immediate: true })

onMounted(() => {
  if (activities.value.length === 0) {
    activityStore.init()
  }
})
</script>

<style scoped>
.activity-feed {
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.activity-feed.compact {
  max-height: 400px;
}

.feed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.feed-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  color: #22c55e;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.feed-actions {
  display: flex;
  gap: 4px;
}

.feed-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.activity-item:hover {
  background: var(--bg-tertiary);
}

.activity-item.highlighted {
  background: rgba(249, 115, 22, 0.05);
  border-left: 3px solid #f97316;
}

.activity-avatar {
  flex-shrink: 0;
}

.activity-avatar a {
  display: block;
}

.activity-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 16px;
  flex-shrink: 0;
}

.compact .activity-icon {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-message {
  margin: 0 0 2px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.compact .activity-message {
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-link {
  font-weight: 600;
  color: var(--text-primary);
  text-decoration: none;
  margin-right: 4px;
}

.user-link:hover {
  color: #f97316;
}

.activity-time {
  font-size: 11px;
  color: var(--text-tertiary);
}

.activity-action {
  color: var(--text-tertiary);
  opacity: 0;
  transition: opacity 0.2s;
}

.activity-item:hover .activity-action {
  opacity: 1;
}

.load-more {
  padding: 8px;
}

.feed-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.view-all-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #f97316;
  text-decoration: none;
  transition: opacity 0.2s;
}

.view-all-link:hover {
  opacity: 0.8;
}

/* Activity Transitions */
.activity-enter-active {
  animation: slideIn 0.3s ease;
}

.activity-leave-active {
  animation: slideOut 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(20px);
  }
}
</style>
