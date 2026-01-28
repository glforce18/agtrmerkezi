import apiClient from './client'

/**
 * Forum API Service - Updated for Modular API v3
 * Uses /api/forum endpoints (modular structure)
 */
export default {
  // Categories
  getCategories() {
    return apiClient.get('/forum/categories')  // Already correct
  },

  getCategory(slugOrId) {
    return apiClient.get(`/forum/categories/${slugOrId}`)  // NEW endpoint
  },

  // Topics
  getTopics(params = {}) {
    return apiClient.get('/forum/topics', { params })  // Already correct
  },

  getTopicsByCategory(categoryId, params = {}) {
    // Updated to use new modular structure
    return apiClient.get('/forum/topics', { params: { ...params, category_id: categoryId } })
  },

  getTopic(slugOrId) {
    return apiClient.get(`/forum/topics/${slugOrId}`)  // Already correct
  },

  createTopic(data) {
    return apiClient.post('/forum/topics', data)  // Already correct
  },

  updateTopic(id, data) {
    return apiClient.put(`/forum/topics/${id}`, data)  // NEW endpoint
  },

  deleteTopic(id) {
    return apiClient.delete(`/forum/topics/${id}`)  // NEW endpoint
  },

  // Replies
  getReplies(topicId, params = {}) {
    return apiClient.get(`/forum/replies/topic/${topicId}`, { params })  // Updated to modular endpoint
  },

  createReply(data) {
    return apiClient.post('/forum/replies', data)  // Updated to modular endpoint (data should include topic_id)
  },

  updateReply(id, data) {
    return apiClient.put(`/forum/replies/${id}`, data)  // NEW endpoint
  },

  deleteReply(id) {
    return apiClient.delete(`/forum/replies/${id}`)  // NEW endpoint
  },

  // Like System
  likeTopic(topicId) {
    return apiClient.post(`/forum/topics/${topicId}/like`)
  },

  unlikeTopic(topicId) {
    return apiClient.delete(`/forum/topics/${topicId}/like`)
  },

  likeReply(replyId) {
    return apiClient.post(`/forum/replies/${replyId}/like`)
  },

  unlikeReply(replyId) {
    return apiClient.delete(`/forum/replies/${replyId}/like`)
  },

  // Bookmark System
  bookmarkTopic(topicId) {
    return apiClient.post(`/forum/topics/${topicId}/bookmark`)
  },

  unbookmarkTopic(topicId) {
    return apiClient.delete(`/forum/topics/${topicId}/bookmark`)
  },

  getBookmarks(params = {}) {
    return apiClient.get('/forum/bookmarks', { params })
  },

  // Best Answer
  markBestAnswer(replyId) {
    return apiClient.post(`/forum/replies/${replyId}/best`)
  },

  unmarkBestAnswer(replyId) {
    return apiClient.delete(`/forum/replies/${replyId}/best`)
  },

  // Stats
  getForumStats() {
    return apiClient.get('/forum/stats')
  },

  getTrendingTopics(params = {}) {
    return apiClient.get('/forum/trending', { params })
  },

  // Moderation (NEW)
  reportContent(data) {
    return apiClient.post('/forum/moderation/reports', data)
  },

  moderateTopic(topicId, action) {
    return apiClient.post(`/forum/moderation/topics/${topicId}/moderate`, { action })
  }
}
