import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Authentication requirement composable
 * Provides consistent auth checking and login redirect across the app
 */
export function useRequireAuth() {
  const authStore = useAuthStore()
  const router = useRouter()
  const route = useRoute()

  const isLoggedIn = computed(() => !!authStore.user)
  const user = computed(() => authStore.user)

  /**
   * Check if user is authenticated, redirect to login if not
   * @param {Object} options - Options
   * @param {boolean} options.redirect - Whether to redirect to login (default: true)
   * @param {string} options.message - Custom message to show (default: 'Lutfen giris yapin')
   * @param {Function} options.onSuccess - Callback to run if authenticated
   * @returns {boolean} - Whether user is authenticated
   */
  const requireAuth = (options = {}) => {
    const {
      redirect = true,
      message = 'Bu islem icin giris yapmaniz gerekiyor',
      onSuccess = null
    } = typeof options === 'function' ? { onSuccess: options } : options

    if (!isLoggedIn.value) {
      // Show user-friendly message
      window.$message?.warning(message)

      // Redirect to login with return URL
      if (redirect) {
        router.push({
          name: 'login',
          query: { redirect: route.fullPath }
        })
      }
      return false
    }

    // Run callback if provided and user is authenticated
    if (onSuccess && typeof onSuccess === 'function') {
      onSuccess()
    }

    return true
  }

  /**
   * Wrapper for actions that require authentication
   * @param {Function} action - Action to perform if authenticated
   * @param {Object} options - Options for requireAuth
   * @returns {Function} - Wrapped action
   */
  const withAuth = (action, options = {}) => {
    return (...args) => {
      if (requireAuth(options)) {
        return action(...args)
      }
    }
  }

  /**
   * Check auth and show login modal instead of redirect
   * Useful for inline actions like like/favorite
   */
  const checkAuthOrPrompt = (callback) => {
    if (!isLoggedIn.value) {
      window.$message?.info('Bu islem icin giris yapmaniz gerekiyor')
      // Show a confirmation to redirect
      window.$dialog?.warning({
        title: 'Giris Gerekli',
        content: 'Bu islemi yapabilmek icin giris yapmaniz gerekiyor. Giris sayfasina yonlendirilmek ister misiniz?',
        positiveText: 'Giris Yap',
        negativeText: 'Vazgec',
        onPositiveClick: () => {
          router.push({
            name: 'login',
            query: { redirect: route.fullPath }
          })
        }
      })
      return false
    }
    if (callback) callback()
    return true
  }

  return {
    isLoggedIn,
    user,
    requireAuth,
    withAuth,
    checkAuthOrPrompt
  }
}
