// ============================================
// AGTR v6.0 - Forum Advanced Components
// Export all advanced forum components
// ============================================

// Reactions & Engagement
export { default as ForumReactions } from '../ForumReactions.vue'
export { default as ForumPoll } from '../ForumPoll.vue'
export { default as ForumBookmarkButton } from '../ForumBookmarkButton.vue'

// Content Creation
export { default as ForumDraftIndicator } from '../ForumDraftIndicator.vue'
export { default as ForumTemplateSelector } from '../ForumTemplateSelector.vue'
export { default as ForumLivePreview } from '../ForumLivePreview.vue'
export { default as ForumSimilarTopics } from '../ForumSimilarTopics.vue'

// Navigation & Search
export { default as ForumAdvancedSearch } from '../ForumAdvancedSearch.vue'
export { default as ForumInfiniteScroll } from '../ForumInfiniteScroll.vue'

// User & Reputation
export { default as ForumReputationCard } from '../ForumReputationCard.vue'
export { default as ForumLeaderboard } from '../ForumLeaderboard.vue'

// Threading
export { default as ForumQuoteThread } from '../ForumQuoteThread.vue'

// Admin
export { default as ForumSpamRules } from '../ForumSpamRules.vue'

// Default export with all components
export default {
  ForumReactions: () => import('../ForumReactions.vue'),
  ForumPoll: () => import('../ForumPoll.vue'),
  ForumBookmarkButton: () => import('../ForumBookmarkButton.vue'),
  ForumDraftIndicator: () => import('../ForumDraftIndicator.vue'),
  ForumTemplateSelector: () => import('../ForumTemplateSelector.vue'),
  ForumLivePreview: () => import('../ForumLivePreview.vue'),
  ForumSimilarTopics: () => import('../ForumSimilarTopics.vue'),
  ForumAdvancedSearch: () => import('../ForumAdvancedSearch.vue'),
  ForumInfiniteScroll: () => import('../ForumInfiniteScroll.vue'),
  ForumReputationCard: () => import('../ForumReputationCard.vue'),
  ForumLeaderboard: () => import('../ForumLeaderboard.vue'),
  ForumQuoteThread: () => import('../ForumQuoteThread.vue'),
  ForumSpamRules: () => import('../ForumSpamRules.vue')
}
