<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="mb-12 text-center animate-slide-down">
        <h1 class="text-5xl font-display font-bold mb-4">
          <span class="neon-text">Sunucu Paketleri</span>
        </h1>
        <p class="text-xl opacity-60 max-w-2xl mx-auto">
          Sunucu yonetiminizi bir ust seviyeye tasiyin. TL veya Armor ile odeme yapin.
        </p>

        <!-- User Balance Display -->
        <div v-if="user" class="flex justify-center gap-4 mt-6">
          <div class="balance-badge tl">
            <Banknote :size="18" />
            <span>{{ formatCurrency(user.balance || 0) }} TL</span>
          </div>
          <div class="balance-badge armor">
            <ShieldCheck :size="18" />
            <span>{{ formatNumber(user.balance_coin || 0) }} Armor</span>
          </div>
          <router-link to="/wallet" class="balance-badge add">
            <Plus :size="18" />
            <span>Bakiye Yukle</span>
          </router-link>
        </div>
      </div>

      <!-- Payment Method Toggle -->
      <div class="flex justify-center mb-8 animate-slide-up">
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
            class="toggle-btn armor"
            :class="{ active: paymentMethod === 'armor' }"
            @click="paymentMethod = 'armor'"
          >
            <ShieldCheck :size="18" />
            Armor ile Ode
          </button>
        </div>
      </div>

      <!-- Billing Period Toggle -->
      <div class="flex justify-center mb-12 animate-slide-up">
        <div class="tabs tabs-boxed bg-base-200/50 backdrop-blur-sm">
          <a
            class="tab"
            :class="{ 'tab-active': billingPeriod === 'monthly' }"
            @click="billingPeriod = 'monthly'"
          >
            Aylik
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': billingPeriod === 'yearly' }"
            @click="billingPeriod = 'yearly'"
          >
            Yillik
            <span class="badge badge-success badge-sm ml-2">20% Indirim</span>
          </a>
        </div>
      </div>

      <!-- Pricing Cards -->
      <div class="grid md:grid-cols-3 gap-8 mb-16 animate-slide-up" style="animation-delay: 0.1s">
        <!-- Starter Plan -->
        <BaseCard variant="glass" class="card-hover relative pricing-card">
          <div class="p-8">
            <div class="text-center mb-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-base-200 flex items-center justify-center">
                <RocketIcon class="w-8 h-8 opacity-60" />
              </div>
              <h3 class="text-2xl font-bold mb-2">Baslangic</h3>
              <p class="opacity-60 text-sm mb-4">Kucuk topluluklar icin</p>

              <!-- Price Display -->
              <div class="price-display">
                <div v-if="paymentMethod === 'tl'" class="price tl">
                  <span class="amount">{{ getPrice('starter', 'tl') }}</span>
                  <span class="currency">TL</span>
                  <span class="period">/{{ billingPeriod === 'monthly' ? 'ay' : 'yil' }}</span>
                </div>
                <div v-else class="price armor">
                  <ShieldCheck :size="24" />
                  <span class="amount">{{ formatNumber(getPrice('starter', 'armor')) }}</span>
                  <span class="currency">Armor</span>
                  <span class="period">/{{ billingPeriod === 'monthly' ? 'ay' : 'yil' }}</span>
                </div>
              </div>

              <!-- Alternative Price -->
              <div class="alt-price">
                <span v-if="paymentMethod === 'tl'">
                  veya {{ formatNumber(getPrice('starter', 'armor')) }} Armor
                </span>
                <span v-else>
                  veya {{ getPrice('starter', 'tl') }} TL
                </span>
              </div>
            </div>

            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">1 Sunucu</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Maksimum 16 slot</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Temel panel erisimi</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Gunluk yedekleme</span>
              </li>
              <li class="flex items-center gap-2">
                <XIcon class="w-5 h-5 text-error flex-shrink-0" />
                <span class="text-sm opacity-50">DDoS korumasi</span>
              </li>
            </ul>

            <button class="purchase-btn" @click="purchasePlan('starter')">
              <ShoppingCartIcon class="w-4 h-4" />
              Satin Al
            </button>
          </div>
        </BaseCard>

        <!-- Pro Plan -->
        <BaseCard variant="glass" class="card-hover relative pricing-card featured">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2">
            <span class="badge badge-primary badge-lg">En Populer</span>
          </div>
          <div class="p-8">
            <div class="text-center mb-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <ZapIcon class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-2xl font-bold mb-2">Pro</h3>
              <p class="opacity-60 text-sm mb-4">Profesyoneller icin</p>

              <!-- Price Display -->
              <div class="price-display">
                <div v-if="paymentMethod === 'tl'" class="price tl">
                  <span class="amount">{{ getPrice('pro', 'tl') }}</span>
                  <span class="currency">TL</span>
                  <span class="period">/{{ billingPeriod === 'monthly' ? 'ay' : 'yil' }}</span>
                </div>
                <div v-else class="price armor">
                  <ShieldCheck :size="24" />
                  <span class="amount">{{ formatNumber(getPrice('pro', 'armor')) }}</span>
                  <span class="currency">Armor</span>
                  <span class="period">/{{ billingPeriod === 'monthly' ? 'ay' : 'yil' }}</span>
                </div>
              </div>

              <div class="alt-price">
                <span v-if="paymentMethod === 'tl'">
                  veya {{ formatNumber(getPrice('pro', 'armor')) }} Armor
                </span>
                <span v-else>
                  veya {{ getPrice('pro', 'tl') }} TL
                </span>
              </div>
            </div>

            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">3 Sunucu</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Maksimum 32 slot</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Gelismis panel ozellikleri</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">DDoS korumasi</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Oncelikli destek</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Saatlik yedekleme</span>
              </li>
            </ul>

            <button class="purchase-btn primary" @click="purchasePlan('pro')">
              <ShoppingCartIcon class="w-4 h-4" />
              Satin Al
            </button>
          </div>
        </BaseCard>

        <!-- Enterprise Plan -->
        <BaseCard variant="glass" class="card-hover relative pricing-card">
          <div class="p-8">
            <div class="text-center mb-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-accent to-error flex items-center justify-center">
                <CrownIcon class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-2xl font-bold mb-2">Enterprise</h3>
              <p class="opacity-60 text-sm mb-4">Buyuk topluluklar icin</p>

              <!-- Price Display -->
              <div class="price-display">
                <div v-if="paymentMethod === 'tl'" class="price tl">
                  <span class="amount">{{ getPrice('enterprise', 'tl') }}</span>
                  <span class="currency">TL</span>
                  <span class="period">/{{ billingPeriod === 'monthly' ? 'ay' : 'yil' }}</span>
                </div>
                <div v-else class="price armor">
                  <ShieldCheck :size="24" />
                  <span class="amount">{{ formatNumber(getPrice('enterprise', 'armor')) }}</span>
                  <span class="currency">Armor</span>
                  <span class="period">/{{ billingPeriod === 'monthly' ? 'ay' : 'yil' }}</span>
                </div>
              </div>

              <div class="alt-price">
                <span v-if="paymentMethod === 'tl'">
                  veya {{ formatNumber(getPrice('enterprise', 'armor')) }} Armor
                </span>
                <span v-else>
                  veya {{ getPrice('enterprise', 'tl') }} TL
                </span>
              </div>
            </div>

            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">10 Sunucu</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Sinirsiz slot</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Tum ozellikler</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Gelismis DDoS korumasi</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">7/24 Ozel destek</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Ozel entegrasyonlar</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">SLA garantisi</span>
              </li>
            </ul>

            <button class="purchase-btn" @click="purchasePlan('enterprise')">
              <ShoppingCartIcon class="w-4 h-4" />
              Satin Al
            </button>
          </div>
        </BaseCard>
      </div>

      <!-- Armor Rate Info -->
      <div class="rate-info-banner animate-slide-up" style="animation-delay: 0.2s">
        <div class="rate-content">
          <ShieldCheck :size="24" />
          <div>
            <strong>1 TL = {{ ARMOR_RATE }} Armor</strong>
            <span>Armor ile odeme yaptiginizda ek indirimler kazanabilirsiniz!</span>
          </div>
          <router-link to="/wallet" class="rate-link">
            Armor Yukle
            <ArrowRight :size="16" />
          </router-link>
        </div>
      </div>

      <!-- Features Comparison -->
      <div class="mb-16 animate-slide-up" style="animation-delay: 0.3s">
        <h2 class="text-3xl font-display font-bold text-center mb-8">
          <span class="text-gradient-primary">Ozellik Karsilastirmasi</span>
        </h2>

        <BaseCard variant="glass">
          <div class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Ozellik</th>
                  <th class="text-center">Baslangic</th>
                  <th class="text-center">Pro</th>
                  <th class="text-center">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Sunucu Sayisi</td>
                  <td class="text-center">1</td>
                  <td class="text-center">3</td>
                  <td class="text-center">10</td>
                </tr>
                <tr>
                  <td>Maksimum Slot</td>
                  <td class="text-center">16</td>
                  <td class="text-center">32</td>
                  <td class="text-center">Sinirsiz</td>
                </tr>
                <tr>
                  <td>DDoS Korumasi</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
                <tr>
                  <td>Yedekleme</td>
                  <td class="text-center">Gunluk</td>
                  <td class="text-center">Saatlik</td>
                  <td class="text-center">Anlik</td>
                </tr>
                <tr>
                  <td>Oncelikli Destek</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
                <tr>
                  <td>Ozel Entegrasyonlar</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </BaseCard>
      </div>

      <!-- CTA Section -->
      <div class="text-center animate-slide-up" style="animation-delay: 0.4s">
        <BaseCard variant="glass" class="max-w-3xl mx-auto">
          <div class="p-12">
            <h2 class="text-3xl font-display font-bold mb-4">
              <span class="neon-text">Hala Kararisiz misiniz?</span>
            </h2>
            <p class="text-xl opacity-60 mb-8">
              Ekibimiz size en uygun plani secmenizde yardimci olmaktan mutluluk duyar.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <BaseButton variant="gaming" size="lg">
                <MessageCircleIcon class="w-5 h-5 mr-2" />
                Canli Destek
              </BaseButton>
              <BaseButton variant="outline" size="lg">
                <MailIcon class="w-5 h-5 mr-2" />
                Iletisime Gec
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>

    <!-- Purchase Confirmation Modal -->
    <Teleport to="body">
      <div v-if="showPurchaseModal" class="modal-overlay" @click.self="showPurchaseModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Satin Alma Onayi</h3>
            <button class="close-btn" @click="showPurchaseModal = false">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="purchase-summary">
              <div class="summary-plan">
                <component :is="getPlanIcon(selectedPlan)" :size="32" />
                <div>
                  <h4>{{ getPlanName(selectedPlan) }}</h4>
                  <p>{{ billingPeriod === 'monthly' ? 'Aylik' : 'Yillik' }} plan</p>
                </div>
              </div>

              <div class="summary-price">
                <div class="price-row">
                  <span>Paket Ucreti</span>
                  <span v-if="paymentMethod === 'tl'">{{ getPrice(selectedPlan, 'tl') }} TL</span>
                  <span v-else>{{ formatNumber(getPrice(selectedPlan, 'armor')) }} Armor</span>
                </div>
                <div class="price-row total">
                  <span>Toplam</span>
                  <span v-if="paymentMethod === 'tl'" class="tl">{{ getPrice(selectedPlan, 'tl') }} TL</span>
                  <span v-else class="armor">{{ formatNumber(getPrice(selectedPlan, 'armor')) }} Armor</span>
                </div>
              </div>

              <div class="balance-check" :class="{ insufficient: !hasEnoughBalance }">
                <span>Mevcut Bakiyeniz:</span>
                <span v-if="paymentMethod === 'tl'">{{ formatCurrency(user?.balance || 0) }} TL</span>
                <span v-else>{{ formatNumber(user?.balance_coin || 0) }} Armor</span>
              </div>

              <div v-if="!hasEnoughBalance" class="insufficient-warning">
                <AlertTriangle :size="18" />
                <span>Yetersiz bakiye!</span>
                <router-link to="/wallet" @click="showPurchaseModal = false">
                  Bakiye Yukle
                </router-link>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showPurchaseModal = false">Iptal</button>
            <button
              class="btn-primary"
              @click="confirmPurchase"
              :disabled="!hasEnoughBalance || purchasing"
            >
              <Loader2 v-if="purchasing" :size="18" class="spin" />
              <span v-else>Onayla ve Ode</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import {
  RocketIcon,
  ZapIcon,
  CrownIcon,
  CheckIcon,
  XIcon,
  ShoppingCartIcon,
  MessageCircleIcon,
  MailIcon,
  Banknote,
  ShieldCheck,
  Plus,
  ArrowRight,
  X,
  Loader2,
  AlertTriangle
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// Constants
const ARMOR_RATE = 100 // 1 TL = 100 Armor

// State
const billingPeriod = ref('monthly')
const paymentMethod = ref('tl')
const showPurchaseModal = ref(false)
const selectedPlan = ref(null)
const purchasing = ref(false)

// Computed
const user = computed(() => authStore.user)

// Plans with TL prices
const plans = {
  starter: {
    monthly: { tl: 49.99 },
    yearly: { tl: 479.90 } // 20% discount
  },
  pro: {
    monthly: { tl: 99.99 },
    yearly: { tl: 959.90 }
  },
  enterprise: {
    monthly: { tl: 199.99 },
    yearly: { tl: 1919.90 }
  }
}

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

const getPrice = (planType, currency) => {
  const period = billingPeriod.value
  const tlPrice = plans[planType][period].tl

  if (currency === 'tl') {
    return formatCurrency(tlPrice)
  } else {
    // Convert TL to Armor
    return Math.floor(tlPrice * ARMOR_RATE)
  }
}

const getPlanName = (planType) => {
  const names = {
    starter: 'Baslangic',
    pro: 'Pro',
    enterprise: 'Enterprise'
  }
  return names[planType] || planType
}

const getPlanIcon = (planType) => {
  const icons = {
    starter: RocketIcon,
    pro: ZapIcon,
    enterprise: CrownIcon
  }
  return icons[planType] || RocketIcon
}

const hasEnoughBalance = computed(() => {
  if (!user.value || !selectedPlan.value) return false

  const period = billingPeriod.value
  const tlPrice = plans[selectedPlan.value][period].tl

  if (paymentMethod.value === 'tl') {
    return user.value.balance >= tlPrice
  } else {
    const armorPrice = Math.floor(tlPrice * ARMOR_RATE)
    return user.value.balance_coin >= armorPrice
  }
})

const purchasePlan = (planType) => {
  if (!user.value) {
    router.push('/login')
    return
  }

  selectedPlan.value = planType
  showPurchaseModal.value = true
}

const confirmPurchase = async () => {
  if (!hasEnoughBalance.value) return

  purchasing.value = true
  try {
    const period = billingPeriod.value
    const tlPrice = plans[selectedPlan.value][period].tl

    const response = await fetch('/api/packages/purchase', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plan: selectedPlan.value,
        period: period,
        payment_method: paymentMethod.value,
        amount: paymentMethod.value === 'tl' ? tlPrice : Math.floor(tlPrice * ARMOR_RATE)
      })
    })

    if (response.ok) {
      alert('Paket basariyla satin alindi!')
      showPurchaseModal.value = false
      authStore.fetchUser()
      router.push('/dashboard')
    } else {
      const error = await response.json()
      alert(error.detail || 'Satin alma basarisiz')
    }
  } catch (e) {
    alert('Bir hata olustu')
  } finally {
    purchasing.value = false
  }
}
</script>

<style scoped>
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

.text-gradient-primary {
  @apply bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent;
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

.balance-badge.tl {
  color: #10b981;
}

.balance-badge.armor {
  color: #f97316;
}

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
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.toggle-btn.active.armor {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

/* Pricing Cards */
.pricing-card.featured {
  border: 2px solid var(--primary-color);
}

.price-display {
  margin-bottom: 8px;
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
  font-size: 40px;
  font-weight: 700;
}

.price .currency {
  font-size: 20px;
  font-weight: 600;
}

.price .period {
  font-size: 14px;
  opacity: 0.6;
}

.alt-price {
  font-size: 12px;
  color: var(--text-muted);
}

/* Purchase Button */
.purchase-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.purchase-btn:hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--bg-primary);
}

.purchase-btn.primary {
  background: var(--gradient-primary);
  border: none;
  color: var(--bg-primary);
}

.purchase-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

/* Rate Info Banner */
.rate-info-banner {
  background: var(--bg-secondary);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 12px;
  padding: 16px 24px;
  margin-bottom: 40px;
}

.rate-content {
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--primary-color);
}

.rate-content div {
  flex: 1;
}

.rate-content strong {
  display: block;
  font-size: 16px;
}

.rate-content span {
  font-size: 13px;
  opacity: 0.8;
}

.rate-link {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  background: var(--primary-color);
  color: var(--bg-primary);
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
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
  max-width: 450px;
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

/* Purchase Summary */
.purchase-summary {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-plan {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.summary-plan h4 {
  font-weight: 600;
  color: var(--text-primary);
}

.summary-plan p {
  font-size: 13px;
  color: var(--text-secondary);
}

.summary-price {
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  color: var(--text-secondary);
}

.price-row.total {
  border-top: 1px solid var(--border-color);
  margin-top: 8px;
  padding-top: 16px;
  font-weight: 600;
  font-size: 18px;
}

.price-row.total .tl {
  color: #10b981;
}

.price-row.total .armor {
  color: #f97316;
}

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

.insufficient-warning {
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

.insufficient-warning a {
  margin-left: auto;
  color: var(--primary-color);
  font-weight: 500;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-slide-down {
  animation: slideDown 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}
</style>
