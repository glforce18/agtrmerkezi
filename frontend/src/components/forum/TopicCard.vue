<template>
  <router-link
    :to="`/forum/topic/${topic.id}`"
    class="block card p-4 hover:border-primary/50 transition-all"
  >
    <div class="flex gap-4">
      <!-- Avatar -->
      <div class="flex-shrink-0">
        <div class="avatar avatar-md">
          <span>{{ getInitials(topic.author?.username) }}</span>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <!-- Title & Badges -->
        <div class="flex items-start gap-2 mb-2">
          <h3 class="text-lg font-semibold text-text-primary hover:text-primary transition-colors flex-1">
            {{ topic.title }}
          </h3>
          <span v-if="topic.is_pinned" class="badge badge-warning flex-shrink-0">
            📌
          </span>
          <span v-if="topic.is_locked" class="badge badge-neutral flex-shrink-0">
            🔒
          </span>
        </div>

        <!-- Meta Info -->
        <div class="flex items-center gap-3 text-sm text-text-secondary mb-2">
          <span class="font-medium">{{ topic.author?.username || 'Anonim' }}</span>
          <span>•</span>
          <span>{{ formatDate(topic.created_at) }}</span>
          <span v-if="topic.category" class="hidden sm:inline">•</span>
          <span v-if="topic.category" class="text-primary hidden sm:inline">
            {{ topic.category.name }}
          </span>
        </div>

        <!-- Preview (if has content) -->
        <p v-if="topic.content" class="text-text-secondary text-sm line-clamp-2 mb-3">
          {{ stripHtml(topic.content) }}
        </p>

        <!-- Stats -->
        <div class="flex items-center gap-4 text-sm">
          <div class="flex items-center gap-1.5 text-text-muted">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
            <span>{{ topic.view_count || 0 }}</span>
          </div>

          <div class="flex items-center gap-1.5" :class="topic.post_count > 0 ? 'text-primary' : 'text-text-muted'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <span class="font-medium">{{ topic.post_count || 0 }}</span>
          </div>

          <div v-if="topic.likes > 0" class="flex items-center gap-1.5 text-status-success">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z"/>
            </svg>
            <span>{{ topic.likes }}</span>
          </div>
        </div>
      </div>

      <!-- Last Activity (Desktop) -->
      <div v-if="topic.last_reply_at" class="hidden lg:flex flex-col items-end text-right flex-shrink-0">
        <div class="text-xs text-text-muted mb-1">Son yanıt</div>
        <div class="text-sm text-text-secondary">{{ formatDate(topic.last_reply_at) }}</div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
const props = defineProps({
  topic: {
    type: Object,
    required: true
  }
})

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const stripHtml = (html) => {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '').substring(0, 150)
}

const formatDate = (dateString) => {
  if (!dateString) return ''

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Az önce'
  if (diffMins < 60) return `${diffMins}dk önce`
  if (diffHours < 24) return `${diffHours}sa önce`
  if (diffDays < 7) return `${diffDays}g önce`

  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short'
  })
}
</script>
