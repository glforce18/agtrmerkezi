/**
 * Clans Store - Klan/Takım Sistemi
 * Manage gaming clans, members, and clan activities
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

// Member Roles
export const ClanRole = {
  LEADER: 'leader',
  OFFICER: 'officer',
  MEMBER: 'member'
}

// Clan Status
export const ClanStatus = {
  ACTIVE: 'active',
  RECRUITING: 'recruiting',
  CLOSED: 'closed',
  INACTIVE: 'inactive'
}

export const useClansStore = defineStore('clans', () => {
  // State
  const clans = ref([])
  const myClan = ref(null)
  const currentClan = ref(null) // For viewing a specific clan
  const clanMembers = ref([])
  const clanInvites = ref([]) // Invites received
  const clanApplications = ref([]) // Applications to join (for leaders)
  const myApplications = ref([]) // My pending applications
  const loading = ref(false)
  const error = ref(null)

  // Search/filter
  const searchQuery = ref('')
  const filters = ref({
    status: null,
    minMembers: null,
    maxMembers: null
  })

  // Pagination
  const pagination = ref({
    page: 1,
    limit: 12,
    total: 0,
    hasMore: true
  })

  // Computed
  const isInClan = computed(() => !!myClan.value)

  const myRole = computed(() => {
    if (!myClan.value) return null
    return myClan.value.my_role || myClan.value.role
  })

  const isLeader = computed(() => myRole.value === ClanRole.LEADER)
  const isOfficer = computed(() => myRole.value === ClanRole.OFFICER || isLeader.value)

  const filteredClans = computed(() => {
    let result = [...clans.value]

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(c =>
        c.name.toLowerCase().includes(query) ||
        c.tag?.toLowerCase().includes(query)
      )
    }

    if (filters.value.status) {
      result = result.filter(c => c.status === filters.value.status)
    }

    return result
  })

  const recruitingClans = computed(() => {
    return clans.value.filter(c => c.status === ClanStatus.RECRUITING)
  })

  // Actions
  const fetchClans = async (options = {}) => {
    const { reset = false } = options

    if (reset) {
      pagination.value.page = 1
      clans.value = []
    }

    loading.value = true
    error.value = null

    try {
      const params = {
        page: pagination.value.page,
        limit: pagination.value.limit,
        q: searchQuery.value || undefined,
        ...filters.value
      }

      const response = await api.get('/social/clans', { params })
      const newClans = response.clans || response.data || response || []

      if (reset) {
        clans.value = newClans
      } else {
        clans.value = [...clans.value, ...newClans]
      }

      pagination.value.total = response.total || newClans.length
      pagination.value.hasMore = newClans.length >= pagination.value.limit

      return newClans
    } catch (e) {
      console.error('Failed to fetch clans:', e)
      error.value = 'Klanlar yüklenemedi'
      return []
    } finally {
      loading.value = false
    }
  }

  const fetchClan = async (clanId) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/social/clans/${clanId}`)
      currentClan.value = response.clan || response
      return currentClan.value
    } catch (e) {
      console.error('Failed to fetch clan:', e)
      error.value = 'Klan bulunamadı'
      return null
    } finally {
      loading.value = false
    }
  }

  const fetchMyClan = async () => {
    try {
      const response = await api.get('/social/clans/me')
      myClan.value = response.clan || response
      return myClan.value
    } catch (e) {
      // User might not be in a clan
      myClan.value = null
      return null
    }
  }

  const fetchClanMembers = async (clanId) => {
    try {
      const response = await api.get(`/social/clans/${clanId}/members`)
      clanMembers.value = response.members || response || []
      return clanMembers.value
    } catch (e) {
      console.error('Failed to fetch clan members:', e)
      clanMembers.value = []
      return []
    }
  }

  const fetchMyInvites = async () => {
    try {
      const response = await api.get('/social/clans/invites')
      clanInvites.value = response.invites || response || []
      return clanInvites.value
    } catch (e) {
      console.error('Failed to fetch invites:', e)
      clanInvites.value = []
      return []
    }
  }

  const fetchApplications = async () => {
    if (!myClan.value || !isOfficer.value) return []

    try {
      const response = await api.get(`/social/clans/${myClan.value.id}/applications`)
      clanApplications.value = response.applications || response || []
      return clanApplications.value
    } catch (e) {
      console.error('Failed to fetch applications:', e)
      clanApplications.value = []
      return []
    }
  }

  const fetchMyApplications = async () => {
    try {
      const response = await api.get('/social/clans/my-applications')
      myApplications.value = response.applications || response || []
      return myApplications.value
    } catch (e) {
      console.error('Failed to fetch my applications:', e)
      myApplications.value = []
      return []
    }
  }

  const loadMore = async () => {
    if (!pagination.value.hasMore || loading.value) return

    pagination.value.page++
    await fetchClans()
  }

  // Clan Management
  const createClan = async (clanData) => {
    try {
      const response = await api.post('/social/clans', clanData)
      const newClan = response.clan || response

      myClan.value = newClan
      clans.value.unshift(newClan)

      return { success: true, clan: newClan, message: 'Klan başarıyla oluşturuldu!' }
    } catch (e) {
      console.error('Failed to create clan:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Klan oluşturulamadı'
      }
    }
  }

  const updateClan = async (clanId, clanData) => {
    try {
      const response = await api.put(`/social/clans/${clanId}`, clanData)
      const updatedClan = response.clan || response

      // Update local state
      if (myClan.value?.id === clanId) {
        myClan.value = { ...myClan.value, ...updatedClan }
      }
      if (currentClan.value?.id === clanId) {
        currentClan.value = { ...currentClan.value, ...updatedClan }
      }

      const index = clans.value.findIndex(c => c.id === clanId)
      if (index !== -1) {
        clans.value[index] = { ...clans.value[index], ...updatedClan }
      }

      return { success: true, clan: updatedClan, message: 'Klan güncellendi!' }
    } catch (e) {
      console.error('Failed to update clan:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Klan güncellenemedi'
      }
    }
  }

  const deleteClan = async (clanId) => {
    try {
      await api.delete(`/social/clans/${clanId}`)

      // Update local state
      if (myClan.value?.id === clanId) {
        myClan.value = null
      }
      clans.value = clans.value.filter(c => c.id !== clanId)

      return { success: true, message: 'Klan silindi!' }
    } catch (e) {
      console.error('Failed to delete clan:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Klan silinemedi'
      }
    }
  }

  // Membership
  const applyToClan = async (clanId, message = '') => {
    try {
      await api.post(`/social/clans/${clanId}/apply`, { message })
      return { success: true, message: 'Başvurunuz gönderildi!' }
    } catch (e) {
      console.error('Failed to apply:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Başvuru gönderilemedi'
      }
    }
  }

  const cancelApplication = async (clanId) => {
    try {
      await api.delete(`/social/clans/${clanId}/apply`)
      return { success: true, message: 'Başvuru iptal edildi' }
    } catch (e) {
      console.error('Failed to cancel application:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Başvuru iptal edilemedi'
      }
    }
  }

  const acceptApplication = async (applicationId) => {
    try {
      await api.post(`/social/clans/applications/${applicationId}/accept`)

      clanApplications.value = clanApplications.value.filter(a => a.id !== applicationId)

      return { success: true, message: 'Üye kabul edildi!' }
    } catch (e) {
      console.error('Failed to accept application:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Üye kabul edilemedi'
      }
    }
  }

  const rejectApplication = async (applicationId) => {
    try {
      await api.post(`/social/clans/applications/${applicationId}/reject`)

      clanApplications.value = clanApplications.value.filter(a => a.id !== applicationId)

      return { success: true, message: 'Başvuru reddedildi' }
    } catch (e) {
      console.error('Failed to reject application:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Başvuru reddedilemedi'
      }
    }
  }

  const inviteUser = async (clanId, userId) => {
    try {
      await api.post(`/social/clans/${clanId}/invite`, { user_id: userId })
      return { success: true, message: 'Davet gönderildi!' }
    } catch (e) {
      console.error('Failed to invite user:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Davet gönderilemedi'
      }
    }
  }

  const acceptInvite = async (inviteId) => {
    try {
      const response = await api.post(`/social/clans/invites/${inviteId}/accept`)
      myClan.value = response.clan || response

      clanInvites.value = clanInvites.value.filter(i => i.id !== inviteId)

      return { success: true, message: 'Klana katıldınız!' }
    } catch (e) {
      console.error('Failed to accept invite:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Davet kabul edilemedi'
      }
    }
  }

  const declineInvite = async (inviteId) => {
    try {
      await api.post(`/social/clans/invites/${inviteId}/decline`)

      clanInvites.value = clanInvites.value.filter(i => i.id !== inviteId)

      return { success: true, message: 'Davet reddedildi' }
    } catch (e) {
      console.error('Failed to decline invite:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Davet reddedilemedi'
      }
    }
  }

  const leaveClan = async () => {
    if (!myClan.value) return { success: false, message: 'Bir klana üye değilsiniz' }

    try {
      await api.post(`/social/clans/${myClan.value.id}/leave`)
      myClan.value = null

      return { success: true, message: 'Klandan ayrıldınız' }
    } catch (e) {
      console.error('Failed to leave clan:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Klandan ayrılamadınız'
      }
    }
  }

  const kickMember = async (memberId) => {
    if (!myClan.value || !isOfficer.value) {
      return { success: false, message: 'Yetkiniz yok' }
    }

    try {
      await api.post(`/social/clans/${myClan.value.id}/kick`, { user_id: memberId })

      clanMembers.value = clanMembers.value.filter(m => m.id !== memberId)

      return { success: true, message: 'Üye klandan çıkarıldı' }
    } catch (e) {
      console.error('Failed to kick member:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Üye çıkarılamadı'
      }
    }
  }

  const promoteToOfficer = async (memberId) => {
    if (!myClan.value || !isLeader.value) {
      return { success: false, message: 'Yetkiniz yok' }
    }

    try {
      await api.post(`/social/clans/${myClan.value.id}/promote`, {
        user_id: memberId,
        role: ClanRole.OFFICER
      })

      const member = clanMembers.value.find(m => m.id === memberId)
      if (member) {
        member.role = ClanRole.OFFICER
      }

      return { success: true, message: 'Üye subay yapıldı!' }
    } catch (e) {
      console.error('Failed to promote member:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Üye terfi ettirilemedi'
      }
    }
  }

  const demoteToMember = async (memberId) => {
    if (!myClan.value || !isLeader.value) {
      return { success: false, message: 'Yetkiniz yok' }
    }

    try {
      await api.post(`/social/clans/${myClan.value.id}/demote`, { user_id: memberId })

      const member = clanMembers.value.find(m => m.id === memberId)
      if (member) {
        member.role = ClanRole.MEMBER
      }

      return { success: true, message: 'Üye indirildi' }
    } catch (e) {
      console.error('Failed to demote member:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Üye indirilemedi'
      }
    }
  }

  const transferLeadership = async (memberId) => {
    if (!myClan.value || !isLeader.value) {
      return { success: false, message: 'Yetkiniz yok' }
    }

    try {
      await api.post(`/social/clans/${myClan.value.id}/transfer`, { user_id: memberId })

      // Update roles
      const oldLeader = clanMembers.value.find(m => m.role === ClanRole.LEADER)
      const newLeader = clanMembers.value.find(m => m.id === memberId)

      if (oldLeader) oldLeader.role = ClanRole.OFFICER
      if (newLeader) newLeader.role = ClanRole.LEADER

      myClan.value.my_role = ClanRole.OFFICER

      return { success: true, message: 'Liderlik devredildi!' }
    } catch (e) {
      console.error('Failed to transfer leadership:', e)
      return {
        success: false,
        message: e.response?.data?.message || 'Liderlik devredilemedi'
      }
    }
  }

  // Search
  const setSearchQuery = (query) => {
    searchQuery.value = query
    fetchClans({ reset: true })
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    fetchClans({ reset: true })
  }

  // Helpers
  const getRoleLabel = (role) => {
    const labels = {
      [ClanRole.LEADER]: 'Lider',
      [ClanRole.OFFICER]: 'Subay',
      [ClanRole.MEMBER]: 'Üye'
    }
    return labels[role] || role
  }

  const getRoleColor = (role) => {
    const colors = {
      [ClanRole.LEADER]: '#fbbf24',
      [ClanRole.OFFICER]: '#3b82f6',
      [ClanRole.MEMBER]: '#6b7280'
    }
    return colors[role] || '#6b7280'
  }

  const getStatusLabel = (status) => {
    const labels = {
      [ClanStatus.ACTIVE]: 'Aktif',
      [ClanStatus.RECRUITING]: 'Üye Alıyor',
      [ClanStatus.CLOSED]: 'Kapalı',
      [ClanStatus.INACTIVE]: 'Pasif'
    }
    return labels[status] || status
  }

  // Initialize
  const init = async () => {
    await Promise.all([
      fetchClans({ reset: true }),
      fetchMyClan(),
      fetchMyInvites()
    ])
  }

  // Reset
  const reset = () => {
    clans.value = []
    myClan.value = null
    currentClan.value = null
    clanMembers.value = []
    clanInvites.value = []
    clanApplications.value = []
    myApplications.value = []
    searchQuery.value = ''
    filters.value = { status: null, minMembers: null, maxMembers: null }
    pagination.value = { page: 1, limit: 12, total: 0, hasMore: true }
    error.value = null
  }

  return {
    // State
    clans,
    myClan,
    currentClan,
    clanMembers,
    clanInvites,
    clanApplications,
    myApplications,
    loading,
    error,
    searchQuery,
    filters,
    pagination,

    // Computed
    isInClan,
    myRole,
    isLeader,
    isOfficer,
    filteredClans,
    recruitingClans,

    // Actions
    fetchClans,
    fetchClan,
    fetchMyClan,
    fetchClanMembers,
    fetchMyInvites,
    fetchApplications,
    fetchMyApplications,
    loadMore,
    createClan,
    updateClan,
    deleteClan,
    applyToClan,
    cancelApplication,
    acceptApplication,
    rejectApplication,
    inviteUser,
    acceptInvite,
    declineInvite,
    leaveClan,
    kickMember,
    promoteToOfficer,
    demoteToMember,
    transferLeadership,
    setSearchQuery,
    setFilters,
    init,
    reset,

    // Helpers
    getRoleLabel,
    getRoleColor,
    getStatusLabel,

    // Constants
    ClanRole,
    ClanStatus
  }
})
