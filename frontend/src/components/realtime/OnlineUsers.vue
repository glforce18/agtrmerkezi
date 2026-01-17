<template>
  <div class="online-users">
    <div class="header">
      <h3>🟢 Online Kullanıcılar</h3>
      <span class="count">{{ onlineCount }}</span>
    </div>

    <div v-if="onlineUsers.length === 0" class="no-users">
      Şu anda kimse online değil
    </div>

    <div v-else class="users-list">
      <div
        v-for="user in onlineUsers"
        :key="user.user_id"
        class="user-item"
      >
        <div class="user-avatar">
          {{ getUserInitial(user) }}
        </div>
        <div class="user-info">
          <div class="user-name">User #{{ user.user_id }}</div>
          <div class="user-status">{{ getTimeAgo(user.timestamp) }}</div>
        </div>
        <span class="status-dot"></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRealtimeStore } from '@/stores/realtime'
import { useWebSocket } from '@/composables/useWebSocket'

const realtimeStore = useRealtimeStore()
const onlineUsers = ref([])
const onlineCount = ref(0)

// Connect to activity feed for online users
const { isConnected } = useWebSocket('/ws/activity', {
  onMessage: (data) => {
    if (data.type === 'user_activity') {
      handleUserActivity(data)
    } else if (data.type === 'online_users') {
      onlineUsers.value = data.users || []
      onlineCount.value = data.users?.length || 0
    }
  }
})

function handleUserActivity(data) {
  const { user_id, activity } = data

  if (activity === 'online') {
    realtimeStore.addOnlineUser({ user_id, timestamp: Date.now() })
  } else if (activity === 'offline') {
    realtimeStore.removeOnlineUser(user_id)
  }

  onlineUsers.value = realtimeStore.onlineUsers
  onlineCount.value = realtimeStore.onlineCount
}

function getUserInitial(user) {
  return `U${user.user_id % 26 + 1}`
}

function getTimeAgo(timestamp) {
  const seconds = Math.floor((Date.now() - timestamp) / 1000)

  if (seconds < 60) return 'Az önce'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}d önce`
  return `${Math.floor(seconds / 3600)}s önce`
}

// Update every 30 seconds
let updateInterval
onMounted(() => {
  updateInterval = setInterval(() => {
    onlineUsers.value = [...onlineUsers.value] // Force reactivity
  }, 30000)
})

onUnmounted(() => {
  if (updateInterval) clearInterval(updateInterval)
})
</script>

<style scoped>
.online-users {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 500px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.header h3 {
  margin: 0;
  font-size: 18px;
}

.count {
  background: var(--primary-color);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.no-users {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.users-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  transition: background 0.2s;
}

.user-item:hover {
  background: var(--bg-primary);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  font-size: 14px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-status {
  font-size: 12px;
  color: var(--text-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
