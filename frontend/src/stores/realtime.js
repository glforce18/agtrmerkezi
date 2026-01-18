import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Memory management constants
const MAX_SERVER_STATS_AGE = 5 * 60 * 1000 // 5 dakika
const MAX_ACTIVITY_FEED_SIZE = 50
const MAX_CHAT_MESSAGES_PER_ROOM = 100
const MAX_NOTIFICATIONS = 20
const CLEANUP_INTERVAL = 60 * 1000 // 1 dakika

export const useRealtimeStore = defineStore('realtime', () => {
  // Dashboard stats
  const dashboardStats = ref({
    total_online: 0,
    total_players: 0,
    today_revenue: 0,
    active_users: 0
  })

  // Online users
  const onlineUsers = ref([])

  // Server stats cache
  const serverStats = ref(new Map())

  // Activity feed
  const activityFeed = ref([])

  // Chat messages
  const chatMessages = ref(new Map()) // room_id -> messages[]

  // Notifications
  const liveNotifications = ref([])

  // Connection status
  const connectionStatus = ref({
    dashboard: false,
    notifications: false,
    chat: false,
    serverStats: false
  })

  // Cleanup timer reference
  let cleanupTimer = null

  // Computed
  const onlineCount = computed(() => onlineUsers.value.length)

  const hasUnreadNotifications = computed(() =>
    liveNotifications.value.some(n => !n.read)
  )

  const unreadNotificationCount = computed(() =>
    liveNotifications.value.filter(n => !n.read).length
  )

  // Actions
  function updateDashboardStats(stats) {
    dashboardStats.value = { ...dashboardStats.value, ...stats }
  }

  function setOnlineUsers(users) {
    onlineUsers.value = users
  }

  function addOnlineUser(user) {
    if (!onlineUsers.value.find(u => u.id === user.id)) {
      onlineUsers.value.push(user)
    }
  }

  function removeOnlineUser(userId) {
    onlineUsers.value = onlineUsers.value.filter(u => u.id !== userId)
  }

  function updateServerStats(serverId, stats) {
    serverStats.value.set(serverId, {
      ...stats,
      updated_at: Date.now()
    })

    // Cleanup old entries if Map grows too large (> 100 servers)
    if (serverStats.value.size > 100) {
      cleanupStaleServerStats()
    }
  }

  function getServerStats(serverId) {
    return serverStats.value.get(serverId) || null
  }

  // Memory cleanup: Remove stale server stats
  function cleanupStaleServerStats() {
    const now = Date.now()
    const staleIds = []

    serverStats.value.forEach((stats, serverId) => {
      if (now - stats.updated_at > MAX_SERVER_STATS_AGE) {
        staleIds.push(serverId)
      }
    })

    staleIds.forEach(id => serverStats.value.delete(id))
  }

  // Clear specific server stats
  function clearServerStats(serverId) {
    serverStats.value.delete(serverId)
  }

  function addActivity(activity) {
    activityFeed.value.unshift({
      ...activity,
      id: Date.now(),
      timestamp: activity.timestamp || Date.now()
    })

    // Keep last N activities (use constant)
    if (activityFeed.value.length > MAX_ACTIVITY_FEED_SIZE) {
      activityFeed.value = activityFeed.value.slice(0, MAX_ACTIVITY_FEED_SIZE)
    }
  }

  function addChatMessage(roomId, message) {
    if (!chatMessages.value.has(roomId)) {
      chatMessages.value.set(roomId, [])
    }

    const messages = chatMessages.value.get(roomId)
    messages.push({
      ...message,
      id: Date.now(),
      timestamp: message.timestamp || Date.now()
    })

    // Keep last N messages per room (use constant)
    if (messages.length > MAX_CHAT_MESSAGES_PER_ROOM) {
      chatMessages.value.set(roomId, messages.slice(-MAX_CHAT_MESSAGES_PER_ROOM))
    }
  }

  function getChatMessages(roomId) {
    return chatMessages.value.get(roomId) || []
  }

  function clearChatMessages(roomId) {
    chatMessages.value.delete(roomId)
  }

  function addNotification(notification) {
    liveNotifications.value.unshift({
      ...notification,
      id: Date.now(),
      read: false,
      timestamp: notification.timestamp || Date.now()
    })

    // Keep last N notifications (use constant)
    if (liveNotifications.value.length > MAX_NOTIFICATIONS) {
      liveNotifications.value = liveNotifications.value.slice(0, MAX_NOTIFICATIONS)
    }
  }

  function markNotificationRead(notificationId) {
    const notification = liveNotifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  function markAllNotificationsRead() {
    liveNotifications.value.forEach(n => n.read = true)
  }

  function clearNotifications() {
    liveNotifications.value = []
  }

  function setConnectionStatus(endpoint, status) {
    connectionStatus.value[endpoint] = status
  }

  // Periodic cleanup for memory management
  function startPeriodicCleanup() {
    if (cleanupTimer) return // Already running

    cleanupTimer = setInterval(() => {
      cleanupStaleServerStats()

      // Cleanup inactive chat rooms (no messages in 30 minutes)
      const thirtyMinutesAgo = Date.now() - 30 * 60 * 1000
      chatMessages.value.forEach((messages, roomId) => {
        if (messages.length === 0) {
          chatMessages.value.delete(roomId)
        } else {
          const lastMessage = messages[messages.length - 1]
          if (lastMessage.timestamp < thirtyMinutesAgo) {
            chatMessages.value.delete(roomId)
          }
        }
      })
    }, CLEANUP_INTERVAL)
  }

  function stopPeriodicCleanup() {
    if (cleanupTimer) {
      clearInterval(cleanupTimer)
      cleanupTimer = null
    }
  }

  function reset() {
    stopPeriodicCleanup()

    dashboardStats.value = {
      total_online: 0,
      total_players: 0,
      today_revenue: 0,
      active_users: 0
    }
    onlineUsers.value = []
    serverStats.value.clear()
    activityFeed.value = []
    chatMessages.value.clear()
    liveNotifications.value = []
    connectionStatus.value = {
      dashboard: false,
      notifications: false,
      chat: false,
      serverStats: false
    }
  }

  return {
    // State
    dashboardStats,
    onlineUsers,
    serverStats,
    activityFeed,
    chatMessages,
    liveNotifications,
    connectionStatus,

    // Computed
    onlineCount,
    hasUnreadNotifications,
    unreadNotificationCount,

    // Actions
    updateDashboardStats,
    setOnlineUsers,
    addOnlineUser,
    removeOnlineUser,
    updateServerStats,
    getServerStats,
    clearServerStats,
    cleanupStaleServerStats,
    addActivity,
    addChatMessage,
    getChatMessages,
    clearChatMessages,
    addNotification,
    markNotificationRead,
    markAllNotificationsRead,
    clearNotifications,
    setConnectionStatus,
    startPeriodicCleanup,
    stopPeriodicCleanup,
    reset
  }
})
