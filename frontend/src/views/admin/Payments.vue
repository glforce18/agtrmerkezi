<template>
  <AdminLayout>
    <div class="payments-page">
      <!-- Page Header -->
      <header class="page-header">
        <div class="header-content">
          <div class="header-title">
            <h1>Ödeme Yönetimi</h1>
            <p class="header-subtitle">
              <span class="pulse-dot"></span>
              {{ pendingCount }} bekleyen ödeme
            </p>
          </div>
          <div class="header-actions">
            <button
              v-if="selectedPayments.length > 0"
              class="btn btn-outline-danger"
              @click="bulkReject"
            >
              <XCircle :size="18" />
              <span>Seçilenleri Reddet ({{ selectedPayments.length }})</span>
            </button>
            <button
              v-if="selectedPayments.length > 0"
              class="btn btn-success"
              @click="bulkApprove"
            >
              <CheckCircle :size="18" />
              <span>Seçilenleri Onayla ({{ selectedPayments.length }})</span>
            </button>
            <button class="btn btn-outline" @click="exportPayments">
              <FileDown :size="18" />
              <span>Rapor İndir</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Stats Cards -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card stat-total">
            <div class="stat-icon-wrapper">
              <Wallet :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ formatCurrency(stats.totalRevenue) }}</span>
              <span class="stat-label">Toplam Gelir</span>
            </div>
            <div class="stat-trend positive">
              <TrendingUp :size="14" />
              <span>+12%</span>
            </div>
          </div>

          <div class="stat-card stat-pending">
            <div class="stat-icon-wrapper warning">
              <Clock :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ pendingCount }}</span>
              <span class="stat-label">Bekleyen</span>
            </div>
            <div class="stat-badge warning" v-if="pendingCount > 0">
              İşlem Bekliyor
            </div>
          </div>

          <div class="stat-card stat-approved">
            <div class="stat-icon-wrapper success">
              <CheckCircle :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.approvedCount }}</span>
              <span class="stat-label">Onaylanan</span>
            </div>
          </div>

          <div class="stat-card stat-rejected">
            <div class="stat-icon-wrapper danger">
              <XCircle :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.rejectedCount }}</span>
              <span class="stat-label">Reddedilen</span>
            </div>
          </div>

          <div class="stat-card stat-today">
            <div class="stat-icon-wrapper accent">
              <Calendar :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ formatCurrency(stats.todayRevenue) }}</span>
              <span class="stat-label">Bugunun Geliri</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Filters Section -->
      <section class="filters-section">
        <div class="filters-wrapper">
          <!-- Search -->
          <div class="search-input-wrapper">
            <Search :size="18" class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Kullanıcı adı, işlem ID veya miktar ara..."
              class="search-input"
              @input="debouncedSearch"
            />
            <button v-if="searchQuery" class="clear-search" @click="clearSearch">
              <X :size="16" />
            </button>
          </div>

          <!-- Filter Pills -->
          <div class="filter-pills">
            <button
              class="filter-pill"
              :class="{ active: activeStatus === 'all' }"
              @click="setStatus('all')"
            >
              Tümu
            </button>
            <button
              class="filter-pill pending"
              :class="{ active: activeStatus === 'pending' }"
              @click="setStatus('pending')"
            >
              <span class="pill-dot pending"></span>
              Bekleyen
              <span v-if="pendingCount > 0" class="pill-count">{{ pendingCount }}</span>
            </button>
            <button
              class="filter-pill approved"
              :class="{ active: activeStatus === 'completed' }"
              @click="setStatus('completed')"
            >
              <span class="pill-dot approved"></span>
              Onaylanan
            </button>
            <button
              class="filter-pill rejected"
              :class="{ active: activeStatus === 'failed' }"
              @click="setStatus('failed')"
            >
              <span class="pill-dot rejected"></span>
              Reddedilen
            </button>
          </div>

          <!-- Advanced Filters -->
          <div class="advanced-filters">
            <div class="filter-group">
              <label>Ödeme Yontemi</label>
              <select v-model="filterMethod" class="filter-select" @change="fetchPayments">
                <option value="">Tüm Yontemler</option>
                <option value="bank">Banka Havalesi</option>
                <option value="papara">Papara</option>
                <option value="crypto">Kripto</option>
              </select>
            </div>

            <div class="filter-group">
              <label>Başlangıç Tarihi</label>
              <input
                type="date"
                v-model="filterDateFrom"
                class="filter-date"
                @change="fetchPayments"
              />
            </div>

            <div class="filter-group">
              <label>Bitis Tarihi</label>
              <input
                type="date"
                v-model="filterDateTo"
                class="filter-date"
                @change="fetchPayments"
              />
            </div>

            <button class="btn btn-ghost" @click="resetFilters">
              <RotateCcw :size="16" />
              Sifirla
            </button>
          </div>
        </div>
      </section>

      <!-- Table Section -->
      <section class="table-section">
        <div class="table-container">
          <!-- Loading State -->
          <div v-if="loading" class="loading-overlay">
            <div class="loader">
              <Loader2 :size="40" class="spin" />
              <span>Ödemeler yükleniyor...</span>
            </div>
          </div>

          <!-- Table -->
          <table class="data-table" v-else-if="payments.length > 0">
            <thead>
              <tr>
                <th class="checkbox-col">
                  <label class="checkbox-wrapper">
                    <input
                      type="checkbox"
                      :checked="allSelected"
                      @change="toggleSelectAll"
                      :disabled="pendingPayments.length === 0"
                    />
                    <span class="checkmark"></span>
                  </label>
                </th>
                <th class="sortable" @click="toggleSort('id')">
                  ID
                  <component :is="getSortIcon('id')" :size="14" />
                </th>
                <th>Kullanıcı</th>
                <th class="sortable" @click="toggleSort('amount')">
                  Tutar
                  <component :is="getSortIcon('amount')" :size="14" />
                </th>
                <th>Yontem</th>
                <th>Durum</th>
                <th class="sortable" @click="toggleSort('created_at')">
                  Tarih
                  <component :is="getSortIcon('created_at')" :size="14" />
                </th>
                <th class="actions-col">İşlemler</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="payment in payments"
                :key="payment.id"
                :class="{ selected: isSelected(payment.id) }"
                @click="payment.status === 'pending' ? toggleSelect(payment.id) : null"
              >
                <td class="checkbox-col">
                  <label class="checkbox-wrapper" v-if="payment.status === 'pending'" @click.stop>
                    <input
                      type="checkbox"
                      :checked="isSelected(payment.id)"
                      @change="toggleSelect(payment.id)"
                    />
                    <span class="checkmark"></span>
                  </label>
                </td>
                <td class="id-cell">
                  <span class="id-badge">#{{ payment.id }}</span>
                </td>
                <td>
                  <div
                    class="user-cell"
                    @mouseenter="showUserPreview($event, payment)"
                    @mouseleave="hideUserPreview"
                  >
                    <img :src="getUserAvatar(payment.username)" class="user-avatar" />
                    <div class="user-info">
                      <span class="user-name">{{ payment.username || 'N/A' }}</span>
                      <span class="user-email">{{ payment.email || '' }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="amount-cell">{{ formatCurrency(payment.amount) }}</span>
                </td>
                <td>
                  <span class="method-badge" :class="payment.method">
                    <component :is="getMethodIcon(payment.method)" :size="14" />
                    {{ getMethodLabel(payment.method) }}
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="payment.status">
                    <component :is="getStatusIcon(payment.status)" :size="14" />
                    {{ getStatusLabel(payment.status) }}
                  </span>
                </td>
                <td class="date-cell">
                  <div class="date-info">
                    <span class="date-primary">{{ formatDate(payment.created_at) }}</span>
                    <span class="date-secondary">{{ formatTime(payment.created_at) }}</span>
                  </div>
                </td>
                <td class="actions-col" @click.stop>
                  <div class="action-buttons">
                    <template v-if="payment.status === 'pending'">
                      <button
                        class="action-btn approve"
                        @click="confirmApprove(payment)"
                        title="Onayla"
                      >
                        <Check :size="16" />
                      </button>
                      <button
                        class="action-btn reject"
                        @click="openRejectModal(payment)"
                        title="Reddet"
                      >
                        <X :size="16" />
                      </button>
                    </template>
                    <button
                      class="action-btn view"
                      @click="viewPayment(payment)"
                      title="Detay"
                    >
                      <Eye :size="16" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Empty State -->
          <div v-else class="empty-state">
            <div class="empty-icon">
              <Receipt :size="64" />
            </div>
            <h3>Ödeme Bulunamadı</h3>
            <p>Seçilen kriterlere uygun ödeme kaydina rastlanmadi.</p>
            <button class="btn btn-outline" @click="resetFilters">
              <RotateCcw :size="16" />
              Filtreleri Sifirla
            </button>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <div class="pagination-info">
            {{ (currentPage - 1) * perPage + 1 }} - {{ Math.min(currentPage * perPage, totalPayments) }} / {{ totalPayments }} kayıt
          </div>
          <div class="pagination-controls">
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
          </div>
        </div>
      </section>

      <!-- User Preview Tooltip -->
      <Teleport to="body">
        <Transition name="tooltip">
          <div
            v-if="userPreview.visible"
            class="user-preview-tooltip"
            :style="{ top: userPreview.y + 'px', left: userPreview.x + 'px' }"
          >
            <div class="preview-header">
              <img :src="getUserAvatar(userPreview.data?.username)" class="preview-avatar" />
              <div class="preview-info">
                <span class="preview-name">{{ userPreview.data?.username }}</span>
                <span class="preview-email">{{ userPreview.data?.email || 'Email yok' }}</span>
              </div>
            </div>
            <div class="preview-stats">
              <div class="preview-stat">
                <span class="preview-stat-value">{{ userPreview.data?.total_payments || 0 }}</span>
                <span class="preview-stat-label">Toplam Ödeme</span>
              </div>
              <div class="preview-stat">
                <span class="preview-stat-value">{{ formatCurrency(userPreview.data?.total_spent || 0) }}</span>
                <span class="preview-stat-label">Toplam Harcama</span>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Payment Detail Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="selectedPayment" class="modal-backdrop" @click.self="closeModal">
            <div class="modal-container detail-modal">
              <div class="modal-header">
                <div class="modal-title">
                  <Receipt :size="24" />
                  <h2>Ödeme Detayi #{{ selectedPayment.id }}</h2>
                </div>
                <button class="modal-close" @click="closeModal">
                  <X :size="20" />
                </button>
              </div>

              <div class="modal-body">
                <!-- Amount & Status -->
                <div class="detail-hero">
                  <div class="detail-amount">{{ formatCurrency(selectedPayment.amount) }}</div>
                  <span class="status-badge large" :class="selectedPayment.status">
                    <component :is="getStatusIcon(selectedPayment.status)" :size="16" />
                    {{ getStatusLabel(selectedPayment.status) }}
                  </span>
                </div>

                <!-- User Info -->
                <div class="detail-section">
                  <h4>Kullanıcı Bilgileri</h4>
                  <div class="detail-card user-detail-card">
                    <img :src="getUserAvatar(selectedPayment.username)" class="detail-user-avatar" />
                    <div class="detail-user-info">
                      <span class="detail-user-name">{{ selectedPayment.username }}</span>
                      <span class="detail-user-email">{{ selectedPayment.email || 'Email bilgisi yok' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Payment Details Grid -->
                <div class="detail-section">
                  <h4>Ödeme Bilgileri</h4>
                  <div class="detail-grid">
                    <div class="detail-item">
                      <span class="detail-label">Ödeme Yontemi</span>
                      <span class="detail-value">
                        <span class="method-badge" :class="selectedPayment.method">
                          <component :is="getMethodIcon(selectedPayment.method)" :size="14" />
                          {{ getMethodLabel(selectedPayment.method) }}
                        </span>
                      </span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">Oluşturulma Tarihi</span>
                      <span class="detail-value">{{ formatFullDate(selectedPayment.created_at) }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">İşlem Tarihi</span>
                      <span class="detail-value">{{ formatFullDate(selectedPayment.processed_at) || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">Referans No</span>
                      <span class="detail-value mono">{{ selectedPayment.reference || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Proof Image -->
                <div v-if="selectedPayment.proof_url" class="detail-section">
                  <h4>Dekont / Kanit</h4>
                  <div class="proof-container">
                    <img
                      :src="selectedPayment.proof_url"
                      alt="Dekont"
                      class="proof-image"
                      @click="openImageViewer(selectedPayment.proof_url)"
                    />
                    <div class="proof-overlay">
                      <ZoomIn :size="24" />
                      <span>Buyutmek için tıkla</span>
                    </div>
                  </div>
                </div>

                <!-- Note -->
                <div v-if="selectedPayment.note" class="detail-section">
                  <h4>Kullanıcı Notu</h4>
                  <div class="note-card">
                    <MessageSquare :size="18" />
                    <p>{{ selectedPayment.note }}</p>
                  </div>
                </div>

                <!-- Reject Reason -->
                <div v-if="selectedPayment.reject_reason" class="detail-section">
                  <h4>Red Sebebi</h4>
                  <div class="reject-reason-card">
                    <AlertTriangle :size="18" />
                    <p>{{ selectedPayment.reject_reason }}</p>
                  </div>
                </div>
              </div>

              <!-- Modal Footer Actions -->
              <div v-if="selectedPayment.status === 'pending'" class="modal-footer">
                <button class="btn btn-danger" @click="openRejectModal(selectedPayment)">
                  <X :size="18" />
                  Reddet
                </button>
                <button class="btn btn-success" @click="confirmApprove(selectedPayment)">
                  <Check :size="18" />
                  Onayla
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Reject Reason Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showRejectModal" class="modal-backdrop" @click.self="closeRejectModal">
            <div class="modal-container reject-modal">
              <div class="modal-header">
                <div class="modal-title danger">
                  <AlertTriangle :size="24" />
                  <h2>Ödemeyi Reddet</h2>
                </div>
                <button class="modal-close" @click="closeRejectModal">
                  <X :size="20" />
                </button>
              </div>

              <div class="modal-body">
                <div class="reject-info">
                  <p>
                    <strong>{{ paymentToReject?.username }}</strong> kullanıcısının
                    <strong>{{ formatCurrency(paymentToReject?.amount) }}</strong> tutarındaki
                    ödemesini reddetmek uzeresiniz.
                  </p>
                </div>

                <div class="form-group">
                  <label for="rejectReason">Red Sebebi <span class="required">*</span></label>
                  <textarea
                    id="rejectReason"
                    v-model="rejectReason"
                    rows="4"
                    placeholder="Red sebebini açıklayin..."
                    class="form-textarea"
                  ></textarea>
                </div>

                <div class="quick-reasons">
                  <span class="quick-label">Hızlı Seçim:</span>
                  <button
                    v-for="reason in quickRejectReasons"
                    :key="reason"
                    class="quick-reason-btn"
                    @click="rejectReason = reason"
                  >
                    {{ reason }}
                  </button>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn btn-ghost" @click="closeRejectModal">İptal</button>
                <button class="btn btn-danger" @click="confirmReject" :disabled="!rejectReason.trim()">
                  <X :size="18" />
                  Reddet
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Approve Confirmation Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showApproveModal" class="modal-backdrop" @click.self="closeApproveModal">
            <div class="modal-container confirm-modal">
              <div class="modal-header">
                <div class="modal-title success">
                  <CheckCircle :size="24" />
                  <h2>Ödemeyi Onayla</h2>
                </div>
                <button class="modal-close" @click="closeApproveModal">
                  <X :size="20" />
                </button>
              </div>

              <div class="modal-body">
                <div class="confirm-content">
                  <div class="confirm-icon success">
                    <Check :size="48" />
                  </div>
                  <p>
                    <strong>{{ paymentToApprove?.username }}</strong> kullanıcısının
                    <strong>{{ formatCurrency(paymentToApprove?.amount) }}</strong> tutarındaki
                    ödemesini onaylamak istiyor musunuz?
                  </p>
                  <p class="confirm-warning">
                    Bu işlem geri alınamaz ve kullanıcının bakiyesine yansıtılacaktır.
                  </p>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn btn-ghost" @click="closeApproveModal">İptal</button>
                <button class="btn btn-success" @click="executeApprove">
                  <Check :size="18" />
                  Onayla
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Bulk Action Confirmation Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showBulkModal" class="modal-backdrop" @click.self="closeBulkModal">
            <div class="modal-container confirm-modal">
              <div class="modal-header">
                <div class="modal-title" :class="bulkAction">
                  <component :is="bulkAction === 'approve' ? CheckCircle : XCircle" :size="24" />
                  <h2>{{ bulkAction === 'approve' ? 'Toplu Onaylama' : 'Toplu Reddetme' }}</h2>
                </div>
                <button class="modal-close" @click="closeBulkModal">
                  <X :size="20" />
                </button>
              </div>

              <div class="modal-body">
                <div class="confirm-content">
                  <div class="confirm-icon" :class="bulkAction === 'approve' ? 'success' : 'danger'">
                    <component :is="bulkAction === 'approve' ? Check : X" :size="48" />
                  </div>
                  <p>
                    <strong>{{ selectedPayments.length }}</strong> adet ödemeyi
                    {{ bulkAction === 'approve' ? 'onaylamak' : 'reddetmek' }} istiyor musunuz?
                  </p>
                  <div class="bulk-total">
                    Toplam Tutar: <strong>{{ formatCurrency(selectedPaymentsTotal) }}</strong>
                  </div>

                  <!-- Reject reason for bulk reject -->
                  <div v-if="bulkAction === 'reject'" class="form-group" style="margin-top: 16px;">
                    <label for="bulkRejectReason">Red Sebebi <span class="required">*</span></label>
                    <textarea
                      id="bulkRejectReason"
                      v-model="bulkRejectReason"
                      rows="3"
                      placeholder="Red sebebini açıklayin..."
                      class="form-textarea"
                    ></textarea>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn btn-ghost" @click="closeBulkModal">İptal</button>
                <button
                  class="btn"
                  :class="bulkAction === 'approve' ? 'btn-success' : 'btn-danger'"
                  @click="executeBulkAction"
                  :disabled="bulkAction === 'reject' && !bulkRejectReason.trim()"
                >
                  <component :is="bulkAction === 'approve' ? Check : X" :size="18" />
                  {{ bulkAction === 'approve' ? 'Tümü Onayla' : 'Tümü Reddet' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Image Viewer Modal -->
      <Teleport to="body">
        <Transition name="fade">
          <div v-if="imageViewerUrl" class="image-viewer" @click="imageViewerUrl = null">
            <button class="viewer-close">
              <X :size="24" />
            </button>
            <img :src="imageViewerUrl" alt="Dekont" />
          </div>
        </Transition>
      </Teleport>

      <!-- Toast Notifications -->
      <Teleport to="body">
        <TransitionGroup name="toast" tag="div" class="toast-container">
          <div
            v-for="toast in toasts"
            :key="toast.id"
            class="toast"
            :class="toast.type"
          >
            <component :is="getToastIcon(toast.type)" :size="20" />
            <span>{{ toast.message }}</span>
          </div>
        </TransitionGroup>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Search,
  FileDown,
  Wallet,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  Calendar,
  Eye,
  Check,
  X,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Loader2,
  Receipt,
  AlertTriangle,
  MessageSquare,
  ZoomIn,
  RotateCcw,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  Building,
  Smartphone,
  Bitcoin,
  CreditCard,
  AlertCircle,
  Info
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()

// State
const loading = ref(false)
const payments = ref([])
const totalPayments = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 20

// Stats
const stats = reactive({
  totalRevenue: 0,
  todayRevenue: 0,
  approvedCount: 0,
  rejectedCount: 0
})
const pendingCount = ref(0)

// Filters
const activeStatus = ref('all')
const searchQuery = ref('')
const filterMethod = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const sortField = ref('created_at')
const sortOrder = ref('desc')

// Selection
const selectedPayments = ref([])

// Modals
const selectedPayment = ref(null)
const showRejectModal = ref(false)
const showApproveModal = ref(false)
const showBulkModal = ref(false)
const paymentToReject = ref(null)
const paymentToApprove = ref(null)
const rejectReason = ref('')
const bulkAction = ref('')
const bulkRejectReason = ref('')
const imageViewerUrl = ref(null)

// User Preview
const userPreview = reactive({
  visible: false,
  x: 0,
  y: 0,
  data: null
})

// Toasts
const toasts = ref([])

// Quick reject reasons
const quickRejectReasons = [
  'Dekont okunamıyor',
  'Tutar uyuşmuyor',
  'Gönderen bilgisi hatalı',
  'Geçersiz işlem',
  'Şüpheli işlem'
]

let searchTimeout = null
let toastId = 0

// Computed
const pendingPayments = computed(() => payments.value.filter(p => p.status === 'pending'))
const allSelected = computed(() => {
  return pendingPayments.value.length > 0 &&
    pendingPayments.value.every(p => selectedPayments.value.includes(p.id))
})
const selectedPaymentsTotal = computed(() => {
  return payments.value
    .filter(p => selectedPayments.value.includes(p.id))
    .reduce((sum, p) => sum + (p.amount || 0), 0)
})
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

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
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }
  return headers
}

// API Calls
const fetchPayments = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: perPage,
      sort: sortField.value,
      order: sortOrder.value
    })

    if (activeStatus.value !== 'all') params.append('status', activeStatus.value)
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
    // Error handled
    showToast('Ödemeler yüklenirken hata oluştu', 'error')
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
      stats.totalRevenue = data.payments?.total_revenue || 0
      stats.todayRevenue = data.payments?.today_revenue || 0
      stats.approvedCount = data.payments?.approved || 0
      stats.rejectedCount = data.payments?.rejected || 0
      pendingCount.value = data.payments?.pending || 0
    }
  } catch (error) {
    // Error handled
  }
}

// Search
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchPayments()
  }, 300)
}

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
  fetchPayments()
}

// Filters
const setStatus = (status) => {
  activeStatus.value = status
  currentPage.value = 1
  selectedPayments.value = []
  fetchPayments()
}

const resetFilters = () => {
  activeStatus.value = 'all'
  searchQuery.value = ''
  filterMethod.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  currentPage.value = 1
  selectedPayments.value = []
  fetchPayments()
}

// Sorting
const toggleSort = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
  fetchPayments()
}

const getSortIcon = (field) => {
  if (sortField.value !== field) return ArrowUpDown
  return sortOrder.value === 'asc' ? ArrowUp : ArrowDown
}

// Pagination
const goToPage = (page) => {
  currentPage.value = page
  selectedPayments.value = []
  fetchPayments()
}

// Selection
const isSelected = (id) => selectedPayments.value.includes(id)

const toggleSelect = (id) => {
  const index = selectedPayments.value.indexOf(id)
  if (index === -1) {
    selectedPayments.value.push(id)
  } else {
    selectedPayments.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedPayments.value = []
  } else {
    selectedPayments.value = pendingPayments.value.map(p => p.id)
  }
}

// Formatting
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy', { locale: tr })
}

const formatTime = (date) => {
  if (!date) return ''
  return format(new Date(date), 'HH:mm', { locale: tr })
}

const formatFullDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMMM yyyy HH:mm', { locale: tr })
}

const getUserAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}&backgroundColor=f97316`
}

// Labels and Icons
const getMethodLabel = (method) => {
  const labels = {
    bank: 'Banka Havalesi',
    papara: 'Papara',
    crypto: 'Kripto'
  }
  return labels[method] || 'Havale'
}

const getMethodIcon = (method) => {
  const icons = {
    bank: Building,
    papara: Smartphone,
    crypto: Bitcoin
  }
  return icons[method] || CreditCard
}

const getStatusLabel = (status) => {
  const labels = {
    pending: 'Bekliyor',
    completed: 'Onaylandı',
    failed: 'Reddedildi'
  }
  return labels[status] || status
}

const getStatusIcon = (status) => {
  const icons = {
    pending: Clock,
    completed: CheckCircle,
    failed: XCircle
  }
  return icons[status] || AlertCircle
}

// User Preview
let previewTimeout = null
const showUserPreview = (event, payment) => {
  previewTimeout = setTimeout(() => {
    const rect = event.target.getBoundingClientRect()
    userPreview.x = rect.left + rect.width / 2
    userPreview.y = rect.bottom + 10
    userPreview.data = {
      username: payment.username,
      email: payment.email,
      total_payments: payment.user_total_payments || 0,
      total_spent: payment.user_total_spent || 0
    }
    userPreview.visible = true
  }, 500)
}

const hideUserPreview = () => {
  clearTimeout(previewTimeout)
  userPreview.visible = false
}

// Modal Actions
const viewPayment = (payment) => {
  selectedPayment.value = payment
}

const closeModal = () => {
  selectedPayment.value = null
}

const confirmApprove = (payment) => {
  paymentToApprove.value = payment
  showApproveModal.value = true
}

const closeApproveModal = () => {
  showApproveModal.value = false
  paymentToApprove.value = null
}

const executeApprove = async () => {
  const payment = paymentToApprove.value
  try {
    const response = await fetch(`/api/admin/payments/${payment.id}/approve`, {
      method: 'POST',
      headers: getHeaders()
    })

    if (response.ok) {
      payment.status = 'completed'
      pendingCount.value = Math.max(0, pendingCount.value - 1)
      stats.approvedCount++
      closeApproveModal()
      closeModal()
      showToast('Ödeme başarıyla onaylandı', 'success')
      fetchPayments()
      fetchStats()
    } else {
      const data = await response.json()
      showToast(data.detail || 'Onaylama başarısız', 'error')
    }
  } catch (error) {
    // Error handled
    showToast('Bir hata oluştu', 'error')
  }
}

const openRejectModal = (payment) => {
  paymentToReject.value = payment
  rejectReason.value = ''
  showRejectModal.value = true
}

const closeRejectModal = () => {
  showRejectModal.value = false
  paymentToReject.value = null
  rejectReason.value = ''
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    showToast('Lütfen bir red sebebi yazın', 'warning')
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
      stats.rejectedCount++
      closeRejectModal()
      closeModal()
      showToast('Ödeme reddedildi', 'success')
      fetchPayments()
      fetchStats()
    } else {
      const data = await response.json()
      showToast(data.detail || 'Reddetme başarısız', 'error')
    }
  } catch (error) {
    // Error handled
    showToast('Bir hata oluştu', 'error')
  }
}

// Bulk Actions
const bulkApprove = () => {
  bulkAction.value = 'approve'
  showBulkModal.value = true
}

const bulkReject = () => {
  bulkAction.value = 'reject'
  bulkRejectReason.value = ''
  showBulkModal.value = true
}

const closeBulkModal = () => {
  showBulkModal.value = false
  bulkAction.value = ''
  bulkRejectReason.value = ''
}

const executeBulkAction = async () => {
  const action = bulkAction.value
  const ids = [...selectedPayments.value]
  let successCount = 0

  for (const id of ids) {
    try {
      const endpoint = action === 'approve'
        ? `/api/admin/payments/${id}/approve`
        : `/api/admin/payments/${id}/reject`

      const body = action === 'reject'
        ? JSON.stringify({ reason: bulkRejectReason.value })
        : undefined

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: getHeaders(),
        body
      })

      if (response.ok) {
        successCount++
        const payment = payments.value.find(p => p.id === id)
        if (payment) {
          payment.status = action === 'approve' ? 'completed' : 'failed'
        }
      }
    } catch (error) {
      // Error handled
    }
  }

  closeBulkModal()
  selectedPayments.value = []

  const actionText = action === 'approve' ? 'onaylandı' : 'reddedildi'
  showToast(`${successCount}/${ids.length} ödeme ${actionText}`, 'success')

  fetchPayments()
  fetchStats()
}

// Export
const exportPayments = () => {
  const params = new URLSearchParams()
  if (activeStatus.value !== 'all') params.append('status', activeStatus.value)
  if (filterDateFrom.value) params.append('from', filterDateFrom.value)
  if (filterDateTo.value) params.append('to', filterDateTo.value)
  params.append('format', 'csv')
  params.append('token', authStore.token)

  window.open(`/api/admin/payments/export?${params}`, '_blank')
  showToast('Rapor indirme başladı', 'info')
}

// Image Viewer
const openImageViewer = (url) => {
  imageViewerUrl.value = url
}

// Toast
const showToast = (message, type = 'info') => {
  const id = ++toastId
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) toasts.value.splice(index, 1)
  }, 4000)
}

const getToastIcon = (type) => {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertTriangle,
    info: Info
  }
  return icons[type] || Info
}

// Lifecycle
onMounted(() => {
  fetchPayments()
  fetchStats()
})
</script>

<style scoped>
/* ========================================
   CSS Variables (Dark Theme with Orange Accent)
   ======================================== */
.payments-page {
  --bg-primary: #0a0a0b;
  --bg-secondary: #111113;
  --bg-tertiary: #18181b;
  --bg-card: #1c1c1f;
  --bg-hover: #252529;

  --border-color: #27272a;
  --border-light: #3f3f46;

  --text-primary: #fafafa;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;

  --accent: #f97316;
  --accent-hover: #ea580c;
  --accent-light: rgba(249, 115, 22, 0.15);
  --accent-glow: rgba(249, 115, 22, 0.4);

  --success: #22c55e;
  --success-light: rgba(34, 197, 94, 0.15);
  --success-glow: rgba(34, 197, 94, 0.4);

  --warning: #eab308;
  --warning-light: rgba(234, 179, 8, 0.15);
  --warning-glow: rgba(234, 179, 8, 0.4);

  --danger: #ef4444;
  --danger-light: rgba(239, 68, 68, 0.15);
  --danger-glow: rgba(239, 68, 68, 0.4);

  --info: #3b82f6;
  --info-light: rgba(59, 130, 246, 0.15);

  min-height: 100vh;
  padding: 32px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* ========================================
   Animations
   ======================================== */
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.spin {
  animation: spin 1s linear infinite;
}

/* ========================================
   Page Header
   ======================================== */
.page-header {
  margin-bottom: 32px;
  animation: slideUp 0.4s ease-out;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.header-subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--warning);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* ========================================
   Buttons
   ======================================== */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-primary);
}

.btn-outline:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--accent);
  color: var(--accent);
}

.btn-outline-danger {
  background: transparent;
  border: 1px solid var(--danger);
  color: var(--danger);
}

.btn-outline-danger:hover:not(:disabled) {
  background: var(--danger-light);
}

.btn-success {
  background: var(--success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #16a34a;
  box-shadow: 0 0 20px var(--success-glow);
}

.btn-danger {
  background: var(--danger);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  box-shadow: 0 0 20px var(--danger-glow);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  padding: 10px 16px;
}

.btn-ghost:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* ========================================
   Stats Section
   ======================================== */
.stats-section {
  margin-bottom: 32px;
  animation: slideUp 0.4s ease-out 0.1s both;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-light);
  border-radius: 14px;
  color: var(--accent);
  flex-shrink: 0;
}

.stat-icon-wrapper.warning {
  background: var(--warning-light);
  color: var(--warning);
}

.stat-icon-wrapper.success {
  background: var(--success-light);
  color: var(--success);
}

.stat-icon-wrapper.danger {
  background: var(--danger-light);
  color: var(--danger);
}

.stat-icon-wrapper.accent {
  background: var(--accent-light);
  color: var(--accent);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 6px;
}

.stat-trend.positive {
  background: var(--success-light);
  color: var(--success);
}

.stat-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-badge.warning {
  background: var(--warning-light);
  color: var(--warning);
  animation: pulse 2s ease-in-out infinite;
}

/* ========================================
   Filters Section
   ======================================== */
.filters-section {
  margin-bottom: 24px;
  animation: slideUp 0.4s ease-out 0.2s both;
}

.filters-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 14px 44px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.clear-search {
  position: absolute;
  right: 12px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-hover);
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-search:hover {
  background: var(--danger-light);
  color: var(--danger);
}

/* Filter Pills */
.filter-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-pill:hover {
  background: var(--bg-hover);
  border-color: var(--border-light);
  color: var(--text-primary);
}

.filter-pill.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.pill-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.pill-dot.pending { background: var(--warning); }
.pill-dot.approved { background: var(--success); }
.pill-dot.rejected { background: var(--danger); }

.filter-pill.active .pill-dot {
  background: white;
}

.pill-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.filter-pill.active .pill-count {
  background: rgba(0, 0, 0, 0.2);
}

/* Advanced Filters */
.advanced-filters {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-select,
.filter-date {
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 160px;
}

.filter-select:focus,
.filter-date:focus {
  outline: none;
  border-color: var(--accent);
}

/* ========================================
   Table Section
   ======================================== */
.table-section {
  animation: slideUp 0.4s ease-out 0.3s both;
}

.table-container {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 10, 11, 0.9);
  z-index: 10;
}

.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-secondary);
}

.loader svg {
  color: var(--accent);
}

/* Data Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 16px 20px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: color 0.2s ease;
}

.data-table th.sortable:hover {
  color: var(--accent);
}

.data-table th.sortable svg {
  margin-left: 4px;
  opacity: 0.5;
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  vertical-align: middle;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr {
  transition: background-color 0.2s ease;
}

.data-table tr:hover td {
  background: var(--bg-hover);
}

.data-table tr.selected td {
  background: var(--accent-light);
}

/* Checkbox Column */
.checkbox-col {
  width: 50px;
  text-align: center;
}

.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.checkbox-wrapper input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-light);
  border-radius: 4px;
  transition: all 0.2s ease;
  position: relative;
}

.checkbox-wrapper input:checked + .checkmark {
  background: var(--accent);
  border-color: var(--accent);
}

.checkbox-wrapper input:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 1px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-wrapper input:disabled + .checkmark {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ID Cell */
.id-cell .id-badge {
  display: inline-block;
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  font-family: monospace;
  font-size: 13px;
  color: var(--text-secondary);
}

/* User Cell */
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  transition: all 0.2s ease;
}

.user-cell:hover .user-avatar {
  border-color: var(--accent);
  transform: scale(1.05);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
}

.user-email {
  font-size: 12px;
  color: var(--text-muted);
}

/* Amount Cell */
.amount-cell {
  font-weight: 600;
  font-size: 15px;
  color: var(--success);
}

/* Method Badge */
.method-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.method-badge.bank {
  background: var(--info-light);
  color: var(--info);
}

.method-badge.papara {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.method-badge.crypto {
  background: var(--accent-light);
  color: var(--accent);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: var(--warning-light);
  color: var(--warning);
}

.status-badge.completed {
  background: var(--success-light);
  color: var(--success);
}

.status-badge.failed {
  background: var(--danger-light);
  color: var(--danger);
}

.status-badge.large {
  font-size: 14px;
  padding: 8px 16px;
}

/* Date Cell */
.date-cell .date-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.date-primary {
  font-size: 13px;
  color: var(--text-primary);
}

.date-secondary {
  font-size: 11px;
  color: var(--text-muted);
}

/* Actions Column */
.actions-col {
  width: 140px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.approve {
  background: var(--success-light);
  color: var(--success);
}

.action-btn.approve:hover {
  background: var(--success);
  color: white;
  box-shadow: 0 0 15px var(--success-glow);
  transform: scale(1.1);
}

.action-btn.reject {
  background: var(--danger-light);
  color: var(--danger);
}

.action-btn.reject:hover {
  background: var(--danger);
  color: white;
  box-shadow: 0 0 15px var(--danger-glow);
  transform: scale(1.1);
}

.action-btn.view {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.action-btn.view:hover {
  background: var(--accent);
  color: white;
  box-shadow: 0 0 15px var(--accent-glow);
  transform: scale(1.1);
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
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 24px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-state p {
  color: var(--text-muted);
  margin: 0 0 24px 0;
}

/* ========================================
   Pagination
   ======================================== */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 16px 16px;
}

.pagination-info {
  font-size: 14px;
  color: var(--text-muted);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-num {
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-num:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.page-num.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

/* ========================================
   User Preview Tooltip
   ======================================== */
.user-preview-tooltip {
  position: fixed;
  z-index: 1000;
  width: 280px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  transform: translateX(-50%);
  pointer-events: none;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.preview-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 2px solid var(--accent);
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.preview-name {
  font-weight: 600;
  color: var(--text-primary);
}

.preview-email {
  font-size: 12px;
  color: var(--text-muted);
}

.preview-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.preview-stat {
  text-align: center;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.preview-stat-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--accent);
}

.preview-stat-label {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Tooltip Animation */
.tooltip-enter-active,
.tooltip-leave-active {
  transition: all 0.2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

/* ========================================
   Modals
   ======================================== */
.modal-backdrop {
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
  max-width: 560px;
  max-height: 90vh;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.detail-modal {
  max-width: 600px;
}

.confirm-modal {
  max-width: 440px;
}

.reject-modal {
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--accent);
}

.modal-title.danger {
  color: var(--danger);
}

.modal-title.success {
  color: var(--success);
}

.modal-title h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--danger-light);
  color: var(--danger);
}

.modal-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

/* Detail Modal */
.detail-hero {
  text-align: center;
  padding: 24px;
  background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary));
  border-radius: 16px;
  margin-bottom: 24px;
}

.detail-amount {
  font-size: 36px;
  font-weight: 700;
  color: var(--success);
  margin-bottom: 12px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px 0;
}

.detail-card {
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.user-detail-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  border: 2px solid var(--accent);
}

.detail-user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-user-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.detail-user-email {
  font-size: 13px;
  color: var(--text-muted);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  padding: 14px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.detail-label {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.detail-value.mono {
  font-family: monospace;
}

/* Proof Section */
.proof-container {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}

.proof-image {
  width: 100%;
  display: block;
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.proof-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.proof-container:hover .proof-overlay {
  opacity: 1;
}

.proof-container:hover .proof-image {
  transform: scale(1.02);
}

/* Note & Reject Cards */
.note-card,
.reject-reason-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.note-card svg {
  flex-shrink: 0;
  color: var(--text-muted);
}

.note-card p,
.reject-reason-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.reject-reason-card {
  border-left: 3px solid var(--danger);
}

.reject-reason-card svg {
  color: var(--danger);
}

/* Confirm Modal */
.confirm-content {
  text-align: center;
}

.confirm-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  border-radius: 50%;
}

.confirm-icon.success {
  background: var(--success-light);
  color: var(--success);
}

.confirm-icon.danger {
  background: var(--danger-light);
  color: var(--danger);
}

.confirm-content p {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.confirm-warning {
  font-size: 13px;
  color: var(--text-muted);
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.bulk-total {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  font-size: 16px;
  color: var(--text-secondary);
}

.bulk-total strong {
  color: var(--success);
}

/* Reject Modal */
.reject-info {
  padding: 16px;
  background: var(--danger-light);
  border-radius: 12px;
  margin-bottom: 20px;
}

.reject-info p {
  margin: 0;
  color: var(--text-secondary);
}

.reject-info strong {
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.required {
  color: var(--danger);
}

.form-textarea {
  width: 100%;
  padding: 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  resize: vertical;
  transition: all 0.2s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.quick-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.quick-label {
  font-size: 12px;
  color: var(--text-muted);
}

.quick-reason-btn {
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-reason-btn:hover {
  background: var(--accent-light);
  border-color: var(--accent);
  color: var(--accent);
}

/* Modal Animation */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9) translateY(20px);
}

/* ========================================
   Image Viewer
   ======================================== */
.image-viewer {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  cursor: pointer;
}

.image-viewer img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.viewer-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.viewer-close:hover {
  background: var(--danger);
}

/* Fade Animation */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ========================================
   Toast Notifications
   ======================================== */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 3000;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  min-width: 280px;
}

.toast.success {
  border-left: 4px solid var(--success);
}

.toast.success svg {
  color: var(--success);
}

.toast.error {
  border-left: 4px solid var(--danger);
}

.toast.error svg {
  color: var(--danger);
}

.toast.warning {
  border-left: 4px solid var(--warning);
}

.toast.warning svg {
  color: var(--warning);
}

.toast.info {
  border-left: 4px solid var(--info);
}

.toast.info svg {
  color: var(--info);
}

/* Toast Animation */
.toast-enter-active {
  animation: slideInRight 0.3s ease;
}

.toast-leave-active {
  animation: slideOutRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOutRight {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100px);
  }
}

/* ========================================
   Responsive Design
   ======================================== */
@media (max-width: 1024px) {
  .payments-page {
    padding: 20px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filter-pills {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 8px;
    -webkit-overflow-scrolling: touch;
  }

  .filter-pill {
    flex-shrink: 0;
  }

  .advanced-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    width: 100%;
  }

  .filter-select,
  .filter-date {
    width: 100%;
  }

  .data-table {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .pagination {
    flex-direction: column;
    gap: 16px;
  }

  .modal-container {
    margin: 10px;
    max-height: calc(100vh - 20px);
  }
}

@media (max-width: 480px) {
  .page-numbers {
    display: none;
  }

  .toast {
    min-width: auto;
    max-width: calc(100vw - 40px);
  }

  .toast-container {
    left: 20px;
    right: 20px;
  }
}
</style>
