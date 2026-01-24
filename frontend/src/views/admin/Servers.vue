<template>
  <AdminLayout>
    <div class="servers-page">
      <!-- Page Header -->
      <header class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">
              <Server :size="28" class="title-icon" />
              Sunucu Yönetimi
            </h1>
            <p class="page-subtitle">Tüm sunucuları tek panelden yönetin ve izleyin</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-ghost" @click="refreshServers" :disabled="refreshing">
              <RefreshCw :size="18" :class="{ 'spin': refreshing }" />
              <span>Yenile</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Quick Stats -->
      <section class="stats-section">
        <div class="stat-card total">
          <div class="stat-icon">
            <Server :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ totalServers }}</span>
            <span class="stat-label">Toplam Sunucu</span>
          </div>
          <div class="stat-decoration"></div>
        </div>

        <div class="stat-card online">
          <div class="stat-icon">
            <Wifi :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ onlineCount }}</span>
            <span class="stat-label">Online</span>
          </div>
          <div class="stat-indicator pulse"></div>
        </div>

        <div class="stat-card offline">
          <div class="stat-icon">
            <WifiOff :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ offlineCount }}</span>
            <span class="stat-label">Offline</span>
          </div>
        </div>

        <div class="stat-card players">
          <div class="stat-icon">
            <Users :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ totalPlayers }}</span>
            <span class="stat-label">Aktif Oyuncu</span>
          </div>
        </div>
      </section>

      <!-- Filters & Controls -->
      <section class="controls-section">
        <div class="search-wrapper">
          <Search :size="18" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Sunucu, harita veya sahip ara..."
            class="search-input"
            @input="debouncedSearch"
          />
          <kbd v-if="!searchQuery" class="search-shortcut">/</kbd>
          <button v-else class="search-clear" @click="clearSearch">
            <X :size="16" />
          </button>
        </div>

        <!-- Steam ID Search -->
        <div class="steam-search-wrapper">
          <Hash :size="18" class="search-icon" />
          <input
            v-model="steamIdSearch"
            type="text"
            placeholder="Steam ID ile ara (STEAM_0:0:123)"
            class="search-input steam-input"
            @keyup.enter="searchBySteamId"
          />
          <button class="btn btn-sm btn-primary" @click="searchBySteamId" :disabled="!steamIdSearch || steamSearching">
            <Loader2 v-if="steamSearching" :size="14" class="spin" />
            <Search v-else :size="14" />
          </button>
        </div>

        <div class="filter-group">
          <div class="filter-item">
            <Gamepad2 :size="16" class="filter-icon" />
            <select v-model="filterGame" class="filter-select" @change="applyFilters">
              <option value="">Tüm Oyunlar</option>
              <option value="hldm">Half-Life</option>
              <option value="ag">Half-Life AG</option>
              <option value="cs16">Counter-Strike 1.6</option>
            </select>
          </div>

          <div class="filter-item">
            <Activity :size="16" class="filter-icon" />
            <select v-model="filterStatus" class="filter-select" @change="applyFilters">
              <option value="">Tüm Durumlar</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
            </select>
          </div>
        </div>

        <div class="view-toggle">
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
            title="Izgara Görünüm"
          >
            <LayoutGrid :size="18" />
          </button>
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
            title="Liste Görünüm"
          >
            <List :size="18" />
          </button>
        </div>
      </section>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner">
          <Loader2 :size="40" class="spin" />
        </div>
        <p class="loading-text">Sunucular yükleniyor...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredServers.length === 0" class="empty-state">
        <div class="empty-icon">
          <ServerOff :size="64" />
        </div>
        <h3 class="empty-title">Sunucu Bulunamadı</h3>
        <p class="empty-description">
          {{ searchQuery || filterGame || filterStatus
            ? 'Arama kriterlerine uygun sunucu bulunamadı.'
            : 'Henüz kayıtli sunucu bulunmuyor.' }}
        </p>
        <button v-if="searchQuery || filterGame || filterStatus" class="btn btn-secondary" @click="clearAllFilters">
          <RotateCcw :size="16" />
          Filtreleri Temizle
        </button>
      </div>

      <!-- Grid View -->
      <section v-else-if="viewMode === 'grid'" class="servers-grid">
        <TransitionGroup name="card" appear>
          <article
            v-for="server in filteredServers"
            :key="server.id"
            class="server-card"
            :class="{ 'is-online': server.is_online, 'is-offline': !server.is_online }"
          >
            <!-- Map Thumbnail -->
            <div class="card-thumbnail">
              <img
                v-if="server.map && getMapThumbnail(server.map)"
                :src="getMapThumbnail(server.map)"
                :alt="server.map"
                class="map-image"
                @error="handleImageError"
              />
              <div v-else class="map-placeholder">
                <Map :size="32" />
              </div>
              <div class="status-badge" :class="server.is_online ? 'online' : 'offline'">
                <span class="status-dot"></span>
                {{ server.is_online ? 'Online' : 'Offline' }}
              </div>
              <div class="game-tag">{{ getGameLabel(server.game_type) }}</div>
            </div>

            <!-- Card Content -->
            <div class="card-content">
              <div class="card-header">
                <h3 class="server-name">{{ server.name }}</h3>
                <div class="player-badge" :class="getPlayerBadgeClass(server)">
                  <Users :size="14" />
                  <span>{{ server.players || 0 }}/{{ server.max_players || 0 }}</span>
                </div>
              </div>

              <div class="server-info">
                <div class="info-row">
                  <Map :size="14" />
                  <span>{{ server.map || 'N/A' }}</span>
                </div>
                <div class="info-row">
                  <Globe :size="14" />
                  <code class="server-address">{{ server.ip }}:{{ server.port }}</code>
                </div>
              </div>

              <!-- Resource Bars -->
              <div v-if="server.is_online && server.resources" class="resource-bars">
                <div class="resource-item">
                  <div class="resource-header">
                    <Cpu :size="12" />
                    <span>CPU</span>
                    <span class="resource-value">{{ server.resources.cpu || 0 }}%</span>
                  </div>
                  <div class="resource-bar">
                    <div
                      class="resource-fill cpu"
                      :style="{ width: `${server.resources.cpu || 0}%` }"
                      :class="getResourceClass(server.resources.cpu)"
                    ></div>
                  </div>
                </div>

                <div class="resource-item">
                  <div class="resource-header">
                    <MemoryStick :size="12" />
                    <span>RAM</span>
                    <span class="resource-value">{{ server.resources.ram || 0 }}%</span>
                  </div>
                  <div class="resource-bar">
                    <div
                      class="resource-fill ram"
                      :style="{ width: `${server.resources.ram || 0}%` }"
                      :class="getResourceClass(server.resources.ram)"
                    ></div>
                  </div>
                </div>

                <div class="resource-item">
                  <div class="resource-header">
                    <HardDrive :size="12" />
                    <span>Disk</span>
                    <span class="resource-value">{{ server.resources.disk || 0 }}%</span>
                  </div>
                  <div class="resource-bar">
                    <div
                      class="resource-fill disk"
                      :style="{ width: `${server.resources.disk || 0}%` }"
                      :class="getResourceClass(server.resources.disk)"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- Owner Info -->
              <div v-if="server.owner" class="owner-info">
                <img :src="getUserAvatar(server.owner.username)" :alt="server.owner.username" class="owner-avatar" />
                <span class="owner-name">{{ server.owner.username }}</span>
              </div>
            </div>

            <!-- Card Actions -->
            <div class="card-actions">
              <button class="action-btn view" @click="viewServer(server)" title="Detay">
                <Eye :size="16" />
              </button>
              <button
                v-if="!server.is_online"
                class="action-btn start"
                @click="startServer(server)"
                :disabled="actionLoading[server.id]"
                title="Başlat"
              >
                <Play :size="16" />
              </button>
              <button
                v-else
                class="action-btn stop"
                @click="stopServer(server)"
                :disabled="actionLoading[server.id]"
                title="Durdur"
              >
                <Square :size="16" />
              </button>
              <button
                class="action-btn restart"
                @click="restartServer(server)"
                :disabled="actionLoading[server.id] || !server.is_online"
                title="Yeniden Başlat"
              >
                <RotateCcw :size="16" />
              </button>
              <button class="action-btn delete" @click="confirmDelete(server)" title="Sil">
                <Trash2 :size="16" />
              </button>
            </div>
          </article>
        </TransitionGroup>
      </section>

      <!-- List View -->
      <section v-else class="servers-list">
        <div class="list-header">
          <div class="col-status">Durum</div>
          <div class="col-name">Sunucu</div>
          <div class="col-game">Oyun</div>
          <div class="col-map">Harita</div>
          <div class="col-players">Oyuncular</div>
          <div class="col-owner">Sahip</div>
          <div class="col-resources">Kaynaklar</div>
          <div class="col-actions">İşlemler</div>
        </div>

        <TransitionGroup name="list" appear>
          <div
            v-for="server in filteredServers"
            :key="server.id"
            class="list-row"
            :class="{ 'is-online': server.is_online }"
          >
            <div class="col-status">
              <span class="status-indicator" :class="server.is_online ? 'online' : 'offline'">
                <span class="indicator-dot"></span>
              </span>
            </div>

            <div class="col-name">
              <span class="server-title">{{ server.name }}</span>
              <code class="server-addr">{{ server.ip }}:{{ server.port }}</code>
            </div>

            <div class="col-game">
              <span class="game-badge" :class="server.game_type">
                {{ getGameLabel(server.game_type) }}
              </span>
            </div>

            <div class="col-map">
              <div class="map-info">
                <img
                  v-if="getMapThumbnail(server.map)"
                  :src="getMapThumbnail(server.map)"
                  class="map-thumb"
                  @error="handleImageError"
                />
                <span>{{ server.map || 'N/A' }}</span>
              </div>
            </div>

            <div class="col-players">
              <div class="players-display" :class="getPlayerBadgeClass(server)">
                <Users :size="14" />
                <span>{{ server.players || 0 }}/{{ server.max_players || 0 }}</span>
              </div>
            </div>

            <div class="col-owner">
              <div v-if="server.owner" class="owner-cell">
                <img :src="getUserAvatar(server.owner.username)" class="owner-thumb" />
                <span>{{ server.owner.username }}</span>
              </div>
              <span v-else class="no-owner">-</span>
            </div>

            <div class="col-resources">
              <div v-if="server.is_online && server.resources" class="mini-resources">
                <div class="mini-bar" :title="`CPU: ${server.resources.cpu || 0}%`">
                  <div
                    class="mini-fill"
                    :style="{ width: `${server.resources.cpu || 0}%` }"
                    :class="getResourceClass(server.resources.cpu)"
                  ></div>
                </div>
                <div class="mini-bar" :title="`RAM: ${server.resources.ram || 0}%`">
                  <div
                    class="mini-fill"
                    :style="{ width: `${server.resources.ram || 0}%` }"
                    :class="getResourceClass(server.resources.ram)"
                  ></div>
                </div>
              </div>
              <span v-else class="no-resources">-</span>
            </div>

            <div class="col-actions">
              <div class="action-group">
                <button class="icon-btn" @click="viewServer(server)" title="Detay">
                  <Eye :size="15" />
                </button>
                <button
                  v-if="!server.is_online"
                  class="icon-btn success"
                  @click="startServer(server)"
                  :disabled="actionLoading[server.id]"
                  title="Başlat"
                >
                  <Play :size="15" />
                </button>
                <button
                  v-else
                  class="icon-btn warning"
                  @click="stopServer(server)"
                  :disabled="actionLoading[server.id]"
                  title="Durdur"
                >
                  <Square :size="15" />
                </button>
                <button
                  class="icon-btn"
                  @click="restartServer(server)"
                  :disabled="actionLoading[server.id] || !server.is_online"
                  title="Yeniden Başlat"
                >
                  <RotateCcw :size="15" />
                </button>
                <button class="icon-btn danger" @click="confirmDelete(server)" title="Sil">
                  <Trash2 :size="15" />
                </button>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </section>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination-section">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="goToPage(1)"
        >
          <ChevronsLeft :size="18" />
        </button>
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <ChevronLeft :size="18" />
        </button>

        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-num"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </div>

        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          <ChevronRight :size="18" />
        </button>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(totalPages)"
        >
          <ChevronsRight :size="18" />
        </button>

        <span class="page-info">
          {{ currentPage }} / {{ totalPages }} sayfa ({{ totalServers }} sunucu)
        </span>
      </div>

      <!-- Server Detail Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="selectedServer" class="modal-overlay" @click.self="closeModal">
            <div class="modal-container">
              <div class="modal-header">
                <div class="modal-title-section">
                  <div class="modal-status" :class="selectedServer.is_online ? 'online' : 'offline'">
                    <Server :size="20" />
                  </div>
                  <div>
                    <h2 class="modal-title">{{ selectedServer.name }}</h2>
                    <code class="modal-address">{{ selectedServer.ip }}:{{ selectedServer.port }}</code>
                  </div>
                </div>
                <button class="modal-close" @click="closeModal">
                  <X :size="22" />
                </button>
              </div>

              <div class="modal-body">
                <!-- Server Info Grid -->
                <div class="detail-grid">
                  <div class="detail-card">
                    <Gamepad2 :size="18" class="detail-icon" />
                    <div class="detail-content">
                      <span class="detail-label">Oyun</span>
                      <span class="detail-value">{{ getGameLabel(selectedServer.game_type) }}</span>
                    </div>
                  </div>

                  <div class="detail-card">
                    <Map :size="18" class="detail-icon" />
                    <div class="detail-content">
                      <span class="detail-label">Harita</span>
                      <span class="detail-value">{{ selectedServer.map || 'N/A' }}</span>
                    </div>
                  </div>

                  <div class="detail-card">
                    <Users :size="18" class="detail-icon" />
                    <div class="detail-content">
                      <span class="detail-label">Oyuncular</span>
                      <span class="detail-value">{{ selectedServer.players || 0 }}/{{ selectedServer.max_players || 0 }}</span>
                    </div>
                  </div>

                  <div class="detail-card">
                    <User :size="18" class="detail-icon" />
                    <div class="detail-content">
                      <span class="detail-label">Sahip</span>
                      <span class="detail-value">{{ selectedServer.owner?.username || 'N/A' }}</span>
                    </div>
                  </div>

                  <div class="detail-card">
                    <Calendar :size="18" class="detail-icon" />
                    <div class="detail-content">
                      <span class="detail-label">Oluşturulma</span>
                      <span class="detail-value">{{ formatDate(selectedServer.created_at) }}</span>
                    </div>
                  </div>

                  <div class="detail-card">
                    <Clock :size="18" class="detail-icon" />
                    <div class="detail-content">
                      <span class="detail-label">Son Sorgu</span>
                      <span class="detail-value">{{ formatDate(selectedServer.last_query) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Resource Usage -->
                <div v-if="selectedServer.is_online && selectedServer.resources" class="modal-resources">
                  <h4 class="section-title">
                    <Activity :size="16" />
                    Kaynak Kullanımi
                  </h4>
                  <div class="resource-grid">
                    <div class="resource-card">
                      <div class="resource-icon cpu">
                        <Cpu :size="20" />
                      </div>
                      <div class="resource-info">
                        <span class="resource-name">CPU</span>
                        <span class="resource-percent">{{ selectedServer.resources.cpu || 0 }}%</span>
                      </div>
                      <div class="resource-bar-large">
                        <div
                          class="bar-fill"
                          :style="{ width: `${selectedServer.resources.cpu || 0}%` }"
                          :class="getResourceClass(selectedServer.resources.cpu)"
                        ></div>
                      </div>
                    </div>

                    <div class="resource-card">
                      <div class="resource-icon ram">
                        <MemoryStick :size="20" />
                      </div>
                      <div class="resource-info">
                        <span class="resource-name">RAM</span>
                        <span class="resource-percent">{{ selectedServer.resources.ram || 0 }}%</span>
                      </div>
                      <div class="resource-bar-large">
                        <div
                          class="bar-fill"
                          :style="{ width: `${selectedServer.resources.ram || 0}%` }"
                          :class="getResourceClass(selectedServer.resources.ram)"
                        ></div>
                      </div>
                    </div>

                    <div class="resource-card">
                      <div class="resource-icon disk">
                        <HardDrive :size="20" />
                      </div>
                      <div class="resource-info">
                        <span class="resource-name">Disk</span>
                        <span class="resource-percent">{{ selectedServer.resources.disk || 0 }}%</span>
                      </div>
                      <div class="resource-bar-large">
                        <div
                          class="bar-fill"
                          :style="{ width: `${selectedServer.resources.disk || 0}%` }"
                          :class="getResourceClass(selectedServer.resources.disk)"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Players List -->
                <div v-if="selectedServer.player_list && selectedServer.player_list.length > 0" class="modal-players">
                  <h4 class="section-title">
                    <Users :size="16" />
                    Aktif Oyuncular ({{ selectedServer.player_list.length }})
                  </h4>
                  <div class="players-grid">
                    <div v-for="player in selectedServer.player_list" :key="player.name" class="player-card">
                      <div class="player-info">
                        <span class="player-name">{{ player.name }}</span>
                        <span class="player-duration" v-if="player.duration">{{ formatDuration(player.duration) }}</span>
                      </div>
                      <div class="player-score">
                        <Trophy :size="12" />
                        {{ player.score }} puan
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn btn-ghost" @click="copyConnect">
                  <Copy :size="16" />
                  Bağlantı Kopyala
                </button>
                <div class="footer-actions">
                  <button
                    v-if="!selectedServer.is_online"
                    class="btn btn-success"
                    @click="startServer(selectedServer)"
                    :disabled="actionLoading[selectedServer.id]"
                  >
                    <Play :size="16" />
                    Başlat
                  </button>
                  <button
                    v-else
                    class="btn btn-warning"
                    @click="stopServer(selectedServer)"
                    :disabled="actionLoading[selectedServer.id]"
                  >
                    <Square :size="16" />
                    Durdur
                  </button>
                  <button
                    class="btn btn-primary"
                    @click="restartServer(selectedServer)"
                    :disabled="actionLoading[selectedServer.id] || !selectedServer.is_online"
                  >
                    <RotateCcw :size="16" />
                    Yeniden Başlat
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Delete Confirmation Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="deleteTarget" class="modal-overlay" @click.self="cancelDelete">
            <div class="confirm-modal">
              <div class="confirm-icon">
                <AlertTriangle :size="48" />
              </div>
              <h3 class="confirm-title">Sunucuyu Sil</h3>
              <p class="confirm-message">
                <strong>{{ deleteTarget.name }}</strong> sunucusunu silmek istediğinize emin misiniz?
                Bu işlem geri alınamaz!
              </p>
              <div class="confirm-actions">
                <button class="btn btn-ghost" @click="cancelDelete">İptal</button>
                <button class="btn btn-danger" @click="executeDelete" :disabled="deleteLoading">
                  <Trash2 v-if="!deleteLoading" :size="16" />
                  <Loader2 v-else :size="16" class="spin" />
                  Evet, Sil
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Toast Notifications -->
      <div class="toast-container">
        <TransitionGroup name="toast">
          <div
            v-for="toast in toasts"
            :key="toast.id"
            class="toast"
            :class="toast.type"
          >
            <CheckCircle v-if="toast.type === 'success'" :size="18" />
            <AlertCircle v-else-if="toast.type === 'error'" :size="18" />
            <Info v-else :size="18" />
            <span>{{ toast.message }}</span>
          </div>
        </TransitionGroup>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { adminApi, api } from '@/services/api'
import { useUIStore } from '@/stores/ui'
import {
  Search,
  RefreshCw,
  Server,
  ServerOff,
  Wifi,
  WifiOff,
  Users,
  User,
  Eye,
  RotateCcw,
  Trash2,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Loader2,
  X,
  Copy,
  Play,
  Square,
  Map,
  Globe,
  Cpu,
  MemoryStick,
  HardDrive,
  LayoutGrid,
  List,
  Gamepad2,
  Activity,
  Calendar,
  Clock,
  Trophy,
  AlertTriangle,
  CheckCircle,
  AlertCircle,
  Info,
  Hash
} from 'lucide-vue-next'
import { format, formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

const uiStore = useUIStore()

// State
const loading = ref(false)
const refreshing = ref(false)
const servers = ref([])
const totalServers = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 12

const searchQuery = ref('')
const filterGame = ref('')
const filterStatus = ref('')
const viewMode = ref('grid')
const steamIdSearch = ref('')
const steamSearching = ref(false)
const steamSearchResult = ref(null)

const selectedServer = ref(null)
const deleteTarget = ref(null)
const deleteLoading = ref(false)
const actionLoading = reactive({})
const toasts = ref([])

let searchTimeout = null
let refreshInterval = null

// Computed
const onlineCount = computed(() => servers.value.filter(s => s.is_online).length)
const offlineCount = computed(() => servers.value.filter(s => !s.is_online).length)
const totalPlayers = computed(() => servers.value.reduce((sum, s) => sum + (s.players || 0), 0))

const filteredServers = computed(() => {
  let result = [...servers.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      s.name?.toLowerCase().includes(query) ||
      s.map?.toLowerCase().includes(query) ||
      s.owner?.username?.toLowerCase().includes(query) ||
      `${s.ip}:${s.port}`.includes(query)
    )
  }

  return result
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// Methods
const fetchServers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: perPage
    }

    if (filterGame.value) params.game_type = filterGame.value
    if (filterStatus.value) params.status = filterStatus.value

    const data = await adminApi.getServers(params)

    servers.value = (data.servers || []).map(s => ({
      ...s,
      is_online: s.status === 'running',
      players: s.current_players || 0,
      max_players: s.slots || 32,
      map: s.current_map || 'N/A',
      resources: s.resources || null
    }))

    totalServers.value = data.pagination?.total || data.total || servers.value.length
    totalPages.value = data.pagination?.pages || Math.ceil(totalServers.value / perPage) || 1
  } catch (error) {
    // Error handled
    showToast('Sunucular yüklenirken hata oluştu', 'error')
  }
  loading.value = false
}

const refreshServers = async () => {
  refreshing.value = true
  await fetchServers()
  setTimeout(() => {
    refreshing.value = false
  }, 500)
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchServers()
  }, 300)
}

const clearSearch = () => {
  searchQuery.value = ''
  fetchServers()
}

const searchBySteamId = async () => {
  if (!steamIdSearch.value) return
  steamSearching.value = true
  try {
    const response = await api.get(`/v2/servers/search/steam/${encodeURIComponent(steamIdSearch.value)}`)
    steamSearchResult.value = response.data
    if (response.data.servers && response.data.servers.length > 0) {
      // Filter servers by the found ones
      servers.value = response.data.servers.map(s => ({
        ...s,
        is_online: s.status === 'running',
        players: s.current_players,
        owner_username: response.data.owner?.username || 'Bilinmiyor',
        owner_steam_id: response.data.steam_id
      }))
      addToast(`${response.data.server_count} sunucu bulundu (${response.data.owner?.username || 'Bilinmiyor'})`, 'success')
    } else {
      addToast('Bu Steam ID ile sunucu bulunamadi', 'warning')
    }
  } catch (error) {
    console.error('Steam search error:', error)
    addToast(error.response?.data?.detail || 'Arama basarisiz', 'error')
  } finally {
    steamSearching.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  fetchServers()
}

const clearAllFilters = () => {
  searchQuery.value = ''
  filterGame.value = ''
  filterStatus.value = ''
  fetchServers()
}

const goToPage = (page) => {
  currentPage.value = page
  fetchServers()
}

const getUserAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}&backgroundColor=ff6b00&textColor=ffffff`
}

const getGameLabel = (game) => {
  const labels = {
    hldm: 'Half-Life',
    ag: 'Half-Life AG',
    cs16: 'CS 1.6'
  }
  return labels[game] || game || 'Unknown'
}

const getMapThumbnail = (mapName) => {
  if (!mapName || mapName === 'N/A') return '/static/maps/default.jpg'
  // Common map thumbnails - can be extended or connected to a map image service
  return `/static/maps/${mapName}.jpg`
}

const handleImageError = (e) => {
  e.target.src = '/static/maps/default.jpg'
}

const getPlayerBadgeClass = (server) => {
  if (!server.max_players) return ''
  const ratio = (server.players || 0) / server.max_players
  if (ratio >= 1) return 'full'
  if (ratio >= 0.7) return 'high'
  if (ratio >= 0.3) return 'medium'
  return 'low'
}

const getResourceClass = (value) => {
  if (value >= 90) return 'critical'
  if (value >= 70) return 'warning'
  return 'normal'
}

const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy HH:mm', { locale: tr })
}

const formatDuration = (seconds) => {
  if (!seconds) return ''
  const mins = Math.floor(seconds / 60)
  const hours = Math.floor(mins / 60)
  if (hours > 0) return `${hours}s ${mins % 60}dk`
  return `${mins}dk`
}

// Server Actions
const viewServer = (server) => {
  selectedServer.value = server
}

const closeModal = () => {
  selectedServer.value = null
}

const startServer = async (server) => {
  actionLoading[server.id] = true
  try {
    await adminApi.restartServer(server.id) // Using restart as start since API uses same endpoint
    showToast(`${server.name} başlatılıyor...`, 'success')
    await fetchServers()
  } catch (error) {
    // Error handled
    showToast('Sunucu başlatilirken hata oluştu', 'error')
  }
  actionLoading[server.id] = false
}

const stopServer = async (server) => {
  actionLoading[server.id] = true
  try {
    await adminApi.stopServer(server.id)
    showToast(`${server.name} durduruluyor...`, 'success')
    await fetchServers()
  } catch (error) {
    // Error handled
    showToast('Sunucu durdurulurken hata oluştu', 'error')
  }
  actionLoading[server.id] = false
}

const restartServer = async (server) => {
  actionLoading[server.id] = true
  try {
    await adminApi.restartServer(server.id)
    showToast(`${server.name} yeniden başlatılıyor...`, 'success')
    await fetchServers()
  } catch (error) {
    // Error handled
    showToast('Sunucu yeniden başlatilirken hata oluştu', 'error')
  }
  actionLoading[server.id] = false
}

const confirmDelete = (server) => {
  deleteTarget.value = server
}

const cancelDelete = () => {
  deleteTarget.value = null
}

const executeDelete = async () => {
  if (!deleteTarget.value) return

  deleteLoading.value = true
  try {
    await adminApi.deleteServer(deleteTarget.value.id)
    servers.value = servers.value.filter(s => s.id !== deleteTarget.value.id)
    totalServers.value--
    showToast(`${deleteTarget.value.name} silindi`, 'success')
    deleteTarget.value = null
  } catch (error) {
    // Error handled
    showToast('Sunucu silinirken hata oluştu', 'error')
  }
  deleteLoading.value = false
}

const copyConnect = () => {
  if (selectedServer.value) {
    navigator.clipboard.writeText(`connect ${selectedServer.value.ip}:${selectedServer.value.port}`)
    showToast('Bağlantı adresi kopyalandi!', 'success')
  }
}

// Toast System
const showToast = (message, type = 'info') => {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 4000)
}

// Lifecycle
onMounted(() => {
  fetchServers()
  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(fetchServers, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<style scoped>
/* ===== Base Variables & Theme ===== */
.servers-page {
  --accent: #ff6b00;
  --accent-light: #ff8533;
  --accent-dark: #cc5500;
  --accent-glow: rgba(255, 107, 0, 0.3);

  --bg-primary: #0a0a0b;
  --bg-secondary: #111113;
  --bg-tertiary: #18181b;
  --bg-elevated: #1f1f23;

  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-default: rgba(255, 255, 255, 0.1);
  --border-strong: rgba(255, 255, 255, 0.15);

  --text-primary: #fafafa;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;

  --success: #22c55e;
  --success-bg: rgba(34, 197, 94, 0.1);
  --warning: #f59e0b;
  --warning-bg: rgba(245, 158, 11, 0.1);
  --danger: #ef4444;
  --danger-bg: rgba(239, 68, 68, 0.1);

  max-width: 1600px;
  margin: 0 auto;
  padding: 0 24px 40px;
}

/* ===== Page Header ===== */
.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.title-icon {
  color: var(--accent);
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 15px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* ===== Buttons ===== */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-light);
  box-shadow: 0 4px 20px var(--accent-glow);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-elevated);
  border-color: var(--border-strong);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-success {
  background: var(--success);
  color: #fff;
}

.btn-success:hover:not(:disabled) {
  background: #16a34a;
}

.btn-warning {
  background: var(--warning);
  color: #fff;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}

.btn-danger {
  background: var(--danger);
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

/* ===== Stats Section ===== */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: var(--border-default);
  transform: translateY(-2px);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.stat-card.total .stat-icon {
  background: rgba(255, 107, 0, 0.1);
  color: var(--accent);
}

.stat-card.online .stat-icon {
  background: var(--success-bg);
  color: var(--success);
}

.stat-card.offline .stat-icon {
  background: var(--danger-bg);
  color: var(--danger);
}

.stat-card.players .stat-icon {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.stat-indicator {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
}

.stat-indicator.pulse {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  50% { opacity: 0.8; box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
}

/* ===== Controls Section ===== */
.controls-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-wrapper {
  flex: 1;
  min-width: 280px;
  position: relative;
  display: flex;
  align-items: center;
}

.steam-search-wrapper {
  display: flex;
  align-items: center;
  position: relative;
  min-width: 300px;
  gap: 8px;
}

.steam-search-wrapper .search-icon {
  position: absolute;
  left: 14px;
  color: var(--text-muted);
  pointer-events: none;
}

.steam-search-wrapper .steam-input {
  padding-left: 40px;
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
}

.steam-search-wrapper .steam-input:focus {
  border-color: var(--orange);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.btn-sm {
  padding: 8px 12px;
  font-size: 13px;
}

.search-icon {
  position: absolute;
  left: 14px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 44px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-shortcut {
  position: absolute;
  right: 14px;
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-muted);
}

.search-clear {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-clear:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.filter-group {
  display: flex;
  gap: 12px;
}

.filter-item {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  pointer-events: none;
  z-index: 1;
}

.filter-select {
  padding: 12px 16px 12px 38px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%2371717a' viewBox='0 0 16 16'%3E%3Cpath d='M4.5 6l3.5 4 3.5-4h-7z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.filter-select:hover {
  border-color: var(--border-default);
}

.filter-select:focus {
  outline: none;
  border-color: var(--accent);
}

.view-toggle {
  display: flex;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  overflow: hidden;
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.toggle-btn.active {
  color: var(--accent);
  background: rgba(255, 107, 0, 0.1);
}

/* ===== Loading State ===== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.loading-spinner {
  color: var(--accent);
}

.loading-text {
  color: var(--text-secondary);
  font-size: 15px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== Empty State ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 20px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.empty-description {
  color: var(--text-secondary);
  margin: 0 0 24px;
  max-width: 400px;
}

/* ===== Server Grid ===== */
.servers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.server-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.server-card:hover {
  border-color: var(--border-default);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.server-card.is-online {
  border-color: rgba(34, 197, 94, 0.2);
}

.server-card.is-online:hover {
  border-color: rgba(34, 197, 94, 0.4);
}

/* Card Thumbnail */
.card-thumbnail {
  position: relative;
  height: 140px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.map-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.server-card:hover .map-image {
  transform: scale(1.05);
}

.map-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--text-muted);
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-elevated) 100%);
}

.status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  backdrop-filter: blur(8px);
}

.status-badge.online {
  background: rgba(34, 197, 94, 0.9);
  color: #fff;
}

.status-badge.offline {
  background: rgba(113, 113, 122, 0.9);
  color: #fff;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.status-badge.online .status-dot {
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.game-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Card Content */
.card-content {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.server-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}

.player-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.player-badge.full {
  background: var(--success-bg);
  color: var(--success);
}

.player-badge.high {
  background: var(--warning-bg);
  color: var(--warning);
}

.player-badge.medium {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.server-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.info-row svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.server-address {
  font-size: 12px;
  background: var(--bg-tertiary);
  padding: 4px 8px;
  border-radius: 6px;
  color: var(--text-muted);
}

/* Resource Bars */
.resource-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
  padding: 14px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.resource-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.resource-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-muted);
}

.resource-value {
  margin-left: auto;
  font-weight: 500;
  color: var(--text-secondary);
}

.resource-bar {
  height: 4px;
  background: var(--bg-elevated);
  border-radius: 2px;
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.resource-fill.normal {
  background: var(--success);
}

.resource-fill.warning {
  background: var(--warning);
}

.resource-fill.critical {
  background: var(--danger);
}

/* Owner Info */
.owner-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid var(--border-subtle);
}

.owner-avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
}

.owner-name {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Card Actions */
.card-actions {
  display: flex;
  gap: 8px;
  padding: 16px 20px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-subtle);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  border-color: var(--border-default);
  color: var(--text-primary);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-btn.view:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}

.action-btn.start:hover:not(:disabled) {
  background: var(--success-bg);
  border-color: rgba(34, 197, 94, 0.3);
  color: var(--success);
}

.action-btn.stop:hover:not(:disabled) {
  background: var(--warning-bg);
  border-color: rgba(245, 158, 11, 0.3);
  color: var(--warning);
}

.action-btn.restart:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: #8b5cf6;
}

.action-btn.delete:hover:not(:disabled) {
  background: var(--danger-bg);
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--danger);
}

/* ===== List View ===== */
.servers-list {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 60px 2fr 100px 140px 100px 140px 100px 160px;
  gap: 16px;
  padding: 14px 20px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.list-row {
  display: grid;
  grid-template-columns: 60px 2fr 100px 140px 100px 140px 100px 160px;
  gap: 16px;
  padding: 16px 20px;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle);
  transition: background 0.2s ease;
}

.list-row:last-child {
  border-bottom: none;
}

.list-row:hover {
  background: var(--bg-tertiary);
}

.list-row.is-online {
  background: rgba(34, 197, 94, 0.02);
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
}

.indicator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--text-muted);
}

.status-indicator.online .indicator-dot {
  background: var(--success);
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
  animation: pulse 2s ease-in-out infinite;
}

.status-indicator.offline .indicator-dot {
  background: var(--text-muted);
}

.server-title {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.server-addr {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}

.game-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
}

.game-badge.hldm {
  background: rgba(255, 107, 0, 0.15);
  color: var(--accent);
}

.game-badge.ag {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.game-badge.cs16 {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.map-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.map-thumb {
  width: 32px;
  height: 24px;
  border-radius: 4px;
  object-fit: cover;
}

.players-display {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.owner-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.owner-thumb {
  width: 24px;
  height: 24px;
  border-radius: 6px;
}

.no-owner,
.no-resources {
  color: var(--text-muted);
}

.mini-resources {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mini-bar {
  width: 60px;
  height: 4px;
  background: var(--bg-elevated);
  border-radius: 2px;
  overflow: hidden;
}

.mini-fill {
  height: 100%;
  border-radius: 2px;
}

.action-group {
  display: flex;
  gap: 6px;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-btn:hover:not(:disabled) {
  background: var(--bg-elevated);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.icon-btn.success:hover:not(:disabled) {
  background: var(--success-bg);
  border-color: rgba(34, 197, 94, 0.3);
  color: var(--success);
}

.icon-btn.warning:hover:not(:disabled) {
  background: var(--warning-bg);
  border-color: rgba(245, 158, 11, 0.3);
  color: var(--warning);
}

.icon-btn.danger:hover:not(:disabled) {
  background: var(--danger-bg);
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--danger);
}

/* ===== Pagination ===== */
.pagination-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 32px;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-num:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.page-num.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

.page-info {
  margin-left: 16px;
  font-size: 13px;
  color: var(--text-muted);
}

/* ===== Modal ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-status {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
}

.modal-status.online {
  background: var(--success-bg);
  color: var(--success);
}

.modal-status.offline {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.modal-address {
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 4px 10px;
  border-radius: 6px;
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 10px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.detail-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.detail-icon {
  color: var(--accent);
}

.detail-content {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-top: 2px;
}

.modal-resources {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.resource-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.resource-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
}

.resource-icon.cpu {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.resource-icon.ram {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.resource-icon.disk {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.resource-info {
  display: flex;
  flex-direction: column;
  min-width: 60px;
}

.resource-name {
  font-size: 12px;
  color: var(--text-muted);
}

.resource-percent {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.resource-bar-large {
  flex: 1;
  height: 8px;
  background: var(--bg-elevated);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.modal-players {
  margin-bottom: 16px;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.player-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.player-info {
  display: flex;
  flex-direction: column;
}

.player-name {
  font-weight: 500;
  color: var(--text-primary);
}

.player-duration {
  font-size: 11px;
  color: var(--text-muted);
}

.player-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--warning);
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-tertiary);
}

.footer-actions {
  display: flex;
  gap: 10px;
}

/* ===== Confirm Modal ===== */
.confirm-modal {
  width: 100%;
  max-width: 400px;
  padding: 32px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  text-align: center;
}

.confirm-icon {
  color: var(--danger);
  margin-bottom: 16px;
}

.confirm-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.confirm-message {
  color: var(--text-secondary);
  margin: 0 0 28px;
  line-height: 1.6;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.confirm-actions .btn {
  min-width: 120px;
}

/* ===== Toast Notifications ===== */
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1100;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  color: var(--text-primary);
  font-size: 14px;
}

.toast.success {
  border-color: rgba(34, 197, 94, 0.3);
  color: var(--success);
}

.toast.error {
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--danger);
}

/* ===== Animations ===== */
.card-enter-active,
.card-leave-active {
  transition: all 0.3s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.card-leave-to {
  opacity: 0;
  transform: scale(0.95);
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

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-enter-from .confirm-modal,
.modal-leave-to .modal-container,
.modal-leave-to .confirm-modal {
  transform: scale(0.95) translateY(20px);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* ===== Responsive ===== */
@media (max-width: 1200px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .list-header,
  .list-row {
    grid-template-columns: 50px 1.5fr 90px 1fr 90px 1fr 160px;
  }

  .col-resources {
    display: none;
  }
}

@media (max-width: 900px) {
  .servers-page {
    padding: 0 16px 32px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    min-width: 100%;
  }

  .filter-group {
    flex-wrap: wrap;
  }

  .servers-grid {
    grid-template-columns: 1fr;
  }

  .servers-list {
    display: none;
  }

  .detail-grid,
  .players-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 22px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 24px;
  }

  .modal-container {
    max-height: 95vh;
    border-radius: 16px 16px 0 0;
  }

  .modal-footer {
    flex-direction: column;
    gap: 12px;
  }

  .footer-actions {
    width: 100%;
  }

  .footer-actions .btn {
    flex: 1;
  }

  .pagination-section {
    flex-wrap: wrap;
  }

  .page-info {
    width: 100%;
    text-align: center;
    margin: 12px 0 0;
  }
}
</style>
