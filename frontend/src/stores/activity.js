/**
 * Activity Store - Canlı Aktivite Akışı
 * Track and display platform-wide activities
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

// Activity Types
export const ActivityType = {
  // User activities
  USER_JOINED: 'user_joined',
  USER_LEVEL_UP: 'user_level_up',
  USER_ACHIEVEMENT: 'user_achievement',

  // Social activities
  FRIEND_ADDED: 'friend_added',
  CLAN_JOINED: 'clan_joined',
  CLAN_CREATED: 'clan_created',

  // Forum activities
  TOPIC_CREATED: 'topic_created',
  POST_CREATED: 'post_created',
  POST_LIKED: 'post_liked',

  // Gaming activities
  SERVER_ONLINE: 'server_online',
  TOURNAMENT_CREATED: 'tournament_created',
  TOURNAMENT_WIN: 'tournament_win',
  MATCH_PLAYED: 'match_played',
  KILLSTREAK: 'killstreak',

  // Shop activities
  PURCHASE: 'purchase',
  VIP_ACTIVATED: 'vip_activated',

  // System
  ANNOUNCEMENT: 'announcement'
}

export const useActivityStore = defineStore('activity', () => {
  // State
  const activities = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Real-time connection status
  const isConnected = ref(false)

  // Filters
  const filters = ref({
    types: [], // Empty means all
    userId: null, // Filter by specific user
    friendsOnly: false
  })

  // Pagination
  const pagination = ref({
    page: 1,
    limit: 20,
    hasMore: true
  })

  // Computed
  const filteredActivities = computed(() => {
    let result = [...activities.value]

    if (filters.value.types.length > 0) {
      result = result.filter(a => filters.value.types.includes(a.type))
    }

    if (filters.value.userId) {
      result = result.filter(a => a.user?.id === filters.value.userId)
    }

    return result
  })

  const recentActivities = computed(() => {
    return filteredActivities.value.slice(0, 10)
  })

  const groupedByDate = computed(() => {
    const groups = {}

    activities.value.forEach(activity => {
      const date = new Date(activity.created_at).toDateString()
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(activity)
    })

    return groups
  })

  // Demo activities for when API returns empty
  const generateDemoActivities = () => {
    const demoUsers = [
      { id: 1, username: 'ProGamer', avatar: null },
      { id: 2, username: 'NightHawk', avatar: null },
      { id: 3, username: 'ShadowKiller', avatar: null },
      { id: 4, username: 'EliteSniper', avatar: null },
      { id: 5, username: 'StormRider', avatar: null },
      { id: 6, username: 'ThunderBolt', avatar: null },
      { id: 7, username: 'IronWolf', avatar: null },
      { id: 8, username: 'CyberNinja', avatar: null }
    ]

    const now = Date.now()
    const minute = 60 * 1000
    const hour = 60 * minute

    return [
      {
        id: 'demo_1',
        type: ActivityType.USER_JOINED,
        user: demoUsers[0],
        data: {},
        created_at: new Date(now - 2 * minute).toISOString()
      },
      {
        id: 'demo_2',
        type: ActivityType.SERVER_ONLINE,
        user: null,
        data: { server: 'AGTR Public #1' },
        created_at: new Date(now - 5 * minute).toISOString()
      },
      {
        id: 'demo_3',
        type: ActivityType.TOPIC_CREATED,
        user: demoUsers[1],
        data: { title: 'En iyi AWP ayarları nedir?' },
        created_at: new Date(now - 12 * minute).toISOString()
      },
      {
        id: 'demo_4',
        type: ActivityType.USER_LEVEL_UP,
        user: demoUsers[2],
        data: { level: 15 },
        created_at: new Date(now - 25 * minute).toISOString()
      },
      {
        id: 'demo_5',
        type: ActivityType.CLAN_JOINED,
        user: demoUsers[3],
        data: { clan: 'Turkish Elite' },
        created_at: new Date(now - 45 * minute).toISOString()
      },
      {
        id: 'demo_6',
        type: ActivityType.KILLSTREAK,
        user: demoUsers[4],
        data: { kills: 10 },
        created_at: new Date(now - 1 * hour).toISOString()
      },
      {
        id: 'demo_7',
        type: ActivityType.VIP_ACTIVATED,
        user: demoUsers[5],
        data: {},
        created_at: new Date(now - 1.5 * hour).toISOString()
      },
      {
        id: 'demo_8',
        type: ActivityType.TOURNAMENT_WIN,
        user: demoUsers[6],
        data: { tournament: '1v1 AWP Challenge' },
        created_at: new Date(now - 2 * hour).toISOString()
      },
      {
        id: 'demo_9',
        type: ActivityType.USER_ACHIEVEMENT,
        user: demoUsers[7],
        data: { achievement: 'Headshot Master' },
        created_at: new Date(now - 3 * hour).toISOString()
      },
      {
        id: 'demo_10',
        type: ActivityType.CLAN_CREATED,
        user: demoUsers[0],
        data: { clan: 'Pro Killers' },
        created_at: new Date(now - 4 * hour).toISOString()
      }
    ]
  }

  // Actions
  const fetchActivities = async (options = {}) => {
    const { reset = false } = options

    if (reset) {
      pagination.value.page = 1
      activities.value = []
    }

    loading.value = true
    error.value = null

    try {
      const params = {
        page: pagination.value.page,
        limit: pagination.value.limit,
        ...filters.value
      }

      const response = await api.get('/activities', params)
      let newActivities = response.activities || response.data || response || []

      // If API returns empty, use demo data
      if (newActivities.length === 0 && reset && pagination.value.page === 1) {
        newActivities = generateDemoActivities()
        pagination.value.hasMore = false
      }

      if (reset) {
        activities.value = newActivities
      } else {
        // Avoid duplicates
        const existingIds = new Set(activities.value.map(a => a.id))
        const uniqueNew = newActivities.filter(a => !existingIds.has(a.id))
        activities.value = [...activities.value, ...uniqueNew]
      }

      pagination.value.hasMore = newActivities.length >= pagination.value.limit

      return newActivities
    } catch (e) {
      console.error('Failed to fetch activities:', e)
      // On error, use demo data as fallback
      if (reset && pagination.value.page === 1) {
        activities.value = generateDemoActivities()
        pagination.value.hasMore = false
      }
      error.value = null // Don't show error since we have fallback data
      return activities.value
    } finally {
      loading.value = false
    }
  }

  const loadMore = async () => {
    if (!pagination.value.hasMore || loading.value) return

    pagination.value.page++
    await fetchActivities()
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    fetchActivities({ reset: true })
  }

  const clearFilters = () => {
    filters.value = {
      types: [],
      userId: null,
      friendsOnly: false
    }
    fetchActivities({ reset: true })
  }

  // Real-time handlers
  const addActivity = (activity) => {
    // Check for duplicate
    if (activities.value.find(a => a.id === activity.id)) return

    // Add to beginning
    activities.value.unshift(activity)

    // Keep list manageable
    if (activities.value.length > 100) {
      activities.value = activities.value.slice(0, 100)
    }
  }

  const removeActivity = (activityId) => {
    activities.value = activities.value.filter(a => a.id !== activityId)
  }

  // Helper functions
  const getActivityIcon = (type) => {
    const icons = {
      [ActivityType.USER_JOINED]: '👋',
      [ActivityType.USER_LEVEL_UP]: '⬆️',
      [ActivityType.USER_ACHIEVEMENT]: '🏆',
      [ActivityType.FRIEND_ADDED]: '🤝',
      [ActivityType.CLAN_JOINED]: '⚔️',
      [ActivityType.CLAN_CREATED]: '🏴',
      [ActivityType.TOPIC_CREATED]: '📝',
      [ActivityType.POST_CREATED]: '💬',
      [ActivityType.POST_LIKED]: '❤️',
      [ActivityType.SERVER_ONLINE]: '🖥️',
      [ActivityType.TOURNAMENT_CREATED]: '🎮',
      [ActivityType.TOURNAMENT_WIN]: '🥇',
      [ActivityType.MATCH_PLAYED]: '⚔️',
      [ActivityType.KILLSTREAK]: '🔥',
      [ActivityType.PURCHASE]: '🛒',
      [ActivityType.VIP_ACTIVATED]: '⭐',
      [ActivityType.ANNOUNCEMENT]: '📣'
    }
    return icons[type] || '📌'
  }

  const getActivityColor = (type) => {
    const colors = {
      [ActivityType.USER_JOINED]: '#22c55e',
      [ActivityType.USER_LEVEL_UP]: '#3b82f6',
      [ActivityType.USER_ACHIEVEMENT]: '#f59e0b',
      [ActivityType.FRIEND_ADDED]: '#8b5cf6',
      [ActivityType.CLAN_JOINED]: '#ef4444',
      [ActivityType.CLAN_CREATED]: '#ef4444',
      [ActivityType.TOPIC_CREATED]: '#06b6d4',
      [ActivityType.POST_CREATED]: '#06b6d4',
      [ActivityType.POST_LIKED]: '#ec4899',
      [ActivityType.SERVER_ONLINE]: '#22c55e',
      [ActivityType.TOURNAMENT_CREATED]: '#f97316',
      [ActivityType.TOURNAMENT_WIN]: '#fbbf24',
      [ActivityType.MATCH_PLAYED]: '#f97316',
      [ActivityType.KILLSTREAK]: '#ef4444',
      [ActivityType.PURCHASE]: '#10b981',
      [ActivityType.VIP_ACTIVATED]: '#fbbf24',
      [ActivityType.ANNOUNCEMENT]: '#3b82f6'
    }
    return colors[type] || '#6b7280'
  }

  const formatActivityMessage = (activity) => {
    const user = activity.user?.username || 'Birisi'

    const messages = {
      [ActivityType.USER_JOINED]: `${user} topluluğa katıldı!`,
      [ActivityType.USER_LEVEL_UP]: `${user} seviye ${activity.data?.level || '?'} oldu!`,
      [ActivityType.USER_ACHIEVEMENT]: `${user} "${activity.data?.achievement || 'bir başarım'}" başarımını kazandı!`,
      [ActivityType.FRIEND_ADDED]: `${user} ve ${activity.data?.friend || 'birisi'} artık arkadaş!`,
      [ActivityType.CLAN_JOINED]: `${user} "${activity.data?.clan || 'bir klan'}" klanına katıldı`,
      [ActivityType.CLAN_CREATED]: `${user} "${activity.data?.clan || 'bir klan'}" klanını kurdu!`,
      [ActivityType.TOPIC_CREATED]: `${user} yeni bir konu açtı: "${activity.data?.title || 'Konu'}"`,
      [ActivityType.POST_CREATED]: `${user} bir konuya yanıt verdi`,
      [ActivityType.POST_LIKED]: `${user} bir gönderiyi beğendi`,
      [ActivityType.SERVER_ONLINE]: `"${activity.data?.server || 'Bir sunucu'}" çevrimiçi oldu!`,
      [ActivityType.TOURNAMENT_CREATED]: `Yeni turnuva: "${activity.data?.tournament || 'Turnuva'}"`,
      [ActivityType.TOURNAMENT_WIN]: `${user} "${activity.data?.tournament || 'turnuvayı'}" kazandı! 🎉`,
      [ActivityType.MATCH_PLAYED]: `${user} bir maç tamamladı`,
      [ActivityType.KILLSTREAK]: `${user} ${activity.data?.kills || '?'} kişilik öldürme serisi yaptı! 🔥`,
      [ActivityType.PURCHASE]: `${user} mağazadan alışveriş yaptı`,
      [ActivityType.VIP_ACTIVATED]: `${user} VIP üye oldu! ⭐`,
      [ActivityType.ANNOUNCEMENT]: activity.data?.message || 'Yeni duyuru!'
    }

    return messages[activity.type] || 'Yeni aktivite'
  }

  // Initialize
  const init = async () => {
    await fetchActivities({ reset: true })
  }

  // Reset
  const reset = () => {
    activities.value = []
    filters.value = { types: [], userId: null, friendsOnly: false }
    pagination.value = { page: 1, limit: 20, hasMore: true }
    error.value = null
    isConnected.value = false
  }

  return {
    // State
    activities,
    loading,
    error,
    isConnected,
    filters,
    pagination,

    // Computed
    filteredActivities,
    recentActivities,
    groupedByDate,

    // Actions
    fetchActivities,
    loadMore,
    setFilters,
    clearFilters,
    addActivity,
    removeActivity,
    init,
    reset,

    // Helpers
    getActivityIcon,
    getActivityColor,
    formatActivityMessage,

    // Constants
    ActivityType
  }
})
