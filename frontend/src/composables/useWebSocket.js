import { ref, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const WS_BASE_URL = import.meta.env.VITE_WS_URL ||
  (window.location.protocol === 'https:' ? 'wss://' : 'ws://') +
  window.location.host

export function useWebSocket(endpoint, options = {}) {
  const {
    autoConnect = true,
    reconnect = true,
    reconnectDelay = 3000,
    maxReconnectAttempts = 10,
    heartbeatInterval = 30000,
    onMessage = null,
    onOpen = null,
    onClose = null,
    onError = null
  } = options

  const ws = ref(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const messageQueue = ref([])
  const lastHeartbeat = ref(null)
  const shouldReconnect = ref(reconnect) // Track reconnect state separately

  let heartbeatTimer = null
  let reconnectTimer = null

  const authStore = useAuthStore()

  // Connection status
  const status = computed(() => {
    if (isConnected.value) return 'connected'
    if (reconnectAttempts.value > 0) return 'reconnecting'
    return 'disconnected'
  })

  // Connect to WebSocket
  function connect() {
    if (ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    const url = `${WS_BASE_URL}${endpoint}`
    // Debug: WebSocket connecting

    try {
      ws.value = new WebSocket(url)

      ws.value.onopen = () => {
        // Debug: WebSocket connected
        isConnected.value = true
        reconnectAttempts.value = 0

        // Send queued messages
        while (messageQueue.value.length > 0) {
          const msg = messageQueue.value.shift()
          send(msg)
        }

        // Authenticate if token exists
        if (authStore.token) {
          send({
            action: 'auth',
            token: authStore.token
          })
        }

        // Start heartbeat
        startHeartbeat()

        if (onOpen) onOpen()
      }

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Handle ping/pong
          if (data.type === 'ping') {
            lastHeartbeat.value = Date.now()
            return
          }

          if (onMessage) onMessage(data)
        } catch (err) {
          // Parse error - ignore invalid message
        }
      }

      ws.value.onclose = (event) => {
        // Debug: WebSocket closed
        isConnected.value = false
        stopHeartbeat()

        if (onClose) onClose(event)

        // Attempt reconnect
        if (shouldReconnect.value && reconnectAttempts.value < maxReconnectAttempts) {
          reconnectAttempts.value++
          // Debug: Reconnecting... (attempt ${reconnectAttempts.value}/${maxReconnectAttempts})`)

          reconnectTimer = setTimeout(() => {
            connect()
          }, reconnectDelay)
        }
      }

      ws.value.onerror = (error) => {
        // WebSocket error - handled by onclose
        if (onError) onError(error)
      }

    } catch (error) {
      // Connection error
      isConnected.value = false
    }
  }

  // Disconnect from WebSocket
  function disconnect() {
    shouldReconnect.value = false // Prevent auto-reconnect
    stopHeartbeat()

    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    if (ws.value) {
      ws.value.close()
      ws.value = null
    }

    isConnected.value = false
  }

  // Send message
  function send(data) {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      // Queue message if not connected
      messageQueue.value.push(data)
      return false
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data)
      ws.value.send(message)
      return true
    } catch (error) {
      // Send error
      return false
    }
  }

  // Heartbeat
  function startHeartbeat() {
    stopHeartbeat()

    heartbeatTimer = setInterval(() => {
      if (isConnected.value) {
        send({ type: 'ping' })
      }
    }, heartbeatInterval)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  // Auto-connect on mount
  if (autoConnect) {
    connect()
  }

  // Cleanup on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    status,
    reconnectAttempts,
    connect,
    disconnect,
    send,
    lastHeartbeat
  }
}

// Specialized WebSocket hooks

export function useServerStatsWS(serverId = null) {
  const stats = ref(null)
  const loading = ref(true)

  const { isConnected, send } = useWebSocket('/ws/server-stats', {
    onMessage: (data) => {
      if (data.stats) {
        stats.value = data.stats
        loading.value = false
      }
    }
  })

  // Request stats for specific server
  function requestStats(id) {
    if (id) {
      send({ server_id: id })
    }
  }

  // Auto-request if serverId provided
  if (serverId) {
    requestStats(serverId)
  }

  return {
    stats,
    loading,
    isConnected,
    requestStats
  }
}

export function useDashboardWS() {
  const dashboardStats = ref({
    total_online: 0,
    total_players: 0,
    today_revenue: 0,
    active_users: 0
  })

  const { isConnected } = useWebSocket('/ws/dashboard', {
    onMessage: (data) => {
      if (data.total_online !== undefined) {
        dashboardStats.value = data
      }
    }
  })

  return {
    dashboardStats,
    isConnected
  }
}

export function useNotificationsWS() {
  const notifications = ref([])
  const authStore = useAuthStore()

  const { isConnected, send } = useWebSocket('/ws/notifications', {
    onMessage: (data) => {
      if (data.type && data.type !== 'ping') {
        notifications.value.unshift(data)
      }
    },
    onOpen: () => {
      // Send auth token on connect
      if (authStore.token) {
        send({ token: authStore.token })
      }
    }
  })

  return {
    notifications,
    isConnected
  }
}

export function useChatWS(room = 'global') {
  const messages = ref([])
  const members = ref([])
  const currentRoom = ref(room)
  const authStore = useAuthStore()

  const { isConnected, send } = useWebSocket('/ws/chat', {
    onMessage: (data) => {
      if (data.type === 'message' || data.type === 'system') {
        messages.value.push(data)

        // Keep last 100 messages
        if (messages.value.length > 100) {
          messages.value = messages.value.slice(-100)
        }
      } else if (data.type === 'members') {
        members.value = data.members || []
      }
    },
    onOpen: () => {
      // Auth and join room
      if (authStore.token) {
        send({ action: 'auth', token: authStore.token })
      }
      send({ action: 'join', room: currentRoom.value })
    }
  })

  function sendMessage(text) {
    send({
      action: 'message',
      message: text
    })
  }

  function joinRoom(roomId) {
    send({ action: 'leave' })
    currentRoom.value = roomId
    send({ action: 'join', room: roomId })
    messages.value = []
  }

  return {
    messages,
    members,
    currentRoom,
    isConnected,
    sendMessage,
    joinRoom
  }
}

// Forum Topic WebSocket - Real-time replies and typing indicators
export function useForumTopicWS(topicId, options = {}) {
  const {
    onNewReply = null,
    onReplyUpdated = null,
    onReplyDeleted = null,
    onUserTyping = null,
    onUserStopTyping = null,
    onUserJoined = null,
    onUserLeft = null,
    onViewersUpdate = null
  } = options

  const replies = ref([])
  const typingUsers = ref([])
  const viewers = ref([])
  const viewerCount = ref(0)
  const hasJoined = ref(false)
  const authStore = useAuthStore()

  // Typing indicator management
  let typingTimeout = null
  let typingClearTimeouts = {}

  const { isConnected, send, disconnect } = useWebSocket(`/ws/forum/topic/${topicId}`, {
    autoConnect: true,
    reconnect: true,
    onMessage: (data) => {
      switch (data.type) {
        case 'auth_success':
          // Authenticated, now join the room
          send({ action: 'join' })
          break

        case 'room_joined':
          hasJoined.value = true
          viewerCount.value = data.viewer_count || 0
          viewers.value = data.viewers || []
          if (onViewersUpdate) onViewersUpdate(data.viewer_count, data.viewers)
          break

        case 'forum_new_reply':
          // New reply received
          if (data.reply) {
            replies.value.push(data.reply)
            if (onNewReply) onNewReply(data.reply)
          }
          break

        case 'forum_reply_updated':
          // Reply was updated
          if (data.reply) {
            const index = replies.value.findIndex(r => r.id === data.reply_id)
            if (index !== -1) {
              replies.value[index] = { ...replies.value[index], ...data.reply }
            }
            if (onReplyUpdated) onReplyUpdated(data.reply_id, data.reply)
          }
          break

        case 'forum_reply_deleted':
          // Reply was deleted
          const deleteIndex = replies.value.findIndex(r => r.id === data.reply_id)
          if (deleteIndex !== -1) {
            replies.value.splice(deleteIndex, 1)
          }
          if (onReplyDeleted) onReplyDeleted(data.reply_id)
          break

        case 'forum_user_typing':
          // Another user is typing
          if (data.user) {
            const existingIndex = typingUsers.value.findIndex(u => u.id === data.user.id)
            if (existingIndex === -1) {
              typingUsers.value.push(data.user)
            }

            // Clear existing timeout for this user
            if (typingClearTimeouts[data.user.id]) {
              clearTimeout(typingClearTimeouts[data.user.id])
            }

            // Set timeout to remove typing indicator after 3 seconds
            typingClearTimeouts[data.user.id] = setTimeout(() => {
              const idx = typingUsers.value.findIndex(u => u.id === data.user.id)
              if (idx !== -1) {
                typingUsers.value.splice(idx, 1)
              }
              delete typingClearTimeouts[data.user.id]
            }, 3000)

            if (onUserTyping) onUserTyping(data.user)
          }
          break

        case 'forum_user_stop_typing':
          // User stopped typing
          const stopIdx = typingUsers.value.findIndex(u => u.id === data.user_id)
          if (stopIdx !== -1) {
            typingUsers.value.splice(stopIdx, 1)
          }
          if (typingClearTimeouts[data.user_id]) {
            clearTimeout(typingClearTimeouts[data.user_id])
            delete typingClearTimeouts[data.user_id]
          }
          if (onUserStopTyping) onUserStopTyping(data.user_id)
          break

        case 'forum_user_joined':
          // User joined the topic
          viewerCount.value = data.viewer_count || viewerCount.value
          if (data.user && !viewers.value.find(v => v.id === data.user.id)) {
            viewers.value.push(data.user)
          }
          if (onUserJoined) onUserJoined(data.user, data.viewer_count)
          break

        case 'forum_user_left':
          // User left the topic
          viewerCount.value = data.viewer_count || viewerCount.value
          if (data.user) {
            const leftIdx = viewers.value.findIndex(v => v.id === data.user.id)
            if (leftIdx !== -1) {
              viewers.value.splice(leftIdx, 1)
            }
          }
          if (onUserLeft) onUserLeft(data.user, data.viewer_count)
          break

        case 'viewers_update':
          viewerCount.value = data.viewer_count || 0
          viewers.value = data.viewers || []
          if (onViewersUpdate) onViewersUpdate(data.viewer_count, data.viewers)
          break
      }
    },
    onOpen: () => {
      // Authenticate first
      if (authStore.token) {
        send({ action: 'auth', token: authStore.token })
      } else {
        // Anonymous user, join directly
        send({ action: 'join' })
      }
    },
    onClose: () => {
      hasJoined.value = false
      // Clear all typing timeouts
      Object.values(typingClearTimeouts).forEach(clearTimeout)
      typingClearTimeouts = {}
    }
  })

  // Send typing indicator (debounced)
  function sendTyping() {
    if (!isConnected.value || !hasJoined.value) return

    // Clear existing timeout
    if (typingTimeout) {
      clearTimeout(typingTimeout)
    }

    // Send typing event
    send({ action: 'typing' })

    // Auto-stop typing after 3 seconds of no input
    typingTimeout = setTimeout(() => {
      send({ action: 'stop_typing' })
    }, 3000)
  }

  // Stop typing indicator
  function stopTyping() {
    if (typingTimeout) {
      clearTimeout(typingTimeout)
      typingTimeout = null
    }
    if (isConnected.value && hasJoined.value) {
      send({ action: 'stop_typing' })
    }
  }

  // Leave the room
  function leave() {
    if (isConnected.value) {
      send({ action: 'leave' })
    }
  }

  // Request viewers update
  function requestViewers() {
    if (isConnected.value) {
      send({ action: 'get_viewers' })
    }
  }

  // Cleanup function
  function cleanup() {
    stopTyping()
    leave()
    disconnect()
  }

  return {
    isConnected,
    hasJoined,
    replies,
    typingUsers,
    viewers,
    viewerCount,
    sendTyping,
    stopTyping,
    leave,
    requestViewers,
    disconnect: cleanup
  }
}
