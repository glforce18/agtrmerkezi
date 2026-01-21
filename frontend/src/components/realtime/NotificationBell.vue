<template>
  <div class="notification-bell" ref="bellRef">
    <button class="bell-button" @click="toggleDropdown" :class="{ 'has-unread': unreadCount > 0 }">
      <BellIcon :size="22" />
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
      <span v-if="unreadCount > 0" class="pulse-ring"></span>
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="notifications-dropdown">
        <div class="dropdown-header">
          <div class="header-title">
            <BellIcon :size="18" />
            <h4>Bildirimler</h4>
          </div>
          <div class="header-actions" v-if="notifications.length > 0">
            <button class="action-btn" @click="markAllAsRead" :disabled="loading" title="Tümünü okundu işaretle">
              <CheckCheckIcon :size="16" />
              <span>Okundu</span>
            </button>
            <button class="action-btn danger" @click="clearAllNotifications" :disabled="loading" title="Tümünü temizle">
              <Trash2Icon :size="16" />
              <span>Temizle</span>
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <Loader2Icon :size="24" class="spin" />
          <span>Yükleniyor...</span>
        </div>

        <div v-else-if="notifications.length === 0" class="empty-state">
          <BellOffIcon :size="48" />
          <p>Bildirim yok</p>
          <span>Yeni bildirimler burada görünecek</span>
        </div>

        <div v-else class="notifications-list">
          <TransitionGroup name="notification">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              :class="['notification-item', { unread: !notification.is_read }]"
              @click="handleNotificationClick(notification)"
            >
              <div class="notification-icon" :class="notification.type">
                {{ notification.icon || getNotificationIcon(notification.type) }}
              </div>
              <div class="notification-content">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-message" v-if="notification.message">{{ notification.message }}</div>
                <div class="notification-meta">
                  <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                  <span v-if="!notification.is_read" class="unread-badge">Yeni</span>
                </div>
              </div>
              <button class="delete-btn" @click.stop="deleteNotification(notification.id)" title="Sil">
                <XIcon :size="14" />
              </button>
            </div>
          </TransitionGroup>
        </div>

        <div class="dropdown-footer" v-if="notifications.length > 0">
          <router-link to="/notifications" class="view-all-btn" @click="isOpen = false">
            Tüm Bildirimleri Gör
            <ChevronRightIcon :size="16" />
          </router-link>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Bell as BellIcon,
  BellOff as BellOffIcon,
  CheckCheck as CheckCheckIcon,
  Trash2 as Trash2Icon,
  X as XIcon,
  Loader2 as Loader2Icon,
  ChevronRight as ChevronRightIcon
} from 'lucide-vue-next'

const bellRef = ref(null)
const isOpen = ref(false)
const loading = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

// Toggle dropdown
function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    fetchNotifications()
  }
}

// Fetch notifications from API
async function fetchNotifications() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const res = await fetch('/api/notifications/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (res.ok) {
      const data = await res.json()
      notifications.value = data.notifications || []
      unreadCount.value = data.unread_count || 0
    }
  } catch (e) {
    // Error handled
  } finally {
    loading.value = false
  }
}

// Mark single notification as read
async function markAsRead(notificationId) {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return

    await fetch(`/api/notifications/${notificationId}/read`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    // Update local state
    const notif = notifications.value.find(n => n.id === notificationId)
    if (notif) {
      notif.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  } catch (e) {
    // Error handled
  }
}

// Mark all as read
async function markAllAsRead() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const res = await fetch('/api/notifications/read-all', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (res.ok) {
      // Update local state
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    }
  } catch (e) {
    // Error handled
  } finally {
    loading.value = false
  }
}

// Delete single notification
async function deleteNotification(notificationId) {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const res = await fetch(`/api/notifications/${notificationId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (res.ok) {
      const notif = notifications.value.find(n => n.id === notificationId)
      if (notif && !notif.is_read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      notifications.value = notifications.value.filter(n => n.id !== notificationId)
    }
  } catch (e) {
    // Error handled
  }
}

// Clear all notifications
async function clearAllNotifications() {
  if (!confirm('Tüm bildirimleri silmek istediğinize emin misiniz?')) return

  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const res = await fetch('/api/notifications/', {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (res.ok) {
      notifications.value = []
      unreadCount.value = 0
    }
  } catch (e) {
    // Error handled
  } finally {
    loading.value = false
  }
}

// Handle notification click
function handleNotificationClick(notification) {
  if (!notification.is_read) {
    markAsRead(notification.id)
  }

  if (notification.action_url) {
    window.location.href = notification.action_url
    isOpen.value = false
  }
}

// Get icon for notification type
function getNotificationIcon(type) {
  const icons = {
    success: '✅',
    info: 'ℹ️',
    warning: '⚠️',
    error: '❌',
    payment: '💰',
    server: '🖥️',
    forum: '💬',
    system: '🔧'
  }
  return icons[type] || '📢'
}

// Format time
function formatTime(timestamp) {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Az önce'
  if (minutes < 60) return `${minutes} dk önce`
  if (hours < 24) return `${hours} saat önce`
  if (days < 7) return `${days} gün önce`

  return date.toLocaleDateString('tr-TR')
}

// Click outside handler
function handleClickOutside(event) {
  if (bellRef.value && !bellRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

// Periodic refresh
let refreshInterval = null

onMounted(() => {
  document.addEventListener('click', handleClickOutside)

  // Initial fetch
  fetchNotifications()

  // Refresh every 30 seconds
  refreshInterval = setInterval(fetchNotifications, 30000)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-button {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
}

.bell-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: scale(1.05);
}

.bell-button.has-unread {
  color: #ff6b00;
  border-color: rgba(255, 107, 0, 0.3);
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: linear-gradient(135deg, #ff3366 0%, #ff6b00 100%);
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 700;
  min-width: 18px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(255, 51, 102, 0.4);
}

.pulse-ring {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(255, 51, 102, 0.4);
  animation: pulse-ring 1.5s ease-out infinite;
  pointer-events: none;
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

.notifications-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 400px;
  max-height: 520px;
  background: linear-gradient(135deg, rgba(30, 30, 45, 0.98) 0%, rgba(20, 20, 30, 0.98) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
}

.header-title h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
  color: #00d4ff;
}

.action-btn.danger:hover:not(:disabled) {
  background: rgba(255, 51, 102, 0.1);
  border-color: rgba(255, 51, 102, 0.3);
  color: #ff3366;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: rgba(255, 255, 255, 0.4);
  gap: 12px;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
}

.empty-state span {
  font-size: 13px;
}

.notifications-list {
  flex: 1;
  overflow-y: auto;
  max-height: 360px;
}

.notifications-list::-webkit-scrollbar {
  width: 6px;
}

.notifications-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}

.notifications-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.notification-item {
  display: flex;
  gap: 14px;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.notification-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.notification-item.unread {
  background: rgba(255, 107, 0, 0.05);
  border-left: 3px solid #ff6b00;
}

.notification-item.unread:hover {
  background: rgba(255, 107, 0, 0.08);
}

.notification-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  font-size: 18px;
  flex-shrink: 0;
}

.notification-icon.success { background: rgba(0, 255, 136, 0.1); }
.notification-icon.error { background: rgba(255, 51, 102, 0.1); }
.notification-icon.warning { background: rgba(255, 200, 0, 0.1); }
.notification-icon.payment { background: rgba(255, 200, 0, 0.1); }

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  color: #fff;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.notification-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.unread-badge {
  font-size: 10px;
  font-weight: 700;
  color: #ff6b00;
  background: rgba(255, 107, 0, 0.15);
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.delete-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.notification-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(255, 51, 102, 0.2);
  color: #ff3366;
}

.dropdown-footer {
  padding: 12px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.view-all-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  background: rgba(255, 107, 0, 0.1);
  border: 1px solid rgba(255, 107, 0, 0.2);
  border-radius: 10px;
  color: #ff6b00;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  background: rgba(255, 107, 0, 0.2);
  border-color: rgba(255, 107, 0, 0.4);
}

/* Animations */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Responsive */
@media (max-width: 480px) {
  .notifications-dropdown {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-height: 70vh;
    border-radius: 20px 20px 0 0;
  }

  .header-actions span {
    display: none;
  }
}
</style>
