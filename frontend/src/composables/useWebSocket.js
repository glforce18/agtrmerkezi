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
