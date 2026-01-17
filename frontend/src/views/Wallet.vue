<template>
  <div class="wallet-page">
    <div class="container-custom py-8">
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">
          <Wallet :size="32" />
          Cuzdan
        </h1>
        <p class="page-desc">Bakiyeni yonet, TL yukle ve Armor'a donustur</p>
      </div>

      <!-- Balance Cards -->
      <div class="balance-cards">
        <div class="balance-card tl">
          <div class="card-icon">
            <Banknote :size="32" />
          </div>
          <div class="card-info">
            <span class="card-label">TL Bakiye</span>
            <span class="card-value">{{ formatCurrency(user?.balance || 0) }} TL</span>
          </div>
          <button class="card-action" @click="showDepositModal = true">
            <Plus :size="18" />
            TL Yukle
          </button>
        </div>

        <div class="balance-card armor">
          <div class="card-icon armor-icon">
            <img :src="armorIconUrl" alt="Armor" />
          </div>
          <div class="card-info">
            <span class="card-label">Armor Bakiye</span>
            <span class="card-value">{{ formatNumber(user?.balance_coin || 0) }} Armor</span>
          </div>
          <button class="card-action" @click="showConvertModal = true">
            <ArrowRightLeft :size="18" />
            Donustur
          </button>
        </div>

        <div class="balance-card rate">
          <div class="card-icon">
            <TrendingUp :size="32" />
          </div>
          <div class="card-info">
            <span class="card-label">Donusum Orani</span>
            <span class="card-value">1 TL = {{ armorRate }} Armor</span>
          </div>
          <span class="rate-info">Sabit oran</span>
        </div>
      </div>

      <!-- Armor Packages -->
      <div class="section">
        <div class="section-header">
          <h2>Armor Paketleri</h2>
          <p>TL ile Armor satin al, bonus kazan!</p>
        </div>

        <div class="packages-grid">
          <div
            v-for="pkg in armorPackages"
            :key="pkg.id"
            class="package-card"
            :class="{ featured: pkg.is_featured, selected: selectedPackage?.id === pkg.id }"
            @click="selectPackage(pkg)"
          >
            <div v-if="pkg.bonus_percent > 0" class="package-badge">
              +{{ pkg.bonus_percent }}% Bonus
            </div>
            <div class="package-icon armor-pkg-icon">
              <img :src="armorIconUrl" alt="Armor" />
            </div>
            <div class="package-amount">{{ formatNumber(pkg.armor_amount) }}</div>
            <div class="package-name">Armor</div>
            <div v-if="pkg.bonus_percent > 0" class="package-bonus">
              +{{ formatNumber(Math.floor(pkg.armor_amount * pkg.bonus_percent / 100)) }} Bonus
            </div>
            <div class="package-price">{{ formatCurrency(pkg.tl_amount) }} TL</div>
            <button class="package-btn" @click.stop="buyPackage(pkg)">
              Satin Al
            </button>
          </div>
        </div>
      </div>

      <!-- Transaction History -->
      <div class="section">
        <div class="section-header">
          <h2>Islem Gecmisi</h2>
        </div>

        <div class="transactions-table">
          <table>
            <thead>
              <tr>
                <th>Tarih</th>
                <th>Islem</th>
                <th>Miktar</th>
                <th>Durum</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tx in transactions" :key="tx.id">
                <td>{{ formatDate(tx.created_at) }}</td>
                <td>
                  <div class="tx-type">
                    <component :is="getTxIcon(tx.type)" :size="16" />
                    {{ getTxLabel(tx.type) }}
                  </div>
                </td>
                <td :class="tx.amount > 0 ? 'positive' : 'negative'">
                  {{ tx.amount > 0 ? '+' : '' }}{{ formatNumber(tx.amount) }}
                  {{ tx.wallet_type === 'REAL' ? 'TL' : 'Armor' }}
                </td>
                <td>
                  <span class="status-badge" :class="tx.status">
                    {{ getStatusLabel(tx.status) }}
                  </span>
                </td>
              </tr>
              <tr v-if="transactions.length === 0">
                <td colspan="4" class="empty-row">
                  <Receipt :size="32" />
                  <span>Henuz islem yok</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TL Deposit Modal -->
    <Teleport to="body">
      <div v-if="showDepositModal" class="modal-overlay" @click.self="showDepositModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>TL Yukle</h3>
            <button class="close-btn" @click="showDepositModal = false">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="deposit-info">
              <p>Hesabiniza TL yuklemek icin asagidaki yontemlerden birini secin.</p>
            </div>

            <div class="amount-input">
              <label>Yuklenecek Miktar</label>
              <div class="input-group">
                <input
                  v-model.number="depositAmount"
                  type="number"
                  min="10"
                  max="10000"
                  placeholder="0.00"
                />
                <span class="input-suffix">TL</span>
              </div>
              <div class="quick-amounts">
                <button @click="depositAmount = 50">50 TL</button>
                <button @click="depositAmount = 100">100 TL</button>
                <button @click="depositAmount = 250">250 TL</button>
                <button @click="depositAmount = 500">500 TL</button>
              </div>
            </div>

            <div class="payment-methods">
              <label>Odeme Yontemi</label>
              <div class="methods-grid">
                <div
                  v-for="method in paymentMethods"
                  :key="method.id"
                  class="method-card"
                  :class="{ selected: selectedMethod === method.id }"
                  @click="selectedMethod = method.id"
                >
                  <component :is="method.icon" :size="24" />
                  <span>{{ method.name }}</span>
                </div>
              </div>
            </div>

            <div v-if="depositAmount >= 10" class="deposit-summary">
              <div class="summary-row">
                <span>Yukleme Miktari</span>
                <span>{{ formatCurrency(depositAmount) }} TL</span>
              </div>
              <div class="summary-row total">
                <span>Hesabiniza Eklenecek</span>
                <span>{{ formatCurrency(depositAmount) }} TL</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showDepositModal = false">Iptal</button>
            <button
              class="btn-primary"
              @click="processDeposit"
              :disabled="depositAmount < 10 || !selectedMethod || depositing"
            >
              <Loader2 v-if="depositing" :size="18" class="spin" />
              <span v-else>Odemeye Devam Et</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- TL to Armor Conversion Modal -->
    <Teleport to="body">
      <div v-if="showConvertModal" class="modal-overlay" @click.self="showConvertModal = false">
        <div class="modal-content convert-modal">
          <div class="modal-header">
            <h3>TL'yi Armor'a Donustur</h3>
            <button class="close-btn" @click="showConvertModal = false">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="convert-rate">
              <div class="rate-display">
                <span class="rate-value">1 TL</span>
                <ArrowRight :size="20" />
                <span class="rate-value armor">{{ armorRate }} Armor</span>
              </div>
            </div>

            <div class="convert-form">
              <div class="convert-input">
                <label>TL Miktari</label>
                <div class="input-group">
                  <input
                    v-model.number="convertAmount"
                    type="number"
                    :min="1"
                    :max="user?.balance || 0"
                    placeholder="0.00"
                  />
                  <span class="input-suffix">TL</span>
                </div>
                <div class="input-hint">
                  Mevcut: {{ formatCurrency(user?.balance || 0) }} TL
                </div>
              </div>

              <div class="convert-arrow">
                <ArrowDown :size="24" />
              </div>

              <div class="convert-result">
                <label>Alacaginiz Armor</label>
                <div class="result-display">
                  <ShieldCheck :size="24" />
                  <span class="result-value">{{ formatNumber(convertAmount * armorRate) }}</span>
                  <span class="result-label">Armor</span>
                </div>
              </div>

              <div class="quick-convert">
                <button @click="convertAmount = 10">10 TL</button>
                <button @click="convertAmount = 50">50 TL</button>
                <button @click="convertAmount = 100">100 TL</button>
                <button @click="convertAmount = user?.balance || 0">Tumu</button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showConvertModal = false">Iptal</button>
            <button
              class="btn-primary"
              @click="processConversion"
              :disabled="convertAmount < 1 || convertAmount > (user?.balance || 0) || converting"
            >
              <Loader2 v-if="converting" :size="18" class="spin" />
              <span v-else>Donustur</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  Wallet,
  Banknote,
  ShieldCheck,
  Plus,
  ArrowRightLeft,
  TrendingUp,
  X,
  Loader2,
  ArrowRight,
  ArrowDown,
  CreditCard,
  Building2,
  Smartphone,
  Receipt,
  ArrowUpRight,
  ArrowDownLeft,
  RefreshCw
} from 'lucide-vue-next'

const authStore = useAuthStore()

// Auth headers helper
const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authStore.token}`
})

// State
const showDepositModal = ref(false)
const showConvertModal = ref(false)
const depositAmount = ref(100)
const convertAmount = ref(10)
const selectedMethod = ref(null)
const selectedPackage = ref(null)
const depositing = ref(false)
const converting = ref(false)
const transactions = ref([])

// Constants
const armorRate = 100 // 1 TL = 100 Armor
const armorIconUrl = '/static/images/icons/armor.png'

// Computed
const user = computed(() => authStore.user)

// Armor Packages
const armorPackages = ref([
  { id: 1, name: 'Baslangic', tl_amount: 10, armor_amount: 1000, bonus_percent: 0, is_featured: false },
  { id: 2, name: 'Standart', tl_amount: 25, armor_amount: 2500, bonus_percent: 5, is_featured: false },
  { id: 3, name: 'Populer', tl_amount: 50, armor_amount: 5000, bonus_percent: 10, is_featured: true },
  { id: 4, name: 'Premium', tl_amount: 100, armor_amount: 10000, bonus_percent: 15, is_featured: false },
  { id: 5, name: 'Elite', tl_amount: 250, armor_amount: 25000, bonus_percent: 20, is_featured: false },
  { id: 6, name: 'Legend', tl_amount: 500, armor_amount: 50000, bonus_percent: 25, is_featured: false }
])

// Payment Methods
const paymentMethods = [
  { id: 'card', name: 'Kredi Karti', icon: CreditCard },
  { id: 'bank', name: 'Havale/EFT', icon: Building2 },
  { id: 'mobile', name: 'Mobil Odeme', icon: Smartphone }
]

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value || 0)
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('tr-TR').format(value || 0)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getTxIcon = (type) => {
  const icons = {
    deposit: ArrowDownLeft,
    withdraw: ArrowUpRight,
    convert: RefreshCw,
    purchase: Receipt
  }
  return icons[type] || Receipt
}

const getTxLabel = (type) => {
  const labels = {
    deposit: 'TL Yukleme',
    withdraw: 'Cekim',
    convert: 'Donusum',
    purchase: 'Satin Alma'
  }
  return labels[type] || type
}

const getStatusLabel = (status) => {
  const labels = {
    pending: 'Bekliyor',
    completed: 'Tamamlandi',
    failed: 'Basarisiz',
    cancelled: 'Iptal'
  }
  return labels[status] || status
}

const selectPackage = (pkg) => {
  selectedPackage.value = pkg
}

const buyPackage = async (pkg) => {
  if (!user.value) {
    alert('Lutfen giris yapin')
    return
  }

  if (user.value.balance < pkg.tl_amount) {
    alert('Yetersiz TL bakiye. Lutfen once TL yukleyin.')
    showDepositModal.value = true
    return
  }

  if (!confirm(`${pkg.tl_amount} TL karsiliginda ${formatNumber(pkg.armor_amount + (pkg.armor_amount * pkg.bonus_percent / 100))} Armor satin almak istiyor musunuz?`)) {
    return
  }

  try {
    const response = await fetch('/api/wallet/buy-armor-package', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ package_id: pkg.id })
    })

    if (response.ok) {
      alert('Armor paketi basariyla satin alindi!')
      authStore.fetchUser()
      fetchTransactions()
    } else {
      const error = await response.json()
      alert(error.detail || 'Islem basarisiz')
    }
  } catch (e) {
    alert('Bir hata olustu')
  }
}

const processDeposit = async () => {
  if (depositAmount.value < 10 || !selectedMethod.value) return

  depositing.value = true
  try {
    const response = await fetch('/api/wallet/deposit', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        amount: depositAmount.value,
        payment_method: selectedMethod.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      if (data.payment_url) {
        window.location.href = data.payment_url
      } else {
        alert('Yukleme islemi baslatildi!')
        showDepositModal.value = false
        authStore.fetchUser()
        fetchTransactions()
      }
    } else {
      const error = await response.json()
      alert(error.detail || 'Yukleme basarisiz')
    }
  } catch (e) {
    alert('Bir hata olustu')
  } finally {
    depositing.value = false
  }
}

const processConversion = async () => {
  if (convertAmount.value < 1 || convertAmount.value > (user.value?.balance || 0)) return

  converting.value = true
  try {
    const response = await fetch('/api/wallet/exchange', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ tl_amount: convertAmount.value })
    })

    if (response.ok) {
      const data = await response.json()
      alert(`Donusum basarili! ${formatNumber(data.armor_added)} Armor eklendi.`)
      showConvertModal.value = false
      authStore.fetchUser()
      fetchTransactions()
    } else {
      const error = await response.json()
      alert(error.detail || 'Donusum basarisiz')
    }
  } catch (e) {
    alert('Bir hata olustu')
  } finally {
    converting.value = false
  }
}

const fetchTransactions = async () => {
  try {
    const response = await fetch('/api/wallet/transactions', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      // Map API response to frontend expected format
      transactions.value = (data || []).map(tx => ({
        id: tx.id,
        type: tx.type,
        amount: tx.amount,
        wallet_type: tx.wallet_type,
        status: 'completed',
        created_at: tx.created_at
      }))
    }
  } catch (e) {
    console.error('Fetch transactions error:', e)
    transactions.value = []
  }
}

onMounted(() => {
  fetchTransactions()
})
</script>

<style scoped>
.wallet-page {
  min-height: 100vh;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-desc {
  color: var(--text-secondary);
}

/* Balance Cards */
.balance-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.balance-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.balance-card.tl {
  border-color: rgba(16, 185, 129, 0.3);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, transparent 100%);
}

.balance-card.armor {
  border-color: rgba(249, 115, 22, 0.3);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.05) 0%, transparent 100%);
}

.balance-card.rate {
  border-color: rgba(139, 92, 246, 0.3);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, transparent 100%);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.balance-card.tl .card-icon {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.balance-card.armor .card-icon {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.card-icon.armor-icon img {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.balance-card.rate .card-icon {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.card-label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.card-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.card-action:hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--bg-primary);
}

.rate-info {
  font-size: 12px;
  color: var(--text-muted);
}

/* Sections */
.section {
  margin-bottom: 40px;
}

.section-header {
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.section-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

/* Packages Grid */
.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.package-card {
  position: relative;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.package-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-4px);
}

.package-card.featured {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, transparent 100%);
}

.package-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2);
}

.package-badge {
  position: absolute;
  top: -10px;
  right: 12px;
  background: var(--primary-color);
  color: var(--bg-primary);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.package-icon {
  color: var(--primary-color);
  margin-bottom: 12px;
}

.package-icon.armor-pkg-icon img {
  width: 50px;
  height: 50px;
  object-fit: contain;
}

.package-amount {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
}

.package-name {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.package-bonus {
  font-size: 12px;
  color: #10b981;
  margin-bottom: 12px;
}

.package-price {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.package-btn {
  width: 100%;
  padding: 10px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 8px;
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.package-btn:hover {
  transform: scale(1.02);
}

/* Transactions Table */
.transactions-table {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  background: var(--bg-tertiary);
}

td {
  color: var(--text-primary);
}

.tx-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.positive {
  color: #10b981;
}

.negative {
  color: #ef4444;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.empty-row {
  text-align: center;
  padding: 40px !important;
  color: var(--text-muted);
}

.empty-row span {
  display: block;
  margin-top: 8px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid var(--border-color);
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

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 10px;
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 12px 24px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  cursor: pointer;
}

/* Deposit Modal */
.deposit-info {
  margin-bottom: 24px;
  color: var(--text-secondary);
}

.amount-input label,
.payment-methods label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.input-group {
  display: flex;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
}

.input-group input {
  flex: 1;
  padding: 14px 16px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.input-suffix {
  padding: 14px 16px;
  color: var(--text-secondary);
  font-weight: 500;
  background: var(--bg-secondary);
}

.quick-amounts {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.quick-amounts button {
  flex: 1;
  padding: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
}

.quick-amounts button:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.payment-methods {
  margin-top: 24px;
}

.methods-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.method-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.method-card:hover {
  border-color: var(--primary-color);
}

.method-card.selected {
  border-color: var(--primary-color);
  background: rgba(249, 115, 22, 0.1);
}

.method-card span {
  font-size: 12px;
  color: var(--text-secondary);
}

.deposit-summary {
  margin-top: 24px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.summary-row.total {
  border-top: 1px solid var(--border-color);
  margin-top: 8px;
  padding-top: 16px;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 16px;
}

/* Convert Modal */
.convert-modal {
  max-width: 450px;
}

.convert-rate {
  text-align: center;
  padding: 20px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  margin-bottom: 24px;
}

.rate-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.rate-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.rate-value.armor {
  color: var(--primary-color);
}

.convert-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.convert-input label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.input-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}

.convert-arrow {
  text-align: center;
  color: var(--primary-color);
}

.convert-result label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.result-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: rgba(249, 115, 22, 0.1);
  border: 2px solid rgba(249, 115, 22, 0.3);
  border-radius: 12px;
  color: var(--primary-color);
}

.result-value {
  font-size: 32px;
  font-weight: 700;
}

.result-label {
  font-size: 14px;
  opacity: 0.8;
}

.quick-convert {
  display: flex;
  gap: 8px;
}

.quick-convert button {
  flex: 1;
  padding: 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
}

.quick-convert button:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .balance-cards {
    grid-template-columns: 1fr;
  }

  .packages-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .methods-grid {
    grid-template-columns: 1fr;
  }
}
</style>
