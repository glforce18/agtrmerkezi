<template>
  <div class="activity-feed-container">
    <div class="activity-feed-header">
      <div class="activity-feed-title">
        <ActivityIcon class="w-4 h-4" />
        <span>Canli Aktivite</span>
        <span class="activity-live-badge">
          <span class="activity-live-dot"></span>
          CANLI
        </span>
      </div>
      <button
        class="activity-toggle-btn"
        :class="{ active: isPaused }"
        @click="isPaused = !isPaused"
        :title="isPaused ? 'Devam Et' : 'Duraklat'"
      >
        <component :is="isPaused ? PlayIcon : PauseIcon" class="w-4 h-4" />
      </button>
    </div>

    <div class="activity-feed-list" ref="feedList">
      <TransitionGroup name="activity-item">
        <div
          v-for="(item, index) in visibleActivities"
          :key="item.id"
          class="activity-item"
          :class="[`activity-${item.type}`, { 'activity-new': item.isNew }]"
          :style="{ animationDelay: `${index * 50}ms` }"
        >
          <!-- Avatar -->
          <div class="activity-avatar">
            <img
              v-if="item.user?.avatar"
              :src="item.user.avatar"
              :alt="item.user.username"
              class="activity-avatar-img"
            />
            <div v-else class="activity-avatar-fallback">
              {{ getInitials(item.user?.username) }}
            </div>
            <div class="activity-type-badge" :class="`badge-${item.type}`">
              <component :is="getTypeIcon(item.type)" class="w-3 h-3" />
            </div>
          </div>

          <!-- Content -->
          <div class="activity-content">
            <div class="activity-text">
              <router-link
                v-if="item.user"
                :to="`/profile/${item.user.id}`"
                class="activity-username"
              >
                {{ item.user.username }}
              </router-link>
              <span class="activity-action">{{ item.action }}</span>
              <router-link
                v-if="item.target"
                :to="item.target.url"
                class="activity-target"
              >
                {{ item.target.title }}
              </router-link>
            </div>
            <div class="activity-meta">
              <ClockIcon class="w-3 h-3" />
              {{ formatTime(item.timestamp) }}
            </div>
          </div>

          <!-- Value (for achievements, levels, etc.) -->
          <div v-if="item.value" class="activity-value" :class="`value-${item.type}`">
            <component :is="getValueIcon(item.type)" class="w-4 h-4" />
            <span>{{ item.value }}</span>
          </div>
        </div>
      </TransitionGroup>

      <!-- Empty State -->
      <div v-if="activities.length === 0" class="activity-empty">
        <RadioIcon class="w-8 h-8" />
        <span>Henuz aktivite yok</span>
      </div>
    </div>

    <!-- View All Link -->
    <router-link to="/activity" class="activity-view-all">
      Tum Aktiviteleri Gor
      <ArrowRightIcon class="w-4 h-4" />
    </router-link>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  ActivityIcon,
  PlayIcon,
  PauseIcon,
  ClockIcon,
  ArrowRightIcon,
  RadioIcon,
  TrophyIcon,
  MessageSquareIcon,
  HeartIcon,
  StarIcon,
  ServerIcon,
  AwardIcon,
  UserPlusIcon,
  ZapIcon,
  ShieldIcon
} from 'lucide-vue-next'

const props = defineProps({
  maxItems: {
    type: Number,
    default: 10
  },
  autoRefresh: {
    type: Boolean,
    default: true
  },
  refreshInterval: {
    type: Number,
    default: 30000 // 30 seconds
  }
})

// State
const activities = ref([])
const isPaused = ref(false)
const feedList = ref(null)
let refreshTimer = null
let wsConnection = null

// Computed
const visibleActivities = computed(() => {
  return activities.value.slice(0, props.maxItems)
})

// Methods
const getInitials = (name) => {
  if (!name) return '?'
  return name.substring(0, 2).toUpperCase()
}

const getTypeIcon = (type) => {
  const icons = {
    topic: MessageSquareIcon,
    reply: MessageSquareIcon,
    like: HeartIcon,
    trophy: TrophyIcon,
    badge: AwardIcon,
    level: StarIcon,
    server: ServerIcon,
    follow: UserPlusIcon,
    streak: ZapIcon,
    admin: ShieldIcon
  }
  return icons[type] || ActivityIcon
}

const getValueIcon = (type) => {
  const icons = {
    level: StarIcon,
    trophy: TrophyIcon,
    badge: AwardIcon,
    streak: ZapIcon
  }
  return icons[type] || StarIcon
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)

  if (diff < 10) return 'simdi'
  if (diff < 60) return `${diff}sn once`
  if (diff < 3600) return `${Math.floor(diff / 60)}dk once`
  if (diff < 86400) return `${Math.floor(diff / 3600)}sa once`
  return date.toLocaleDateString('tr-TR')
}

const addActivity = (activity) => {
  activity.isNew = true
  activities.value.unshift(activity)

  // Remove new flag after animation
  setTimeout(() => {
    activity.isNew = false
  }, 2000)

  // Limit list size
  if (activities.value.length > 50) {
    activities.value = activities.value.slice(0, 50)
  }
}

const fetchActivities = async () => {
  if (isPaused.value) return

  try {
    const response = await fetch('/api/activities/recent?limit=' + props.maxItems)
    if (response.ok) {
      const data = await response.json()
      // Only add new activities
      const existingIds = new Set(activities.value.map(a => a.id))
      const newActivities = (data.activities || []).filter(a => !existingIds.has(a.id))
      newActivities.forEach(a => addActivity(a))
    }
  } catch (err) {
    console.error('Failed to fetch activities:', err)
  }
}

const connectWebSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws/activities`

  try {
    wsConnection = new WebSocket(wsUrl)

    wsConnection.onmessage = (event) => {
      if (isPaused.value) return

      try {
        const data = JSON.parse(event.data)
        if (data.type === 'activity') {
          addActivity(data.activity)
        }
      } catch (err) {
        console.error('WebSocket message error:', err)
      }
    }

    wsConnection.onclose = () => {
      // Reconnect after delay
      setTimeout(connectWebSocket, 5000)
    }

    wsConnection.onerror = (err) => {
      console.error('WebSocket error:', err)
    }
  } catch (err) {
    console.error('Failed to connect WebSocket:', err)
  }
}

// Lifecycle
onMounted(() => {
  fetchActivities()

  // Start auto refresh
  if (props.autoRefresh) {
    refreshTimer = setInterval(fetchActivities, props.refreshInterval)
  }

  // Connect WebSocket for real-time updates
  connectWebSocket()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (wsConnection) {
    wsConnection.close()
  }
})

// Expose for parent components
defineExpose({
  addActivity,
  refresh: fetchActivities
})
</script>

<style scoped>
.activity-feed-container {
  display: flex;
  flex-direction: column;
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 16px;
  overflow: hidden;
}

.activity-feed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #27272a;
  background: linear-gradient(180deg, rgba(249, 115, 22, 0.05) 0%, transparent 100%);
}

.activity-feed-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #fafafa;
}

.activity-live-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  font-size: 9px;
  font-weight: 700;
  color: #ef4444;
  letter-spacing: 0.05em;
}

.activity-live-dot {
  width: 6px;
  height: 6px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.activity-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #27272a;
  border: none;
  border-radius: 8px;
  color: #71717a;
  cursor: pointer;
  transition: all 0.2s;
}

.activity-toggle-btn:hover {
  background: #3f3f46;
  color: #a1a1aa;
}

.activity-toggle-btn.active {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.activity-feed-list {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
  padding: 8px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  transition: background 0.2s;
  animation: activity-fade-in 0.3s ease-out;
}

@keyframes activity-fade-in {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.activity-item:hover {
  background: #27272a;
}

.activity-item.activity-new {
  background: rgba(249, 115, 22, 0.1);
  animation: activity-highlight 2s ease-out;
}

@keyframes activity-highlight {
  0% {
    background: rgba(249, 115, 22, 0.2);
  }
  100% {
    background: transparent;
  }
}

.activity-avatar {
  position: relative;
  flex-shrink: 0;
}

.activity-avatar-img {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  object-fit: cover;
}

.activity-avatar-fallback {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #3f3f46;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #a1a1aa;
}

.activity-type-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #18181b;
}

.badge-topic { background: #3b82f6; color: white; }
.badge-reply { background: #06b6d4; color: white; }
.badge-like { background: #ef4444; color: white; }
.badge-trophy { background: #eab308; color: white; }
.badge-badge { background: #8b5cf6; color: white; }
.badge-level { background: #22c55e; color: white; }
.badge-server { background: #f97316; color: white; }
.badge-follow { background: #ec4899; color: white; }
.badge-streak { background: #f97316; color: white; }

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-text {
  font-size: 13px;
  line-height: 1.4;
  color: #a1a1aa;
}

.activity-username {
  font-weight: 600;
  color: #fafafa;
  text-decoration: none;
  transition: color 0.2s;
}

.activity-username:hover {
  color: #f97316;
}

.activity-action {
  margin: 0 4px;
}

.activity-target {
  font-weight: 500;
  color: #fafafa;
  text-decoration: none;
  transition: color 0.2s;
}

.activity-target:hover {
  color: #f97316;
  text-decoration: underline;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 11px;
  color: #52525b;
}

.activity-value {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.value-level { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.value-trophy { background: rgba(234, 179, 8, 0.15); color: #eab308; }
.value-badge { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
.value-streak { background: rgba(249, 115, 22, 0.15); color: #f97316; }

.activity-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 24px;
  color: #52525b;
  font-size: 13px;
}

.activity-view-all {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-top: 1px solid #27272a;
  font-size: 13px;
  font-weight: 500;
  color: #f97316;
  text-decoration: none;
  transition: all 0.2s;
}

.activity-view-all:hover {
  background: rgba(249, 115, 22, 0.1);
}

/* Transition Group */
.activity-item-enter-active {
  transition: all 0.3s ease-out;
}

.activity-item-leave-active {
  transition: all 0.2s ease-in;
}

.activity-item-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.activity-item-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.activity-item-move {
  transition: transform 0.3s ease;
}
</style>
