import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
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
      localStorage.setItem('access_token', accessToken)
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
      localStorage.setItem('access_token', accessToken)
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
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
    }
  }

  async function fetchUser() {
    if (!token.value) return false

    loading.value = true
    try {
      const response = await authAPI.me()
      user.value = response
      return true
    } catch (err) {
      console.error('Fetch user error:', err)
      // Token invalid, clear auth
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      return false
    } finally {
      loading.value = false
    }
  }

  async function refreshToken() {
    try {
      const response = await authAPI.refresh()
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)
      return true
    } catch (err) {
      console.error('Token refresh error:', err)
      return false
    }
  }

  async function verify2FA({ token: tempToken, code }) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.verify2FA({ token: tempToken, code })

      const accessToken = response.token || response.access_token
      if (!accessToken) {
        throw new Error('No token received from server')
      }

      token.value = accessToken
      user.value = response.user
      localStorage.setItem('access_token', accessToken)
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '2FA verification failed'
      throw err
    } finally {
      loading.value = false
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
    verify2FA
  }
})
