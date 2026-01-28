<template>
  <router-link
    :to="`/forum/topic/${topic.id}`"
    class="block relative overflow-hidden rounded-xl border border-dark-border/50 bg-gradient-to-br from-dark-card/80 to-dark-elevated/80 backdrop-blur-sm hover:border-primary/50 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 group fade-in-up"
  >
    <!-- Animated gradient overlay on hover -->
    <div class="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/5 to-primary/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

    <!-- Status badges ribbon -->
    <div v-if="topic.is_pinned || topic.is_locked || topic.is_solved" class="absolute top-0 right-0 flex gap-2 p-3 z-10">
      <span v-if="topic.is_pinned" class="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-yellow-500/20 text-yellow-400 border border-yellow-500/40 rounded-full font-semibold backdrop-blur-sm shadow-lg">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L11 4.323V3a1 1 0 011-1h-2zM9 5.323V3a1 1 0 00-1-1H6a1 1 0 00-1 1v2.323l-3.954 1.582-1.599-.8a1 1 0 10-.894 1.79l1.233.616-1.738 5.42a1 1 0 00.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 012.667-1.019 1 1 0 00.285-1.05l-1.738-5.42 1.233-.617a1 1 0 10-.894-1.788l-1.599.799L9 5.323z"/></svg>
        Sabit
      </span>
      <span v-if="topic.is_solved" class="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-green-500/20 text-green-400 border border-green-500/40 rounded-full font-semibold backdrop-blur-sm shadow-lg">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
        Çözüldü
      </span>
      <span v-if="topic.is_locked" class="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-gray-500/20 text-gray-400 border border-gray-500/40 rounded-full font-semibold backdrop-blur-sm shadow-lg">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/></svg>
        Kilitli
      </span>
    </div>

    <!-- Main content -->
    <div class="relative p-6">
      <div class="flex gap-4">
        <!-- Enhanced Avatar -->
        <div class="flex-shrink-0">
          <div class="relative">
            <div class="absolute -inset-1 bg-gradient-to-r from-primary to-orange-500 rounded-full opacity-0 group-hover:opacity-20 blur transition-opacity duration-300"></div>
            <img
              v-if="topic.author?.avatar"
              :src="topic.author.avatar"
              :alt="topic.author?.username"
              class="relative w-16 h-16 rounded-full ring-2 ring-primary/30 group-hover:ring-primary/60 transition-all duration-300 object-cover"
            />
            <div v-else class="relative w-16 h-16 rounded-full bg-gradient-to-br from-primary via-primary/80 to-orange-600 flex items-center justify-center ring-2 ring-primary/30 group-hover:ring-primary/60 transition-all duration-300 shadow-lg">
              <span class="text-white font-bold text-xl">{{ getInitials(topic.author?.username) }}</span>
            </div>
            <!-- Online indicator with pulse -->
            <div v-if="isUserOnline(topic.author?.id)" class="absolute -bottom-1 -right-1">
              <span class="flex h-4 w-4">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-4 w-4 bg-green-500 border-2 border-dark-card"></span>
              </span>
            </div>
          </div>
        </div>

        <!-- Content area -->
        <div class="flex-1 min-w-0">
          <!-- Category badge -->
          <div v-if="topic.category" class="mb-2">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-primary/10 text-primary text-xs font-semibold rounded-md border border-primary/20">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/></svg>
              {{ topic.category.name }}
            </span>
          </div>

          <!-- Title with hover effect -->
          <h3 class="text-xl font-bold text-text-primary mb-3 line-clamp-2 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-primary group-hover:to-orange-500 transition-all duration-300">
            {{ topic.title }}
          </h3>

          <!-- Author info with enhanced Steam badge -->
          <div class="flex items-center gap-3 mb-3 flex-wrap">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-text-primary text-sm">{{ topic.author?.username || 'Anonim' }}</span>
              <a
                v-if="topic.author?.steam_id"
                :href="`https://steamcommunity.com/profiles/${topic.author.steam_id}`"
                target="_blank"
                @click.stop
                class="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-blue-600/30 to-blue-500/30 hover:from-blue-600/50 hover:to-blue-500/50 text-blue-400 text-xs font-medium rounded border border-blue-500/40 hover:border-blue-500/60 transition-all hover:scale-105"
                title="Steam Profiline Git">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
                </svg>
              </a>
            </div>
            <span class="text-text-muted text-xs">•</span>
            <div class="flex items-center gap-1.5 text-text-muted text-xs">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>{{ formatDate(topic.created_at) }}</span>
            </div>
          </div>

          <!-- Preview text -->
          <p v-if="topic.content" class="text-text-secondary text-sm line-clamp-2 mb-4 leading-relaxed">
            {{ stripHtml(topic.content) }}
          </p>

          <!-- Stats bar with modern design -->
          <div class="flex items-center gap-2 flex-wrap">
            <!-- Views -->
            <div class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-dark-elevated/80 rounded-lg text-xs font-medium text-text-muted hover:bg-dark-hover transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <span>{{ formatNumber(topic.view_count || 0) }}</span>
            </div>

            <!-- Replies -->
            <div
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
              :class="(topic.reply_count || 0) > 0 ? 'bg-primary/15 text-primary border border-primary/30 hover:bg-primary/25' : 'bg-dark-elevated/80 text-text-muted hover:bg-dark-hover'">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
              <span>{{ topic.reply_count || 0 }}</span>
            </div>

            <!-- Likes -->
            <div
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
              :class="(topic.likes || 0) > 0 ? 'bg-green-500/15 text-green-400 border border-green-500/30 hover:bg-green-500/25' : 'bg-dark-elevated/80 text-text-muted hover:bg-dark-hover'">
              <svg class="w-4 h-4" :fill="(topic.likes || 0) > 0 ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 20 20">
                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z"/>
              </svg>
              <span>{{ formatNumber(topic.likes || 0) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Hover arrow indicator -->
      <div class="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-300 transform group-hover:translate-x-1">
        <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
        </svg>
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
  return html.replace(/<[^>]*>/g, '').substring(0, 200)
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
    month: 'short',
    year: 'numeric'
  })
}

const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num
}

const isUserOnline = (userId) => {
  return false // Will be implemented with real-time presence
}
</script>
