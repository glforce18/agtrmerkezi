<template>
  <AdminLayout>
    <div class="users-page">
      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <Users :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">Toplam Kullanıcı</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <UserCheck :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.active }}</span>
            <span class="stat-label">Aktif</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon banned">
            <Ban :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.banned }}</span>
            <span class="stat-label">Yasaklı</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon new">
            <UserPlus :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.newToday }}</span>
            <span class="stat-label">Bugun Yeni</span>
          </div>
        </div>
      </div>

      <!-- Filters & Actions Bar -->
      <div class="actions-bar">
        <div class="search-filters">
          <div class="search-box">
            <Search :size="18" class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Kullanıcı ara..."
              @input="debouncedSearch"
            />
            <button v-if="searchQuery" class="clear-btn" @click="clearSearch">
              <X :size="16" />
            </button>
          </div>

          <div class="filter-group">
            <button
              class="filter-btn"
              :class="{ active: showFilters }"
              @click="showFilters = !showFilters"
            >
              <Filter :size="18" />
              <span>Filtreler</span>
              <ChevronDown :size="16" :class="{ rotated: showFilters }" />
            </button>
          </div>
        </div>

        <div class="action-buttons">
          <Transition name="fade">
            <div v-if="selectedUsers.length > 0" class="bulk-actions">
              <span class="selected-count">{{ selectedUsers.length }} seçili</span>
              <button class="bulk-btn warning" @click="bulkChangeRole">
                <Shield :size="16" />
                Rol Degistir
              </button>
              <button class="bulk-btn danger" @click="bulkBan">
                <Ban :size="16" />
                Yasakla
              </button>
              <button class="bulk-btn error" @click="bulkDelete">
                <Trash2 :size="16" />
                Sil
              </button>
            </div>
          </Transition>

          <button class="action-btn secondary" @click="exportUsers" :disabled="exporting">
            <Download :size="18" />
            <span>Disa Aktar</span>
          </button>
        </div>
      </div>

      <!-- Advanced Filters Panel -->
      <Transition name="slide-down">
        <div v-if="showFilters" class="filters-panel">
          <div class="filter-item">
            <label>Rol</label>
            <select v-model="filterRole" @change="applyFilters">
              <option value="">Tüm Roller</option>
              <option value="user">Kullanıcı</option>
              <option value="moderatör">Moderatör</option>
              <option value="admin">Admin</option>
              <option value="superadmin">Super Admin</option>
            </select>
          </div>
          <div class="filter-item">
            <label>Durum</label>
            <select v-model="filterStatus" @change="applyFilters">
              <option value="">Tüm Durumlar</option>
              <option value="active">Aktif</option>
              <option value="inactive">Pasif</option>
              <option value="banned">Yasaklı</option>
            </select>
          </div>
          <div class="filter-item">
            <label>Kayıt Tarihi</label>
            <select v-model="filterDate" @change="applyFilters">
              <option value="">Tüm Zamanlar</option>
              <option value="today">Bugun</option>
              <option value="week">Bu Hafta</option>
              <option value="month">Bu Ay</option>
              <option value="year">Bu Yil</option>
            </select>
          </div>
          <button class="clear-filters-btn" @click="clearFilters">
            <RotateCcw :size="16" />
            Temizle
          </button>
        </div>
      </Transition>

      <!-- View Toggle -->
      <div class="view-controls">
        <div class="view-toggle">
          <button
            :class="{ active: viewMode === 'table' }"
            @click="viewMode = 'table'"
            title="Tablo Görünümu"
          >
            <List :size="18" />
          </button>
          <button
            :class="{ active: viewMode === 'cards' }"
            @click="viewMode = 'cards'"
            title="Kart Görünümu"
          >
            <LayoutGrid :size="18" />
          </button>
        </div>
        <div class="results-info">
          <span>{{ totalUsers }} kullanıcıdan {{ users.length }} gösteriliyor</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loader"></div>
        <span>Kullanıcılar yükleniyor...</span>
      </div>

      <!-- Table View -->
      <div v-else-if="viewMode === 'table'" class="users-table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  :indeterminate="someSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th>Kullanıcı</th>
              <th>Bakiye</th>
              <th>Rol</th>
              <th>Durum</th>
              <th>Kayıt Tarihi</th>
              <th class="actions-col">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <TransitionGroup name="table-row">
              <tr
                v-for="user in users"
                :key="user.id"
                :class="{ selected: selectedUsers.includes(user.id) }"
              >
                <td class="checkbox-col">
                  <input
                    type="checkbox"
                    :checked="selectedUsers.includes(user.id)"
                    @change="toggleSelect(user.id)"
                  />
                </td>
                <td>
                  <div class="user-cell">
                    <div class="user-avatar">
                      <img :src="getAvatar(user.username)" :alt="user.username" />
                      <span class="status-dot" :class="user.status"></span>
                    </div>
                    <div class="user-info">
                      <router-link :to="`/user/${user.username}`" class="username username-link" target="_blank">
                        {{ user.username }}
                      </router-link>
                      <span class="email">{{ user.email }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="balance-cell">
                    <span class="tl-balance">{{ formatCurrency(user.balance || 0) }} TL</span>
                    <span class="coin-balance">{{ formatNumber(user.balance_coin || 0) }} Armor</span>
                  </div>
                </td>
                <td>
                  <span class="role-badge" :class="getRoleClass(user.role)">
                    {{ getRoleLabel(user.role) }}
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="user.status">
                    {{ getStatusLabel(user.status) }}
                  </span>
                </td>
                <td class="date-cell">
                  {{ formatDate(user.created_at) }}
                </td>
                <td class="actions-col">
                  <div class="row-actions">
                    <button class="row-action-btn view" @click="viewUser(user)" title="Görüntüle">
                      <Eye :size="16" />
                    </button>
                    <button class="row-action-btn edit" @click="openEditUser(user)" title="Düzenle">
                      <Edit2 :size="16" />
                    </button>
                    <button
                      v-if="user.status !== 'banned'"
                      class="row-action-btn ban"
                      @click="confirmBan(user)"
                      title="Yasakla"
                    >
                      <Ban :size="16" />
                    </button>
                    <button
                      v-else
                      class="row-action-btn unban"
                      @click="confirmUnban(user)"
                      title="Yasagi Kaldır"
                    >
                      <UserCheck :size="16" />
                    </button>
                  </div>
                </td>
              </tr>
            </TransitionGroup>
          </tbody>
        </table>

        <div v-if="users.length === 0 && !loading" class="empty-state">
          <Users :size="48" />
          <h3>Kullanıcı Bulunamadı</h3>
          <p>Arama kriterlerinize uygun kullanıcı yok.</p>
        </div>
      </div>

      <!-- Cards View -->
      <div v-else class="users-cards-container">
        <TransitionGroup name="card-list" tag="div" class="cards-grid">
          <div
            v-for="user in users"
            :key="user.id"
            class="user-card"
            :class="{ selected: selectedUsers.includes(user.id) }"
          >
            <div class="card-header">
              <input
                type="checkbox"
                :checked="selectedUsers.includes(user.id)"
                @change="toggleSelect(user.id)"
              />
              <span class="role-badge" :class="getRoleClass(user.role)">
                {{ getRoleLabel(user.role) }}
              </span>
            </div>

            <div class="card-avatar">
              <img :src="getAvatar(user.username)" :alt="user.username" />
              <span class="status-indicator" :class="user.status"></span>
            </div>

            <div class="card-info">
              <router-link :to="`/user/${user.username}`" class="card-username card-username-link" target="_blank">
                {{ user.username }}
              </router-link>
              <p class="card-email">{{ user.email }}</p>
            </div>

            <div class="card-stats">
              <div class="card-stat">
                <Wallet :size="16" />
                <span>{{ formatCurrency(user.balance || 0) }} TL</span>
              </div>
              <div class="card-stat coin">
                <Shield :size="16" />
                <span>{{ formatNumber(user.balance_coin || 0) }}</span>
              </div>
            </div>

            <div class="card-meta">
              <Calendar :size="14" />
              <span>{{ formatDate(user.created_at) }}</span>
            </div>

            <div class="card-actions">
              <button class="card-action view" @click="viewUser(user)">
                <Eye :size="16" />
                <span>Görüntüle</span>
              </button>
              <button class="card-action edit" @click="openEditUser(user)">
                <Edit2 :size="16" />
                <span>Düzenle</span>
              </button>
              <button
                v-if="user.status !== 'banned'"
                class="card-action ban"
                @click="confirmBan(user)"
              >
                <Ban :size="16" />
              </button>
              <button
                v-else
                class="card-action unban"
                @click="confirmUnban(user)"
              >
                <UserCheck :size="16" />
              </button>
            </div>
          </div>
        </TransitionGroup>

        <div v-if="users.length === 0 && !loading" class="empty-state">
          <Users :size="48" />
          <h3>Kullanıcı Bulunamadı</h3>
          <p>Arama kriterlerinize uygun kullanıcı yok.</p>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-container" v-if="totalUsers > 0">
        <div class="page-size-selector">
          <label>Sayfa basina:</label>
          <select v-model="pageSize" @change="handlePageSizeChange">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>

        <div class="pagination">
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

          <template v-for="page in visiblePages" :key="page">
            <span v-if="page === '...'" class="page-ellipsis">...</span>
            <button
              v-else
              class="page-btn"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </template>

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
        </div>

        <div class="page-info">
          Sayfa {{ currentPage }} / {{ totalPages }}
        </div>
      </div>

      <!-- User Detail/Edit Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal-container">
              <div class="modal-header">
                <h2>{{ editMode ? 'Kullanıcı Düzenle' : 'Kullanıcı Detayi' }}</h2>
                <button class="modal-close" @click="closeModal">
                  <X :size="20" />
                </button>
              </div>

              <div v-if="selectedUser" class="modal-body">
                <div class="modal-user-header">
                  <div class="modal-avatar">
                    <img :src="getAvatar(selectedUser.username)" :alt="selectedUser.username" />
                    <span class="status-indicator large" :class="selectedUser.status"></span>
                  </div>
                  <div class="modal-user-info">
                    <h3>{{ selectedUser.username }}</h3>
                    <span class="role-badge" :class="getRoleClass(selectedUser.role)">
                      {{ getRoleLabel(selectedUser.role) }}
                    </span>
                  </div>
                </div>

                <div class="modal-stats-grid">
                  <div class="modal-stat">
                    <Mail :size="18" />
                    <div>
                      <label>E-posta</label>
                      <span>{{ selectedUser.email }}</span>
                    </div>
                  </div>
                  <div class="modal-stat">
                    <Calendar :size="18" />
                    <div>
                      <label>Kayıt Tarihi</label>
                      <span>{{ formatDate(selectedUser.created_at) }}</span>
                    </div>
                  </div>
                  <div class="modal-stat">
                    <Wallet :size="18" />
                    <div>
                      <label>TL Bakiye</label>
                      <input
                        v-if="editMode"
                        v-model.number="editForm.balance"
                        type="number"
                        step="0.01"
                        min="0"
                        class="modal-input"
                      />
                      <span v-else>{{ formatCurrency(selectedUser.balance || 0) }} TL</span>
                    </div>
                  </div>
                  <div class="modal-stat">
                    <Shield :size="18" />
                    <div>
                      <label>Armor Bakiye</label>
                      <input
                        v-if="editMode"
                        v-model.number="editForm.balance_coin"
                        type="number"
                        step="1"
                        min="0"
                        class="modal-input"
                      />
                      <span v-else>{{ formatNumber(selectedUser.balance_coin || 0) }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="editMode" class="modal-edit-section">
                  <div class="edit-row">
                    <label>Rol</label>
                    <select v-model="editForm.role" class="modal-select">
                      <option value="user">Kullanıcı</option>
                      <option value="moderatör">Moderatör</option>
                      <option value="admin">Admin</option>
                      <option value="superadmin">Super Admin</option>
                    </select>
                  </div>
                  <div class="edit-row">
                    <label>Durum</label>
                    <select v-model="editForm.status" class="modal-select">
                      <option value="active">Aktif</option>
                      <option value="inactive">Pasif</option>
                      <option value="banned">Yasaklı</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button class="modal-btn secondary" @click="closeModal">İptal</button>
                <button
                  v-if="!editMode"
                  class="modal-btn primary"
                  @click="editMode = true"
                >
                  <Edit2 :size="16" />
                  Düzenle
                </button>
                <button
                  v-else
                  class="modal-btn primary"
                  :disabled="saving"
                  @click="saveUser"
                >
                  <Save :size="16" />
                  {{ saving ? 'Kaydediliyor...' : 'Kaydet' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Confirmation Dialog -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showConfirm" class="modal-overlay" @click.self="closeConfirm">
            <div class="confirm-dialog">
              <div class="confirm-icon" :class="confirmType">
                <component :is="confirmIcon" :size="32" />
              </div>
              <h3>{{ confirmTitle }}</h3>
              <p>{{ confirmMessage }}</p>
              <div class="confirm-actions">
                <button class="modal-btn secondary" @click="closeConfirm">İptal</button>
                <button
                  class="modal-btn"
                  :class="confirmType"
                  @click="executeConfirm"
                >
                  {{ confirmButtonText }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Bulk Role Change Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showRoleModal" class="modal-overlay" @click.self="showRoleModal = false">
            <div class="confirm-dialog">
              <div class="confirm-icon warning">
                <Shield :size="32" />
              </div>
              <h3>Toplu Rol Degisikligi</h3>
              <p>{{ selectedUsers.length }} kullanıcı için yeni rol seçin</p>
              <select v-model="bulkRole" class="modal-select">
                <option value="user">Kullanıcı</option>
                <option value="moderatör">Moderatör</option>
                <option value="admin">Admin</option>
              </select>
              <div class="confirm-actions">
                <button class="modal-btn secondary" @click="showRoleModal = false">İptal</button>
                <button class="modal-btn primary" @click="executeBulkRoleChange">
                  Uygula
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, markRaw } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Search, Download, Eye, Edit2, Ban, UserCheck, Mail, Calendar,
  Wallet, Shield, Save, Users, UserPlus, Filter, X, ChevronDown,
  ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, List,
  LayoutGrid, RotateCcw, Trash2, AlertTriangle
} from 'lucide-vue-next'
import { format, isToday, isThisWeek, isThisMonth, isThisYear } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()

// State
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const users = ref([])
const totalUsers = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const viewMode = ref('table')

// Stats
const stats = reactive({
  total: 0,
  active: 0,
  banned: 0,
  newToday: 0
})

// Search & Filters
const searchQuery = ref('')
const filterRole = ref('')
const filterStatus = ref('')
const filterDate = ref('')
const showFilters = ref(false)

// Selection
const selectedUsers = ref([])

// Modal State
const showModal = ref(false)
const editMode = ref(false)
const selectedUser = ref(null)
const editForm = reactive({
  role: '',
  status: '',
  balance: 0,
  balance_coin: 0
})

// Confirmation Dialog
const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmType = ref('danger')
const confirmButtonText = ref('Onayla')
const confirmIcon = ref(AlertTriangle)
const confirmCallback = ref(null)

// Bulk Actions
const showRoleModal = ref(false)
const bulkRole = ref('user')

let searchTimeout = null

// Computed
const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize.value) || 1)

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      pages.push(1, 2, 3, 4, '...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...', total - 3, total - 2, total - 1, total)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }

  return pages
})

const allSelected = computed(() =>
  users.value.length > 0 && selectedUsers.value.length === users.value.length
)

const someSelected = computed(() =>
  selectedUsers.value.length > 0 && selectedUsers.value.length < users.value.length
)

// CSRF Token
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
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken
  return headers
}

// Helpers
const getAvatar = (username) => `https://api.dicebear.com/7.x/initials/svg?seed=${username}`

const getRoleLabel = (role) => {
  const r = typeof role === 'string' ? role : role?.value || 'user'
  const labels = { admin: 'Admin', moderatör: 'Moderatör', user: 'Kullanıcı', superadmin: 'Super Admin' }
  return labels[r] || r
}

const getRoleClass = (role) => {
  const r = typeof role === 'string' ? role : role?.value || 'user'
  return `role-${r}`
}

const getStatusLabel = (status) => {
  const labels = { active: 'Aktif', inactive: 'Pasif', banned: 'Yasaklı' }
  return labels[status] || status
}

const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy', { locale: tr })
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('tr-TR').format(value)
}

// API Calls
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: pageSize.value
    })
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterRole.value) params.append('role', filterRole.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    if (filterDate.value) params.append('date_filter', filterDate.value)

    const response = await fetch(`/api/admin/users?${params}`, { headers: getHeaders() })
    if (response.ok) {
      const data = await response.json()
      users.value = data.users || []
      totalUsers.value = data.pagination?.total || 0

      // Update stats
      if (data.stats) {
        stats.total = data.stats.total || 0
        stats.active = data.stats.active || 0
        stats.banned = data.stats.banned || 0
        stats.newToday = data.stats.new_today || 0
      }
    } else {
      showNotification('Kullanıcılar yüklenemedi', 'error')
    }
  } catch {
    showNotification('Bağlantı hatası', 'error')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await fetch('/api/admin/users/stats', { headers: getHeaders() })
    if (response.ok) {
      const data = await response.json()
      stats.total = data.total || 0
      stats.active = data.active || 0
      stats.banned = data.banned || 0
      stats.newToday = data.new_today || 0
    }
  } catch {
    // Stats fetch error
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchUsers()
  }, 300)
}

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
  fetchUsers()
}

const applyFilters = () => {
  currentPage.value = 1
  fetchUsers()
}

const clearFilters = () => {
  filterRole.value = ''
  filterStatus.value = ''
  filterDate.value = ''
  currentPage.value = 1
  fetchUsers()
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchUsers()
  }
}

const handlePageSizeChange = () => {
  currentPage.value = 1
  fetchUsers()
}

// Selection
const toggleSelect = (userId) => {
  const index = selectedUsers.value.indexOf(userId)
  if (index === -1) {
    selectedUsers.value.push(userId)
  } else {
    selectedUsers.value.splice(index, 1)
  }
}

const toggleSelectAll = (event) => {
  if (event.target.checked) {
    selectedUsers.value = users.value.map(u => u.id)
  } else {
    selectedUsers.value = []
  }
}

// User Actions
const viewUser = (user) => {
  selectedUser.value = { ...user }
  editMode.value = false
  showModal.value = true
  resetEditForm(user)
}

const openEditUser = (user) => {
  selectedUser.value = { ...user }
  editMode.value = true
  showModal.value = true
  resetEditForm(user)
}

const resetEditForm = (user) => {
  const role = typeof user.role === 'string' ? user.role : user.role?.value || 'user'
  editForm.role = role
  editForm.status = user.status || 'active'
  editForm.balance = user.balance || 0
  editForm.balance_coin = user.balance_coin || 0
}

const closeModal = () => {
  showModal.value = false
  selectedUser.value = null
  editMode.value = false
}

const saveUser = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/admin/users/${selectedUser.value.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        role: editForm.role,
        status: editForm.status,
        balance: editForm.balance,
        balance_coin: editForm.balance_coin
      })
    })

    if (response.ok) {
      showNotification('Kullanıcı başarıyla güncellendi', 'success')

      const index = users.value.findIndex(u => u.id === selectedUser.value.id)
      if (index !== -1) {
        users.value[index] = {
          ...users.value[index],
          role: editForm.role,
          status: editForm.status,
          balance: editForm.balance,
          balance_coin: editForm.balance_coin
        }
      }

      if (authStore.user?.id === selectedUser.value.id) {
        authStore.updateBalance(editForm.balance, editForm.balance_coin)
      }

      closeModal()
      fetchStats()
    } else {
      const error = await response.json()
      showNotification(error.detail || 'Güncelleme başarısız', 'error')
    }
  } catch {
    showNotification('Bağlantı hatası', 'error')
  } finally {
    saving.value = false
  }
}

// Confirmation Dialog
const showConfirmDialog = (title, message, type, buttonText, callback) => {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmType.value = type
  confirmButtonText.value = buttonText
  confirmIcon.value = type === 'danger' ? markRaw(AlertTriangle) : markRaw(Shield)
  confirmCallback.value = callback
  showConfirm.value = true
}

const closeConfirm = () => {
  showConfirm.value = false
  confirmCallback.value = null
}

const executeConfirm = async () => {
  if (confirmCallback.value) {
    await confirmCallback.value()
  }
  closeConfirm()
}

const confirmBan = (user) => {
  showConfirmDialog(
    'Kullanıcıyi Yasakla',
    `${user.username} kullanıcısini yasaklamak istediğinize emin misiniz?`,
    'danger',
    'Yasakla',
    () => banUser(user)
  )
}

const confirmUnban = (user) => {
  showConfirmDialog(
    'Yasagi Kaldır',
    `${user.username} kullanıcısının yasagini kaldırmak istediğinize emin misiniz?`,
    'primary',
    'Kaldır',
    () => unbanUser(user)
  )
}

const banUser = async (user) => {
  try {
    const response = await fetch(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ status: 'banned' })
    })
    if (response.ok) {
      user.status = 'banned'
      showNotification(`${user.username} yasaklandi`, 'success')
      fetchStats()
    } else {
      showNotification('İşlem başarısız', 'error')
    }
  } catch (error) {
    showNotification('Bağlantı hatası', 'error')
  }
}

const unbanUser = async (user) => {
  try {
    const response = await fetch(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ status: 'active' })
    })
    if (response.ok) {
      user.status = 'active'
      showNotification(`${user.username} yasagi kaldırıldı`, 'success')
      fetchStats()
    } else {
      showNotification('İşlem başarısız', 'error')
    }
  } catch (error) {
    showNotification('Bağlantı hatası', 'error')
  }
}

// Bulk Actions
const bulkChangeRole = () => {
  showRoleModal.value = true
}

const executeBulkRoleChange = async () => {
  try {
    const response = await fetch('/api/admin/users/bulk', {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        user_ids: selectedUsers.value,
        action: 'change_role',
        role: bulkRole.value
      })
    })
    if (response.ok) {
      showNotification(`${selectedUsers.value.length} kullanıcının rolu değiştirildi`, 'success')
      selectedUsers.value = []
      showRoleModal.value = false
      fetchUsers()
    } else {
      showNotification('İşlem başarısız', 'error')
    }
  } catch (error) {
    showNotification('Bağlantı hatası', 'error')
  }
}

const bulkBan = () => {
  showConfirmDialog(
    'Toplu Yasaklama',
    `${selectedUsers.value.length} kullanıcıyı yasaklamak istediğinize emin misiniz?`,
    'danger',
    'Yasakla',
    async () => {
      try {
        const response = await fetch('/api/admin/users/bulk', {
          method: 'PUT',
          headers: getHeaders(),
          body: JSON.stringify({
            user_ids: selectedUsers.value,
            action: 'ban'
          })
        })
        if (response.ok) {
          showNotification(`${selectedUsers.value.length} kullanıcı yasaklandi`, 'success')
          selectedUsers.value = []
          fetchUsers()
          fetchStats()
        }
      } catch (error) {
        showNotification('Bağlantı hatası', 'error')
      }
    }
  )
}

const bulkDelete = () => {
  showConfirmDialog(
    'Toplu Silme',
    `${selectedUsers.value.length} kullanıcıyı silmek istediğinize emin misiniz? Bu işlem geri alınamaz!`,
    'danger',
    'Sil',
    async () => {
      try {
        const response = await fetch('/api/admin/users/bulk', {
          method: 'DELETE',
          headers: getHeaders(),
          body: JSON.stringify({
            user_ids: selectedUsers.value
          })
        })
        if (response.ok) {
          showNotification(`${selectedUsers.value.length} kullanıcı silindi`, 'success')
          selectedUsers.value = []
          fetchUsers()
          fetchStats()
        }
      } catch (error) {
        showNotification('Bağlantı hatası', 'error')
      }
    }
  )
}

const exportUsers = async () => {
  exporting.value = true
  try {
    window.open(`/api/admin/users/export?format=csv&token=${authStore.token}`, '_blank')
  } finally {
    exporting.value = false
  }
}

// Simple notification
const showNotification = (message, type = 'info') => {
  // Create and show a simple toast notification
  const toast = document.createElement('div')
  toast.className = `toast-notification ${type}`
  toast.textContent = message
  document.body.appendChild(toast)

  setTimeout(() => toast.classList.add('show'), 10)
  setTimeout(() => {
    toast.classList.remove('show')
    setTimeout(() => toast.remove(), 300)
  }, 3000)
}

onMounted(() => {
  fetchUsers()
  fetchStats()
})

// Clear selection when users change
watch(users, () => {
  selectedUsers.value = selectedUsers.value.filter(id =>
    users.value.some(u => u.id === id)
  )
})
</script>

<style scoped>
.users-page {
  padding: 0;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-icon.active {
  background: linear-gradient(135deg, #11998e, #38ef7d);
}

.stat-icon.banned {
  background: linear-gradient(135deg, #eb3349, #f45c43);
}

.stat-icon.new {
  background: linear-gradient(135deg, #ff6b00, #ff9500);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary, #a0a0c0);
  margin-top: 4px;
}

/* Actions Bar */
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.search-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box input {
  width: 100%;
  padding: 12px 40px 12px 44px;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  color: var(--text-primary, #fff);
  font-size: 14px;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #ff6b00;
  box-shadow: 0 0 0 3px rgba(255, 107, 0, 0.15);
}

.search-box input::placeholder {
  color: var(--text-secondary, #a0a0c0);
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary, #a0a0c0);
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary, #a0a0c0);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.clear-btn:hover {
  color: var(--text-primary, #fff);
  background: var(--bg-tertiary, #2a2a4a);
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  color: var(--text-secondary, #a0a0c0);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover,
.filter-btn.active {
  border-color: #ff6b00;
  color: #ff6b00;
}

.filter-btn svg:last-child {
  transition: transform 0.2s;
}

.filter-btn svg:last-child.rotated {
  transform: rotate(180deg);
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: var(--bg-tertiary, #2a2a4a);
  border-radius: 12px;
}

.selected-count {
  font-size: 13px;
  font-weight: 600;
  color: #ff6b00;
  padding-right: 10px;
  border-right: 1px solid var(--border-color, #3a3a5a);
}

.bulk-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-btn.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.bulk-btn.warning:hover {
  background: rgba(245, 158, 11, 0.25);
}

.bulk-btn.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.bulk-btn.danger:hover {
  background: rgba(239, 68, 68, 0.25);
}

.bulk-btn.error {
  background: rgba(220, 38, 38, 0.15);
  color: #dc2626;
}

.bulk-btn.error:hover {
  background: rgba(220, 38, 38, 0.25);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.secondary {
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  color: var(--text-primary, #fff);
}

.action-btn.secondary:hover {
  background: var(--bg-tertiary, #2a2a4a);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Filters Panel */
.filters-panel {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  padding: 20px;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 16px;
  margin-bottom: 16px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.filter-item label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #a0a0c0);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-item select {
  padding: 10px 14px;
  background: var(--bg-tertiary, #2a2a4a);
  border: 1px solid var(--border-color, #3a3a5a);
  border-radius: 10px;
  color: var(--text-primary, #fff);
  font-size: 14px;
  cursor: pointer;
}

.filter-item select:focus {
  outline: none;
  border-color: #ff6b00;
}

.clear-filters-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: 1px solid var(--border-color, #3a3a5a);
  border-radius: 10px;
  color: var(--text-secondary, #a0a0c0);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.clear-filters-btn:hover {
  border-color: #ff6b00;
  color: #ff6b00;
}

/* View Controls */
.view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.view-toggle {
  display: flex;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 10px;
  padding: 4px;
}

.view-toggle button {
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary, #a0a0c0);
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggle button:hover {
  color: var(--text-primary, #fff);
}

.view-toggle button.active {
  background: #ff6b00;
  color: white;
}

.results-info {
  font-size: 14px;
  color: var(--text-secondary, #a0a0c0);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
  color: var(--text-secondary, #a0a0c0);
}

.loader {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color, #2a2a4a);
  border-top-color: #ff6b00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table View */
.users-table-container {
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 16px;
  overflow: hidden;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
}

.users-table th {
  background: var(--bg-tertiary, #2a2a4a);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary, #a0a0c0);
}

.users-table tbody tr {
  transition: all 0.2s;
}

.users-table tbody tr:hover {
  background: rgba(255, 107, 0, 0.05);
}

.users-table tbody tr.selected {
  background: rgba(255, 107, 0, 0.1);
}

.users-table tbody tr:last-child td {
  border-bottom: none;
}

.checkbox-col {
  width: 48px;
  text-align: center !important;
}

.checkbox-col input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #ff6b00;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  position: relative;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  object-fit: cover;
  background: var(--bg-tertiary, #2a2a4a);
}

.status-dot {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid var(--bg-secondary, #1a1a2e);
}

.status-dot.active {
  background: #22c55e;
}

.status-dot.inactive {
  background: #6b7280;
}

.status-dot.banned {
  background: #ef4444;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-weight: 600;
  color: var(--text-primary, #fff);
}

.username-link {
  text-decoration: none;
  transition: color 0.2s ease;
}

.username-link:hover {
  color: #f97316;
  text-decoration: underline;
}

.email {
  font-size: 13px;
  color: var(--text-secondary, #a0a0c0);
}

.balance-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tl-balance {
  font-weight: 600;
  color: #22c55e;
}

.coin-balance {
  font-size: 13px;
  color: #ff6b00;
}

/* Role Badges */
.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.role-badge.role-user {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
}

.role-badge.role-moderatör {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

.role-badge.role-admin {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.role-badge.role-superadmin {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(168, 85, 247, 0.2));
  color: #e879f9;
}

/* Status Badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.status-badge.inactive {
  background: rgba(107, 114, 128, 0.15);
  color: #9ca3af;
}

.status-badge.banned {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.date-cell {
  color: var(--text-secondary, #a0a0c0);
  font-size: 14px;
}

.actions-col {
  width: 140px;
}

.row-actions {
  display: flex;
  gap: 4px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

tr:hover .row-actions {
  opacity: 1;
}

.row-action-btn {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary, #2a2a4a);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.row-action-btn.view {
  color: #60a5fa;
}

.row-action-btn.view:hover {
  background: rgba(96, 165, 250, 0.2);
}

.row-action-btn.edit {
  color: #fbbf24;
}

.row-action-btn.edit:hover {
  background: rgba(251, 191, 36, 0.2);
}

.row-action-btn.ban {
  color: #f87171;
}

.row-action-btn.ban:hover {
  background: rgba(248, 113, 113, 0.2);
}

.row-action-btn.unban {
  color: #4ade80;
}

.row-action-btn.unban:hover {
  background: rgba(74, 222, 128, 0.2);
}

/* Cards View */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.user-card {
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
}

.user-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 107, 0, 0.3);
}

.user-card.selected {
  border-color: #ff6b00;
  background: rgba(255, 107, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #ff6b00;
}

.card-avatar {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
}

.card-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 20px;
  object-fit: cover;
  background: var(--bg-tertiary, #2a2a4a);
}

.status-indicator {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 3px solid var(--bg-secondary, #1a1a2e);
}

.status-indicator.active {
  background: #22c55e;
}

.status-indicator.inactive {
  background: #6b7280;
}

.status-indicator.banned {
  background: #ef4444;
}

.status-indicator.large {
  width: 24px;
  height: 24px;
  border-width: 4px;
}

.card-info {
  text-align: center;
  margin-bottom: 20px;
}

.card-username {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  margin-bottom: 4px;
  display: block;
}

.card-username-link {
  text-decoration: none;
  transition: color 0.2s ease;
}

.card-username-link:hover {
  color: #f97316;
}

.card-email {
  font-size: 14px;
  color: var(--text-secondary, #a0a0c0);
}

.card-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 16px 0;
  border-top: 1px solid var(--border-color, #2a2a4a);
  border-bottom: 1px solid var(--border-color, #2a2a4a);
  margin-bottom: 16px;
}

.card-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #22c55e;
}

.card-stat.coin {
  color: #ff6b00;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary, #a0a0c0);
  margin-bottom: 20px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-action {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  background: var(--bg-tertiary, #2a2a4a);
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.card-action.view {
  color: #60a5fa;
}

.card-action.view:hover {
  background: rgba(96, 165, 250, 0.2);
}

.card-action.edit {
  color: #fbbf24;
}

.card-action.edit:hover {
  background: rgba(251, 191, 36, 0.2);
}

.card-action.ban {
  color: #f87171;
  flex: 0;
  padding: 10px 14px;
}

.card-action.ban:hover {
  background: rgba(248, 113, 113, 0.2);
}

.card-action.unban {
  color: #4ade80;
  flex: 0;
  padding: 10px 14px;
}

.card-action.unban:hover {
  background: rgba(74, 222, 128, 0.2);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  color: var(--text-secondary, #a0a0c0);
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  margin: 20px 0 8px;
}

.empty-state p {
  font-size: 14px;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding: 20px;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 16px;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary, #a0a0c0);
}

.page-size-selector select {
  padding: 8px 12px;
  background: var(--bg-tertiary, #2a2a4a);
  border: 1px solid var(--border-color, #3a3a5a);
  border-radius: 8px;
  color: var(--text-primary, #fff);
  cursor: pointer;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary, #2a2a4a);
  border: 1px solid var(--border-color, #3a3a5a);
  border-radius: 10px;
  color: var(--text-secondary, #a0a0c0);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #ff6b00;
  color: #ff6b00;
}

.page-btn.active {
  background: #ff6b00;
  border-color: #ff6b00;
  color: white;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-ellipsis {
  padding: 0 8px;
  color: var(--text-secondary, #a0a0c0);
}

.page-info {
  font-size: 14px;
  color: var(--text-secondary, #a0a0c0);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 24px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary, #fff);
}

.modal-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary, #2a2a4a);
  border: none;
  border-radius: 10px;
  color: var(--text-secondary, #a0a0c0);
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  color: var(--text-primary, #fff);
  background: rgba(255, 107, 0, 0.2);
}

.modal-body {
  padding: 24px;
}

.modal-user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
  margin-bottom: 24px;
}

.modal-avatar {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.modal-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 20px;
  object-fit: cover;
  background: var(--bg-tertiary, #2a2a4a);
}

.modal-user-info h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  margin-bottom: 8px;
}

.modal-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.modal-stat {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--bg-tertiary, #2a2a4a);
  border-radius: 14px;
}

.modal-stat svg {
  color: #ff6b00;
  flex-shrink: 0;
  margin-top: 2px;
}

.modal-stat div {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.modal-stat label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #a0a0c0);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.modal-stat span {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary, #fff);
}

.modal-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #3a3a5a);
  border-radius: 10px;
  color: var(--text-primary, #fff);
  font-size: 15px;
}

.modal-input:focus {
  outline: none;
  border-color: #ff6b00;
}

.modal-edit-section {
  padding-top: 24px;
  border-top: 1px solid var(--border-color, #2a2a4a);
}

.edit-row {
  margin-bottom: 16px;
}

.edit-row label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #a0a0c0);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.modal-select {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-tertiary, #2a2a4a);
  border: 1px solid var(--border-color, #3a3a5a);
  border-radius: 12px;
  color: var(--text-primary, #fff);
  font-size: 14px;
  cursor: pointer;
}

.modal-select:focus {
  outline: none;
  border-color: #ff6b00;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color, #2a2a4a);
}

.modal-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-btn.secondary {
  background: var(--bg-tertiary, #2a2a4a);
  color: var(--text-primary, #fff);
}

.modal-btn.secondary:hover {
  background: var(--border-color, #3a3a5a);
}

.modal-btn.primary {
  background: #ff6b00;
  color: white;
}

.modal-btn.primary:hover {
  background: #e65f00;
}

.modal-btn.danger {
  background: #ef4444;
  color: white;
}

.modal-btn.danger:hover {
  background: #dc2626;
}

.modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Confirmation Dialog */
.confirm-dialog {
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 24px;
  padding: 32px;
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.confirm-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  border-radius: 50%;
}

.confirm-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.confirm-icon.primary {
  background: rgba(255, 107, 0, 0.15);
  color: #ff6b00;
}

.confirm-icon.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.confirm-dialog h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary, #fff);
  margin-bottom: 12px;
}

.confirm-dialog p {
  font-size: 14px;
  color: var(--text-secondary, #a0a0c0);
  margin-bottom: 24px;
  line-height: 1.6;
}

.confirm-dialog .modal-select {
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Toast Notification */
:global(.toast-notification) {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  background: var(--bg-secondary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  color: var(--text-primary, #fff);
  font-size: 14px;
  font-weight: 500;
  z-index: 9999;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.3s ease;
}

:global(.toast-notification.show) {
  opacity: 1;
  transform: translateY(0);
}

:global(.toast-notification.success) {
  border-left: 4px solid #22c55e;
}

:global(.toast-notification.error) {
  border-left: 4px solid #ef4444;
}

:global(.toast-notification.info) {
  border-left: 4px solid #3b82f6;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
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
.modal-leave-to .modal-container,
.modal-enter-from .confirm-dialog,
.modal-leave-to .confirm-dialog {
  transform: scale(0.95);
}

.table-row-enter-active,
.table-row-leave-active {
  transition: all 0.3s ease;
}

.table-row-enter-from,
.table-row-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.card-list-enter-active,
.card-list-leave-active {
  transition: all 0.4s ease;
}

.card-list-enter-from,
.card-list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.card-list-move {
  transition: transform 0.4s ease;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .actions-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-filters {
    flex-direction: column;
  }

  .search-box {
    max-width: none;
  }

  .action-buttons {
    justify-content: center;
    flex-wrap: wrap;
  }

  .filters-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    flex: none;
  }

  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }

  .users-table {
    display: block;
    overflow-x: auto;
  }

  .cards-grid {
    grid-template-columns: 1fr;
  }

  .modal-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
