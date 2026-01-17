<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 animate-slide-down">
        <div>
          <h1 class="text-4xl font-display font-bold mb-2">
            <span class="neon-text">Sunucularım</span>
          </h1>
          <p class="opacity-60">
            Tüm Counter-Strike 1.6 sunucularınızı yönetin
          </p>
        </div>
        <router-link to="/dashboard">
          <BaseButton variant="gaming" size="lg">
            <PlusCircleIcon class="w-5 h-5 mr-2" />
            Yeni Sunucu
          </BaseButton>
        </router-link>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8 animate-slide-up">
        <BaseCard variant="glass" class="card-hover">
          <div class="flex items-center justify-between p-4">
            <div>
              <p class="text-sm opacity-60">Toplam Sunucu</p>
              <h3 class="text-2xl font-bold text-primary">{{ servers.length }}</h3>
            </div>
            <ServerIcon class="w-8 h-8 text-primary" />
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="flex items-center justify-between p-4">
            <div>
              <p class="text-sm opacity-60">Aktif</p>
              <h3 class="text-2xl font-bold text-success">{{ activeServersCount }}</h3>
            </div>
            <ActivityIcon class="w-8 h-8 text-success" />
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="flex items-center justify-between p-4">
            <div>
              <p class="text-sm opacity-60">Toplam Oyuncu</p>
              <h3 class="text-2xl font-bold text-secondary">{{ totalPlayersCount }}</h3>
            </div>
            <UsersIcon class="w-8 h-8 text-secondary" />
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="flex items-center justify-between p-4">
            <div>
              <p class="text-sm opacity-60">Kapasite</p>
              <h3 class="text-2xl font-bold text-accent">{{ totalCapacityCount }}</h3>
            </div>
            <TrendingUpIcon class="w-8 h-8 text-accent" />
          </div>
        </BaseCard>
      </div>

      <!-- Filters & Search -->
      <BaseCard variant="glass" class="mb-6 animate-slide-up" style="animation-delay: 0.1s">
        <div class="p-4">
          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1">
              <BaseInput
                v-model="searchQuery"
                placeholder="Sunucu ara..."
                :icon="SearchIcon"
              />
            </div>
            <div class="flex gap-2">
              <button
                @click="filterStatus = 'all'"
                :class="['btn btn-sm', filterStatus === 'all' ? 'btn-primary' : 'btn-ghost']"
              >
                Tümü
              </button>
              <button
                @click="filterStatus = 'active'"
                :class="['btn btn-sm', filterStatus === 'active' ? 'btn-success' : 'btn-ghost']"
              >
                Aktif
              </button>
              <button
                @click="filterStatus = 'inactive'"
                :class="['btn btn-sm', filterStatus === 'inactive' ? 'btn-error' : 'btn-ghost']"
              >
                Pasif
              </button>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BaseCard v-for="i in 6" :key="i" variant="glass" class="animate-pulse">
          <div class="p-6">
            <div class="flex items-center gap-4 mb-4">
              <div class="w-16 h-16 bg-base-200/50 rounded-lg"></div>
              <div class="flex-1">
                <div class="h-4 bg-base-200/50 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-base-200/50 rounded w-1/2"></div>
              </div>
            </div>
            <div class="space-y-2">
              <div class="h-3 bg-base-200/50 rounded"></div>
              <div class="h-3 bg-base-200/50 rounded"></div>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Servers Grid -->
      <div v-else-if="filteredServers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BaseCard
          v-for="server in filteredServers"
          :key="server.id"
          variant="glass"
          class="card-hover group animate-slide-up"
        >
          <div class="p-6">
            <!-- Server Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3 flex-1">
                <div class="w-16 h-16 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center flex-shrink-0">
                  <ServerIcon class="w-8 h-8 text-white" />
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="font-bold text-lg truncate group-hover:text-primary transition-colors">
                    {{ server.name }}
                  </h3>
                  <p class="text-sm opacity-60 truncate">
                    {{ server.ip }}:{{ server.port }}
                  </p>
                </div>
              </div>
              <div
                :class="[
                  'w-3 h-3 rounded-full flex-shrink-0',
                  server.status === 'active' ? 'status-online' : 'status-offline'
                ]"
              ></div>
            </div>

            <!-- Server Info -->
            <div class="space-y-2 mb-4">
              <div class="flex items-center justify-between text-sm">
                <div class="flex items-center gap-2 opacity-60">
                  <MapIcon class="w-4 h-4" />
                  <span>Map</span>
                </div>
                <span class="font-mono text-primary">{{ server.current_map || 'de_dust2' }}</span>
              </div>

              <div class="flex items-center justify-between text-sm">
                <div class="flex items-center gap-2 opacity-60">
                  <UsersIcon class="w-4 h-4" />
                  <span>Oyuncular</span>
                </div>
                <span class="font-semibold">
                  {{ server.current_players || 0 }}/{{ server.max_players || 32 }}
                </span>
              </div>

              <!-- Player Progress Bar -->
              <div class="w-full bg-base-200/50 rounded-full h-2 overflow-hidden">
                <div
                  class="bg-gradient-to-r from-primary to-secondary h-full rounded-full transition-all duration-300"
                  :style="{ width: `${((server.current_players || 0) / (server.max_players || 32)) * 100}%` }"
                ></div>
              </div>
            </div>

            <!-- Server Actions -->
            <div class="flex gap-2">
              <router-link :to="`/servers/${server.id}`" class="flex-1">
                <BaseButton variant="primary" size="sm" block>
                  <SettingsIcon class="w-4 h-4 mr-1" />
                  Yönet
                </BaseButton>
              </router-link>

              <button
                v-if="server.status === 'active'"
                @click="stopServer(server.id)"
                class="btn btn-sm btn-error"
                title="Durdur"
              >
                <StopCircleIcon class="w-4 h-4" />
              </button>
              <button
                v-else
                @click="startServer(server.id)"
                class="btn btn-sm btn-success"
                title="Başlat"
              >
                <PlayCircleIcon class="w-4 h-4" />
              </button>

              <button
                @click="restartServer(server.id)"
                class="btn btn-sm btn-ghost"
                title="Yeniden Başlat"
              >
                <RefreshCwIcon class="w-4 h-4" />
              </button>
            </div>

            <!-- Status Badge -->
            <div class="mt-4 pt-4 border-t border-base-300">
              <div class="flex items-center justify-between">
                <span
                  :class="[
                    'badge badge-sm',
                    server.status === 'active' ? 'badge-success' : 'badge-error'
                  ]"
                >
                  {{ server.status === 'active' ? 'Aktif' : 'Pasif' }}
                </span>
                <span class="text-xs opacity-50">
                  ID: #{{ server.id }}
                </span>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Empty State -->
      <BaseCard v-else variant="glass" class="text-center py-16">
        <div class="max-w-md mx-auto">
          <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-base-200 flex items-center justify-center">
            <ServerIcon class="w-12 h-12 opacity-40" />
          </div>
          <h3 class="text-2xl font-bold mb-2">Sunucu Bulunamadı</h3>
          <p class="opacity-60 mb-6">
            {{ searchQuery ? 'Arama kriterlerinize uygun sunucu bulunamadı.' : 'Henüz sunucu oluşturmadınız.' }}
          </p>
          <router-link to="/dashboard">
            <BaseButton variant="gaming" size="lg">
              <PlusCircleIcon class="w-5 h-5 mr-2" />
              İlk Sunucunuzu Oluşturun
            </BaseButton>
          </router-link>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import {
  ServerIcon,
  ActivityIcon,
  UsersIcon,
  TrendingUpIcon,
  PlusCircleIcon,
  SearchIcon,
  MapIcon,
  SettingsIcon,
  PlayCircleIcon,
  StopCircleIcon,
  RefreshCwIcon
} from 'lucide-vue-next'
import { serversAPI } from '@/api'

const router = useRouter()
const servers = ref([])
const loading = ref(true)
const searchQuery = ref('')
const filterStatus = ref('all')

// Computed Stats
const activeServersCount = computed(() => {
  return servers.value.filter(s => s.status === 'active').length
})

const totalPlayersCount = computed(() => {
  return servers.value.reduce((sum, s) => sum + (s.current_players || 0), 0)
})

const totalCapacityCount = computed(() => {
  return servers.value.reduce((sum, s) => sum + (s.max_players || 32), 0)
})

// Filtered Servers
const filteredServers = computed(() => {
  let filtered = servers.value

  // Filter by status
  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(s => s.status === filterStatus.value)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(s =>
      s.name.toLowerCase().includes(query) ||
      s.ip.toLowerCase().includes(query) ||
      (s.current_map && s.current_map.toLowerCase().includes(query))
    )
  }

  return filtered
})

// Load Servers
onMounted(async () => {
  try {
    const data = await serversAPI.getAll()
    servers.value = data.items || []
  } catch (err) {
    // Failed to load servers - will show empty state
  } finally {
    loading.value = false
  }
})

// Server Actions
const startServer = async (serverId) => {
  try {
    await serversAPI.start(serverId)
    // Refresh server status
    const server = servers.value.find(s => s.id === serverId)
    if (server) server.status = 'active'
  } catch (err) {
    // Failed to start server - status unchanged
  }
}

const stopServer = async (serverId) => {
  try {
    await serversAPI.stop(serverId)
    // Refresh server status
    const server = servers.value.find(s => s.id === serverId)
    if (server) server.status = 'inactive'
  } catch (err) {
    // Failed to stop server - status unchanged
  }
}

const restartServer = async (serverId) => {
  try {
    await serversAPI.restart(serverId)
  } catch (err) {
    // Failed to restart server - status unchanged
  }
}
</script>

<style scoped>
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

.status-online {
  @apply bg-success shadow-[0_0_10px_rgba(16,185,129,0.5)];
  animation: pulse-glow 2s ease-in-out infinite;
}

.status-offline {
  @apply bg-error;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-down {
  animation: slideDown 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}
</style>
