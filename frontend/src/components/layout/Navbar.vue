<template>
  <nav class="sticky top-0 z-50 border-b" :class="isDark ? 'bg-zinc-900/95 border-zinc-800' : 'bg-white/95 border-zinc-200'" style="backdrop-filter: blur(12px);">
    <div class="container-main">
      <div class="flex items-center justify-between h-16">
        <!-- Left: Logo & Nav -->
        <div class="flex items-center gap-6">
          <!-- Mobile Menu -->
          <n-button quaternary circle class="lg:hidden" @click="mobileMenuOpen = !mobileMenuOpen">
            <template #icon>
              <n-icon><Menu /></n-icon>
            </template>
          </n-button>

          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-2">
            <img src="/logo-navbar.png" alt="AGTR Merkezi" class="h-9 w-auto" />
          </router-link>

          <!-- Desktop Nav -->
          <div class="hidden lg:flex items-center gap-1">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-link"
              :class="{ 'nav-link-active': isActive(item.path) }"
            >
              <n-icon :component="item.icon" size="16" />
              {{ item.label }}
            </router-link>
          </div>
        </div>

        <!-- Right: Actions -->
        <div class="flex items-center gap-2">
          <!-- Wallet (logged in) -->
          <div v-if="user" class="hidden md:flex items-center gap-2">
            <n-tag type="success" :bordered="false">
              {{ formatCurrency(user.balance || 0) }} TL
            </n-tag>
            <n-tag type="warning" :bordered="false">
              <template #icon>
                <n-icon><ShieldCheck /></n-icon>
              </template>
              {{ formatNumber(user.balance_coin || 0) }} Armor
            </n-tag>
          </div>

          <!-- Theme Toggle -->
          <n-button quaternary circle @click="toggleTheme">
            <template #icon>
              <n-icon :component="isDark ? Sun : Moon" :color="isDark ? '#facc15' : undefined" />
            </template>
          </n-button>

          <!-- Notifications -->
          <n-popover v-if="user" trigger="click" placement="bottom-end" :show-arrow="false">
            <template #trigger>
              <n-badge :value="unreadCount" :max="9" :show="unreadCount > 0">
                <n-button quaternary circle>
                  <template #icon>
                    <n-icon><Bell /></n-icon>
                  </template>
                </n-button>
              </n-badge>
            </template>
            <div class="w-72">
              <div class="flex items-center justify-between mb-3">
                <span class="font-semibold">Bildirimler</span>
                <n-button text type="primary" size="small">Tumu okundu</n-button>
              </div>
              <n-list v-if="notifications.length > 0" :show-divider="false">
                <n-list-item v-for="n in notifications" :key="n.id">
                  <div class="text-sm font-medium">{{ n.title }}</div>
                  <div class="text-xs opacity-60">{{ n.message }}</div>
                </n-list-item>
              </n-list>
              <n-empty v-else description="Bildirim yok" size="small" />
            </div>
          </n-popover>

          <!-- User Menu -->
          <n-dropdown v-if="user" trigger="click" :options="userMenuOptions" @select="handleUserMenuSelect">
            <n-button quaternary class="!px-2">
              <div class="flex items-center gap-2">
                <n-avatar
                  :size="32"
                  :src="user.avatar"
                  :fallback-src="undefined"
                  round
                >
                  {{ getInitials(user.username) }}
                </n-avatar>
                <span class="hidden sm:inline font-medium">{{ user.username }}</span>
                <n-icon><ChevronDown /></n-icon>
              </div>
            </n-button>
          </n-dropdown>

          <!-- Login Button -->
          <router-link v-else to="/login">
            <n-button type="primary">
              <template #icon>
                <n-icon><LogIn /></n-icon>
              </template>
              <span class="hidden sm:inline">Giris Yap</span>
            </n-button>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <n-collapse-transition :show="mobileMenuOpen">
      <div class="lg:hidden border-t" :class="isDark ? 'border-zinc-800' : 'border-zinc-200'">
        <div class="container-main py-4">
          <!-- Mobile Wallet -->
          <div v-if="user" class="flex gap-2 mb-4 pb-4 border-b" :class="isDark ? 'border-zinc-800' : 'border-zinc-200'">
            <n-tag type="success" :bordered="false" class="flex-1 justify-center">
              {{ formatCurrency(user.balance || 0) }} TL
            </n-tag>
            <n-tag type="warning" :bordered="false" class="flex-1 justify-center">
              {{ formatNumber(user.balance_coin || 0) }} Armor
            </n-tag>
          </div>

          <div class="flex flex-col gap-1">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-link-mobile"
              :class="{ 'nav-link-mobile-active': isActive(item.path) }"
              @click="mobileMenuOpen = false"
            >
              <n-icon :component="item.icon" size="20" />
              {{ item.label }}
            </router-link>
          </div>
        </div>
      </div>
    </n-collapse-transition>
  </nav>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { NIcon } from 'naive-ui'
import {
  Menu,
  Bell,
  Sun,
  Moon,
  User,
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
  Dice5
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const mobileMenuOpen = ref(false)

const user = computed(() => authStore.user)
const isDark = computed(() => themeStore.isDark)
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

const navItems = [
  { path: '/', label: 'Ana Sayfa', icon: Home },
  { path: '/servers', label: 'Sunucular', icon: Server },
  { path: '/leaderboard', label: 'Siralamalar', icon: Trophy },
  { path: '/forum', label: 'Forum', icon: MessageSquare },
  { path: '/jackpot', label: 'Jackpot', icon: Dice5 },
  { path: '/shop', label: 'Premium', icon: ShoppingBag }
]

const notifications = ref([
  { id: 1, title: 'Sunucu Basladi', message: 'AGTR Public #1 basariyla basladi.', read: false },
  { id: 2, title: 'Yeni Guncelleme', message: 'v8.0 yayinlandi!', read: false }
])

const userMenuOptions = computed(() => {
  const items = [
    {
      label: user.value?.username || 'Kullanici',
      key: 'header',
      disabled: true
    },
    { type: 'divider', key: 'd1' },
    {
      label: 'Profil',
      key: 'profile',
      icon: () => h(NIcon, null, { default: () => h(User) })
    },
    {
      label: 'Dashboard',
      key: 'dashboard',
      icon: () => h(NIcon, null, { default: () => h(LayoutDashboard) })
    },
    {
      label: 'Sunucularim',
      key: 'servers',
      icon: () => h(NIcon, null, { default: () => h(Server) })
    }
  ]

  if (['admin', 'superadmin'].includes(user.value?.role)) {
    items.push({
      label: 'Admin Panel',
      key: 'admin',
      icon: () => h(NIcon, null, { default: () => h(Shield) })
    })
  }

  items.push(
    { type: 'divider', key: 'd2' },
    {
      label: 'Cikis Yap',
      key: 'logout',
      icon: () => h(NIcon, null, { default: () => h(LogOut) })
    }
  )

  return items
})

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

const handleUserMenuSelect = async (key) => {
  if (key === 'logout') {
    await authStore.logout()
    router.push('/login')
  } else if (key === 'profile') {
    router.push('/profile')
  } else if (key === 'dashboard') {
    router.push('/dashboard')
  } else if (key === 'servers') {
    router.push('/servers')
  } else if (key === 'admin') {
    router.push('/admin')
  }
}
</script>

<style scoped>
.nav-link {
  @apply flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors;
  color: var(--n-text-color-3, #94a3b8);
}

.nav-link:hover {
  color: var(--n-text-color, #f8fafc);
  background-color: var(--n-hover-color, rgba(255, 255, 255, 0.05));
}

.nav-link-active {
  color: #f97316 !important;
  background-color: rgba(249, 115, 22, 0.1) !important;
}

.nav-link-mobile {
  @apply flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors;
}

.nav-link-mobile:hover {
  background-color: var(--n-hover-color, rgba(255, 255, 255, 0.05));
}

.nav-link-mobile-active {
  color: #f97316 !important;
  background-color: rgba(249, 115, 22, 0.1) !important;
}
</style>
