<template>
  <div class="container mx-auto px-4 py-8 max-w-[1200px]">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-text-primary mb-2">Cüzdan</h1>
        <p class="text-text-secondary">Bakiyenizi yönetin ve işlem geçmişinizi görüntüleyin</p>
      </div>
      <button @click="showAddFunds = true" class="btn btn-primary">
        💰 Bakiye Yükle
      </button>
    </div>

    <!-- Balance Card -->
    <div class="card p-8 mb-8 bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-text-muted mb-2">Mevcut Bakiye</p>
          <h2 class="text-4xl font-bold text-primary">₺{{ balance.toFixed(2) }}</h2>
          <p class="text-sm text-text-secondary mt-2">
            Son güncelleme: {{ formatDate(new Date()) }}
          </p>
        </div>
        <div class="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center">
          <svg class="w-12 h-12 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="card p-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 rounded-lg bg-status-success/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-status-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
          </div>
          <span class="text-text-muted text-sm">Bu Ay Yükleme</span>
        </div>
        <p class="text-2xl font-bold text-text-primary">₺{{ monthlyDeposit.toFixed(2) }}</p>
      </div>

      <div class="card p-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 rounded-lg bg-status-error/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-status-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
            </svg>
          </div>
          <span class="text-text-muted text-sm">Bu Ay Harcama</span>
        </div>
        <p class="text-2xl font-bold text-text-primary">₺{{ monthlySpent.toFixed(2) }}</p>
      </div>

      <div class="card p-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 rounded-lg bg-status-info/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-status-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
          </div>
          <span class="text-text-muted text-sm">Toplam İşlem</span>
        </div>
        <p class="text-2xl font-bold text-text-primary">{{ totalTransactions }}</p>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-text-primary">İşlem Geçmişi</h2>
        <div class="flex gap-2">
          <button
            v-for="filter in filters"
            :key="filter.value"
            @click="currentFilter = filter.value"
            class="px-4 py-2 rounded-lg text-sm transition-colors"
            :class="currentFilter === filter.value
              ? 'bg-primary text-white'
              : 'bg-dark-elevated text-text-secondary hover:bg-dark-hover'"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 5" :key="i" class="skeleton h-16 rounded-lg"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredTransactions.length === 0" class="text-center py-12">
        <svg class="w-16 h-16 mx-auto mb-4 text-text-muted opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <p class="text-text-muted">Henüz işlem yok</p>
      </div>

      <!-- Transactions List -->
      <div v-else class="space-y-3">
        <div
          v-for="transaction in filteredTransactions"
          :key="transaction.id"
          class="flex items-center gap-4 p-4 rounded-lg border border-dark-border hover:border-primary/50 transition-colors"
        >
          <!-- Icon -->
          <div
            class="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
            :class="transaction.type === 'deposit'
              ? 'bg-status-success/10'
              : 'bg-status-error/10'"
          >
            <svg
              class="w-6 h-6"
              :class="transaction.type === 'deposit' ? 'text-status-success' : 'text-status-error'"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                v-if="transaction.type === 'deposit'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 12H4"
              />
            </svg>
          </div>

          <!-- Details -->
          <div class="flex-1 min-w-0">
            <p class="font-medium text-text-primary">{{ transaction.description }}</p>
            <p class="text-sm text-text-muted">{{ formatDate(transaction.created_at) }}</p>
          </div>

          <!-- Amount -->
          <div class="text-right">
            <p
              class="text-lg font-semibold"
              :class="transaction.type === 'deposit' ? 'text-status-success' : 'text-status-error'"
            >
              {{ transaction.type === 'deposit' ? '+' : '-' }}₺{{ Math.abs(transaction.amount).toFixed(2) }}
            </p>
            <span
              class="badge text-xs"
              :class="{
                'badge-success': transaction.status === 'completed',
                'badge-warning': transaction.status === 'pending',
                'badge-error': transaction.status === 'failed'
              }"
            >
              {{ getStatusLabel(transaction.status) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !loading" class="text-center pt-6">
        <button @click="loadMore" class="btn btn-secondary">
          Daha Fazla Yükle
        </button>
      </div>
    </div>

    <!-- Add Funds Modal -->
    <div v-if="showAddFunds" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="card p-6 max-w-md w-full">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-text-primary">Bakiye Yükle</h3>
          <button @click="showAddFunds = false" class="text-text-muted hover:text-text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitAddFunds" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Miktar (₺)</label>
            <input
              v-model.number="addFundsAmount"
              type="number"
              min="10"
              step="10"
              class="input"
              placeholder="100"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-text-primary mb-2">Ödeme Yöntemi</label>
            <select v-model="paymentMethod" class="input" required>
              <option value="">Seçiniz</option>
              <option value="credit_card">Kredi Kartı</option>
              <option value="bank_transfer">Banka Havalesi</option>
              <option value="papara">Papara</option>
              <option value="paypal">PayPal</option>
            </select>
          </div>

          <div class="bg-dark-elevated p-4 rounded-lg">
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-text-muted">Miktar:</span>
              <span class="text-text-primary font-medium">₺{{ addFundsAmount }}</span>
            </div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-text-muted">İşlem Ücreti:</span>
              <span class="text-text-primary font-medium">₺0.00</span>
            </div>
            <div class="border-t border-dark-border pt-2 mt-2">
              <div class="flex items-center justify-between">
                <span class="text-text-primary font-semibold">Toplam:</span>
                <span class="text-primary font-bold text-lg">₺{{ addFundsAmount }}</span>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button type="button" @click="showAddFunds = false" class="btn btn-secondary flex-1">
              İptal
            </button>
            <button type="submit" class="btn btn-primary flex-1">
              Ödemeye Geç
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import walletAPI from '@/api/wallet'

const authStore = useAuthStore()

const balance = ref(0)
const monthlyDeposit = ref(0)
const monthlySpent = ref(0)
const totalTransactions = ref(0)
const transactions = ref([])
const loading = ref(true)
const hasMore = ref(false)
const currentFilter = ref('all')
const showAddFunds = ref(false)
const addFundsAmount = ref(100)
const paymentMethod = ref('')

const filters = [
  { value: 'all', label: 'Tümü' },
  { value: 'deposit', label: 'Yükleme' },
  { value: 'withdraw', label: 'Harcama' }
]

const filteredTransactions = computed(() => {
  if (currentFilter.value === 'all') return transactions.value
  return transactions.value.filter(t => t.type === currentFilter.value)
})

onMounted(async () => {
  await fetchWalletData()
})

const fetchWalletData = async () => {
  try {
    loading.value = true

    // Fetch balance
    const balanceResponse = await walletAPI.getBalance()
    balance.value = balanceResponse.data.balance_real || 0

    // Fetch transactions
    const txResponse = await walletAPI.getTransactions({
      wallet_type: 'real',
      limit: 50
    })
    transactions.value = txResponse.data || []
    totalTransactions.value = transactions.value.length

    // Calculate monthly stats
    const now = new Date()
    const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)

    const monthlyTxs = transactions.value.filter(tx => {
      const txDate = new Date(tx.created_at)
      return txDate >= firstDayOfMonth
    })

    monthlyDeposit.value = monthlyTxs
      .filter(tx => tx.amount > 0)
      .reduce((sum, tx) => sum + tx.amount, 0)

    monthlySpent.value = Math.abs(monthlyTxs
      .filter(tx => tx.amount < 0)
      .reduce((sum, tx) => sum + tx.amount, 0))

  } catch (error) {
    console.error('Failed to fetch wallet data:', error)
    // Fallback to auth store balance
    balance.value = authStore.balance?.balance_real || 0
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusLabel = (status) => {
  const labels = {
    completed: 'Tamamlandı',
    pending: 'Beklemede',
    failed: 'Başarısız'
  }
  return labels[status] || status
}

const loadMore = async () => {
  try {
    const offset = transactions.value.length
    const txResponse = await walletAPI.getTransactions({
      wallet_type: 'real',
      limit: 50,
      offset
    })

    const newTxs = txResponse.data || []
    transactions.value.push(...newTxs)
    hasMore.value = newTxs.length === 50
  } catch (error) {
    console.error('Failed to load more transactions:', error)
  }
}

const submitAddFunds = async () => {
  try {
    if (!paymentMethod.value) {
      alert('Lütfen ödeme yöntemi seçiniz')
      return
    }

    const response = await walletAPI.deposit({
      amount: addFundsAmount.value,
      payment_method: paymentMethod.value
    })

    if (response.data.success) {
      // Refresh wallet data
      await fetchWalletData()
      await authStore.fetchBalance()

      showAddFunds.value = false
      addFundsAmount.value = 100
      paymentMethod.value = ''

      alert('Bakiye yükleme başarılı!')
    }
  } catch (error) {
    console.error('Add funds error:', error)
    alert(error.response?.data?.detail || 'Bakiye yüklenirken hata oluştu')
  }
}
</script>
