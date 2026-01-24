<template>
  <article
    :class="[
      'forum-post-card forum-card',
      {
        'forum-best-answer': post.isBestAnswer,
        'forum-best-answer--animated': post.isBestAnswer && animateBestAnswer
      }
    ]"
    :id="`post-${post.id}`"
    role="article"
    :aria-label="`${post.author} tarafindan gönderilen yanıtlar`"
  >
    <!-- Best Answer Badge -->
    <div v-if="post.isBestAnswer" class="forum-best-answer__badge">
      <CheckCircleIcon class="w-4 h-4" />
      En Iyi Cevap
    </div>

    <div class="forum-post-card__layout">
      <!-- Author Sidebar -->
      <div class="forum-author-sidebar">
        <!-- Clickable Author Profile Link -->
        <router-link
          :to="authorProfileUrl"
          class="forum-author-profile-link"
          @click.stop
        >
          <!-- Avatar with level ring -->
          <div class="forum-post-card__avatar-wrapper">
            <svg v-if="showLevelRing" class="forum-post-card__level-ring" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="3"/>
              <circle
                cx="50" cy="50" r="46" fill="none"
                :stroke="levelColor"
                stroke-width="3"
                stroke-linecap="round"
                :stroke-dasharray="`${(post.authorXpProgress || 75) * 2.89} 289`"
                transform="rotate(-90 50 50)"
                class="level-progress-ring"
              />
            </svg>
            <n-avatar
              round
              :size="64"
              :src="post.authorAvatar"
              :fallback-src="defaultAvatar"
              class="forum-post-card__avatar"
            />
            <div
              v-if="post.authorOnline"
              class="forum-post-card__online-dot"
              aria-label="Çevrimiçi"
            />
          </div>

          <!-- Author Name -->
          <h4 class="forum-author-sidebar__name">{{ post.author }}</h4>
        </router-link>

        <!-- Role Badge -->
        <span
          v-if="post.authorRole"
          :class="['forum-post-card__role', `forum-post-card__role--${post.authorRole?.toLowerCase()}`]"
        >
          {{ post.authorRole }}
        </span>

        <!-- Badges -->
        <ForumBadges
          v-if="post.authorBadges?.length"
          :badges="post.authorBadges"
          :max="5"
          class="forum-post-card__badges"
        />

        <!-- Level & XP -->
        <div v-if="showLevel" class="forum-post-card__level-info">
          <span class="forum-level-badge">
            <ZapIcon class="w-3 h-3" />
            Lv.{{ post.authorLevel || 1 }}
          </span>
          <div class="forum-xp-bar">
            <div
              class="forum-xp-bar__fill"
              :style="{ width: `${post.authorXpProgress || 0}%` }"
            />
          </div>
        </div>

        <!-- Author Stats -->
        <div class="forum-author-sidebar__stats">
          <div class="forum-author-sidebar__stat">
            <span class="forum-author-sidebar__stat-value">{{ formatNumber(post.authorPosts || 0) }}</span>
            <span class="forum-author-sidebar__stat-label">Gönderi</span>
          </div>
          <div class="forum-author-sidebar__stat">
            <span class="forum-author-sidebar__stat-value">{{ formatNumber(post.authorLikes || 0) }}</span>
            <span class="forum-author-sidebar__stat-label">Beğeni</span>
          </div>
        </div>

        <!-- Join Date -->
        <div class="forum-post-card__joined">
          <CalendarIcon class="w-3.5 h-3.5" />
          <span>{{ post.authorJoined }}</span>
        </div>
      </div>

      <!-- Post Content -->
      <div class="forum-post-card__content">
        <!-- Post Header -->
        <div class="forum-post-card__header">
          <div class="forum-meta forum-post-card__time">
            <ClockIcon class="w-4 h-4" />
            {{ post.created }}
            <span v-if="post.isEdited" class="forum-post-card__edited">
              (düzenlendi)
            </span>
          </div>

          <div class="forum-post-card__actions-menu">
            <slot name="actions">
              <n-dropdown
                v-if="showActions"
                :options="actionOptions"
                @select="handleAction"
                trigger="click"
              >
                <n-button quaternary circle size="small">
                  <MoreHorizontalIcon class="w-4 h-4" />
                </n-button>
              </n-dropdown>
            </slot>
          </div>
        </div>

        <!-- Post Body -->
        <div class="forum-post-card__body forum-body">
          <div v-if="post.htmlContent" v-html="sanitizedHtmlContent" class="prose prose-invert max-w-none" />
          <p v-else>{{ post.content }}</p>
        </div>

        <!-- Attachments -->
        <div v-if="post.attachments?.length" class="forum-post-card__attachments">
          <h5 class="forum-meta">
            <PaperclipIcon class="w-4 h-4" />
            Ekler
          </h5>
          <div class="forum-post-card__attachment-list">
            <a
              v-for="attachment in post.attachments"
              :key="attachment.id"
              :href="attachment.url"
              target="_blank"
              class="forum-post-card__attachment"
            >
              <FileIcon class="w-4 h-4" />
              <span>{{ attachment.name }}</span>
              <span class="forum-meta">({{ attachment.size }})</span>
            </a>
          </div>
        </div>

        <!-- Post Footer Actions -->
        <div class="forum-post-card__footer" role="group" aria-label="Gönderi eylemleri">
          <div class="forum-post-card__reactions">
            <button
              :class="['forum-post-card__like-btn', { 'liked': hasLiked, 'like-animating': likeAnimating }]"
              @click="handleLike"
              :disabled="!canInteract"
              :aria-pressed="hasLiked"
              :aria-label="`Begen (${postLikes} begeni)`"
              type="button"
            >
              <HeartIcon :class="['w-4 h-4', { 'like-pulse': likeAnimating }]" aria-hidden="true" />
              <span>{{ postLikes }}</span>
            </button>

            <button
              class="forum-post-card__reply-btn"
              @click="$emit('reply', post)"
              :disabled="!canInteract"
              aria-label="Bu gönderiye yanıt ver"
              type="button"
            >
              <ReplyIcon class="w-4 h-4" aria-hidden="true" />
              Yanıtla
            </button>

            <button
              class="forum-post-card__quote-btn"
              @click="$emit('quote', post)"
              :disabled="!canInteract"
              aria-label="Alinti yaparak yanıt ver"
              type="button"
            >
              <QuoteIcon class="w-4 h-4" aria-hidden="true" />
              Alintiyla Yanıtla
            </button>
          </div>

          <div class="forum-post-card__secondary-actions">
            <button
              class="forum-post-card__share-btn"
              @click="$emit('share', post)"
              aria-label="Bu gönderiyi paylaş"
              type="button"
            >
              <Share2Icon class="w-4 h-4" aria-hidden="true" />
            </button>

            <button
              v-if="canInteract"
              class="forum-post-card__report-btn"
              @click="$emit('report', post)"
              aria-label="Bu gönderiyi bildir"
              type="button"
            >
              <FlagIcon class="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, onUnmounted } from 'vue'
import DOMPurify from 'dompurify'
import ForumBadges from './ForumBadges.vue'
import {
  CheckCircleIcon,
  ZapIcon,
  CalendarIcon,
  ClockIcon,
  MoreHorizontalIcon,
  PaperclipIcon,
  FileIcon,
  HeartIcon,
  ReplyIcon,
  Share2Icon,
  FlagIcon
} from 'lucide-vue-next'

// Quote icon component (not in lucide-vue-next by default)
const QuoteIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>`
}

const props = defineProps({
  post: {
    type: Object,
    required: true,
    validator: (post) => {
      // Validate required post properties
      if (!post || typeof post.id === 'undefined') {
        console.warn('[ForumPostCard] post.id is required')
        return false
      }
      if (typeof post.author !== 'string') {
        console.warn('[ForumPostCard] post.author must be a string')
        return false
      }
      return true
    }
  },
  showLevel: {
    type: Boolean,
    default: true
  },
  showLevelRing: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  canInteract: {
    type: Boolean,
    default: true
  },
  animateBestAnswer: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['like', 'reply', 'quote', 'share', 'report', 'action'])

const defaultAvatar = '/images/default-avatar.png'
const likeAnimating = ref(false)
let likeAnimationTimer = null

// Like with animation
const handleLike = () => {
  likeAnimating.value = true
  emit('like', props.post)
  // BUGFIX: Track timeout for cleanup
  if (likeAnimationTimer) clearTimeout(likeAnimationTimer)
  likeAnimationTimer = setTimeout(() => {
    likeAnimating.value = false
    likeAnimationTimer = null
  }, 400)
}

// BUGFIX: Cleanup on unmount
onUnmounted(() => {
  if (likeAnimationTimer) {
    clearTimeout(likeAnimationTimer)
  }
})

// Computed properties for safe access with defaults
const authorLevel = computed(() => props.post.authorLevel || 1)
const authorXpProgress = computed(() => Math.min(100, Math.max(0, props.post.authorXpProgress || 0)))
const authorPosts = computed(() => props.post.authorPosts || 0)
const authorLikes = computed(() => props.post.authorLikes || 0)
const postLikes = computed(() => props.post.likes || 0)
const hasLiked = computed(() => !!props.post.hasLiked)
const isEdited = computed(() => !!props.post.isEdited)
const isBestAnswer = computed(() => !!props.post.isBestAnswer)

// Sanitized HTML content to prevent XSS
const sanitizedHtmlContent = computed(() => {
  return DOMPurify.sanitize(props.post.htmlContent || '')
})

const levelColor = computed(() => {
  const level = authorLevel.value
  if (level >= 50) return '#f97316'
  if (level >= 30) return '#8b5cf6'
  if (level >= 15) return '#22d3ee'
  return '#22c55e'
})

// Author profile URL - kullanıcı profiline yönlendirme
const authorProfileUrl = computed(() => {
  // authorId varsa ID ile, yoksa username ile profil linki
  if (props.post.authorId) {
    return `/profile/${props.post.authorId}`
  }
  // Username ile de gidilebilir
  if (props.post.author && props.post.author !== 'Anonim') {
    return `/user/${encodeURIComponent(props.post.author)}`
  }
  return '#'
})

const actionOptions = [
  { label: 'Düzenle', key: 'edit' },
  { label: 'Sil', key: 'delete' },
  { type: 'divider' },
  { label: 'Link Kopyala', key: 'copy-link' }
]

const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const handleAction = (key) => {
  emit('action', { action: key, post: props.post })
}
</script>

<style scoped>
.forum-post-card {
  position: relative;
  overflow: hidden;
}

/* Author Profile Link */
.forum-author-profile-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  cursor: pointer;
}

.forum-author-profile-link:hover {
  transform: translateY(-2px);
}

.forum-author-profile-link:hover .forum-author-sidebar__name {
  color: var(--forum-accent, #22d3ee);
}

.forum-author-profile-link:hover .forum-post-card__avatar {
  box-shadow: 0 0 0 3px var(--forum-accent, #22d3ee);
}

.forum-post-card__layout {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .forum-post-card__layout {
    flex-direction: row;
  }
}

.forum-post-card__avatar-wrapper {
  position: relative;
  width: 70px;
  height: 70px;
  margin-bottom: 8px;
}

.forum-post-card__level-ring {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.level-progress-ring {
  transition: stroke-dasharray 0.5s ease;
}

.forum-post-card__avatar {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.forum-post-card__online-dot {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 14px;
  height: 14px;
  background: var(--forum-success);
  border: 3px solid var(--forum-bg-card);
  border-radius: 50%;
  z-index: 1;
}

.forum-post-card__role {
  display: inline-block;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-radius: 4px;
  margin-bottom: 6px;
}

.forum-post-card__role--admin {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.forum-post-card__role--moderator {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
}

.forum-post-card__role--vip {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.forum-post-card__role--member {
  background: var(--forum-bg-hover);
  color: var(--forum-muted);
}

.forum-post-card__badges {
  margin-bottom: 8px;
}

.forum-post-card__level-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 100%;
  margin-bottom: 8px;
}

.forum-post-card__joined {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--forum-muted);
  margin-top: 6px;
}

.forum-post-card__content {
  flex: 1;
  padding: 14px;
  min-width: 0;
}

.forum-post-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.forum-post-card__time {
  display: flex;
  align-items: center;
  gap: 6px;
}

.forum-post-card__edited {
  color: var(--forum-warning);
  font-style: italic;
}

.forum-post-card__body {
  margin-bottom: 12px;
}

.forum-post-card__attachments {
  margin-bottom: 12px;
  padding: 10px;
  background: var(--forum-bg-hover);
  border-radius: var(--forum-radius-sm);
}

.forum-post-card__attachments h5 {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
}

.forum-post-card__attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.forum-post-card__attachment {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--forum-bg-card);
  border-radius: var(--forum-radius-sm);
  color: var(--forum-link);
  text-decoration: none;
  transition: background 0.2s ease;
}

.forum-post-card__attachment:hover {
  background: var(--forum-bg-panel);
}

.forum-post-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--forum-border);
}

.forum-post-card__reactions {
  display: flex;
  gap: 8px;
}

.forum-post-card__like-btn,
.forum-post-card__reply-btn,
.forum-post-card__quote-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--forum-bg-hover);
  border: none;
  border-radius: var(--forum-radius-sm);
  color: var(--forum-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.forum-post-card__like-btn:hover,
.forum-post-card__reply-btn:hover,
.forum-post-card__quote-btn:hover {
  background: rgba(79, 140, 255, 0.15);
  color: var(--forum-link);
}

.forum-post-card__like-btn.liked {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.forum-post-card__like-btn.liked svg {
  fill: currentColor;
}

.forum-post-card__secondary-actions {
  display: flex;
  gap: 4px;
}

.forum-post-card__share-btn,
.forum-post-card__report-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  border-radius: var(--forum-radius-sm);
  color: var(--forum-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.forum-post-card__share-btn:hover {
  background: var(--forum-bg-hover);
  color: var(--forum-link);
}

.forum-post-card__report-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Like Animation */
@keyframes like-pulse {
  0% { transform: scale(1); }
  25% { transform: scale(1.3); }
  50% { transform: scale(0.9); }
  75% { transform: scale(1.15); }
  100% { transform: scale(1); }
}

.like-pulse {
  animation: like-pulse 0.4s ease-out;
}

.like-animating {
  background: rgba(239, 68, 68, 0.2) !important;
}
</style>
