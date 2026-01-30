<template>
  <div class="relative min-h-screen">
    <!-- Background -->
    <div class="fixed inset-0 z-0">
      <img :src="getBackgroundImage('tunnel')" alt="" class="absolute inset-0 w-full h-full object-cover opacity-60" />
      <div class="absolute inset-0 bg-gradient-to-b from-dark-bg/40 via-dark-bg/55 to-dark-bg/70"></div>
    </div>

    <div class="container mx-auto px-4 py-8 max-w-7xl relative z-10">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-text-primary mb-2">Sunucularım</h1>
        <p class="text-text-secondary">Tüm sunucularınızı buradan yönetin</p>
      </div>
      <router-link to="/servers/rent" class="btn btn-primary">
        + Yeni Sunucu Kirala
      </router-link>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="glass-card p-4 fade-in-up delay-100">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-3xl font-bold text-primary">{{ serversStore.servers.length }}</div>
            <div class="text-sm text-text-muted">Toplam Sunucu</div>
          </div>
          <div class="text-4xl opacity-20">🖥️</div>
        </div>
      </div>

      <div class="glass-card p-4 fade-in-up delay-200">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-3xl font-bold text-status-success">{{ runningCount }}</div>
            <div class="text-sm text-text-muted">Çalışan</div>
          </div>
          <div class="text-4xl opacity-20">✅</div>
        </div>
      </div>

      <div class="glass-card p-4 fade-in-up delay-300">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-3xl font-bold text-status-info">{{ totalPlayers }}</div>
            <div class="text-sm text-text-muted">Toplam Oyuncu</div>
          </div>
          <div class="text-4xl opacity-20">👥</div>
        </div>
      </div>

      <div class="glass-card p-4 fade-in-up delay-400">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-3xl font-bold text-gradient">{{ totalSlots }}</div>
            <div class="text-sm text-text-muted">Toplam Slot</div>
          </div>
          <div class="text-4xl opacity-20">📊</div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="serversStore.loading" class="text-center py-20">
      <div class="spinner mx-auto mb-4"></div>
      <p class="text-text-secondary">Sunucular yükleniyor...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!serversStore.servers.length" class="empty-state glass-card p-12 fade-in-up">
      <div class="empty-state-icon">🚀</div>
      <p class="empty-state-title">Henüz Sunucunuz Yok</p>
      <p class="empty-state-description mb-6">
        Hemen bir sunucu kiralayın ve CS 1.6 veya Half-Life maceralarına başlayın!
      </p>
      <router-link to="/servers/rent" class="btn btn-primary">
        İlk Sunucunuzu Kiralayın
      </router-link>
    </div>

    <!-- Servers Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="(server, index) in serversStore.servers"
        :key="server.id"
        class="glass-card p-6 fade-in-up"
        :class="`delay-${((index % 3) + 1)}00`"
      >
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <span
            class="badge"
            :class="statusBadgeClass(server.status)"
          >
            <span class="status-dot inline-block mr-2" :class="statusDotClass(server.status) + ' pulse'"></span>
            {{ statusText(server.status) }}
          </span>
          <span class="text-text-muted text-sm font-mono">#{server.id}</span>
        </div>

        <!-- Server Info -->
        <div class="space-y-4 mb-6">
          <!-- Name -->
          <div>
            <h3 class="text-xl font-bold text-text-primary mb-1">
              {{ server.name }}
            </h3>
            <div class="text-primary text-sm font-medium">
              {{ getGameTypeName(server.game_type) }}
            </div>
          </div>

          <!-- Info Grid -->
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="bg-dark-elevated rounded-lg p-3 col-span-2">
              <div class="text-text-muted text-xs mb-1">IP Address</div>
              <div class="text-text-primary font-mono text-xs break-all">{{ server.ip_address }}:{{ server.port }}</div>
            </div>
            <div class="bg-dark-elevated rounded-lg p-3">
              <div class="text-text-muted text-xs mb-1">Players</div>
              <div class="text-status-success font-semibold">{{ server.current_players || 0 }}/{{ server.slots }}</div>
            </div>
            <div class="bg-dark-elevated rounded-lg p-3">
              <div class="text-text-muted text-xs mb-1">Current Map</div>
              <div class="text-text-primary font-medium truncate">{{ server.map || 'N/A' }}</div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col gap-2">
          <!-- Status Messages for non-operational servers -->
          <div v-if="server.status === 'pending'" class="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-center">
            <p class="text-yellow-300 text-sm">⏳ Admin onayı bekleniyor</p>
          </div>
          <div v-else-if="server.status === 'installing'" class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 text-center">
            <p class="text-blue-300 text-sm">🔧 Sunucu kuruluyor...</p>
            <p class="text-blue-200 text-xs mt-1">Kurulum tamamlandığında erişebilirsiniz</p>
          </div>
          <div v-else-if="server.status === 'rejected'" class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-center">
            <p class="text-red-300 text-sm">❌ Sunucu reddedildi</p>
            <p class="text-red-200 text-xs mt-1">Destek ile iletişime geçin</p>
          </div>
          <div v-else-if="server.status === 'error'" class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-center">
            <p class="text-red-300 text-sm">⚠️ Kurulum başarısız</p>
            <p class="text-red-200 text-xs mt-1">Destek ekibine bildirildi</p>
          </div>
          <div v-else-if="server.status === 'suspended'" class="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 text-center">
            <p class="text-orange-300 text-sm">⏸ Sunucu askıda</p>
            <p class="text-orange-200 text-xs mt-1">Ödeme gerekli</p>
          </div>

          <!-- Normal controls for running/stopped servers -->
          <div v-else class="flex gap-2">
            <button
              v-if="server.status === 'stopped'"
              @click="handleStart(server.id)"
              class="btn btn-secondary flex-1 text-status-success border-status-success/30 hover:bg-status-success/10"
            >
              ▶ Start
            </button>
            <button
              v-if="server.status === 'running'"
              @click="handleStop(server.id)"
              class="btn btn-secondary flex-1 text-status-error border-status-error/30 hover:bg-status-error/10"
            >
              ⏹ Stop
            </button>
            <button
              v-if="server.status === 'running'"
              @click="handleRestart(server.id)"
              class="btn btn-secondary flex-1 text-status-warning border-status-warning/30 hover:bg-status-warning/10"
            >
              🔄 Restart
            </button>
            <router-link :to="{ name: 'server-webpanel-dashboard', params: { id: server.id } }" class="flex-1">
              <button class="btn btn-primary w-full">
                🎮 Manage
              </button>
            </router-link>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useServersStore } from '@/stores/servers'

const serversStore = useServersStore()

onMounted(() => {
  serversStore.fetchMyServers()
})

// Computed stats
const runningCount = computed(() => {
  return serversStore.servers.filter(s => s.status === 'running').length
})

const totalPlayers = computed(() => {
  return serversStore.servers.reduce((sum, s) => sum + (s.current_players || 0), 0)
})

const totalSlots = computed(() => {
  return serversStore.servers.reduce((sum, s) => sum + (s.slots || 0), 0)
})

// Status helpers
const statusBadgeClass = (status) => {
  const classes = {
    running: 'badge-success',
    stopped: 'badge-neutral',
    starting: 'badge-warning',
    pending: 'badge-warning',
    installing: 'badge-info',
    rejected: 'badge-error',
    error: 'badge-error',
    suspended: 'badge-error',
    expired: 'badge-neutral',
    cancelled: 'badge-neutral'
  }
  return classes[status?.toLowerCase()] || classes.stopped
}

const statusDotClass = (status) => {
  const classes = {
    running: 'online',
    stopped: 'offline',
    starting: 'online',
    pending: 'offline',
    installing: 'online',
    rejected: 'offline',
    error: 'offline',
    suspended: 'offline',
    expired: 'offline',
    cancelled: 'offline'
  }
  return classes[status?.toLowerCase()] || classes.stopped
}

const statusText = (status) => {
  const texts = {
    running: 'Online',
    stopped: 'Offline',
    starting: 'Starting',
    pending: '🕐 Onay Bekleniyor',
    installing: '🔧 Kuruluyor',
    rejected: '❌ Reddedildi',
    error: '⚠️ Hata',
    suspended: '⏸ Askıda',
    expired: '⏰ Süresi Doldu',
    cancelled: 'İptal Edildi'
  }
  return texts[status?.toLowerCase()] || 'Offline'
}

const getGameTypeName = (game) => {
  const names = {
    'cs16': 'Counter-Strike 1.6',
    'ag': 'Adrenaline Gamer',
    'hldm': 'Half-Life Deathmatch'
  }
  return names[game] || game
}

// Server actions
const handleStart = async (id) => {
  const result = await serversStore.startServer(id)
  if (!result.success) {
    alert('Sunucu başlatılamadı: ' + result.error)
  }
}

const handleStop = async (id) => {
  const result = await serversStore.stopServer(id)
  if (!result.success) {
    alert('Sunucu durdurulamadı: ' + result.error)
  }
}

const handleRestart = async (id) => {
  const result = await serversStore.restartServer(id)
  if (!result.success) {
    alert('Sunucu yeniden başlatılamadı: ' + result.error)
  }
}

// Background image helper
const getBackgroundImage = (name) => {
  const baseUrl = window.location.origin
  return `${baseUrl}/static/images/backgrounds/${name}.jpg`
}
</script>
