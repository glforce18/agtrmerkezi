<template>
  <div class="relative min-h-screen">
    <!-- Background -->
    <div class="fixed inset-0 z-0">
      <img :src="getBackgroundImage('energy')" alt="" class="absolute inset-0 w-full h-full object-cover opacity-65" />
      <div class="absolute inset-0 bg-gradient-to-b from-dark-bg/40 via-dark-bg/55 to-dark-bg/70"></div>
      <div class="absolute inset-0 bg-gradient-radial from-primary/15 via-transparent to-transparent"></div>
    </div>

    <div class="container mx-auto px-4 py-8 relative z-10">
      <!-- Header -->
      <div class="text-center mb-12 space-y-4">
        <div class="inline-block px-6 py-2 bg-primary/20 border border-primary rounded-full text-primary text-sm font-bold mb-4">
          🎮 PROFESYONEL GAME SERVER HOSTING
        </div>
        <h1 class="text-5xl md:text-6xl font-lambda font-bold text-white mb-4 tracking-tight">
          Sunucu <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-orange-500">Kirala</span>
        </h1>
        <p class="text-gray-400 text-lg max-w-2xl mx-auto">
          Counter-Strike 1.6 & Half-Life sunucunuzu <span class="text-primary font-semibold">5 dakikada</span> başlatın
        </p>
      </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-primary text-4xl mb-4">⏳</div>
      <p class="text-gray-400">Paketler yükleniyor...</p>
    </div>

    <div v-else>
      <!-- Features Section -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12 max-w-6xl mx-auto">
        <div class="feature-card group hover:border-primary hover:bg-primary/5 transition-all duration-300">
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">⚡</div>
          <div class="font-bold text-white mb-1 text-sm">Hızlı Kurulum</div>
          <div class="text-gray-400 text-xs">5 dakikada aktif</div>
        </div>

        <div class="feature-card group hover:border-primary hover:bg-primary/5 transition-all duration-300">
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">🔧</div>
          <div class="font-bold text-white mb-1 text-sm">RCON Kontrolü</div>
          <div class="text-gray-400 text-xs">Tam yönetim</div>
        </div>

        <div class="feature-card group hover:border-primary hover:bg-primary/5 transition-all duration-300">
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">🛡️</div>
          <div class="font-bold text-white mb-1 text-sm">DDoS Koruması</div>
          <div class="text-gray-400 text-xs">Güvenli altyapı</div>
        </div>

        <div class="feature-card group hover:border-primary hover:bg-primary/5 transition-all duration-300">
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">💬</div>
          <div class="font-bold text-white mb-1 text-sm">7/24 Destek</div>
          <div class="text-gray-400 text-xs">Her zaman yanınızda</div>
        </div>
      </div>

      <!-- Package Selection -->
      <div class="mb-8">
        <h2 class="text-2xl font-lambda font-bold text-white mb-6 text-center">Paketlerimiz</h2>

        <div v-if="!packages.length" class="text-center py-12 bg-dark-card border border-primary/30 rounded-lg">
          <div class="text-6xl mb-4">📦</div>
          <p class="text-gray-400">Henüz paket bulunmuyor</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          <div
            v-for="pkg in packages"
            :key="pkg.id"
            class="package-card group"
            :class="{ 'popular': pkg.is_popular, 'selected': selectedPackage?.id === pkg.id }"
            @click="selectPackage(pkg)"
          >
            <!-- Popular Badge -->
            <div v-if="pkg.is_popular" class="popular-badge">
              <span class="text-xs font-bold">⭐ POPÜLER</span>
            </div>

            <!-- Package Image -->
            <div class="package-image-wrapper relative overflow-hidden rounded-t-lg">
              <img
                :src="getPackageImage(pkg.name)"
                :alt="pkg.name"
                class="package-image w-full h-56 object-contain"
                @error="handleImageError"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-dark-bg/80 via-transparent to-transparent"></div>
            </div>

            <!-- Package Content -->
            <div class="p-6 space-y-4">
              <!-- Title & Description -->
              <div class="text-center border-b border-primary/20 pb-4">
                <h3 class="text-xl font-bold text-white mb-2 line-clamp-1">{{ pkg.name }}</h3>
                <p class="text-gray-400 text-xs leading-relaxed line-clamp-2">{{ pkg.description }}</p>
              </div>

              <!-- Price -->
              <div class="text-center py-3 bg-primary/10 rounded-lg border border-primary/30">
                <div class="text-3xl font-bold text-primary">₺{{ pkg.price }}</div>
                <div class="text-gray-400 text-xs mt-1">Aylık Ödeme</div>
              </div>

              <!-- Features -->
              <div class="space-y-2">
                <!-- Slots -->
                <div class="flex items-center justify-between text-xs px-3 py-2 bg-dark-bg/50 rounded hover:bg-dark-bg/70 transition-colors">
                  <span class="text-gray-400 flex items-center gap-1">
                    <span class="text-primary">👥</span> Maksimum Oyuncu
                  </span>
                  <span class="text-white font-bold">{{ pkg.max_slots }} Kişi</span>
                </div>

                <!-- Tick Rate -->
                <div class="flex items-center justify-between text-xs px-3 py-2 bg-dark-bg/50 rounded hover:bg-dark-bg/70 transition-colors">
                  <span class="text-gray-400 flex items-center gap-1">
                    <span class="text-primary">⚡</span> Tick Rate
                  </span>
                  <span class="text-white font-bold">1000 FPS</span>
                </div>

                <!-- Ping -->
                <div class="flex items-center justify-between text-xs px-3 py-2 bg-dark-bg/50 rounded hover:bg-dark-bg/70 transition-colors">
                  <span class="text-gray-400 flex items-center gap-1">
                    <span class="text-primary">📡</span> Ortalama Ping
                  </span>
                  <span class="text-white font-bold">5-15ms</span>
                </div>

                <!-- Mod Support -->
                <div class="flex items-center justify-between text-xs px-3 py-2 bg-dark-bg/50 rounded hover:bg-dark-bg/70 transition-colors">
                  <span class="text-gray-400 flex items-center gap-1">
                    <span class="text-primary">🎮</span> Mod/Plugin
                  </span>
                  <span class="text-white font-bold">Sınırsız</span>
                </div>

                <!-- Map Support -->
                <div class="flex items-center justify-between text-xs px-3 py-2 bg-dark-bg/50 rounded hover:bg-dark-bg/70 transition-colors">
                  <span class="text-gray-400 flex items-center gap-1">
                    <span class="text-primary">🗺️</span> Harita Desteği
                  </span>
                  <span class="text-white font-bold">Tüm Haritalar</span>
                </div>

                <!-- Admin Tools -->
                <div class="flex items-center justify-between text-xs px-3 py-2 bg-dark-bg/50 rounded hover:bg-dark-bg/70 transition-colors">
                  <span class="text-gray-400 flex items-center gap-1">
                    <span class="text-primary">🛠️</span> Admin Panel
                  </span>
                  <span class="text-white font-bold">Web + RCON</span>
                </div>

                <!-- Included Features -->
                <div class="border-t border-primary/20 pt-3 mt-2">
                  <div class="text-xs text-gray-400 mb-2 font-semibold">🎯 Oyun Özellikleri:</div>
                  <div class="grid grid-cols-2 gap-2 text-xs">
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">AMX Mod X</span>
                    </div>
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">MetaMod</span>
                    </div>
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">Custom Maplar</span>
                    </div>
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">Fast Download</span>
                    </div>
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">HLTV Desteği</span>
                    </div>
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">Anti-Cheat</span>
                    </div>
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">Stat Tracking</span>
                    </div>
                    <div class="flex items-center gap-1 text-green-400">
                      <span>✓</span> <span class="text-gray-300">7/24 Aktif</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Select Button -->
              <button
                @click.stop="selectPackage(pkg)"
                class="w-full btn-select"
                :class="{ 'selected': selectedPackage?.id === pkg.id }"
              >
                <span v-if="selectedPackage?.id === pkg.id" class="flex items-center justify-center gap-2">
                  <span class="text-lg">✓</span> SEÇİLDİ
                </span>
                <span v-else class="flex items-center justify-center gap-2">
                  <span>🎮</span> SEÇ
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Form -->
      <div v-if="selectedPackage" class="max-w-2xl mx-auto">
        <div class="bg-dark-card border border-primary rounded-lg p-6">
          <h2 class="text-2xl font-lambda font-bold text-white mb-6">Sipariş Detayları</h2>

          <form @submit.prevent="handleOrder" class="space-y-4">
            <!-- Server Name -->
            <div>
              <label class="block text-gray-400 text-sm mb-2">Sunucu Adı</label>
              <input
                v-model="orderForm.server_name"
                type="text"
                class="form-input"
                placeholder="Benim CS 1.6 Sunucum"
                required
                maxlength="50"
              />
              <p class="text-gray-500 text-xs mt-1">Sunucunuzun görünen adı</p>
            </div>

            <!-- Duration -->
            <div>
              <label class="block text-gray-400 text-sm mb-2">Süre</label>
              <select v-model="orderForm.duration" class="form-input" required>
                <option value="1">1 Ay</option>
                <option value="3">3 Ay (%10 İndirim)</option>
                <option value="6">6 Ay (%15 İndirim)</option>
                <option value="12">12 Ay (%20 İndirim)</option>
              </select>
            </div>

            <!-- Order Summary -->
            <div class="bg-dark-bg border border-primary/30 rounded-lg p-4">
              <h3 class="text-lg font-bold text-white mb-3">Sipariş Özeti</h3>

              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-400">Paket:</span>
                  <span class="text-white">{{ selectedPackage.name }}</span>
                </div>

                <div class="flex justify-between">
                  <span class="text-gray-400">Süre:</span>
                  <span class="text-white">{{ orderForm.duration }} Ay</span>
                </div>

                <div v-if="discount > 0" class="flex justify-between text-green-400">
                  <span>İndirim:</span>
                  <span>-₺{{ calculateDiscount() }}</span>
                </div>

                <div class="border-t border-gray-700 pt-2 mt-2">
                  <div class="flex justify-between text-lg font-bold">
                    <span class="text-white">Toplam:</span>
                    <span class="text-primary">₺{{ calculateTotal() }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Terms -->
            <div class="flex items-start space-x-2">
              <input
                v-model="orderForm.accept_terms"
                type="checkbox"
                id="order-terms"
                class="mt-1"
                required
              />
              <label for="order-terms" class="text-gray-400 text-sm">
                <router-link to="/terms" class="text-primary hover:underline">Kullanım Şartlarını</router-link>
                ve
                <router-link to="/refund" class="text-primary hover:underline">İptal ve İade Koşullarını</router-link>
                kabul ediyorum
              </label>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="p-3 bg-red-500/20 border border-red-500/50 rounded text-red-400 text-sm">
              {{ error }}
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="ordering || !orderForm.accept_terms"
              class="w-full btn-primary-large"
              :class="{ 'opacity-50 cursor-not-allowed': ordering || !orderForm.accept_terms }"
            >
              {{ ordering ? 'Sipariş Oluşturuluyor...' : `Siparişi Tamamla (₺${calculateTotal()})` }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import serversAPI from '@/api/servers'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const packages = ref([])
const selectedPackage = ref(null)
const ordering = ref(false)
const error = ref(null)

const orderForm = ref({
  server_name: '',
  duration: '1',
  accept_terms: false
})

const discount = computed(() => {
  const duration = parseInt(orderForm.value.duration)
  if (duration >= 12) return 20
  if (duration >= 6) return 15
  if (duration >= 3) return 10
  return 0
})

onMounted(async () => {
  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: '/servers/rent' } })
    return
  }

  await fetchPackages()
})

const fetchPackages = async () => {
  try {
    const response = await serversAPI.getPackages()
    // Map API response to component expectations
    const apiData = response.data.data || response.data.packages || response.data
    packages.value = apiData.map(pkg => ({
      id: pkg.id,
      slug: pkg.slug,
      name: pkg.name,
      game_type: pkg.game_type,
      description: pkg.description || 'Yüksek performanslı oyun sunucusu - AMX Mod X, MetaMod ve tüm plugin desteği',
      max_slots: pkg.max_slots || pkg.slots,  // API returns 'max_slots'
      price: pkg.price || pkg.price_monthly,  // API returns 'price'
      is_popular: pkg.is_popular || false,
      is_active: pkg.is_active !== false
    }))
  } catch (err) {
    console.error('Failed to fetch packages:', err)
    error.value = 'Paketler yüklenirken hata oluştu'
  } finally {
    loading.value = false
  }
}

const selectPackage = (pkg) => {
  selectedPackage.value = pkg

  // Scroll to order form
  setTimeout(() => {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: 'smooth'
    })
  }, 100)
}

const calculateDiscount = () => {
  if (!selectedPackage.value) return 0
  const basePrice = selectedPackage.value.price * parseInt(orderForm.value.duration)
  return Math.floor(basePrice * (discount.value / 100))
}

const calculateTotal = () => {
  if (!selectedPackage.value) return 0
  const basePrice = selectedPackage.value.price * parseInt(orderForm.value.duration)
  const discountAmount = calculateDiscount()
  return basePrice - discountAmount
}

const handleOrder = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: '/servers/rent' } })
    return
  }

  error.value = null
  ordering.value = true

  try {
    // Use wallet order endpoint
    const response = await serversAPI.orderPackageWallet({
      package_id: selectedPackage.value.id,
      server_name: orderForm.value.server_name,
      months: parseInt(orderForm.value.duration),
      payment_type: 'TL', // Use TL wallet by default
      auto_renew: true // Enable auto-renewal by default
    })

    // Show success message and redirect to server panel
    if (response.data.success && response.data.order && response.data.order.server_id) {
      // Show success toast
      alert(`Siparişiniz oluşturuldu! Admin onayından sonra sunucunuz kurulacak.`)
      // Redirect to my servers page
      router.push('/servers/my')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Sipariş oluşturulamadı'
  } finally {
    ordering.value = false
  }
}

const getDurationText = (duration) => {
  return duration === 'monthly' ? 'Ay' : 'Yıl'
}

const getPackageImage = (packageName) => {
  // Map package names to image files
  const baseUrl = window.location.origin
  const imageMap = {
    'Half-Life Deathmatch': `${baseUrl}/static/images/packages/hlpaket.png`,
    'Half-Life Adrenaline Gamer': `${baseUrl}/static/images/packages/hlagpaket.png`,
    'CS 1.6 Pro/Public': `${baseUrl}/static/images/packages/cspropublicpaket.png`,
    'CS 1.6 Fun/Zombie': `${baseUrl}/static/images/packages/cszombiefunpaket.png`
  }
  return imageMap[packageName] || `${baseUrl}/static/images/packages/default.png`
}

const handleImageError = (event) => {
  console.error('Image failed to load:', event.target.src)
  // Optionally set a fallback image
  event.target.style.display = 'none'
}

// Background image helper
const getBackgroundImage = (name) => {
  const baseUrl = window.location.origin
  return `${baseUrl}/static/images/backgrounds/${name}.jpg`
}
</script>

<style scoped>
.feature-card {
  @apply text-center rounded-lg p-4;
  background: rgba(26, 26, 30, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 119, 0, 0.2);
  animation: fadeInUp 0.5s ease-out forwards;
}

.package-card {
  background: rgba(26, 26, 30, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  @apply border-2 border-primary/20 rounded-xl cursor-pointer transition-all duration-500 relative shadow-xl overflow-hidden;
  min-height: 680px;
  display: flex;
  flex-direction: column;
  animation: fadeInUp 0.6s ease-out forwards;
}

.package-card:hover {
  @apply border-primary transform -translate-y-2 shadow-2xl;
  background: rgba(26, 26, 30, 0.9);
  box-shadow: 0 25px 50px rgba(255, 119, 0, 0.3);
}

.package-card.selected {
  @apply border-primary bg-primary/5;
  box-shadow: 0 0 30px rgba(255, 119, 0, 0.3);
}

.package-card.popular {
  @apply border-primary;
  box-shadow: 0 0 20px rgba(255, 119, 0, 0.2);
}

.package-image-wrapper {
  @apply bg-dark-bg/50;
}

.package-image {
  @apply transition-all duration-500;
  object-fit: contain;
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.8) 0%, rgba(17, 24, 39, 0.95) 100%);
}

.package-card:hover .package-image {
  @apply scale-110;
  filter: brightness(1.1);
}

.package-card.popular {
  @apply border-primary bg-primary/5;
}

.popular-badge {
  @apply absolute top-0 right-0 z-10 px-3 py-1 bg-primary text-white rounded-bl-lg rounded-tr-lg;
}

.btn-select {
  @apply w-full px-6 py-3 bg-gradient-to-r from-primary to-orange-600 text-white rounded-lg hover:from-orange-600 hover:to-primary transition-all duration-300 font-bold text-sm uppercase tracking-wider shadow-lg hover:shadow-xl;
  border: 2px solid transparent;
}

.btn-select:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(255, 119, 0, 0.3);
}

.btn-select.selected {
  @apply bg-gradient-to-r from-green-500 to-green-600;
  border-color: #10b981;
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
}

.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.form-input {
  @apply w-full bg-dark-bg border border-primary/30 text-white rounded px-4 py-2 focus:border-primary outline-none transition-colors duration-200;
}

.btn-primary-large {
  @apply px-6 py-4 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors duration-200 font-bold text-lg;
}
</style>
