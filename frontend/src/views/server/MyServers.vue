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
              {{ getGameTypeName(server.game) }}
            </div>
          </div>

          <!-- Info Grid -->
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="bg-dark-elevated rounded-lg p-3">
              <div class="text-text-muted text-xs mb-1">IP Address</div>
              <div class="text-text-primary font-mono text-sm">{{ server.ip }}:{{ server.port }}</div>
            </div>
            <div class="bg-dark-elevated rounded-lg p-3">
              <div class="text-text-muted text-xs mb-1">Players</div>
              <div class="text-status-success font-semibold">{{ server.current_players }}/{{ server.max_players }}</div>
            </div>
            <div class="bg-dark-elevated rounded-lg p-3 col-span-2">
              <div class="text-text-muted text-xs mb-1">Current Map</div>
              <div class="text-text-primary font-medium">{{ server.map || 'de_dust2' }}</div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-2">
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
          <router-link :to="`/servers/${server.id}`" class="flex-1">
            <button class="btn btn-primary w-full">
              🎮 Manage
            </button>
          </router-link>
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
  return serversStore.servers.reduce((sum, s) => sum + (s.max_players || 0), 0)
})

// Status helpers
const statusBadgeClass = (status) => {
  const classes = {
    running: 'badge-success',
    stopped: 'badge-neutral',
    starting: 'badge-warning',
    error: 'badge-error'
  }
  return classes[status] || classes.stopped
}

const statusDotClass = (status) => {
  const classes = {
    running: 'online',
    stopped: 'offline',
    starting: 'online',
    error: 'offline'
  }
  return classes[status] || classes.stopped
}

const statusText = (status) => {
  const texts = {
    running: 'Online',
    stopped: 'Offline',
    starting: 'Starting',
    error: 'Error'
  }
  return texts[status] || 'Offline'
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
