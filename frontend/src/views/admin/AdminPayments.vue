<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-2xl font-bold text-text-primary">Ödeme İşlemleri</h1>
        <router-link to="/admin" class="text-primary text-sm hover:text-primary-light">← Admin Panel</router-link>
      </div>
      <p class="text-text-muted text-sm">Bekleyen ödemeleri onayla veya reddet</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Bekleyen</div>
        <div class="text-2xl font-bold text-status-warning">{{ stats.pending || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Onaylanan</div>
        <div class="text-2xl font-bold text-status-success">{{ stats.completed || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Reddedilen</div>
        <div class="text-2xl font-bold text-status-error">{{ stats.cancelled || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-text-muted text-xs mb-1">Toplam Gelir</div>
        <div class="text-2xl font-bold text-primary">₺{{ (stats.total_revenue || 0).toFixed(2) }}</div>
      </div>
    </div>

    <!-- Pending Payments -->
    <div class="card mb-4">
      <div class="p-4 border-b border-dark-border">
        <h2 class="text-lg font-bold text-text-primary">Bekleyen Ödemeler</h2>
      </div>

      <div v-if="loadingPending" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">⏳</div>
        <p class="text-sm">Ödemeler yükleniyor...</p>
      </div>

      <div v-else-if="pendingPayments.length === 0" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">✅</div>
        <p class="text-sm">Bekleyen ödeme yok</p>
      </div>

      <div v-else class="divide-y divide-dark-border">
        <div v-for="payment in pendingPayments" :key="payment.id" class="p-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <span class="font-bold text-text-primary">{{ payment.username }}</span>
                <span class="badge badge-warning">Bekliyor</span>
              </div>
              <div class="text-sm text-text-secondary mb-1">
                Tutar: <span class="font-bold text-primary">₺{{ payment.amount }}</span>
              </div>
              <div class="text-sm text-text-muted mb-1">
                Yöntem: {{ getPaymentMethod(payment.method) }}
              </div>
              <div class="text-sm text-text-muted mb-1">
                Referans: {{ payment.reference_code }}
              </div>
              <div v-if="payment.bank_transfer" class="mt-2 p-2 bg-dark-elevated rounded text-xs">
                <div class="text-text-secondary">Gönderen: {{ payment.bank_transfer.sender_name }}</div>
                <div class="text-text-muted">IBAN: {{ payment.bank_transfer.sender_iban }}</div>
                <div v-if="payment.bank_transfer.notes" class="text-text-muted mt-1">Not: {{ payment.bank_transfer.notes }}</div>
              </div>
              <div class="text-xs text-text-muted mt-2">
                {{ formatDate(payment.created_at) }}
              </div>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button @click="approvePayment(payment)" class="btn btn-primary text-sm">
                ✓ Onayla
              </button>
              <button @click="rejectPayment(payment)" class="btn btn-secondary text-sm">
                ✗ Reddet
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- All Payments -->
    <div class="card overflow-hidden">
      <div class="p-4 border-b border-dark-border flex items-center justify-between">
        <h2 class="text-lg font-bold text-text-primary">Tüm Ödemeler</h2>
        <select v-model="filterStatus" @change="fetchPayments" class="input w-48">
          <option value="">Tüm Durumlar</option>
          <option value="pending">Bekleyen</option>
          <option value="completed">Onaylanan</option>
          <option value="cancelled">Reddedilen</option>
        </select>
      </div>

      <div v-if="loading" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">⏳</div>
        <p class="text-sm">Ödemeler yükleniyor...</p>
      </div>

      <div v-else-if="payments.length === 0" class="p-8 text-center text-text-muted">
        <div class="text-3xl mb-2">💳</div>
        <p class="text-sm">Ödeme bulunamadı</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Kullanıcı</th>
              <th>Tutar</th>
              <th>Yöntem</th>
              <th>Durum</th>
              <th>Tarih</th>
              <th>Açıklama</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in payments" :key="payment.id">
              <td class="text-text-muted text-sm">{{ payment.id }}</td>
              <td class="font-medium text-text-primary">{{ payment.username }}</td>
              <td class="font-bold text-primary">₺{{ payment.amount }}</td>
              <td class="text-text-secondary text-sm">{{ getPaymentMethod(payment.method) }}</td>
              <td>
                <span class="badge text-xs" :class="getStatusBadge(payment.status)">
                  {{ getStatusText(payment.status) }}
                </span>
              </td>
              <td class="text-text-muted text-sm">{{ formatDate(payment.created_at) }}</td>
              <td class="text-text-muted text-sm truncate max-w-xs">{{ payment.description || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="border-t border-dark-border p-4">
        <div class="flex items-center justify-between">
          <div class="text-sm text-text-muted">
            Toplam {{ total }} ödeme
          </div>
          <div class="flex gap-2">
            <button
              @click="page--"
              :disabled="page === 1"
              class="pagination-btn"
            >
              ← Önceki
            </button>
            <span class="px-3 py-1.5 text-sm text-text-secondary">
              Sayfa {{ page }} / {{ totalPages }}
            </span>
            <button
              @click="page++"
              :disabled="page === totalPages"
              class="pagination-btn"
            >
              Sonraki →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import apiClient from '@/api/client'

const loading = ref(true)
const loadingPending = ref(true)
const payments = ref([])
const pendingPayments = ref([])
const stats = ref({})
const total = ref(0)
const page = ref(1)
const perPage = ref(20)
const totalPages = ref(0)
const filterStatus = ref('')

onMounted(() => {
  fetchStats()
  fetchPendingPayments()
  fetchPayments()
})

watch(page, () => {
  fetchPayments()
})

const fetchStats = async () => {
  try {
    const response = await apiClient.get('/admin/payments/stats')
    stats.value = response.data || {}
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchPendingPayments = async () => {
  try {
    loadingPending.value = true
    const response = await apiClient.get('/admin/commerce/payments/pending')
    pendingPayments.value = response.data.data?.payments || []
  } catch (error) {
    console.error('Failed to fetch pending payments:', error)
  } finally {
    loadingPending.value = false
  }
}

const fetchPayments = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      per_page: perPage.value
    }

    if (filterStatus.value) params.status = filterStatus.value

    const response = await apiClient.get('/admin/commerce/payments', { params })
    payments.value = response.data.data || []
    total.value = response.data.total || 0
    totalPages.value = Math.ceil(total.value / perPage.value)
  } catch (error) {
    console.error('Failed to fetch payments:', error)
    payments.value = []
  } finally {
    loading.value = false
  }
}

const approvePayment = async (payment) => {
  if (!confirm(`${payment.username} kullanıcısının ₺${payment.amount} tutarındaki ödemesini onaylamak istediğinize emin misiniz?`)) return

  try {
    await apiClient.post(`/admin/commerce/payments/${payment.id}/approve`)
    alert('Ödeme onaylandı!')
    await fetchPendingPayments()
    await fetchPayments()
    await fetchStats()
  } catch (error) {
    alert('Ödeme onaylanamadı: ' + (error.response?.data?.detail || 'Bilinmeyen hata'))
  }
}

const rejectPayment = async (payment) => {
  const reason = prompt(`Ödeme reddetme nedeni:`)
  if (!reason) return

  try {
    await apiClient.post(`/admin/commerce/payments/${payment.id}/reject`, { reason })
    alert('Ödeme reddedildi!')
    await fetchPendingPayments()
    await fetchPayments()
  } catch (error) {
    alert('Ödeme reddedilemedi: ' + (error.response?.data?.detail || 'Bilinmeyen hata'))
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getPaymentMethod = (method) => {
  const methods = {
    bank_transfer: 'Banka Havalesi',
    credit_card: 'Kredi Kartı',
    balance: 'Bakiye',
    papara: 'Papara'
  }
  return methods[method] || method || 'N/A'
}

const getStatusBadge = (status) => {
  const badges = {
    pending: 'badge-warning',
    completed: 'badge-success',
    cancelled: 'badge-error'
  }
  return badges[status] || 'badge-neutral'
}

const getStatusText = (status) => {
  const texts = {
    pending: 'Bekliyor',
    completed: 'Onaylandı',
    cancelled: 'Reddedildi'
  }
  return texts[status] || status
}
</script>
