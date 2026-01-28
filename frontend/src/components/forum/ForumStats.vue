<template>
  <aside class="space-y-6 sticky top-20">
    <!-- Forum Stats -->
    <div class="card p-4">
      <h3 class="text-sm font-semibold text-text-primary uppercase tracking-wide mb-4">Forum İstatistikleri</h3>
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-text-secondary text-sm">Toplam Konu</span>
          <span class="text-text-primary font-semibold">{{ stats.total_topics || 0 }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-text-secondary text-sm">Toplam Mesaj</span>
          <span class="text-text-primary font-semibold">{{ stats.total_replies || 0 }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-text-secondary text-sm">Üyeler</span>
          <span class="text-text-primary font-semibold">{{ stats.total_users || 0 }}</span>
        </div>
        <div class="divider"></div>
        <div class="flex items-center justify-between">
          <span class="text-text-secondary text-sm">Çevrimiçi</span>
          <span class="text-primary font-semibold flex items-center gap-2">
            <span class="status-dot online pulse"></span>
            {{ stats.online_users || 0 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Trending Topics -->
    <div v-if="trendingTopics && trendingTopics.length" class="card p-4">
      <h3 class="text-sm font-semibold text-text-primary uppercase tracking-wide mb-4">
        🔥 Trend Konular
      </h3>
      <div class="space-y-3">
        <router-link
          v-for="topic in trendingTopics"
          :key="topic.id"
          :to="`/forum/topic/${topic.id}`"
          class="block group"
        >
          <div class="text-sm text-text-primary group-hover:text-primary transition-colors line-clamp-2 mb-1">
            {{ topic.title }}
          </div>
          <div class="text-xs text-text-muted">
            {{ topic.reply_count || 0 }} yanıt
          </div>
        </router-link>
      </div>
    </div>

    <!-- Online Users -->
    <div v-if="onlineUsers && onlineUsers.length" class="card p-4">
      <h3 class="text-sm font-semibold text-text-primary uppercase tracking-wide mb-4">
        Çevrimiçi Kullanıcılar
      </h3>
      <div class="space-y-2">
        <div
          v-for="user in onlineUsers.slice(0, 8)"
          :key="user.id"
          class="flex items-center gap-2"
        >
          <div class="avatar avatar-sm">
            <span>{{ getInitials(user.username) }}</span>
          </div>
          <span class="text-sm text-text-secondary truncate">{{ user.username }}</span>
        </div>
        <div v-if="onlineUsers.length > 8" class="text-xs text-text-muted pt-2">
          +{{ onlineUsers.length - 8 }} diğer...
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
</script>
