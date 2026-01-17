<template>
  <div class="navbar-wrapper">
    <nav class="navbar navbar-glass sticky top-0 z-50 shadow-lg">
      <div class="container-custom">
        <div class="flex items-center justify-between h-16">
          <!-- Left: Logo -->
          <div class="flex items-center gap-4">
            <!-- Mobile Menu Button -->
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="lg:hidden p-2 rounded-lg hover:bg-base-200 transition-colors"
            >
              <Menu class="w-6 h-6" />
            </button>

            <!-- Logo -->
            <router-link to="/" class="flex items-center gap-2 group">
              <img
                src="/logo-navbar.png"
                alt="AGTR Merkezi"
                class="h-10 w-auto group-hover:scale-105 transition-transform"
              />
            </router-link>
          </div>

          <!-- Center: Navigation Links (Desktop) -->
          <div class="hidden lg:flex items-center gap-1">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-link px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
              :class="isActive(item.path) ? 'nav-link-active' : ''"
            >
              <component :is="item.icon" class="w-4 h-4" />
              {{ item.label }}
            </router-link>
          </div>

          <!-- Right: Actions -->
          <div class="flex items-center gap-2">
            <!-- Wallet Display (when logged in) -->
            <div v-if="user" class="hidden md:flex items-center gap-3 mr-2">
              <!-- TL Balance -->
              <div class="wallet-item flex items-center gap-1.5 px-3 py-1.5 rounded-lg">
                <span class="text-green-500 font-bold text-sm">TL</span>
                <span class="font-mono font-semibold text-sm">{{ formatCurrency(user.balance || 0) }}</span>
              </div>

              <!-- Armor Balance -->
              <div class="wallet-item wallet-armor flex items-center gap-1.5 px-3 py-1.5 rounded-lg">
                <ShieldCheck class="w-4 h-4 text-orange-500" />
                <span class="font-mono font-semibold text-sm text-orange-500">{{ formatNumber(user.balance_coin || 0) }}</span>
                <span class="text-xs opacity-60">Armor</span>
              </div>
            </div>

            <!-- Search Button (Desktop) -->
            <button
              @click="openCommandPalette"
              class="search-btn hidden lg:flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-sm"
            >
              <Search class="w-4 h-4 opacity-60" />
              <span class="opacity-60">Ara...</span>
              <kbd class="search-kbd hidden xl:inline px-1.5 py-0.5 text-xs rounded opacity-60">Ctrl+K</kbd>
            </button>

            <!-- Theme Toggle -->
            <button
              @click="toggleTheme"
              class="p-2 rounded-lg hover:bg-base-200 transition-colors"
              :title="darkMode ? 'Light Mode' : 'Dark Mode'"
            >
              <Sun v-if="darkMode" class="w-5 h-5 text-yellow-500" />
              <Moon v-else class="w-5 h-5 opacity-40" />
            </button>

            <!-- Notifications -->
            <div class="relative" v-if="user">
              <button
                @click="notificationsOpen = !notificationsOpen"
                class="p-2 rounded-lg hover:bg-base-200 transition-colors relative"
              >
                <Bell class="w-5 h-5" />
                <span
                  v-if="unreadCount > 0"
                  class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"
                ></span>
              </button>

              <!-- Notifications Dropdown -->
              <Transition name="dropdown">
                <div
                  v-if="notificationsOpen"
                  class="absolute right-0 mt-2 w-80 dropdown-glass p-4"
                >
                  <div class="flex items-center justify-between mb-3">
                    <h3 class="font-bold">Bildirimler</h3>
                    <button class="text-xs text-primary hover:underline">Tumunu Okundu</button>
                  </div>
                  <div class="space-y-2 max-h-64 overflow-y-auto">
                    <div
                      v-for="notification in notifications"
                      :key="notification.id"
                      class="p-3 rounded-lg bg-base-200 hover:bg-base-300 transition-colors cursor-pointer"
                    >
                      <p class="font-medium text-sm">{{ notification.title }}</p>
                      <p class="text-xs opacity-60 mt-1">{{ notification.message }}</p>
                    </div>
                    <div v-if="notifications.length === 0" class="text-center py-8 opacity-60">
                      <Bell class="w-8 h-8 mx-auto mb-2" />
                      <p class="text-sm">Bildirim yok</p>
                    </div>
                  </div>
                </div>
              </Transition>
            </div>

            <!-- User Menu -->
            <div v-if="user" class="relative">
              <button
                @click="userMenuOpen = !userMenuOpen"
                class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-base-200 transition-colors"
              >
                <!-- Avatar - Steam veya varsayilan -->
                <div class="w-8 h-8 rounded-lg overflow-hidden">
                  <img
                    v-if="user.avatar"
                    :src="user.avatar"
                    :alt="user.username"
                    class="w-full h-full object-cover"
                  />
                  <div
                    v-else
                    class="w-full h-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center"
                  >
                    <span class="text-white font-bold text-sm">{{ getInitials(user.username) }}</span>
                  </div>
                </div>
                <ChevronDown class="w-4 h-4 hidden sm:block" />
              </button>

              <!-- User Dropdown -->
              <Transition name="dropdown">
                <div
                  v-if="userMenuOpen"
                  class="absolute right-0 mt-2 w-72 dropdown-glass p-2"
                >
                  <!-- User Info -->
                  <div class="flex items-center gap-3 px-3 py-3 border-b border-base-300 mb-2">
                    <div class="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0">
                      <img
                        v-if="user.avatar"
                        :src="user.avatar"
                        :alt="user.username"
                        class="w-full h-full object-cover"
                      />
                      <div
                        v-else
                        class="w-full h-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center"
                      >
                        <span class="text-white font-bold">{{ getInitials(user.username) }}</span>
                      </div>
                    </div>
                    <div class="min-w-0 flex-1">
                      <p class="font-bold truncate">{{ user.display_name || user.username }}</p>
                      <p class="text-xs opacity-60 truncate">@{{ user.username }}</p>
                    </div>
                  </div>

                  <!-- Wallet Summary in Dropdown -->
                  <div class="px-3 py-2 mb-2 space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-sm opacity-60">TL Bakiye</span>
                      <span class="font-mono font-bold text-green-500">{{ formatCurrency(user.balance || 0) }} TL</span>
                    </div>
                    <div class="flex items-center justify-between">
                      <span class="text-sm opacity-60 flex items-center gap-1">
                        <ShieldCheck class="w-4 h-4 text-orange-500" /> Armor
                      </span>
                      <span class="font-mono font-bold text-orange-500">{{ formatNumber(user.balance_coin || 0) }}</span>
                    </div>
                    <router-link
                      to="/shop"
                      class="block w-full mt-2 text-center py-2 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 text-white text-sm font-semibold hover:from-orange-600 hover:to-orange-700 transition-all"
                      @click="userMenuOpen = false"
                    >
                      Armor Yukle
                    </router-link>
                  </div>

                  <div class="border-t border-base-300 pt-2">
                    <!-- Menu Items -->
                    <router-link
                      v-for="item in userMenuItems"
                      :key="item.path"
                      :to="item.path"
                      class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-base-200 transition-colors"
                      @click="userMenuOpen = false"
                    >
                      <component :is="item.icon" class="w-4 h-4" />
                      <span class="text-sm">{{ item.label }}</span>
                    </router-link>
                  </div>

                  <div class="border-t border-base-300 mt-2 pt-2">
                    <button
                      @click="handleLogout"
                      class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-500/10 text-red-500 w-full transition-colors"
                    >
                      <LogOut class="w-4 h-4" />
                      <span class="text-sm">Cikis Yap</span>
                    </button>
                  </div>
                </div>
              </Transition>
            </div>

            <!-- Login Button -->
            <router-link v-else to="/login">
              <button class="btn-gaming text-sm px-4 py-2">
                <LogIn class="w-4 h-4" />
                <span class="hidden sm:inline">Giris Yap</span>
              </button>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Mobile Menu -->
      <Transition name="slide-down">
        <div v-if="mobileMenuOpen" class="lg:hidden border-t border-base-300">
          <div class="container-custom py-4">
            <!-- Mobile Wallet -->
            <div v-if="user" class="flex items-center gap-3 mb-4 pb-4 border-b border-base-300">
              <div class="wallet-item flex items-center gap-1.5 px-3 py-2 rounded-lg flex-1 justify-center">
                <span class="text-green-500 font-bold">TL</span>
                <span class="font-mono font-semibold">{{ formatCurrency(user.balance || 0) }}</span>
              </div>
              <div class="wallet-item wallet-armor flex items-center gap-1.5 px-3 py-2 rounded-lg flex-1 justify-center">
                <ShieldCheck class="w-4 h-4 text-orange-500" />
                <span class="font-mono font-semibold text-orange-500">{{ formatNumber(user.balance_coin || 0) }}</span>
                <span class="text-xs opacity-60">Armor</span>
              </div>
            </div>

            <div class="flex flex-col gap-1">
              <router-link
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-base-200 transition-colors"
                :class="isActive(item.path) ? 'bg-orange-500/10 text-orange-500' : ''"
                @click="mobileMenuOpen = false"
              >
                <component :is="item.icon" class="w-5 h-5" />
                <span class="font-medium">{{ item.label }}</span>
              </router-link>
            </div>
          </div>
        </div>
      </Transition>
    </nav>

    <!-- Click outside to close dropdowns -->
    <div
      v-if="notificationsOpen || userMenuOpen"
      class="fixed inset-0 z-40"
      @click="notificationsOpen = false; userMenuOpen = false"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import {
  Menu,
  Search,
  Bell,
  Sun,
  Moon,
  User,
  Settings,
  CreditCard,
  Shield,
  ShieldCheck,
  LogOut,
  LogIn,
  LayoutDashboard,
  Server,
  MessageSquare,
  Trophy,
  Home,
  ShoppingBag,
  ChevronDown,
  Dice5,
  Wallet
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// State
const mobileMenuOpen = ref(false)
const notificationsOpen = ref(false)
const userMenuOpen = ref(false)

// Computed
const user = computed(() => authStore.user)
const darkMode = computed(() => themeStore.currentTheme === 'dark')
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

// Navigation items
const navItems = [
  { path: '/', label: 'Ana Sayfa', icon: Home },
  { path: '/servers', label: 'Sunucular', icon: Server },
  { path: '/leaderboard', label: 'Siralamalar', icon: Trophy },
  { path: '/forum', label: 'Forum', icon: MessageSquare },
  { path: '/jackpot', label: 'Jackpot', icon: Dice5 },
  { path: '/shop', label: 'Premium', icon: ShoppingBag }
]

// User menu items
const userMenuItems = computed(() => {
  const items = [
    { path: '/profile', label: 'Profil', icon: User },
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/servers', label: 'Sunucularim', icon: Server }
  ]

  if (['admin', 'superadmin'].includes(user.value?.role)) {
    items.push({ path: '/admin', label: 'Admin Panel', icon: Shield })
  }

  return items
})

// Notifications (mock data)
const notifications = ref([
  { id: 1, title: 'Sunucu Basladi', message: 'AGTR Public #1 basariyla basladi.', read: false },
  { id: 2, title: 'Yeni Guncelleme', message: 'v8.0 yayinlandi!', read: false }
])

// Methods
const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const getInitials = (name) => {
  if (!name) return 'U'
  return name.substring(0, 2).toUpperCase()
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('tr-TR').format(value)
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const openCommandPalette = () => {
  window.dispatchEvent(new CustomEvent('open-command-palette'))
}

const handleLogout = async () => {
  userMenuOpen.value = false
  await authStore.logout()
  router.push('/login')
}

// Close dropdowns on escape key
const handleEscape = (e) => {
  if (e.key === 'Escape') {
    notificationsOpen.value = false
    userMenuOpen.value = false
    mobileMenuOpen.value = false
  }
}

// Keyboard shortcut for search
const handleKeydown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    openCommandPalette()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEscape)
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscape)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* Navigation Link Styles */
.nav-link {
  color: var(--text-secondary, #94a3b8);
}

.nav-link:hover {
  color: var(--text-primary, #f8fafc);
  background-color: var(--bg-secondary, rgba(30, 41, 59, 0.5));
}

.nav-link-active {
  color: var(--primary-color, #f97316);
  background-color: rgba(249, 115, 22, 0.1);
}

/* Search Button Styles */
.search-btn {
  background-color: var(--bg-secondary, #1e293b);
  border: 1px solid var(--border-color, #475569);
  color: var(--text-secondary, #94a3b8);
}

.search-btn:hover {
  background-color: var(--bg-tertiary, #334155);
  border-color: var(--text-muted, #64748b);
}

.search-kbd {
  background-color: var(--bg-tertiary, #334155);
  color: var(--text-muted, #64748b);
}

/* Wallet Styles */
.wallet-item {
  background-color: var(--bg-secondary, #1e293b);
  border: 1px solid var(--border-color, #475569);
}

.wallet-armor {
  border-color: rgba(249, 115, 22, 0.3);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(234, 88, 12, 0.05) 100%);
}

/* Dropdown Transitions */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Slide Down Transition */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
