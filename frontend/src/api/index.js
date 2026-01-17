import apiClient from './client'

export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  me: () => apiClient.get('/auth/me'),
  refresh: () => apiClient.post('/auth/refresh'),
  verify2FA: (data) => apiClient.post('/auth/2fa/verify', data),
  enable2FA: () => apiClient.post('/auth/2fa/enable'),
  disable2FA: (code) => apiClient.post('/auth/2fa/disable', { code }),
  forgotPassword: (email) => apiClient.post('/auth/forgot-password', { email }),
  resetPassword: (data) => apiClient.post('/auth/reset-password', data)
}

export const serversAPI = {
  getAll: (params) => apiClient.get('/servers', { params }),
  getOne: (id) => apiClient.get(`/servers/${id}`),
  create: (data) => apiClient.post('/servers', data),
  update: (id, data) => apiClient.put(`/servers/${id}`, data),
  delete: (id) => apiClient.delete(`/servers/${id}`),
  stats: (id) => apiClient.get(`/servers/${id}/stats`),
  start: (id) => apiClient.post(`/servers/${id}/start`),
  stop: (id) => apiClient.post(`/servers/${id}/stop`),
  restart: (id) => apiClient.post(`/servers/${id}/restart`),
  console: (id, command) => apiClient.post(`/servers/${id}/console`, { command }),
  files: (id, path) => apiClient.get(`/servers/${id}/files`, { params: { path } }),
  backup: (id) => apiClient.post(`/servers/${id}/backup`),
  restore: (id, backupId) => apiClient.post(`/servers/${id}/restore/${backupId}`)
}

export const forumAPI = {
  getCategories: () => apiClient.get('/forum/categories'),
  getTopics: (categoryId, params) => apiClient.get(`/forum/categories/${categoryId}/topics`, { params }),
  getTopic: (topicId) => apiClient.get(`/forum/topics/${topicId}`),
  createTopic: (categoryId, data) => apiClient.post(`/forum/categories/${categoryId}/topics`, data),
  createReply: (topicId, data) => apiClient.post(`/forum/topics/${topicId}/replies`, data)
}

export const userAPI = {
  getProfile: (userId) => apiClient.get(`/users/${userId}`),
  updateProfile: (userId, data) => apiClient.put(`/users/${userId}`, data),
  getStats: (userId) => apiClient.get(`/users/${userId}/stats`)
}

export const shopAPI = {
  getProducts: () => apiClient.get('/shop/products'),
  getProduct: (id) => apiClient.get(`/shop/products/${id}`),
  purchase: (productId, data) => apiClient.post(`/shop/products/${productId}/purchase`, data)
}

export const statsAPI = {
  getDashboard: () => apiClient.get('/stats/dashboard'),
  getDaily: (params) => apiClient.get('/stats/daily', { params }),
  getLeaderboard: (params) => apiClient.get('/stats/leaderboard', { params })
}

export default {
  auth: authAPI,
  servers: serversAPI,
  forum: forumAPI,
  user: userAPI,
  shop: shopAPI,
  stats: statsAPI
}
