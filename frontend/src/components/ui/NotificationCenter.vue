<template>
  <div class="notification-center">
    <!-- Trigger Button -->
    <button
      class="notification-trigger"
      :class="{ 'has-unread': hasUnread }"
      @click="togglePanel"
    >
      <Bell class="w-5 h-5" />
      <span v-if="hasUnread" class="unread-badge">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Panel -->
    <Transition name="slide">
      <div v-if="isPanelOpen" class="notification-panel">
        <!-- Header -->
        <div class="panel-header">
          <h3>Bildirimler</h3>
          <div class="header-actions">
            <button
              v-if="hasUnread"
              class="mark-all-read"
              @click="handleMarkAllAsRead"
            >
              Tümünü Okundu İşaretle
            </button>
            <button class="settings-btn" @click="toggleSound">
              <VolumeX v-if="!settings.sound" class="w-4 h-4" />
              <Volume2 v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="panel-tabs">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'all' }"
            @click="activeTab = 'all'"
          >
            Tümü
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'unread' }"
            @click="activeTab = 'unread'"
          >
            Okunmamış
            <span v-if="unreadCount > 0" class="tab-count">{{ unreadCount }}</span>
          </button>
        </div>

        <!-- Content -->
        <div class="panel-content" ref="contentRef">
          <!-- Loading -->
          <div v-if="loading && notifications.length === 0" class="loading-state">
            <n-spin size="small" />
            <span>Yükleniyor...</span>
          </div>

          <!-- Empty -->
          <div v-else-if="displayedNotifications.length === 0" class="empty-state">
            <BellOff class="w-12 h-12" />
            <p v-if="activeTab === 'unread'">Okunmamış bildirim yok</p>
            <p v-else>Henüz bildirim yok</p>
          </div>

          <!-- Notifications List -->
          <div v-else class="notifications-list">
            <!-- Grouped by Date -->
            <template v-if="activeTab === 'all'">
              <div v-if="groupedNotifications.today.length > 0" class="notification-group">
                <div class="group-label">Bugün</div>
                <div
                  v-for="notification in groupedNotifications.today"
                  :key="notification.id"
                  class="notification-item"
                  :class="{ unread: !notification.read_at }"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="notification-icon" :style="{ background: getIconBg(notification.type) }">
                    <span>{{ getNotificationIcon(notification.type) }}</span>
                  </div>
                  <div class="notification-content">
                    <p class="notification-title">{{ notification.title }}</p>
                    <p class="notification-message">{{ notification.message }}</p>
                    <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                  </div>
                  <button class="delete-btn" @click.stop="handleDelete(notification.id)">
                    <X class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div v-if="groupedNotifications.yesterday.length > 0" class="notification-group">
                <div class="group-label">Dün</div>
                <div
                  v-for="notification in groupedNotifications.yesterday"
                  :key="notification.id"
                  class="notification-item"
                  :class="{ unread: !notification.read_at }"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="notification-icon" :style="{ background: getIconBg(notification.type) }">
                    <span>{{ getNotificationIcon(notification.type) }}</span>
                  </div>
                  <div class="notification-content">
                    <p class="notification-title">{{ notification.title }}</p>
                    <p class="notification-message">{{ notification.message }}</p>
                    <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                  </div>
                  <button class="delete-btn" @click.stop="handleDelete(notification.id)">
                    <X class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div v-if="groupedNotifications.thisWeek.length > 0" class="notification-group">
                <div class="group-label">Bu Hafta</div>
                <div
                  v-for="notification in groupedNotifications.thisWeek"
                  :key="notification.id"
                  class="notification-item"
                  :class="{ unread: !notification.read_at }"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="notification-icon" :style="{ background: getIconBg(notification.type) }">
                    <span>{{ getNotificationIcon(notification.type) }}</span>
                  </div>
                  <div class="notification-content">
                    <p class="notification-title">{{ notification.title }}</p>
                    <p class="notification-message">{{ notification.message }}</p>
                    <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                  </div>
                  <button class="delete-btn" @click.stop="handleDelete(notification.id)">
                    <X class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div v-if="groupedNotifications.older.length > 0" class="notification-group">
                <div class="group-label">Daha Eski</div>
                <div
                  v-for="notification in groupedNotifications.older"
                  :key="notification.id"
                  class="notification-item"
                  :class="{ unread: !notification.read_at }"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="notification-icon" :style="{ background: getIconBg(notification.type) }">
                    <span>{{ getNotificationIcon(notification.type) }}</span>
                  </div>
                  <div class="notification-content">
                    <p class="notification-title">{{ notification.title }}</p>
                    <p class="notification-message">{{ notification.message }}</p>
                    <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                  </div>
                  <button class="delete-btn" @click.stop="handleDelete(notification.id)">
                    <X class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </template>

            <!-- Unread Only -->
            <template v-else>
              <div
                v-for="notification in unreadNotifications"
                :key="notification.id"
                class="notification-item unread"
                @click="handleNotificationClick(notification)"
              >
                <div class="notification-icon" :style="{ background: getIconBg(notification.type) }">
                  <span>{{ getNotificationIcon(notification.type) }}</span>
                </div>
                <div class="notification-content">
                  <p class="notification-title">{{ notification.title }}</p>
                  <p class="notification-message">{{ notification.message }}</p>
                  <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                </div>
                <button class="delete-btn" @click.stop="handleDelete(notification.id)">
                  <X class="w-4 h-4" />
                </button>
              </div>
            </template>

            <!-- Load More -->
            <div v-if="pagination.hasMore" class="load-more">
              <button class="load-more-btn" @click="loadMore" :disabled="loading">
                {{ loading ? 'Yükleniyor...' : 'Daha Fazla Yükle' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="panel-footer">
          <router-link to="/notifications" class="view-all-btn" @click="closePanel">
            Tüm Bildirimleri Gör
            <ChevronRight class="w-4 h-4" />
          </router-link>
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

    <!-- Toast Notifications -->
    <Teleport to="body">
      <TransitionGroup name="toast" tag="div" class="toast-container">
        <div
          v-for="toast in toastQueue"
          :key="toast.id"
          class="toast-notification"
          :class="[toast.priority]"
          @click="handleToastClick(toast)"
        >
          <div class="toast-icon" :style="{ background: getIconBg(toast.type) }">
            {{ getNotificationIcon(toast.type) }}
          </div>
          <div class="toast-content">
            <span class="toast-title">{{ toast.title }}</span>
            <span class="toast-message">{{ toast.message }}</span>
          </div>
          <button class="toast-close" @click.stop="dismissToast(toast.id)">
            <X class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Bell, BellOff, X, ChevronRight, Volume2, VolumeX } from 'lucide-vue-next'
import { useNotificationsStore } from '@/stores/notifications'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const notificationsStore = useNotificationsStore()
const authStore = useAuthStore()

const {
  notifications,
  unreadCount,
  hasUnread,
  unreadNotifications,
  groupedNotifications,
  loading,
  pagination,
  settings
} = storeToRefs(notificationsStore)

const { getNotificationIcon, getNotificationColor } = notificationsStore

// Local state
const isPanelOpen = ref(false)
const activeTab = ref('all')
const contentRef = ref(null)
const toastQueue = ref([])

// Computed
const displayedNotifications = computed(() => {
  if (activeTab.value === 'unread') {
    return unreadNotifications.value
  }
  return notifications.value
})

// Methods
const getIconBg = (type) => {
  const color = getNotificationColor(type)
  return `${color}20`
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Az önce'
  if (minutes < 60) return `${minutes} dk önce`
  if (hours < 24) return `${hours} saat önce`
  if (days < 7) return `${days} gün önce`

  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

const togglePanel = () => {
  isPanelOpen.value = !isPanelOpen.value
}

const closePanel = () => {
  isPanelOpen.value = false
}

const handleNotificationClick = async (notification) => {
  // Mark as read
  if (!notification.read_at) {
    await notificationsStore.markAsRead(notification.id)
  }

  // Navigate if has action URL
  if (notification.action_url) {
    closePanel()
    router.push(notification.action_url)
  }
}

const handleDelete = async (id) => {
  await notificationsStore.deleteNotification(id)
}

const handleMarkAllAsRead = async () => {
  await notificationsStore.markAllAsRead()
}

const toggleSound = () => {
  notificationsStore.updateSettings({ sound: !settings.value.sound })
}

const loadMore = () => {
  notificationsStore.loadMore()
}

// Toast functions
const showToast = (notification) => {
  if (isPanelOpen.value) return

  toastQueue.value.push(notification)

  setTimeout(() => {
    dismissToast(notification.id)
  }, 5000)
}

const dismissToast = (id) => {
  const index = toastQueue.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toastQueue.value.splice(index, 1)
  }
}

const handleToastClick = (toast) => {
  dismissToast(toast.id)

  if (toast.action_url) {
    router.push(toast.action_url)
  } else {
    isPanelOpen.value = true
  }
}

// Watch for new notifications
watch(() => notifications.value.length, (newLen, oldLen) => {
  if (newLen > oldLen && notifications.value[0]) {
    const newNotification = notifications.value[0]
    if (!newNotification.read_at) {
      showToast(newNotification)
    }
  }
})

// Close on escape
const handleEscape = (e) => {
  if (e.key === 'Escape' && isPanelOpen.value) {
    closePanel()
  }
}

// Initialize when authenticated
watch(() => authStore.isAuthenticated, async (isAuth) => {
  if (isAuth) {
    await notificationsStore.init()
  } else {
    notificationsStore.reset()
  }
}, { immediate: true })

onMounted(() => {
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

.notification-trigger.has-unread {
  color: #f97316;
}

.unread-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #ef4444;
  border-radius: 9px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
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
  width: 400px;
  max-height: 560px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 101;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mark-all-read {
  font-size: 12px;
  color: #f97316;
  background: none;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.mark-all-read:hover {
  opacity: 0.8;
}

.settings-btn {
  padding: 6px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.settings-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.panel-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: none;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: var(--bg-secondary);
}

.tab-btn.active {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.tab-count {
  padding: 2px 8px;
  background: #ef4444;
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
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
  color: var(--text-tertiary);
  gap: 12px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.notifications-list {
  padding: 12px;
}

.notification-group {
  margin-bottom: 8px;
}

.group-label {
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.notification-item:hover {
  background: var(--bg-secondary);
}

.notification-item.unread {
  background: rgba(249, 115, 22, 0.05);
  border-left: 3px solid #f97316;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  margin: 0 0 2px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.notification-message {
  margin: 0 0 4px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  font-size: 11px;
  color: var(--text-tertiary);
}

.delete-btn {
  opacity: 0;
  padding: 6px;
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.notification-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: var(--bg-tertiary);
  color: #ef4444;
}

.load-more {
  padding: 12px;
  text-align: center;
}

.load-more-btn {
  padding: 10px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.panel-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border-color);
}

.view-all-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 12px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.view-all-btn:hover {
  background: var(--bg-tertiary);
  color: #f97316;
}

/* Transitions */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(-10px) scale(0.95);
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

/* Toast Notifications */
.toast-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 380px;
}

.toast-notification {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.2s;
}

.toast-notification:hover {
  transform: translateX(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}

.toast-notification.urgent {
  border-left: 4px solid #ef4444;
}

.toast-notification.high {
  border-left: 4px solid #f97316;
}

.toast-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 20px;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toast-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.toast-message {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toast-close {
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all 0.2s;
}

.toast-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* Toast Animations */
.toast-enter-active {
  animation: toastIn 0.3s ease;
}

.toast-leave-active {
  animation: toastOut 0.3s ease;
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toastOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
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
    max-height: 75vh;
    border-radius: 20px 20px 0 0;
  }

  .toast-container {
    left: 16px;
    right: 16px;
    max-width: none;
  }
}
</style>
