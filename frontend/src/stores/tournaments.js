/**
 * Tournaments Store - Turnuva Sistemi
 * Manage gaming tournaments, brackets, and registrations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

// Tournament Status
export const TournamentStatus = {
  UPCOMING: 'upcoming',
  REGISTRATION: 'registration',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
}

// Tournament Format
export const TournamentFormat = {
  SINGLE_ELIMINATION: 'single_elimination',
  DOUBLE_ELIMINATION: 'double_elimination',
  ROUND_ROBIN: 'round_robin',
  SWISS: 'swiss'
}

// Game Types
export const GameType = {
  CS_16: 'cs16',
  HALF_LIFE: 'halflife',
  OTHER: 'other'
}

export const useTournamentsStore = defineStore('tournaments', () => {
  // State
  const tournaments = ref([])
  const currentTournament = ref(null)
  const myTournaments = ref([]) // Tournaments user is participating in
  const loading = ref(false)
  const error = ref(null)

  // Filters
  const filters = ref({
    status: null,
    game: null,
    search: ''
  })

  // Pagination
  const pagination = ref({
    page: 1,
    limit: 12,
    total: 0,
    hasMore: true
  })

  // Computed
  const upcomingTournaments = computed(() => {
    return tournaments.value.filter(t =>
      t.status === TournamentStatus.UPCOMING ||
      t.status === TournamentStatus.REGISTRATION
    )
  })

  const activeTournaments = computed(() => {
    return tournaments.value.filter(t => t.status === TournamentStatus.IN_PROGRESS)
  })

  const completedTournaments = computed(() => {
    return tournaments.value.filter(t => t.status === TournamentStatus.COMPLETED)
  })

  const filteredTournaments = computed(() => {
    let result = [...tournaments.value]

    if (filters.value.status) {
      result = result.filter(t => t.status === filters.value.status)
    }

    if (filters.value.game) {
      result = result.filter(t => t.game_type === filters.value.game)
    }

    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      result = result.filter(t =>
        t.name.toLowerCase().includes(search) ||
        t.description?.toLowerCase().includes(search)
      )
    }

    return result
  })

  // Actions
  const fetchTournaments = async (options = {}) => {
    const { reset = false } = options

    if (reset) {
      pagination.value.page = 1
      tournaments.value = []
    }

    loading.value = true
    error.value = null

    try {
      const params = {
        page: pagination.value.page,
        limit: pagination.value.limit,
        ...filters.value
      }

      const response = await api.get('/tournaments', params)
      const newTournaments = response.tournaments || response.data || response || []

      if (reset) {
        tournaments.value = newTournaments
      } else {
        tournaments.value = [...tournaments.value, ...newTournaments]
      }

      pagination.value.total = response.total || newTournaments.length
      pagination.value.hasMore = newTournaments.length >= pagination.value.limit

      return newTournaments
    } catch (e) {
      console.error('Failed to fetch tournaments:', e)
      error.value = 'Turnuvalar yüklenemedi'
      return []
    } finally {
      loading.value = false
    }
  }

  const fetchTournament = async (id) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/tournaments/${id}`)
      currentTournament.value = response.tournament || response
      return currentTournament.value
    } catch (e) {
      console.error('Failed to fetch tournament:', e)
      error.value = 'Turnuva bulunamadı'
      return null
    } finally {
      loading.value = false
    }
  }

  const fetchMyTournaments = async () => {
    try {
      const response = await api.get('/tournaments/me')
      myTournaments.value = response.tournaments || response || []
      return myTournaments.value
    } catch (e) {
      console.error('Failed to fetch my tournaments:', e)
      myTournaments.value = []
      return []
    }
  }

  const loadMore = async () => {
    if (!pagination.value.hasMore || loading.value) return

    pagination.value.page++
    await fetchTournaments()
  }

  const registerForTournament = async (tournamentId, teamData = null) => {
    try {
      const payload = teamData ? { team: teamData } : {}
      const response = await api.post(`/tournaments/${tournamentId}/register`, payload)

      // Update local state
      const tournament = tournaments.value.find(t => t.id === tournamentId)
      if (tournament) {
        tournament.participants_count = (tournament.participants_count || 0) + 1
        tournament.is_registered = true
      }

      if (currentTournament.value?.id === tournamentId) {
        currentTournament.value.is_registered = true
        currentTournament.value.participants_count = (currentTournament.value.participants_count || 0) + 1
      }

      return { success: true, message: 'Turnuvaya kayıt başarılı!' }
    } catch (e) {
      console.error('Failed to register:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Kayıt başarısız oldu'
      }
    }
  }

  const unregisterFromTournament = async (tournamentId) => {
    try {
      await api.delete(`/tournaments/${tournamentId}/register`)

      // Update local state
      const tournament = tournaments.value.find(t => t.id === tournamentId)
      if (tournament) {
        tournament.participants_count = Math.max(0, (tournament.participants_count || 1) - 1)
        tournament.is_registered = false
      }

      if (currentTournament.value?.id === tournamentId) {
        currentTournament.value.is_registered = false
        currentTournament.value.participants_count = Math.max(0, (currentTournament.value.participants_count || 1) - 1)
      }

      return { success: true, message: 'Turnuva kaydı iptal edildi' }
    } catch (e) {
      console.error('Failed to unregister:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Kayıt iptali başarısız oldu'
      }
    }
  }

  const fetchBracket = async (tournamentId) => {
    try {
      const response = await api.get(`/tournaments/${tournamentId}/bracket`)
      return response.bracket || response
    } catch (e) {
      console.error('Failed to fetch bracket:', e)
      return null
    }
  }

  const fetchMatches = async (tournamentId, options = {}) => {
    try {
      const response = await api.get(`/tournaments/${tournamentId}/matches`, options)
      return response.matches || response || []
    } catch (e) {
      console.error('Failed to fetch matches:', e)
      return []
    }
  }

  const fetchParticipants = async (tournamentId) => {
    try {
      const response = await api.get(`/tournaments/${tournamentId}/participants`)
      return response.participants || response || []
    } catch (e) {
      console.error('Failed to fetch participants:', e)
      return []
    }
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    fetchTournaments({ reset: true })
  }

  const clearFilters = () => {
    filters.value = {
      status: null,
      game: null,
      search: ''
    }
    fetchTournaments({ reset: true })
  }

  // Initialize
  const init = async () => {
    await Promise.all([
      fetchTournaments({ reset: true }),
      fetchMyTournaments()
    ])
  }

  // Reset
  const reset = () => {
    tournaments.value = []
    currentTournament.value = null
    myTournaments.value = []
    filters.value = { status: null, game: null, search: '' }
    pagination.value = { page: 1, limit: 12, total: 0, hasMore: true }
    error.value = null
  }

  // Helper functions
  const getStatusLabel = (status) => {
    const labels = {
      [TournamentStatus.UPCOMING]: 'Yaklaşan',
      [TournamentStatus.REGISTRATION]: 'Kayıt Açık',
      [TournamentStatus.IN_PROGRESS]: 'Devam Ediyor',
      [TournamentStatus.COMPLETED]: 'Tamamlandı',
      [TournamentStatus.CANCELLED]: 'İptal Edildi'
    }
    return labels[status] || status
  }

  const getStatusColor = (status) => {
    const colors = {
      [TournamentStatus.UPCOMING]: '#3b82f6',
      [TournamentStatus.REGISTRATION]: '#22c55e',
      [TournamentStatus.IN_PROGRESS]: '#f97316',
      [TournamentStatus.COMPLETED]: '#6b7280',
      [TournamentStatus.CANCELLED]: '#ef4444'
    }
    return colors[status] || '#6b7280'
  }

  const getFormatLabel = (format) => {
    const labels = {
      [TournamentFormat.SINGLE_ELIMINATION]: 'Tek Eleme',
      [TournamentFormat.DOUBLE_ELIMINATION]: 'Çift Eleme',
      [TournamentFormat.ROUND_ROBIN]: 'Lig Usulü',
      [TournamentFormat.SWISS]: 'İsviçre Sistemi'
    }
    return labels[format] || format
  }

  const getGameLabel = (game) => {
    const labels = {
      [GameType.CS_16]: 'Counter-Strike 1.6',
      [GameType.HALF_LIFE]: 'Half-Life',
      [GameType.OTHER]: 'Diğer'
    }
    return labels[game] || game
  }

  return {
    // State
    tournaments,
    currentTournament,
    myTournaments,
    loading,
    error,
    filters,
    pagination,

    // Computed
    upcomingTournaments,
    activeTournaments,
    completedTournaments,
    filteredTournaments,

    // Actions
    fetchTournaments,
    fetchTournament,
    fetchMyTournaments,
    loadMore,
    registerForTournament,
    unregisterFromTournament,
    fetchBracket,
    fetchMatches,
    fetchParticipants,
    setFilters,
    clearFilters,
    init,
    reset,

    // Helpers
    getStatusLabel,
    getStatusColor,
    getFormatLabel,
    getGameLabel,

    // Constants
    TournamentStatus,
    TournamentFormat,
    GameType
  }
})
