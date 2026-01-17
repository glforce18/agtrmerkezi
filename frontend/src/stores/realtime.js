import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
  }

  function getServerStats(serverId) {
    return serverStats.value.get(serverId) || null
  }

  function addActivity(activity) {
    activityFeed.value.unshift({
      ...activity,
      id: Date.now(),
      timestamp: activity.timestamp || Date.now()
    })

    // Keep last 50 activities
    if (activityFeed.value.length > 50) {
      activityFeed.value = activityFeed.value.slice(0, 50)
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

    // Keep last 100 messages per room
    if (messages.length > 100) {
      chatMessages.value.set(roomId, messages.slice(-100))
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

    // Keep last 20 notifications
    if (liveNotifications.value.length > 20) {
      liveNotifications.value = liveNotifications.value.slice(0, 20)
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

  function reset() {
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
    addActivity,
    addChatMessage,
    getChatMessages,
    clearChatMessages,
    addNotification,
    markNotificationRead,
    markAllNotificationsRead,
    clearNotifications,
    setConnectionStatus,
    reset
  }
})
