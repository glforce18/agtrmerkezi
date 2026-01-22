import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useRequireSteam() {
  const authStore = useAuthStore()
  const showSteamModal = ref(false)

  const hasSteam = computed(() => !!authStore.user?.steam_id)
  const isLoggedIn = computed(() => !!authStore.user)

  const requireSteam = (callback) => {
    if (!isLoggedIn.value) {
      window.$message?.warning('Lutfen giris yapin')
      return false
    }
    if (!hasSteam.value) {
      showSteamModal.value = true
      return false
    }
    if (callback) callback()
    return true
  }

  const connectSteam = () => {
    window.location.href = '/api/auth/oauth/steam'
  }

  const closeModal = () => {
    showSteamModal.value = false
  }

  return {
    hasSteam,
    isLoggedIn,
    showSteamModal,
    requireSteam,
    connectSteam,
    closeModal
  }
}
