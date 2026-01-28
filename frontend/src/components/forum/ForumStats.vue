<template>
  <aside class="space-y-6 sticky top-20">
    <!-- Forum Stats -->
    <div class="glass-card p-5 scale-in">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 bg-gradient-to-br from-primary to-orange-600 rounded-lg flex items-center justify-center">
          <span class="text-lg">📊</span>
        </div>
        <h3 class="text-sm font-bold text-gradient uppercase tracking-wide">Forum İstatistikleri</h3>
      </div>
      <div class="space-y-3">
        <div class="flex items-center justify-between p-2 bg-dark-elevated rounded-lg hover:bg-dark-hover transition-colors">
          <span class="text-text-secondary text-sm flex items-center gap-2">
            <span>📝</span>
            <span>Toplam Konu</span>
          </span>
          <span class="text-text-primary font-bold text-lg">{{ formatNumber(stats.total_topics || 0) }}</span>
        </div>
        <div class="flex items-center justify-between p-2 bg-dark-elevated rounded-lg hover:bg-dark-hover transition-colors">
          <span class="text-text-secondary text-sm flex items-center gap-2">
            <span>💬</span>
            <span>Toplam Mesaj</span>
          </span>
          <span class="text-text-primary font-bold text-lg">{{ formatNumber(stats.total_replies || 0) }}</span>
        </div>
        <div class="flex items-center justify-between p-2 bg-dark-elevated rounded-lg hover:bg-dark-hover transition-colors">
          <span class="text-text-secondary text-sm flex items-center gap-2">
            <span>👥</span>
            <span>Üyeler</span>
          </span>
          <span class="text-text-primary font-bold text-lg">{{ formatNumber(stats.total_users || 0) }}</span>
        </div>
        <div class="h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent my-2"></div>
        <div class="flex items-center justify-between p-2 bg-green-500/10 rounded-lg border border-green-500/30">
          <span class="text-green-500 text-sm font-medium flex items-center gap-2">
            <span class="relative flex h-3 w-3">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span>Çevrimiçi</span>
          </span>
          <span class="text-green-500 font-bold text-lg">{{ stats.online_users || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- Trending Topics -->
    <div v-if="trendingTopics && trendingTopics.length" class="glass-card p-5 scale-in delay-100">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
          <span class="text-lg">🔥</span>
        </div>
        <h3 class="text-sm font-bold text-gradient uppercase tracking-wide">Trend Konular</h3>
      </div>
      <div class="space-y-3">
        <router-link
          v-for="topic in trendingTopics"
          :key="topic.id"
          :to="`/forum/topic/${topic.id}`"
          class="block p-3 bg-dark-elevated hover:bg-dark-hover rounded-lg transition-all group border border-dark-border hover:border-primary/30"
        >
          <div class="text-sm text-text-primary group-hover:text-primary transition-colors line-clamp-2 mb-2 font-medium">
            {{ topic.title }}
          </div>
          <div class="flex items-center gap-3 text-xs text-text-muted">
            <span class="flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
              <span>{{ topic.reply_count || 0 }}</span>
            </span>
            <span class="flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <span>{{ topic.view_count || 0 }}</span>
            </span>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Online Users with Steam Avatars -->
    <div v-if="onlineUsers && onlineUsers.length" class="glass-card p-5 scale-in delay-200">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
          <span class="text-lg">👥</span>
        </div>
        <h3 class="text-sm font-bold text-gradient uppercase tracking-wide">Çevrimiçi</h3>
      </div>
      <div class="space-y-2">
        <div
          v-for="user in onlineUsers.slice(0, 8)"
          :key="user.id"
          class="flex items-center gap-3 p-2 bg-dark-elevated hover:bg-dark-hover rounded-lg transition-colors group"
        >
          <div class="relative">
            <img
              v-if="user.avatar"
              :src="user.avatar"
              :alt="user.username"
              class="w-8 h-8 rounded-full ring-2 ring-green-500/30"
            />
            <div v-else class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white text-xs font-bold ring-2 ring-green-500/30">
              {{ getInitials(user.username) }}
            </div>
            <div class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-dark-card"></div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-text-primary group-hover:text-primary transition-colors truncate font-medium">{{ user.username }}</div>
            <div v-if="user.steam_id" class="text-xs text-text-muted">🎮 Steam</div>
          </div>
        </div>
        <div v-if="onlineUsers.length > 8" class="text-xs text-text-muted pt-2 text-center px-2 py-1 bg-dark-elevated rounded">
          +{{ onlineUsers.length - 8 }} diğer kullanıcı çevrimiçi
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      total_topics: 0,
      total_replies: 0,
      total_users: 0,
      online_users: 0
    })
  },
  trendingTopics: {
    type: Array,
    default: () => []
  },
  onlineUsers: {
    type: Array,
    default: () => []
  }
})

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num
}
</script>
