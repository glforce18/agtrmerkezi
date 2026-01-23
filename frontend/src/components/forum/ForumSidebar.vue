<template>
  <div class="forum-sidebar">
    <!-- Header -->
    <div class="forum-sidebar__header">
      <h2 class="forum-heading forum-heading--sm">Kategoriler</h2>
    </div>

    <!-- Categories Navigation -->
    <nav class="forum-category-nav" aria-label="Forum kategorileri">
      <div
        v-for="category in categories"
        :key="category.id"
        :class="[
          'forum-category-item',
          { 'forum-category-item--active': isActive(category.id) }
        ]"
        @click="navigateToCategory(category)"
        @keydown="(e) => handleKeydown(e, category)"
        role="button"
        tabindex="0"
        :aria-current="isActive(category.id) ? 'page' : undefined"
      >
        <div
          class="forum-category-item__icon"
          :style="category.color ? { background: `${category.color}20` } : {}"
        >
          <span v-if="category.emoji" class="text-lg">{{ category.emoji }}</span>
          <component
            v-else
            :is="category.icon || DefaultIcon"
            class="w-4 h-4"
            :style="category.color ? { color: category.color } : {}"
          />
        </div>
        <span class="forum-category-item__name">{{ category.name }}</span>
        <span v-if="category.topicCount" class="forum-category-item__count">
          {{ formatCount(category.topicCount) }}
        </span>
      </div>
    </nav>

    <!-- Quick Stats -->
    <div class="forum-sidebar__stats" v-if="showStats">
      <h3 class="forum-heading forum-heading--sm forum-sidebar__section-title">
        Istatistikler
      </h3>
      <div class="forum-sidebar__stat-grid">
        <div class="forum-stat-pill">
          <FileTextIcon class="forum-stat-pill__icon w-4 h-4" />
          <span class="forum-stat-pill__value">{{ formatCount(topicsCount) }}</span>
          <span>Konu</span>
        </div>
        <div class="forum-stat-pill">
          <MessageSquareIcon class="forum-stat-pill__icon w-4 h-4" />
          <span class="forum-stat-pill__value">{{ formatCount(postsCount) }}</span>
          <span>Gonderi</span>
        </div>
        <div class="forum-stat-pill">
          <UsersIcon class="forum-stat-pill__icon w-4 h-4" />
          <span class="forum-stat-pill__value">{{ formatCount(membersCount) }}</span>
          <span>Uye</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  FileTextIcon,
  MessageSquareIcon,
  UsersIcon,
  FolderIcon
} from 'lucide-vue-next'

const DefaultIcon = FolderIcon

const props = defineProps({
  categories: {
    type: Array,
    default: () => [],
    validator: (categories) => {
      if (!Array.isArray(categories)) return false
      return categories.every(cat => cat && (typeof cat.id !== 'undefined'))
    }
  },
  stats: {
    type: Object,
    default: () => ({
      topics: 0,
      posts: 0,
      members: 0
    })
  },
  showStats: {
    type: Boolean,
    default: true
  },
  activeCategory: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['category-click'])

const router = useRouter()
const route = useRoute()

// Computed for safe stats access
const topicsCount = computed(() => props.stats?.topics || props.stats?.totalTopics || 0)
const postsCount = computed(() => props.stats?.posts || props.stats?.totalPosts || 0)
const membersCount = computed(() => props.stats?.members || props.stats?.totalMembers || 0)

const isActive = (categoryId) => {
  if (props.activeCategory !== null) {
    return String(props.activeCategory) === String(categoryId)
  }
  return route.params.id === String(categoryId)
}

const formatCount = (count) => {
  if (typeof count !== 'number') return '0'
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'K'
  }
  return count.toString()
}

const navigateToCategory = (category) => {
  emit('category-click', category)
  // Use slug if available, fallback to id
  const categoryPath = category.slug || category.id
  router.push(`/forum/category/${categoryPath}`)
}

// Keyboard navigation handler
const handleKeydown = (event, category) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    navigateToCategory(category)
  }
}
</script>

<style scoped>
.forum-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 90px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--forum-border) transparent;
}

.forum-sidebar::-webkit-scrollbar {
  width: 4px;
}

.forum-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.forum-sidebar::-webkit-scrollbar-thumb {
  background: var(--forum-border);
  border-radius: 2px;
}

.forum-sidebar__header {
  padding: 0 16px;
}

.forum-sidebar__section-title {
  padding: 0 16px;
  margin-bottom: 12px;
  color: var(--forum-muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.forum-sidebar__stats {
  padding-top: 16px;
  border-top: 1px solid var(--forum-border);
}

.forum-sidebar__stat-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 16px;
}
</style>
