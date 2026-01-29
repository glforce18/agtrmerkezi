<template>
  <nav
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 border-b"
    :class="[
      scrolled
        ? 'bg-dark-card/98 backdrop-blur-xl border-dark-border shadow-2xl shadow-primary/10'
        : 'bg-dark-card/95 backdrop-blur-lg border-dark-border/50'
    ]"
  >
    <div class="container mx-auto px-4">
      <div
        class="flex items-center justify-between transition-all duration-300"
        :class="scrolled ? 'h-14' : 'h-16'"
      >
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3 group">
          <div class="w-10 h-10 bg-primary rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform">
            <span class="text-2xl font-bold text-white">λ</span>
          </div>
          <span class="text-xl font-bold text-text-primary hidden sm:block">AGTR Merkezi</span>
        </router-link>

        <!-- Navigation Links - Desktop -->
        <div class="hidden md:flex items-center gap-1">
          <router-link to="/" class="nav-link">
            Ana Sayfa
          </router-link>
          <router-link to="/servers" class="nav-link">
            Sunucular
          </router-link>
          <router-link to="/forum" class="nav-link">
            Forum
          </router-link>
          <router-link to="/servers/rent" class="nav-link">
            Kirala
          </router-link>
        </div>

        <!-- User Menu -->
        <div class="flex items-center gap-3">
          <template v-if="authStore.isAuthenticated">
            <!-- Wallet Balance -->
            <router-link to="/wallet" class="hidden lg:flex items-center gap-3 px-3 py-1.5 bg-dark-elevated hover:bg-dark-hover rounded-lg border border-dark-border transition-all group">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <div class="flex flex-col">
                  <span class="text-xs text-text-muted leading-none">Bakiye</span>
                  <span class="text-sm font-bold text-amber-400 leading-none mt-0.5">{{ tlBalance }}₺</span>
                </div>
              </div>
              <div class="h-8 w-px bg-dark-border"></div>
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                  </svg>
                </div>
                <div class="flex flex-col">
                  <span class="text-xs text-text-muted leading-none">Armor</span>
                  <span class="text-sm font-bold text-primary leading-none mt-0.5">{{ armorBalance }}</span>
                </div>
              </div>
            </router-link>

            <router-link to="/servers/my" class="hidden lg:inline-flex nav-link">
              Sunucularım
            </router-link>
            <router-link v-if="authStore.isAdmin" to="/admin" class="hidden lg:inline-flex">
              <span class="badge badge-success">Admin</span>
            </router-link>
            <router-link to="/profile" class="flex items-center gap-2 nav-link">
              <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" :alt="authStore.user.username" class="w-8 h-8 rounded-full" />
              <span class="hidden lg:inline">{{ authStore.user?.username }}</span>
            </router-link>
            <button @click="handleLogout" class="btn btn-ghost">Çıkış</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn btn-primary">Steam ile Giriş</router-link>
          </template>

          <!-- Mobile Menu Button -->
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden btn btn-ghost p-2">
            <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div v-if="mobileMenuOpen" class="md:hidden py-4 border-t border-dark-border">
        <div class="flex flex-col gap-2">
          <!-- Mobile Wallet Balance -->
          <div v-if="authStore.isAuthenticated" class="px-4 py-3 bg-dark-elevated rounded-lg border border-dark-border mb-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <div>
                  <div class="text-xs text-text-muted">Bakiye</div>
                  <div class="text-sm font-bold text-amber-400">{{ tlBalance }}₺</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                  </svg>
                </div>
                <div>
                  <div class="text-xs text-text-muted">Armor</div>
                  <div class="text-sm font-bold text-primary">{{ armorBalance }}</div>
                </div>
              </div>
            </div>
          </div>

          <router-link @click="mobileMenuOpen = false" to="/" class="nav-link-mobile">
            Ana Sayfa
          </router-link>
          <router-link @click="mobileMenuOpen = false" to="/servers" class="nav-link-mobile">
            Sunucular
          </router-link>
          <router-link @click="mobileMenuOpen = false" to="/forum" class="nav-link-mobile">
            Forum
          </router-link>
          <router-link @click="mobileMenuOpen = false" to="/servers/rent" class="nav-link-mobile">
            Kirala
          </router-link>
          <template v-if="authStore.isAuthenticated">
            <div class="divider my-2"></div>
            <router-link @click="mobileMenuOpen = false" to="/wallet" class="nav-link-mobile">
              💰 Cüzdan
            </router-link>
            <router-link @click="mobileMenuOpen = false" to="/servers/my" class="nav-link-mobile">
              Sunucularım
            </router-link>
            <router-link @click="mobileMenuOpen = false" to="/profile" class="nav-link-mobile">
              Profil
            </router-link>
            <router-link v-if="authStore.isAdmin" @click="mobileMenuOpen = false" to="/admin" class="nav-link-mobile">
              Admin Panel
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>

  <!-- Spacer for fixed navbar -->
  <div class="h-16"></div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const mobileMenuOpen = ref(false)
const scrolled = ref(false)

const handleScroll = () => {
  scrolled.value = window.scrollY > 20
}

// Computed properties for balance with fallback
const tlBalance = computed(() => {
  const val = authStore.balance?.balance_real || authStore.user?.balance || 0
  return parseFloat(val).toFixed(2)
})

const armorBalance = computed(() => {
  const val = authStore.balance?.balance_coin || authStore.user?.balance_coin || 0
  const num = parseFloat(val)
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toFixed(0)
})

onMounted(async () => {
  window.addEventListener('scroll', handleScroll)
  // Fetch balance on mount if authenticated
  if (authStore.isAuthenticated) {
    try {
      await authStore.fetchBalance()
    } catch (error) {
      console.error('Failed to fetch balance:', error)
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const handleLogout = async () => {
  await authStore.logout()
  mobileMenuOpen.value = false
  router.push('/')
}
</script>

<style scoped>
.nav-link {
  @apply px-4 py-2 text-text-secondary hover:text-text-primary hover:bg-dark-hover rounded-lg transition-all duration-300;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #f97316, #fb923c);
  transform: translateX(-50%);
  transition: width 0.3s ease;
}

.nav-link:hover::after {
  width: 80%;
}

.nav-link.router-link-active {
  @apply text-primary bg-dark-elevated;
}

.nav-link.router-link-active::after {
  width: 80%;
}

.nav-link-mobile {
  @apply px-4 py-3 text-text-secondary hover:text-text-primary hover:bg-dark-hover rounded-lg transition-colors block;
}

.nav-link-mobile.router-link-active {
  @apply text-primary bg-dark-elevated;
}
</style>
