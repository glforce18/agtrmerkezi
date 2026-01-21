<template>
  <div class="notification-center">
    <!-- Trigger Button -->
    <button
      class="notification-trigger"
      :class="{ 'has-unread': unreadCount > 0 }"
      @click="togglePanel"
    >
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
      <span v-if="unreadCount > 0" class="unread-badge">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Panel -->
    <Transition name="slide">
      <div v-if="isPanelOpen" class="notification-panel">
        <!-- Header -->
        <div class="panel-header">
          <h3>Bildirimler</h3>
          <button
            v-if="unreadCount > 0"
            class="mark-all-read"
            @click="markAllAsRead"
          >
            Tümünü Okundu İşaretle
          </button>
        </div>

        <!-- Tabs -->
        <div class="panel-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" class="tab-count">{{ tab.count }}</span>
          </button>
        </div>

        <!-- Content -->
        <div class="panel-content">
          <!-- Loading -->
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <span>Yükleniyor...</span>
          </div>

          <!-- Empty -->
          <div v-else-if="filteredNotifications.length === 0" class="empty-state">
            <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            <p>Bildirim yok</p>
          </div>

          <!-- Notifications List -->
          <div v-else class="notifications-list">
            <TransitionGroup name="list">
              <div
                v-for="notification in filteredNotifications"
                :key="notification.id"
                class="notification-item"
                :class="{ unread: !notification.read }"
                @click="handleNotificationClick(notification)"
              >
                <div class="notification-icon" :class="notification.type">
                  <component :is="getIcon(notification.type)" />
                </div>
                <div class="notification-content">
                  <p class="notification-message">{{ notification.message }}</p>
                  <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                </div>
                <button
                  class="delete-btn"
                  @click.stop="deleteNotification(notification.id)"
                >
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </TransitionGroup>
          </div>
        </div>

        <!-- Footer -->
        <div class="panel-footer">
          <button class="view-all-btn" @click="viewAll">
            Tümünü Gör
          </button>
        </div>
      </div>
    </Transition>

    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="isPanelOpen"
        class="notification-backdrop"
        @click="closePanel"
      ></div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

const router = useRouter()

// State
const isPanelOpen = ref(false)
const activeTab = ref('all')
const loading = ref(false)
const notifications = ref([])

// Tabs configuration
const tabs = computed(() => [
  { id: 'all', label: 'Tümü', count: notifications.value.length },
  { id: 'unread', label: 'Okunmamış', count: unreadCount.value },
  { id: 'system', label: 'Sistem', count: notifications.value.filter(n => n.type === 'system').length },
])

// Computed
const unreadCount = computed(() =>
  notifications.value.filter(n => !n.read).length
)

const filteredNotifications = computed(() => {
  let result = [...notifications.value]

  switch (activeTab.value) {
    case 'unread':
      result = result.filter(n => !n.read)
      break
    case 'system':
      result = result.filter(n => n.type === 'system')
      break
  }

  return result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

// Icons based on notification type
const getIcon = (type) => {
  const icons = {
    success: () => h('svg', { viewBox: '0 0 24 24', width: 18, height: 18, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14' }),
      h('path', { d: 'M22 4L12 14.01l-3-3' })
    ]),
    error: () => h('svg', { viewBox: '0 0 24 24', width: 18, height: 18, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('path', { d: 'M15 9l-6 6M9 9l6 6' })
    ]),
    warning: () => h('svg', { viewBox: '0 0 24 24', width: 18, height: 18, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
      h('path', { d: 'M12 9v4M12 17h.01' })
    ]),
    info: () => h('svg', { viewBox: '0 0 24 24', width: 18, height: 18, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('path', { d: 'M12 16v-4M12 8h.01' })
    ]),
    system: () => h('svg', { viewBox: '0 0 24 24', width: 18, height: 18, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z' }),
      h('circle', { cx: 12, cy: 12, r: 3 })
    ])
  }
  return icons[type] || icons.info
}

// Format time
const formatTime = (date) => {
  if (!date) return ''
  return formatDistanceToNow(new Date(date), { addSuffix: true, locale: tr })
}

// Actions
const togglePanel = () => {
  isPanelOpen.value = !isPanelOpen.value
}

const closePanel = () => {
  isPanelOpen.value = false
}

const markAllAsRead = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    const response = await fetch('/api/notifications/read-all', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.ok) {
      notifications.value.forEach(n => n.read = true)
    }
  } catch (error) {
    console.error('Failed to mark all as read:', error)
  }
}

const handleNotificationClick = async (notification) => {
  // Mark as read via API if not already read
  if (!notification.read) {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const response = await fetch(`/api/notifications/${notification.id}/read`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (response.ok) {
          notification.read = true
        }
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
      }
    }
  }

  // Navigate if link exists
  if (notification.link) {
    router.push(notification.link)
    closePanel()
  }
}

const deleteNotification = async (id) => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    const response = await fetch(`/api/notifications/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.ok) {
      notifications.value = notifications.value.filter(n => n.id !== id)
    }
  } catch (error) {
    console.error('Failed to delete notification:', error)
  }
}

const viewAll = () => {
  router.push('/notifications')
  closePanel()
}

// Load notifications
const loadNotifications = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  loading.value = true
  try {
    const response = await fetch('/api/notifications', {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.ok) {
      const data = await response.json()
      // Map API response to component format
      notifications.value = (data.notifications || data || []).map(n => ({
        id: n.id,
        type: n.type || 'info',
        message: n.message || n.content,
        created_at: n.created_at,
        read: n.is_read || false,
        link: n.link || n.action_url
      }))
    }
  } catch (error) {
    console.error('Failed to load notifications:', error)
  } finally {
    loading.value = false
  }
}

// Close on escape
const handleEscape = (e) => {
  if (e.key === 'Escape' && isPanelOpen.value) {
    closePanel()
  }
}

onMounted(() => {
  loadNotifications()
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
.notification-center {
  position: relative;
}

.notification-trigger {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.notification-trigger:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.unread-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: var(--error-color, #ef4444);
  border-radius: 9px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
}

.notification-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 380px;
  max-height: 500px;
  background: var(--bg-primary, #0f0f1a);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  z-index: 101;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.mark-all-read {
  font-size: 12px;
  color: var(--primary-color);
  background: none;
  border: none;
  cursor: pointer;
}

.panel-tabs {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
}

.tab-btn {
  padding: 6px 12px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover,
.tab-btn.active {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tab-count {
  margin-left: 4px;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  font-size: 11px;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-secondary);
  gap: 12px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.notifications-list {
  padding: 8px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: var(--bg-secondary);
}

.notification-item.unread {
  background: rgba(var(--primary-rgb, 59, 130, 246), 0.1);
}

.notification-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.success { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.notification-icon.error { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.notification-icon.warning { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.notification-icon.info { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.notification-icon.system { background: rgba(139, 92, 246, 0.2); color: #8b5cf6; }

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  margin: 0 0 4px;
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
}

.notification-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.delete-btn {
  opacity: 0;
  padding: 4px;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.notification-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: var(--bg-tertiary);
  color: var(--error-color);
}

.panel-footer {
  padding: 12px;
  border-top: 1px solid var(--border-color, #2a2a4a);
}

.view-all-btn {
  width: 100%;
  padding: 10px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.view-all-btn:hover {
  background: var(--bg-tertiary);
}

/* Transitions */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.2s, opacity 0.2s;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Mobile */
@media (max-width: 480px) {
  .notification-panel {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-height: 70vh;
    border-radius: 16px 16px 0 0;
  }
}
</style>
