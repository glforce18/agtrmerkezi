import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function useRequireSteam() {
  const authStore = useAuthStore()
  const router = useRouter()
  const route = useRoute()
  const showSteamModal = ref(false)

  const hasSteam = computed(() => !!authStore.user?.steam_id)
  const isLoggedIn = computed(() => !!authStore.user)

  /**
   * Check if user has Steam linked, redirect to login if not authenticated
   * @param {Function} callback - Callback to run if Steam is linked
   * @param {Object} options - Options
   * @param {boolean} options.redirect - Whether to redirect to login (default: true)
   * @returns {boolean} - Whether user has Steam linked
   */
  const requireSteam = (callback, options = {}) => {
    const { redirect = true } = options

    if (!isLoggedIn.value) {
      window.$message?.warning('Bu islem icin giris yapmaniz gerekiyor')

      // Redirect to login with return URL
      if (redirect) {
        router.push({
          name: 'Login',
          query: { redirect: route.fullPath }
        })
      }
      return false
    }

    if (!hasSteam.value) {
      showSteamModal.value = true
      return false
    }

    if (callback) callback()
    return true
  }

  /**
   * Check auth only (no Steam required)
   * Shows message and optionally redirects
   */
  const requireAuthOnly = (callback, options = {}) => {
    const { redirect = true, message = 'Bu islem icin giris yapmaniz gerekiyor' } = options

    if (!isLoggedIn.value) {
      window.$message?.warning(message)

      if (redirect) {
        router.push({
          name: 'Login',
          query: { redirect: route.fullPath }
        })
      }
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
    requireAuthOnly,
    connectSteam,
    closeModal
  }
}
