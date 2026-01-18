import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'
import { STORAGE_KEYS, ADMIN_ROLES } from '@/constants'
import { getAccessToken, setAccessToken, removeAccessToken } from '@/utils/http'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(getAccessToken())
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => ADMIN_ROLES.includes(user.value?.role))
  const balanceReal = computed(() => user.value?.balance || 0)
  const balanceCoin = computed(() => user.value?.balance_coin || 0)

  async function login(credentials) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.login(credentials)

      // Check if 2FA is required
      if (response.requires_2fa) {
        return response // Return to handle 2FA modal
      }

      // Use 'token' field from backend (not 'access_token')
      const accessToken = response.token || response.access_token
      if (!accessToken) {
        throw new Error('No token received from server')
      }

      token.value = accessToken
      user.value = response.user
      setAccessToken(accessToken)
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.register(userData)

      // Use 'token' field from backend (not 'access_token')
      const accessToken = response.token || response.access_token
      if (!accessToken) {
        throw new Error('No token received from server')
      }

      token.value = accessToken
      user.value = response.user
      setAccessToken(accessToken)
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authAPI.logout()
    } catch (err) {
      // Logout error - continue with local cleanup
    } finally {
      token.value = null
      user.value = null
      removeAccessToken()
    }
  }

  async function fetchUser() {
    if (!token.value) return false

    loading.value = true
    try {
      const response = await authAPI.me()
      // /auth/me returns direct user object with all fields including balance_coin
      if (response.id && response.username) {
        user.value = response
        return true
      }
      // Fallback for /auth/check format (legacy)
      if (response.authenticated && response.user) {
        user.value = response.user
        return true
      }
      throw new Error('Invalid response')
    } catch (err) {
      // Token invalid, clear auth
      token.value = null
      user.value = null
      removeAccessToken()
      return false
    } finally {
      loading.value = false
    }
  }

  async function refreshToken() {
    try {
      const response = await authAPI.refresh()
      token.value = response.access_token
      setAccessToken(response.access_token)
      return true
    } catch (err) {
      // Token refresh failed
      return false
    }
  }

  async function verify2FA({ user_id, code }) {
    loading.value = true
    error.value = null

    try {
      // Use the 2FA login endpoint
      const response = await authAPI.login2FA({ user_id, totp_code: code })

      const accessToken = response.token || response.access_token
      if (!accessToken) {
        throw new Error('No token received from server')
      }

      token.value = accessToken
      user.value = response.user
      setAccessToken(accessToken)
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '2FA verification failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update user balance locally (for real-time updates)
  function updateBalance(newBalance, newBalanceCoin) {
    if (user.value) {
      if (newBalance !== undefined) user.value.balance = newBalance
      if (newBalanceCoin !== undefined) user.value.balance_coin = newBalanceCoin
    }
  }

  // Update user data
  function updateUser(userData) {
    if (user.value && userData) {
      user.value = { ...user.value, ...userData }
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    balanceReal,
    balanceCoin,
    login,
    register,
    logout,
    fetchUser,
    refreshToken,
    verify2FA,
    updateBalance,
    updateUser
  }
})
