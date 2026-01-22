<template>
  <div class="community-servers-page">
    <!-- Background Effects -->
    <div class="page-background">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
      <!-- Floating Weapons -->
      <div class="floating-weapons">
        <GameIcon name="weapon-ak47" size="xl" class="floating-weapon weapon-1" color="rgba(249,115,22,0.15)" />
        <GameIcon name="weapon-awp" size="xl" class="floating-weapon weapon-2" color="rgba(139,92,246,0.15)" />
        <GameIcon name="weapon-crowbar" size="lg" class="floating-weapon weapon-3" color="rgba(249,115,22,0.2)" />
      </div>
    </div>

    <div class="container-main py-6 relative z-10">
      <!-- Page Header -->
      <header class="page-header mb-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold flex items-center gap-3 mb-2">
              <div class="icon-wrapper">
                <GameIcon name="cs-crosshair" size="lg" color="#f97316" />
              </div>
              <span class="text-gradient-orange">Topluluk Sunuculari</span>
            </h1>
            <p class="text-sm text-gray-400">
              Half-Life, CS 1.6 ve AG sunuculari - Gercek zamanli tarama
            </p>
          </div>

          <!-- Stats Cards & Add Server Button -->
          <div class="flex items-center gap-3">
            <div class="stat-mini">
              <GameIcon name="server-pulse" size="sm" color="#22c55e" />
              <span class="text-green-500 font-bold">{{ stats.online_servers }}</span>
              <span class="text-xs text-gray-500">Online</span>
            </div>
            <div class="stat-mini">
              <GameIcon name="hud-health" size="sm" color="#3b82f6" />
              <span class="text-blue-500 font-bold">{{ stats.total_players }}</span>
              <span class="text-xs text-gray-500">Oyuncu</span>
            </div>
            <n-tooltip :disabled="isLoggedIn" trigger="hover">
              <template #trigger>
                <n-button
                  type="primary"
                  size="small"
                  @click="openSubmitModal"
                  class="add-server-btn muzzle-flash-hover"
                  :class="{ 'btn-disabled': !isLoggedIn }"
                >
                  <Lock v-if="!isLoggedIn" class="w-4 h-4 mr-1" />
                  <Plus v-else class="w-4 h-4 mr-1" />
                  {{ isLoggedIn ? 'Sunucu Ekle' : 'Giris Yap' }}
                </n-button>
              </template>
              Sunucu eklemek icin giris yapin
            </n-tooltip>
            <n-button
              quaternary
              circle
              size="small"
              @click="refreshData"
              :loading="loading"
              class="muzzle-flash-hover"
            >
              <template #icon>
                <n-icon :component="RefreshCw" size="16" />
              </template>
            </n-button>
          </div>
        </div>
      </header>

      <!-- My Servers Section (for logged in users) -->
      <div v-if="isLoggedIn && myServers.length > 0" class="my-servers-section mb-6">
        <div class="section-header">
          <h2 class="text-lg font-semibold flex items-center gap-2">
            <User class="w-5 h-5 text-orange-500" />
            Benim Sunucularim
          </h2>
          <n-button quaternary size="small" @click="fetchMyServers" :loading="myServersLoading">
            <RefreshCw class="w-4 h-4" />
          </n-button>
        </div>
        <div class="my-servers-grid">
          <div
            v-for="server in myServers"
            :key="'my-' + server.id"
            class="my-server-card glass-card"
          >
            <div class="my-server-header">
              <div class="game-badge-sm" :style="{ background: getGameColor(server.game_type) }">
                <GameIcon :name="getGameIcon(server.game_type)" size="xs" color="#fff" />
              </div>
              <div class="my-server-info">
                <h4 class="my-server-name">{{ server.name }}</h4>
                <p class="my-server-address">{{ server.address }}</p>
              </div>
              <div class="my-server-status-wrap">
                <div
                  class="status-indicator"
                  :class="server.is_online ? 'online' : 'offline'"
                  :title="server.is_online ? 'Online' : 'Offline'"
                ></div>
                <span class="player-count" v-if="server.is_online">
                  {{ server.players }}/{{ server.max_players }}
                </span>
              </div>
            </div>
            <div class="my-server-actions">
              <n-button size="tiny" quaternary @click="refreshServerStatus(server)">
                <RefreshCw class="w-3 h-3" />
              </n-button>
              <n-button size="tiny" quaternary @click="copyAddress(server.address)">
                <Copy class="w-3 h-3" />
              </n-button>
              <n-button
                size="tiny"
                quaternary
                type="error"
                @click="confirmDeleteServer(server)"
              >
                <Trash2 class="w-3 h-3" />
              </n-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Game Type Tabs -->
      <div class="game-tabs mb-6">
        <button
          v-for="game in gameTypes"
          :key="game.value"
          class="game-tab"
          :class="{ active: selectedGame === game.value }"
          @click="selectedGame = game.value"
        >
          <GameIcon :name="game.icon" size="md" :color="selectedGame === game.value ? game.color : '#64748b'" />
          <span>{{ game.label }}</span>
          <span class="count" :style="{ background: selectedGame === game.value ? game.color : '' }">
            {{ getGameCount(game.value) }}
          </span>
        </button>
      </div>

      <!-- Filters -->
      <div class="filters-bar mb-4">
        <n-input
          v-model:value="searchQuery"
          placeholder="Sunucu ara..."
          clearable
          size="small"
          class="search-input"
        >
          <template #prefix>
            <n-icon :component="Search" />
          </template>
        </n-input>

        <n-select
          v-model:value="filters.country"
          :options="countryOptions"
          placeholder="Ulke"
          clearable
          size="small"
          class="filter-select"
        />

        <n-checkbox v-model:checked="filters.hasPlayers" size="small">
          Oyunculu
        </n-checkbox>

        <n-select
          v-model:value="sortBy"
          :options="sortOptions"
          size="small"
          class="sort-select"
        />
      </div>

      <!-- Loading State -->
      <div v-if="loading && servers.length === 0" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Sunucular taraniyor...</p>
      </div>

      <!-- Server Grid -->
      <div v-else-if="filteredServers.length > 0" class="servers-grid">
        <div
          v-for="server in filteredServers"
          :key="server.id"
          class="server-card glass-card"
          :class="{ featured: server.is_featured }"
          @click="showServerDetail(server)"
        >
          <!-- Featured Badge -->
          <div v-if="server.is_featured" class="featured-badge popular-badge-pulse">
            <Star class="w-3 h-3" />
            One Cikan
          </div>

          <!-- Server Header -->
          <div class="server-header">
            <div class="game-badge" :style="{ background: getGameColor(server.game_type) }">
              <GameIcon :name="getGameIcon(server.game_type)" size="sm" color="#fff" />
            </div>
            <div class="server-info">
              <h3 class="server-name">{{ server.name || 'Unnamed Server' }}</h3>
              <p class="server-address">{{ server.address }}</p>
            </div>
            <div class="server-status" :class="server.is_online ? 'online server-online-pulse' : 'offline'">
              {{ server.is_online ? 'Online' : 'Offline' }}
            </div>
          </div>

          <!-- Server Details -->
          <div class="server-details">
            <!-- Map -->
            <div class="detail-item">
              <Map class="w-4 h-4 text-gray-500" />
              <span>{{ server.current_map || 'Unknown' }}</span>
            </div>

            <!-- Players -->
            <div class="detail-item players">
              <Users class="w-4 h-4" :class="server.players > 0 ? 'text-green-500' : 'text-gray-500'" />
              <span :class="server.players > 0 ? 'text-green-500 font-bold' : ''">
                {{ server.players }}/{{ server.max_players }}
              </span>
              <div class="player-bar">
                <div
                  class="player-fill"
                  :style="{ width: `${(server.players / server.max_players) * 100}%` }"
                ></div>
              </div>
            </div>

            <!-- Ping -->
            <div class="detail-item">
              <Wifi class="w-4 h-4" :class="getPingClass(server.ping)" />
              <span :class="getPingClass(server.ping)">{{ server.ping }}ms</span>
            </div>

            <!-- Country -->
            <div v-if="server.country" class="detail-item">
              <Flag class="w-4 h-4 text-gray-500" />
              <span>{{ server.country }}</span>
            </div>
          </div>

          <!-- Server Footer -->
          <div class="server-footer">
            <n-button
              size="small"
              type="primary"
              class="connect-btn muzzle-flash-hover recoil-click"
              @click.stop="connectToServer(server)"
            >
              <Gamepad2 class="w-4 h-4 mr-1" />
              Baglan
            </n-button>
            <n-button
              size="small"
              quaternary
              @click.stop="copyAddress(server.address)"
            >
              <Copy class="w-4 h-4" />
            </n-button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <GameIcon name="cs-crosshair" size="2xl" color="#64748b" />
        </div>
        <h3>Sunucu Bulunamadi</h3>
        <p>Arama kriterlerinize uygun sunucu yok.</p>
        <n-button type="primary" @click="resetFilters">
          Filtreleri Temizle
        </n-button>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total_pages > 1" class="pagination-wrapper mt-6">
        <n-pagination
          v-model:page="currentPage"
          :page-count="pagination.total_pages"
          :page-slot="5"
          show-quick-jumper
        />
      </div>
    </div>

    <!-- Server Detail Modal -->
    <n-modal v-model:show="showModal" preset="card" :title="selectedServer?.name" class="server-modal">
      <div v-if="selectedServer" class="server-detail">
        <!-- Live Query -->
        <div v-if="queryLoading" class="query-loading">
          <n-spin size="small" />
          <span>Canli sorgu yapiliyor...</span>
        </div>

        <div class="detail-grid">
          <div class="detail-section">
            <h4>Sunucu Bilgileri</h4>
            <div class="info-row">
              <span class="label">IP:Port</span>
              <span class="value">{{ selectedServer.address }}</span>
            </div>
            <div class="info-row">
              <span class="label">Oyun</span>
              <span class="value">{{ getGameLabel(selectedServer.game_type) }}</span>
            </div>
            <div class="info-row">
              <span class="label">Harita</span>
              <span class="value">{{ selectedServer.current_map }}</span>
            </div>
            <div class="info-row">
              <span class="label">Oyuncular</span>
              <span class="value">{{ selectedServer.players }}/{{ selectedServer.max_players }}</span>
            </div>
            <div class="info-row">
              <span class="label">Ping</span>
              <span class="value" :class="getPingClass(selectedServer.ping)">{{ selectedServer.ping }}ms</span>
            </div>
          </div>

          <!-- Player List -->
          <div v-if="selectedServer.player_list?.length > 0" class="detail-section">
            <h4>Oyuncular ({{ selectedServer.player_list.length }})</h4>
            <div class="player-list">
              <div v-for="(player, idx) in selectedServer.player_list" :key="idx" class="player-row">
                <span class="player-name">{{ player.name || 'Connecting...' }}</span>
                <span class="player-score">{{ player.score }} puan</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <n-button type="primary" size="large" @click="connectToServer(selectedServer)" class="muzzle-flash-hover">
            <Gamepad2 class="w-5 h-5 mr-2" />
            Sunucuya Baglan
          </n-button>
          <n-button @click="copyAddress(selectedServer.address)">
            <Copy class="w-4 h-4 mr-2" />
            IP Kopyala
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- Submit Server Modal -->
    <n-modal
      v-model:show="showSubmitModal"
      preset="card"
      title="Sunucu Ekle"
      :style="{ maxWidth: '480px' }"
      class="submit-modal"
    >
      <div class="submit-form">
        <p class="form-desc mb-4">
          Kendi sunucunuzu topluluk listesine ekleyin. Sunucunuzun online oldugunu ve Steam hesabinizin bagli oldugunu kontrol edin.
        </p>

        <n-form ref="submitFormRef" :model="submitForm" :rules="submitRules">
          <n-form-item label="IP Adresi" path="ip">
            <n-input
              v-model:value="submitForm.ip"
              placeholder="192.168.1.1"
              :disabled="submitting"
            />
          </n-form-item>

          <n-form-item label="Port" path="port">
            <n-input-number
              v-model:value="submitForm.port"
              :min="1"
              :max="65535"
              placeholder="27015"
              style="width: 100%"
              :disabled="submitting"
            />
          </n-form-item>

          <n-form-item label="Sunucu Adi (Opsiyonel)" path="name">
            <n-input
              v-model:value="submitForm.name"
              placeholder="Sunucu adi (bos birakirsaniz otomatik alinir)"
              :disabled="submitting"
              :maxlength="200"
              show-count
            />
          </n-form-item>

          <n-form-item label="Aciklama (Opsiyonel)" path="description">
            <n-input
              v-model:value="submitForm.description"
              type="textarea"
              placeholder="Sunucu hakkinda kisa aciklama..."
              :disabled="submitting"
              :maxlength="500"
              show-count
              :rows="3"
            />
          </n-form-item>
        </n-form>

        <div class="submit-actions">
          <n-button
            type="primary"
            @click="submitServer"
            :loading="submitting"
            :disabled="!submitForm.ip"
          >
            <Plus class="w-4 h-4 mr-1" />
            Sunucu Ekle
          </n-button>
          <n-button quaternary @click="showSubmitModal = false" :disabled="submitting">
            Vazgec
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- Delete Confirmation Modal -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="Sunucuyu Sil"
      type="warning"
      positive-text="Sil"
      negative-text="Vazgec"
      @positive-click="deleteServer"
      @negative-click="showDeleteModal = false"
    >
      <p>
        <strong>{{ serverToDelete?.name }}</strong> sunucusunu silmek istediginizden emin misiniz?
        Bu islem geri alinamaz.
      </p>
    </n-modal>

    <!-- Steam Required Modal -->
    <SteamRequiredModal
      :show="showSteamModal"
      @close="closeSteamModal"
      @connect="connectSteam"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  RefreshCw, Search, Map, Users, Wifi, Flag,
  Gamepad2, Copy, Star, Plus, User, Trash2, Lock
} from 'lucide-vue-next'
import GameIcon from '@/components/game/GameIcon.vue'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import { useGameEffects } from '@/composables/useGameEffects'
import { useRequireSteam } from '@/composables/useRequireSteam'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const message = useMessage()
const gameEffects = useGameEffects()
const authStore = useAuthStore()
const {
  hasSteam,
  showSteamModal,
  requireSteam,
  connectSteam,
  closeModal: closeSteamModal
} = useRequireSteam()

// Auth state
const isLoggedIn = computed(() => !!authStore.user)

// State
const loading = ref(false)
const queryLoading = ref(false)
const servers = ref([])
const stats = ref({ online_servers: 0, total_players: 0, by_game_type: {} })
const currentPage = ref(1)
const pagination = ref({ total: 0, total_pages: 1 })
const showModal = ref(false)
const selectedServer = ref(null)

// My Servers State
const myServers = ref([])
const myServersLoading = ref(false)

// Submit Server State
const showSubmitModal = ref(false)
const submitting = ref(false)
const submitFormRef = ref(null)
const submitForm = ref({
  ip: '',
  port: 27015,
  name: '',
  description: ''
})

const submitRules = {
  ip: [
    { required: true, message: 'IP adresi gerekli', trigger: 'blur' },
    {
      pattern: /^(\d{1,3}\.){3}\d{1,3}$/,
      message: 'Gecerli bir IP adresi girin (ornek: 192.168.1.1)',
      trigger: 'blur'
    }
  ],
  port: [
    { required: true, message: 'Port gerekli', trigger: 'blur' },
    { type: 'number', min: 1, max: 65535, message: 'Port 1-65535 arasinda olmali', trigger: 'blur' }
  ]
}

// Delete Server State
const showDeleteModal = ref(false)
const serverToDelete = ref(null)

// Filters
const searchQuery = ref('')
const selectedGame = ref(null)
const sortBy = ref('players')
const filters = ref({
  country: null,
  hasPlayers: false
})

// Game types config
const gameTypes = [
  { value: null, label: 'Tumu', icon: 'cs-crosshair', color: '#f97316' },
  { value: 'ag', label: 'AG', icon: 'ag', color: '#f97316' },
  { value: 'cs16', label: 'CS 1.6', icon: 'cs16', color: '#22c55e' },
  { value: 'hldm', label: 'HLDM', icon: 'hldm', color: '#8b5cf6' }
]

const countryOptions = [
  { label: 'Turkiye', value: 'TR' },
  { label: 'Almanya', value: 'DE' },
  { label: 'ABD', value: 'US' },
  { label: 'Rusya', value: 'RU' }
]

const sortOptions = [
  { label: 'Oyuncu (Cok-Az)', value: 'players' },
  { label: 'Ping (Dusuk-Yuksek)', value: 'ping' },
  { label: 'Isim (A-Z)', value: 'name' }
]

// Computed
const filteredServers = computed(() => {
  let result = [...servers.value]

  // Game type filter
  if (selectedGame.value) {
    result = result.filter(s => s.game_type === selectedGame.value)
  }

  // Search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      s.name?.toLowerCase().includes(query) ||
      s.address?.toLowerCase().includes(query) ||
      s.current_map?.toLowerCase().includes(query)
    )
  }

  // Has players
  if (filters.value.hasPlayers) {
    result = result.filter(s => s.players > 0)
  }

  // Country
  if (filters.value.country) {
    result = result.filter(s => s.country === filters.value.country)
  }

  return result
})

// Methods
const fetchServers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: 50,
      sort_by: sortBy.value,
      online_only: true
    }

    if (selectedGame.value) params.game_type = selectedGame.value
    if (filters.value.hasPlayers) params.has_players = true
    if (filters.value.country) params.country = filters.value.country
    if (searchQuery.value) params.search = searchQuery.value

    const response = await api.get('/community/servers', params)
    servers.value = response.servers || response.data?.servers || []
    pagination.value = response.pagination || response.data?.pagination || { total: 0, total_pages: 1 }
  } catch (error) {
    console.error('Failed to fetch servers:', error)
    servers.value = []
    pagination.value = { total: 0, total_pages: 1 }
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await api.get('/community/servers/stats')
    stats.value = response || { online_servers: 0, total_players: 0, by_game_type: {} }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    stats.value = { online_servers: 0, total_players: 0, by_game_type: {} }
  }
}

const fetchMyServers = async () => {
  if (!isLoggedIn.value) return

  myServersLoading.value = true
  try {
    const response = await api.get('/community/community-servers/my')
    myServers.value = response.servers || []
  } catch (error) {
    console.error('Failed to fetch my servers:', error)
    myServers.value = []
  } finally {
    myServersLoading.value = false
  }
}

const refreshData = async () => {
  await Promise.all([fetchServers(), fetchStats()])
  if (isLoggedIn.value) {
    await fetchMyServers()
  }
  message.success('Veriler guncellendi')
}

const showServerDetail = async (server) => {
  selectedServer.value = { ...server }
  showModal.value = true

  // Live query
  queryLoading.value = true
  try {
    const response = await api.get(`/community/servers/${server.id}`)
    selectedServer.value = response || server
  } catch (error) {
    console.error('Live query failed:', error)
  } finally {
    queryLoading.value = false
  }
}

const connectToServer = (server) => {
  const protocol = server.game_type === 'cs16' ? 'steam://connect/' : 'hl://'
  window.location.href = `${protocol}${server.address}`

  gameEffects.showAchievement({
    title: 'Sunucuya Baglaniliyor',
    description: server.name,
    gameIcon: getGameIcon(server.game_type),
    color: getGameColor(server.game_type)
  })
}

const copyAddress = (address) => {
  navigator.clipboard.writeText(address)
  message.success('IP adresi kopyalandi')
  gameEffects.showXP(10, { type: 'default', label: '' })
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedGame.value = null
  filters.value = { country: null, hasPlayers: false }
  fetchServers()
}

const getGameCount = (gameType) => {
  if (!gameType) return stats.value.online_servers || 0
  return stats.value.by_game_type?.[gameType]?.servers || 0
}

const getGameIcon = (gameType) => {
  const icons = { ag: 'ag', cs16: 'cs16', hldm: 'hldm' }
  return icons[gameType] || 'cs-crosshair'
}

const getGameColor = (gameType) => {
  const colors = { ag: '#f97316', cs16: '#22c55e', hldm: '#8b5cf6' }
  return colors[gameType] || '#f97316'
}

const getGameLabel = (gameType) => {
  const labels = { ag: 'Adrenaline Gamer', cs16: 'Counter-Strike 1.6', hldm: 'Half-Life Deathmatch' }
  return labels[gameType] || gameType
}

const getPingClass = (ping) => {
  if (ping < 50) return 'text-green-500'
  if (ping < 100) return 'text-yellow-500'
  return 'text-red-500'
}

// Submit Server Methods
const openSubmitModal = () => {
  requireSteam(() => {
    submitForm.value = { ip: '', port: 27015, name: '', description: '' }
    showSubmitModal.value = true
  })
}

const submitServer = async () => {
  try {
    await submitFormRef.value?.validate()
  } catch (errors) {
    return
  }

  submitting.value = true
  try {
    const response = await api.post('/community/community-servers/submit', {
      ip: submitForm.value.ip,
      port: submitForm.value.port,
      name: submitForm.value.name || null,
      description: submitForm.value.description || null
    })

    message.success(response.message || 'Sunucu basariyla eklendi!')
    showSubmitModal.value = false

    // Refresh data
    await Promise.all([fetchServers(), fetchStats(), fetchMyServers()])

    gameEffects.showAchievement({
      title: 'Sunucu Eklendi!',
      description: response.server?.name || submitForm.value.ip,
      gameIcon: 'server-pulse',
      color: '#22c55e'
    })
  } catch (error) {
    console.error('Failed to submit server:', error)
    message.error(error.message || 'Sunucu eklenirken bir hata olustu')
  } finally {
    submitting.value = false
  }
}

// Delete Server Methods
const confirmDeleteServer = (server) => {
  serverToDelete.value = server
  showDeleteModal.value = true
}

const deleteServer = async () => {
  if (!serverToDelete.value) return

  try {
    await api.delete(`/community/community-servers/${serverToDelete.value.id}`)
    message.success('Sunucu silindi')
    showDeleteModal.value = false
    serverToDelete.value = null
    await fetchMyServers()
  } catch (error) {
    console.error('Failed to delete server:', error)
    message.error(error.message || 'Sunucu silinirken bir hata olustu')
  }
}

// Refresh single server status
const refreshServerStatus = async (server) => {
  try {
    const response = await api.post(`/community/community-servers/${server.id}/refresh`)
    const idx = myServers.value.findIndex(s => s.id === server.id)
    if (idx !== -1) {
      myServers.value[idx] = {
        ...myServers.value[idx],
        is_online: response.is_online,
        players: response.players || 0,
        max_players: response.max_players || myServers.value[idx].max_players,
        current_map: response.current_map || myServers.value[idx].current_map,
        ping: response.ping || myServers.value[idx].ping
      }
    }
    message.success(response.is_online ? 'Sunucu online' : 'Sunucu offline')
  } catch (error) {
    console.error('Failed to refresh server status:', error)
    message.error('Sunucu durumu alinamadi')
  }
}

// Periodic refresh for status indicators
let statusRefreshInterval = null

const startStatusRefresh = () => {
  statusRefreshInterval = setInterval(async () => {
    if (myServers.value.length > 0) {
      for (const server of myServers.value) {
        try {
          const response = await api.post(`/community/community-servers/${server.id}/refresh`)
          const idx = myServers.value.findIndex(s => s.id === server.id)
          if (idx !== -1) {
            myServers.value[idx].is_online = response.is_online
            myServers.value[idx].players = response.players || 0
          }
        } catch (error) {
          // Silent fail for background refresh
        }
      }
    }
  }, 60000) // Refresh every 60 seconds
}

// Watchers
watch([selectedGame, sortBy, currentPage], () => {
  fetchServers()
})

watch([() => filters.value.hasPlayers, () => filters.value.country], () => {
  currentPage.value = 1
  fetchServers()
})

// Debounced search
let searchTimeout
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchServers()
  }, 300)
})

// Watch for login state changes
watch(isLoggedIn, (newVal) => {
  if (newVal) {
    fetchMyServers()
    startStatusRefresh()
  } else {
    myServers.value = []
    if (statusRefreshInterval) {
      clearInterval(statusRefreshInterval)
    }
  }
})

// Lifecycle
onMounted(() => {
  fetchServers()
  fetchStats()
  if (isLoggedIn.value) {
    fetchMyServers()
    startStatusRefresh()
  }
})

onUnmounted(() => {
  if (statusRefreshInterval) {
    clearInterval(statusRefreshInterval)
  }
})
</script>

<style scoped>
.community-servers-page {
  position: relative;
  min-height: 100vh;
  padding-bottom: 4rem;
}

.page-background {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.4) 0%, transparent 70%);
  top: -200px;
  right: -200px;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
  bottom: 10%;
  left: -100px;
}

.floating-weapons {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.weapon-1 { position: absolute; top: 15%; right: 10%; animation-delay: 0s; }
.weapon-2 { position: absolute; top: 60%; left: 5%; animation-delay: 1s; }
.weapon-3 { position: absolute; bottom: 20%; right: 15%; animation-delay: 2s; }

/* Header */
.icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(234, 88, 12, 0.1) 100%);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 12px;
}

.stat-mini {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.add-server-btn {
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
}

.add-server-btn.btn-disabled {
  background: linear-gradient(135deg, #4b5563, #374151);
  cursor: not-allowed;
  opacity: 0.8;
}

/* My Servers Section */
.my-servers-section {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.my-servers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.my-server-card {
  padding: 12px;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.my-server-card:hover {
  border-color: rgba(249, 115, 22, 0.3);
}

.my-server-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.game-badge-sm {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
}

.my-server-info {
  flex: 1;
  min-width: 0;
}

.my-server-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.my-server-address {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: 'JetBrains Mono', monospace;
}

.my-server-status-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
  animation: pulse-green 2s infinite;
}

.status-indicator.offline {
  background: #ef4444;
}

@keyframes pulse-green {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.player-count {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.my-server-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid var(--border-light);
}

/* Game Tabs */
.game-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.game-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
  font-weight: 500;
}

.game-tab:hover {
  border-color: rgba(249, 115, 22, 0.3);
  background: rgba(249, 115, 22, 0.05);
}

.game-tab.active {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.game-tab .count {
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.game-tab.active .count {
  color: #fff;
}

/* Filters */
.filters-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input {
  width: 280px;
}

.filter-select {
  width: 140px;
}

.sort-select {
  width: 180px;
}

/* Server Grid */
.servers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.server-card {
  position: relative;
  padding: 16px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.server-card:hover {
  transform: translateY(-4px);
  border-color: rgba(249, 115, 22, 0.4);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.server-card.featured {
  border-color: rgba(249, 115, 22, 0.5);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.08) 0%, var(--glass-bg) 100%);
}

.featured-badge {
  position: absolute;
  top: -8px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--gradient-primary);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
}

/* Server Header */
.server-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.game-badge {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
}

.server-info {
  flex: 1;
  min-width: 0;
}

.server-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.server-address {
  font-size: 12px;
  color: var(--text-tertiary);
  font-family: 'JetBrains Mono', monospace;
}

.server-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.server-status.online {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.server-status.offline {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Server Details */
.server-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.detail-item.players {
  grid-column: span 2;
}

.player-bar {
  flex: 1;
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
  margin-left: 8px;
}

.player-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #16a34a);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* Server Footer */
.server-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.connect-btn {
  flex: 1;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-color);
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 50%;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

/* Modal */
.server-detail {
  padding: 8px 0;
}

.query-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #3b82f6;
}

.detail-grid {
  display: grid;
  gap: 20px;
  margin-bottom: 20px;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-light);
}

.info-row .label {
  color: var(--text-secondary);
}

.info-row .value {
  font-weight: 500;
  color: var(--text-primary);
}

.player-list {
  max-height: 200px;
  overflow-y: auto;
}

.player-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  margin-bottom: 4px;
  font-size: 13px;
}

.player-name {
  color: var(--text-primary);
}

.player-score {
  color: #22c55e;
  font-weight: 500;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

/* Submit Modal */
.submit-form {
  padding: 4px 0;
}

.form-desc {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.submit-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: center;
}

/* Responsive */
@media (max-width: 768px) {
  .servers-grid {
    grid-template-columns: 1fr;
  }

  .my-servers-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input,
  .filter-select,
  .sort-select {
    width: 100%;
  }

  .game-tabs {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 8px;
  }
}
</style>
