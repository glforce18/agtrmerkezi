import { defineStore } from 'pinia'
import { ref } from 'vue'
import serversAPI from '@/api/servers'

export const useServersStore = defineStore('servers', () => {
  const servers = ref([])
  const currentServer = ref(null)
  const loading = ref(false)

  async function fetchMyServers() {
    loading.value = true
    try {
      const response = await serversAPI.getMyServers()
      servers.value = response.data
    } catch (error) {
      console.error('Failed to fetch servers:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchServer(id) {
    loading.value = true
    try {
      const response = await serversAPI.getServer(id)
      currentServer.value = response.data
    } catch (error) {
      console.error('Failed to fetch server:', error)
    } finally {
      loading.value = false
    }
  }

  async function startServer(id) {
    try {
      await serversAPI.startServer(id)
      await fetchMyServers()
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail }
    }
  }

  async function stopServer(id) {
    try {
      await serversAPI.stopServer(id)
      await fetchMyServers()
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail }
    }
  }

  async function restartServer(id) {
    try {
      await serversAPI.restartServer(id)
      await fetchMyServers()
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail }
    }
  }

  return {
    servers,
    currentServer,
    loading,
    fetchMyServers,
    fetchServer,
    startServer,
    stopServer,
    restartServer
  }
})
