import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authAPI from '@/api/auth'
import walletAPI from '@/api/wallet'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const balance = ref({ balance_real: 0, balance_coin: 0 })

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => {
    const role = user.value?.role?.toLowerCase()
    return role === 'admin' || role === 'superadmin'
  })

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
      // Backend returns 'token' field, not 'access_token'
      const token = response.data.token || response.data.access_token
      const user = response.data.user

      if (!token || !user) {
        console.error('Invalid auth response:', response.data)
        return { success: false, error: 'Invalid server response' }
      }

      setAuth(token, user)
      // Fetch balance after login
      await fetchBalance()
      return { success: true }
    } catch (error) {
      console.error('Login error:', error.response?.data)
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
      // API returns user data directly in response.data
      const userData = response.data

      if (userData && userData.id) {
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
        // Also fetch wallet balance
        await fetchBalance()
      } else {
        console.error('Invalid user data:', userData)
        clearAuth()
      }
    } catch (error) {
      console.error('Fetch user error:', error)
      clearAuth()
    }
  }

  async function fetchBalance() {
    try {
      const response = await walletAPI.getBalance()
      balance.value = response.data
    } catch (error) {
      console.error('Fetch balance error:', error)
      // Don't clear auth on balance fetch error
    }
  }

  async function init() {
    const savedUser = localStorage.getItem('user')
    if (savedUser && token.value) {
      try {
        user.value = JSON.parse(savedUser)
        // Fetch balance on init if user is logged in
        await fetchBalance()
      } catch (error) {
        clearAuth()
      }
    }
  }

  // Alias for compatibility
  const fetchProfile = fetchUser

  return {
    user,
    token,
    balance,
    isAuthenticated,
    isAdmin,
    setAuth,
    clearAuth,
    login,
    logout,
    fetchUser,
    fetchProfile,
    fetchBalance,
    init
  }
})
