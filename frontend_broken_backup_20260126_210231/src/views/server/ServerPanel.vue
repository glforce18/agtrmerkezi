<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Loading State -->
      <div v-if="loading && !currentServer" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin text-6xl neon-orange mb-4">λ</div>
          <p class="text-text-secondary font-hev">Panel yükleniyor...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-6 bg-combine-red bg-opacity-10 border border-combine-red rounded">
        <p class="text-combine-red font-hev">{{ error }}</p>
        <router-link to="/servers/my" class="mt-4 inline-block px-6 py-2 bg-lambda-orange text-cyber-black font-lambda rounded">
          Sunucularıma Dön
        </router-link>
      </div>

      <!-- Server Panel -->
      <template v-else-if="currentServer">
        <!-- Header -->
        <div class="mb-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <router-link to="/servers/my" class="text-text-secondary hover:text-lambda-orange font-hev text-sm mb-2 inline-block">
                ← Sunucularıma Dön
              </router-link>
              <h1 class="text-4xl font-lambda font-bold neon-orange">
                {{ currentServer.name || `Server #${currentServer.id}` }}
              </h1>
              <p class="text-text-secondary font-hev mt-1">
                {{ currentServer.ip }}:{{ currentServer.port }}
              </p>
            </div>

            <div
              class="px-4 py-2 rounded font-hev text-sm font-bold"
              :class="getStatusClass(currentServer.status)"
            >
              {{ getStatusText(currentServer.status) }}
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
            <button
              @click="handleStart"
              :disabled="actionLoading || currentServer.status === 'running'"
              class="px-4 py-2 bg-combine-green bg-opacity-10 border border-combine-green text-combine-green font-lambda rounded hover:bg-combine-green hover:text-cyber-black transition-all disabled:opacity-30"
            >
              <Power :size="16" class="inline mr-1" />
              Başlat
            </button>

            <button
              @click="handleRestart"
              :disabled="actionLoading || currentServer.status !== 'running'"
              class="px-4 py-2 bg-combine-yellow bg-opacity-10 border border-combine-yellow text-combine-yellow font-lambda rounded hover:bg-combine-yellow hover:text-cyber-black transition-all disabled:opacity-30"
            >
              <RotateCw :size="16" class="inline mr-1" />
              Restart
            </button>

            <button
              @click="handleStop"
              :disabled="actionLoading || currentServer.status !== 'running'"
              class="px-4 py-2 bg-combine-red bg-opacity-10 border border-combine-red text-combine-red font-lambda rounded hover:bg-combine-red hover:text-cyber-black transition-all disabled:opacity-30"
            >
              <PowerOff :size="16" class="inline mr-1" />
              Durdur
            </button>

            <button
              @click="refreshStatus"
              :disabled="actionLoading"
              class="px-4 py-2 bg-hev-cyan bg-opacity-10 border border-hev-cyan text-hev-cyan font-lambda rounded hover:bg-hev-cyan hover:text-cyber-black transition-all disabled:opacity-30"
            >
              <RefreshCw :size="16" class="inline mr-1" />
              Yenile
            </button>

            <button
              class="px-4 py-2 bg-xen-purple bg-opacity-10 border border-xen-purple text-xen-purple font-lambda rounded hover:bg-xen-purple hover:text-cyber-black transition-all"
            >
              <Settings :size="16" class="inline mr-1" />
              Ayarlar
            </button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="mb-6">
          <div class="flex gap-2 border-b border-cyber-border">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              class="px-6 py-3 font-lambda font-bold transition-all"
              :class="activeTab === tab.id
                ? 'text-lambda-orange border-b-2 border-lambda-orange'
                : 'text-text-secondary hover:text-text-primary'"
            >
              <component :is="tab.icon" :size="18" class="inline mr-2" />
              {{ tab.label }}
            </button>
          </div>
        </div>

        <!-- Tab Content -->
        <div class="space-y-6">
          <!-- RCON Console Tab -->
          <div v-show="activeTab === 'console'">
            <div class="bg-cyber-darker border border-combine-green rounded-lg overflow-hidden">
              <!-- Console Header -->
              <div class="px-4 py-2 bg-cyber-panel border-b border-combine-green flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 rounded-full bg-combine-red"></div>
                  <div class="w-3 h-3 rounded-full bg-combine-yellow"></div>
                  <div class="w-3 h-3 rounded-full bg-combine-green"></div>
                  <span class="ml-4 font-hev text-combine-green text-sm">HEV_TERMINAL v3.0.0</span>
                </div>
                <button
                  @click="clearConsole"
                  class="text-combine-green hover:text-combine-yellow font-hev text-xs"
                >
                  CLEAR
                </button>
              </div>

              <!-- Console Output -->
              <div
                ref="consoleOutput"
                class="h-96 overflow-y-auto p-4 font-hev text-sm space-y-1"
                style="background: rgba(0, 0, 0, 0.8)"
              >
                <div v-if="consoleLines.length === 0" class="text-combine-green opacity-50">
                  &gt; Konsol hazır. Komut göndermek için aşağıdaki input alanını kullanın...
                </div>
                <div
                  v-for="(line, index) in consoleLines"
                  :key="index"
                  class="flex gap-2"
                  :class="line.type === 'error' ? 'text-combine-red' : line.type === 'command' ? 'text-hev-cyan' : 'text-combine-green'"
                >
                  <span class="opacity-50">[{{ line.timestamp }}]</span>
                  <span v-if="line.type === 'command'" class="text-hev-cyan">&gt;</span>
                  <span class="flex-1" style="text-shadow: 0 0 5px rgba(57, 255, 20, 0.5)">{{ line.text }}</span>
                </div>
              </div>

              <!-- Console Input -->
              <div class="p-4 bg-cyber-panel border-t border-combine-green">
                <form @submit.prevent="sendCommand" class="flex gap-2">
                  <div class="flex-1 flex items-center gap-2 bg-cyber-darker border border-combine-green rounded px-3 py-2">
                    <span class="text-hev-cyan font-hev">&gt;</span>
                    <input
                      v-model="command"
                      type="text"
                      placeholder="RCON komutu girin (örn: status, users, say Merhaba)"
                      class="flex-1 bg-transparent text-combine-green font-hev outline-none"
                      style="text-shadow: 0 0 5px rgba(57, 255, 20, 0.3)"
                      autocomplete="off"
                    />
                  </div>
                  <button
                    type="submit"
                    :disabled="!command.trim() || commandLoading"
                    class="px-6 py-2 bg-combine-green bg-opacity-10 border border-combine-green text-combine-green font-lambda rounded hover:bg-combine-green hover:text-cyber-black transition-all disabled:opacity-30"
                  >
                    GÖNDER
                  </button>
                </form>

                <!-- Quick Commands -->
                <div class="mt-3 flex flex-wrap gap-2">
                  <button
                    v-for="quickCmd in quickCommands"
                    :key="quickCmd.cmd"
                    @click="executeQuickCommand(quickCmd.cmd)"
                    class="px-3 py-1 bg-cyber-darker border border-combine-green text-combine-green font-hev text-xs rounded hover:bg-combine-green hover:text-cyber-black transition-all"
                  >
                    {{ quickCmd.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Players Tab -->
          <div v-show="activeTab === 'players'" class="space-y-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-2xl font-lambda font-bold text-text-primary">
                Aktif Oyuncular ({{ players.length }})
              </h3>
              <button
                @click="refreshPlayers"
                class="px-4 py-2 bg-hev-cyan bg-opacity-10 border border-hev-cyan text-hev-cyan font-lambda text-sm rounded hover:bg-hev-cyan hover:text-cyber-black transition-all"
              >
                <RefreshCw :size="16" class="inline mr-1" />
                Yenile
              </button>
            </div>

            <div v-if="players.length === 0" class="text-center py-10 bg-cyber-panel border border-cyber-border rounded">
              <Users :size="48" class="inline text-text-secondary opacity-30 mb-3" />
              <p class="text-text-secondary font-hev">Şu anda sunucuda oyuncu yok</p>
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="player in players"
                :key="player.slot"
                class="bg-cyber-panel border border-cyber-border p-4 rounded hover:border-lambda-orange transition-all"
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-3">
                      <div class="text-2xl font-lambda neon-orange">{{ player.slot }}</div>
                      <div>
                        <div class="font-lambda text-text-primary">{{ player.name }}</div>
                        <div class="text-sm text-text-secondary font-hev">
                          <span>Ping: {{ player.ping }}ms</span>
                          <span class="mx-2">•</span>
                          <span>Skor: {{ player.score }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="flex gap-2">
                    <button
                      @click="kickPlayer(player.slot)"
                      class="px-4 py-2 bg-combine-yellow bg-opacity-10 border border-combine-yellow text-combine-yellow font-lambda text-sm rounded hover:bg-combine-yellow hover:text-cyber-black transition-all"
                    >
                      <UserX :size="16" class="inline mr-1" />
                      Kick
                    </button>
                    <button
                      @click="banPlayer(player)"
                      class="px-4 py-2 bg-combine-red bg-opacity-10 border border-combine-red text-combine-red font-lambda text-sm rounded hover:bg-combine-red hover:text-cyber-black transition-all"
                    >
                      <Shield :size="16" class="inline mr-1" />
                      Ban
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Admins Tab -->
          <div v-show="activeTab === 'admins'" class="space-y-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-2xl font-lambda font-bold text-text-primary">
                Yöneticiler
              </h3>
              <div class="flex gap-2">
                <button
                  class="px-4 py-2 bg-lambda-orange text-cyber-black font-lambda text-sm rounded hover:shadow-neon-orange transition-all"
                >
                  <UserPlus :size="16" class="inline mr-1" />
                  Yönetici Ekle
                </button>
                <button
                  @click="syncAdmins"
                  class="px-4 py-2 bg-hev-cyan bg-opacity-10 border border-hev-cyan text-hev-cyan font-lambda text-sm rounded hover:bg-hev-cyan hover:text-cyber-black transition-all"
                >
                  <RefreshCw :size="16" class="inline mr-1" />
                  Senkronize Et
                </button>
              </div>
            </div>

            <div class="bg-cyber-panel border border-cyber-border rounded-lg overflow-hidden">
              <table class="w-full">
                <thead class="bg-cyber-darker">
                  <tr class="text-left border-b border-cyber-border">
                    <th class="px-4 py-3 font-lambda text-lambda-orange">SteamID</th>
                    <th class="px-4 py-3 font-lambda text-lambda-orange">İsim</th>
                    <th class="px-4 py-3 font-lambda text-lambda-orange">Yetkiler</th>
                    <th class="px-4 py-3 font-lambda text-lambda-orange">İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-cyber-border hover:bg-cyber-darker transition-all">
                    <td class="px-4 py-3 font-hev text-text-secondary text-sm">STEAM_0:1:12345</td>
                    <td class="px-4 py-3 font-lambda text-text-primary">Admin1</td>
                    <td class="px-4 py-3 text-sm">
                      <span class="px-2 py-1 bg-combine-green bg-opacity-20 text-combine-green rounded font-hev text-xs">FULL ACCESS</span>
                    </td>
                    <td class="px-4 py-3">
                      <button class="text-combine-red hover:text-combine-red-dark font-lambda text-sm">
                        <Trash2 :size="16" class="inline" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Stats Tab -->
          <div v-show="activeTab === 'stats'">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-cyber-panel border border-cyber-border p-6 rounded">
                <div class="text-text-secondary text-sm mb-2 font-hev">CPU Kullanımı</div>
                <div class="text-3xl font-lambda neon-orange mb-2">{{ currentServer.cpu_usage || 0 }}%</div>
                <div class="w-full h-2 bg-cyber-darker rounded overflow-hidden">
                  <div
                    class="h-full bg-lambda-orange"
                    :style="{ width: `${currentServer.cpu_usage || 0}%` }"
                  ></div>
                </div>
              </div>

              <div class="bg-cyber-panel border border-cyber-border p-6 rounded">
                <div class="text-text-secondary text-sm mb-2 font-hev">RAM Kullanımı</div>
                <div class="text-3xl font-lambda text-hev-cyan mb-2">{{ currentServer.ram_usage || 0 }}%</div>
                <div class="w-full h-2 bg-cyber-darker rounded overflow-hidden">
                  <div
                    class="h-full bg-hev-cyan"
                    :style="{ width: `${currentServer.ram_usage || 0}%` }"
                  ></div>
                </div>
              </div>

              <div class="bg-cyber-panel border border-cyber-border p-6 rounded">
                <div class="text-text-secondary text-sm mb-2 font-hev">Network</div>
                <div class="text-3xl font-lambda text-combine-green mb-2">{{ currentServer.network_usage || 0 }} MB/s</div>
                <div class="w-full h-2 bg-cyber-darker rounded overflow-hidden">
                  <div class="h-full bg-combine-green" style="width: 45%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useServersStore } from '@/stores/servers'
import serversAPI from '@/api/servers'
import {
  Power,
  PowerOff,
  RotateCw,
  RefreshCw,
  Settings,
  Terminal,
  Users,
  Shield,
  Activity,
  UserX,
  UserPlus,
  Trash2
} from 'lucide-vue-next'

const route = useRoute()
const serversStore = useServersStore()

const activeTab = ref('console')
const actionLoading = ref(false)
const commandLoading = ref(false)
const command = ref('')
const consoleLines = ref([])
const consoleOutput = ref(null)
const players = ref([])
const autoRefreshInterval = ref(null)

const tabs = [
  { id: 'console', label: 'RCON Konsolu', icon: Terminal },
  { id: 'players', label: 'Oyuncular', icon: Users },
  { id: 'admins', label: 'Yöneticiler', icon: Shield },
  { id: 'stats', label: 'İstatistikler', icon: Activity }
]

const quickCommands = [
  { cmd: 'status', label: 'Status' },
  { cmd: 'users', label: 'Users' },
  { cmd: 'maps *', label: 'Maps' },
  { cmd: 'stats', label: 'Stats' },
  { cmd: 'say Hoşgeldiniz!', label: 'Say Hello' }
]

// Computed
const currentServer = computed(() => serversStore.currentServer)
const loading = computed(() => serversStore.loading)
const error = computed(() => serversStore.error)
const serverId = computed(() => route.params.id)

// Methods
function getStatusClass(status) {
  const statusMap = {
    running: 'bg-combine-green bg-opacity-20 text-combine-green border border-combine-green',
    online: 'bg-combine-green bg-opacity-20 text-combine-green border border-combine-green',
    stopped: 'bg-combine-red bg-opacity-20 text-combine-red border border-combine-red',
    offline: 'bg-combine-red bg-opacity-20 text-combine-red border border-combine-red'
  }
  return statusMap[status] || 'bg-cyber-border text-text-secondary'
}

function getStatusText(status) {
  const textMap = {
    running: 'AKTİF',
    online: 'ONLINE',
    stopped: 'DURDURULDU',
    offline: 'OFFLINE'
  }
  return textMap[status] || 'BİLİNMİYOR'
}

function addConsoleLine(text, type = 'output') {
  const timestamp = new Date().toLocaleTimeString('tr-TR')
  consoleLines.value.push({ text, type, timestamp })

  nextTick(() => {
    if (consoleOutput.value) {
      consoleOutput.value.scrollTop = consoleOutput.value.scrollHeight
    }
  })
}

function clearConsole() {
  consoleLines.value = []
}

async function sendCommand() {
  if (!command.value.trim() || commandLoading.value) return

  const cmd = command.value.trim()
  addConsoleLine(cmd, 'command')
  command.value = ''
  commandLoading.value = true

  try {
    const response = await serversAPI.executeRCONV2(serverId.value, cmd)
    addConsoleLine(response.data.output || 'Komut başarıyla çalıştırıldı', 'output')
  } catch (err) {
    addConsoleLine(err.response?.data?.detail || 'Komut çalıştırılamadı', 'error')
  } finally {
    commandLoading.value = false
  }
}

function executeQuickCommand(cmd) {
  command.value = cmd
  sendCommand()
}

async function handleStart() {
  actionLoading.value = true
  try {
    await serversStore.startServer(serverId.value)
    addConsoleLine('Sunucu başlatılıyor...', 'output')
  } catch (err) {
    console.error('Start error:', err)
  } finally {
    actionLoading.value = false
  }
}

async function handleStop() {
  actionLoading.value = true
  try {
    await serversStore.stopServer(serverId.value)
    addConsoleLine('Sunucu durduruluyor...', 'output')
  } catch (err) {
    console.error('Stop error:', err)
  } finally {
    actionLoading.value = false
  }
}

async function handleRestart() {
  actionLoading.value = true
  try {
    await serversStore.restartServer(serverId.value)
    addConsoleLine('Sunucu yeniden başlatılıyor...', 'output')
  } catch (err) {
    console.error('Restart error:', err)
  } finally {
    actionLoading.value = false
  }
}

async function refreshStatus() {
  actionLoading.value = true
  try {
    await serversStore.getServerStatus(serverId.value)
    addConsoleLine('Durum güncellendi', 'output')
  } catch (err) {
    console.error('Refresh error:', err)
  } finally {
    actionLoading.value = false
  }
}

async function refreshPlayers() {
  try {
    const response = await serversAPI.getPlayersV2(serverId.value)
    players.value = response.data.players || response.data || []
  } catch (err) {
    console.error('Refresh players error:', err)
  }
}

async function kickPlayer(slot) {
  if (!confirm('Bu oyuncuyu atmak istediğinize emin misiniz?')) return

  try {
    await serversAPI.kickPlayer(serverId.value, slot, 'Kicked by admin')
    addConsoleLine(`Oyuncu #${slot} sunucudan atıldı`, 'output')
    refreshPlayers()
  } catch (err) {
    addConsoleLine('Oyuncu atılamadı', 'error')
  }
}

async function banPlayer(player) {
  if (!confirm(`${player.name} adlı oyuncuyu banlamak istediğinize emin misiniz?`)) return

  try {
    await serversAPI.banPlayer(serverId.value, {
      steam_id: player.steam_id,
      reason: 'Banned by admin',
      duration: 0 // Permanent
    })
    addConsoleLine(`${player.name} banlandı`, 'output')
    refreshPlayers()
  } catch (err) {
    addConsoleLine('Oyuncu banlanamadı', 'error')
  }
}

async function syncAdmins() {
  try {
    await serversAPI.syncAdmins(serverId.value)
    addConsoleLine('Yöneticiler senkronize edildi', 'output')
  } catch (err) {
    addConsoleLine('Senkronizasyon başarısız', 'error')
  }
}

// Lifecycle
onMounted(async () => {
  await serversStore.fetchServer(serverId.value)
  await refreshPlayers()

  // Auto-refresh status every 15 seconds
  autoRefreshInterval.value = setInterval(() => {
    serversStore.getServerStatus(serverId.value)
  }, 15000)
})

onUnmounted(() => {
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
  }
})
</script>

<style scoped>
.neon-orange {
  text-shadow: 0 0 10px rgba(255, 107, 53, 0.8);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}
</style>
