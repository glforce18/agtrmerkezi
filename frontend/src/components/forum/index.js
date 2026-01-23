/**
 * AGTR Merkezi - Forum Component Library
 *
 * Export all forum components for easy importing
 */

export { default as ForumLayout } from './ForumLayout.vue'
export { default as ForumSidebar } from './ForumSidebar.vue'
export { default as ForumTopicCard } from './ForumTopicCard.vue'
export { default as ForumPostCard } from './ForumPostCard.vue'
export { default as ForumCategoryItem } from './ForumCategoryItem.vue'
export { default as ForumBestAnswer } from './ForumBestAnswer.vue'
export { default as ForumBadges } from './ForumBadges.vue'
export { default as ForumSkeleton } from './ForumSkeleton.vue'
export { default as GameMapGallery } from './GameMapGallery.vue'

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
  GameMapGallery: () => import('./GameMapGallery.vue')
}
