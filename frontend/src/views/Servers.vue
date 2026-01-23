<template>
  <div class="servers-page">
    <!-- Maintenance Check -->
    <MaintenanceOverlay feature="server_rental" />

    <!-- Subtle Background -->
    <div class="page-background">
      <div class="glow-orb orb-1"></div>
    </div>

    <div class="container-main py-3 relative z-10">
      <!-- Compact Header -->
      <header class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
        <div class="flex items-center gap-4">
          <h1 class="text-lg font-bold flex items-center gap-2">
            <n-icon :component="Server" size="20" class="text-orange-500" />
            Sunucular
          </h1>
          <div class="flex items-center gap-3 text-xs text-gray-400">
            <span>{{ servers.length }} sunucu</span>
            <span class="text-green-500">{{ activeServersCount }} aktif</span>
            <span class="text-blue-500">{{ totalPlayersCount }} oyuncu</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <n-switch v-model:value="autoRefresh" size="small" aria-label="Otomatik yenilemeyi aç/kapat" />
          <n-button quaternary circle size="small" @click="refreshServers" :loading="loading" aria-label="Sunucuları yenile">
            <template #icon>
              <n-icon :component="RefreshCw" size="16" :class="{ 'spin-animation': loading }" />
            </template>
          </n-button>
        </div>
      </header>


      <!-- Filters Section -->
      <section class="filters-section">
        <!-- Search Bar -->
        <div class="search-container">
          <n-input
            v-model:value="searchQuery"
            placeholder="Sunucu ara (isim, IP, harita...)"
            clearable
            size="large"
            class="search-input"
            aria-label="Sunucu arama"
          >
            <template #prefix>
              <n-icon :component="Search" />
            </template>
          </n-input>
        </div>

        <!-- Filter Controls -->
        <div class="filter-controls">
          <!-- Game Type Filter -->
          <div class="filter-group">
            <label class="filter-label">Oyun Tipi</label>
            <n-select
              v-model:value="filters.gameType"
              :options="gameTypeOptions"
              placeholder="Tüm Modlar"
              clearable
              size="small"
              class="filter-select"
              aria-label="Oyun tipi filtresi"
            />
          </div>

          <!-- Map Filter -->
          <div class="filter-group">
            <label class="filter-label">Harita</label>
            <n-select
              v-model:value="filters.map"
              :options="mapOptions"
              placeholder="Tüm Haritalar"
              clearable
              filterable
              size="small"
              class="filter-select"
              aria-label="Harita filtresi"
            />
          </div>

          <!-- Player Count Filter -->
          <div class="filter-group">
            <label class="filter-label">Oyuncu Sayısı</label>
            <n-select
              v-model:value="filters.playerCount"
              :options="playerCountOptions"
              placeholder="Tüm Sunucular"
              clearable
              size="small"
              class="filter-select"
              aria-label="Oyuncu sayısı filtresi"
            />
          </div>

          <!-- Region Filter -->
          <div class="filter-group">
            <label class="filter-label">Bölge</label>
            <n-select
              v-model:value="filters.region"
              :options="regionOptions"
              placeholder="Tüm Bölgeler"
              clearable
              size="small"
              class="filter-select"
              aria-label="Bölge filtresi"
            />
          </div>

          <!-- Status Filter -->
          <div class="filter-group">
            <label class="filter-label">Durum</label>
            <n-button-group size="small" role="group" aria-label="Durum filtresi">
              <n-button
                :type="filters.status === 'all' ? 'primary' : 'default'"
                @click="filters.status = 'all'"
                aria-label="Tüm sunucuları göster"
              >
                Tümü
              </n-button>
              <n-button
                :type="filters.status === 'running' ? 'success' : 'default'"
                @click="filters.status = 'running'"
                aria-label="Aktif sunucuları göster"
              >
                <template #icon><n-icon :component="Circle" class="pulse-green" /></template>
                Aktif
              </n-button>
              <n-button
                :type="filters.status === 'stopped' ? 'error' : 'default'"
                @click="filters.status = 'stopped'"
                aria-label="Pasif sunucuları göster"
              >
                <template #icon><n-icon :component="Circle" /></template>
                Pasif
              </n-button>
            </n-button-group>
          </div>
        </div>

        <!-- Sort and View Controls -->
        <div class="sort-view-controls">
          <div class="sort-controls">
            <span class="sort-label">Sırala:</span>
            <n-button-group size="small">
              <n-button
                v-for="option in sortOptions"
                :key="option.value"
                :type="sortBy === option.value ? 'primary' : 'default'"
                @click="toggleSort(option.value)"
              >
                <template #icon>
                  <n-icon :component="sortBy === option.value ? (sortOrder === 'asc' ? ArrowUp : ArrowDown) : option.icon" />
                </template>
                {{ option.label }}
              </n-button>
            </n-button-group>
          </div>

          <div class="view-toggle">
            <n-button-group size="small" role="group" aria-label="Görünüm seçenekleri">
              <n-button
                :type="viewMode === 'grid' ? 'primary' : 'default'"
                @click="viewMode = 'grid'"
                aria-label="Izgara görünümü"
              >
                <template #icon><n-icon :component="Grid" /></template>
              </n-button>
              <n-button
                :type="viewMode === 'list' ? 'primary' : 'default'"
                @click="viewMode = 'list'"
                aria-label="Liste görünümü"
              >
                <template #icon><n-icon :component="List" /></template>
              </n-button>
            </n-button-group>
          </div>
        </div>

        <!-- Active Filters Tags -->
        <div v-if="hasActiveFilters" class="active-filters">
          <span class="active-filters-label">Aktif Filtreler:</span>
          <n-tag
            v-if="searchQuery"
            closable
            @close="searchQuery = ''"
            size="small"
            type="warning"
          >
            Arama: "{{ searchQuery }}"
          </n-tag>
          <n-tag
            v-if="filters.gameType"
            closable
            @close="filters.gameType = null"
            size="small"
            type="info"
          >
            {{ getGameTypeLabel(filters.gameType) }}
          </n-tag>
          <n-tag
            v-if="filters.map"
            closable
            @close="filters.map = null"
            size="small"
            type="success"
          >
            {{ filters.map }}
          </n-tag>
          <n-tag
            v-if="filters.playerCount"
            closable
            @close="filters.playerCount = null"
            size="small"
            type="primary"
          >
            {{ getPlayerCountLabel(filters.playerCount) }}
          </n-tag>
          <n-tag
            v-if="filters.region"
            closable
            @close="filters.region = null"
            size="small"
          >
            {{ getRegionLabel(filters.region) }}
          </n-tag>
          <n-button text size="small" type="warning" @click="clearAllFilters">
            Tümünü Temizle
          </n-button>
        </div>
      </section>

      <!-- Results Info -->
      <div class="results-info">
        <span class="results-count">
          <strong>{{ filteredServers.length }}</strong> sunucu bulundu
        </span>
        <span class="results-page" v-if="!useInfiniteScroll">
          Sayfa {{ currentPage }} / {{ totalPages }}
        </span>
      </div>

      <!-- Loading State -->
      <div v-if="loading && servers.length === 0" class="loading-grid" :class="viewMode">
        <div v-for="i in 8" :key="i" class="skeleton-card">
          <div class="skeleton-thumbnail"></div>
          <div class="skeleton-content">
            <div class="skeleton-line title"></div>
            <div class="skeleton-line subtitle"></div>
            <div class="skeleton-line bar"></div>
            <div class="skeleton-actions">
              <div class="skeleton-btn"></div>
              <div class="skeleton-btn small"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Server Grid/List -->
      <TransitionGroup
        v-else-if="paginatedServers.length > 0"
        :name="viewMode === 'grid' ? 'grid' : 'list'"
        tag="div"
        :class="['servers-container', viewMode]"
      >
        <div
          v-for="server in paginatedServers"
          :key="server.id"
          :class="['server-card', viewMode, { 'is-favorite': favorites.has(server.id) }]"
        >
          <!-- Map Thumbnail -->
          <div class="map-thumbnail">
            <img
              :src="getMapThumbnail(server.current_map)"
              :alt="server.current_map"
              @error="handleImageError"
            />
            <div class="thumbnail-overlay">
              <span class="map-name">{{ server.current_map || 'de_dust2' }}</span>
            </div>
            <!-- Live Status Indicator -->
            <div :class="['status-indicator', server.status, { 'server-online-pulse': server.status === 'running' }]">
              <span class="status-dot"></span>
              <span class="status-text">{{ server.status === 'running' ? 'CANLI' : 'KAPALI' }}</span>
            </div>
            <!-- Favorite Toggle -->
            <n-tooltip v-if="!isLoggedIn" trigger="hover">
              <template #trigger>
                <button
                  class="favorite-btn disabled"
                  @click.stop="toggleFavorite(server.id)"
                  aria-label="Favorilere ekle (giriş gerekli)"
                >
                  <n-icon :component="Heart" />
                </button>
              </template>
              Giriş yaparak favorilere ekleyebilirsiniz
            </n-tooltip>
            <button
              v-else
              :class="['favorite-btn', { active: favorites.has(server.id) }]"
              @click.stop="toggleFavorite(server.id)"
              :aria-label="favorites.has(server.id) ? 'Favorilerden kaldır' : 'Favorilere ekle'"
            >
              <n-icon :component="favorites.has(server.id) ? HeartFilled : Heart" />
            </button>
          </div>

          <!-- Server Info -->
          <div class="server-info">
            <div class="server-header">
              <h3 class="server-name">{{ server.name }}</h3>
              <n-tag :type="getGameModeType(server.game_mode)" size="small" round>
                {{ server.game_mode || 'Classic' }}
              </n-tag>
            </div>

            <div class="server-address">
              <n-icon :component="Globe" size="14" />
              <span>{{ server.ip }}:{{ server.port }}</span>
              <n-button text size="tiny" @click="copyAddress(server)" aria-label="Adresi kopyala">
                <n-icon :component="Copy" />
              </n-button>
            </div>

            <!-- Player Count Bar -->
            <div class="player-section">
              <div class="player-info">
                <n-icon :component="Users" size="16" />
                <span class="player-count">
                  <strong>{{ server.current_players || 0 }}</strong>
                  <span class="separator">/</span>
                  <span>{{ server.max_players || 32 }}</span>
                </span>
              </div>
              <div class="player-bar">
                <div
                  class="player-bar-fill player-bar-animated"
                  :style="{ width: `${getPlayerPercentage(server)}%` }"
                  :class="getPlayerBarClass(server)"
                ></div>
              </div>
            </div>

            <!-- Server Stats -->
            <div class="server-stats">
              <div class="stat" v-if="server.ping">
                <n-icon :component="Wifi" size="14" />
                <span :class="getPingClass(server.ping)">{{ server.ping }}ms</span>
              </div>
              <div class="stat" v-if="server.region">
                <n-icon :component="MapPin" size="14" />
                <span>{{ server.region }}</span>
              </div>
              <div class="stat" v-if="server.version">
                <n-icon :component="Tag" size="14" />
                <span>{{ server.version }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="server-actions">
              <n-button
                type="primary"
                size="small"
                class="connect-btn muzzle-flash-hover recoil-click"
                @click="quickConnect(server)"
                aria-label="Sunucuya hızlı bağlan"
              >
                <template #icon><n-icon :component="Zap" /></template>
                Hızlı Bağlan
              </n-button>
              <router-link :to="`/servers/${server.id}`" :aria-label="`${server.name} sunucu detayları`">
                <n-button size="small" quaternary aria-label="Sunucu ayarları">
                  <template #icon><n-icon :component="Settings" /></template>
                </n-button>
              </router-link>
              <n-dropdown :options="serverMenuOptions" @select="(key) => handleServerAction(key, server)">
                <n-button size="small" quaternary aria-label="Daha fazla seçenek">
                  <template #icon><n-icon :component="MoreVertical" /></template>
                </n-button>
              </n-dropdown>
            </div>
          </div>
        </div>
      </TransitionGroup>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <n-icon :component="SearchX" size="80" />
        </div>
        <h3>Sunucu Bulunamadı</h3>
        <p v-if="hasActiveFilters">Arama kriterlerinize uygun sunucu bulunamadı. Filtreleri değiştirmeyi deneyin.</p>
        <p v-else>Henüz aktif sunucu bulunmuyor.</p>
        <n-button v-if="hasActiveFilters" type="primary" @click="clearAllFilters">
          Filtreleri Temizle
        </n-button>
      </div>

      <!-- Pagination / Infinite Scroll -->
      <div class="pagination-section" v-if="filteredServers.length > 0">
        <n-switch v-model:value="useInfiniteScroll" size="small" aria-label="Sonsuz scroll ve sayfalama arasında geçiş yap">
          <template #checked>Sonsuz Scroll</template>
          <template #unchecked>Sayfalama</template>
        </n-switch>

        <n-pagination
          v-if="!useInfiniteScroll"
          v-model:page="currentPage"
          :page-count="totalPages"
          :page-slot="5"
          show-quick-jumper
        />

        <div v-else-if="hasMorePages" class="load-more">
          <n-button
            @click="loadMore"
            :loading="loadingMore"
            type="primary"
            ghost
          >
            Daha Fazla Yükle ({{ remainingCount }} kaldı)
          </n-button>
        </div>
      </div>
    </div>

    <!-- Quick Connect Modal -->
    <n-modal v-model:show="showConnectModal" preset="card" style="width: 400px" title="Sunucuya Bağlan">
      <div class="connect-modal-content" v-if="selectedServer">
        <div class="connect-server-info">
          <div class="connect-map-img">
            <img :src="getMapThumbnail(selectedServer.current_map)" :alt="selectedServer.current_map" />
          </div>
          <div>
            <h4>{{ selectedServer.name }}</h4>
            <p>{{ selectedServer.ip }}:{{ selectedServer.port }}</p>
          </div>
        </div>
        <n-input
          v-model:value="connectPassword"
          type="password"
          placeholder="Sunucu şifresi (opsiyonel)"
          show-password-on="click"
        />
        <div class="connect-actions">
          <n-button @click="showConnectModal = false">İptal</n-button>
          <n-button type="primary" @click="confirmConnect">
            <template #icon><n-icon :component="Zap" /></template>
            Bağlan
          </n-button>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, h } from 'vue'
import { useMessage } from 'naive-ui'
import MaintenanceOverlay from '@/components/MaintenanceOverlay.vue'
import { useRequireAuth } from '@/composables/useRequireAuth'
import { useAuthStore } from '@/stores/auth'
import {
  Server,
  Activity,
  Users,
  Search,
  RefreshCw,
  Grid,
  List,
  ArrowUp,
  ArrowDown,
  Heart,
  Globe,
  Copy,
  Wifi,
  MapPin,
  Tag,
  Zap,
  Settings,
  MoreVertical,
  Circle,
  Play,
  Square,
  RotateCw,
  ExternalLink,
  Trash2
} from 'lucide-vue-next'
import { serversAPI } from '@/api'

// Custom icon components
const HeartFilled = {
  render() {
    return h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      width: '24',
      height: '24',
      viewBox: '0 0 24 24',
      fill: 'currentColor',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round'
    }, [
      h('path', { d: 'M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z' })
    ])
  }
}

const SearchX = {
  render() {
    return h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      width: '24',
      height: '24',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round'
    }, [
      h('path', { d: 'm13.5 8.5-5 5' }),
      h('path', { d: 'm8.5 8.5 5 5' }),
      h('circle', { cx: '11', cy: '11', r: '8' }),
      h('path', { d: 'm21 21-4.3-4.3' })
    ])
  }
}

import { useRouter } from 'vue-router'

const router = useRouter()

const message = useMessage()
const authStore = useAuthStore()
const { isLoggedIn, requireAuth } = useRequireAuth()

// State
const servers = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const searchQuery = ref('')
const viewMode = ref('grid')
const sortBy = ref('players')
const sortOrder = ref('desc')
const currentPage = ref(1)
const pageSize = ref(12)
const useInfiniteScroll = ref(false)
const infiniteScrollPage = ref(1)
const favorites = ref(new Set((() => {
  try {
    return JSON.parse(localStorage.getItem('serverFavorites') || '[]')
  } catch (e) {
    console.error('Failed to parse serverFavorites from localStorage:', e)
    return []
  }
})()))
const autoRefresh = ref(true)
const refreshInterval = ref(30)
const refreshCountdown = ref(30)
const showConnectModal = ref(false)
const selectedServer = ref(null)
const connectPassword = ref('')

// Filters
const filters = ref({
  gameType: null,
  map: null,
  playerCount: null,
  region: null,
  status: 'all'
})

// Filter Options
const gameTypeOptions = [
  { label: 'Classic', value: 'classic' },
  { label: 'Deathmatch', value: 'deathmatch' },
  { label: 'Gun Game', value: 'gungame' },
  { label: 'Zombie', value: 'zombie' },
  { label: 'Jail Break', value: 'jailbreak' },
  { label: 'Surf', value: 'surf' },
  { label: 'KZ (Kreedz)', value: 'kz' },
  { label: 'Public', value: 'public' }
]

const mapOptions = computed(() => {
  const maps = new Set(servers.value.map(s => s.current_map).filter(Boolean))
  return Array.from(maps).sort().map(m => ({ label: m, value: m }))
})

const playerCountOptions = [
  { label: 'Boş', value: 'empty' },
  { label: '1-10 Oyuncu', value: '1-10' },
  { label: '11-20 Oyuncu', value: '11-20' },
  { label: '21+ Oyuncu', value: '21+' },
  { label: 'Dolu Değil', value: 'not-full' },
  { label: 'Boş Değil', value: 'not-empty' }
]

const regionOptions = [
  { label: 'Türkiye', value: 'TR' },
  { label: 'Avrupa', value: 'EU' },
  { label: 'Amerika', value: 'US' },
  { label: 'Asya', value: 'AS' },
  { label: 'Rusya', value: 'RU' }
]

const sortOptions = [
  { label: 'Oyuncu', value: 'players', icon: Users },
  { label: 'İsim', value: 'name', icon: Tag },
  { label: 'Ping', value: 'ping', icon: Wifi }
]

const serverMenuOptions = [
  { label: 'Sunucu Detayları', key: 'details', icon: () => h(Settings) },
  { label: 'Adresi Kopyala', key: 'copy', icon: () => h(Copy) },
  { label: 'Steam ile Aç', key: 'steam', icon: () => h(ExternalLink) },
  { type: 'divider', key: 'd1' },
  { label: 'Başlat', key: 'start', icon: () => h(Play) },
  { label: 'Durdur', key: 'stop', icon: () => h(Square) },
  { label: 'Yeniden Başlat', key: 'restart', icon: () => h(RotateCw) }
]

// Computed
const activeServersCount = computed(() => servers.value.filter(s => s.status === 'running').length)
const totalPlayersCount = computed(() => servers.value.reduce((sum, s) => sum + (s.current_players || 0), 0))
const avgPing = computed(() => {
  const serversWithPing = servers.value.filter(s => s.ping)
  if (serversWithPing.length === 0) return 0
  return Math.round(serversWithPing.reduce((sum, s) => sum + s.ping, 0) / serversWithPing.length)
})

const hasActiveFilters = computed(() => {
  return searchQuery.value ||
    filters.value.gameType ||
    filters.value.map ||
    filters.value.playerCount ||
    filters.value.region ||
    filters.value.status !== 'all'
})

const filteredServers = computed(() => {
  let result = [...servers.value]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      s.name?.toLowerCase().includes(query) ||
      s.ip?.toLowerCase().includes(query) ||
      s.current_map?.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (filters.value.status !== 'all') {
    result = result.filter(s => s.status === filters.value.status)
  }

  // Game type filter
  if (filters.value.gameType) {
    result = result.filter(s => s.game_mode?.toLowerCase() === filters.value.gameType)
  }

  // Map filter
  if (filters.value.map) {
    result = result.filter(s => s.current_map === filters.value.map)
  }

  // Player count filter
  if (filters.value.playerCount) {
    result = result.filter(s => {
      const players = s.current_players || 0
      const max = s.max_players || 32
      switch (filters.value.playerCount) {
        case 'empty': return players === 0
        case '1-10': return players >= 1 && players <= 10
        case '11-20': return players >= 11 && players <= 20
        case '21+': return players >= 21
        case 'not-full': return players < max
        case 'not-empty': return players > 0
        default: return true
      }
    })
  }

  // Region filter
  if (filters.value.region) {
    result = result.filter(s => s.region === filters.value.region)
  }

  // Sorting
  result.sort((a, b) => {
    let comparison = 0
    switch (sortBy.value) {
      case 'players':
        comparison = (b.current_players || 0) - (a.current_players || 0)
        break
      case 'name':
        comparison = (a.name || '').localeCompare(b.name || '')
        break
      case 'ping':
        comparison = (a.ping || 999) - (b.ping || 999)
        break
    }
    return sortOrder.value === 'asc' ? -comparison : comparison
  })

  // Favorites first
  result.sort((a, b) => {
    const aFav = favorites.value.has(a.id) ? 1 : 0
    const bFav = favorites.value.has(b.id) ? 1 : 0
    return bFav - aFav
  })

  return result
})

const totalPages = computed(() => Math.ceil(filteredServers.value.length / pageSize.value))
const hasMorePages = computed(() => infiniteScrollPage.value * pageSize.value < filteredServers.value.length)
const remainingCount = computed(() => filteredServers.value.length - (infiniteScrollPage.value * pageSize.value))

const paginatedServers = computed(() => {
  if (useInfiniteScroll.value) {
    return filteredServers.value.slice(0, infiniteScrollPage.value * pageSize.value)
  }
  const start = (currentPage.value - 1) * pageSize.value
  return filteredServers.value.slice(start, start + pageSize.value)
})

// Methods
const refreshServers = async () => {
  loading.value = servers.value.length === 0
  try {
    const data = await serversAPI.getAll()
    servers.value = data.items || []
    refreshCountdown.value = refreshInterval.value
  } catch (err) {
    message.error('Sunucular yüklenemedi')
  } finally {
    loading.value = false
  }
}

const toggleSort = (field) => {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortOrder.value = field === 'ping' ? 'asc' : 'desc'
  }
}

const toggleFavorite = async (serverId) => {
  if (!requireAuth({ message: 'Favorilere eklemek için giriş yapmanız gerekiyor' })) return

  // Toggle local state
  if (favorites.value.has(serverId)) {
    favorites.value.delete(serverId)
  } else {
    favorites.value.add(serverId)
  }

  // Save to localStorage as backup
  localStorage.setItem('serverFavorites', JSON.stringify([...favorites.value]))

  // Optionally sync to backend (if endpoint exists)
  try {
    await fetch('/api/user/favorites/server', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ server_id: serverId })
    })
  } catch (e) {
    // Backend sync failed, localStorage still has data
    console.log('Favorite sync failed:', e)
  }
}

const clearAllFilters = () => {
  searchQuery.value = ''
  filters.value = {
    gameType: null,
    map: null,
    playerCount: null,
    region: null,
    status: 'all'
  }
}

const loadMore = () => {
  loadingMore.value = true
  setTimeout(() => {
    infiniteScrollPage.value++
    loadingMore.value = false
  }, 300)
}

const getMapThumbnail = (mapName) => {
  const map = mapName || 'de_dust2'
  return `/maps/${map}.jpg`
}

const handleImageError = (e) => {
  e.target.src = '/maps/default.jpg'
}

const getPlayerPercentage = (server) => {
  return ((server.current_players || 0) / (server.max_players || 32)) * 100
}

const getPlayerBarClass = (server) => {
  const pct = getPlayerPercentage(server)
  if (pct >= 90) return 'full'
  if (pct >= 60) return 'high'
  if (pct >= 30) return 'medium'
  return 'low'
}

const getPingClass = (ping) => {
  if (ping < 50) return 'ping-good'
  if (ping < 100) return 'ping-medium'
  return 'ping-bad'
}

const getGameModeType = (mode) => {
  const types = {
    classic: 'default',
    deathmatch: 'error',
    gungame: 'warning',
    zombie: 'success',
    jailbreak: 'info',
    surf: 'primary',
    kz: 'primary',
    public: 'default'
  }
  return types[mode?.toLowerCase()] || 'default'
}

const getGameTypeLabel = (value) => gameTypeOptions.find(o => o.value === value)?.label || value
const getPlayerCountLabel = (value) => playerCountOptions.find(o => o.value === value)?.label || value
const getRegionLabel = (value) => regionOptions.find(o => o.value === value)?.label || value

const copyAddress = (server) => {
  navigator.clipboard.writeText(`${server.ip}:${server.port}`)
  message.success('Adres kopyalandı')
}

const quickConnect = (server) => {
  selectedServer.value = server
  connectPassword.value = ''
  showConnectModal.value = true
}

const confirmConnect = () => {
  const server = selectedServer.value
  const password = connectPassword.value ? `;password ${connectPassword.value}` : ''
  window.location.href = `steam://connect/${server.ip}:${server.port}${password}`
  showConnectModal.value = false
  message.info('Steam üzerinden bağlanılıyor...')
}

const handleServerAction = async (key, server) => {
  switch (key) {
    case 'details':
      router.push(`/servers/${server.id}`)
      break
    case 'copy':
      copyAddress(server)
      break
    case 'steam':
      window.location.href = `steam://connect/${server.ip}:${server.port}`
      break
    case 'start':
      try {
        await serversAPI.start(server.id)
        server.status = 'running'
        message.success('Sunucu başlatıldı')
      } catch (err) {
        message.error('Sunucu başlatılamadı')
      }
      break
    case 'stop':
      try {
        await serversAPI.stop(server.id)
        server.status = 'stopped'
        message.success('Sunucu durduruldu')
      } catch (err) {
        message.error('Sunucu durdurulamadı')
      }
      break
    case 'restart':
      try {
        await serversAPI.restart(server.id)
        message.success('Sunucu yeniden başlatıldı')
      } catch (err) {
        message.error('Sunucu yeniden başlatılamadı')
      }
      break
  }
}

// Auto refresh timer
let refreshTimer = null
const startRefreshTimer = () => {
  refreshTimer = setInterval(() => {
    if (autoRefresh.value) {
      refreshCountdown.value--
      if (refreshCountdown.value <= 0) {
        refreshServers()
      }
    }
  }, 1000)
}

// Watch for filter changes to reset pagination
watch([searchQuery, filters], () => {
  currentPage.value = 1
  infiniteScrollPage.value = 1
}, { deep: true })

// Lifecycle
onMounted(async () => {
  // Load from localStorage first
  const stored = localStorage.getItem('serverFavorites')
  if (stored) favorites.value = new Set(JSON.parse(stored))

  // If logged in, sync from backend
  if (authStore.isAuthenticated) {
    try {
      const res = await fetch('/api/user/favorites/servers', {
        headers: { 'Authorization': `Bearer ${authStore.token}` }
      })
      if (res.ok) {
        const data = await res.json()
        favorites.value = new Set(data.server_ids || [])
        localStorage.setItem('serverFavorites', JSON.stringify([...favorites.value]))
      }
    } catch (e) {
      // Backend sync failed, use localStorage data
      console.log('Failed to fetch favorites from backend:', e)
    }
  }

  refreshServers()
  startRefreshTimer()
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
/* Page Background */
.servers-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.page-background {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(249, 115, 22, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(249, 115, 22, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #f97316;
  top: -100px;
  right: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #8b5cf6;
  bottom: -50px;
  left: -50px;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 30px); }
}

/* Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
}

.title-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 30px rgba(249, 115, 22, 0.3);
}

.text-gradient-orange {
  background: linear-gradient(135deg, #f97316, #fb923c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.1rem;
  margin: 0;
}

/* Refresh Controls */
.refresh-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.03);
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.refresh-countdown {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.countdown-text {
  position: absolute;
  font-size: 0.7rem;
  font-weight: 600;
  color: #f97316;
}

.spin-animation {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Stats Bar */
.stats-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  padding: 1.25rem 2rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-icon {
  font-size: 1.5rem;
  color: #f97316;
}

.stat-icon.success { color: #22c55e; }
.stat-icon.purple { color: #8b5cf6; }
.stat-icon.cyan { color: #06b6d4; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

/* Filters Section */
.filters-section {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.search-container {
  margin-bottom: 1.25rem;
}

.search-input {
  font-size: 1rem;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 140px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-select {
  min-width: 140px;
}

.sort-view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sort-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Active Filters */
.active-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.active-filters-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Results Info */
.results-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0 0.5rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* Loading Grid */
.loading-grid {
  display: grid;
  gap: 1.5rem;
}

.loading-grid.grid {
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

.loading-grid.list {
  grid-template-columns: 1fr;
}

.skeleton-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.skeleton-thumbnail {
  height: 140px;
  background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  padding: 1rem;
}

.skeleton-line {
  height: 14px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.skeleton-line.title { width: 70%; height: 18px; }
.skeleton-line.subtitle { width: 50%; }
.skeleton-line.bar { height: 8px; }

.skeleton-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.skeleton-btn {
  width: 100px;
  height: 32px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8px;
}

.skeleton-btn.small { width: 32px; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Servers Container */
.servers-container {
  display: grid;
  gap: 1.5rem;
}

.servers-container.grid {
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

.servers-container.list {
  grid-template-columns: 1fr;
}

/* Server Card */
.server-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

.server-card:hover {
  transform: translateY(-4px);
  border-color: rgba(249, 115, 22, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(249, 115, 22, 0.1);
}

.server-card.is-favorite {
  border-color: rgba(249, 115, 22, 0.4);
}

.server-card.list {
  display: flex;
}

.server-card.list .map-thumbnail {
  width: 200px;
  min-height: 140px;
}

.server-card.list .server-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Map Thumbnail */
.map-thumbnail {
  position: relative;
  height: 140px;
  overflow: hidden;
}

.map-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.server-card:hover .map-thumbnail img {
  transform: scale(1.1);
}

.thumbnail-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2rem 1rem 0.75rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
}

.map-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

/* Status Indicator */
.status-indicator {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-indicator.running {
  background: rgba(34, 197, 94, 0.9);
  color: white;
}

.status-indicator.stopped {
  background: rgba(239, 68, 68, 0.9);
  color: white;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.status-indicator.running .status-dot {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

/* Favorite Button */
.favorite-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}

.favorite-btn:hover {
  background: rgba(0, 0, 0, 0.7);
  color: #f97316;
  transform: scale(1.1);
}

.favorite-btn.active {
  color: #f97316;
  animation: heartBeat 0.4s ease;
}

.favorite-btn.disabled {
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

.favorite-btn.disabled:hover {
  background: rgba(0, 0, 0, 0.5);
  color: rgba(255, 255, 255, 0.4);
  transform: none;
}

@keyframes heartBeat {
  0% { transform: scale(1); }
  25% { transform: scale(1.3); }
  50% { transform: scale(1); }
  75% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

/* Server Info */
.server-info {
  padding: 1rem;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.server-name {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.server-address {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  font-family: monospace;
  margin-bottom: 1rem;
}

/* Player Section */
.player-section {
  margin-bottom: 0.75rem;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
  color: rgba(255, 255, 255, 0.7);
}

.player-count {
  font-size: 0.9rem;
}

.player-count strong {
  color: #f97316;
  font-size: 1rem;
}

.player-count .separator {
  color: rgba(255, 255, 255, 0.3);
  margin: 0 0.15rem;
}

.player-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.player-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease, background 0.3s ease;
}

.player-bar-fill.low { background: linear-gradient(90deg, #22c55e, #4ade80); }
.player-bar-fill.medium { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.player-bar-fill.high { background: linear-gradient(90deg, #f97316, #fb923c); }
.player-bar-fill.full { background: linear-gradient(90deg, #ef4444, #f87171); }

/* Server Stats */
.server-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.server-stats .stat {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.ping-good { color: #22c55e !important; }
.ping-medium { color: #f59e0b !important; }
.ping-bad { color: #ef4444 !important; }

/* Server Actions */
.server-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.connect-btn {
  flex: 1;
}

/* Pulse Animation for Active */
.pulse-green {
  color: #22c55e;
  animation: pulseGreen 2s ease-in-out infinite;
}

@keyframes pulseGreen {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.empty-icon {
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 1.5rem;
}

/* Pagination Section */
.pagination-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.load-more {
  text-align: center;
}

/* Connect Modal */
.connect-modal-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.connect-server-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.connect-map-img {
  width: 80px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
}

.connect-map-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.connect-server-info h4 {
  margin: 0 0 0.25rem;
  font-weight: 600;
}

.connect-server-info p {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  font-family: monospace;
}

.connect-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Transition Animations */
.grid-enter-active,
.grid-leave-active {
  transition: all 0.4s ease;
}

.grid-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

.grid-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.grid-move {
  transition: transform 0.4s ease;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.list-move {
  transition: transform 0.3s ease;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.75rem;
  }

  .title-icon {
    width: 48px;
    height: 48px;
  }

  .header-content {
    flex-direction: column;
  }

  .stats-bar {
    gap: 1rem;
    padding: 1rem;
  }

  .stat-divider {
    display: none;
  }

  .filter-controls {
    flex-direction: column;
  }

  .filter-group {
    width: 100%;
  }

  .sort-view-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .server-card.list {
    flex-direction: column;
  }

  .server-card.list .map-thumbnail {
    width: 100%;
    height: 120px;
  }

  .pagination-section {
    flex-direction: column;
    gap: 1rem;
  }
}

/* Color utility classes */
.text-green-500 { color: #22c55e; }
.text-purple-500 { color: #8b5cf6; }
.text-cyan-500 { color: #06b6d4; }
</style>
