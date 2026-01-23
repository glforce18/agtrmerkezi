<template>
  <article
    :class="[
      'forum-category-card forum-card forum-card--interactive forum-hover-scale',
      { 'forum-category-card--hot': category.isHot }
    ]"
    @click="navigateToCategory"
    @keydown="handleKeydown"
    role="article"
    tabindex="0"
    :aria-label="`Kategori: ${category.name}`"
  >
    <!-- Top gradient bar -->
    <div
      class="forum-category-card__gradient-bar"
      :class="getGradientClass(category.gradient)"
      :style="category.color ? { background: `linear-gradient(135deg, ${category.color}, ${adjustColor(category.color, -20)})` } : {}"
    />

    <div class="forum-category-card__content">
      <!-- Icon -->
      <div class="forum-category-card__icon-wrapper">
        <div
          :class="['forum-category-card__icon', getGradientClass(category.gradient)]"
          :style="category.color ? { background: `linear-gradient(135deg, ${category.color}, ${adjustColor(category.color, -20)})` } : {}"
        >
          <span v-if="category.emoji" class="text-2xl">{{ category.emoji }}</span>
          <component v-else :is="category.icon || DefaultIcon" class="w-7 h-7 text-white" />
        </div>
        <div class="forum-category-card__icon-glow" :style="category.color ? { background: category.color } : {}" />
      </div>

      <!-- Info -->
      <div class="forum-category-card__info">
        <div class="forum-category-card__header">
          <h3 class="forum-heading forum-heading--md forum-category-card__name">
            {{ category.name }}
            <span v-if="category.isHot" class="forum-badge forum-badge--hot forum-category-card__hot-badge">
              <FlameIcon class="w-3 h-3" />
              HOT
            </span>
          </h3>
          <ChevronRightIcon class="forum-category-card__arrow w-5 h-5" />
        </div>

        <p v-if="category.description" class="forum-meta forum-category-card__description">
          {{ category.description }}
        </p>

        <!-- Stats -->
        <div class="forum-category-card__stats">
          <div class="forum-stat-pill">
            <FileTextIcon class="forum-stat-pill__icon w-3.5 h-3.5" />
            <span class="forum-stat-pill__value">{{ formatNumber(category.topics || 0) }}</span>
            <span>Konu</span>
          </div>
          <div class="forum-stat-pill">
            <MessageSquareIcon class="forum-stat-pill__icon w-3.5 h-3.5" />
            <span class="forum-stat-pill__value">{{ formatNumber(category.posts || 0) }}</span>
            <span>Gonderi</span>
          </div>
          <div v-if="category.newToday" class="forum-stat-pill forum-stat-pill--highlight">
            <SparklesIcon class="forum-stat-pill__icon w-3.5 h-3.5" />
            <span class="forum-stat-pill__value">+{{ category.newToday }}</span>
            <span>bugun</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Latest topic preview -->
    <div v-if="category.latestTopic && showLatestTopic" class="forum-category-card__latest">
      <div class="forum-category-card__latest-header">
        <span class="forum-meta">Son konu:</span>
      </div>
      <div class="forum-category-card__latest-content">
        <n-avatar round :size="28" :src="category.latestTopic.authorAvatar" />
        <div class="forum-category-card__latest-info">
          <p class="forum-category-card__latest-title">
            {{ category.latestTopic.title }}
          </p>
          <span class="forum-meta">
            {{ category.latestTopic.author }} - {{ category.latestTopic.time }}
          </span>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  FlameIcon,
  FileTextIcon,
  MessageSquareIcon,
  SparklesIcon,
  ChevronRightIcon,
  FolderIcon
} from 'lucide-vue-next'

const DefaultIcon = FolderIcon

const props = defineProps({
  category: {
    type: Object,
    required: true,
    validator: (cat) => {
      if (!cat || typeof cat.id === 'undefined') {
        console.warn('[ForumCategoryItem] category.id is required')
        return false
      }
      return true
    }
  },
  showLatestTopic: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const router = useRouter()

// Computed properties for safe data access
const categoryName = computed(() => props.category.name || 'Kategori')
const categoryDescription = computed(() => props.category.description || '')
const topicsCount = computed(() => props.category.topics || 0)
const postsCount = computed(() => props.category.posts || 0)
const newTodayCount = computed(() => props.category.newToday || 0)
const isHot = computed(() => !!props.category.isHot)
const hasLatestTopic = computed(() => props.category.latestTopic && props.showLatestTopic)

const formatNumber = (num) => {
  if (typeof num !== 'number') return '0'
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const getGradientClass = (gradient) => {
  const gradients = {
    'primary-secondary': 'gradient-orange-purple',
    'secondary-accent': 'gradient-purple-cyan',
    'accent-error': 'gradient-cyan-red',
    'primary-accent': 'gradient-orange-cyan',
    'warning-success': 'gradient-yellow-green'
  }
  return gradients[gradient] || 'gradient-orange-purple'
}

const adjustColor = (color, amount) => {
  // Simple color adjustment - darken or lighten
  const hex = color.replace('#', '')
  const num = parseInt(hex, 16)
  const r = Math.max(0, Math.min(255, (num >> 16) + amount))
  const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amount))
  const b = Math.max(0, Math.min(255, (num & 0x0000FF) + amount))
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`
}

const navigateToCategory = (event) => {
  // Prevent navigation if clicking on a link
  if (event?.target?.tagName === 'A') return

  emit('click', props.category)
  // Use slug if available, fallback to id
  const categoryPath = props.category.slug || props.category.id
  router.push(`/forum/category/${categoryPath}`)
}

// Keyboard navigation handler
const handleKeydown = (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    navigateToCategory(event)
  }
}
</script>

<style scoped>
.forum-category-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.forum-category-card__gradient-bar {
  height: 3px;
  width: 100%;
}

.forum-category-card__content {
  display: flex;
  gap: 16px;
  padding: 20px;
}

.forum-category-card__icon-wrapper {
  position: relative;
  flex-shrink: 0;
}

.forum-category-card__icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease;
}

.forum-category-card:hover .forum-category-card__icon {
  transform: scale(1.05) rotate(3deg);
}

.forum-category-card__icon-glow {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  opacity: 0;
  filter: blur(12px);
  transition: opacity 0.3s ease;
}

.forum-category-card:hover .forum-category-card__icon-glow {
  opacity: 0.4;
}

.forum-category-card__info {
  flex: 1;
  min-width: 0;
}

.forum-category-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

.forum-category-card__name {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.forum-category-card__hot-badge {
  font-size: 10px;
  padding: 2px 6px;
}

.forum-category-card__arrow {
  color: var(--forum-muted);
  flex-shrink: 0;
  transition: transform 0.2s ease, color 0.2s ease;
}

.forum-category-card:hover .forum-category-card__arrow {
  transform: translateX(4px);
  color: var(--forum-accent);
}

.forum-category-card__description {
  margin-bottom: 12px;
  line-height: 1.5;
}

.forum-category-card__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.forum-stat-pill--highlight {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.forum-category-card__latest {
  padding: 12px 20px;
  background: var(--forum-bg-hover);
  border-top: 1px solid var(--forum-border);
}

.forum-category-card__latest-header {
  margin-bottom: 8px;
}

.forum-category-card__latest-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.forum-category-card__latest-info {
  min-width: 0;
}

.forum-category-card__latest-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
  transition: color 0.2s ease;
}

.forum-category-card:hover .forum-category-card__latest-title {
  color: var(--forum-link);
}

/* Gradient classes */
.gradient-orange-purple {
  background: linear-gradient(135deg, #f97316, #8b5cf6);
}

.gradient-purple-cyan {
  background: linear-gradient(135deg, #8b5cf6, #22d3ee);
}

.gradient-cyan-red {
  background: linear-gradient(135deg, #22d3ee, #ef4444);
}

.gradient-orange-cyan {
  background: linear-gradient(135deg, #f97316, #22d3ee);
}

.gradient-yellow-green {
  background: linear-gradient(135deg, #eab308, #22c55e);
}
</style>
