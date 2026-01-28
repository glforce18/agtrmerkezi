<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-5xl font-lambda font-bold mb-4">
          <span class="neon-orange">SUNUCULARIM</span>
        </h1>
        <p class="text-text-secondary font-hev">Sunucularınızı yönetin, kontrol edin ve izleyin</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin text-6xl neon-orange mb-4">λ</div>
          <p class="text-text-secondary font-hev">Sunucular yükleniyor...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-6 bg-combine-red bg-opacity-10 border border-combine-red rounded">
        <p class="text-combine-red font-hev">{{ error }}</p>
        <button @click="loadServers" class="mt-4 px-6 py-2 bg-lambda-orange text-cyber-black font-lambda rounded hover:shadow-neon-orange transition-all">
          Tekrar Dene
        </button>
      </div>

      <!-- Content -->
      <template v-else>
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div class="bg-cyber-panel border border-cyber-border p-6 rounded hover:border-lambda-orange transition-all">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-3xl font-lambda neon-orange">{{ myServers.length }}</div>
                <div class="text-text-secondary text-sm mt-1">Toplam Sunucu</div>
              </div>
              <Server :size="32" class="text-lambda-orange opacity-50" />
            </div>
          </div>

          <div class="bg-cyber-panel border border-cyber-border p-6 rounded hover:border-combine-green transition-all">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-3xl font-lambda text-combine-green">{{ runningServers.length }}</div>
                <div class="text-text-secondary text-sm mt-1">Aktif</div>
              </div>
              <Power :size="32" class="text-combine-green opacity-50" />
            </div>
          </div>

          <div class="bg-cyber-panel border border-cyber-border p-6 rounded hover:border-combine-red transition-all">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-3xl font-lambda text-combine-red">{{ stoppedServers.length }}</div>
                <div class="text-text-secondary text-sm mt-1">Durdurulmuş</div>
              </div>
              <PowerOff :size="32" class="text-combine-red opacity-50" />
            </div>
          </div>

          <div class="bg-cyber-panel border border-cyber-border p-6 rounded hover:border-hev-cyan transition-all">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-3xl font-lambda text-hev-cyan">{{ totalPlayers }}</div>
                <div class="text-text-secondary text-sm mt-1">Toplam Oyuncu</div>
              </div>
              <Users :size="32" class="text-hev-cyan opacity-50" />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!hasServers" class="text-center py-20">
          <div class="text-8xl neon-orange mb-6">λ</div>
          <h2 class="text-3xl font-lambda font-bold text-text-primary mb-4">
            Henüz Sunucunuz Yok
          </h2>
          <p class="text-text-secondary mb-8 font-hev">
            İlk sunucunuzu oluşturun ve oyun topluluğunuzu büyütmeye başlayın
          </p>
          <router-link
            to="/servers/rent"
            class="inline-block px-8 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all duration-300"
          >
            SUNUCU KİRALA
          </router-link>
        </div>

        <!-- Server Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="server in myServers"
            :key="server.id"
            class="bg-cyber-panel border border-cyber-border rounded-lg overflow-hidden hover:border-lambda-orange transition-all duration-300 hover:shadow-neon-orange"
          >
            <!-- Server Header -->
            <div class="p-6 border-b border-cyber-border">
              <div class="flex items-start justify-between mb-3">
                <div class="flex-1">
                  <h3 class="text-xl font-lambda font-bold text-text-primary mb-1">
                    {{ server.name || `Server #${server.id}` }}
                  </h3>
                  <div class="flex items-center gap-2 text-sm text-text-secondary font-hev">
                    <Gamepad2 :size="14" />
                    <span>{{ server.game_type || 'CS 1.6' }}</span>
                  </div>
                </div>

                <!-- Status Badge -->
                <div
                  class="px-3 py-1 rounded font-hev text-xs font-bold"
                  :class="getStatusClass(server.status)"
                >
                  {{ getStatusText(server.status) }}
                </div>
              </div>

              <!-- Server Info -->
              <div class="space-y-2 text-sm">
                <div class="flex items-center gap-2 text-text-secondary font-hev">
                  <Globe :size="14" class="text-hev-cyan" />
                  <span>{{ server.ip }}:{{ server.port }}</span>
                </div>
                <div class="flex items-center gap-2 text-text-secondary font-hev">
                  <Users :size="14" class="text-combine-green" />
                  <span>{{ server.players?.length || 0 }} / {{ server.max_players || 32 }} Oyuncu</span>
                </div>
              </div>
            </div>

            <!-- Server Controls -->
            <div class="p-6 space-y-3">
              <!-- Action Buttons -->
              <div class="grid grid-cols-3 gap-2">
                <button
                  @click="handleStart(server.id)"
                  :disabled="isLoading(server.id) || server.status === 'running'"
                  class="px-4 py-2 bg-combine-green bg-opacity-10 border border-combine-green text-combine-green font-lambda text-sm rounded hover:bg-combine-green hover:text-cyber-black transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <Power :size="16" class="inline-block mr-1" />
                  Başlat
                </button>

                <button
                  @click="handleRestart(server.id)"
                  :disabled="isLoading(server.id) || server.status !== 'running'"
                  class="px-4 py-2 bg-combine-yellow bg-opacity-10 border border-combine-yellow text-combine-yellow font-lambda text-sm rounded hover:bg-combine-yellow hover:text-cyber-black transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <RotateCw :size="16" class="inline-block mr-1" />
                  Restart
                </button>

                <button
                  @click="handleStop(server.id)"
                  :disabled="isLoading(server.id) || server.status !== 'running'"
                  class="px-4 py-2 bg-combine-red bg-opacity-10 border border-combine-red text-combine-red font-lambda text-sm rounded hover:bg-combine-red hover:text-cyber-black transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <PowerOff :size="16" class="inline-block mr-1" />
                  Durdur
                </button>
              </div>

              <!-- Panel Button -->
              <router-link
                :to="`/servers/${server.id}`"
                class="block w-full px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold text-center rounded hover:shadow-neon-orange transition-all duration-300"
              >
                <Terminal :size="16" class="inline-block mr-2" />
                PANEL AÇ
              </router-link>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useServersStore } from '@/stores/servers'
import {
  Server,
  Power,
  PowerOff,
  Users,
  Globe,
  Gamepad2,
  Terminal,
  RotateCw
} from 'lucide-vue-next'

const serversStore = useServersStore()
const loadingActions = ref(new Set())

// Computed
const myServers = computed(() => serversStore.myServers)
const runningServers = computed(() => serversStore.runningServers)
const stoppedServers = computed(() => serversStore.stoppedServers)
const hasServers = computed(() => serversStore.hasServers)
const loading = computed(() => serversStore.loading)
const error = computed(() => serversStore.error)

const totalPlayers = computed(() => {
  return myServers.value.reduce((total, server) => {
    return total + (server.players?.length || 0)
  }, 0)
})

// Methods
function isLoading(serverId) {
  return loadingActions.value.has(serverId)
}

function getStatusClass(status) {
  const statusMap = {
    running: 'bg-combine-green bg-opacity-20 text-combine-green border border-combine-green',
    online: 'bg-combine-green bg-opacity-20 text-combine-green border border-combine-green',
    stopped: 'bg-combine-red bg-opacity-20 text-combine-red border border-combine-red',
    offline: 'bg-combine-red bg-opacity-20 text-combine-red border border-combine-red',
    pending: 'bg-combine-yellow bg-opacity-20 text-combine-yellow border border-combine-yellow',
    creating: 'bg-hev-cyan bg-opacity-20 text-hev-cyan border border-hev-cyan'
  }
  return statusMap[status] || 'bg-cyber-border text-text-secondary'
}

function getStatusText(status) {
  const textMap = {
    running: 'AKTİF',
    online: 'ONLINE',
    stopped: 'DURDURULDU',
    offline: 'OFFLINE',
    pending: 'BEKLEMEDE',
    creating: 'OLUŞTURULUYOR'
  }
  return textMap[status] || 'BİLİNMİYOR'
}

async function handleStart(serverId) {
  if (isLoading(serverId)) return

  loadingActions.value.add(serverId)
  try {
    await serversStore.startServer(serverId)
  } catch (err) {
    console.error('Start server error:', err)
  } finally {
    loadingActions.value.delete(serverId)
  }
}

async function handleStop(serverId) {
  if (isLoading(serverId)) return

  loadingActions.value.add(serverId)
  try {
    await serversStore.stopServer(serverId)
  } catch (err) {
    console.error('Stop server error:', err)
  } finally {
    loadingActions.value.delete(serverId)
  }
}

async function handleRestart(serverId) {
  if (isLoading(serverId)) return

  loadingActions.value.add(serverId)
  try {
    await serversStore.restartServer(serverId)
  } catch (err) {
    console.error('Restart server error:', err)
  } finally {
    loadingActions.value.delete(serverId)
  }
}

async function loadServers() {
  try {
    await serversStore.fetchMyServers()
  } catch (err) {
    console.error('Load servers error:', err)
  }
}

// Lifecycle
onMounted(() => {
  loadServers()

  // Auto-refresh every 30 seconds
  const interval = setInterval(() => {
    if (!loading.value) {
      loadServers()
    }
  }, 30000)

  // Cleanup
  return () => clearInterval(interval)
})
</script>

<style scoped>
.bg-lambda-gradient {
  background: linear-gradient(135deg, #FF6B35 0%, #E85D2C 100%);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}
</style>
