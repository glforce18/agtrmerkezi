<template>
  <div class="min-h-screen py-8">
    <div class="container-custom">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold flex items-center gap-3 mb-2">
          <WalletIcon class="w-8 h-8 text-orange-500" />
          Cüzdan
        </h1>
        <p class="text-gray-400">Bakiyeni yönet, TL yükle ve Armor'a dönüştür</p>
      </div>

      <!-- Balance Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
        <n-card class="balance-card tl-card">
          <div class="flex flex-col gap-4">
            <div class="w-14 h-14 rounded-xl bg-green-500/10 flex items-center justify-center">
              <Banknote class="w-8 h-8 text-green-500" />
            </div>
            <div>
              <span class="text-sm text-gray-400 block mb-1">TL Bakiye</span>
              <span class="text-3xl font-bold">{{ formatCurrency(user?.balance || 0) }} TL</span>
            </div>
            <n-button type="primary" block @click="showDepositModal = true">
              <template #icon><Plus class="w-4 h-4" /></template>
              TL Yükle
            </n-button>
          </div>
        </n-card>

        <n-card class="balance-card armor-card">
          <div class="flex flex-col gap-4">
            <div class="w-14 h-14 rounded-xl bg-orange-500/10 flex items-center justify-center">
              <img :src="armorIconUrl" alt="Armor" class="w-12 h-12 object-contain" />
            </div>
            <div>
              <span class="text-sm text-gray-400 block mb-1">Armor Bakiye</span>
              <span class="text-3xl font-bold">{{ formatNumber(user?.balance_coin || 0) }} Armor</span>
            </div>
            <n-button block secondary @click="showConvertModal = true">
              <template #icon><ArrowRightLeft class="w-4 h-4" /></template>
              Dönüştür
            </n-button>
          </div>
        </n-card>

        <n-card class="balance-card rate-card">
          <div class="flex flex-col gap-4">
            <div class="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center">
              <TrendingUp class="w-8 h-8 text-purple-500" />
            </div>
            <div>
              <span class="text-sm text-gray-400 block mb-1">Dönüşüm Oranı</span>
              <span class="text-3xl font-bold">1 TL = {{ armorRate }} Armor</span>
            </div>
            <n-tag type="info" size="small">Sabit oran</n-tag>
          </div>
        </n-card>
      </div>

      <!-- Armor Packages -->
      <div class="mb-10">
        <div class="mb-6">
          <h2 class="text-xl font-bold mb-1">Armor Paketleri</h2>
          <p class="text-gray-400 text-sm">TL ile Armor satın al, bonus kazan!</p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <n-card
            v-for="pkg in armorPackages"
            :key="pkg.id"
            class="package-card cursor-pointer"
            :class="{ 'featured': pkg.is_featured, 'selected': selectedPackage?.id === pkg.id }"
            @click="selectPackage(pkg)"
          >
            <n-tag v-if="pkg.bonus_percent > 0" type="warning" size="small" class="absolute -top-2 right-2">
              +{{ pkg.bonus_percent }}% Bonus
            </n-tag>
            <div class="text-center">
              <div class="mb-3">
                <img :src="armorIconUrl" alt="Armor" class="w-12 h-12 mx-auto object-contain" />
              </div>
              <div class="text-3xl font-bold mb-1">{{ formatNumber(pkg.armor_amount) }}</div>
              <div class="text-sm text-gray-400 mb-2">Armor</div>
              <div v-if="pkg.bonus_percent > 0" class="text-xs text-green-500 mb-3">
                +{{ formatNumber(Math.floor(pkg.armor_amount * pkg.bonus_percent / 100)) }} Bonus
              </div>
              <div class="text-lg font-bold text-orange-500 mb-4">{{ formatCurrency(pkg.tl_amount) }} TL</div>
              <n-button type="primary" size="small" block @click.stop="buyPackage(pkg)">
                Satın Al
              </n-button>
            </div>
          </n-card>
        </div>
      </div>

      <!-- Transaction History -->
      <div>
        <div class="mb-6">
          <h2 class="text-xl font-bold">İşlem Geçmişi</h2>
        </div>

        <n-card class="glass-card">
          <n-data-table
            :columns="txColumns"
            :data="transactions"
            :bordered="false"
            :single-line="false"
          />
          <n-empty v-if="transactions.length === 0" description="Henüz işlem yok" class="py-8">
            <template #icon>
              <Receipt class="w-8 h-8 text-gray-400" />
            </template>
          </n-empty>
        </n-card>
      </div>
    </div>

    <!-- TL Deposit Modal -->
    <n-modal v-model:show="showDepositModal" preset="card" title="TL Yükle" style="width: 500px;">
      <div class="space-y-6">
        <p class="text-gray-400">Hesabınıza TL yüklemek için aşağıdaki yöntemlerden birini seçin.</p>

        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">Yüklenecek Miktar</label>
          <n-input-group>
            <n-input-number
              v-model:value="depositAmount"
              :min="10"
              :max="10000"
              placeholder="0.00"
              class="flex-1"
            />
            <n-input-group-label>TL</n-input-group-label>
          </n-input-group>
          <div class="flex gap-2 mt-3">
            <n-button v-for="amount in [50, 100, 250, 500]" :key="amount" size="small" quaternary @click="depositAmount = amount">
              {{ amount }} TL
            </n-button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">Ödeme Yöntemi</label>
          <div class="grid grid-cols-3 gap-3">
            <div
              v-for="method in paymentMethods"
              :key="method.id"
              class="payment-method"
              :class="{ 'selected': selectedMethod === method.id }"
              @click="selectedMethod = method.id"
            >
              <component :is="method.icon" class="w-6 h-6 mb-2" />
              <span class="text-xs">{{ method.name }}</span>
            </div>
          </div>
        </div>

        <div v-if="depositAmount >= 10" class="p-4 bg-white/5 rounded-lg">
          <div class="flex justify-between text-sm text-gray-400 mb-2">
            <span>Yükleme Miktarı</span>
            <span>{{ formatCurrency(depositAmount) }} TL</span>
          </div>
          <div class="flex justify-between font-bold text-lg border-t border-white/10 pt-2 mt-2">
            <span>Hesabınıza Eklenecek</span>
            <span>{{ formatCurrency(depositAmount) }} TL</span>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button quaternary @click="showDepositModal = false">İptal</n-button>
          <n-button
            type="primary"
            @click="processDeposit"
            :disabled="depositAmount < 10 || !selectedMethod"
            :loading="depositing"
          >
            Ödemeye Devam Et
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- TL to Armor Conversion Modal -->
    <n-modal v-model:show="showConvertModal" preset="card" title="TL'yi Armor'a Dönüştür" style="width: 450px;">
      <div class="space-y-6">
        <div class="text-center p-5 bg-white/5 rounded-xl">
          <div class="flex items-center justify-center gap-4">
            <span class="text-2xl font-bold">1 TL</span>
            <ArrowRight class="w-5 h-5 text-orange-500" />
            <span class="text-2xl font-bold text-orange-500">{{ armorRate }} Armor</span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">TL Miktarı</label>
          <n-input-group>
            <n-input-number
              v-model:value="convertAmount"
              :min="1"
              :max="user?.balance || 0"
              placeholder="0.00"
              class="flex-1"
            />
            <n-input-group-label>TL</n-input-group-label>
          </n-input-group>
          <div class="text-xs text-gray-500 mt-2">
            Mevcut: {{ formatCurrency(user?.balance || 0) }} TL
          </div>
        </div>

        <div class="text-center">
          <ArrowDown class="w-6 h-6 text-orange-500 mx-auto" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">Alacağınız Armor</label>
          <div class="flex items-center justify-center gap-3 p-5 bg-orange-500/10 border-2 border-orange-500/30 rounded-xl">
            <ShieldCheck class="w-6 h-6 text-orange-500" />
            <span class="text-3xl font-bold text-orange-500">{{ formatNumber(convertAmount * armorRate) }}</span>
            <span class="text-sm text-orange-400">Armor</span>
          </div>
        </div>

        <div class="flex gap-2">
          <n-button v-for="amount in [10, 50, 100]" :key="amount" size="small" quaternary @click="convertAmount = amount">
            {{ amount }} TL
          </n-button>
          <n-button size="small" quaternary @click="convertAmount = user?.balance || 0">Tümü</n-button>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button quaternary @click="showConvertModal = false">İptal</n-button>
          <n-button
            type="primary"
            @click="processConversion"
            :disabled="convertAmount < 1 || convertAmount > (user?.balance || 0)"
            :loading="converting"
          >
            Dönüştür
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, h } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { NTag } from 'naive-ui'
import {
  Wallet as WalletIcon,
  Banknote,
  ShieldCheck,
  Plus,
  ArrowRightLeft,
  TrendingUp,
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

const route = useRoute()
const authStore = useAuthStore()

// Auth headers helper
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
const armorRate = 100
const armorIconUrl = '/static/images/icons/armor.png'

// Computed
const user = computed(() => authStore.user)

// Transaction table columns
const txColumns = [
  {
    title: 'Tarih',
    key: 'created_at',
    render: (row) => formatDate(row.created_at)
  },
  {
    title: 'İşlem',
    key: 'type',
    render: (row) => {
      const icons = {
        deposit: ArrowDownLeft,
        withdraw: ArrowUpRight,
        convert: RefreshCw,
        purchase: Receipt
      }
      const labels = {
        deposit: 'TL Yükleme',
        withdraw: 'Çekim',
        convert: 'Dönüşüm',
        purchase: 'Satın Alma'
      }
      const Icon = icons[row.type] || Receipt
      return h('div', { class: 'flex items-center gap-2' }, [
        h(Icon, { class: 'w-4 h-4' }),
        labels[row.type] || row.type
      ])
    }
  },
  {
    title: 'Miktar',
    key: 'amount',
    render: (row) => {
      const isPositive = row.amount > 0
      const color = isPositive ? 'text-green-500' : 'text-red-500'
      const prefix = isPositive ? '+' : ''
      const suffix = row.wallet_type === 'REAL' ? ' TL' : ' Armor'
      return h('span', { class: color }, prefix + formatNumber(row.amount) + suffix)
    }
  },
  {
    title: 'Durum',
    key: 'status',
    render: (row) => {
      const types = {
        pending: 'warning',
        completed: 'success',
        failed: 'error',
        cancelled: 'default'
      }
      const labels = {
        pending: 'Bekliyor',
        completed: 'Tamamlandı',
        failed: 'Başarısız',
        cancelled: 'İptal'
      }
      return h(NTag, { type: types[row.status] || 'default', size: 'small' }, () => labels[row.status] || row.status)
    }
  }
]

// Armor Packages
const armorPackages = ref([
  { id: 1, name: 'Başlangıç', tl_amount: 10, armor_amount: 1000, bonus_percent: 0, is_featured: false },
  { id: 2, name: 'Standart', tl_amount: 25, armor_amount: 2500, bonus_percent: 5, is_featured: false },
  { id: 3, name: 'Popüler', tl_amount: 50, armor_amount: 5000, bonus_percent: 10, is_featured: true },
  { id: 4, name: 'Premium', tl_amount: 100, armor_amount: 10000, bonus_percent: 15, is_featured: false },
  { id: 5, name: 'Elite', tl_amount: 250, armor_amount: 25000, bonus_percent: 20, is_featured: false },
  { id: 6, name: 'Legend', tl_amount: 500, armor_amount: 50000, bonus_percent: 25, is_featured: false }
])

// Payment Methods
const paymentMethods = [
  { id: 'card', name: 'Kredi Kartı', icon: CreditCard },
  { id: 'bank', name: 'Havale/EFT', icon: Building2 },
  { id: 'mobile', name: 'Mobil Ödeme', icon: Smartphone }
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

const selectPackage = (pkg) => {
  selectedPackage.value = pkg
}

const buyPackage = async (pkg) => {
  if (!user.value) {
    window.$message?.warning('Lütfen giriş yapın')
    return
  }

  if (user.value.balance < pkg.tl_amount) {
    window.$message?.warning('Yetersiz TL bakiye. Lütfen önce TL yükleyin.')
    showDepositModal.value = true
    return
  }

  window.$dialog?.warning({
    title: 'Onay',
    content: `${pkg.tl_amount} TL karşılığında ${formatNumber(pkg.armor_amount + (pkg.armor_amount * pkg.bonus_percent / 100))} Armor satın almak istiyor musunuz?`,
    positiveText: 'Satın Al',
    negativeText: 'İptal',
    onPositiveClick: async () => {
      try {
        const response = await fetch('/api/wallet/buy-armor-package', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ package_id: pkg.id })
        })

        if (response.ok) {
          window.$message?.success('Armor paketi başarıyla satın alındı!')
          authStore.fetchUser()
          fetchTransactions()
        } else {
          const error = await response.json()
          window.$message?.error(error.detail || 'İşlem başarısız')
        }
      } catch (e) {
        window.$message?.error('Bir hata oluştu')
      }
    }
  })
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
        window.$message?.success('Yükleme işlemi başlatıldı!')
        showDepositModal.value = false
        authStore.fetchUser()
        fetchTransactions()
      }
    } else {
      const error = await response.json()
      window.$message?.error(error.detail || 'Yükleme başarısız')
    }
  } catch (e) {
    window.$message?.error('Bir hata oluştu')
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
      window.$message?.success(`Dönüşüm başarılı! ${formatNumber(data.armor_added)} Armor eklendi.`)
      showConvertModal.value = false
      authStore.fetchUser()
      fetchTransactions()
    } else {
      const error = await response.json()
      window.$message?.error(error.detail || 'Dönüşüm başarısız')
    }
  } catch (e) {
    window.$message?.error('Bir hata oluştu')
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

// Handle tab query parameter from navbar
const handleTabQuery = () => {
  const tab = route.query.tab
  if (tab === 'tl') {
    showDepositModal.value = true
  } else if (tab === 'armor') {
    showConvertModal.value = true
  }
}

onMounted(() => {
  fetchTransactions()
  handleTabQuery()
})

// Watch for query changes
watch(() => route.query.tab, () => {
  handleTabQuery()
})
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.balance-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tl-card {
  border-color: rgba(16, 185, 129, 0.3);
}

.armor-card {
  border-color: rgba(249, 115, 22, 0.3);
}

.rate-card {
  border-color: rgba(139, 92, 246, 0.3);
}

.package-card {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
}

.package-card:hover {
  border-color: #f97316;
  transform: translateY(-4px);
}

.package-card.featured {
  border-color: #f97316;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, transparent 100%);
}

.package-card.selected {
  border-color: #f97316;
  box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2);
}

.payment-method {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-method:hover {
  border-color: #f97316;
}

.payment-method.selected {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}
</style>
