/**
 * AGTR Merkezi - Centralized WebSocket Manager
 * Tek bağlantı üzerinden çoklu kanal yönetimi
 */

import { ref, readonly } from 'vue'
import { getAccessToken } from '@/utils/http'

const WS_BASE_URL = import.meta.env.VITE_WS_URL ||
  (window.location.protocol === 'https:' ? 'wss://' : 'ws://') +
  window.location.host

class WebSocketManager {
  constructor() {
    this.connections = new Map() // endpoint -> { ws, listeners, status }
    this.reconnectTimers = new Map()
    this.heartbeatTimers = new Map()

    // Reactive state for UI binding
    this._connectionStates = ref({})

    // Global config
    this.config = {
      reconnectDelay: 3000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000
    }
  }

  /**
   * Get connection state (reactive)
   */
  get connectionStates() {
    return readonly(this._connectionStates)
  }

  /**
   * Connect to a WebSocket endpoint
   */
  connect(endpoint, options = {}) {
    if (this.connections.has(endpoint)) {
      return this.connections.get(endpoint)
    }

    const connection = {
      ws: null,
      listeners: new Set(),
      status: 'connecting',
      reconnectAttempts: 0,
      options: {
        autoReconnect: true,
        requireAuth: false,
        ...options
      }
    }

    this.connections.set(endpoint, connection)
    this._updateState(endpoint, 'connecting')
    this._createConnection(endpoint)

    return connection
  }

  /**
   * Create WebSocket connection
   */
  _createConnection(endpoint) {
    const connection = this.connections.get(endpoint)
    if (!connection) return

    const url = `${WS_BASE_URL}${endpoint}`

    try {
      connection.ws = new WebSocket(url)

      connection.ws.onopen = () => {
        connection.status = 'connected'
        connection.reconnectAttempts = 0
        this._updateState(endpoint, 'connected')

        // Authenticate if required
        if (connection.options.requireAuth) {
          const token = getAccessToken()
          if (token) {
            this.send(endpoint, { action: 'auth', token })
          }
        }

        // Start heartbeat
        this._startHeartbeat(endpoint)

        // Notify listeners
        this._notifyListeners(endpoint, { type: 'connected' })
      }

      connection.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Handle ping/pong internally
          if (data.type === 'ping') {
            this.send(endpoint, { type: 'pong' })
            return
          }
          if (data.type === 'pong') return

          // Notify all listeners
          this._notifyListeners(endpoint, data)
        } catch (err) {
          // Parse error - ignore invalid messages
        }
      }

      connection.ws.onclose = (event) => {
        connection.status = 'disconnected'
        this._updateState(endpoint, 'disconnected')
        this._stopHeartbeat(endpoint)

        this._notifyListeners(endpoint, { type: 'disconnected', code: event.code })

        // Auto reconnect
        if (connection.options.autoReconnect && connection.reconnectAttempts < this.config.maxReconnectAttempts) {
          this._scheduleReconnect(endpoint)
        }
      }

      connection.ws.onerror = (error) => {
        // WebSocket error - handled by onclose
        this._notifyListeners(endpoint, { type: 'error', error })
      }

    } catch (error) {
      // Connection error
      connection.status = 'error'
      this._updateState(endpoint, 'error')
    }
  }

  /**
   * Send message to endpoint
   */
  send(endpoint, data) {
    const connection = this.connections.get(endpoint)
    if (!connection?.ws || connection.ws.readyState !== WebSocket.OPEN) {
      // Cannot send - not connected
      return false
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data)
      connection.ws.send(message)
      return true
    } catch (error) {
      // Send error
      return false
    }
  }

  /**
   * Subscribe to endpoint messages
   */
  subscribe(endpoint, callback, options = {}) {
    // Connect if not already connected
    if (!this.connections.has(endpoint)) {
      this.connect(endpoint, options)
    }

    const connection = this.connections.get(endpoint)
    connection.listeners.add(callback)

    // Return unsubscribe function
    return () => {
      connection.listeners.delete(callback)

      // Disconnect if no more listeners
      if (connection.listeners.size === 0 && !options.keepAlive) {
        this.disconnect(endpoint)
      }
    }
  }

  /**
   * Disconnect from endpoint
   */
  disconnect(endpoint) {
    const connection = this.connections.get(endpoint)
    if (!connection) return

    // Clear timers
    this._stopHeartbeat(endpoint)
    this._clearReconnect(endpoint)

    // Disable auto reconnect before closing
    connection.options.autoReconnect = false

    // Close connection
    if (connection.ws) {
      connection.ws.close()
    }

    // Clean up
    this.connections.delete(endpoint)
    this._updateState(endpoint, null)
  }

  /**
   * Disconnect all connections
   */
  disconnectAll() {
    for (const endpoint of this.connections.keys()) {
      this.disconnect(endpoint)
    }
  }

  /**
   * Update reactive state
   */
  _updateState(endpoint, status) {
    if (status === null) {
      delete this._connectionStates.value[endpoint]
    } else {
      this._connectionStates.value[endpoint] = status
    }
  }

  /**
   * Notify all listeners
   */
  _notifyListeners(endpoint, data) {
    const connection = this.connections.get(endpoint)
    if (!connection) return

    for (const listener of connection.listeners) {
      try {
        listener(data)
      } catch (err) {
        // Listener error
      }
    }
  }

  /**
   * Heartbeat management
   */
  _startHeartbeat(endpoint) {
    this._stopHeartbeat(endpoint)

    const timer = setInterval(() => {
      this.send(endpoint, { type: 'ping' })
    }, this.config.heartbeatInterval)

    this.heartbeatTimers.set(endpoint, timer)
  }

  _stopHeartbeat(endpoint) {
    const timer = this.heartbeatTimers.get(endpoint)
    if (timer) {
      clearInterval(timer)
      this.heartbeatTimers.delete(endpoint)
    }
  }

  /**
   * Reconnection management
   */
  _scheduleReconnect(endpoint) {
    this._clearReconnect(endpoint)

    const connection = this.connections.get(endpoint)
    if (!connection) return

    connection.reconnectAttempts++
    connection.status = 'reconnecting'
    this._updateState(endpoint, 'reconnecting')

    const delay = this.config.reconnectDelay * Math.min(connection.reconnectAttempts, 5)

    const timer = setTimeout(() => {
      this._createConnection(endpoint)
    }, delay)

    this.reconnectTimers.set(endpoint, timer)
  }

  _clearReconnect(endpoint) {
    const timer = this.reconnectTimers.get(endpoint)
    if (timer) {
      clearTimeout(timer)
      this.reconnectTimers.delete(endpoint)
    }
  }
}

// Singleton instance
export const wsManager = new WebSocketManager()

// Vue composable for easy usage
export function useWebSocketManager() {
  return {
    connectionStates: wsManager.connectionStates,
    connect: (endpoint, options) => wsManager.connect(endpoint, options),
    disconnect: (endpoint) => wsManager.disconnect(endpoint),
    subscribe: (endpoint, callback, options) => wsManager.subscribe(endpoint, callback, options),
    send: (endpoint, data) => wsManager.send(endpoint, data)
  }
}

export default wsManager
