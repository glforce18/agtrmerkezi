<template>
  <div class="min-h-screen">
    <div class="container-main py-8">
      <!-- Header -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 class="text-3xl font-bold mb-2">
            <span class="text-gradient-orange">Sunucularim</span>
          </h1>
          <p class="opacity-60">Tum Counter-Strike 1.6 sunucularinizi yonetin</p>
        </div>
        <router-link to="/dashboard">
          <n-button type="primary" size="large">
            <template #icon><n-icon><PlusCircle /></n-icon></template>
            Yeni Sunucu
          </n-button>
        </router-link>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <n-card size="small">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm opacity-60">Toplam Sunucu</div>
              <div class="text-2xl font-bold text-orange-500">{{ servers.length }}</div>
            </div>
            <n-icon :component="Server" size="32" color="#f97316" />
          </div>
        </n-card>

        <n-card size="small">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm opacity-60">Aktif</div>
              <div class="text-2xl font-bold text-green-500">{{ activeServersCount }}</div>
            </div>
            <n-icon :component="Activity" size="32" color="#22c55e" />
          </div>
        </n-card>

        <n-card size="small">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm opacity-60">Toplam Oyuncu</div>
              <div class="text-2xl font-bold text-purple-500">{{ totalPlayersCount }}</div>
            </div>
            <n-icon :component="Users" size="32" color="#8b5cf6" />
          </div>
        </n-card>

        <n-card size="small">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm opacity-60">Kapasite</div>
              <div class="text-2xl font-bold text-cyan-500">{{ totalCapacityCount }}</div>
            </div>
            <n-icon :component="TrendingUp" size="32" color="#06b6d4" />
          </div>
        </n-card>
      </div>

      <!-- Filters -->
      <n-card class="mb-6">
        <div class="flex flex-col md:flex-row gap-4">
          <n-input
            v-model:value="searchQuery"
            placeholder="Sunucu ara..."
            clearable
            class="flex-1"
          >
            <template #prefix>
              <n-icon :component="Search" />
            </template>
          </n-input>
          <n-button-group>
            <n-button :type="filterStatus === 'all' ? 'primary' : 'default'" @click="filterStatus = 'all'">
              Tumu
            </n-button>
            <n-button :type="filterStatus === 'running' ? 'success' : 'default'" @click="filterStatus = 'running'">
              Aktif
            </n-button>
            <n-button :type="filterStatus === 'stopped' ? 'error' : 'default'" @click="filterStatus = 'stopped'">
              Pasif
            </n-button>
          </n-button-group>
        </div>
      </n-card>

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <n-card v-for="i in 6" :key="i">
          <n-skeleton height="200px" />
        </n-card>
      </div>

      <!-- Servers Grid -->
      <div v-else-if="filteredServers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <n-card v-for="server in filteredServers" :key="server.id" hoverable>
          <!-- Server Header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3 flex-1">
              <div class="w-14 h-14 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center flex-shrink-0">
                <n-icon :component="Server" size="28" color="white" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="font-bold text-lg truncate">{{ server.name }}</div>
                <div class="text-sm opacity-60 truncate">{{ server.ip }}:{{ server.port }}</div>
              </div>
            </div>
            <n-badge :type="server.status === 'running' ? 'success' : 'error'" dot />
          </div>

          <!-- Server Info -->
          <n-space vertical size="small" class="mb-4">
            <div class="flex items-center justify-between text-sm">
              <n-space size="small" align="center">
                <n-icon :component="Map" />
                <span class="opacity-60">Map</span>
              </n-space>
              <span class="font-mono text-orange-500">{{ server.current_map || 'de_dust2' }}</span>
            </div>

            <div class="flex items-center justify-between text-sm">
              <n-space size="small" align="center">
                <n-icon :component="Users" />
                <span class="opacity-60">Oyuncular</span>
              </n-space>
              <span class="font-semibold">{{ server.current_players || 0 }}/{{ server.max_players || 32 }}</span>
            </div>

            <n-progress
              type="line"
              :percentage="((server.current_players || 0) / (server.max_players || 32)) * 100"
              :show-indicator="false"
              :height="6"
            />
          </n-space>

          <!-- Server Actions -->
          <n-space>
            <router-link :to="`/servers/${server.id}`">
              <n-button type="primary" size="small">
                <template #icon><n-icon><Settings /></n-icon></template>
                Yonet
              </n-button>
            </router-link>

            <n-button
              v-if="server.status === 'running'"
              type="error"
              size="small"
              @click="stopServer(server.id)"
            >
              <template #icon><n-icon><StopCircle /></n-icon></template>
            </n-button>
            <n-button
              v-else
              type="success"
              size="small"
              @click="startServer(server.id)"
            >
              <template #icon><n-icon><PlayCircle /></n-icon></template>
            </n-button>

            <n-button size="small" @click="restartServer(server.id)">
              <template #icon><n-icon><RefreshCw /></n-icon></template>
            </n-button>
          </n-space>

          <!-- Status -->
          <n-divider />
          <div class="flex items-center justify-between">
            <n-tag :type="server.status === 'running' ? 'success' : 'error'" size="small">
              {{ server.status === 'running' ? 'Calisiyor' : 'Durduruldu' }}
            </n-tag>
            <span class="text-xs opacity-50">ID: #{{ server.id }}</span>
          </div>
        </n-card>
      </div>

      <!-- Empty State -->
      <n-card v-else class="text-center py-16">
        <n-empty :description="searchQuery ? 'Arama kriterlerinize uygun sunucu bulunamadi.' : 'Henuz sunucu olusturmadiniz.'">
          <template #icon>
            <n-icon :component="Server" size="64" />
          </template>
          <template #extra>
            <router-link to="/dashboard">
              <n-button type="primary" size="large">
                <template #icon><n-icon><PlusCircle /></n-icon></template>
                Ilk Sunucunuzu Olusturun
              </n-button>
            </router-link>
          </template>
        </n-empty>
      </n-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  Server,
  Activity,
  Users,
  TrendingUp,
  PlusCircle,
  Search,
  Map,
  Settings,
  PlayCircle,
  StopCircle,
  RefreshCw
} from 'lucide-vue-next'
import { serversAPI } from '@/api'

const message = useMessage()
const servers = ref([])
const loading = ref(true)
const searchQuery = ref('')
const filterStatus = ref('all')

// Computed Stats
const activeServersCount = computed(() => {
  return servers.value.filter(s => s.status === 'running').length
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

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(s => s.status === filterStatus.value)
  }

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
    message.error('Sunucular yuklenemedi')
  } finally {
    loading.value = false
  }
})

// Server Actions
const startServer = async (serverId) => {
  try {
    await serversAPI.start(serverId)
    const server = servers.value.find(s => s.id === serverId)
    if (server) server.status = 'running'
    message.success('Sunucu baslatildi')
  } catch (err) {
    message.error('Sunucu baslatilamadi')
  }
}

const stopServer = async (serverId) => {
  try {
    await serversAPI.stop(serverId)
    const server = servers.value.find(s => s.id === serverId)
    if (server) server.status = 'stopped'
    message.success('Sunucu durduruldu')
  } catch (err) {
    message.error('Sunucu durdurulamadi')
  }
}

const restartServer = async (serverId) => {
  try {
    await serversAPI.restart(serverId)
    message.success('Sunucu yeniden baslatildi')
  } catch (err) {
    message.error('Sunucu yeniden baslatilamadi')
  }
}
</script>
