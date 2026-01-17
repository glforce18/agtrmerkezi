<template>
  <AdminLayout>
    <div class="admin-payments">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Ödeme Yönetimi</h1>
          <p class="subtitle">{{ pendingCount }} bekleyen ödeme</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="exportPayments">
            <Download :size="18" />
            <span>Rapor</span>
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon green">
            <DollarSign :size="24" />
          </div>
          <div>
            <span class="stat-value">{{ formatCurrency(totalRevenue) }}</span>
            <span class="stat-label">Toplam Gelir</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon blue">
            <TrendingUp :size="24" />
          </div>
          <div>
            <span class="stat-value">{{ formatCurrency(monthlyRevenue) }}</span>
            <span class="stat-label">Bu Ay</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">
            <Clock :size="24" />
          </div>
          <div>
            <span class="stat-value">{{ pendingCount }}</span>
            <span class="stat-label">Bekleyen</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">
            <CreditCard :size="24" />
          </div>
          <div>
            <span class="stat-value">{{ totalPayments }}</span>
            <span class="stat-label">Toplam İşlem</span>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <button
          class="tab"
          :class="{ active: activeTab === 'all' }"
          @click="setTab('all')"
        >
          Tümü
        </button>
        <button
          class="tab"
          :class="{ active: activeTab === 'pending' }"
          @click="setTab('pending')"
        >
          Bekleyen
          <span v-if="pendingCount > 0" class="tab-badge">{{ pendingCount }}</span>
        </button>
        <button
          class="tab"
          :class="{ active: activeTab === 'completed' }"
          @click="setTab('completed')"
        >
          Tamamlanan
        </button>
        <button
          class="tab"
          :class="{ active: activeTab === 'failed' }"
          @click="setTab('failed')"
        >
          Başarısız
        </button>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Kullanıcı veya işlem ara..."
            @input="debouncedSearch"
          />
        </div>
        <select v-model="filterMethod" class="filter-select" @change="fetchPayments">
          <option value="">Tüm Yöntemler</option>
          <option value="bank">Banka Havalesi</option>
          <option value="papara">Papara</option>
          <option value="crypto">Kripto</option>
        </select>
        <input
          type="date"
          v-model="filterDateFrom"
          class="filter-input"
          @change="fetchPayments"
        />
        <input
          type="date"
          v-model="filterDateTo"
          class="filter-input"
          @change="fetchPayments"
        />
      </div>

      <!-- Payments Table -->
      <div class="table-container">
        <div v-if="loading" class="loading-state">
          <Loader2 :size="32" class="spin" />
          <span>Yükleniyor...</span>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Kullanıcı</th>
              <th>Tutar</th>
              <th>Yöntem</th>
              <th>Durum</th>
              <th>Tarih</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in payments" :key="payment.id">
              <td class="id-cell">#{{ payment.id }}</td>
              <td>
                <div class="user-cell">
                  <img :src="getUserAvatar(payment.username)" class="avatar" />
                  <span>{{ payment.username || 'N/A' }}</span>
                </div>
              </td>
              <td>
                <span class="amount">{{ formatCurrency(payment.amount) }}</span>
              </td>
              <td>
                <span class="method-badge" :class="payment.method">
                  {{ getMethodLabel(payment.method) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="payment.status">
                  <component :is="getStatusIcon(payment.status)" :size="14" />
                  {{ getStatusLabel(payment.status) }}
                </span>
              </td>
              <td class="date-cell">{{ formatDate(payment.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <template v-if="payment.status === 'pending'">
                    <button
                      class="btn-action approve"
                      @click="approvePayment(payment)"
                      title="Onayla"
                    >
                      <Check :size="16" />
                    </button>
                    <button
                      class="btn-action reject"
                      @click="rejectPayment(payment)"
                      title="Reddet"
                    >
                      <X :size="16" />
                    </button>
                  </template>
                  <button class="btn-icon" @click="viewPayment(payment)" title="Detay">
                    <Eye :size="16" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="payments.length === 0">
              <td colspan="7" class="empty-state">
                <Wallet :size="48" />
                <p>Ödeme bulunamadı</p>
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

      <!-- Payment Detail Modal -->
      <div v-if="selectedPayment" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h3>Ödeme Detayı #{{ selectedPayment.id }}</h3>
            <button class="btn-icon" @click="closeModal">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="payment-detail-header">
              <div class="amount-large">{{ formatCurrency(selectedPayment.amount) }}</div>
              <span class="status-badge large" :class="selectedPayment.status">
                {{ getStatusLabel(selectedPayment.status) }}
              </span>
            </div>

            <div class="detail-grid">
              <div class="detail-item">
                <span class="label">Kullanıcı</span>
                <span class="value">{{ selectedPayment.username }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Yöntem</span>
                <span class="value">{{ getMethodLabel(selectedPayment.method) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Tarih</span>
                <span class="value">{{ formatDate(selectedPayment.created_at) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">İşlem Tarihi</span>
                <span class="value">{{ formatDate(selectedPayment.processed_at) || '-' }}</span>
              </div>
            </div>

            <div v-if="selectedPayment.proof_url" class="proof-section">
              <h5>Dekont</h5>
              <img :src="selectedPayment.proof_url" alt="Dekont" class="proof-image" />
            </div>

            <div v-if="selectedPayment.note" class="note-section">
              <h5>Not</h5>
              <p>{{ selectedPayment.note }}</p>
            </div>

            <div v-if="selectedPayment.reject_reason" class="reject-section">
              <h5>Red Sebebi</h5>
              <p>{{ selectedPayment.reject_reason }}</p>
            </div>
          </div>
          <div v-if="selectedPayment.status === 'pending'" class="modal-footer">
            <button class="btn btn-danger" @click="rejectPayment(selectedPayment)">
              <X :size="16" />
              Reddet
            </button>
            <button class="btn btn-success" @click="approvePayment(selectedPayment)">
              <Check :size="16" />
              Onayla
            </button>
          </div>
        </div>
      </div>

      <!-- Reject Reason Modal -->
      <div v-if="showRejectModal" class="modal-overlay" @click.self="showRejectModal = false">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h3>Ödemeyi Reddet</h3>
            <button class="btn-icon" @click="showRejectModal = false">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Red Sebebi</label>
              <textarea
                v-model="rejectReason"
                rows="3"
                placeholder="Red sebebini yazın..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showRejectModal = false">İptal</button>
            <button class="btn btn-danger" @click="confirmReject">Reddet</button>
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
  Download,
  DollarSign,
  TrendingUp,
  Clock,
  CreditCard,
  Wallet,
  Eye,
  Check,
  X,
  ChevronLeft,
  ChevronRight,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()
const loading = ref(false)
const payments = ref([])
const totalPayments = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 20

const totalRevenue = ref(0)
const monthlyRevenue = ref(0)
const pendingCount = ref(0)

const activeTab = ref('all')
const searchQuery = ref('')
const filterMethod = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')

const selectedPayment = ref(null)
const showRejectModal = ref(false)
const rejectReason = ref('')
const paymentToReject = ref(null)

let searchTimeout = null

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authStore.token}`
})

const fetchPayments = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: perPage
    })

    if (activeTab.value !== 'all') params.append('status', activeTab.value)
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterMethod.value) params.append('method', filterMethod.value)
    if (filterDateFrom.value) params.append('from', filterDateFrom.value)
    if (filterDateTo.value) params.append('to', filterDateTo.value)

    const response = await fetch(`/api/admin/payments?${params}`, {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      payments.value = data.payments || []
      totalPayments.value = data.pagination?.total || 0
      totalPages.value = data.pagination?.pages || 1
    }
  } catch (error) {
    console.error('Fetch payments error:', error)
  }
  loading.value = false
}

const fetchStats = async () => {
  try {
    const response = await fetch('/api/admin/dashboard', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      totalRevenue.value = data.payments?.total_revenue || 0
      monthlyRevenue.value = data.payments?.month_revenue || 0
      pendingCount.value = data.payments?.pending || 0
    }
  } catch (error) {
    console.error('Stats fetch error:', error)
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchPayments()
  }, 300)
}

const setTab = (tab) => {
  activeTab.value = tab
  currentPage.value = 1
  fetchPayments()
}

const goToPage = (page) => {
  currentPage.value = page
  fetchPayments()
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount || 0)
}

const getUserAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}`
}

const getMethodLabel = (method) => {
  const labels = {
    bank: 'Banka',
    papara: 'Papara',
    crypto: 'Kripto'
  }
  return labels[method] || method || 'Havale'
}

const getStatusLabel = (status) => {
  const labels = {
    pending: 'Bekliyor',
    completed: 'Tamamlandı',
    failed: 'Başarısız'
  }
  return labels[status] || status
}

const getStatusIcon = (status) => {
  const icons = {
    pending: AlertCircle,
    completed: CheckCircle,
    failed: XCircle
  }
  return icons[status] || AlertCircle
}

const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy HH:mm', { locale: tr })
}

const viewPayment = (payment) => {
  selectedPayment.value = payment
}

const closeModal = () => {
  selectedPayment.value = null
}

const approvePayment = async (payment) => {
  if (!confirm(`${payment.amount} ₺ tutarındaki ödemeyi onaylamak istediğinize emin misiniz?`)) return

  try {
    const response = await fetch(`/api/admin/payments/${payment.id}/approve`, {
      method: 'POST',
      headers: getHeaders()
    })

    if (response.ok) {
      payment.status = 'completed'
      pendingCount.value = Math.max(0, pendingCount.value - 1)
      closeModal()
      fetchPayments()
      fetchStats()
    } else {
      const data = await response.json()
      alert(data.detail || 'Onaylama başarısız')
    }
  } catch (error) {
    console.error('Approve payment error:', error)
    alert('Bir hata oluştu')
  }
}

const rejectPayment = (payment) => {
  paymentToReject.value = payment
  rejectReason.value = ''
  showRejectModal.value = true
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    alert('Lütfen bir red sebebi yazın')
    return
  }

  try {
    const response = await fetch(`/api/admin/payments/${paymentToReject.value.id}/reject`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ reason: rejectReason.value })
    })

    if (response.ok) {
      paymentToReject.value.status = 'failed'
      pendingCount.value = Math.max(0, pendingCount.value - 1)
      showRejectModal.value = false
      closeModal()
      fetchPayments()
      fetchStats()
    } else {
      const data = await response.json()
      alert(data.detail || 'Reddetme başarısız')
    }
  } catch (error) {
    console.error('Reject payment error:', error)
    alert('Bir hata oluştu')
  }
}

const exportPayments = () => {
  const params = new URLSearchParams()
  if (activeTab.value !== 'all') params.append('status', activeTab.value)
  if (filterDateFrom.value) params.append('from', filterDateFrom.value)
  if (filterDateTo.value) params.append('to', filterDateTo.value)
  params.append('format', 'csv')
  params.append('token', authStore.token)

  window.open(`/api/admin/payments/export?${params}`, '_blank')
}

onMounted(() => {
  fetchPayments()
  fetchStats()
})
</script>

<style scoped>
.admin-payments {
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.green {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
}

.stat-icon.blue {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-color, #3b82f6);
}

.stat-icon.orange {
  background: rgba(255, 107, 0, 0.15);
  color: var(--primary-color, #ff6b00);
}

.stat-icon.purple {
  background: rgba(139, 92, 246, 0.15);
  color: var(--secondary-color, #8b5cf6);
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

/* Tabs */
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  padding: 4px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  background: none;
  border: none;
  border-radius: 10px;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.tab.active {
  background: var(--primary-color);
  color: var(--bg-primary);
}

.tab-badge {
  background: rgba(239, 68, 68, 0.9);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

.tab.active .tab-badge {
  background: rgba(0, 0, 0, 0.2);
  color: var(--bg-primary);
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

.btn-success {
  background: var(--success-color, #10b981);
  color: var(--bg-primary);
}

.btn-danger {
  background: var(--error-color, #ef4444);
  color: white;
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

.filter-select,
.filter-input {
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

.id-cell {
  font-family: monospace;
  color: var(--text-secondary);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.amount {
  font-weight: 600;
  color: var(--success-color, #10b981);
}

.method-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.method-badge.bank {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-color, #3b82f6);
}

.method-badge.papara {
  background: rgba(139, 92, 246, 0.15);
  color: var(--secondary-color, #8b5cf6);
}

.method-badge.crypto {
  background: rgba(255, 107, 0, 0.15);
  color: var(--primary-color, #ff6b00);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning-color, #f59e0b);
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color, #ef4444);
}

.status-badge.large {
  font-size: 14px;
  padding: 6px 14px;
}

.date-cell {
  color: var(--text-secondary);
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-action {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action.approve {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
}

.btn-action.approve:hover {
  background: var(--success-color, #10b981);
  color: white;
}

.btn-action.reject {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color, #ef4444);
}

.btn-action.reject:hover {
  background: var(--error-color, #ef4444);
  color: white;
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

.modal-sm {
  max-width: 400px;
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

.payment-detail-header {
  text-align: center;
  margin-bottom: 24px;
}

.amount-large {
  font-size: 32px;
  font-weight: 700;
  color: var(--success-color, #10b981);
  margin-bottom: 8px;
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

.proof-section,
.note-section,
.reject-section {
  margin-top: 20px;
}

.proof-section h5,
.note-section h5,
.reject-section h5 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.proof-image {
  width: 100%;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.note-section p,
.reject-section p {
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 12px;
  border-radius: 8px;
}

.reject-section p {
  border-left: 3px solid var(--error-color, #ef4444);
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group textarea {
  width: 100%;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  resize: vertical;
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

  .tabs {
    flex-wrap: wrap;
  }

  .tab {
    flex: none;
    padding: 10px 16px;
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
