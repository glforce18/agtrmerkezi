<template>
  <div class="space-y-6">
    <!-- Status Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Server Status Card -->
      <div class="glass-card p-6 fade-in-up">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-text-secondary">Sunucu Durumu</h3>
          <div
            class="w-3 h-3 rounded-full"
            :class="serverStatus?.is_online ? 'bg-status-success pulse' : 'bg-text-muted'"
          ></div>
        </div>
        <div class="space-y-2">
          <div class="text-3xl font-bold" :class="serverStatus?.is_online ? 'text-status-success' : 'text-text-muted'">
            {{ serverStatus?.is_online ? 'Çevrimiçi' : 'Çevrimdışı' }}
          </div>
          <div class="text-sm text-text-muted">
            {{ serverInfo?.game_type?.toUpperCase() || 'N/A' }} • {{ serverInfo?.slots }} Slot
          </div>
        </div>
      </div>

      <!-- Players Card -->
      <div class="glass-card p-6 fade-in-up delay-100">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-text-secondary">Oyuncular</h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-primary opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <div class="space-y-2">
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-bold text-primary">{{ serverStatus?.current_players || 0 }}</span>
            <span class="text-text-muted">/</span>
            <span class="text-xl text-text-secondary">{{ serverInfo?.slots }}</span>
          </div>
          <div class="w-full bg-dark-elevated rounded-full h-2 overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-primary to-primary-light rounded-full transition-all duration-500"
              :style="{ width: playerPercentage + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Map Card -->
      <div class="glass-card p-6 fade-in-up delay-200">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-text-secondary">Aktif Map</h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-primary opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
        <div class="space-y-2">
          <div class="text-2xl font-bold text-text-primary truncate">
            {{ serverStatus?.current_map || 'N/A' }}
          </div>
          <div class="text-sm text-text-muted">
            {{ serverStatus?.is_online ? 'Oynuyor' : 'Bekleniyor' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Server Info Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Connection Info -->
      <div class="glass-card p-6 fade-in-up delay-300">
        <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Bağlantı Bilgileri
        </h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center py-2 border-b border-dark-border">
            <span class="text-text-secondary text-sm">IP Address</span>
            <div class="flex items-center gap-2">
              <span class="font-mono text-text-primary">{{ serverInfo?.ip_address }}:{{ serverInfo?.port }}</span>
              <button
                @click="copyToClipboard(`${serverInfo?.ip_address}:${serverInfo?.port}`)"
                class="btn-ghost px-2 py-1 text-xs"
                title="Kopyala"
              >
                📋
              </button>
            </div>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-dark-border">
            <span class="text-text-secondary text-sm">RCON Password</span>
            <div class="flex items-center gap-2">
              <span class="font-mono text-text-primary" :class="{ 'blur-sm': !showRcon }">
                {{ serverInfo?.rcon_password || 'N/A' }}
              </span>
              <button
                @click="showRcon = !showRcon"
                class="btn-ghost px-2 py-1 text-xs"
              >
                {{ showRcon ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-dark-border">
            <span class="text-text-secondary text-sm">Server Code</span>
            <span class="font-mono text-primary font-semibold">{{ serverInfo?.unique_code }}</span>
          </div>
          <div class="flex justify-between items-center py-2">
            <span class="text-text-secondary text-sm">Game Type</span>
            <span class="font-medium text-text-primary">{{ gameTypeName }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="glass-card p-6 fade-in-up delay-400">
        <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Hızlı İşlemler
        </h3>
        <div class="grid grid-cols-2 gap-3">
          <button
            @click="$router.push({ name: 'server-webpanel-settings' })"
            class="btn btn-secondary justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Ayarlar
          </button>
          <button
            @click="$router.push({ name: 'server-webpanel-files' })"
            class="btn btn-secondary justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            Dosyalar
          </button>
          <button
            @click="restartServer"
            :disabled="!serverStatus?.is_online"
            class="btn btn-secondary justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Restart
          </button>
          <button
            @click="$emit('refresh')"
            class="btn btn-primary justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Yenile
          </button>
        </div>

        <!-- Server Timeline -->
        <div class="mt-6 pt-6 border-t border-dark-border">
          <h4 class="text-sm font-medium text-text-secondary mb-3">Sunucu Zaman Çizelgesi</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-text-muted">Oluşturulma:</span>
              <span class="text-text-primary">{{ formatDate(serverInfo?.created_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-muted">Son Bitiş:</span>
              <span class="text-text-primary">{{ formatDate(serverInfo?.expires_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-muted">Auto-Restart:</span>
              <span :class="serverInfo?.auto_restart ? 'text-status-success' : 'text-text-muted'">
                {{ serverInfo?.auto_restart ? 'Aktif' : 'Pasif' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

const props = defineProps({
  serverId: Number,
  serverInfo: Object,
  serverStatus: Object
})

const emit = defineEmits(['refresh'])

const showRcon = ref(false)

const playerPercentage = computed(() => {
  if (!props.serverStatus || !props.serverInfo) return 0
  const percentage = (props.serverStatus.current_players / props.serverInfo.slots) * 100
  return Math.min(Math.max(percentage, 0), 100)
})

const gameTypeName = computed(() => {
  const names = {
    'cs16': 'Counter-Strike 1.6',
    'ag': 'Adrenaline Gamer',
    'hldm': 'Half-Life Deathmatch'
  }
  return names[props.serverInfo?.game_type] || props.serverInfo?.game_type || 'N/A'
})

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('Kopyalandı: ' + text)
  } catch (err) {
    console.error('Kopyalama hatası:', err)
  }
}

const restartServer = async () => {
  if (!confirm('Sunucuyu yeniden başlatmak istediğinizden emin misiniz?')) return

  try {
    await apiClient.post(`/servers/${props.serverId}/restart`)
    alert('Sunucu yeniden başlatılıyor...')
    setTimeout(() => emit('refresh'), 3000)
  } catch (error) {
    alert('Restart hatası: ' + (error.response?.data?.detail || error.message))
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
