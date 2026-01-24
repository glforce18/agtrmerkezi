<template>
  <div class="quote-thread">
    <!-- Parent Quote (collapsed by default) -->
    <div v-if="parentReply" class="parent-quote" @click="showParentDetails = !showParentDetails">
      <div class="quote-header">
        <n-icon><FormatQuote /></n-icon>
        <span class="quote-author">{{ parentReply.author?.username }} yazmis:</span>
        <n-icon class="expand-icon" :class="{ expanded: showParentDetails }">
          <ExpandMore />
        </n-icon>
      </div>

      <n-collapse-transition :show="showParentDetails">
        <div class="quote-content" v-html="formatContent(parentReply.content)"></div>
        <div class="quote-actions">
          <n-button text size="small" @click.stop="goToReply(parentReply.id)">
            Yanita Git
          </n-button>
        </div>
      </n-collapse-transition>

      <div v-if="!showParentDetails" class="quote-preview">
        {{ truncate(stripHtml(parentReply.content), 100) }}
      </div>
    </div>

    <!-- Current Reply Content -->
    <slot></slot>

    <!-- Child Replies Preview -->
    <div v-if="childReplies.length > 0" class="child-replies">
      <div class="children-header" @click="showChildren = !showChildren">
        <n-icon><Reply /></n-icon>
        <span>{{ childReplies.length }} yanit</span>
        <n-icon class="expand-icon" :class="{ expanded: showChildren }">
          <ExpandMore />
        </n-icon>
      </div>

      <n-collapse-transition :show="showChildren">
        <div class="children-list">
          <div
            v-for="child in childReplies"
            :key="child.id"
            class="child-item"
            @click="goToReply(child.id)"
          >
            <n-avatar :src="child.author?.avatar" size="small" round />
            <div class="child-content">
              <span class="child-author">{{ child.author?.username }}</span>
              <span class="child-preview">{{ truncate(stripHtml(child.content), 80) }}</span>
            </div>
          </div>
        </div>
      </n-collapse-transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon, NCollapseTransition, NButton, NAvatar } from 'naive-ui'
import { QuoteIcon, ChevronDownIcon, ReplyIcon } from 'lucide-vue-next'

const Reply = ReplyIcon
import { threadingApi } from '@/services/forumAdvanced.js'

const FormatQuote = QuoteIcon
const ExpandMore = ChevronDownIcon

const router = useRouter()

const props = defineProps({
  replyId: {
    type: Number,
    required: true
  },
  parentReplyId: {
    type: Number,
    default: null
  },
  topicId: {
    type: Number,
    required: true
  },
  lazyLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['reply-click'])

// State
const parentReply = ref(null)
const childReplies = ref([])
const showParentDetails = ref(false)
const showChildren = ref(false)
const loading = ref(false)

// Methods
const fetchThread = async () => {
  if (loading.value) return

  loading.value = true
  try {
    const { data } = await threadingApi.getReplyThread(props.replyId)
    if (data.success && data.thread) {
      // Set parent from thread
      if (data.thread.parents?.length > 0) {
        parentReply.value = data.thread.parents[data.thread.parents.length - 1]
      }
      // Set children
      childReplies.value = data.thread.children || []
    }
  } catch (err) {
    // Silent fail
  } finally {
    loading.value = false
  }
}

const goToReply = (replyId) => {
  emit('reply-click', replyId)

  // Scroll to reply or navigate
  const element = document.getElementById(`reply-${replyId}`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    element.classList.add('highlight')
    setTimeout(() => element.classList.remove('highlight'), 2000)
  } else {
    // Navigate to topic with reply anchor
    router.push(`/forum/topic/${props.topicId}#reply-${replyId}`)
  }
}

const formatContent = (content) => {
  if (!content) return ''
  // Basic formatting
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

const stripHtml = (html) => {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '').replace(/\n/g, ' ')
}

const truncate = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Watch for parent reply ID changes
watch(() => props.parentReplyId, (newVal) => {
  if (newVal && props.lazyLoad) {
    fetchThread()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  if (!props.lazyLoad || props.parentReplyId) {
    fetchThread()
  }
})
</script>

<style scoped>
.quote-thread {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.parent-quote {
  padding: 12px;
  background: var(--n-color);
  border-left: 3px solid var(--n-primary-color);
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  transition: background 0.2s;
}

.parent-quote:hover {
  background: var(--n-color-hover);
}

.quote-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--n-text-color-3);
}

.quote-author {
  font-weight: 500;
  color: var(--n-primary-color);
}

.expand-icon {
  margin-left: auto;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.quote-content {
  margin-top: 8px;
  padding: 8px;
  background: var(--n-color-modal);
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
}

.quote-preview {
  margin-top: 4px;
  font-size: 13px;
  color: var(--n-text-color-2);
  font-style: italic;
}

.quote-actions {
  margin-top: 8px;
}

.child-replies {
  padding: 12px;
  background: var(--n-color);
  border-radius: 8px;
}

.children-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--n-text-color-3);
  cursor: pointer;
}

.children-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.child-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.child-item:hover {
  background: var(--n-color-hover);
}

.child-content {
  flex: 1;
  min-width: 0;
}

.child-author {
  font-weight: 500;
  font-size: 13px;
  display: block;
  margin-bottom: 2px;
}

.child-preview {
  font-size: 12px;
  color: var(--n-text-color-2);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Highlight animation for scrolled-to replies */
:global(.highlight) {
  animation: highlight-pulse 2s ease-out;
}

@keyframes highlight-pulse {
  0%, 100% {
    box-shadow: none;
  }
  50% {
    box-shadow: 0 0 0 4px var(--n-primary-color-suppl);
  }
}
</style>
