<template>
  <AdminLayout>
    <div class="admin-servers">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Sunucu Yönetimi</h1>
          <p class="subtitle">{{ onlineCount }} aktif / {{ totalServers }} toplam</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="refreshServers">
            <RefreshCw :size="18" :class="{ spin: refreshing }" />
            <span>Yenile</span>
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-row">
        <div class="mini-stat">
          <Server :size="20" />
          <div>
            <span class="stat-value">{{ totalServers }}</span>
            <span class="stat-label">Toplam Sunucu</span>
          </div>
        </div>
        <div class="mini-stat online">
          <Wifi :size="20" />
          <div>
            <span class="stat-value">{{ onlineCount }}</span>
            <span class="stat-label">Online</span>
          </div>
        </div>
        <div class="mini-stat offline">
          <WifiOff :size="20" />
          <div>
            <span class="stat-value">{{ offlineCount }}</span>
            <span class="stat-label">Offline</span>
          </div>
        </div>
        <div class="mini-stat">
          <Users :size="20" />
          <div>
            <span class="stat-value">{{ totalPlayers }}</span>
            <span class="stat-label">Toplam Oyuncu</span>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Sunucu veya sahip ara..."
            @input="debouncedSearch"
          />
        </div>
        <select v-model="filterGame" class="filter-select" @change="fetchServers">
          <option value="">Tüm Oyunlar</option>
          <option value="hldm">Half-Life</option>
          <option value="ag">Half-Life AG</option>
          <option value="cs16">Counter-Strike 1.6</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="fetchServers">
          <option value="">Tüm Durumlar</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
        </select>
      </div>

      <!-- Servers Table -->
      <div class="table-container">
        <div v-if="loading" class="loading-state">
          <Loader2 :size="32" class="spin" />
          <span>Yükleniyor...</span>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Durum</th>
              <th>Sunucu</th>
              <th>Oyun</th>
              <th>Sahip</th>
              <th>Oyuncular</th>
              <th>Adres</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="server in servers" :key="server.id">
              <td>
                <span class="status-dot" :class="server.is_online ? 'online' : 'offline'"></span>
              </td>
              <td>
                <div class="server-cell">
                  <span class="server-name">{{ server.name }}</span>
                  <span class="server-map">{{ server.map || 'N/A' }}</span>
                </div>
              </td>
              <td>
                <span class="game-badge" :class="server.game_type">
                  {{ getGameLabel(server.game_type) }}
                </span>
              </td>
              <td>
                <div class="user-cell" v-if="server.owner">
                  <img :src="getUserAvatar(server.owner.username)" class="avatar-sm" />
                  <span>{{ server.owner.username }}</span>
                </div>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span class="player-count" :class="{ full: server.players >= server.max_players }">
                  {{ server.players || 0 }}/{{ server.max_players || 0 }}
                </span>
              </td>
              <td>
                <code class="server-address">{{ server.ip }}:{{ server.port }}</code>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-icon" @click="viewServer(server)" title="Detay">
                    <Eye :size="16" />
                  </button>
                  <button class="btn-icon" @click="restartServer(server)" title="Yeniden Başlat">
                    <RotateCcw :size="16" />
                  </button>
                  <button class="btn-icon danger" @click="deleteServer(server)" title="Sil">
                    <Trash2 :size="16" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="servers.length === 0">
              <td colspan="7" class="empty-state">
                <ServerOff :size="48" />
                <p>Sunucu bulunamadı</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="btn btn-secondary"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <ChevronLeft :size="18" />
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="btn btn-secondary"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          <ChevronRight :size="18" />
        </button>
      </div>

      <!-- Server Detail Modal -->
      <div v-if="selectedServer" class="modal-overlay" @click.self="closeModal">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h3>Sunucu Detayı</h3>
            <button class="btn-icon" @click="closeModal">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="server-detail-header">
              <div class="server-status-large" :class="selectedServer.is_online ? 'online' : 'offline'">
                <Server :size="24" />
              </div>
              <div>
                <h4>{{ selectedServer.name }}</h4>
                <code>{{ selectedServer.ip }}:{{ selectedServer.port }}</code>
              </div>
            </div>

            <div class="detail-grid">
              <div class="detail-item">
                <span class="label">Oyun</span>
                <span class="value">{{ getGameLabel(selectedServer.game_type) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Harita</span>
                <span class="value">{{ selectedServer.map || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Oyuncular</span>
                <span class="value">{{ selectedServer.players }}/{{ selectedServer.max_players }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Sahip</span>
                <span class="value">{{ selectedServer.owner?.username || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Oluşturulma</span>
                <span class="value">{{ formatDate(selectedServer.created_at) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Son Sorgu</span>
                <span class="value">{{ formatDate(selectedServer.last_query) }}</span>
              </div>
            </div>

            <div v-if="selectedServer.players > 0" class="players-section">
              <h5>Oyuncular</h5>
              <div class="players-list">
                <div v-for="player in selectedServer.player_list" :key="player.name" class="player-item">
                  <span class="player-name">{{ player.name }}</span>
                  <span class="player-score">{{ player.score }} puan</span>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="copyConnect">
              <Copy :size="16" />
              Bağlantı Kopyala
            </button>
            <button class="btn btn-primary" @click="restartServer(selectedServer)">
              <RotateCcw :size="16" />
              Yeniden Başlat
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Search,
  RefreshCw,
  Server,
  ServerOff,
  Wifi,
  WifiOff,
  Users,
  Eye,
  RotateCcw,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Loader2,
  X,
  Copy
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()
const loading = ref(false)
const refreshing = ref(false)
const servers = ref([])
const totalServers = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 20

const searchQuery = ref('')
const filterGame = ref('')
const filterStatus = ref('')

const selectedServer = ref(null)

let searchTimeout = null

// Get CSRF token from cookie
const getCsrfToken = () => {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrf_token') return value
  }
  return null
}

const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authStore.token}`
  }
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }
  return headers
}

const onlineCount = computed(() => servers.value.filter(s => s.is_online || s.status === 'running').length)
const offlineCount = computed(() => servers.value.filter(s => !s.is_online && s.status !== 'running').length)
const totalPlayers = computed(() => servers.value.reduce((sum, s) => sum + (s.players || s.current_players || 0), 0))

const fetchServers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: perPage
    })

    if (filterGame.value) params.append('game_type', filterGame.value)
    if (filterStatus.value) params.append('status', filterStatus.value)

    const response = await fetch(`/api/admin/servers?${params}`, {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      // Map API response to frontend expected format
      servers.value = (data.servers || []).map(s => ({
        ...s,
        is_online: s.status === 'running',
        players: s.current_players || 0,
        max_players: s.slots || 32,
        map: s.current_map || 'N/A'
      }))
      totalServers.value = data.pagination?.total || 0
      totalPages.value = data.pagination?.pages || 1
    }
  } catch (error) {
    console.error('Fetch servers error:', error)
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

const goToPage = (page) => {
  currentPage.value = page
  fetchServers()
}

const getUserAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}`
}

const getGameLabel = (game) => {
  const labels = {
    hldm: 'Half-Life',
    ag: 'Half-Life AG',
    cs16: 'CS 1.6'
  }
  return labels[game] || game
}

const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy HH:mm', { locale: tr })
}

const viewServer = (server) => {
  selectedServer.value = server
}

const closeModal = () => {
  selectedServer.value = null
}

const restartServer = async (server) => {
  if (!confirm(`${server.name} sunucusunu yeniden başlatmak istediğinize emin misiniz?`)) return

  try {
    const response = await fetch(`/api/admin/servers/${server.id}/restart`, {
      method: 'POST',
      headers: getHeaders()
    })
    if (response.ok) {
      alert('Sunucu yeniden başlatılıyor...')
    }
  } catch (error) {
    console.error('Restart server error:', error)
  }
}

const deleteServer = async (server) => {
  if (!confirm(`${server.name} sunucusunu silmek istediğinize emin misiniz? Bu işlem geri alınamaz!`)) return

  try {
    const response = await fetch(`/api/admin/servers/${server.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (response.ok) {
      servers.value = servers.value.filter(s => s.id !== server.id)
      totalServers.value--
    }
  } catch (error) {
    console.error('Delete server error:', error)
  }
}

const copyConnect = () => {
  if (selectedServer.value) {
    navigator.clipboard.writeText(`connect ${selectedServer.value.ip}:${selectedServer.value.port}`)
    alert('Bağlantı kopyalandı!')
  }
}

onMounted(() => {
  fetchServers()
})
</script>

<style scoped>
.admin-servers {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.subtitle {
  color: var(--text-secondary);
  margin: 4px 0 0;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.mini-stat svg {
  color: var(--text-secondary);
}

.mini-stat.online svg {
  color: var(--success-color, #10b981);
}

.mini-stat.offline svg {
  color: var(--error-color, #ef4444);
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Buttons */
.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: var(--primary-color);
  color: var(--bg-primary);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn:hover {
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Filters */
.filters-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0 14px;
}

.search-box input {
  flex: 1;
  background: none;
  border: none;
  padding: 12px 0;
  color: var(--text-primary);
  font-size: 14px;
}

.search-box input::placeholder {
  color: var(--text-muted);
}

.search-box svg {
  color: var(--text-muted);
}

.filter-select {
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
}

/* Table */
.table-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-secondary);
  gap: 12px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 16px 20px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover td {
  background: var(--bg-tertiary);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.online {
  background: var(--success-color, #10b981);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-dot.offline {
  background: var(--text-muted, #6b7280);
}

.server-cell {
  display: flex;
  flex-direction: column;
}

.server-name {
  font-weight: 500;
}

.server-map {
  font-size: 12px;
  color: var(--text-secondary);
}

.game-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.game-badge.hldm {
  background: rgba(255, 107, 0, 0.15);
  color: var(--primary-color, #ff6b00);
}

.game-badge.ag {
  background: rgba(139, 92, 246, 0.15);
  color: var(--secondary-color, #8b5cf6);
}

.game-badge.cs16 {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-color, #3b82f6);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar-sm {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.text-muted {
  color: var(--text-muted);
}

.player-count {
  font-weight: 500;
  color: var(--text-secondary);
}

.player-count.full {
  color: var(--success-color, #10b981);
}

.server-address {
  font-size: 12px;
  background: var(--bg-tertiary);
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

.btn-icon.danger:hover {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color, #ef4444);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-state svg {
  opacity: 0.5;
  margin-bottom: 12px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-info {
  color: var(--text-secondary);
  font-size: 14px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: var(--bg-secondary);
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-lg {
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.server-detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.server-status-large {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.server-status-large.online {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
}

.server-status-large.offline {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted, #6b7280);
}

.server-detail-header h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px;
}

.server-detail-header code {
  font-size: 13px;
  color: var(--text-secondary);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  background: var(--bg-tertiary);
  padding: 12px 16px;
  border-radius: 10px;
}

.detail-item .label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.detail-item .value {
  font-weight: 500;
  color: var(--text-primary);
}

.players-section {
  margin-top: 24px;
}

.players-section h5 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.players-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.player-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.player-name {
  font-weight: 500;
}

.player-score {
  color: var(--text-secondary);
  font-size: 13px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    min-width: 100%;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
