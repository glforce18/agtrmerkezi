<template>
  <article
    :class="[
      'forum-topic-card forum-card forum-card--interactive forum-hover-scale',
      {
        'forum-topic-card--pinned': topic.isPinned,
        'forum-topic-card--solved': topic.isSolved,
        'forum-topic-card--unread': topic.isUnread
      }
    ]"
    @click="navigateToTopic"
    @keydown="handleKeydown"
    role="article"
    tabindex="0"
    :aria-label="`Konu: ${topic.title}`"
  >
    <!-- State badges row -->
    <div class="forum-topic-card__badges" v-if="showBadges">
      <span v-if="topic.isPinned" class="forum-badge forum-badge--pinned">
        <PinIcon class="w-3 h-3" />
        Sabit
      </span>
      <span v-if="topic.isSolved" class="forum-badge forum-badge--solved">
        <CheckCircleIcon class="w-3 h-3" />
        Cozuldu
      </span>
      <span v-if="topic.isLocked" class="forum-badge forum-badge--locked">
        <LockIcon class="w-3 h-3" />
        Kilitli
      </span>
      <span v-if="topic.isHot && !topic.isPinned" class="forum-badge forum-badge--hot">
        <FlameIcon class="w-3 h-3" />
        Populer
      </span>
    </div>

    <!-- Main content -->
    <div class="forum-topic-card__content">
      <!-- Author avatar -->
      <div class="forum-topic-card__avatar">
        <n-avatar
          round
          :size="compact ? 40 : 48"
          :src="topic.authorAvatar"
          :fallback-src="defaultAvatar"
          lazy
          :intersection-observer-options="{ rootMargin: '100px' }"
        />
        <div
          v-if="topic.authorOnline"
          class="forum-topic-card__online-indicator"
          role="status"
          aria-label="Cevrimici"
        />
      </div>

      <!-- Topic info -->
      <div class="forum-topic-card__info">
        <!-- Title -->
        <h3 class="forum-topic-title">
          <span v-if="topic.isUnread" class="forum-topic-card__unread-dot" aria-label="Okunmamis" />
          {{ topic.title }}
        </h3>

        <!-- Meta info -->
        <div class="forum-meta forum-topic-card__meta">
          <span class="forum-topic-card__author">
            <UserIcon class="w-3.5 h-3.5" />
            {{ topic.author }}
          </span>
          <span class="forum-topic-card__divider" aria-hidden="true"></span>
          <span class="forum-topic-card__time">
            <ClockIcon class="w-3.5 h-3.5" />
            {{ topic.created }}
          </span>
          <span v-if="topic.categoryName" class="forum-topic-card__divider" aria-hidden="true"></span>
          <span v-if="topic.categoryName" class="forum-topic-card__category">
            <FolderIcon class="w-3.5 h-3.5" />
            {{ topic.categoryName }}
          </span>
        </div>

        <!-- Tags -->
        <div v-if="topic.tags?.length && showTags" class="forum-topic-card__tags">
          <span
            v-for="tag in topic.tags.slice(0, 3)"
            :key="tag"
            class="forum-tag"
          >
            #{{ tag }}
          </span>
          <span v-if="topic.tags.length > 3" class="forum-tag">
            +{{ topic.tags.length - 3 }}
          </span>
        </div>
      </div>

      <!-- Stats -->
      <div class="forum-topic-card__stats">
        <div class="forum-stat-pill" title="Yanitlar">
          <MessageSquareIcon class="forum-stat-pill__icon w-4 h-4" />
          <span class="forum-stat-pill__value">{{ formatNumber(topic.replies || 0) }}</span>
        </div>
        <div class="forum-stat-pill" title="Goruntulenme">
          <EyeIcon class="forum-stat-pill__icon w-4 h-4" />
          <span class="forum-stat-pill__value">{{ formatNumber(topic.views || 0) }}</span>
        </div>
        <div v-if="!compact" class="forum-stat-pill" title="Begeniler">
          <HeartIcon class="forum-stat-pill__icon w-4 h-4" />
          <span class="forum-stat-pill__value">{{ formatNumber(topic.likes || 0) }}</span>
        </div>
      </div>

      <!-- Last reply info (optional) -->
      <div v-if="topic.lastReply && !compact" class="forum-topic-card__last-reply">
        <span class="forum-meta">Son yanit:</span>
        <n-avatar round :size="20" :src="topic.lastReply.avatar" />
        <span class="forum-meta">{{ topic.lastReply.author }}</span>
        <span class="forum-meta">{{ topic.lastReply.time }}</span>
      </div>
    </div>

    <!-- Arrow indicator -->
    <div class="forum-topic-card__arrow" aria-hidden="true">
      <ChevronRightIcon class="w-5 h-5" />
    </div>
  </article>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  PinIcon,
  CheckCircleIcon,
  LockIcon,
  FlameIcon,
  UserIcon,
  ClockIcon,
  FolderIcon,
  MessageSquareIcon,
  EyeIcon,
  HeartIcon,
  ChevronRightIcon
} from 'lucide-vue-next'

import { computed } from 'vue'

const props = defineProps({
  topic: {
    type: Object,
    required: true,
    validator: (topic) => {
      if (!topic || typeof topic.id === 'undefined') {
        console.warn('[ForumTopicCard] topic.id is required')
        return false
      }
      if (typeof topic.title !== 'string') {
        console.warn('[ForumTopicCard] topic.title must be a string')
        return false
      }
      return true
    }
  },
  compact: {
    type: Boolean,
    default: false
  },
  showBadges: {
    type: Boolean,
    default: true
  },
  showTags: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const router = useRouter()

const defaultAvatar = '/images/default-avatar.png'

// Computed properties for safe access
const topicTitle = computed(() => props.topic.title || 'Basliksiz Konu')
const topicAuthor = computed(() => props.topic.author || 'Anonim')
const topicReplies = computed(() => props.topic.replies || 0)
const topicViews = computed(() => props.topic.views || 0)
const topicLikes = computed(() => props.topic.likes || 0)
const hasBadges = computed(() => props.topic.isPinned || props.topic.isSolved || props.topic.isLocked || props.topic.isHot)
const visibleTags = computed(() => (props.topic.tags || []).slice(0, 3))
const remainingTagsCount = computed(() => Math.max(0, (props.topic.tags?.length || 0) - 3))

const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const navigateToTopic = (event) => {
  // Prevent navigation if clicking on a link inside the card
  if (event.target.tagName === 'A') return

  emit('click', props.topic)
  // Use slug if available, fallback to id for navigation
  const topicPath = props.topic.slug || props.topic.id
  router.push(`/forum/topic/${topicPath}`)
}

// Keyboard navigation handler
const handleKeydown = (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    navigateToTopic(event)
  }
}
</script>

<style scoped>
.forum-topic-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 20px;
  position: relative;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 15, 20, 0.95) 100%);
  border: 1px solid rgba(71, 85, 105, 0.3);
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.forum-topic-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.02), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.forum-topic-card:hover {
  border-color: rgba(249, 115, 22, 0.4);
  transform: translateY(-2px) scale(1.005);
  box-shadow:
    0 10px 40px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(249, 115, 22, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.forum-topic-card:hover::before {
  transform: translateX(100%);
}

.forum-topic-card--pinned {
  border-left: 3px solid #f97316;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.05) 0%, rgba(11, 15, 20, 0.95) 100%);
}

.forum-topic-card--pinned:hover {
  border-color: rgba(249, 115, 22, 0.6);
  box-shadow:
    0 10px 40px rgba(249, 115, 22, 0.2),
    inset 0 0 40px rgba(249, 115, 22, 0.03);
}

.forum-topic-card--solved {
  border-left: 3px solid var(--forum-success);
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.03) 0%, rgba(11, 15, 20, 0.95) 100%);
}

.forum-topic-card--solved:hover {
  border-color: rgba(34, 197, 94, 0.5);
  box-shadow:
    0 10px 40px rgba(34, 197, 94, 0.15),
    inset 0 0 40px rgba(34, 197, 94, 0.02);
}

.forum-topic-card--unread::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, var(--forum-link), var(--forum-accent));
  animation: unread-pulse 2s ease-in-out infinite;
}

@keyframes unread-pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 10px rgba(79, 140, 255, 0.5); }
  50% { opacity: 0.7; box-shadow: 0 0 20px rgba(79, 140, 255, 0.8); }
}

.forum-topic-card__badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.forum-topic-card__content {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 16px;
  align-items: center;
}

.forum-topic-card__avatar {
  position: relative;
}

.forum-topic-card__online-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: var(--forum-success);
  border: 2px solid var(--forum-bg-card);
  border-radius: 50%;
}

.forum-topic-card__info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.forum-topic-card__unread-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: var(--forum-link);
  border-radius: 50%;
  margin-right: 8px;
}

.forum-topic-card__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.forum-topic-card__author,
.forum-topic-card__time,
.forum-topic-card__category {
  display: flex;
  align-items: center;
  gap: 4px;
}

.forum-topic-card__divider {
  width: 4px;
  height: 4px;
  background: var(--forum-muted);
  border-radius: 50%;
  opacity: 0.5;
}

.forum-topic-card__tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.forum-topic-card__stats {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.forum-topic-card__last-reply {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--forum-bg-hover);
  border-radius: var(--forum-radius-sm);
}

.forum-topic-card__arrow {
  color: var(--forum-muted);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.5;
}

.forum-topic-card:hover .forum-topic-card__arrow {
  transform: translateX(6px);
  color: var(--forum-accent);
  opacity: 1;
  filter: drop-shadow(0 0 8px rgba(34, 211, 238, 0.5));
}

/* Stats enhancement */
.forum-topic-card__stats {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.forum-topic-card:hover .forum-stat-pill {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
}

.forum-topic-card:hover .forum-stat-pill__icon {
  color: var(--forum-brand);
}

/* Responsive */
@media (max-width: 768px) {
  .forum-topic-card__content {
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto;
  }

  .forum-topic-card__stats {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }

  .forum-topic-card__arrow,
  .forum-topic-card__last-reply {
    display: none;
  }
}
</style>
