import apiClient from './client'

export default {
  // Authentication
  register(data) {
    return apiClient.post('/auth/register', data)
  },

  login(data) {
    return apiClient.post('/auth/login', data)
  },

  logout() {
    return apiClient.post('/auth/logout')
  },

  getMe() {
    return apiClient.get('/auth/me')
  },

  // OAuth
  getOAuthUrl(provider) {
    return `/api/auth/oauth/${provider}`
  },

  // Password Management
  changePassword(data) {
    return apiClient.post('/auth/change-password', data)
  }
}
