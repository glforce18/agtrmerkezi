import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authAPI from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

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

  async function login(credentials) {
    try {
      const response = await authAPI.login(credentials)
      setAuth(response.data.access_token, response.data.user)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' }
    }
  }

  async function logout() {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearAuth()
    }
  }

  async function fetchUser() {
    try {
      const response = await authAPI.getMe()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      clearAuth()
    }
  }

  function init() {
    const savedUser = localStorage.getItem('user')
    if (savedUser && token.value) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        clearAuth()
      }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    setAuth,
    clearAuth,
    login,
    logout,
    fetchUser,
    init
  }
})
