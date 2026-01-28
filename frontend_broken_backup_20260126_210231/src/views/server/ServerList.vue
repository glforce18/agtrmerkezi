<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-5xl font-lambda font-bold mb-4">
          <span class="text-hev-cyan" style="text-shadow: 0 0 20px rgba(0, 245, 255, 0.6)">SUNUCU LİSTESİ</span>
        </h1>
        <p class="text-text-secondary font-hev">Aktif Half-Life ve Counter-Strike 1.6 sunucularını keşfet</p>
      </div>

      <!-- Filters -->
      <div class="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Search -->
        <div class="md:col-span-2">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Sunucu ara... (isim, IP, harita)"
            class="w-full px-4 py-3 bg-cyber-panel border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
          />
        </div>

        <!-- Game Type -->
        <div>
          <select
            v-model="filters.game_type"
            class="w-full px-4 py-3 bg-cyber-panel border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
          >
            <option value="">Tüm Oyunlar</option>
            <option value="cs16">Counter-Strike 1.6</option>
            <option value="hl">Half-Life</option>
            <option value="czero">Condition Zero</option>
            <option value="tfc">Team Fortress Classic</option>
          </select>
        </div>

        <!-- Sort -->
        <div>
          <select
            v-model="filters.sort"
            class="w-full px-4 py-3 bg-cyber-panel border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
          >
            <option value="players">En Kalabalık</option>
            <option value="name">İsim (A-Z)</option>
            <option value="ping">Ping (Düşük-Yüksek)</option>
          </select>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-cyber-panel border border-cyber-border p-4 rounded text-center">
          <div class="text-2xl font-lambda text-lambda-orange">{{ filteredServers.length }}</div>
          <div class="text-xs text-text-secondary font-hev">Sunucu</div>
        </div>
        <div class="bg-cyber-panel border border-cyber-border p-4 rounded text-center">
          <div class="text-2xl font-lambda text-combine-green">{{ totalPlayers }}</div>
          <div class="text-xs text-text-secondary font-hev">Oyuncu</div>
        </div>
        <div class="bg-cyber-panel border border-cyber-border p-4 rounded text-center">
          <div class="text-2xl font-lambda text-hev-cyan">{{ onlineServers }}</div>
          <div class="text-xs text-text-secondary font-hev">Online</div>
        </div>
        <div class="bg-cyber-panel border border-cyber-border p-4 rounded text-center">
          <div class="text-2xl font-lambda text-xen-purple">{{ totalSlots }}</div>
          <div class="text-xs text-text-secondary font-hev">Toplam Slot</div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin text-6xl text-hev-cyan mb-4">λ</div>
          <p class="text-text-secondary font-hev">Sunucular yükleniyor...</p>
        </div>
      </div>

      <!-- Server Table -->
      <div v-else class="bg-cyber-panel border border-cyber-border rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-cyber-darker border-b border-cyber-border">
              <tr>
                <th class="px-4 py-3 text-left font-lambda text-lambda-orange text-sm">Sunucu Adı</th>
                <th class="px-4 py-3 text-left font-lambda text-lambda-orange text-sm">Oyuncular</th>
                <th class="px-4 py-3 text-left font-lambda text-lambda-orange text-sm">Harita</th>
                <th class="px-4 py-3 text-left font-lambda text-lambda-orange text-sm">Oyun</th>
                <th class="px-4 py-3 text-left font-lambda text-lambda-orange text-sm">IP:Port</th>
                <th class="px-4 py-3 text-left font-lambda text-lambda-orange text-sm">Ping</th>
                <th class="px-4 py-3 text-left font-lambda text-lambda-orange text-sm">Durum</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="server in paginatedServers"
                :key="server.id"
                class="border-b border-cyber-border hover:bg-cyber-darker transition-all cursor-pointer"
                @click="connectToServer(server)"
              >
                <!-- Server Name -->
                <td class="px-4 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-2 h-2 rounded-full"
                      :class="server.online ? 'bg-combine-green' : 'bg-combine-red'">
                    </div>
                    <div>
                      <div class="font-lambda text-text-primary">{{ server.name }}</div>
                      <div v-if="server.tags" class="flex gap-1 mt-1">
                        <span
                          v-for="tag in server.tags.slice(0, 3)"
                          :key="tag"
                          class="px-2 py-0.5 bg-lambda-orange bg-opacity-20 text-lambda-orange rounded text-xs font-hev"
                        >
                          {{ tag }}
                        </span>
                      </div>
                    </div>
                  </div>
                </td>

                <!-- Players -->
                <td class="px-4 py-4">
                  <div class="flex items-center gap-2">
                    <Users :size="14" class="text-hev-cyan" />
                    <span class="font-lambda text-text-primary">
                      {{ server.current_players || 0 }}/{{ server.max_players || 32 }}
                    </span>
                    <div class="w-16 h-2 bg-cyber-darker rounded overflow-hidden">
                      <div
                        class="h-full bg-hev-cyan"
                        :style="{ width: `${getPlayerPercentage(server)}%` }"
                      ></div>
                    </div>
                  </div>
                </td>

                <!-- Map -->
                <td class="px-4 py-4">
                  <div class="flex items-center gap-2">
                    <Map :size="14" class="text-combine-green" />
                    <span class="font-hev text-text-primary text-sm">{{ server.map || 'de_dust2' }}</span>
                  </div>
                </td>

                <!-- Game -->
                <td class="px-4 py-4">
                  <span class="font-hev text-text-secondary text-sm">{{ getGameName(server.game_type) }}</span>
                </td>

                <!-- IP:Port -->
                <td class="px-4 py-4">
                  <div class="flex items-center gap-2">
                    <Globe :size="14" class="text-xen-purple" />
                    <code class="font-hev text-text-primary text-sm">{{ server.ip }}:{{ server.port }}</code>
                  </div>
                </td>

                <!-- Ping -->
                <td class="px-4 py-4">
                  <span
                    class="font-lambda"
                    :class="getPingColor(server.ping || 0)"
                  >
                    {{ server.ping || 0 }}ms
                  </span>
                </td>

                <!-- Status -->
                <td class="px-4 py-4">
                  <button
                    v-if="server.online"
                    @click.stop="connectToServer(server)"
                    class="px-4 py-2 bg-combine-green bg-opacity-10 border border-combine-green text-combine-green font-lambda text-xs rounded hover:bg-combine-green hover:text-cyber-black transition-all"
                  >
                    <Zap :size="14" class="inline mr-1" />
                    BAĞLAN
                  </button>
                  <span v-else class="px-4 py-2 bg-combine-red bg-opacity-10 border border-combine-red text-combine-red font-lambda text-xs rounded">
                    OFFLINE
                  </span>
                </td>
              </tr>

              <tr v-if="filteredServers.length === 0">
                <td colspan="7" class="px-4 py-12 text-center">
                  <Server :size="48" class="inline text-text-secondary opacity-30 mb-3" />
                  <p class="text-text-secondary font-hev">Sunucu bulunamadı</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="px-4 py-3 bg-cyber-darker border-t border-cyber-border flex items-center justify-between">
          <div class="text-sm text-text-secondary font-hev">
            {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, filteredServers.length) }} / {{ filteredServers.length }}
          </div>

          <div class="flex gap-2">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="px-3 py-1 bg-cyber-panel border border-cyber-border text-text-primary font-lambda text-sm rounded hover:border-hev-cyan transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              ‹ Önceki
            </button>

            <button
              v-for="page in visiblePages"
              :key="page"
              @click="currentPage = page"
              class="px-3 py-1 font-lambda text-sm rounded transition-all"
              :class="currentPage === page
                ? 'bg-hev-cyan text-cyber-black'
                : 'bg-cyber-panel border border-cyber-border text-text-primary hover:border-hev-cyan'"
            >
              {{ page }}
            </button>

            <button
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 bg-cyber-panel border border-cyber-border text-text-primary font-lambda text-sm rounded hover:border-hev-cyan transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Sonraki ›
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import serversAPI from '@/api/servers'
import { Users, Map, Globe, Zap, Server } from 'lucide-vue-next'

const loading = ref(false)
const servers = ref([])
const currentPage = ref(1)
const perPage = 20

const filters = ref({
  search: '',
  game_type: '',
  sort: 'players'
})

// Computed
const filteredServers = computed(() => {
  let filtered = [...servers.value]

  // Search filter
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(s =>
      s.name?.toLowerCase().includes(search) ||
      s.ip?.includes(search) ||
      s.map?.toLowerCase().includes(search)
    )
  }

  // Game type filter
  if (filters.value.game_type) {
    filtered = filtered.filter(s => s.game_type === filters.value.game_type)
  }

  // Sort
  switch (filters.value.sort) {
    case 'players':
      filtered.sort((a, b) => (b.current_players || 0) - (a.current_players || 0))
      break
    case 'name':
      filtered.sort((a, b) => (a.name || '').localeCompare(b.name || ''))
      break
    case 'ping':
      filtered.sort((a, b) => (a.ping || 999) - (b.ping || 999))
      break
  }

  return filtered
})

const paginatedServers = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredServers.value.slice(start, start + perPage)
})

const totalPages = computed(() => Math.ceil(filteredServers.value.length / perPage))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

const totalPlayers = computed(() =>
  servers.value.reduce((sum, s) => sum + (s.current_players || 0), 0)
)

const onlineServers = computed(() =>
  servers.value.filter(s => s.online).length
)

const totalSlots = computed(() =>
  servers.value.reduce((sum, s) => sum + (s.max_players || 0), 0)
)

// Methods
function getPlayerPercentage(server) {
  if (!server.max_players) return 0
  return Math.round((server.current_players || 0) / server.max_players * 100)
}

function getGameName(gameType) {
  const names = {
    cs16: 'CS 1.6',
    hl: 'Half-Life',
    czero: 'CZ',
    tfc: 'TFC'
  }
  return names[gameType] || 'Unknown'
}

function getPingColor(ping) {
  if (ping < 50) return 'text-combine-green'
  if (ping < 100) return 'text-combine-yellow'
  return 'text-combine-red'
}

function connectToServer(server) {
  const connectURL = `steam://connect/${server.ip}:${server.port}`
  window.location.href = connectURL
}

async function loadServers() {
  loading.value = true
  try {
    const response = await serversAPI.getServers()
    servers.value = response.data.servers || response.data || []

    // Mock data if empty
    if (servers.value.length === 0) {
      servers.value = Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        name: `[TR] AGTR Server #${i + 1}`,
        ip: `185.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
        port: 27015 + i,
        current_players: Math.floor(Math.random() * 32),
        max_players: 32,
        map: ['de_dust2', 'de_inferno', 'cs_office', 'de_nuke', 'de_train'][Math.floor(Math.random() * 5)],
        game_type: ['cs16', 'hl', 'czero'][Math.floor(Math.random() * 3)],
        online: Math.random() > 0.2,
        ping: Math.floor(Math.random() * 100) + 10,
        tags: ['Public', 'Deathmatch', 'Ranked'].slice(0, Math.floor(Math.random() * 3) + 1)
      }))
    }
  } catch (err) {
    console.error('Load servers error:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadServers()

  // Auto-refresh every 30 seconds
  setInterval(loadServers, 30000)
})
</script>
