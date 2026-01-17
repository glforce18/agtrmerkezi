<template>
  <AdminLayout>
    <div class="admin-users">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Kullanıcı Yönetimi</h1>
          <p class="subtitle">Toplam {{ totalUsers }} kullanıcı</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="exportUsers">
            <Download :size="18" />
            <span>Dışa Aktar</span>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Kullanıcı ara..."
            @input="debouncedSearch"
          />
        </div>
        <select v-model="filterRole" class="filter-select" @change="fetchUsers">
          <option value="">Tüm Roller</option>
          <option value="admin">Admin</option>
          <option value="moderator">Moderatör</option>
          <option value="user">Kullanıcı</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="fetchUsers">
          <option value="">Tüm Durumlar</option>
          <option value="active">Aktif</option>
          <option value="banned">Yasaklı</option>
          <option value="inactive">Pasif</option>
        </select>
      </div>

      <!-- Users Table -->
      <div class="table-container">
        <div v-if="loading" class="loading-state">
          <Loader2 :size="32" class="spin" />
          <span>Yükleniyor...</span>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th @click="sortBy('id')" class="sortable">
                ID
                <ArrowUpDown :size="14" />
              </th>
              <th>Kullanıcı</th>
              <th>E-posta</th>
              <th @click="sortBy('role')" class="sortable">
                Rol
                <ArrowUpDown :size="14" />
              </th>
              <th>Durum</th>
              <th @click="sortBy('created_at')" class="sortable">
                Kayıt Tarihi
                <ArrowUpDown :size="14" />
              </th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td class="id-cell">#{{ user.id }}</td>
              <td>
                <div class="user-cell">
                  <img :src="getUserAvatar(user.username)" :alt="user.username" class="avatar" />
                  <div class="user-info">
                    <span class="username">{{ user.username }}</span>
                    <span v-if="user.is_online" class="online-badge">Online</span>
                  </div>
                </div>
              </td>
              <td class="email-cell">{{ user.email }}</td>
              <td>
                <span class="role-badge" :class="getUserRole(user)">
                  {{ getRoleLabel(getUserRole(user)) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="getStatusClass(user)">
                  {{ getStatusLabel(user) }}
                </span>
              </td>
              <td class="date-cell">{{ formatDate(user.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-icon" @click="viewUser(user)" title="Görüntüle">
                    <Eye :size="16" />
                  </button>
                  <button class="btn-icon" @click="editUser(user)" title="Düzenle">
                    <Edit2 :size="16" />
                  </button>
                  <button
                    v-if="!user.is_banned"
                    class="btn-icon danger"
                    @click="banUser(user)"
                    title="Yasakla"
                  >
                    <Ban :size="16" />
                  </button>
                  <button
                    v-else
                    class="btn-icon success"
                    @click="unbanUser(user)"
                    title="Yasağı Kaldır"
                  >
                    <UserCheck :size="16" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="7" class="empty-state">
                <UserX :size="48" />
                <p>Kullanıcı bulunamadı</p>
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

    </div>

    <!-- User Detail Modal -->
    <Teleport to="body">
      <div v-if="selectedUser" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h3>{{ editMode ? 'Kullanıcı Düzenle' : 'Kullanıcı Detayı' }}</h3>
            <button class="btn-icon" @click="closeModal">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="user-detail-header">
              <img :src="getUserAvatar(selectedUser.username)" class="detail-avatar" />
              <div>
                <h4>{{ selectedUser.username }}</h4>
                <span class="role-badge" :class="getUserRole(selectedUser)">
                  {{ getRoleLabel(getUserRole(selectedUser)) }}
                </span>
              </div>
            </div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="label">E-posta</span>
                <span class="value">{{ selectedUser.email }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Kayıt Tarihi</span>
                <span class="value">{{ formatDate(selectedUser.created_at) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Son Giriş</span>
                <span class="value">{{ selectedUser.last_login ? formatDate(selectedUser.last_login) : 'Hiç' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">TL Bakiye</span>
                <span class="value">{{ selectedUser.balance || 0 }} TL</span>
              </div>
              <div class="detail-item">
                <span class="label">Armor Bakiye</span>
                <span class="value">{{ selectedUser.balance_coin || 0 }} Armor</span>
              </div>
            </div>
            <div v-if="editMode" class="edit-form">
              <div class="form-group">
                <label>Rol</label>
                <select v-model="editForm.role">
                  <option value="user">Kullanıcı</option>
                  <option value="moderator">Moderatör</option>
                  <option value="admin">Admin</option>
                  <option value="superadmin">Süper Admin</option>
                </select>
              </div>
              <div class="form-group">
                <label>TL Bakiye</label>
                <input type="number" v-model.number="editForm.balance" step="0.01" min="0" />
              </div>
              <div class="form-group">
                <label>Armor Bakiye</label>
                <input type="number" v-model.number="editForm.balance_coin" step="1" min="0" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button v-if="!editMode" class="btn btn-secondary" @click="editMode = true">
              <Edit2 :size="16" />
              Düzenle
            </button>
            <template v-else>
              <button class="btn btn-secondary" @click="editMode = false">İptal</button>
              <button class="btn btn-primary" @click="saveUser">Kaydet</button>
            </template>
          </div>
        </div>
      </div>
    </Teleport>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Search,
  Download,
  Eye,
  Edit2,
  Ban,
  UserCheck,
  UserX,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  Loader2,
  X
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()
const loading = ref(false)
const users = ref([])
const totalUsers = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 20

const searchQuery = ref('')
const filterRole = ref('')
const filterStatus = ref('')
const sortField = ref('id')
const sortOrder = ref('desc')

const selectedUser = ref(null)
const editMode = ref(false)
const editForm = reactive({
  role: '',
  balance: 0,
  balance_coin: 0
})

let searchTimeout = null

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authStore.token}`
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: perPage
    })

    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterRole.value) params.append('role', filterRole.value)
    if (filterStatus.value) params.append('status', filterStatus.value)

    const response = await fetch(`/api/admin/users?${params}`, {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      // Map API response to frontend expected format
      users.value = (data.users || []).map(u => ({
        ...u,
        is_banned: u.status === 'banned',
        is_online: false // Backend doesn't track online status
      }))
      totalUsers.value = data.pagination?.total || 0
      totalPages.value = data.pagination?.pages || 1
    }
  } catch (error) {
    console.error('Fetch users error:', error)
  }
  loading.value = false
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchUsers()
  }, 300)
}

const sortBy = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
  fetchUsers()
}

const goToPage = (page) => {
  currentPage.value = page
  fetchUsers()
}

const getUserAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}`
}

const getRoleLabel = (role) => {
  const labels = { admin: 'Admin', moderator: 'Moderatör', user: 'Kullanıcı', superadmin: 'Süper Admin' }
  return labels[role] || role
}

// Helper to get role string from user object (handles both string and object formats)
const getUserRole = (user) => {
  if (!user) return 'user'
  if (typeof user.role === 'string') return user.role
  if (user.role?.value) return user.role.value
  return 'user'
}

const getStatusClass = (user) => {
  if (user.is_banned) return 'banned'
  if (user.is_online) return 'online'
  return 'offline'
}

const getStatusLabel = (user) => {
  if (user.is_banned) return 'Yasaklı'
  if (user.is_online) return 'Online'
  return 'Offline'
}

const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy HH:mm', { locale: tr })
}

const viewUser = (user) => {
  selectedUser.value = user
  editMode.value = false
  editForm.role = getUserRole(user)
  editForm.balance = user.balance || 0
  editForm.balance_coin = user.balance_coin || 0
}

const editUser = (user) => {
  selectedUser.value = user
  editMode.value = true
  editForm.role = getUserRole(user)
  editForm.balance = user.balance || 0
  editForm.balance_coin = user.balance_coin || 0
}

const closeModal = () => {
  selectedUser.value = null
  editMode.value = false
}

const saveUser = async () => {
  try {
    const response = await fetch(`/api/admin/users/${selectedUser.value.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        role: editForm.role,
        balance: editForm.balance,
        balance_coin: editForm.balance_coin
      })
    })

    if (response.ok) {
      const index = users.value.findIndex(u => u.id === selectedUser.value.id)
      if (index !== -1) {
        users.value[index] = {
          ...users.value[index],
          role: editForm.role,
          balance: editForm.balance,
          balance_coin: editForm.balance_coin
        }
      }
      alert('Kullanıcı güncellendi!')
      closeModal()
    } else {
      const error = await response.json()
      alert(error.detail || 'Güncelleme başarısız')
    }
  } catch (error) {
    console.error('Save user error:', error)
    alert('Bir hata oluştu')
  }
}

const banUser = async (user) => {
  if (!confirm(`${user.username} kullanıcısını yasaklamak istediğinize emin misiniz?`)) return

  try {
    // Use DELETE endpoint which sets status to banned
    const response = await fetch(`/api/admin/users/${user.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (response.ok) {
      user.is_banned = true
      user.status = 'banned'
    }
  } catch (error) {
    console.error('Ban user error:', error)
  }
}

const unbanUser = async (user) => {
  try {
    // Update user status back to active
    const response = await fetch(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ status: 'active' })
    })
    if (response.ok) {
      user.is_banned = false
      user.status = 'active'
    }
  } catch (error) {
    console.error('Unban user error:', error)
  }
}

const exportUsers = () => {
  // Add token to export URL
  window.open(`/api/admin/users/export?format=csv&token=${authStore.token}`, '_blank')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-users {
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

.header-actions {
  display: flex;
  gap: 12px;
}

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

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  color: var(--text-primary);
}

.data-table th svg {
  vertical-align: middle;
  margin-left: 4px;
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

.id-cell {
  font-family: monospace;
  color: var(--text-secondary);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-tertiary);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
}

.online-badge {
  font-size: 11px;
  color: var(--success-color);
}

.email-cell {
  color: var(--text-secondary);
}

.date-cell {
  color: var(--text-secondary);
  font-size: 13px;
}

.role-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color, #ef4444);
}

.role-badge.moderator {
  background: rgba(139, 92, 246, 0.15);
  color: var(--secondary-color, #8b5cf6);
}

.role-badge.user {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-color, #3b82f6);
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.online {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
}

.status-badge.offline {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted, #6b7280);
}

.status-badge.banned {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color, #ef4444);
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

.btn-icon.success:hover {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
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

.user-detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
}

.user-detail-header h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
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

.edit-form {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    min-width: 100%;
  }

  .data-table {
    font-size: 13px;
  }

  .data-table th,
  .data-table td {
    padding: 12px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
