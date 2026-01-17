/**
 * API Service - Modern Fetch Wrapper
 * Centralized API handling for AGTR Merkezi
 */

const API_BASE = '/api'

class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const handleResponse = async (response) => {
  const contentType = response.headers.get('content-type')
  const isJson = contentType && contentType.includes('application/json')
  const data = isJson ? await response.json() : await response.text()

  if (!response.ok) {
    const message = isJson && data.detail ? data.detail : `HTTP ${response.status}`
    throw new ApiError(message, response.status, data)
  }

  return data
}

const request = async (endpoint, options = {}) => {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options.headers
    },
    ...options
  }

  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body)
  }

  const response = await fetch(url, config)
  return handleResponse(response)
}

// HTTP Methods
export const api = {
  get: (endpoint, params = {}) => {
    const query = new URLSearchParams(params).toString()
    const url = query ? `${endpoint}?${query}` : endpoint
    return request(url, { method: 'GET' })
  },

  post: (endpoint, body = {}) => {
    return request(endpoint, { method: 'POST', body })
  },

  put: (endpoint, body = {}) => {
    return request(endpoint, { method: 'PUT', body })
  },

  patch: (endpoint, body = {}) => {
    return request(endpoint, { method: 'PATCH', body })
  },

  delete: (endpoint) => {
    return request(endpoint, { method: 'DELETE' })
  }
}

// Admin API Endpoints
export const adminApi = {
  // Dashboard
  getDashboard: () => api.get('/admin/dashboard'),

  // Users
  getUsers: (params = {}) => api.get('/admin/users', params),
  getUser: (id) => api.get(`/admin/users/${id}`),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  banUser: (id) => api.post(`/admin/users/${id}/ban`),
  unbanUser: (id) => api.post(`/admin/users/${id}/unban`),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),

  // Servers
  getServers: (params = {}) => api.get('/admin/servers', params),
  getServer: (id) => api.get(`/admin/servers/${id}`),
  updateServer: (id, data) => api.put(`/admin/servers/${id}`, data),
  restartServer: (id) => api.post(`/admin/servers/${id}/restart`),
  stopServer: (id) => api.post(`/admin/servers/${id}/stop`),
  deleteServer: (id) => api.delete(`/admin/servers/${id}`),

  // Payments
  getPayments: (params = {}) => api.get('/admin/payments', params),
  getPayment: (id) => api.get(`/admin/payments/${id}`),
  approvePayment: (id) => api.post(`/admin/payments/${id}/approve`),
  rejectPayment: (id, reason) => api.post(`/admin/payments/${id}/reject`, { reason }),
  getPendingPayments: () => api.get('/admin/payments/pending'),

  // Packages
  getPackages: (params = {}) => api.get('/admin/packages', params),
  getPackage: (id) => api.get(`/admin/packages/${id}`),
  createPackage: (data) => api.post('/admin/packages', data),
  updatePackage: (id, data) => api.put(`/admin/packages/${id}`, data),
  deletePackage: (id) => api.delete(`/admin/packages/${id}`),

  // Settings
  getSettings: () => api.get('/admin/settings'),
  updateSettings: (data) => api.put('/admin/settings', data),
  testEmail: () => api.post('/admin/settings/test-email'),

  // Reports
  getReports: (params = {}) => api.get('/admin/reports', params),
  getStats: (period = 'week') => api.get('/admin/stats', { period }),

  // Activity Logs
  getLogs: (params = {}) => api.get('/admin/logs', params)
}

// User API Endpoints
export const userApi = {
  // Auth
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  refreshToken: () => api.post('/auth/refresh'),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
  changePassword: (data) => api.post('/auth/change-password', data),

  // 2FA
  enable2FA: () => api.post('/auth/2fa/enable'),
  verify2FA: (code) => api.post('/auth/2fa/verify', { code }),
  disable2FA: (code) => api.post('/auth/2fa/disable', { code }),

  // Servers
  getMyServers: () => api.get('/servers/my'),
  getServer: (id) => api.get(`/servers/${id}`),
  createServer: (data) => api.post('/servers', data),
  updateServer: (id, data) => api.put(`/servers/${id}`, data),
  controlServer: (id, action) => api.post(`/servers/${id}/${action}`),

  // Payments
  getMyPayments: () => api.get('/payments/my'),
  createPayment: (data) => api.post('/payments', data),
  uploadProof: (paymentId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${API_BASE}/payments/${paymentId}/proof`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    }).then(handleResponse)
  },

  // Balance
  getBalance: () => api.get('/wallet/balance'),
  getTransactions: () => api.get('/wallet/transactions')
}

// Public API Endpoints
export const publicApi = {
  getServers: (params = {}) => api.get('/servers', params),
  getServer: (id) => api.get(`/servers/${id}`),
  getPackages: () => api.get('/packages'),
  getAnnouncements: () => api.get('/announcements'),
  getLeaderboard: (game) => api.get('/leaderboard', { game })
}

export { ApiError }
export default api
