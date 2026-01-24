/**
 * AGTR Merkezi - Forum Component Library
 *
 * Export all forum components for easy importing
 */

// Core Components
export { default as ForumLayout } from './ForumLayout.vue'
export { default as ForumSidebar } from './ForumSidebar.vue'
export { default as ForumTopicCard } from './ForumTopicCard.vue'
export { default as ForumPostCard } from './ForumPostCard.vue'
export { default as ForumCategoryItem } from './ForumCategoryItem.vue'
export { default as ForumBestAnswer } from './ForumBestAnswer.vue'
export { default as ForumBadges } from './ForumBadges.vue'
export { default as ForumSkeleton } from './ForumSkeleton.vue'
export { default as GameMapGallery } from './GameMapGallery.vue'

// Advanced Features - v6.0
export { default as ForumReactions } from './ForumReactions.vue'
export { default as ForumPoll } from './ForumPoll.vue'
export { default as ForumBookmarkButton } from './ForumBookmarkButton.vue'
export { default as ForumDraftIndicator } from './ForumDraftIndicator.vue'
export { default as ForumTemplateSelector } from './ForumTemplateSelector.vue'
export { default as ForumLivePreview } from './ForumLivePreview.vue'
export { default as ForumSimilarTopics } from './ForumSimilarTopics.vue'
export { default as ForumAdvancedSearch } from './ForumAdvancedSearch.vue'
export { default as ForumInfiniteScroll } from './ForumInfiniteScroll.vue'
export { default as ForumReputationCard } from './ForumReputationCard.vue'
export { default as ForumLeaderboard } from './ForumLeaderboard.vue'
export { default as ForumQuoteThread } from './ForumQuoteThread.vue'
export { default as ForumSpamRules } from './ForumSpamRules.vue'

// Default export with all components
export default {
  ForumLayout: () => import('./ForumLayout.vue'),
  ForumSidebar: () => import('./ForumSidebar.vue'),
  ForumTopicCard: () => import('./ForumTopicCard.vue'),
  ForumPostCard: () => import('./ForumPostCard.vue'),
  ForumCategoryItem: () => import('./ForumCategoryItem.vue'),
  ForumBestAnswer: () => import('./ForumBestAnswer.vue'),
  ForumBadges: () => import('./ForumBadges.vue'),
  ForumSkeleton: () => import('./ForumSkeleton.vue'),
  GameMapGallery: () => import('./GameMapGallery.vue'),
  // Advanced Features
  ForumReactions: () => import('./ForumReactions.vue'),
  ForumPoll: () => import('./ForumPoll.vue'),
  ForumBookmarkButton: () => import('./ForumBookmarkButton.vue'),
  ForumDraftIndicator: () => import('./ForumDraftIndicator.vue'),
  ForumTemplateSelector: () => import('./ForumTemplateSelector.vue'),
  ForumLivePreview: () => import('./ForumLivePreview.vue'),
  ForumSimilarTopics: () => import('./ForumSimilarTopics.vue'),
  ForumAdvancedSearch: () => import('./ForumAdvancedSearch.vue'),
  ForumInfiniteScroll: () => import('./ForumInfiniteScroll.vue'),
  ForumReputationCard: () => import('./ForumReputationCard.vue'),
  ForumLeaderboard: () => import('./ForumLeaderboard.vue'),
  ForumQuoteThread: () => import('./ForumQuoteThread.vue'),
  ForumSpamRules: () => import('./ForumSpamRules.vue')
}
