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

  // My servers (requires auth) - v2 API
  getMy: () => apiClient.get('/v2/servers/my'),
  getOne: (id) => apiClient.get(`/v2/servers/${id}`),
  create: (data) => apiClient.post('/v2/servers/create', data),

  // Server actions
  start: (id) => apiClient.post(`/v2/servers/${id}/start`),
  stop: (id) => apiClient.post(`/v2/servers/${id}/stop`),
  restart: (id) => apiClient.post(`/v2/servers/${id}/restart`),

  // Server info
  status: (id) => apiClient.get(`/v2/servers/${id}/status`),
  players: (id) => apiClient.get(`/v2/servers/${id}/players`),
  resources: (id) => apiClient.get(`/v2/servers/${id}/resources`),
  logs: (id, lines = 100) => apiClient.get(`/v2/servers/${id}/logs`, { params: { lines } }),

  // RCON
  rcon: (id, command) => apiClient.post(`/v2/servers/${id}/rcon`, { command }),
  rconHistory: (id, limit = 50) => apiClient.get(`/v2/servers/${id}/rcon/history`, { params: { limit } }),

  // Maps
  maps: (id) => apiClient.get(`/v2/servers/${id}/maps`),
  changeMap: (id, mapName) => apiClient.post(`/v2/servers/${id}/maps/change`, { map_name: mapName }),

  // Config
  getConfig: (id, filename = 'server.cfg') => apiClient.get(`/v2/servers/${id}/config`, { params: { filename } }),
  saveConfig: (id, filename, content) => apiClient.put(`/v2/servers/${id}/config`, { content }, { params: { filename } }),

  // Admins
  getAdmins: (id) => apiClient.get(`/v2/servers/${id}/admins`),
  addAdmin: (id, data) => apiClient.post(`/v2/servers/${id}/admins`, data),
  removeAdmin: (id, adminId) => apiClient.delete(`/v2/servers/${id}/admins/${adminId}`),

  // Search by Steam ID or Unique Code
  searchBySteamId: (steamId) => apiClient.get(`/v2/servers/search/steam/${steamId}`),
  searchByCode: (code) => apiClient.get(`/v2/servers/search/code/${code}`)
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
