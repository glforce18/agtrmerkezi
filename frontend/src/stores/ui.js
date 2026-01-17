import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const mobileMenuOpen = ref(false)
  const notifications = ref([])
  const loading = ref(false)
  const pageTitle = ref('AGTR Merkezi')

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function toggleMobileMenu() {
    mobileMenuOpen.value = !mobileMenuOpen.value
  }

  function addNotification(notification) {
    const id = Date.now()
    notifications.value.push({
      id,
      type: 'info',
      duration: 5000,
      ...notification
    })

    if (notification.duration !== 0) {
      setTimeout(() => removeNotification(id), notification.duration || 5000)
    }
  }

  function removeNotification(id) {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  function setLoading(value) {
    loading.value = value
  }

  function setPageTitle(title) {
    pageTitle.value = title
    document.title = `${title} - AGTR Merkezi`
  }

  return {
    sidebarOpen,
    mobileMenuOpen,
    notifications,
    loading,
    pageTitle,
    toggleSidebar,
    toggleMobileMenu,
    addNotification,
    removeNotification,
    setLoading,
    setPageTitle
  }
})
