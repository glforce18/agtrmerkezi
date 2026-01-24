/**
 * Notifications Store - Bildirim Sistemi
 * Real-time notifications for user activities
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

// Notification Types
export const NotificationType = {
  // Social
  FRIEND_REQUEST: 'friend_request',
  FRIEND_ACCEPTED: 'friend_accepted',
  NEW_MESSAGE: 'new_message',
  MENTION: 'mention',

  // Gaming
  ACHIEVEMENT_UNLOCKED: 'achievement_unlocked',
  LEVEL_UP: 'level_up',
  TOURNAMENT_INVITE: 'tournament_invite',
  TOURNAMENT_START: 'tournament_start',
  MATCH_READY: 'match_ready',

  // Forum
  REPLY_TO_POST: 'reply_to_post',
  POST_LIKED: 'post_liked',
  NEW_TOPIC_IN_FOLLOWED: 'new_topic_in_followed',

  // Server
  SERVER_ONLINE: 'server_online',
  SERVER_OFFLINE: 'server_offline',
  SERVER_EXPIRING: 'server_expiring',

  // System
  SYSTEM_ANNOUNCEMENT: 'system_announcement',
  WELCOME: 'welcome',
  DAILY_REWARD: 'daily_reward'
}

// Notification Priority
export const NotificationPriority = {
  LOW: 'low',
  NORMAL: 'normal',
  HIGH: 'high',
  URGENT: 'urgent'
}

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref(null)

  // Settings
  const settings = ref({
    sound: true,
    desktop: false,
    email: true,
    push: true,
    // Type-specific settings
    types: {
      [NotificationType.FRIEND_REQUEST]: true,
      [NotificationType.NEW_MESSAGE]: true,
      [NotificationType.ACHIEVEMENT_UNLOCKED]: true,
      [NotificationType.TOURNAMENT_INVITE]: true,
      [NotificationType.SERVER_EXPIRING]: true,
      [NotificationType.SYSTEM_ANNOUNCEMENT]: true
    }
  })

  // Pagination
  const pagination = ref({
    page: 1,
    limit: 20,
    hasMore: true
  })

  // Computed
  const hasUnread = computed(() => unreadCount.value > 0)

  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => !n.read_at)
  })

  const groupedNotifications = computed(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const thisWeek = new Date(today)
    thisWeek.setDate(thisWeek.getDate() - 7)

    const groups = {
      today: [],
      yesterday: [],
      thisWeek: [],
      older: []
    }

    notifications.value.forEach(notification => {
      const date = new Date(notification.created_at)
      date.setHours(0, 0, 0, 0)

      if (date.getTime() === today.getTime()) {
        groups.today.push(notification)
      } else if (date.getTime() === yesterday.getTime()) {
        groups.yesterday.push(notification)
      } else if (date >= thisWeek) {
        groups.thisWeek.push(notification)
      } else {
        groups.older.push(notification)
      }
    })

    return groups
  })

  // Actions
  const fetchNotifications = async (options = {}) => {
    const { reset = false } = options

    if (reset) {
      pagination.value.page = 1
      notifications.value = []
    }

    loading.value = true
    error.value = null

    try {
      const response = await api.get('/notifications', {
        page: pagination.value.page,
        limit: pagination.value.limit
      })

      const newNotifications = response.notifications || response.data || response || []

      if (reset) {
        notifications.value = newNotifications
      } else {
        notifications.value = [...notifications.value, ...newNotifications]
      }

      unreadCount.value = response.unread_count ?? unreadNotifications.value.length
      pagination.value.hasMore = newNotifications.length >= pagination.value.limit

      return newNotifications
    } catch (e) {
      // Notification fetch failed - silent
      error.value = 'Bildirimler yüklenemedi'
      return []
    } finally {
      loading.value = false
    }
  }

  const loadMore = async () => {
    if (!pagination.value.hasMore || loading.value) return

    pagination.value.page++
    await fetchNotifications()
  }

  const markAsRead = async (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (!notification || notification.read_at) return

    // Optimistic update
    notification.read_at = new Date().toISOString()
    unreadCount.value = Math.max(0, unreadCount.value - 1)

    try {
      await api.post(`/notifications/${notificationId}/read`)
    } catch (e) {
      // Mark as read failed - revert
      // Revert on error
      notification.read_at = null
      unreadCount.value++
    }
  }

  const markAllAsRead = async () => {
    // Optimistic update
    const previousUnread = notifications.value.filter(n => !n.read_at)
    const now = new Date().toISOString()

    previousUnread.forEach(n => {
      n.read_at = now
    })
    unreadCount.value = 0

    try {
      await api.post('/notifications/read-all')
    } catch (e) {
      // Mark all as read failed - revert
      // Revert on error
      previousUnread.forEach(n => {
        n.read_at = null
      })
      unreadCount.value = previousUnread.length
    }
  }

  const deleteNotification = async (notificationId) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index === -1) return

    const notification = notifications.value[index]
    const wasUnread = !notification.read_at

    // Optimistic update
    notifications.value.splice(index, 1)
    if (wasUnread) {
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }

    try {
      await api.delete(`/notifications/${notificationId}`)
    } catch (e) {
      // Delete notification failed - revert
      // Revert on error
      notifications.value.splice(index, 0, notification)
      if (wasUnread) {
        unreadCount.value++
      }
    }
  }

  const clearAll = async () => {
    const previousNotifications = [...notifications.value]
    const previousUnread = unreadCount.value

    // Optimistic update
    notifications.value = []
    unreadCount.value = 0

    try {
      await api.delete('/notifications')
    } catch (e) {
      // Revert on error
      notifications.value = previousNotifications
      unreadCount.value = previousUnread
    }
  }

  // Real-time handler
  const addNotification = (notification) => {
    // Check if notification type is enabled
    if (settings.value.types[notification.type] === false) return

    // Check for duplicate
    if (notifications.value.find(n => n.id === notification.id)) return

    // Add to beginning
    notifications.value.unshift(notification)
    unreadCount.value++

    // Play sound if enabled
    if (settings.value.sound) {
      playNotificationSound(notification.priority)
    }

    // Show desktop notification if enabled
    if (settings.value.desktop && Notification.permission === 'granted') {
      showDesktopNotification(notification)
    }

    return notification
  }

  const playNotificationSound = (priority = NotificationPriority.NORMAL) => {
    try {
      const audio = new Audio()

      // Different sounds for different priorities
      if (priority === NotificationPriority.URGENT) {
        audio.src = '/sounds/notification-urgent.mp3'
      } else if (priority === NotificationPriority.HIGH) {
        audio.src = '/sounds/notification-high.mp3'
      } else {
        audio.src = '/sounds/notification.mp3'
      }

      audio.volume = 0.5
      audio.play().catch(() => {
        // Autoplay might be blocked
      })
    } catch (e) {
      // Sound not available
    }
  }

  const showDesktopNotification = (notification) => {
    if (Notification.permission !== 'granted') return

    const options = {
      body: notification.message || notification.content,
      icon: notification.icon || '/favicon.ico',
      badge: '/badge.png',
      tag: notification.id,
      requireInteraction: notification.priority === NotificationPriority.URGENT,
      data: { url: notification.action_url }
    }

    const desktopNotif = new Notification(
      notification.title || 'AGTR Merkezi',
      options
    )

    desktopNotif.onclick = () => {
      window.focus()
      if (notification.action_url) {
        window.location.href = notification.action_url
      }
      desktopNotif.close()
    }
  }

  const requestDesktopPermission = async () => {
    if (!('Notification' in window)) {
      return false
    }

    if (Notification.permission === 'granted') {
      settings.value.desktop = true
      return true
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission()
      settings.value.desktop = permission === 'granted'
      return permission === 'granted'
    }

    return false
  }

  // Settings
  const updateSettings = async (newSettings) => {
    const previousSettings = { ...settings.value }
    settings.value = { ...settings.value, ...newSettings }

    try {
      await api.put('/notifications/preferences', settings.value)
    } catch (e) {
      // Silent fail - settings will revert
      settings.value = previousSettings
    }
  }

  const fetchSettings = async () => {
    try {
      const response = await api.get('/notifications/preferences')
      settings.value = { ...settings.value, ...response }
    } catch (e) {
      // Silent fail - use default settings
    }
  }

  // Helpers
  const getNotificationIcon = (type) => {
    const icons = {
      [NotificationType.FRIEND_REQUEST]: '👥',
      [NotificationType.FRIEND_ACCEPTED]: '🤝',
      [NotificationType.NEW_MESSAGE]: '💬',
      [NotificationType.MENTION]: '@',
      [NotificationType.ACHIEVEMENT_UNLOCKED]: '🏆',
      [NotificationType.LEVEL_UP]: '⬆️',
      [NotificationType.TOURNAMENT_INVITE]: '🎮',
      [NotificationType.TOURNAMENT_START]: '🏁',
      [NotificationType.MATCH_READY]: '⚔️',
      [NotificationType.REPLY_TO_POST]: '💭',
      [NotificationType.POST_LIKED]: '❤️',
      [NotificationType.NEW_TOPIC_IN_FOLLOWED]: '📢',
      [NotificationType.SERVER_ONLINE]: '🟢',
      [NotificationType.SERVER_OFFLINE]: '🔴',
      [NotificationType.SERVER_EXPIRING]: '⚠️',
      [NotificationType.SYSTEM_ANNOUNCEMENT]: '📣',
      [NotificationType.WELCOME]: '👋',
      [NotificationType.DAILY_REWARD]: '🎁'
    }
    return icons[type] || '🔔'
  }

  const getNotificationColor = (type) => {
    const colors = {
      [NotificationType.FRIEND_REQUEST]: '#3b82f6',
      [NotificationType.FRIEND_ACCEPTED]: '#22c55e',
      [NotificationType.NEW_MESSAGE]: '#8b5cf6',
      [NotificationType.ACHIEVEMENT_UNLOCKED]: '#f59e0b',
      [NotificationType.LEVEL_UP]: '#22c55e',
      [NotificationType.TOURNAMENT_INVITE]: '#f97316',
      [NotificationType.SERVER_EXPIRING]: '#ef4444',
      [NotificationType.SYSTEM_ANNOUNCEMENT]: '#06b6d4'
    }
    return colors[type] || '#6b7280'
  }

  // Initialize
  const init = async () => {
    await Promise.all([
      fetchNotifications({ reset: true }),
      fetchSettings()
    ])
  }

  // Reset
  const reset = () => {
    notifications.value = []
    unreadCount.value = 0
    pagination.value = { page: 1, limit: 20, hasMore: true }
    error.value = null
  }

  return {
    // State
    notifications,
    unreadCount,
    loading,
    error,
    settings,
    pagination,

    // Computed
    hasUnread,
    unreadNotifications,
    groupedNotifications,

    // Actions
    fetchNotifications,
    loadMore,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
    addNotification,
    playNotificationSound,
    showDesktopNotification,
    requestDesktopPermission,
    updateSettings,
    fetchSettings,
    init,
    reset,

    // Helpers
    getNotificationIcon,
    getNotificationColor,

    // Constants
    NotificationType,
    NotificationPriority
  }
})
