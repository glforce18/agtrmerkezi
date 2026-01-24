// ============================================
// AGTR v6.0 - Forum Advanced Services
// Frontend API Services for 20 New Features
// ============================================

import api from './api'

// ============ Reactions API ============

export const reactionApi = {
  // Add/update/remove reaction
  addReaction: (contentType, contentId, reactionType) =>
    api.post('/forum/v2/reactions', {
      content_type: contentType,
      content_id: contentId,
      reaction_type: reactionType
    }),

  // Get reactions for content
  getReactions: (contentType, contentId) =>
    api.get(`/forum/v2/reactions/${contentType}/${contentId}`),

  // Get users who reacted
  getReactionUsers: (contentType, contentId, reactionType, limit = 20) =>
    api.get(`/forum/v2/reactions/${contentType}/${contentId}/users/${reactionType}`, {
      params: { limit }
    })
}

// ============ Polls API ============

export const pollApi = {
  // Create poll
  createPoll: (data) =>
    api.post('/forum/v2/polls', data),

  // Vote on poll
  vote: (pollId, optionIds) =>
    api.post(`/forum/v2/polls/${pollId}/vote`, { option_ids: optionIds }),

  // Get poll details
  getPoll: (pollId) =>
    api.get(`/forum/v2/polls/${pollId}`),

  // Get poll by topic
  getTopicPoll: (topicId) =>
    api.get(`/forum/v2/topics/${topicId}/poll`)
}

// ============ Templates API ============

export const templateApi = {
  // Get templates
  getTemplates: (categoryId = null) =>
    api.get('/forum/v2/templates', {
      params: categoryId ? { category_id: categoryId } : {}
    }),

  // Create template (admin)
  createTemplate: (data) =>
    api.post('/forum/v2/templates', data),

  // Delete template (admin)
  deleteTemplate: (templateId) =>
    api.delete(`/forum/v2/templates/${templateId}`)
}

// ============ Drafts API ============

export const draftApi = {
  // Save draft
  saveDraft: (data) =>
    api.post('/forum/v2/drafts', data),

  // Get draft
  getDraft: (draftType, topicId = null) =>
    api.get(`/forum/v2/drafts/${draftType}`, {
      params: topicId ? { topic_id: topicId } : {}
    }),

  // Delete draft
  deleteDraft: (draftType, topicId = null) =>
    api.delete(`/forum/v2/drafts/${draftType}`, {
      params: topicId ? { topic_id: topicId } : {}
    }),

  // Get all drafts
  getAllDrafts: () =>
    api.get('/forum/v2/drafts')
}

// ============ Spam Filter API (Admin) ============

export const spamApi = {
  // Get rules (admin)
  getRules: () =>
    api.get('/forum/v2/spam/rules'),

  // Create rule (admin)
  createRule: (data) =>
    api.post('/forum/v2/spam/rules', data),

  // Delete rule (admin)
  deleteRule: (ruleId) =>
    api.delete(`/forum/v2/spam/rules/${ruleId}`),

  // Check content
  checkContent: (content) =>
    api.post('/forum/v2/spam/check', { content })
}

// ============ Search API ============

export const searchApi = {
  // Advanced search
  advancedSearch: (data, page = 1, limit = 20) =>
    api.post('/forum/v2/search', data, {
      params: { page, limit }
    }),

  // Quick search
  quickSearch: (query, page = 1, limit = 20) =>
    api.get('/forum/v2/search', {
      params: { q: query, page, limit }
    }),

  // Find similar topics
  findSimilar: (title, content) =>
    api.post('/forum/v2/search/similar', { title, content })
}

// ============ Reputation API ============

export const reputationApi = {
  // Get user reputation
  getUserReputation: (userId) =>
    api.get(`/forum/v2/reputation/${userId}`),

  // Get my reputation
  getMyReputation: () =>
    api.get('/forum/v2/reputation/me'),

  // Get leaderboard
  getLeaderboard: (timeframe = 'all', limit = 10) =>
    api.get('/forum/v2/leaderboard', {
      params: { timeframe, limit }
    })
}

// ============ Bookmarks API ============

export const bookmarkApi = {
  // Toggle bookmark
  toggleBookmark: (topicId) =>
    api.post(`/forum/v2/bookmarks/${topicId}`),

  // Get my bookmarks
  getMyBookmarks: (page = 1, limit = 20) =>
    api.get('/forum/v2/bookmarks', {
      params: { page, limit }
    }),

  // Check if bookmarked
  isBookmarked: (topicId) =>
    api.get(`/forum/v2/bookmarks/${topicId}/check`)
}

// ============ Threading API ============

export const threadingApi = {
  // Get reply thread
  getReplyThread: (replyId) =>
    api.get(`/forum/v2/replies/${replyId}/thread`)
}

// ============ Infinite Scroll API ============

export const infiniteScrollApi = {
  // Get topics with cursor
  getTopicsCursor: (cursor = null, limit = 20, categoryId = null) =>
    api.get('/forum/v2/topics/cursor', {
      params: {
        ...(cursor && { cursor }),
        limit,
        ...(categoryId && { category_id: categoryId })
      }
    }),

  // Get replies with cursor
  getRepliesCursor: (topicId, cursor = null, limit = 20) =>
    api.get(`/forum/v2/replies/cursor/${topicId}`, {
      params: {
        ...(cursor && { cursor }),
        limit
      }
    })
}

// ============ Export All ============

export default {
  reaction: reactionApi,
  poll: pollApi,
  template: templateApi,
  draft: draftApi,
  spam: spamApi,
  search: searchApi,
  reputation: reputationApi,
  bookmark: bookmarkApi,
  threading: threadingApi,
  infiniteScroll: infiniteScrollApi
}
