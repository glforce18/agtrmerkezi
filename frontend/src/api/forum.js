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

  // Moderation (NEW)
  reportContent(data) {
    return apiClient.post('/forum/moderation/reports', data)
  },

  moderateTopic(topicId, action) {
    return apiClient.post(`/forum/moderation/topics/${topicId}/moderate`, { action })
  }
}
