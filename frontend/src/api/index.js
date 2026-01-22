import apiClient from './client'

export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  me: () => apiClient.get('/auth/me'),
  check: () => apiClient.get('/auth/check'),
  refresh: () => apiClient.post('/auth/refresh'),
  verify2FA: (data) => apiClient.post('/auth/2fa/verify', data),
  login2FA: (data) => apiClient.post('/auth/2fa/login', data),
  enable2FA: () => apiClient.post('/auth/2fa/setup'),
  confirmEnable2FA: (code) => apiClient.post('/auth/2fa/enable', { code }),
  disable2FA: (code) => apiClient.post('/auth/2fa/disable', { code }),
  forgotPassword: (email) => apiClient.post('/auth/forgot-password', { email }),
  resetPassword: (data) => apiClient.post('/auth/reset-password', data),
  changePassword: (data) => apiClient.post('/auth/change-password', data),
  // Email verification
  sendVerificationEmail: () => apiClient.post('/auth/email/send-verification'),
  verifyEmail: (token) => apiClient.post('/auth/email/verify', { token }),
  getEmailVerificationStatus: () => apiClient.get('/auth/email/status')
}

export const serversAPI = {
  // Public servers list
  getAll: (params) => apiClient.get('/servers', { params }),
  getPublic: (id) => apiClient.get(`/servers/${id}`),

  // My servers (requires auth)
  getMy: () => apiClient.get('/my-servers'),
  getOne: (id) => apiClient.get(`/my-servers/${id}/status`),
  create: (data) => apiClient.post('/servers/create', data),

  // Server actions
  start: (id) => apiClient.post(`/my-servers/${id}/action`, { action: 'start' }),
  stop: (id) => apiClient.post(`/my-servers/${id}/action`, { action: 'stop' }),
  restart: (id) => apiClient.post(`/my-servers/${id}/action`, { action: 'restart' }),

  // Server info
  status: (id) => apiClient.get(`/my-servers/${id}/status`),
  players: (id) => apiClient.get(`/my-servers/${id}/players`),
  resources: (id) => apiClient.get(`/my-servers/${id}/resources`),
  logs: (id, lines = 100) => apiClient.get(`/my-servers/${id}/logs`, { params: { lines } }),

  // RCON
  rcon: (id, command) => apiClient.post(`/my-servers/${id}/rcon`, { command }),
  rconHistory: (id, limit = 50) => apiClient.get(`/my-servers/${id}/rcon-history`, { params: { limit } }),

  // Maps
  maps: (id) => apiClient.get(`/my-servers/${id}/maps`),
  changeMap: (id, mapName) => apiClient.post(`/my-servers/${id}/change-map`, { map_name: mapName }),

  // Config
  getConfig: (id, configType = 'server.cfg') => apiClient.get(`/my-servers/${id}/config`, { params: { config_type: configType } }),
  saveConfig: (id, configType, content) => apiClient.post(`/my-servers/${id}/config`, { config_type: configType, content }),

  // Files & Plugins
  files: (id, path = '') => apiClient.get(`/my-servers/${id}/files`, { params: { path } }),
  plugins: (id) => apiClient.get(`/my-servers/${id}/plugins`)
}

export const forumAPI = {
  // Categories
  getCategories: () => apiClient.get('/forum/categories'),
  getCategory: (slug) => apiClient.get(`/forum/categories/${slug}`),

  // Topics
  getTopics: (categorySlug, params) => apiClient.get(`/forum/categories/${categorySlug}/topics`, { params }),
  getAllTopics: (params) => apiClient.get('/forum/topics', { params }),
  getTopic: (slug) => apiClient.get(`/forum/topics/${slug}`),
  createTopic: (data) => apiClient.post('/forum/topics', data),

  // Replies
  getReplies: (topicSlug, params) => apiClient.get(`/forum/topics/${topicSlug}/replies`, { params }),
  createReply: (topicSlug, data) => apiClient.post(`/forum/topics/${topicSlug}/replies`, data),

  // Stats
  getStats: () => apiClient.get('/forum/stats')
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
