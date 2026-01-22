/**
 * Messages Store - Mesajlaşma Sistemi
 * Real-time messaging between users
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useMessagesStore = defineStore('messages', () => {
  // State
  const conversations = ref([]) // List of all conversations
  const activeConversation = ref(null) // Currently open conversation
  const messages = ref({}) // Messages by conversation ID
  const loading = ref(false)
  const sendingMessage = ref(false)
  const error = ref(null)

  // Unread counts
  const unreadCounts = ref({}) // Unread count per conversation

  // Typing indicators
  const typingUsers = ref({}) // Users typing in each conversation

  // Computed
  const totalUnread = computed(() => {
    return Object.values(unreadCounts.value).reduce((sum, count) => sum + count, 0)
  })

  const sortedConversations = computed(() => {
    return [...conversations.value].sort((a, b) => {
      const aTime = new Date(a.last_message?.created_at || a.updated_at || 0)
      const bTime = new Date(b.last_message?.created_at || b.updated_at || 0)
      return bTime - aTime
    })
  })

  const activeMessages = computed(() => {
    if (!activeConversation.value) return []
    return messages.value[activeConversation.value.id] || []
  })

  // Actions
  const fetchConversations = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/messages/conversations')
      conversations.value = response.conversations || response || []

      // Update unread counts
      conversations.value.forEach(conv => {
        if (conv.unread_count) {
          unreadCounts.value[conv.id] = conv.unread_count
        }
      })
    } catch (e) {
      console.error('Failed to fetch conversations:', e)
      error.value = 'Konuşmalar yüklenemedi'
      conversations.value = []
    } finally {
      loading.value = false
    }
  }

  const fetchMessages = async (conversationId, options = {}) => {
    const { limit = 50, before = null } = options

    try {
      const params = { limit }
      if (before) params.before = before

      const response = await api.get(`/messages/conversations/${conversationId}/messages`, params)
      const newMessages = response.messages || response || []

      if (before) {
        // Prepend older messages
        messages.value[conversationId] = [
          ...newMessages,
          ...(messages.value[conversationId] || [])
        ]
      } else {
        messages.value[conversationId] = newMessages
      }

      return newMessages
    } catch (e) {
      console.error('Failed to fetch messages:', e)
      return []
    }
  }

  const openConversation = async (conversationOrUserId) => {
    // If it's a user ID, find or create conversation
    if (typeof conversationOrUserId === 'number' || typeof conversationOrUserId === 'string') {
      const userId = conversationOrUserId

      // Check if conversation exists
      let conv = conversations.value.find(c =>
        c.participant?.id === userId ||
        c.participants?.some(p => p.id === userId)
      )

      if (!conv) {
        // Create new conversation
        try {
          const response = await api.post('/messages/conversations', { user_id: userId })
          conv = response.conversation || response
          conversations.value.unshift(conv)
        } catch (e) {
          console.error('Failed to create conversation:', e)
          return null
        }
      }

      activeConversation.value = conv
    } else {
      activeConversation.value = conversationOrUserId
    }

    // Fetch messages for this conversation
    if (activeConversation.value) {
      await fetchMessages(activeConversation.value.id)
      // Mark as read
      markAsRead(activeConversation.value.id)
    }

    return activeConversation.value
  }

  const closeConversation = () => {
    activeConversation.value = null
  }

  const sendMessage = async (content, options = {}) => {
    if (!activeConversation.value || !content.trim()) return null

    const conversationId = activeConversation.value.id
    const { type = 'text', attachments = [] } = options

    // Optimistic update
    const tempId = `temp_${Date.now()}`
    const tempMessage = {
      id: tempId,
      conversation_id: conversationId,
      content: content.trim(),
      type,
      attachments,
      sender: { id: 'me' }, // Will be replaced with actual user
      created_at: new Date().toISOString(),
      status: 'sending'
    }

    if (!messages.value[conversationId]) {
      messages.value[conversationId] = []
    }
    messages.value[conversationId].push(tempMessage)

    sendingMessage.value = true

    try {
      const response = await api.post(`/messages/conversations/${conversationId}/messages`, {
        content: content.trim(),
        type,
        attachments
      })

      const sentMessage = response.message || response

      // Replace temp message with real one
      const index = messages.value[conversationId].findIndex(m => m.id === tempId)
      if (index !== -1) {
        messages.value[conversationId][index] = { ...sentMessage, status: 'sent' }
      }

      // Update conversation's last message
      const convIndex = conversations.value.findIndex(c => c.id === conversationId)
      if (convIndex !== -1) {
        conversations.value[convIndex].last_message = sentMessage
        conversations.value[convIndex].updated_at = sentMessage.created_at
      }

      return sentMessage
    } catch (e) {
      console.error('Failed to send message:', e)

      // Mark as failed
      const index = messages.value[conversationId].findIndex(m => m.id === tempId)
      if (index !== -1) {
        messages.value[conversationId][index].status = 'failed'
      }

      return null
    } finally {
      sendingMessage.value = false
    }
  }

  const markAsRead = async (conversationId) => {
    if (!conversationId || !unreadCounts.value[conversationId]) return

    unreadCounts.value[conversationId] = 0

    try {
      await api.post(`/messages/conversations/${conversationId}/read`)
    } catch (e) {
      console.error('Failed to mark as read:', e)
    }
  }

  const deleteMessage = async (messageId) => {
    if (!activeConversation.value) return false

    const conversationId = activeConversation.value.id

    try {
      await api.delete(`/messages/${messageId}`)

      // Remove from local state
      messages.value[conversationId] = messages.value[conversationId].filter(
        m => m.id !== messageId
      )

      return true
    } catch (e) {
      console.error('Failed to delete message:', e)
      return false
    }
  }

  const deleteConversation = async (conversationId) => {
    try {
      await api.delete(`/messages/conversations/${conversationId}`)

      // Remove from local state
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      delete messages.value[conversationId]
      delete unreadCounts.value[conversationId]

      if (activeConversation.value?.id === conversationId) {
        activeConversation.value = null
      }

      return true
    } catch (e) {
      console.error('Failed to delete conversation:', e)
      return false
    }
  }

  // Real-time handlers
  const handleNewMessage = (message) => {
    const conversationId = message.conversation_id

    // Add to messages if conversation is loaded
    if (messages.value[conversationId]) {
      // Check if message already exists
      if (!messages.value[conversationId].find(m => m.id === message.id)) {
        messages.value[conversationId].push(message)
      }
    }

    // Update conversation
    const convIndex = conversations.value.findIndex(c => c.id === conversationId)
    if (convIndex !== -1) {
      conversations.value[convIndex].last_message = message
      conversations.value[convIndex].updated_at = message.created_at

      // Increment unread if not active conversation
      if (activeConversation.value?.id !== conversationId) {
        unreadCounts.value[conversationId] = (unreadCounts.value[conversationId] || 0) + 1
      }
    }
  }

  const handleTypingStart = (data) => {
    const { conversation_id, user } = data
    if (!typingUsers.value[conversation_id]) {
      typingUsers.value[conversation_id] = []
    }
    if (!typingUsers.value[conversation_id].find(u => u.id === user.id)) {
      typingUsers.value[conversation_id].push(user)
    }

    // Auto-clear after 3 seconds
    setTimeout(() => {
      handleTypingStop({ conversation_id, user })
    }, 3000)
  }

  const handleTypingStop = (data) => {
    const { conversation_id, user } = data
    if (typingUsers.value[conversation_id]) {
      typingUsers.value[conversation_id] = typingUsers.value[conversation_id].filter(
        u => u.id !== user.id
      )
    }
  }

  const sendTypingIndicator = async () => {
    if (!activeConversation.value) return

    try {
      await api.post(`/messages/conversations/${activeConversation.value.id}/typing`)
    } catch (e) {
      // Ignore typing indicator errors
    }
  }

  // Initialize
  const init = async () => {
    await fetchConversations()
  }

  // Reset
  const reset = () => {
    conversations.value = []
    activeConversation.value = null
    messages.value = {}
    unreadCounts.value = {}
    typingUsers.value = {}
    error.value = null
  }

  return {
    // State
    conversations,
    activeConversation,
    messages,
    loading,
    sendingMessage,
    error,
    unreadCounts,
    typingUsers,

    // Computed
    totalUnread,
    sortedConversations,
    activeMessages,

    // Actions
    fetchConversations,
    fetchMessages,
    openConversation,
    closeConversation,
    sendMessage,
    markAsRead,
    deleteMessage,
    deleteConversation,
    handleNewMessage,
    handleTypingStart,
    handleTypingStop,
    sendTypingIndicator,
    init,
    reset
  }
})
