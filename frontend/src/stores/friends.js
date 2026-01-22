/**
 * Friends Store - Arkadaşlık Sistemi
 * Friend requests, friend list, online status
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useFriendsStore = defineStore('friends', () => {
  // State
  const friends = ref([])
  const pendingRequests = ref([]) // Requests received
  const sentRequests = ref([]) // Requests sent
  const blockedUsers = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const onlineFriends = computed(() =>
    friends.value.filter(f => f.is_online)
  )

  const offlineFriends = computed(() =>
    friends.value.filter(f => !f.is_online)
  )

  const friendCount = computed(() => friends.value.length)

  const pendingCount = computed(() => pendingRequests.value.length)

  const hasPendingRequests = computed(() => pendingRequests.value.length > 0)

  // Check if user is friend
  const isFriend = (userId) => {
    return friends.value.some(f => f.id === userId || f.user_id === userId)
  }

  // Check if request is pending
  const isPending = (userId) => {
    return sentRequests.value.some(r => r.to_user_id === userId) ||
           pendingRequests.value.some(r => r.from_user_id === userId)
  }

  // Check if user is blocked
  const isBlocked = (userId) => {
    return blockedUsers.value.some(b => b.id === userId || b.user_id === userId)
  }

  // Actions
  const fetchFriends = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/friends')
      friends.value = response.friends || response || []
    } catch (e) {
      console.error('Failed to fetch friends:', e)
      error.value = 'Arkadaş listesi yüklenemedi'
      friends.value = []
    } finally {
      loading.value = false
    }
  }

  const fetchPendingRequests = async () => {
    try {
      const response = await api.get('/friends/requests')
      pendingRequests.value = response.received || response.pending || []
      sentRequests.value = response.sent || []
    } catch (e) {
      console.error('Failed to fetch friend requests:', e)
      pendingRequests.value = []
      sentRequests.value = []
    }
  }

  const fetchBlockedUsers = async () => {
    try {
      const response = await api.get('/friends/blocked')
      blockedUsers.value = response.blocked || response || []
    } catch (e) {
      console.error('Failed to fetch blocked users:', e)
      blockedUsers.value = []
    }
  }

  const sendFriendRequest = async (userId) => {
    try {
      await api.post('/friends/request', { user_id: userId })
      // Add to sent requests
      sentRequests.value.push({ to_user_id: userId, created_at: new Date().toISOString() })
      return { success: true, message: 'Arkadaşlık isteği gönderildi' }
    } catch (e) {
      console.error('Failed to send friend request:', e)
      return { success: false, message: e.message || 'İstek gönderilemedi' }
    }
  }

  const acceptFriendRequest = async (requestId, fromUserId) => {
    try {
      const response = await api.post(`/friends/request/${requestId}/accept`)
      // Remove from pending
      pendingRequests.value = pendingRequests.value.filter(r => r.id !== requestId)
      // Add to friends
      if (response.friend) {
        friends.value.push(response.friend)
      }
      return { success: true, message: 'Arkadaşlık isteği kabul edildi' }
    } catch (e) {
      console.error('Failed to accept friend request:', e)
      return { success: false, message: e.message || 'İstek kabul edilemedi' }
    }
  }

  const rejectFriendRequest = async (requestId) => {
    try {
      await api.post(`/friends/request/${requestId}/reject`)
      // Remove from pending
      pendingRequests.value = pendingRequests.value.filter(r => r.id !== requestId)
      return { success: true, message: 'Arkadaşlık isteği reddedildi' }
    } catch (e) {
      console.error('Failed to reject friend request:', e)
      return { success: false, message: e.message || 'İstek reddedilemedi' }
    }
  }

  const cancelFriendRequest = async (userId) => {
    try {
      await api.delete(`/friends/request/${userId}`)
      sentRequests.value = sentRequests.value.filter(r => r.to_user_id !== userId)
      return { success: true, message: 'Arkadaşlık isteği iptal edildi' }
    } catch (e) {
      console.error('Failed to cancel friend request:', e)
      return { success: false, message: e.message || 'İstek iptal edilemedi' }
    }
  }

  const removeFriend = async (userId) => {
    try {
      await api.delete(`/friends/${userId}`)
      friends.value = friends.value.filter(f => f.id !== userId && f.user_id !== userId)
      return { success: true, message: 'Arkadaşlıktan çıkarıldı' }
    } catch (e) {
      console.error('Failed to remove friend:', e)
      return { success: false, message: e.message || 'Arkadaş çıkarılamadı' }
    }
  }

  const blockUser = async (userId) => {
    try {
      await api.post('/friends/block', { user_id: userId })
      // Remove from friends if exists
      friends.value = friends.value.filter(f => f.id !== userId && f.user_id !== userId)
      // Add to blocked
      blockedUsers.value.push({ user_id: userId, blocked_at: new Date().toISOString() })
      return { success: true, message: 'Kullanıcı engellendi' }
    } catch (e) {
      console.error('Failed to block user:', e)
      return { success: false, message: e.message || 'Kullanıcı engellenemedi' }
    }
  }

  const unblockUser = async (userId) => {
    try {
      await api.delete(`/friends/block/${userId}`)
      blockedUsers.value = blockedUsers.value.filter(b => b.id !== userId && b.user_id !== userId)
      return { success: true, message: 'Engel kaldırıldı' }
    } catch (e) {
      console.error('Failed to unblock user:', e)
      return { success: false, message: e.message || 'Engel kaldırılamadı' }
    }
  }

  // Update friend's online status (called from WebSocket)
  const updateFriendStatus = (userId, isOnline, lastSeen = null) => {
    const friend = friends.value.find(f => f.id === userId || f.user_id === userId)
    if (friend) {
      friend.is_online = isOnline
      if (lastSeen) friend.last_seen = lastSeen
    }
  }

  // Initialize
  const init = async () => {
    await Promise.all([
      fetchFriends(),
      fetchPendingRequests(),
      fetchBlockedUsers()
    ])
  }

  // Reset state
  const reset = () => {
    friends.value = []
    pendingRequests.value = []
    sentRequests.value = []
    blockedUsers.value = []
    loading.value = false
    error.value = null
  }

  return {
    // State
    friends,
    pendingRequests,
    sentRequests,
    blockedUsers,
    loading,
    error,

    // Computed
    onlineFriends,
    offlineFriends,
    friendCount,
    pendingCount,
    hasPendingRequests,

    // Methods
    isFriend,
    isPending,
    isBlocked,
    fetchFriends,
    fetchPendingRequests,
    fetchBlockedUsers,
    sendFriendRequest,
    acceptFriendRequest,
    rejectFriendRequest,
    cancelFriendRequest,
    removeFriend,
    blockUser,
    unblockUser,
    updateFriendStatus,
    init,
    reset
  }
})
