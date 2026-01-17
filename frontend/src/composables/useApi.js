import { ref } from 'vue'
import { useUIStore } from '@/stores/ui'

export function useApi(apiCall) {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const uiStore = useUIStore()

  const execute = async (...args) => {
    loading.value = true
    error.value = null

    try {
      const response = await apiCall(...args)
      data.value = response
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'An error occurred'
      uiStore.addNotification({
        type: 'error',
        message: error.value
      })
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    execute
  }
}
