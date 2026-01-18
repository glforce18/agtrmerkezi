<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-4xl font-display font-bold mb-4 text-gradient-primary">
          Oyun Sunucusu Paketleri
        </h1>
        <p class="opacity-60 max-w-2xl mx-auto">
          Adrenaline Gamer, Counter-Strike 1.6 ve Half-Life Deathmatch sunuculari
        </p>

        <!-- User Balance -->
        <div v-if="user" class="flex justify-center gap-4 mt-6">
          <div class="balance-badge tl">
            <Banknote :size="18" />
            <span>{{ formatCurrency(user.balance || 0) }} TL</span>
          </div>
          <div class="balance-badge armor">
            <Shield :size="18" />
            <span>{{ formatNumber(user.balance_coin || 0) }} Armor</span>
          </div>
          <router-link to="/wallet" class="balance-badge add">
            <Plus :size="18" />
            <span>Bakiye Yukle</span>
          </router-link>
        </div>
      </div>

      <!-- Payment Method Toggle -->
      <div class="flex justify-center mb-6">
        <div class="payment-toggle">
          <button
            class="toggle-btn"
            :class="{ active: paymentMethod === 'tl' }"
            @click="paymentMethod = 'tl'"
          >
            <Banknote :size="18" />
            TL ile Ode
          </button>
          <button
            class="toggle-btn"
            :class="{ active: paymentMethod === 'armor' }"
            @click="paymentMethod = 'armor'"
          >
            <Shield :size="18" />
            Armor ile Ode
          </button>
        </div>
      </div>

      <!-- Game Type Filter -->
      <div class="flex justify-center gap-4 mb-8">
        <button
          v-for="game in gameTypes"
          :key="game.value"
          class="game-filter-btn"
          :class="{ active: selectedGame === game.value }"
          @click="selectedGame = game.value"
        >
          <component :is="game.icon" :size="20" />
          {{ game.label }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <Loader2 :size="40" class="animate-spin opacity-50" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-12">
        <AlertTriangle :size="48" class="mx-auto mb-4 text-error" />
        <p class="text-error">{{ error }}</p>
        <button @click="fetchPackages" class="btn-retry mt-4">Tekrar Dene</button>
      </div>

      <!-- Packages Grid -->
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <div
          v-for="pkg in filteredPackages"
          :key="pkg.id"
          class="package-card"
          :class="{ featured: pkg.slug.includes('pro') }"
        >
          <!-- Package Image -->
          <div class="package-image">
            <img :src="getPackageImage(pkg.slug)" :alt="pkg.name" />
          </div>

          <!-- Header -->
          <div class="package-header">
            <h3 class="package-name">{{ pkg.name }}</h3>
            <span class="game-type-label">{{ getGameLabel(pkg.game_type) }}</span>
          </div>

          <!-- Price -->
          <div class="package-price">
            <div v-if="paymentMethod === 'tl'" class="price tl">
              <span class="amount">{{ formatCurrency(pkg.price_monthly) }}</span>
              <span class="currency">TL</span>
              <span class="period">/ay</span>
            </div>
            <div v-else class="price armor">
              <Shield :size="20" />
              <span class="amount">{{ formatNumber(Math.floor(pkg.price_monthly * ARMOR_RATE)) }}</span>
              <span class="currency">Armor</span>
              <span class="period">/ay</span>
            </div>
            <div class="alt-price">
              <span v-if="paymentMethod === 'tl'">
                veya {{ formatNumber(Math.floor(pkg.price_monthly * ARMOR_RATE)) }} Armor
              </span>
              <span v-else>
                veya {{ formatCurrency(pkg.price_monthly) }} TL
              </span>
            </div>
          </div>

          <!-- Specs -->
          <div class="package-specs">
            <div class="spec-item">
              <Users :size="16" />
              <span>{{ pkg.slots }} Slot</span>
            </div>
            <div class="spec-item">
              <Server :size="16" />
              <span>{{ getGameLabel(pkg.game_type) }}</span>
            </div>
          </div>

          <!-- Features -->
          <div class="package-features">
            <div
              v-for="feature in pkg.features"
              :key="feature"
              class="feature-item"
            >
              <Check :size="14" />
              <span>{{ getFeatureLabel(feature) }}</span>
            </div>
          </div>

          <!-- Description -->
          <p class="package-desc">{{ pkg.description }}</p>

          <!-- Action -->
          <button class="purchase-btn" @click="selectPackage(pkg)">
            <ShoppingCart :size="18" />
            Satin Al
          </button>
        </div>
      </div>

      <!-- No packages -->
      <div v-if="!loading && !error && filteredPackages.length === 0" class="text-center py-12">
        <Package :size="48" class="mx-auto mb-4 opacity-30" />
        <p class="opacity-60">Bu kategoride paket bulunamadi</p>
      </div>

      <!-- Rate Info -->
      <div class="rate-info">
        <Shield :size="20" />
        <span><strong>1 TL = {{ ARMOR_RATE }} Armor</strong> - Armor ile odeme yapabilirsiniz</span>
        <router-link to="/wallet">Armor Yukle</router-link>
      </div>
    </div>

    <!-- Purchase Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Sunucu Satin Al</h3>
            <button @click="showModal = false" class="close-btn">
              <X :size="20" />
            </button>
          </div>

          <div class="modal-body">
            <!-- Selected Package Info -->
            <div class="selected-package" v-if="selectedPkg">
              <div class="game-icon" :class="selectedPkg.game_type">
                <Gamepad2 :size="24" />
              </div>
              <div>
                <h4>{{ selectedPkg.name }}</h4>
                <p>{{ selectedPkg.slots }} Slot - {{ getGameLabel(selectedPkg.game_type) }}</p>
              </div>
            </div>

            <!-- Server Name -->
            <div class="form-group">
              <label>Sunucu Adi</label>
              <input
                v-model="serverName"
                type="text"
                placeholder="Ornek: My AG Server"
                class="form-input"
              />
            </div>

            <!-- Duration -->
            <div class="form-group">
              <label>Sure</label>
              <div class="duration-options">
                <button
                  v-for="opt in durationOptions"
                  :key="opt.months"
                  class="duration-btn"
                  :class="{ active: duration === opt.months }"
                  @click="duration = opt.months"
                >
                  <span class="duration-label">{{ opt.label }}</span>
                  <span v-if="opt.discount" class="duration-discount">%{{ opt.discount }} indirim</span>
                </button>
              </div>
            </div>

            <!-- Price Summary -->
            <div class="price-summary" v-if="selectedPkg">
              <div class="summary-row">
                <span>Aylik Ucret</span>
                <span>{{ formatCurrency(selectedPkg.price_monthly) }} TL</span>
              </div>
              <div class="summary-row">
                <span>Sure</span>
                <span>{{ duration }} Ay</span>
              </div>
              <div v-if="getDiscount() > 0" class="summary-row discount">
                <span>Indirim (%{{ getDiscount() }})</span>
                <span>-{{ formatCurrency(getDiscountAmount()) }} TL</span>
              </div>
              <div class="summary-row total">
                <span>Toplam</span>
                <span v-if="paymentMethod === 'tl'" class="tl">{{ formatCurrency(getTotalPrice()) }} TL</span>
                <span v-else class="armor">{{ formatNumber(getTotalArmor()) }} Armor</span>
              </div>
            </div>

            <!-- Balance Check -->
            <div class="balance-check" :class="{ insufficient: !hasEnoughBalance }">
              <span>Bakiyeniz:</span>
              <span v-if="paymentMethod === 'tl'">{{ formatCurrency(user?.balance || 0) }} TL</span>
              <span v-else>{{ formatNumber(user?.balance_coin || 0) }} Armor</span>
            </div>

            <div v-if="!hasEnoughBalance" class="warning-box">
              <AlertTriangle :size="18" />
              <span>Yetersiz bakiye!</span>
              <router-link to="/wallet" @click="showModal = false">Bakiye Yukle</router-link>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="showModal = false" class="btn-cancel">Iptal</button>
            <button
              @click="confirmPurchase"
              class="btn-confirm"
              :disabled="!canPurchase || purchasing"
            >
              <Loader2 v-if="purchasing" :size="18" class="animate-spin" />
              <span v-else>Satin Al</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Banknote,
  Shield,
  Plus,
  Gamepad2,
  Users,
  Server,
  Check,
  ShoppingCart,
  Package,
  Loader2,
  AlertTriangle,
  X
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

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

// Constants
const ARMOR_RATE = 100

// State
const packages = ref([])
const loading = ref(true)
const error = ref(null)
const selectedGame = ref('all')
const paymentMethod = ref('tl')
const showModal = ref(false)
const selectedPkg = ref(null)
const serverName = ref('')
const duration = ref(1)
const purchasing = ref(false)

// Game types
const gameTypes = [
  { value: 'all', label: 'Tumu', icon: Package },
  { value: 'ag', label: 'Adrenaline Gamer', icon: Gamepad2 },
  { value: 'cs16', label: 'CS 1.6', icon: Gamepad2 },
  { value: 'hldm', label: 'HLDM', icon: Gamepad2 }
]

// Duration options
const durationOptions = [
  { months: 1, label: '1 Ay', discount: 0 },
  { months: 3, label: '3 Ay', discount: 10 },
  { months: 6, label: '6 Ay', discount: 15 },
  { months: 12, label: '12 Ay', discount: 20 }
]

// Computed
const user = computed(() => authStore.user)

const filteredPackages = computed(() => {
  if (selectedGame.value === 'all') {
    return packages.value
  }
  return packages.value.filter(p => p.game_type === selectedGame.value)
})

const hasEnoughBalance = computed(() => {
  if (!user.value || !selectedPkg.value) return false

  if (paymentMethod.value === 'tl') {
    return (user.value.balance || 0) >= getTotalPrice()
  } else {
    return (user.value.balance_coin || 0) >= getTotalArmor()
  }
})

const canPurchase = computed(() => {
  return selectedPkg.value && serverName.value.trim().length >= 3 && hasEnoughBalance.value
})

// Methods
const formatCurrency = (val) => {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(val || 0)
}

const formatNumber = (val) => {
  return new Intl.NumberFormat('tr-TR').format(val || 0)
}

const getPackageImage = (slug) => {
  const images = {
    halflife: '/static/images/packages/hlpaket.png',
    halflife_ag: '/static/images/packages/hlagpaket.png',
    cs16_pro: '/static/images/packages/cspropublicpaket.png',
    cs16_fun: '/static/images/packages/cszombiefunpaket.png'
  }
  return images[slug] || '/static/images/packages/hlpaket.png'
}

const getGameLabel = (type) => {
  const labels = {
    ag: 'Adrenaline Gamer',
    cs16: 'Counter-Strike 1.6',
    hldm: 'Half-Life Deathmatch'
  }
  return labels[type] || type
}

const getFeatureLabel = (feature) => {
  const labels = {
    basic_plugins: 'Temel Pluginler',
    fun_plugins: 'Fun Pluginler',
    zombie_mod: 'Zombie Mod',
    rcon_access: 'RCON Erisimi',
    anticheat: 'Anti-Cheat',
    amvp: 'AMVP Sistemi',
    statsme: 'StatsMe',
    custom_domain: 'Ozel Domain',
    priority_support: 'Oncelikli Destek',
    ddos_protection: 'DDoS Koruma',
    '247_support': '7/24 Destek',
    auto_backup: 'Otomatik Yedekleme'
  }
  return labels[feature] || feature
}

const getDiscount = () => {
  const opt = durationOptions.find(o => o.months === duration.value)
  return opt?.discount || 0
}

const getDiscountAmount = () => {
  if (!selectedPkg.value) return 0
  const base = selectedPkg.value.price_monthly * duration.value
  return base * (getDiscount() / 100)
}

const getTotalPrice = () => {
  if (!selectedPkg.value) return 0
  const base = selectedPkg.value.price_monthly * duration.value
  return base - getDiscountAmount()
}

const getTotalArmor = () => {
  return Math.floor(getTotalPrice() * ARMOR_RATE)
}

const selectPackage = (pkg) => {
  if (!user.value) {
    router.push('/login')
    return
  }
  selectedPkg.value = pkg
  serverName.value = ''
  duration.value = 1
  showModal.value = true
}

const fetchPackages = async () => {
  loading.value = true
  error.value = null

  try {
    const res = await fetch('/api/servers/packages')
    if (!res.ok) throw new Error('Paketler yuklenemedi')

    const data = await res.json()
    packages.value = data.packages || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const confirmPurchase = async () => {
  if (!canPurchase.value || purchasing.value) return

  purchasing.value = true

  try {
    const res = await fetch('/api/servers/order/package-wallet', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        package_id: selectedPkg.value.id,
        months: duration.value,
        server_name: serverName.value.trim(),
        auto_renew: false,
        payment_type: paymentMethod.value
      })
    })

    const data = await res.json()

    if (res.ok) {
      alert(`Sunucu basariyla olusturuldu!\n\nSunucu: ${data.order.server_info.name}\nIP: ${data.order.server_info.ip}`)
      showModal.value = false
      await authStore.fetchUser()
      router.push('/dashboard')
    } else {
      alert(data.detail || 'Satin alma basarisiz')
    }
  } catch (e) {
    alert('Bir hata olustu: ' + e.message)
  } finally {
    purchasing.value = false
  }
}

onMounted(() => {
  fetchPackages()
})
</script>

<style scoped>
.text-gradient-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Balance Badges */
.balance-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.balance-badge.tl { color: #10b981; }
.balance-badge.armor { color: #f97316; }
.balance-badge.add {
  color: var(--primary-color);
  cursor: pointer;
  text-decoration: none;
}
.balance-badge.add:hover {
  background: rgba(249, 115, 22, 0.1);
}

/* Payment Toggle */
.payment-toggle {
  display: flex;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 4px;
  border: 1px solid var(--border-color);
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: var(--primary-color);
  color: white;
}

/* Game Filter */
.game-filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.game-filter-btn:hover {
  border-color: var(--primary-color);
}

.game-filter-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

/* Package Card */
.package-card {
  position: relative;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
}

.package-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-4px);
}

.package-card.featured {
  border-color: var(--primary-color);
  box-shadow: 0 0 30px rgba(249, 115, 22, 0.1);
}

.package-badge {
  position: absolute;
  top: -12px;
  right: 16px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.package-badge.popular {
  background: var(--primary-color);
  color: white;
}

.package-badge.enterprise {
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
  color: white;
}

.package-image {
  margin: -24px -24px 16px -24px;
  border-radius: 16px 16px 0 0;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, transparent 100%);
}

.package-image img {
  width: 100%;
  max-width: 200px;
  height: auto;
  object-fit: contain;
  transition: transform 0.3s;
}

.package-card:hover .package-image img {
  transform: scale(1.05);
}

.package-header {
  text-align: center;
  margin-bottom: 16px;
}

.game-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.game-icon.ag { background: linear-gradient(135deg, #f97316, #ea580c); }
.game-icon.cs16 { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.game-icon.hldm { background: linear-gradient(135deg, #10b981, #059669); }

.package-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.game-type-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Price */
.package-price {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  text-align: center;
}

.price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.price.armor {
  align-items: center;
  color: #f97316;
}

.price .amount {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.price.armor .amount {
  color: #f97316;
}

.price .currency {
  font-size: 16px;
  font-weight: 600;
}

.price .period {
  font-size: 14px;
  color: var(--text-secondary);
}

.alt-price {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Specs */
.package-specs {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.spec-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

/* Features */
.package-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-secondary);
}

.feature-item svg {
  color: #10b981;
}

.package-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

/* Purchase Button */
.purchase-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.purchase-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

.btn-retry {
  padding: 10px 20px;
  background: var(--primary-color);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
}

/* Rate Info */
.rate-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 12px;
  color: var(--primary-color);
}

.rate-info a {
  color: var(--primary-color);
  font-weight: 600;
  text-decoration: underline;
}

/* Modal */
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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

/* Selected Package */
.selected-package {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.selected-package h4 {
  font-weight: 600;
  color: var(--text-primary);
}

.selected-package p {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Form */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

/* Duration Options */
.duration-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.duration-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.duration-btn:hover {
  border-color: var(--primary-color);
}

.duration-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.duration-label {
  font-weight: 600;
  font-size: 14px;
}

.duration-discount {
  font-size: 10px;
  color: #10b981;
  margin-top: 2px;
}

.duration-btn.active .duration-discount {
  color: rgba(255,255,255,0.9);
}

/* Price Summary */
.price-summary {
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.summary-row.discount {
  color: #10b981;
}

.summary-row.total {
  border-top: 1px solid var(--border-color);
  margin-top: 8px;
  padding-top: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-row.total .tl { color: #10b981; }
.summary-row.total .armor { color: #f97316; }

/* Balance Check */
.balance-check {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
  font-size: 14px;
  color: #10b981;
}

.balance-check.insufficient {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.warning-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  color: #f59e0b;
  font-size: 14px;
}

.warning-box a {
  margin-left: auto;
  color: var(--primary-color);
  font-weight: 500;
}

/* Buttons */
.btn-cancel {
  padding: 12px 24px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  cursor: pointer;
}

.btn-confirm {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
