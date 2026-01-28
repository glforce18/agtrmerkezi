import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import serversAPI from '@/api/servers'

export const useServersStore = defineStore('servers', () => {
  // State
  const myServers = ref([])
  const currentServer = ref(null)
  const packages = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const runningServers = computed(() =>
    myServers.value.filter(s => s.status === 'running' || s.status === 'online')
  )

  const stoppedServers = computed(() =>
    myServers.value.filter(s => s.status === 'stopped' || s.status === 'offline')
  )

  const pendingServers = computed(() =>
    myServers.value.filter(s => s.status === 'pending' || s.status === 'creating')
  )

  const hasServers = computed(() => myServers.value.length > 0)

  // Actions
  async function fetchMyServers() {
    loading.value = true
    error.value = null

    try {
      const response = await serversAPI.getMyServersV2()
      myServers.value = response.data.servers || response.data || []
      return myServers.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sunucular yüklenemedi'
      console.error('Fetch servers error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchServer(id) {
    loading.value = true
    error.value = null

    try {
      const response = await serversAPI.getServer(id)
      currentServer.value = response.data
      return currentServer.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sunucu bulunamadı'
      console.error('Fetch server error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPackages() {
    loading.value = true
    error.value = null

    try {
      const response = await serversAPI.getPackages()
      packages.value = response.data.packages || response.data || []
      return packages.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Paketler yüklenemedi'
      console.error('Fetch packages error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function startServer(id) {
    try {
      const response = await serversAPI.startServer(id)
      // Update server status in local state
      const server = myServers.value.find(s => s.id === id)
      if (server) {
        server.status = 'running'
      }
      if (currentServer.value?.id === id) {
        currentServer.value.status = 'running'
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sunucu başlatılamadı'
      throw err
    }
  }

  async function stopServer(id, force = false) {
    try {
      const response = await serversAPI.stopServer(id, force)
      // Update server status in local state
      const server = myServers.value.find(s => s.id === id)
      if (server) {
        server.status = 'stopped'
      }
      if (currentServer.value?.id === id) {
        currentServer.value.status = 'stopped'
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sunucu durdurulamadı'
      throw err
    }
  }

  async function restartServer(id) {
    try {
      const response = await serversAPI.restartServer(id)
      // Update server status in local state
      const server = myServers.value.find(s => s.id === id)
      if (server) {
        server.status = 'running'
      }
      if (currentServer.value?.id === id) {
        currentServer.value.status = 'running'
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sunucu yeniden başlatılamadı'
      throw err
    }
  }

  async function getServerStatus(id) {
    try {
      const response = await serversAPI.getServerStatusV2(id)
      // Update server status in local state
      const server = myServers.value.find(s => s.id === id)
      if (server && response.data.status) {
        server.status = response.data.status
        server.players = response.data.players || []
        server.online = response.data.online || false
      }
      if (currentServer.value?.id === id && response.data.status) {
        currentServer.value.status = response.data.status
        currentServer.value.players = response.data.players || []
        currentServer.value.online = response.data.online || false
      }
      return response.data
    } catch (err) {
      console.error('Get server status error:', err)
      return null
    }
  }

  async function deleteServer(id) {
    try {
      await serversAPI.deleteServer(id)
      // Remove from local state
      myServers.value = myServers.value.filter(s => s.id !== id)
      if (currentServer.value?.id === id) {
        currentServer.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sunucu silinemedi'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrentServer() {
    currentServer.value = null
  }

  return {
    // State
    myServers,
    currentServer,
    packages,
    loading,
    error,
    // Getters
    runningServers,
    stoppedServers,
    pendingServers,
    hasServers,
    // Actions
    fetchMyServers,
    fetchServer,
    fetchPackages,
    startServer,
    stopServer,
    restartServer,
    getServerStatus,
    deleteServer,
    clearError,
    clearCurrentServer
  }
})
