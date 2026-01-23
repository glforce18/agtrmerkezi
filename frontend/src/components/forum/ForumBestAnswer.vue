<template>
  <div
    :class="[
      'forum-best-answer-wrapper',
      { 'forum-best-answer-wrapper--animated': animated }
    ]"
    role="region"
    :aria-label="`En iyi cevap - ${post.author} tarafindan`"
  >
    <!-- Best Answer Header -->
    <div class="forum-best-answer-header">
      <div class="forum-best-answer-header__badge">
        <CheckCircleIcon class="w-5 h-5" />
        <span>En Iyi Cevap</span>
      </div>
      <div class="forum-best-answer-header__info">
        <span class="forum-meta">{{ markedByLabel }}</span>
      </div>
    </div>

    <!-- Answer Content -->
    <div class="forum-best-answer-content">
      <div class="forum-best-answer-content__author">
        <n-avatar
          round
          :size="48"
          :src="post.authorAvatar"
          :fallback-src="defaultAvatar"
        />
        <div class="forum-best-answer-content__author-info">
          <span class="forum-best-answer-content__author-name">{{ post.author }}</span>
          <span v-if="post.authorRole" class="forum-best-answer-content__author-role">
            {{ post.authorRole }}
          </span>
        </div>
      </div>

      <div class="forum-best-answer-content__body forum-body">
        <div v-if="post.htmlContent" v-html="sanitizedTruncatedContent" />
        <p v-else>{{ truncatedText }}</p>

        <button
          v-if="isLongContent"
          class="forum-best-answer-content__expand"
          @click="$emit('expand', post)"
        >
          Devamini oku...
        </button>
      </div>

      <div class="forum-best-answer-content__footer">
        <div class="forum-best-answer-content__stats">
          <span class="forum-stat-pill">
            <HeartIcon class="w-4 h-4" />
            {{ post.likes || 0 }} Begeni
          </span>
          <span class="forum-meta">
            <ClockIcon class="w-3.5 h-3.5" />
            {{ post.created }}
          </span>
        </div>

        <button
          class="forum-best-answer-content__goto"
          @click="$emit('goto', post)"
        >
          <span>Cevaba git</span>
          <ArrowRightIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import {
  CheckCircleIcon,
  HeartIcon,
  ClockIcon,
  ArrowRightIcon
} from 'lucide-vue-next'

const props = defineProps({
  post: {
    type: Object,
    required: true,
    validator: (post) => {
      if (!post || typeof post.id === 'undefined') {
        console.warn('[ForumBestAnswer] post.id is required')
        return false
      }
      if (typeof post.author !== 'string') {
        console.warn('[ForumBestAnswer] post.author must be a string')
        return false
      }
      return true
    }
  },
  markedBy: {
    type: String,
    default: ''
  },
  animated: {
    type: Boolean,
    default: true
  },
  maxLength: {
    type: Number,
    default: 300,
    validator: (val) => val > 0
  }
})

const emit = defineEmits(['expand', 'goto'])

// Safe data access computed properties
const authorName = computed(() => props.post.author || 'Anonim')
const authorAvatar = computed(() => props.post.authorAvatar || null)
const authorRole = computed(() => props.post.authorRole || '')
const postLikes = computed(() => props.post.likes || 0)
const postCreated = computed(() => props.post.created || '')

const defaultAvatar = '/images/default-avatar.png'

const markedByLabel = computed(() => {
  if (props.markedBy) {
    return `${props.markedBy} tarafindan en iyi cevap secildi`
  }
  return 'Konu sahibi tarafindan en iyi cevap secildi'
})

const contentText = computed(() => {
  if (props.post.htmlContent) {
    // Strip HTML tags for length check - sanitize first to prevent XSS
    const tmp = document.createElement('div')
    tmp.innerHTML = DOMPurify.sanitize(props.post.htmlContent)
    return tmp.textContent || tmp.innerText || ''
  }
  return props.post.content || ''
})

const isLongContent = computed(() => {
  return contentText.value.length > props.maxLength
})

const truncatedText = computed(() => {
  if (!isLongContent.value) return contentText.value
  return contentText.value.slice(0, props.maxLength) + '...'
})

const truncatedContent = computed(() => {
  if (!isLongContent.value) return props.post.htmlContent
  // For HTML content, we just return the full content and use CSS to truncate
  // A proper implementation would need a more sophisticated HTML truncation
  return props.post.htmlContent
})

// Sanitized version of truncatedContent for safe rendering
const sanitizedTruncatedContent = computed(() => {
  return DOMPurify.sanitize(truncatedContent.value || '')
})
</script>

<style scoped>
.forum-best-answer-wrapper {
  border: 2px solid var(--forum-success);
  border-radius: var(--forum-radius-lg);
  overflow: hidden;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), transparent);
}

.forum-best-answer-wrapper--animated {
  animation: forum-solved-glow 3s ease-in-out infinite;
}

@keyframes forum-solved-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(34, 197, 94, 0.2);
  }
  50% {
    box-shadow: 0 0 25px rgba(34, 197, 94, 0.4);
  }
}

.forum-best-answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(34, 197, 94, 0.1);
  border-bottom: 1px solid rgba(34, 197, 94, 0.2);
}

.forum-best-answer-header__badge {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--forum-success);
  font-weight: 600;
  font-size: 14px;
}

.forum-best-answer-content {
  padding: 20px;
}

.forum-best-answer-content__author {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.forum-best-answer-content__author-info {
  display: flex;
  flex-direction: column;
}

.forum-best-answer-content__author-name {
  font-weight: 600;
  color: var(--text-primary);
}

.forum-best-answer-content__author-role {
  font-size: 12px;
  color: var(--forum-accent);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.forum-best-answer-content__body {
  margin-bottom: 16px;
  max-height: 200px;
  overflow: hidden;
  position: relative;
}

.forum-best-answer-content__expand {
  display: inline-block;
  margin-top: 8px;
  padding: 0;
  background: none;
  border: none;
  color: var(--forum-link);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.forum-best-answer-content__expand:hover {
  color: var(--forum-link-hover);
  text-decoration: underline;
}

.forum-best-answer-content__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--forum-border);
}

.forum-best-answer-content__stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.forum-best-answer-content__goto {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--forum-success);
  border: none;
  border-radius: var(--forum-radius-sm);
  color: white;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.forum-best-answer-content__goto:hover {
  background: #16a34a;
  transform: translateX(2px);
}
</style>
