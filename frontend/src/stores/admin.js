import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { adminApi } from '@/services/api'

export const useAdminStore = defineStore('admin', () => {
  // State
  const dashboardData = ref(null)
  const users = ref([])
  const servers = ref([])
  const payments = ref([])
  const packages = ref([])
  const settings = ref({})
  const loading = ref(false)
  const error = ref(null)

  // Pagination
  const pagination = ref({
    users: { page: 1, total: 0, perPage: 20 },
    servers: { page: 1, total: 0, perPage: 20 },
    payments: { page: 1, total: 0, perPage: 20 }
  })

  // Computed
  const pendingPaymentsCount = computed(() => {
    return dashboardData.value?.pending_payments || 0
  })

  const totalUsers = computed(() => {
    return dashboardData.value?.total_users || 0
  })

  const activeServers = computed(() => {
    return dashboardData.value?.active_servers || 0
  })

  const monthlyRevenue = computed(() => {
    return dashboardData.value?.monthly_revenue || 0
  })

  // Actions
  const fetchDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      dashboardData.value = await adminApi.getDashboard()
    } catch (e) {
      error.value = e.message
      console.error('Dashboard fetch error:', e)
    }
    loading.value = false
  }

  const fetchUsers = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const data = await adminApi.getUsers({
        page: pagination.value.users.page,
        limit: pagination.value.users.perPage,
        ...params
      })
      users.value = data.users || []
      pagination.value.users.total = data.total || 0
    } catch (e) {
      error.value = e.message
      console.error('Users fetch error:', e)
    }
    loading.value = false
  }

  const updateUser = async (id, data) => {
    try {
      await adminApi.updateUser(id, data)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...data }
      }
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const banUser = async (id) => {
    try {
      await adminApi.banUser(id)
      const user = users.value.find(u => u.id === id)
      if (user) user.is_banned = true
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const unbanUser = async (id) => {
    try {
      await adminApi.unbanUser(id)
      const user = users.value.find(u => u.id === id)
      if (user) user.is_banned = false
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const fetchServers = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const data = await adminApi.getServers({
        page: pagination.value.servers.page,
        limit: pagination.value.servers.perPage,
        ...params
      })
      servers.value = data.servers || []
      pagination.value.servers.total = data.total || 0
    } catch (e) {
      error.value = e.message
      console.error('Servers fetch error:', e)
    }
    loading.value = false
  }

  const restartServer = async (id) => {
    try {
      await adminApi.restartServer(id)
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const deleteServer = async (id) => {
    try {
      await adminApi.deleteServer(id)
      servers.value = servers.value.filter(s => s.id !== id)
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const fetchPayments = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const data = await adminApi.getPayments({
        page: pagination.value.payments.page,
        limit: pagination.value.payments.perPage,
        ...params
      })
      payments.value = data.payments || []
      pagination.value.payments.total = data.total || 0
    } catch (e) {
      error.value = e.message
      console.error('Payments fetch error:', e)
    }
    loading.value = false
  }

  const approvePayment = async (id) => {
    try {
      await adminApi.approvePayment(id)
      const payment = payments.value.find(p => p.id === id)
      if (payment) payment.status = 'completed'
      if (dashboardData.value) {
        dashboardData.value.pending_payments = Math.max(0, (dashboardData.value.pending_payments || 1) - 1)
      }
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const rejectPayment = async (id, reason) => {
    try {
      await adminApi.rejectPayment(id, reason)
      const payment = payments.value.find(p => p.id === id)
      if (payment) {
        payment.status = 'failed'
        payment.reject_reason = reason
      }
      if (dashboardData.value) {
        dashboardData.value.pending_payments = Math.max(0, (dashboardData.value.pending_payments || 1) - 1)
      }
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const fetchPackages = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await adminApi.getPackages()
      packages.value = data.packages || []
    } catch (e) {
      error.value = e.message
      console.error('Packages fetch error:', e)
    }
    loading.value = false
  }

  const createPackage = async (data) => {
    try {
      const pkg = await adminApi.createPackage(data)
      packages.value.push(pkg)
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const updatePackage = async (id, data) => {
    try {
      await adminApi.updatePackage(id, data)
      const index = packages.value.findIndex(p => p.id === id)
      if (index !== -1) {
        packages.value[index] = { ...packages.value[index], ...data }
      }
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const deletePackage = async (id) => {
    try {
      await adminApi.deletePackage(id)
      packages.value = packages.value.filter(p => p.id !== id)
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const fetchSettings = async () => {
    loading.value = true
    error.value = null
    try {
      settings.value = await adminApi.getSettings()
    } catch (e) {
      error.value = e.message
      console.error('Settings fetch error:', e)
    }
    loading.value = false
  }

  const updateSettings = async (data) => {
    try {
      await adminApi.updateSettings(data)
      settings.value = { ...settings.value, ...data }
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    dashboardData,
    users,
    servers,
    payments,
    packages,
    settings,
    loading,
    error,
    pagination,

    // Computed
    pendingPaymentsCount,
    totalUsers,
    activeServers,
    monthlyRevenue,

    // Actions
    fetchDashboard,
    fetchUsers,
    updateUser,
    banUser,
    unbanUser,
    fetchServers,
    restartServer,
    deleteServer,
    fetchPayments,
    approvePayment,
    rejectPayment,
    fetchPackages,
    createPackage,
    updatePackage,
    deletePackage,
    fetchSettings,
    updateSettings,
    clearError
  }
})
