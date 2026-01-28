<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-lambda font-bold mb-4">
          <span class="neon-orange">SUNUCU KİRALA</span>
        </h1>
        <p class="text-xl text-text-secondary font-hev">
          Half-Life & Counter-Strike 1.6 sunucunuzu dakikalar içinde başlatın
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin text-6xl neon-orange mb-4">λ</div>
          <p class="text-text-secondary font-hev">Paketler yükleniyor...</p>
        </div>
      </div>

      <!-- Packages -->
      <template v-else>
        <!-- Package Selection -->
        <div class="mb-12">
          <h2 class="text-2xl font-lambda font-bold text-text-primary mb-6 text-center">
            PAKET SEÇİMİ
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div
              v-for="pkg in packages"
              :key="pkg.id"
              @click="selectPackage(pkg)"
              class="bg-cyber-panel border-2 rounded-lg p-6 cursor-pointer transition-all duration-300"
              :class="selectedPackage?.id === pkg.id
                ? 'border-lambda-orange shadow-neon-orange scale-105'
                : 'border-cyber-border hover:border-hev-cyan'"
            >
              <!-- Package Badge -->
              <div v-if="pkg.is_popular" class="inline-block px-3 py-1 bg-combine-yellow bg-opacity-20 border border-combine-yellow text-combine-yellow rounded-full font-lambda text-xs mb-4">
                EN POPÜLER
              </div>

              <!-- Package Name -->
              <h3 class="text-2xl font-lambda font-bold mb-2"
                :class="selectedPackage?.id === pkg.id ? 'text-lambda-orange' : 'text-text-primary'">
                {{ pkg.name }}
              </h3>

              <!-- Package Description -->
              <p class="text-text-secondary font-hev text-sm mb-6">
                {{ pkg.description }}
              </p>

              <!-- Features -->
              <div class="space-y-2 mb-6">
                <div class="flex items-center gap-2 text-sm">
                  <Users :size="16" class="text-hev-cyan" />
                  <span class="font-hev text-text-primary">{{ pkg.max_players }} Slot</span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <Cpu :size="16" class="text-combine-green" />
                  <span class="font-hev text-text-primary">{{ pkg.cpu_cores }} CPU Core</span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <HardDrive :size="16" class="text-xen-purple" />
                  <span class="font-hev text-text-primary">{{ pkg.ram_gb }} GB RAM</span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <Database :size="16" class="text-combine-yellow" />
                  <span class="font-hev text-text-primary">{{ pkg.disk_gb }} GB SSD</span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <Shield :size="16" class="text-combine-green" />
                  <span class="font-hev text-text-primary">DDoS Koruması</span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <Zap :size="16" class="text-lambda-orange" />
                  <span class="font-hev text-text-primary">Anlık Kurulum</span>
                </div>
              </div>

              <!-- Price -->
              <div class="border-t border-cyber-border pt-4">
                <div class="text-center">
                  <div class="text-4xl font-lambda neon-orange mb-1">
                    ₺{{ pkg.price_monthly }}
                  </div>
                  <div class="text-text-secondary font-hev text-sm">/ ay</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Configuration -->
        <div v-if="selectedPackage" class="mb-12">
          <div class="bg-cyber-panel border border-cyber-border rounded-lg p-8">
            <h2 class="text-2xl font-lambda font-bold text-text-primary mb-6">
              SUNUCU YAPILANDIRMASI
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Server Name -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  Sunucu Adı
                </label>
                <input
                  v-model="config.server_name"
                  type="text"
                  placeholder="Benim Harika Sunucum"
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                  maxlength="64"
                />
              </div>

              <!-- Game Type -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  Oyun Türü
                </label>
                <select
                  v-model="config.game_type"
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                >
                  <option value="cs16">Counter-Strike 1.6</option>
                  <option value="cstrike">CS 1.6 (Classic)</option>
                  <option value="czero">Condition Zero</option>
                  <option value="hl">Half-Life</option>
                  <option value="tfc">Team Fortress Classic</option>
                </select>
              </div>

              <!-- Region -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  Bölge
                </label>
                <select
                  v-model="config.region"
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                >
                  <option value="istanbul">İstanbul, TR</option>
                  <option value="ankara">Ankara, TR</option>
                  <option value="frankfurt">Frankfurt, DE</option>
                  <option value="london">London, UK</option>
                </select>
              </div>

              <!-- Billing Period -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  Faturalama Periyodu
                </label>
                <select
                  v-model="config.billing_period"
                  @change="updatePrice"
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                >
                  <option value="1">1 Ay</option>
                  <option value="3">3 Ay (5% indirim)</option>
                  <option value="6">6 Ay (10% indirim)</option>
                  <option value="12">12 Ay (15% indirim)</option>
                </select>
              </div>
            </div>

            <!-- Addons -->
            <div class="mt-6">
              <label class="block text-sm font-lambda text-text-primary mb-3">
                Ek Özellikler
              </label>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <label class="flex items-center gap-3 p-3 bg-cyber-darker border border-cyber-border rounded cursor-pointer hover:border-hev-cyan transition-all">
                  <input
                    type="checkbox"
                    v-model="config.addons.backup"
                    class="w-5 h-5 text-lambda-orange rounded"
                  />
                  <div class="flex-1">
                    <div class="font-lambda text-text-primary">Otomatik Yedekleme</div>
                    <div class="text-xs text-text-secondary font-hev">Günlük yedekleme +₺20/ay</div>
                  </div>
                </label>

                <label class="flex items-center gap-3 p-3 bg-cyber-darker border border-cyber-border rounded cursor-pointer hover:border-hev-cyan transition-all">
                  <input
                    type="checkbox"
                    v-model="config.addons.mysql"
                    class="w-5 h-5 text-lambda-orange rounded"
                  />
                  <div class="flex-1">
                    <div class="font-lambda text-text-primary">MySQL Veritabanı</div>
                    <div class="text-xs text-text-secondary font-hev">Sınırsız veritabanı +₺30/ay</div>
                  </div>
                </label>

                <label class="flex items-center gap-3 p-3 bg-cyber-darker border border-cyber-border rounded cursor-pointer hover:border-hev-cyan transition-all">
                  <input
                    type="checkbox"
                    v-model="config.addons.priority_support"
                    class="w-5 h-5 text-lambda-orange rounded"
                  />
                  <div class="flex-1">
                    <div class="font-lambda text-text-primary">Öncelikli Destek</div>
                    <div class="text-xs text-text-secondary font-hev">7/24 öncelik +₺50/ay</div>
                  </div>
                </label>

                <label class="flex items-center gap-3 p-3 bg-cyber-darker border border-cyber-border rounded cursor-pointer hover:border-hev-cyan transition-all">
                  <input
                    type="checkbox"
                    v-model="config.addons.custom_plugins"
                    class="w-5 h-5 text-lambda-orange rounded"
                  />
                  <div class="flex-1">
                    <div class="font-lambda text-text-primary">Özel Plugin Kurulumu</div>
                    <div class="text-xs text-text-secondary font-hev">Plugin desteği +₺40/ay</div>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div v-if="selectedPackage" class="mb-8">
          <div class="bg-cyber-panel border border-lambda-orange rounded-lg p-8">
            <h2 class="text-2xl font-lambda font-bold text-lambda-orange mb-6">
              SİPARİŞ ÖZETİ
            </h2>

            <div class="space-y-3 mb-6">
              <div class="flex items-center justify-between">
                <span class="font-hev text-text-secondary">Paket</span>
                <span class="font-lambda text-text-primary">{{ selectedPackage.name }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="font-hev text-text-secondary">Faturalama</span>
                <span class="font-lambda text-text-primary">{{ config.billing_period }} Ay</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="font-hev text-text-secondary">Temel Ücret</span>
                <span class="font-lambda text-text-primary">₺{{ selectedPackage.price_monthly }}</span>
              </div>

              <div v-if="addonTotal > 0" class="flex items-center justify-between">
                <span class="font-hev text-text-secondary">Ek Özellikler</span>
                <span class="font-lambda text-text-primary">₺{{ addonTotal }}</span>
              </div>

              <div v-if="discount > 0" class="flex items-center justify-between text-combine-green">
                <span class="font-hev">İndirim</span>
                <span class="font-lambda">-₺{{ discount }}</span>
              </div>

              <div class="border-t border-cyber-border pt-3 mt-3">
                <div class="flex items-center justify-between">
                  <span class="text-lg font-lambda text-text-primary">Toplam</span>
                  <span class="text-3xl font-lambda neon-orange">₺{{ totalPrice }}</span>
                </div>
                <div class="text-right text-sm text-text-secondary font-hev mt-1">
                  ({{ config.billing_period }} ay için ₺{{ totalPrice * config.billing_period }})
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-3">
              <button
                @click="orderWithWallet"
                :disabled="ordering"
                class="flex-1 px-6 py-4 bg-lambda-gradient text-cyber-black font-lambda font-bold text-lg rounded hover:shadow-neon-orange transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <Wallet :size="20" class="inline mr-2" />
                CÜZDANLA ÖDE
              </button>

              <button
                @click="orderWithCard"
                :disabled="ordering"
                class="flex-1 px-6 py-4 bg-hev-cyan bg-opacity-10 border-2 border-hev-cyan text-hev-cyan font-lambda font-bold text-lg rounded hover:bg-hev-cyan hover:text-cyber-black transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <CreditCard :size="20" class="inline mr-2" />
                KARTLA ÖDE
              </button>
            </div>

            <p class="text-xs text-text-secondary font-hev text-center mt-4">
              Sunucunuz ödeme sonrası otomatik olarak kurulacaktır
            </p>
          </div>
        </div>

        <!-- Features -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center p-6 bg-cyber-panel border border-cyber-border rounded">
            <Zap :size="32" class="inline text-lambda-orange mb-3" />
            <h3 class="font-lambda font-bold text-text-primary mb-2">Anlık Kurulum</h3>
            <p class="text-sm text-text-secondary font-hev">Dakikalar içinde aktif</p>
          </div>

          <div class="text-center p-6 bg-cyber-panel border border-cyber-border rounded">
            <Shield :size="32" class="inline text-combine-green mb-3" />
            <h3 class="font-lambda font-bold text-text-primary mb-2">DDoS Koruması</h3>
            <p class="text-sm text-text-secondary font-hev">Sınırsız koruma</p>
          </div>

          <div class="text-center p-6 bg-cyber-panel border border-cyber-border rounded">
            <Headphones :size="32" class="inline text-hev-cyan mb-3" />
            <h3 class="font-lambda font-bold text-text-primary mb-2">7/24 Destek</h3>
            <p class="text-sm text-text-secondary font-hev">Her zaman yanınızdayız</p>
          </div>

          <div class="text-center p-6 bg-cyber-panel border border-cyber-border rounded">
            <TrendingUp :size="32" class="inline text-xen-purple mb-3" />
            <h3 class="font-lambda font-bold text-text-primary mb-2">99.9% Uptime</h3>
            <p class="text-sm text-text-secondary font-hev">Kesintisiz hizmet</p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useServersStore } from '@/stores/servers'
import serversAPI from '@/api/servers'
import {
  Users,
  Cpu,
  HardDrive,
  Database,
  Shield,
  Zap,
  Wallet,
  CreditCard,
  Headphones,
  TrendingUp
} from 'lucide-vue-next'

const router = useRouter()
const serversStore = useServersStore()

const loading = ref(false)
const ordering = ref(false)
const packages = ref([])
const selectedPackage = ref(null)

const config = ref({
  server_name: '',
  game_type: 'cs16',
  region: 'istanbul',
  billing_period: 1,
  addons: {
    backup: false,
    mysql: false,
    priority_support: false,
    custom_plugins: false
  }
})

// Computed
const addonTotal = computed(() => {
  let total = 0
  if (config.value.addons.backup) total += 20
  if (config.value.addons.mysql) total += 30
  if (config.value.addons.priority_support) total += 50
  if (config.value.addons.custom_plugins) total += 40
  return total
})

const discount = computed(() => {
  if (!selectedPackage.value) return 0

  const basePrice = selectedPackage.value.price_monthly + addonTotal.value
  const period = config.value.billing_period

  if (period === 3) return Math.floor(basePrice * 0.05)
  if (period === 6) return Math.floor(basePrice * 0.10)
  if (period === 12) return Math.floor(basePrice * 0.15)

  return 0
})

const totalPrice = computed(() => {
  if (!selectedPackage.value) return 0
  return selectedPackage.value.price_monthly + addonTotal.value - discount.value
})

// Methods
function selectPackage(pkg) {
  selectedPackage.value = pkg
}

function updatePrice() {
  // Trigger reactivity
  selectedPackage.value = { ...selectedPackage.value }
}

async function orderWithWallet() {
  if (!selectedPackage.value || ordering.value) return
  if (!config.value.server_name.trim()) {
    alert('Lütfen sunucu adı girin')
    return
  }

  ordering.value = true
  try {
    const orderData = {
      package_id: selectedPackage.value.id,
      server_name: config.value.server_name,
      game_type: config.value.game_type,
      region: config.value.region,
      billing_period: config.value.billing_period,
      addons: config.value.addons
    }

    await serversAPI.orderPackageWallet(orderData)
    alert('Sunucu siparişiniz alındı! Kurulum başlatılıyor...')
    router.push('/servers/my')
  } catch (err) {
    alert(err.response?.data?.detail || 'Sipariş oluşturulamadı. Lütfen cüzdan bakiyenizi kontrol edin.')
  } finally {
    ordering.value = false
  }
}

async function orderWithCard() {
  if (!selectedPackage.value || ordering.value) return
  if (!config.value.server_name.trim()) {
    alert('Lütfen sunucu adı girin')
    return
  }

  ordering.value = true
  try {
    const orderData = {
      package_id: selectedPackage.value.id,
      server_name: config.value.server_name,
      game_type: config.value.game_type,
      region: config.value.region,
      billing_period: config.value.billing_period,
      addons: config.value.addons
    }

    const response = await serversAPI.orderPackage(orderData)

    // Redirect to payment page
    if (response.data.payment_url) {
      window.location.href = response.data.payment_url
    } else {
      alert('Sipariş oluşturuldu! Ödeme sayfasına yönlendiriliyorsunuz...')
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Sipariş oluşturulamadı')
  } finally {
    ordering.value = false
  }
}

async function loadPackages() {
  loading.value = true
  try {
    const response = await serversAPI.getPackages()
    packages.value = response.data.packages || response.data || []

    // Mock packages if API returns empty
    if (packages.value.length === 0) {
      packages.value = [
        {
          id: 1,
          name: 'BAŞLANGIÇ',
          description: 'Küçük topluluklar için ideal',
          max_players: 16,
          cpu_cores: 2,
          ram_gb: 2,
          disk_gb: 10,
          price_monthly: 99,
          is_popular: false
        },
        {
          id: 2,
          name: 'STANDART',
          description: 'Orta büyüklükte sunucular için',
          max_players: 32,
          cpu_cores: 4,
          ram_gb: 4,
          disk_gb: 20,
          price_monthly: 199,
          is_popular: true
        },
        {
          id: 3,
          name: 'PRO',
          description: 'Profesyonel ve büyük sunucular',
          max_players: 64,
          cpu_cores: 8,
          ram_gb: 8,
          disk_gb: 50,
          price_monthly: 349,
          is_popular: false
        }
      ]
    }
  } catch (err) {
    console.error('Load packages error:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadPackages()
})
</script>

<style scoped>
.bg-lambda-gradient {
  background: linear-gradient(135deg, #FF6B35 0%, #E85D2C 100%);
}

.neon-orange {
  color: #FF6B35;
  text-shadow: 0 0 10px rgba(255, 107, 53, 0.8);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}
</style>
