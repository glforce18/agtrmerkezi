<template>
  <div class="leaderboard-page min-h-screen relative overflow-hidden">
    <!-- Subtle Background -->
    <div class="subtle-bg"></div>

    <div class="container-custom py-3 relative z-10">
      <!-- Compact Header -->
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-lg font-bold flex items-center gap-2">
          <TrophyIcon class="w-5 h-5 text-orange-500" />
          Lider Tablosu
        </h1>
        <span class="text-xs text-green-500 flex items-center gap-1">
          <span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
          Canlı
        </span>
      </div>

      <!-- Category Tabs -->
      <div class="category-tabs-container mb-4">
        <div class="category-tabs glass-morphism">
          <button
            v-for="tab in categoryTabs"
            :key="tab.value"
            :class="['tab-button', { active: activeCategory === tab.value }]"
            @click="activeCategory = tab.value"
          >
            <component :is="tab.icon" class="w-5 h-5" />
            <span>{{ tab.label }}</span>
            <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
          </button>
          <div class="tab-indicator" :style="tabIndicatorStyle"></div>
        </div>
      </div>

      <!-- Filters Section -->
      <div class="filters-section glass-morphism mb-8 p-6">
        <div class="flex flex-col lg:flex-row gap-4 items-center">
          <!-- Search -->
          <div class="search-container flex-1 w-full lg:w-auto">
            <div class="search-input-wrapper">
              <SearchIcon class="w-5 h-5 text-gray-400 search-icon" />
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="getSearchPlaceholder()"
                class="search-input"
                @input="handleSearch"
              />
              <div v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
                <XIcon class="w-4 h-4" />
              </div>
            </div>
            <div v-if="searchQuery && filteredData.length === 0" class="search-no-results">
              Sonuç bulunamadı
            </div>
          </div>

          <!-- Time Range -->
          <div class="filter-group">
            <label class="filter-label">Zaman Aralığı</label>
            <div class="time-range-buttons">
              <button
                v-for="option in timeOptions"
                :key="option.value"
                :class="['time-btn', { active: timeFilter === option.value }]"
                @click="timeFilter = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>

          <!-- Sort -->
          <div class="filter-group">
            <label class="filter-label">Sıralama</label>
            <n-select
              v-model:value="sortBy"
              :options="sortOptions"
              class="sort-select"
              style="width: 160px;"
            />
          </div>
        </div>
      </div>

      <!-- Top 3 Podium -->
      <div v-if="activeCategory === 'players' && filteredData.length >= 3" class="podium-section mb-12">
        <div class="podium-grid">
          <!-- 2nd Place -->
          <div class="podium-item silver podium-entry" style="animation-delay: 0.2s" @mouseenter="hoveredPodium = 2" @mouseleave="hoveredPodium = null">
            <div class="podium-card glass-morphism" :class="{ hovered: hoveredPodium === 2 }">
              <div class="podium-medal silver-medal">
                <MedalIcon class="w-6 h-6" />
                <span>2</span>
              </div>
              <div class="podium-avatar-wrapper silver-ring">
                <n-avatar
                  round
                  :size="90"
                  :src="getAvatarUrl(filteredData[1].avatar, filteredData[1].name)"
                />
                <div class="online-indicator" :class="{ online: filteredData[1].isOnline }"></div>
              </div>
              <h3 class="podium-name">{{ filteredData[1].name }}</h3>
              <n-tag size="small" :bordered="false" class="podium-rank-tag">{{ filteredData[1].rank }}</n-tag>
              <div class="podium-score silver-score">{{ formatNumber(filteredData[1].score) }}</div>
              <div class="podium-label">Skor</div>
              <div class="podium-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ filteredData[1].kd }}</span>
                  <span class="stat-label">K/D</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ filteredData[1].accuracy }}%</span>
                  <span class="stat-label">İsabet</span>
                </div>
              </div>
            </div>
            <div class="podium-base silver-base">
              <div class="podium-height"></div>
            </div>
          </div>

          <!-- 1st Place (Center, Winner) -->
          <div
            class="podium-item gold winner podium-entry"
            style="animation-delay: 0s"
            @mouseenter="hoveredPodium = 1; triggerConfetti()"
            @mouseleave="hoveredPodium = null"
          >
            <div class="winner-spotlight"></div>
            <div class="podium-card glass-morphism gold-glow" :class="{ hovered: hoveredPodium === 1 }">
              <div class="crown-container">
                <CrownIcon class="crown-icon" />
                <div class="crown-glow"></div>
              </div>
              <div class="podium-avatar-wrapper gold-ring winner-avatar">
                <n-avatar
                  round
                  :size="110"
                  :src="getAvatarUrl(filteredData[0].avatar, filteredData[0].name)"
                />
                <div class="online-indicator online"></div>
                <div class="winner-ring"></div>
              </div>
              <h3 class="podium-name winner-name">{{ filteredData[0].name }}</h3>
              <n-tag type="warning" size="small" class="podium-rank-tag">{{ filteredData[0].rank }}</n-tag>
              <div class="podium-score gold-score">{{ formatNumber(filteredData[0].score) }}</div>
              <div class="podium-label">Skor</div>
              <div class="podium-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ filteredData[0].kd }}</span>
                  <span class="stat-label">K/D</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ filteredData[0].accuracy }}%</span>
                  <span class="stat-label">İsabet</span>
                </div>
              </div>
              <!-- Share Button -->
              <button class="share-btn" @click.stop="sharePosition(filteredData[0])">
                <Share2Icon class="w-4 h-4" />
              </button>
            </div>
            <div class="podium-base gold-base">
              <div class="podium-height"></div>
            </div>
          </div>

          <!-- 3rd Place -->
          <div class="podium-item bronze podium-entry" style="animation-delay: 0.4s" @mouseenter="hoveredPodium = 3" @mouseleave="hoveredPodium = null">
            <div class="podium-card glass-morphism" :class="{ hovered: hoveredPodium === 3 }">
              <div class="podium-medal bronze-medal">
                <MedalIcon class="w-6 h-6" />
                <span>3</span>
              </div>
              <div class="podium-avatar-wrapper bronze-ring">
                <n-avatar
                  round
                  :size="90"
                  :src="getAvatarUrl(filteredData[2].avatar, filteredData[2].name)"
                />
                <div class="online-indicator" :class="{ online: filteredData[2].isOnline }"></div>
              </div>
              <h3 class="podium-name">{{ filteredData[2].name }}</h3>
              <n-tag size="small" :bordered="false" class="podium-rank-tag">{{ filteredData[2].rank }}</n-tag>
              <div class="podium-score bronze-score">{{ formatNumber(filteredData[2].score) }}</div>
              <div class="podium-label">Skor</div>
              <div class="podium-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ filteredData[2].kd }}</span>
                  <span class="stat-label">K/D</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ filteredData[2].accuracy }}%</span>
                  <span class="stat-label">İsabet</span>
                </div>
              </div>
            </div>
            <div class="podium-base bronze-base">
              <div class="podium-height"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Your Rank Banner (if logged in) -->
      <div v-if="currentUserRank" class="your-rank-banner glass-morphism mb-8">
        <div class="flex items-center gap-4">
          <div class="your-rank-badge">
            <span>#{{ currentUserRank.position }}</span>
          </div>
          <div class="flex-1">
            <p class="text-sm text-gray-400">Sizin Sıranız</p>
            <h4 class="font-bold text-lg">{{ currentUserRank.name }}</h4>
          </div>
          <div class="your-rank-score">
            <span class="text-2xl font-bold text-orange-500">{{ formatNumber(currentUserRank.score) }}</span>
            <span class="text-sm text-gray-400 ml-2">Skor</span>
          </div>
          <button class="share-btn-alt" @click="sharePosition(currentUserRank)">
            <Share2Icon class="w-5 h-5" />
            <span>Paylaş</span>
          </button>
        </div>
      </div>

      <!-- Leaderboard Table -->
      <div class="leaderboard-table-container glass-morphism">
        <div class="table-header">
          <h2 class="table-title">
            <component :is="getCategoryIcon()" class="w-6 h-6 text-orange-500" />
            <span>{{ getCategoryTitle() }}</span>
          </h2>
          <div class="table-actions">
            <span class="results-count">{{ filteredData.length }} sonuç</span>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="currentData.length === 0 && !loadingPlayers && !loadingServers" class="empty-state">
          <TrophyIcon class="w-16 h-16 text-gray-600 mb-4" />
          <h3 class="text-xl font-semibold text-gray-400 mb-2">Henüz veri yok</h3>
          <p class="text-gray-500">Bu kategoride henüz sıralama verisi bulunmuyor.</p>
        </div>

        <!-- Loading State -->
        <div v-else-if="loadingPlayers || loadingServers" class="loading-state">
          <div class="loading-spinner"></div>
          <p class="text-gray-400 mt-4">Yükleniyor...</p>
        </div>

        <div v-else class="table-wrapper">
          <table class="leaderboard-table">
            <thead>
              <tr>
                <th class="rank-col">Sıra</th>
                <th class="player-col">{{ activeCategory === 'players' ? 'Oyuncu' : activeCategory === 'servers' ? 'Sunucu' : 'Kullanıcı' }}</th>
                <template v-if="activeCategory === 'players'">
                  <th>K/D</th>
                  <th>İsabet</th>
                </template>
                <template v-else-if="activeCategory === 'servers'">
                  <th>Oyuncular</th>
                  <th>Harita</th>
                </template>
                <template v-else>
                  <th>Sunucular</th>
                  <th>Forum</th>
                </template>
                <th class="score-col">Skor</th>
                <th class="actions-col"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in paginatedData"
                :key="item.id"
                :class="getRowClasses(item, index)"
                @mouseenter="hoveredRow = item.id"
                @mouseleave="hoveredRow = null"
              >
                <td class="rank-col">
                  <div :class="getRankClass(item.position)">
                    <template v-if="item.position === 1">
                      <CrownIcon class="w-4 h-4" />
                    </template>
                    <template v-else-if="item.position <= 3">
                      <MedalIcon class="w-4 h-4" />
                    </template>
                    <span>{{ item.position }}</span>
                  </div>
                </td>
                <td class="player-col">
                  <div class="player-info" @mouseenter="showProfilePreview($event, item)" @mouseleave="hideProfilePreview">
                    <div class="avatar-wrapper">
                      <n-avatar
                        v-if="activeCategory !== 'servers'"
                        round
                        :size="48"
                        :src="getAvatarUrl(item.avatar, item.name)"
                      />
                      <div v-else class="server-avatar">
                        <ServerIcon class="w-6 h-6" />
                      </div>
                      <div class="online-indicator" :class="{ online: item.isOnline }"></div>
                    </div>
                    <div class="player-details">
                      <span class="player-name">{{ item.name }}</span>
                      <span class="player-rank">{{ item.rank || item.region || item.role }}</span>
                    </div>
                  </div>
                </td>
                <template v-if="activeCategory === 'players'">
                  <td>
                    <div class="kd-stat">
                      <span class="kd-value">{{ item.kd }}</span>
                      <div class="kd-bar">
                        <div class="kd-fill" :style="{ width: `${Math.min(parseFloat(item.kd) / 4 * 100, 100)}%` }"></div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="accuracy-stat">
                      <div class="accuracy-bar">
                        <div class="accuracy-fill" :style="{ width: `${item.accuracy}%` }"></div>
                      </div>
                      <span class="accuracy-value">{{ item.accuracy }}%</span>
                    </div>
                  </td>
                </template>
                <template v-else-if="activeCategory === 'servers'">
                  <td>
                    <div class="players-stat">
                      <UsersIcon class="w-4 h-4 text-gray-400" />
                      <span>{{ item.players }}/{{ item.maxPlayers }}</span>
                      <div class="capacity-bar">
                        <div class="capacity-fill" :style="{ width: `${(item.players / item.maxPlayers) * 100}%` }"></div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <code class="map-name">{{ item.map }}</code>
                  </td>
                </template>
                <template v-else>
                  <td>
                    <n-tag type="primary" size="small">{{ item.servers }} sunucu</n-tag>
                  </td>
                  <td>
                    <n-tag type="info" size="small">{{ item.posts }} paylaşım</n-tag>
                  </td>
                </template>
                <td class="score-col">
                  <div class="score-display">
                    <TrendingUpIcon class="w-4 h-4 text-green-500" />
                    <span class="score-value">{{ formatNumber(item.score) }}</span>
                  </div>
                </td>
                <td class="actions-col">
                  <button class="row-share-btn" @click="sharePosition(item)">
                    <Share2Icon class="w-4 h-4" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="table-footer">
          <div class="pagination-info">
            {{ (currentPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentPage * itemsPerPage, filteredData.length) }} / {{ filteredData.length }}
          </div>
          <n-pagination
            v-model:page="currentPage"
            :page-count="totalPages"
            :page-slot="5"
            show-quick-jumper
          />
        </div>
      </div>

      <!-- Stats Summary Cards -->
      <div class="stats-section mt-12" ref="statsSection">
        <h3 class="stats-title">İstatistikler</h3>
        <div class="stats-grid">
          <div class="stat-card glass-morphism" v-for="(stat, index) in statsCards" :key="stat.id">
            <div class="stat-icon-wrapper" :style="{ backgroundColor: stat.bgColor }">
              <component :is="stat.icon" class="stat-icon" :style="{ color: stat.color }" />
            </div>
            <div class="stat-content">
              <p class="stat-label">{{ stat.label }}</p>
              <h3 class="stat-value-animated">
                <span ref="statCounters" :data-target="stat.value" :data-index="index">0</span>
                <span v-if="stat.suffix">{{ stat.suffix }}</span>
              </h3>
            </div>
            <div class="stat-trend" :class="stat.trendClass">
              <component :is="stat.trendIcon" class="w-4 h-4" />
              <span>{{ stat.trend }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Preview Tooltip -->
    <Teleport to="body">
      <Transition name="preview-fade">
        <div
          v-if="profilePreview.visible"
          class="profile-preview glass-morphism"
          :style="{ top: profilePreview.y + 'px', left: profilePreview.x + 'px' }"
        >
          <div class="preview-header">
            <n-avatar round :size="60" :src="getAvatarUrl(profilePreview.data?.avatar, profilePreview.data?.name)" />
            <div>
              <h4>{{ profilePreview.data?.name }}</h4>
              <p>{{ profilePreview.data?.rank }}</p>
            </div>
          </div>
          <div class="preview-stats">
            <div class="preview-stat">
              <span class="label">Skor</span>
              <span class="value">{{ formatNumber(profilePreview.data?.score || 0) }}</span>
            </div>
            <div class="preview-stat">
              <span class="label">K/D</span>
              <span class="value">{{ profilePreview.data?.kd }}</span>
            </div>
            <div class="preview-stat">
              <span class="label">İsabet</span>
              <span class="value">{{ profilePreview.data?.accuracy }}%</span>
            </div>
          </div>
          <div class="preview-footer">
            <span class="last-seen">Son görülme: 5 dakika önce</span>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Share Modal -->
    <n-modal v-model:show="shareModal.visible" preset="card" title="Sıralamanı Paylaş" class="share-modal">
      <div class="share-content">
        <div class="share-preview glass-morphism">
          <div class="share-rank">#{{ shareModal.data?.position }}</div>
          <h3>{{ shareModal.data?.name }}</h3>
          <p>{{ formatNumber(shareModal.data?.score || 0) }} Skor</p>
        </div>
        <div class="share-buttons">
          <button class="share-option twitter" @click="shareToTwitter">
            <span>Twitter</span>
          </button>
          <button class="share-option discord" @click="shareToDiscord">
            <span>Discord</span>
          </button>
          <button class="share-option copy" @click="copyShareLink">
            <CopyIcon class="w-5 h-5" />
            <span>Linki Kopyala</span>
          </button>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { NAvatar, NTag, NProgress, useMessage } from 'naive-ui'
import {
  TrophyIcon,
  ServerIcon,
  UsersIcon,
  SearchIcon,
  CrownIcon,
  TrendingUpIcon,
  UserIcon,
  BarChart3Icon as BarChartIcon,
  Share2Icon,
  ActivityIcon,
  ZapIcon,
  XIcon,
  MedalIcon,
  CopyIcon,
  TrendingDownIcon,
  FlameIcon,
  TargetIcon,
  AwardIcon
} from 'lucide-vue-next'

const message = useMessage()

// State
const activeCategory = ref('players')
const searchQuery = ref('')
const timeFilter = ref('all')
const sortBy = ref('rank')
const currentPage = ref(1)
const itemsPerPage = 10
const hoveredPodium = ref(null)
const hoveredRow = ref(null)
const showConfetti = ref(false)
const statsSection = ref(null)
const statCounters = ref([])
const countersAnimated = ref(false)

// Profile preview
const profilePreview = ref({
  visible: false,
  x: 0,
  y: 0,
  data: null
})

// Share modal
const shareModal = ref({
  visible: false,
  data: null
})

// Category tabs config
const categoryTabs = [
  { value: 'players', label: 'En İyi Oyuncular', icon: TrophyIcon, count: 10 },
  { value: 'servers', label: 'Popüler Sunucular', icon: ServerIcon, count: 3 },
  { value: 'users', label: 'Aktif Kullanıcılar', icon: UsersIcon, count: 3 }
]

const timeOptions = [
  { label: 'Hepsi', value: 'all' },
  { label: 'Bugün', value: 'today' },
  { label: 'Hafta', value: 'week' },
  { label: 'Ay', value: 'month' }
]

const sortOptions = [
  { label: 'Sıralama', value: 'rank' },
  { label: 'Skor', value: 'score' },
  { label: 'Kills', value: 'kills' },
  { label: 'İsabet', value: 'accuracy' }
]

// Tab indicator style
const tabIndicatorStyle = computed(() => {
  const index = categoryTabs.findIndex(t => t.value === activeCategory.value)
  return {
    transform: `translateX(${index * 100}%)`,
    width: `${100 / categoryTabs.length}%`
  }
})

// Mock current user (for "your rank" feature)
const currentUserId = ref(5) // Simulating logged in user

const currentUserRank = computed(() => {
  if (!currentUserId.value || activeCategory.value !== 'players') return null
  return playersData.value.find(p => p.id === currentUserId.value)
})

// Stats cards config
const statsCards = computed(() => [
  {
    id: 'competitors',
    label: 'Toplam Yarışmacılar',
    value: totalCompetitors.value,
    icon: UsersIcon,
    color: '#f97316',
    bgColor: 'rgba(249, 115, 22, 0.15)',
    trend: '+12%',
    trendClass: 'positive',
    trendIcon: TrendingUpIcon
  },
  {
    id: 'active',
    label: 'Şu An Aktif',
    value: activeNow.value,
    icon: ActivityIcon,
    color: '#a855f7',
    bgColor: 'rgba(168, 85, 247, 0.15)',
    trend: '+8%',
    trendClass: 'positive',
    trendIcon: TrendingUpIcon
  },
  {
    id: 'highest',
    label: 'En Yüksek Skor',
    value: highestScore.value,
    icon: FlameIcon,
    color: '#06b6d4',
    bgColor: 'rgba(6, 182, 212, 0.15)',
    trend: '+2,341',
    trendClass: 'positive',
    trendIcon: TrendingUpIcon
  },
  {
    id: 'accuracy',
    label: 'Ortalama İsabet',
    value: 72,
    suffix: '%',
    icon: TargetIcon,
    color: '#10b981',
    bgColor: 'rgba(16, 185, 129, 0.15)',
    trend: '+3%',
    trendClass: 'positive',
    trendIcon: TrendingUpIcon
  }
])

// Data - API'den çekilecek
const playersData = ref([])
const serversData = ref([])
const usersData = ref([])

// Loading states
const loadingPlayers = ref(false)
const loadingServers = ref(false)
const loadingUsers = ref(false)

// Fetch functions
const fetchPlayers = async () => {
  loadingPlayers.value = true
  try {
    const response = await fetch('/api/leaderboard?period=month&limit=50')
    if (response.ok) {
      const data = await response.json()
      playersData.value = (data.leaderboard || []).map((p, i) => ({
        id: p.user_id || i + 1,
        position: i + 1,
        name: p.username || 'Oyuncu',
        avatar: p.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${p.username}`,
        rank: getRankFromPoints(p.total_points),
        score: Math.round(p.total_points) || 0,
        kills: Math.round(p.total_points * 10) || 0,
        deaths: Math.round(p.total_points * 3) || 0,
        kd: (p.total_points / 30).toFixed(2),
        accuracy: Math.min(99, Math.floor(50 + p.total_points / 100)),
        isOnline: false
      }))
    }
  } catch (error) {
    console.error('Players fetch error:', error)
  } finally {
    loadingPlayers.value = false
  }
}

const fetchServers = async () => {
  loadingServers.value = true
  try {
    const response = await fetch('/api/servers/live?limit=20')
    if (response.ok) {
      const data = await response.json()
      serversData.value = (data.servers || []).map((s, i) => ({
        id: s.id,
        position: i + 1,
        name: s.name || 'Sunucu',
        region: s.country || 'TR',
        score: (s.current_players || s.players || 0) * 100 + (100 - (s.ping || 50)),
        players: s.current_players || s.players || 0,
        maxPlayers: s.max_players || 32,
        map: s.current_map || s.map || 'unknown',
        isOnline: s.is_online !== false
      }))
    }
  } catch (error) {
    console.error('Servers fetch error:', error)
  } finally {
    loadingServers.value = false
  }
}

const fetchStaff = async () => {
  // Staff listesi admin panelinden veya özel endpoint'den çekilebilir
  // Şimdilik boş bırakıyoruz
  loadingUsers.value = false
  usersData.value = []
}

const getRankFromPoints = (points) => {
  if (points >= 10000) return 'Global Elite'
  if (points >= 7500) return 'Supreme Master'
  if (points >= 5000) return 'Legendary Eagle'
  if (points >= 3000) return 'Distinguished Master'
  if (points >= 2000) return 'Master Guardian Elite'
  if (points >= 1000) return 'Master Guardian'
  if (points >= 500) return 'Gold Nova'
  return 'Silver'
}

// Computed
const currentData = computed(() => {
  switch (activeCategory.value) {
    case 'players': return playersData.value
    case 'servers': return serversData.value
    case 'users': return usersData.value
    default: return []
  }
})

const filteredData = computed(() => {
  let data = [...currentData.value]
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item => item.name.toLowerCase().includes(query))
  }
  // Sort
  if (sortBy.value === 'score') {
    data.sort((a, b) => b.score - a.score)
  } else if (sortBy.value === 'kills' && activeCategory.value === 'players') {
    data.sort((a, b) => b.kills - a.kills)
  } else if (sortBy.value === 'accuracy' && activeCategory.value === 'players') {
    data.sort((a, b) => b.accuracy - a.accuracy)
  }
  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / itemsPerPage))
const totalCompetitors = computed(() => currentData.value.length)
const activeNow = computed(() => Math.floor(currentData.value.length * 0.65))
const highestScore = computed(() => currentData.value.length > 0 ? currentData.value[0].score : 0)

// Methods
const formatNumber = (num) => {
  return new Intl.NumberFormat('tr-TR').format(num)
}

const getAvatarUrl = (avatar, username) => {
  if (!avatar) return `https://api.dicebear.com/7.x/initials/svg?seed=${username || 'user'}`
  if (avatar.startsWith('http')) return avatar
  return `/static/${avatar}`
}

const getSearchPlaceholder = () => {
  switch (activeCategory.value) {
    case 'players': return 'Oyuncu ara...'
    case 'servers': return 'Sunucu ara...'
    case 'users': return 'Kullanıcı ara...'
    default: return 'Ara...'
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const getCategoryIcon = () => {
  switch (activeCategory.value) {
    case 'players': return TrophyIcon
    case 'servers': return ServerIcon
    case 'users': return UsersIcon
    default: return TrophyIcon
  }
}

const getCategoryTitle = () => {
  switch (activeCategory.value) {
    case 'players': return 'Oyuncu Sıralaması'
    case 'servers': return 'Sunucu Sıralaması'
    case 'users': return 'Kullanıcı Sıralaması'
    default: return 'Sıralama'
  }
}

const getRowClasses = (item, index) => {
  const classes = ['table-row']
  if (item.position <= 3) classes.push('top-three')
  if (item.position === 1) classes.push('first-place')
  if (item.position === 2) classes.push('second-place')
  if (item.position === 3) classes.push('third-place')
  if (hoveredRow.value === item.id) classes.push('hovered')
  if (currentUserId.value && item.id === currentUserId.value) classes.push('current-user')
  return classes.join(' ')
}

const getRankClass = (position) => {
  if (position === 1) return 'rank-badge gold rank-glow'
  if (position === 2) return 'rank-badge silver rank-glow'
  if (position === 3) return 'rank-badge bronze rank-glow'
  return 'rank-badge normal'
}

// Particle effects
const getParticleStyle = (index) => {
  const size = Math.random() * 4 + 2
  return {
    '--x': `${Math.random() * 100}%`,
    '--y': `${Math.random() * 100}%`,
    '--size': `${size}px`,
    '--duration': `${Math.random() * 20 + 10}s`,
    '--delay': `${Math.random() * 5}s`,
    '--opacity': Math.random() * 0.5 + 0.1
  }
}

// Confetti effect
const getConfettiStyle = (index) => {
  const colors = ['#f97316', '#fbbf24', '#a855f7', '#06b6d4', '#10b981', '#ef4444']
  return {
    '--x': `${Math.random() * 100}%`,
    '--color': colors[index % colors.length],
    '--rotation': `${Math.random() * 360}deg`,
    '--delay': `${Math.random() * 0.5}s`
  }
}

let confettiTimeout = null
const triggerConfetti = () => {
  if (confettiTimeout) return
  showConfetti.value = true
  confettiTimeout = setTimeout(() => {
    showConfetti.value = false
    confettiTimeout = null
  }, 3000)
}

// Profile preview
let previewTimeout = null
const showProfilePreview = (event, item) => {
  if (activeCategory.value !== 'players') return
  previewTimeout = setTimeout(() => {
    const rect = event.target.getBoundingClientRect()
    profilePreview.value = {
      visible: true,
      x: rect.right + 10,
      y: rect.top,
      data: item
    }
  }, 500)
}

const hideProfilePreview = () => {
  if (previewTimeout) clearTimeout(previewTimeout)
  profilePreview.value.visible = false
}

// Share functionality
const sharePosition = (item) => {
  shareModal.value = {
    visible: true,
    data: item
  }
}

const shareToTwitter = () => {
  const text = `AGTR Merkezi'nde #${shareModal.value.data?.position}. sıradayım! Skor: ${formatNumber(shareModal.value.data?.score || 0)}`
  window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank')
}

const shareToDiscord = () => {
  const text = `AGTR Merkezi'nde #${shareModal.value.data?.position}. sıradayım! Skor: ${formatNumber(shareModal.value.data?.score || 0)}`
  navigator.clipboard.writeText(text)
  message.success('Discord için kopyalandı!')
}

const copyShareLink = () => {
  const link = `${window.location.origin}/leaderboard?highlight=${shareModal.value.data?.id}`
  navigator.clipboard.writeText(link)
  message.success('Link kopyalandı!')
}

// Intersection Observer for animated counters
let observer = null
const setupIntersectionObserver = () => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !countersAnimated.value) {
        countersAnimated.value = true
        animateCounters()
      }
    })
  }, { threshold: 0.3 })

  if (statsSection.value) {
    observer.observe(statsSection.value)
  }
}

const animateCounters = () => {
  nextTick(() => {
    const counters = document.querySelectorAll('[data-target]')
    counters.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-target'))
      const duration = 2000
      const step = target / (duration / 16)
      let current = 0

      const updateCounter = () => {
        current += step
        if (current < target) {
          counter.textContent = formatNumber(Math.floor(current))
          requestAnimationFrame(updateCounter)
        } else {
          counter.textContent = formatNumber(target)
        }
      }

      updateCounter()
    })
  })
}

// Lifecycle
onMounted(() => {
  setupIntersectionObserver()
  // Fetch real data from API
  fetchPlayers()
  fetchServers()
  fetchStaff()
})

onUnmounted(() => {
  if (observer) observer.disconnect()
  if (confettiTimeout) clearTimeout(confettiTimeout)
  if (previewTimeout) clearTimeout(previewTimeout)
})

// Watch for category changes
watch(activeCategory, () => {
  currentPage.value = 1
  searchQuery.value = ''
})
</script>

<style scoped>
/* Base Styles & Variables */
.leaderboard-page {
  --glass-bg: rgba(17, 17, 27, 0.8);
  --glass-border: rgba(255, 255, 255, 0.08);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  --orange: #f97316;
  --gold: #fbbf24;
  --silver: #94a3b8;
  --bronze: #cd7f32;
  --purple: #a855f7;
  --cyan: #06b6d4;
  min-height: 100vh;
  overflow-x: hidden;
  width: 100%;
  max-width: 100vw;
}

/* Glass Morphism */
.glass-morphism {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow);
}

/* Particles Background */
.particles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  left: var(--x);
  top: var(--y);
  width: var(--size);
  height: var(--size);
  background: radial-gradient(circle, var(--orange), transparent);
  border-radius: 50%;
  opacity: var(--opacity);
  animation: particle-float var(--duration) ease-in-out infinite;
  animation-delay: var(--delay);
}

@keyframes particle-float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -30px) scale(1.2);
  }
  50% {
    transform: translate(-10px, -60px) scale(0.8);
  }
  75% {
    transform: translate(30px, -30px) scale(1.1);
  }
}

/* Confetti */
.confetti-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 100;
}

.confetti {
  position: absolute;
  left: var(--x);
  top: -20px;
  width: 10px;
  height: 10px;
  background: var(--color);
  transform: rotate(var(--rotation));
  animation: confetti-fall 3s ease-out forwards;
  animation-delay: var(--delay);
}

@keyframes confetti-fall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

/* Hero Section */
.hero-section {
  position: relative;
}

.trophy-container {
  position: relative;
  display: inline-block;
}

.trophy-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.4), transparent 70%);
  border-radius: 50%;
  animation: trophy-pulse 2s ease-in-out infinite;
}

@keyframes trophy-pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.8;
  }
}

.trophy-icon {
  position: relative;
  z-index: 2;
  animation: trophy-bounce 2s ease-in-out infinite;
}

@keyframes trophy-bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.trophy-sparkles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100px;
  height: 100px;
  transform: translate(-50%, -50%);
}

.sparkle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 4px;
  height: 4px;
  background: var(--gold);
  border-radius: 50%;
  transform-origin: center;
  animation: sparkle-orbit 3s linear infinite;
  animation-delay: var(--delay);
}

@keyframes sparkle-orbit {
  0% {
    transform: rotate(var(--angle)) translateX(50px) scale(0);
    opacity: 0;
  }
  50% {
    transform: rotate(calc(var(--angle) + 180deg)) translateX(50px) scale(1);
    opacity: 1;
  }
  100% {
    transform: rotate(calc(var(--angle) + 360deg)) translateX(50px) scale(0);
    opacity: 0;
  }
}

.hero-title {
  animation: hero-appear 0.8s ease-out;
}

.hero-subtitle {
  animation: hero-appear 0.8s ease-out 0.2s both;
}

@keyframes hero-appear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.text-gradient-animated {
  background: linear-gradient(90deg, var(--orange), var(--purple), var(--cyan), var(--orange));
  background-size: 300% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 8s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: live-pulse 1.5s ease-in-out infinite;
}

@keyframes live-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
  }
}

/* Category Tabs */
.category-tabs-container {
  display: flex;
  justify-content: center;
}

.category-tabs {
  display: flex;
  position: relative;
  padding: 6px;
  gap: 4px;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: transparent;
  border: none;
  color: #9ca3af;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
  border-radius: 10px;
}

.tab-button:hover {
  color: var(--text-primary);
}

.tab-button.active {
  color: var(--text-primary);
}

.tab-count {
  background: rgba(249, 115, 22, 0.2);
  color: var(--orange);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.tab-indicator {
  position: absolute;
  bottom: 6px;
  left: 6px;
  height: calc(100% - 12px);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.3), rgba(168, 85, 247, 0.2));
  border-radius: 10px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
}

/* Filters Section */
.filters-section {
  padding: 24px;
}

.search-container {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  z-index: 2;
  transition: color 0.3s ease;
}

.search-input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 15px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--orange);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.search-input:focus + .search-icon,
.search-input-wrapper:focus-within .search-icon {
  color: var(--orange);
}

.search-input::placeholder {
  color: #6b7280;
}

.search-clear {
  position: absolute;
  right: 12px;
  padding: 4px;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.3s ease;
}

.search-clear:hover {
  color: var(--text-primary);
}

.search-no-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  margin-top: 8px;
  color: #ef4444;
  font-size: 14px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}

.time-range-buttons {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px;
  border-radius: 10px;
}

.time-btn {
  padding: 8px 12px;
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.time-btn:hover {
  color: #fff;
}

.time-btn.active {
  background: var(--orange);
  color: #fff;
}

/* Podium Section */
.podium-section {
  margin-top: 2rem;
}

.podium-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
  max-width: 900px;
  margin: 0 auto;
  align-items: end;
}

.podium-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.podium-item.silver,
.podium-item.bronze {
  margin-top: 60px;
}

.podium-item.gold {
  order: 0;
}

.podium-item.silver {
  order: -1;
}

.podium-item.bronze {
  order: 1;
}

.winner-spotlight {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.3), transparent 70%);
  border-radius: 50%;
  animation: spotlight-pulse 3s ease-in-out infinite;
  pointer-events: none;
}

@keyframes spotlight-pulse {
  0%, 100% {
    opacity: 0.5;
    transform: translateX(-50%) scale(1);
  }
  50% {
    opacity: 0.8;
    transform: translateX(-50%) scale(1.1);
  }
}

.podium-card {
  padding: 24px;
  text-align: center;
  position: relative;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
}

.podium-card.hovered {
  transform: translateY(-8px);
}

.podium-card.gold-glow {
  border: 2px solid rgba(251, 191, 36, 0.5);
  box-shadow:
    0 0 30px rgba(251, 191, 36, 0.2),
    inset 0 0 30px rgba(251, 191, 36, 0.05);
}

.podium-medal {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #fff;
  border: 3px solid #1a1a2e;
}

.silver-medal {
  background: linear-gradient(135deg, #94a3b8, #64748b);
}

.bronze-medal {
  background: linear-gradient(135deg, #cd7f32, #a0522d);
}

.crown-container {
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%);
}

.crown-icon {
  width: 48px;
  height: 48px;
  color: var(--gold);
  filter: drop-shadow(0 0 10px rgba(251, 191, 36, 0.5));
  animation: crown-float 2s ease-in-out infinite;
}

@keyframes crown-float {
  0%, 100% {
    transform: translateY(0) rotate(-5deg);
  }
  50% {
    transform: translateY(-5px) rotate(5deg);
  }
}

.crown-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.4), transparent);
  border-radius: 50%;
  animation: crown-glow-pulse 2s ease-in-out infinite;
}

@keyframes crown-glow-pulse {
  0%, 100% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.2);
  }
}

.podium-avatar-wrapper {
  position: relative;
  margin-bottom: 16px;
  padding: 4px;
  border-radius: 50%;
}

.gold-ring {
  background: linear-gradient(135deg, var(--gold), #f59e0b);
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
}

.silver-ring {
  background: linear-gradient(135deg, var(--silver), #64748b);
  box-shadow: 0 0 15px rgba(148, 163, 184, 0.3);
}

.bronze-ring {
  background: linear-gradient(135deg, var(--bronze), #a0522d);
  box-shadow: 0 0 15px rgba(205, 127, 50, 0.3);
}

.winner-avatar .winner-ring {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border: 2px solid var(--gold);
  border-radius: 50%;
  animation: winner-ring-pulse 2s ease-in-out infinite;
}

@keyframes winner-ring-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0;
  }
}

.online-indicator {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 14px;
  height: 14px;
  background: #6b7280;
  border: 3px solid #1a1a2e;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.online-indicator.online {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.podium-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.winner-name {
  font-size: 22px;
  background: linear-gradient(90deg, var(--gold), #fff, var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.podium-rank-tag {
  margin-bottom: 12px;
}

.podium-score {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 4px;
}

.gold-score {
  color: var(--gold);
  text-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
}

.silver-score {
  color: var(--silver);
}

.bronze-score {
  color: var(--bronze);
}

.podium-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 16px;
}

.podium-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-item .stat-value {
  font-weight: 700;
  font-size: 16px;
  color: var(--text-primary);
}

.stat-item .stat-label {
  font-size: 11px;
  color: #6b7280;
}

.share-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-btn:hover {
  background: var(--orange);
  color: #fff;
}

.podium-base {
  width: 100%;
  margin-top: 16px;
  position: relative;
}

.podium-height {
  width: 100%;
  border-radius: 8px 8px 0 0;
}

.gold-base .podium-height {
  height: 80px;
  background: linear-gradient(180deg, rgba(251, 191, 36, 0.3), rgba(251, 191, 36, 0.1));
  border-top: 2px solid var(--gold);
}

.silver-base .podium-height {
  height: 50px;
  background: linear-gradient(180deg, rgba(148, 163, 184, 0.3), rgba(148, 163, 184, 0.1));
  border-top: 2px solid var(--silver);
}

.bronze-base .podium-height {
  height: 30px;
  background: linear-gradient(180deg, rgba(205, 127, 50, 0.3), rgba(205, 127, 50, 0.1));
  border-top: 2px solid var(--bronze);
}

/* Your Rank Banner */
.your-rank-banner {
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(168, 85, 247, 0.1));
  border: 1px solid rgba(249, 115, 22, 0.3);
  animation: your-rank-glow 3s ease-in-out infinite;
}

@keyframes your-rank-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(249, 115, 22, 0.1);
  }
  50% {
    box-shadow: 0 0 30px rgba(249, 115, 22, 0.2);
  }
}

.your-rank-badge {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, var(--orange), var(--purple));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  color: #fff;
}

.share-btn-alt {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--orange);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-btn-alt:hover {
  background: #ea580c;
  transform: translateY(-2px);
}

/* Leaderboard Table */
.leaderboard-table-container {
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.table-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.results-count {
  font-size: 14px;
  color: #6b7280;
}

.table-wrapper {
  overflow-x: auto;
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
}

.leaderboard-table th {
  padding: 16px 20px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.leaderboard-table td {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-row {
  transition: all 0.3s ease;
}

.table-row:hover,
.table-row.hovered {
  background: rgba(249, 115, 22, 0.05);
}

.table-row.current-user {
  background: rgba(249, 115, 22, 0.1);
  border-left: 3px solid var(--orange);
}

.table-row.first-place {
  background: linear-gradient(90deg, rgba(251, 191, 36, 0.1), transparent);
}

.table-row.second-place {
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.08), transparent);
}

.table-row.third-place {
  background: linear-gradient(90deg, rgba(205, 127, 50, 0.08), transparent);
}

.rank-col {
  width: 80px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
}

.rank-badge.gold {
  background: linear-gradient(135deg, var(--gold), #f59e0b);
  color: #1a1a2e;
  box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3);
}

.rank-badge.silver {
  background: linear-gradient(135deg, var(--silver), #64748b);
  color: #1a1a2e;
  box-shadow: 0 4px 15px rgba(148, 163, 184, 0.3);
}

.rank-badge.bronze {
  background: linear-gradient(135deg, var(--bronze), #a0522d);
  color: #fff;
  box-shadow: 0 4px 15px rgba(205, 127, 50, 0.3);
}

.rank-badge.normal {
  background: rgba(255, 255, 255, 0.05);
  color: #6b7280;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
}

.avatar-wrapper {
  position: relative;
}

.server-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--orange), var(--purple));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.player-details {
  display: flex;
  flex-direction: column;
}

.player-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 15px;
}

.player-rank {
  font-size: 13px;
  color: #6b7280;
}

.kd-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kd-value {
  font-weight: 700;
  font-family: monospace;
  color: var(--text-primary);
}

.kd-bar {
  width: 60px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.kd-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--orange), var(--purple));
  border-radius: 2px;
  transition: width 0.5s ease;
}

.accuracy-stat {
  display: flex;
  align-items: center;
  gap: 10px;
}

.accuracy-bar {
  flex: 1;
  max-width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.accuracy-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #06b6d4);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.accuracy-value {
  font-weight: 600;
  font-size: 14px;
  color: #10b981;
}

.players-stat {
  display: flex;
  align-items: center;
  gap: 8px;
}

.capacity-bar {
  width: 50px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.capacity-fill {
  height: 100%;
  background: var(--orange);
  border-radius: 2px;
}

.map-name {
  padding: 4px 10px;
  background: rgba(249, 115, 22, 0.1);
  color: var(--orange);
  border-radius: 6px;
  font-size: 13px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-value {
  font-weight: 800;
  font-size: 18px;
  color: var(--text-primary);
}

.row-share-btn {
  padding: 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0;
}

.table-row:hover .row-share-btn {
  opacity: 1;
}

.row-share-btn:hover {
  background: var(--orange);
  border-color: var(--orange);
  color: #fff;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

/* Stats Section */
.stats-section {
  padding: 2rem 0;
}

.stats-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(249, 115, 22, 0.3);
}

.stat-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon {
  width: 28px;
  height: 28px;
}

.stat-content {
  flex: 1;
}

.stat-content .stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value-animated {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.stat-trend.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-trend.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Profile Preview Tooltip */
.profile-preview {
  position: fixed;
  z-index: 1000;
  width: 280px;
  padding: 20px;
  pointer-events: none;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.preview-header h4 {
  font-weight: 700;
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.preview-header p {
  font-size: 13px;
  color: #6b7280;
}

.preview-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 12px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-stat {
  text-align: center;
}

.preview-stat .label {
  display: block;
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 4px;
}

.preview-stat .value {
  font-weight: 700;
  font-size: 15px;
  color: var(--orange);
}

.preview-footer {
  padding-top: 12px;
}

.last-seen {
  font-size: 12px;
  color: #6b7280;
}

.preview-fade-enter-active,
.preview-fade-leave-active {
  transition: all 0.2s ease;
}

.preview-fade-enter-from,
.preview-fade-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

/* Share Modal */
.share-modal {
  max-width: 400px;
}

.share-content {
  text-align: center;
}

.share-preview {
  padding: 24px;
  margin-bottom: 24px;
}

.share-rank {
  font-size: 48px;
  font-weight: 800;
  background: linear-gradient(90deg, var(--orange), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.share-preview h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.share-preview p {
  color: #6b7280;
}

.share-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.share-option {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-option.twitter {
  background: #1da1f2;
  color: #fff;
}

.share-option.twitter:hover {
  background: #1a91da;
}

.share-option.discord {
  background: #5865f2;
  color: #fff;
}

.share-option.discord:hover {
  background: #4752c4;
}

.share-option.copy {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.share-option.copy:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Responsive */
@media (max-width: 1024px) {
  .podium-grid {
    gap: 16px;
  }

  .podium-card {
    padding: 16px;
  }

  .podium-avatar-wrapper .n-avatar {
    width: 70px !important;
    height: 70px !important;
  }

  .gold-ring .n-avatar {
    width: 80px !important;
    height: 80px !important;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 3rem;
  }

  .category-tabs {
    flex-direction: column;
    gap: 8px;
  }

  .tab-indicator {
    display: none;
  }

  .tab-button.active {
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.3), rgba(168, 85, 247, 0.2));
  }

  .podium-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .podium-item {
    order: initial !important;
    margin-top: 0 !important;
  }

  .podium-item.gold {
    order: -1 !important;
  }

  .filters-section {
    padding: 16px;
  }

  .time-range-buttons {
    flex-wrap: wrap;
  }

  .leaderboard-table th,
  .leaderboard-table td {
    padding: 12px;
  }

  .your-rank-banner .flex {
    flex-wrap: wrap;
  }

  .share-btn-alt {
    width: 100%;
    justify-content: center;
    margin-top: 12px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .trophy-icon {
    width: 60px;
    height: 60px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* Empty & Loading States */
.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state svg {
  opacity: 0.5;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(249, 115, 22, 0.2);
  border-top-color: var(--orange);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Subtle Background */
.subtle-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at 20% 20%, rgba(249, 115, 22, 0.05) 0%, transparent 50%),
              radial-gradient(ellipse at 80% 80%, rgba(168, 85, 247, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}
</style>
