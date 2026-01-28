<template>
  <div class="container mx-auto px-4 py-8 max-w-[1400px]">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-text-primary mb-2">Mağaza</h1>
      <p class="text-text-secondary">Sunucu paketleri, premium özellikler ve daha fazlası</p>
    </div>

    <!-- Categories -->
    <div class="flex gap-3 mb-8 overflow-x-auto pb-2">
      <button
        v-for="category in categories"
        :key="category.value"
        @click="currentCategory = category.value"
        class="px-6 py-2 rounded-lg whitespace-nowrap transition-all"
        :class="currentCategory === category.value
          ? 'bg-primary text-white'
          : 'bg-dark-card text-text-secondary hover:bg-dark-hover border border-dark-border'"
      >
        {{ category.icon }} {{ category.label }}
      </button>
    </div>

    <!-- Products Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <!-- Server Packages -->
      <template v-if="currentCategory === 'servers'">
        <div
          v-for="pkg in serverPackages"
          :key="pkg.id"
          class="card overflow-hidden hover:border-primary/50 transition-all"
        >
          <!-- Package Header -->
          <div class="p-6 bg-gradient-to-br from-primary/10 to-primary/5 border-b border-dark-border">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-xl font-bold text-text-primary">{{ pkg.name }}</h3>
              <span
                v-if="pkg.popular"
                class="badge bg-primary text-white text-xs px-2 py-1"
              >
                Popüler
              </span>
            </div>
            <p class="text-text-secondary text-sm">{{ pkg.description }}</p>
          </div>

          <!-- Package Details -->
          <div class="p-6">
            <div class="space-y-3 mb-6">
              <div class="flex items-center gap-2 text-sm">
                <svg class="w-5 h-5 text-status-success" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="text-text-primary">{{ pkg.slots }} Slot</span>
              </div>
              <div class="flex items-center gap-2 text-sm">
                <svg class="w-5 h-5 text-status-success" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="text-text-primary">{{ pkg.ram }}MB RAM</span>
              </div>
              <div class="flex items-center gap-2 text-sm">
                <svg class="w-5 h-5 text-status-success" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="text-text-primary">{{ pkg.storage }}GB Disk</span>
              </div>
              <div class="flex items-center gap-2 text-sm">
                <svg class="w-5 h-5 text-status-success" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="text-text-primary">DDoS Koruması</span>
              </div>
            </div>

            <div class="border-t border-dark-border pt-4 mb-4">
              <div class="flex items-baseline gap-2 mb-1">
                <span class="text-3xl font-bold text-primary">₺{{ pkg.price }}</span>
                <span class="text-text-muted text-sm">/ay</span>
              </div>
              <p class="text-xs text-text-muted">
                {{ pkg.daily_cost }} ₺/gün
              </p>
            </div>

            <button
              @click="selectPackage(pkg)"
              class="btn btn-primary w-full"
            >
              Satın Al
            </button>
          </div>
        </div>
      </template>

      <!-- Premium Features -->
      <template v-if="currentCategory === 'premium'">
        <div
          v-for="feature in premiumFeatures"
          :key="feature.id"
          class="card p-6 hover:border-primary/50 transition-all"
        >
          <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
            <span class="text-2xl">{{ feature.icon }}</span>
          </div>
          <h3 class="text-lg font-semibold text-text-primary mb-2">{{ feature.name }}</h3>
          <p class="text-sm text-text-secondary mb-4">{{ feature.description }}</p>
          <div class="flex items-baseline gap-2 mb-4">
            <span class="text-2xl font-bold text-primary">₺{{ feature.price }}</span>
            <span class="text-text-muted text-sm">{{ feature.period }}</span>
          </div>
          <button @click="selectFeature(feature)" class="btn btn-primary w-full">
            Satın Al
          </button>
        </div>
      </template>

      <!-- Plugins -->
      <template v-if="currentCategory === 'plugins'">
        <div
          v-for="plugin in plugins"
          :key="plugin.id"
          class="card p-6 hover:border-primary/50 transition-all"
        >
          <div class="flex items-start gap-3 mb-4">
            <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
              <span class="text-2xl">🔌</span>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-semibold text-text-primary mb-1">{{ plugin.name }}</h3>
              <p class="text-xs text-text-muted">v{{ plugin.version }}</p>
            </div>
          </div>
          <p class="text-sm text-text-secondary mb-4">{{ plugin.description }}</p>
          <div class="flex items-center justify-between">
            <span class="text-xl font-bold text-primary">{{ plugin.free ? 'Ücretsiz' : `₺${plugin.price}` }}</span>
            <button
              @click="installPlugin(plugin)"
              class="btn"
              :class="plugin.free ? 'btn-secondary' : 'btn-primary'"
            >
              {{ plugin.free ? 'Kur' : 'Satın Al' }}
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- Shopping Cart -->
    <div v-if="cart.length > 0" class="fixed bottom-6 right-6 z-50">
      <button
        @click="showCart = !showCart"
        class="relative btn btn-primary shadow-lg"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
        </svg>
        Sepet
        <span class="absolute -top-2 -right-2 w-6 h-6 bg-status-error text-white text-xs rounded-full flex items-center justify-center">
          {{ cart.length }}
        </span>
      </button>
    </div>

    <!-- Cart Modal -->
    <div v-if="showCart" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-text-primary">Sepetim</h3>
          <button @click="showCart = false" class="text-text-muted hover:text-text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div v-if="cart.length === 0" class="text-center py-12 text-text-muted">
          Sepetiniz boş
        </div>

        <div v-else class="space-y-4 mb-6">
          <div
            v-for="item in cart"
            :key="item.id"
            class="flex items-center gap-4 p-4 rounded-lg border border-dark-border"
          >
            <div class="flex-1">
              <p class="font-medium text-text-primary">{{ item.name }}</p>
              <p class="text-sm text-text-muted">{{ item.description }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-primary">₺{{ item.price }}</p>
              <button @click="removeFromCart(item.id)" class="text-xs text-status-error hover:underline">
                Kaldır
              </button>
            </div>
          </div>
        </div>

        <div class="border-t border-dark-border pt-4">
          <div class="flex items-center justify-between mb-4">
            <span class="text-lg font-semibold text-text-primary">Toplam:</span>
            <span class="text-2xl font-bold text-primary">₺{{ cartTotal }}</span>
          </div>
          <div class="flex gap-3">
            <button @click="showCart = false" class="btn btn-secondary flex-1">
              Alışverişe Devam
            </button>
            <button @click="checkout" class="btn btn-primary flex-1">
              Ödemeye Geç
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const currentCategory = ref('servers')
const cart = ref([])
const showCart = ref(false)

const categories = [
  { value: 'servers', label: 'Sunucu Paketleri', icon: '🎮' },
  { value: 'premium', label: 'Premium Özellikler', icon: '⭐' },
  { value: 'plugins', label: 'Pluginler', icon: '🔌' }
]

const serverPackages = [
  {
    id: 1,
    name: 'Başlangıç',
    description: 'Küçük sunucular için ideal',
    slots: 10,
    ram: 512,
    storage: 5,
    price: 25,
    daily_cost: 0.83,
    popular: false
  },
  {
    id: 2,
    name: 'Standart',
    description: 'Orta ölçekli sunucular',
    slots: 20,
    ram: 1024,
    storage: 10,
    price: 45,
    daily_cost: 1.5,
    popular: true
  },
  {
    id: 3,
    name: 'Pro',
    description: 'Büyük sunucular için',
    slots: 32,
    ram: 2048,
    storage: 20,
    price: 75,
    daily_cost: 2.5,
    popular: false
  }
]

const premiumFeatures = [
  {
    id: 1,
    name: 'Premium Üyelik',
    description: 'Tüm özelliklere erişim, öncelikli destek',
    price: 50,
    period: '/ay',
    icon: '👑'
  },
  {
    id: 2,
    name: 'Özel Plugin Geliştirme',
    description: 'Kendi özel plugininizi geliştirin',
    price: 200,
    period: '/proje',
    icon: '⚙️'
  },
  {
    id: 3,
    name: 'Sunucu Yönetimi',
    description: '7/24 profesyonel sunucu yönetimi',
    price: 100,
    period: '/ay',
    icon: '🛠️'
  }
]

const plugins = [
  {
    id: 1,
    name: 'Anti-Cheat Pro',
    version: '2.5.1',
    description: 'Gelişmiş hile tespit sistemi',
    price: 15,
    free: false
  },
  {
    id: 2,
    name: 'Admin Tools',
    version: '1.8.0',
    description: 'Sunucu yönetim araçları',
    price: 0,
    free: true
  },
  {
    id: 3,
    name: 'Map Manager',
    version: '3.2.0',
    description: 'Harita yönetimi ve rotasyon',
    price: 10,
    free: false
  }
]

const cartTotal = computed(() => {
  return cart.value.reduce((sum, item) => sum + item.price, 0).toFixed(2)
})

const selectPackage = (pkg) => {
  cart.value.push({
    id: `pkg-${pkg.id}`,
    name: pkg.name,
    description: `${pkg.slots} slot sunucu paketi`,
    price: pkg.price
  })
  showCart.value = true
}

const selectFeature = (feature) => {
  cart.value.push({
    id: `feature-${feature.id}`,
    name: feature.name,
    description: feature.description,
    price: feature.price
  })
  showCart.value = true
}

const installPlugin = (plugin) => {
  if (plugin.free) {
    console.log('Installing free plugin:', plugin.name)
    // TODO: Install plugin
  } else {
    cart.value.push({
      id: `plugin-${plugin.id}`,
      name: plugin.name,
      description: plugin.description,
      price: plugin.price
    })
    showCart.value = true
  }
}

const removeFromCart = (itemId) => {
  cart.value = cart.value.filter(item => item.id !== itemId)
}

const checkout = () => {
  // TODO: Implement checkout
  console.log('Checkout:', cart.value)
  router.push('/wallet')
}
</script>
