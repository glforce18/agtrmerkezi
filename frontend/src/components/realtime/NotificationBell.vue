<template>
  <div class="notification-bell">
    <button class="bell-button" @click="toggleDropdown">
      <span class="bell-icon">🔔</span>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>

    <transition name="dropdown">
      <div v-if="isOpen" class="notifications-dropdown">
        <div class="dropdown-header">
          <h4>Bildirimler</h4>
          <button
            v-if="notifications.length > 0"
            class="mark-all-read"
            @click="markAllRead"
          >
            Tümünü Okundu İşaretle
          </button>
        </div>

        <div v-if="notifications.length === 0" class="no-notifications">
          Bildirim yok
        </div>

        <div v-else class="notifications-list">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            :class="['notification-item', { unread: !notification.read }]"
            @click="markRead(notification.id)"
          >
            <div class="notification-icon">
              {{ getNotificationIcon(notification.type) }}
            </div>
            <div class="notification-content">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-time">
                {{ formatTime(notification.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotificationsWS } from '@/composables/useWebSocket'
import { useRealtimeStore } from '@/stores/realtime'

const realtimeStore = useRealtimeStore()
const isOpen = ref(false)

const { notifications: liveNotifications, isConnected } = useNotificationsWS()

const notifications = computed(() => realtimeStore.liveNotifications)
const unreadCount = computed(() => realtimeStore.unreadNotificationCount)

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function markRead(notificationId) {
  realtimeStore.markNotificationRead(notificationId)
}

function markAllRead() {
  realtimeStore.markAllNotificationsRead()
}

function getNotificationIcon(type) {
  const icons = {
    success: '✅',
    info: 'ℹ️',
    warning: '⚠️',
    error: '❌',
    message: '💬',
    system: '🔧'
  }
  return icons[type] || 'ℹ️'
}

function formatTime(timestamp) {
  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Az önce'
  if (minutes < 60) return `${minutes} dakika önce`
  if (hours < 24) return `${hours} saat önce`
  return `${days} gün önce`
}

// Sync live notifications to store
let notificationInterval = null

const handleClickOutside = (event) => {
  const dropdown = document.querySelector('.notification-bell')
  if (dropdown && !dropdown.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  notificationInterval = setInterval(() => {
    if (liveNotifications.value.length > 0) {
      liveNotifications.value.forEach(notif => {
        realtimeStore.addNotification(notif)
      })
    }
  }, 1000)

  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (notificationInterval) {
    clearInterval(notificationInterval)
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-button {
  position: relative;
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  transition: transform 0.2s;
}

.bell-button:hover {
  transform: scale(1.1);
}

.badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: var(--error-color, #ef4444);
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  min-width: 18px;
  text-align: center;
}

.notifications-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 360px;
  max-height: 500px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.dropdown-header h4 {
  margin: 0;
  font-size: 16px;
}

.mark-all-read {
  background: transparent;
  border: none;
  color: var(--primary-color);
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
}

.mark-all-read:hover {
  text-decoration: underline;
}

.no-notifications {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.notifications-list {
  overflow-y: auto;
  max-height: 400px;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 12px 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: var(--bg-tertiary);
}

.notification-item.unread {
  background: rgba(255, 107, 0, 0.05);
}

.notification-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.notification-message {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
