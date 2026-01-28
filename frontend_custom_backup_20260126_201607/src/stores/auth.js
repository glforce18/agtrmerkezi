import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authAPI from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.is_admin)
  const has2FA = computed(() => user.value?.two_factor_enabled)

  // Actions
  async function login(credentials) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.login(credentials)

      if (response.data.requires_2fa) {
        // 2FA required, return special flag
        loading.value = false
        return { requires2FA: true }
      }

      // Normal login success
      setAuth(response.data.token, response.data.user)
      loading.value = false
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Giriş başarısız'
      loading.value = false
      throw err
    }
  }

  async function login2FA(code) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.login2FA({ code })
      setAuth(response.data.token, response.data.user)
      loading.value = false
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || '2FA doğrulama başarısız'
      loading.value = false
      throw err
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null

    try {
      const response = await authAPI.register(userData)
      setAuth(response.data.token, response.data.user)
      loading.value = false
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Kayıt başarısız'
      loading.value = false
      throw err
    }
  }

  async function logout() {
    loading.value = true

    try {
      await authAPI.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuth()
      loading.value = false
    }
  }

  async function checkAuth() {
    if (!token.value) return false

    try {
      const response = await authAPI.checkAuth()
      if (response.data.authenticated) {
        user.value = response.data.user
        return true
      } else {
        clearAuth()
        return false
      }
    } catch (err) {
      clearAuth()
      return false
    }
  }

  async function fetchUser() {
    try {
      const response = await authAPI.getMe()
      user.value = response.data
    } catch (err) {
      console.error('Fetch user error:', err)
      clearAuth()
    }
  }

  function setAuth(newToken, newUser) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('auth_token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
  }

  // Initialize from localStorage
  function init() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.error('Failed to parse stored user:', err)
        clearAuth()
      }
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    has2FA,
    // Actions
    login,
    login2FA,
    register,
    logout,
    checkAuth,
    fetchUser,
    setAuth,
    clearAuth,
    init
  }
})
