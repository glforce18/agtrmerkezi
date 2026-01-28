<template>
  <div class="container mx-auto px-4 py-8 max-w-[1400px]">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text-primary mb-2">
        Hoş Geldin, {{ authStore.user?.username || 'Kullanıcı' }}! 👋
      </h1>
      <p class="text-text-secondary">İşte hesap özetiniz</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Balance -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-3">
          <span class="text-text-muted text-sm">Bakiye</span>
          <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-text-primary">₺{{ stats.balance || '0.00' }}</div>
        <router-link to="/wallet" class="text-sm text-primary hover:text-primary-light mt-2 inline-block">
          Bakiye Yükle →
        </router-link>
      </div>

      <!-- Servers -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-3">
          <span class="text-text-muted text-sm">Sunucularım</span>
          <div class="w-10 h-10 rounded-lg bg-status-info/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-status-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
            </svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.servers || 0 }}</div>
        <router-link to="/servers/my" class="text-sm text-status-info hover:opacity-80 mt-2 inline-block">
          Sunucuları Yönet →
        </router-link>
      </div>

      <!-- Forum Activity -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-3">
          <span class="text-text-muted text-sm">Forum Mesajları</span>
          <div class="w-10 h-10 rounded-lg bg-status-success/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-status-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.forum_posts || 0 }}</div>
        <router-link to="/forum" class="text-sm text-status-success hover:opacity-80 mt-2 inline-block">
          Foruma Git →
        </router-link>
      </div>

      <!-- Rank -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-3">
          <span class="text-text-muted text-sm">Seviye</span>
          <div class="w-10 h-10 rounded-lg bg-status-warning/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-status-warning" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.level || 1 }}</div>
        <div class="text-sm text-text-muted mt-2">{{ stats.rank || 'Yeni Üye' }}</div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Quick Actions Card -->
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-text-primary mb-4">Hızlı İşlemler</h2>
        <div class="space-y-3">
          <router-link to="/servers/rent" class="btn btn-primary w-full">
            🎮 Yeni Sunucu Kirala
          </router-link>
          <router-link to="/forum/topic/new" class="btn btn-secondary w-full">
            ✍️ Yeni Konu Aç
          </router-link>
          <router-link to="/wallet" class="btn btn-secondary w-full">
            💰 Bakiye Yükle
          </router-link>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="card p-6 lg:col-span-2">
        <h2 class="text-lg font-semibold text-text-primary mb-4">Son Aktiviteler</h2>
        <div v-if="activities.length === 0" class="text-center py-8 text-text-muted">
          <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          <p>Henüz aktivite yok</p>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="activity in activities.slice(0, 5)"
            :key="activity.id"
            class="flex items-start gap-3 p-3 rounded-lg bg-dark-elevated hover:bg-dark-hover transition-colors"
          >
            <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
              <span class="text-sm">{{ activity.icon }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-text-primary">{{ activity.text }}</p>
              <p class="text-xs text-text-muted mt-1">{{ formatDate(activity.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-text-primary">Bildirimler</h2>
        <button class="text-sm text-primary hover:text-primary-light">
          Tümünü Gör
        </button>
      </div>
      <div v-if="notifications.length === 0" class="text-center py-8 text-text-muted">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
        <p>Bildirim yok</p>
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="notif in notifications.slice(0, 3)"
          :key="notif.id"
          class="p-3 rounded-lg border border-dark-border hover:border-primary/50 transition-colors cursor-pointer"
        >
          <div class="flex items-start gap-3">
            <div class="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-text-primary">{{ notif.message }}</p>
              <p class="text-xs text-text-muted mt-1">{{ formatDate(notif.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const stats = ref({
  balance: 0,
  servers: 0,
  forum_posts: 0,
  level: 1,
  rank: 'Yeni Üye'
})

const activities = ref([])
const notifications = ref([])

onMounted(async () => {
  // Fetch user stats
  // TODO: Add API call
  stats.value = {
    balance: authStore.user?.balance || 0,
    servers: 0,
    forum_posts: 0,
    level: 1,
    rank: 'Yeni Üye'
  }
})

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
</script>
