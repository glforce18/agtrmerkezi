import apiClient from './client'

export default {
  // ===== CATEGORIES =====

  // Get all categories
  getCategories() {
    return apiClient.get('/forum/categories')
  },

  // Get category by ID
  getCategory(id) {
    return apiClient.get(`/forum/categories/${id}`)
  },

  // ===== TOPICS =====

  // Get topics (with filters)
  getTopics(params = {}) {
    return apiClient.get('/forum/topics', { params })
  },

  // Get topics by category
  getTopicsByCategory(categoryId, params = {}) {
    return apiClient.get(`/forum/categories/${categoryId}/topics`, { params })
  },

  // Get topic by ID
  getTopic(id) {
    return apiClient.get(`/forum/topics/${id}`)
  },

  // Create topic
  createTopic(data) {
    return apiClient.post('/forum/topics', data)
  },

  // Update topic
  updateTopic(id, data) {
    return apiClient.put(`/forum/topics/${id}`, data)
  },

  // Delete topic
  deleteTopic(id) {
    return apiClient.delete(`/forum/topics/${id}`)
  },

  // Pin/Unpin topic
  pinTopic(id, pinned = true) {
    return apiClient.post(`/forum/topics/${id}/pin`, { pinned })
  },

  // Lock/Unlock topic
  lockTopic(id, locked = true) {
    return apiClient.post(`/forum/topics/${id}/lock`, { locked })
  },

  // ===== REPLIES =====

  // Get replies for topic
  getReplies(topicId, params = {}) {
    return apiClient.get(`/forum/topics/${topicId}/replies`, { params })
  },

  // Create reply
  createReply(topicId, data) {
    return apiClient.post(`/forum/topics/${topicId}/replies`, data)
  },

  // Update reply
  updateReply(topicId, replyId, data) {
    return apiClient.put(`/forum/topics/${topicId}/replies/${replyId}`, data)
  },

  // Delete reply
  deleteReply(topicId, replyId) {
    return apiClient.delete(`/forum/topics/${topicId}/replies/${replyId}`)
  },

  // ===== REACTIONS =====

  // React to topic
  reactToTopic(topicId, reaction) {
    return apiClient.post(`/forum/topics/${topicId}/react`, { reaction })
  },

  // React to reply
  reactToReply(topicId, replyId, reaction) {
    return apiClient.post(`/forum/topics/${topicId}/replies/${replyId}/react`, { reaction })
  },

  // ===== POLLS =====

  // Vote in poll
  votePoll(topicId, optionId) {
    return apiClient.post(`/forum/topics/${topicId}/poll/vote`, { option_id: optionId })
  },

  // ===== BOOKMARKS =====

  // Bookmark topic
  bookmarkTopic(topicId) {
    return apiClient.post(`/forum/topics/${topicId}/bookmark`)
  },

  // Remove bookmark
  removeBookmark(topicId) {
    return apiClient.delete(`/forum/topics/${topicId}/bookmark`)
  },

  // Get user's bookmarks
  getBookmarks() {
    return apiClient.get('/forum/bookmarks')
  },

  // ===== SEARCH =====

  // Search topics
  searchTopics(query, params = {}) {
    return apiClient.get('/forum/search', { params: { q: query, ...params } })
  },

  // Advanced search
  advancedSearch(data) {
    return apiClient.post('/forum/search/advanced', data)
  },

  // ===== USER STATS =====

  // Get user's forum stats
  getUserStats(userId) {
    return apiClient.get(`/forum/users/${userId}/stats`)
  },

  // Get user's topics
  getUserTopics(userId, params = {}) {
    return apiClient.get(`/forum/users/${userId}/topics`, { params })
  },

  // Get user's replies
  getUserReplies(userId, params = {}) {
    return apiClient.get(`/forum/users/${userId}/replies`, { params })
  },

  // ===== MODERATION =====

  // Report content
  reportContent(data) {
    return apiClient.post('/forum/reports', data)
  },

  // Get reports (moderator only)
  getReports(params = {}) {
    return apiClient.get('/forum/reports', { params })
  }
}
