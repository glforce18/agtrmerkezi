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

  checkAuth() {
    return apiClient.get('/auth/check')
  },

  getMe() {
    return apiClient.get('/auth/me')
  },

  // Two-Factor Authentication
  setup2FA() {
    return apiClient.post('/auth/2fa/setup')
  },

  verify2FA(data) {
    return apiClient.post('/auth/2fa/verify', data)
  },

  disable2FA(data) {
    return apiClient.post('/auth/2fa/disable', data)
  },

  login2FA(data) {
    return apiClient.post('/auth/2fa/login', data)
  },

  get2FAStatus() {
    return apiClient.get('/auth/2fa/status')
  },

  // Password Management
  forgotPassword(data) {
    return apiClient.post('/auth/forgot-password', data)
  },

  resetPassword(data) {
    return apiClient.post('/auth/reset-password', data)
  },

  changePassword(data) {
    return apiClient.post('/auth/change-password', data)
  },

  // OAuth
  getOAuthUrl(provider) {
    return `/api/auth/oauth/${provider}`
  },

  // Email Verification
  sendVerificationEmail() {
    return apiClient.post('/auth/email/send-verification')
  },

  verifyEmail(data) {
    return apiClient.post('/auth/email/verify', data)
  },

  getEmailStatus() {
    return apiClient.get('/auth/email/status')
  }
}
