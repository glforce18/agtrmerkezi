<template>
  <nav
    ref="navbarRef"
    class="navbar-glass"
    :class="[
      isDark ? 'navbar-dark' : 'navbar-light',
      { 'navbar-scrolled': isScrolled, 'navbar-shrink': isScrolled, 'navbar-menu-open': mobileMenuOpen }
    ]"
  >
    <div class="container-main">
      <div class="navbar-content" :class="{ 'navbar-content-shrink': isScrolled }">
        <!-- Left: Logo & Nav -->
        <div class="navbar-left flex items-center gap-3">
          <!-- Animated Logo -->
          <router-link to="/" class="logo-wrapper group">
            <div class="logo-container">
              <img
                :src="logoUrl"
                :style="logoStyle"
                alt="AGTR Merkezi"
                class="logo-img"
                @error="handleLogoError"
              />
              <div class="logo-glow"></div>
              <div class="logo-pulse"></div>
            </div>
            <div v-if="showLogoText" class="logo-text">
              <span class="logo-main">{{ logoText }}</span>
              <span class="logo-sub">{{ logoSubtitle }}</span>
            </div>
          </router-link>

          <!-- Desktop Navigation -->
          <div class="hidden lg:flex items-center gap-1">
            <template v-for="item in navItems" :key="item.path">
              <!-- Dropdown Menu -->
              <n-popover
                v-if="item.dropdown"
                trigger="hover"
                placement="bottom-start"
                :show-arrow="false"
                content-class="nav-dropdown-popover"
              >
                <template #trigger>
                  <button
                    class="nav-link nav-dropdown-trigger"
                    :class="{ 'nav-link-active': isActive(item.path) || item.children?.some(c => isActive(c.path)) }"
                  >
                    <n-icon :component="item.icon" size="16" />
                    <span class="nav-link-text">{{ item.label }}</span>
                    <n-icon :component="ChevronDown" size="14" class="dropdown-chevron" />
                  </button>
                </template>
                <div class="nav-dropdown-menu">
                  <router-link
                    v-for="child in item.children"
                    :key="child.path"
                    :to="child.path"
                    class="nav-dropdown-item"
                    :class="{ 'nav-dropdown-item-active': isActive(child.path) }"
                  >
                    <n-icon :component="child.icon" size="16" />
                    <span>{{ child.label }}</span>
                  </router-link>
                </div>
              </n-popover>

              <!-- Regular Link -->
              <router-link
                v-else
                :to="item.path"
                class="nav-link"
                :class="{
                  'nav-link-active': isActive(item.path),
                  'nav-link-highlight': item.highlight
                }"
                :title="item.label"
              >
                <n-icon :component="item.icon" size="16" />
                <span class="nav-link-text">{{ item.label }}</span>
                <span class="nav-link-underline"></span>
                <span v-if="isActive(item.path)" class="nav-link-active-bg"></span>
              </router-link>
            </template>
          </div>
        </div>

        <!-- Right: Actions -->
        <div class="navbar-actions flex items-center gap-2">
          <!-- Search Button (expandable) - hidden on small screens -->
          <div class="search-container hidden md:block" :class="{ 'search-expanded': searchExpanded }">
            <button
              v-if="!searchExpanded"
              class="search-btn"
              @click="expandSearch"
            >
              <n-icon :component="Search" size="18" />
            </button>
            <div v-else class="search-input-wrapper">
              <n-icon :component="Search" size="16" class="search-icon" />
              <input
                ref="searchInput"
                v-model="searchQuery"
                type="text"
                placeholder="Ara..."
                class="search-input"
                @blur="collapseSearch"
                @keydown.escape="collapseSearch"
              />
              <button class="search-close" @click="collapseSearch">
                <n-icon :component="X" size="14" />
              </button>
            </div>
          </div>

          <!-- Level & XP Display (logged in) - only on very large screens -->
          <div v-if="user" class="hidden 2xl:flex items-center gap-2">
            <!-- Level Badge -->
            <div class="level-badge" @click="navigateTo('/profile')">
              <div class="level-icon">
                <span class="level-number">{{ userLevel }}</span>
              </div>
              <div class="level-info">
                <span class="level-label">Seviye</span>
                <div class="xp-bar">
                  <div class="xp-fill" :style="{ width: xpProgress + '%' }"></div>
                </div>
              </div>
            </div>

            <!-- Streak Badge -->
            <div
              class="streak-badge"
              :class="'streak-' + streakTier"
              :title="`${streak} günlük seri! Sonraki hedef: ${nextMilestone.label}`"
            >
              <n-icon :component="Flame" size="16" class="streak-icon" />
              <span class="streak-count">{{ streak }}</span>
            </div>
          </div>

          <!-- Wallet Display (logged in) - only on large screens -->
          <div v-if="user" class="hidden xl:flex items-center gap-1">
            <div class="wallet-badge wallet-badge-tl" @click="openWallet('tl')">
              <span class="wallet-icon">₺</span>
              <span class="wallet-amount" :key="user.balance">
                <AnimatedNumber :value="user.balance || 0" :decimals="2" /> TL
              </span>
            </div>
            <div class="wallet-badge wallet-badge-armor" @click="openWallet('armor')">
              <n-icon :component="ShieldCheck" size="14" class="wallet-icon-svg" />
              <span class="wallet-amount" :key="user.balance_coin">
                <AnimatedNumber :value="user.balance_coin || 0" :decimals="0" /> Armor
              </span>
            </div>
          </div>

          <!-- Theme Toggle -->
          <button class="theme-toggle" @click="toggleTheme">
            <div class="theme-toggle-track">
              <div class="theme-toggle-thumb" :class="{ 'theme-toggle-thumb-dark': isDark }">
                <n-icon
                  :component="isDark ? Moon : Sun"
                  size="12"
                  class="theme-icon"
                  :class="{ 'theme-icon-rotate': themeAnimating }"
                />
              </div>
            </div>
          </button>

          <!-- Notifications -->
          <div v-if="user" class="relative">
            <n-popover
              trigger="click"
              placement="bottom-end"
              :show-arrow="false"
              content-class="notification-popover"
              @update:show="handleNotificationPopover"
            >
              <template #trigger>
                <button
                  class="notification-btn"
                  :class="{ 'notification-btn-bounce': hasNewNotification }"
                >
                  <n-icon :component="Bell" size="20" />
                  <span v-if="unreadCount > 0" class="notification-badge">
                    {{ unreadCount > 9 ? '9+' : unreadCount }}
                  </span>
                </button>
              </template>
              <div class="notification-dropdown">
                <div class="notification-header">
                  <span class="notification-title">Bildirimler</span>
                  <button
                    v-if="unreadCount > 0"
                    class="notification-mark-read"
                    @click="markAllAsRead"
                  >
                    Tümü okundu
                  </button>
                </div>
                <div class="notification-list" v-if="notifications.length > 0">
                  <div
                    v-for="(n, index) in notifications"
                    :key="n.id"
                    class="notification-item"
                    :class="{ 'notification-item-unread': !n.read }"
                    :style="{ animationDelay: `${index * 50}ms` }"
                    @click="handleNotificationClick(n)"
                  >
                    <div class="notification-item-indicator" v-if="!n.read"></div>
                    <div class="notification-item-content">
                      <div class="notification-item-title">{{ n.title }}</div>
                      <div class="notification-item-message">{{ n.message }}</div>
                      <div class="notification-item-time">{{ n.time || '2 dakika önce' }}</div>
                    </div>
                  </div>
                </div>
                <div v-else class="notification-empty">
                  <n-icon :component="BellOff" size="32" class="opacity-40" />
                  <span>Bildirim yok</span>
                </div>
                <div class="notification-footer">
                  <router-link to="/notifications" class="notification-view-all">
                    Tüm bildirimleri gör
                  </router-link>
                </div>
              </div>
            </n-popover>
          </div>

          <!-- User Menu -->
          <div v-if="user" class="relative">
            <n-popover
              trigger="click"
              placement="bottom-end"
              :show-arrow="false"
              content-class="user-menu-popover"
            >
              <template #trigger>
                <button class="user-menu-trigger">
                  <div class="user-avatar-wrapper">
                    <n-avatar
                      :size="34"
                      :src="user.avatar"
                      :fallback-src="undefined"
                      round
                      class="user-avatar"
                    >
                      {{ getInitials(user.username) }}
                    </n-avatar>
                    <span class="user-status-ring" :class="{ 'user-status-online': true }"></span>
                  </div>
                  <span class="hidden lg:inline user-name">{{ user.username }}</span>
                  <n-icon :component="ChevronDown" size="16" class="user-chevron hidden lg:block" />
                </button>
              </template>
              <div class="user-dropdown">
                <div class="user-dropdown-header">
                  <div class="user-dropdown-avatar-wrapper">
                    <n-avatar :size="48" :src="user.avatar" round>
                      {{ getInitials(user.username) }}
                    </n-avatar>
                    <span class="user-status-ring user-status-online large"></span>
                  </div>
                  <div class="user-dropdown-info">
                    <span class="user-dropdown-name">{{ user.username }}</span>
                    <span class="user-dropdown-role">{{ getRoleLabel(user.role) }}</span>
                  </div>
                </div>
                <div class="user-dropdown-divider"></div>
                <div class="user-dropdown-menu">
                  <button class="user-dropdown-item" @click="navigateTo('/profile')">
                    <n-icon :component="User" size="18" />
                    <span>Profil</span>
                  </button>
                  <button class="user-dropdown-item" @click="navigateTo('/dashboard')">
                    <n-icon :component="LayoutDashboard" size="18" />
                    <span>Dashboard</span>
                  </button>
                  <button class="user-dropdown-item" @click="navigateTo('/my-servers')">
                    <n-icon :component="Server" size="18" />
                    <span>Sunucularım</span>
                  </button>
                  <button
                    v-if="user.role === 'superadmin'"
                    class="user-dropdown-item user-dropdown-item-admin"
                    @click="navigateTo('/admin')"
                  >
                    <n-icon :component="Shield" size="18" />
                    <span>Admin Panel</span>
                  </button>
                </div>
                <div class="user-dropdown-divider"></div>
                <button class="user-dropdown-item user-dropdown-item-logout" @click="handleLogout">
                  <n-icon :component="LogOut" size="18" />
                  <span>Çıkış Yap</span>
                </button>
              </div>
            </n-popover>
          </div>

          <!-- Login Button -->
          <router-link v-else to="/login" class="login-btn">
            <n-icon :component="LogIn" size="18" />
            <span class="hidden sm:inline">Giriş Yap</span>
          </router-link>

          <!-- Mobile Menu Button (Right Side) -->
          <button
            class="mobile-menu-btn lg:hidden"
            :class="{ 'mobile-menu-btn-active': mobileMenuOpen }"
            @click="toggleMobileMenu"
          >
            <span class="hamburger-line hamburger-line-1"></span>
            <span class="hamburger-line hamburger-line-2"></span>
            <span class="hamburger-line hamburger-line-3"></span>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Menu Overlay -->
    <Transition name="mobile-overlay">
      <div
        v-if="mobileMenuOpen"
        class="mobile-overlay lg:hidden"
        @click="mobileMenuOpen = false"
      ></div>
    </Transition>

    <!-- Mobile Menu Slide-in -->
    <Transition name="mobile-menu">
      <div
        v-if="mobileMenuOpen"
        class="mobile-menu lg:hidden"
        :class="isDark ? 'mobile-menu-dark' : 'mobile-menu-light'"
      >
        <div class="mobile-menu-header">
          <router-link to="/" class="mobile-logo" @click="mobileMenuOpen = false">
            <img :src="logoUrl" alt="AGTR" class="mobile-logo-img" />
            <span class="mobile-logo-text">{{ logoText }}</span>
          </router-link>
          <button class="mobile-close-btn" @click="mobileMenuOpen = false">
            <n-icon :component="X" size="24" />
          </button>
        </div>

        <!-- Mobile Wallet -->
        <div v-if="user" class="mobile-wallet">
          <div class="mobile-wallet-item" @click="openWallet('tl'); mobileMenuOpen = false">
            <span class="mobile-wallet-label">Bakiye</span>
            <span class="mobile-wallet-value">{{ formatCurrency(user.balance || 0) }} TL</span>
          </div>
          <div class="mobile-wallet-item" @click="openWallet('armor'); mobileMenuOpen = false">
            <span class="mobile-wallet-label">Armor</span>
            <span class="mobile-wallet-value">{{ formatNumber(user.balance_coin || 0) }}</span>
          </div>
        </div>

        <!-- Mobile Navigation -->
        <nav class="mobile-nav">
          <template v-for="(item, index) in navItems" :key="item.path">
            <!-- Dropdown ile olan item -->
            <template v-if="item.dropdown">
              <div class="mobile-nav-group">
                <div class="mobile-nav-group-title">
                  <n-icon :component="item.icon" size="18" />
                  <span>{{ item.label }}</span>
                </div>
                <router-link
                  v-for="child in item.children"
                  :key="child.path"
                  :to="child.path"
                  class="mobile-nav-item mobile-nav-child"
                  :class="{ 'mobile-nav-item-active': isActive(child.path) }"
                  @click="mobileMenuOpen = false"
                >
                  <n-icon :component="child.icon" size="20" />
                  <span>{{ child.label }}</span>
                  <n-icon :component="ChevronRight" size="16" class="mobile-nav-arrow" />
                </router-link>
              </div>
            </template>
            <!-- Normal link -->
            <router-link
              v-else
              :to="item.path"
              class="mobile-nav-item"
              :class="{ 'mobile-nav-item-active': isActive(item.path) }"
              :style="{ animationDelay: `${index * 50}ms` }"
              @click="mobileMenuOpen = false"
            >
              <n-icon :component="item.icon" size="22" />
              <span>{{ item.label }}</span>
              <n-icon :component="ChevronRight" size="16" class="mobile-nav-arrow" />
            </router-link>
          </template>
        </nav>

        <!-- Mobile User Section -->
        <div v-if="user" class="mobile-user-section">
          <div class="mobile-user-info">
            <n-avatar :size="40" :src="user.avatar" round>
              {{ getInitials(user.username) }}
            </n-avatar>
            <div class="mobile-user-details">
              <span class="mobile-user-name">{{ user.username }}</span>
              <span class="mobile-user-role">{{ getRoleLabel(user.role) }}</span>
            </div>
          </div>
          <button class="mobile-logout-btn" @click="handleLogout">
            <n-icon :component="LogOut" size="20" />
            <span>Çıkış Yap</span>
          </button>
        </div>

        <!-- Mobile Login -->
        <div v-else class="mobile-login">
          <router-link to="/login" class="mobile-login-btn" @click="mobileMenuOpen = false">
            <n-icon :component="LogIn" size="20" />
            <span>Giriş Yap</span>
          </router-link>
        </div>
      </div>
    </Transition>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useSettingsStore } from '@/stores/settings'
import { useStreak } from '@/composables/useStreak'
import { NIcon, NAvatar, NPopover } from 'naive-ui'
import {
  Menu,
  Bell,
  BellOff,
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
  ChevronRight,
  Dice5,
  Search,
  X,
  Globe,
  Flame
} from 'lucide-vue-next'

// Animated Number Component (inline)
const AnimatedNumber = {
  props: {
    value: { type: Number, default: 0 },
    decimals: { type: Number, default: 0 }
  },
  setup(props) {
    const displayValue = ref(props.value)

    watch(() => props.value, (newVal, oldVal) => {
      const diff = newVal - oldVal
      const steps = 20
      const stepValue = diff / steps
      let current = oldVal
      let step = 0

      const animate = () => {
        step++
        current += stepValue
        displayValue.value = step === steps ? newVal : current
        if (step < steps) requestAnimationFrame(animate)
      }
      animate()
    })

    return () => {
      const formatted = new Intl.NumberFormat('tr-TR', {
        minimumFractionDigits: props.decimals,
        maximumFractionDigits: props.decimals
      }).format(displayValue.value)
      return formatted
    }
  }
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const settingsStore = useSettingsStore()
const { streak, streakTier, nextMilestone } = useStreak()

// Refs
const navbarRef = ref(null)
const searchInput = ref(null)
const mobileMenuOpen = ref(false)
const searchExpanded = ref(false)
const searchQuery = ref('')
const isScrolled = ref(false)
const themeAnimating = ref(false)
const hasNewNotification = ref(false)
const logoErrorCount = ref(0) // Guard for infinite logo error loops

// Computed
const user = computed(() => authStore.user)
const isDark = computed(() => themeStore.isDark)
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

// Level & XP calculations based on reputation
const userLevel = computed(() => {
  const rep = user.value?.reputation || 0
  return Math.floor(rep / 100) + 1
})

const xpProgress = computed(() => {
  const rep = user.value?.reputation || 0
  return (rep % 100)
})

// Logo settings
const logoUrl = computed(() => {
  const settings = settingsStore.settings
  if (isDark.value && settings.logo_dark_url) {
    return settings.logo_dark_url
  }
  return settings.logo_url || '/logo-navbar.png'
})

const logoStyle = computed(() => {
  const settings = settingsStore.settings
  return {
    width: settings.logo_width === 'auto' ? 'auto' : `${settings.logo_width}px`,
    height: settings.logo_height === 'auto' ? 'auto' : `${settings.logo_height}px`,
    maxHeight: '40px',
    objectFit: 'contain'
  }
})

const showLogoText = computed(() => settingsStore.settings.show_logo_text)
const logoText = computed(() => settingsStore.settings.logo_text || 'AGTR')
const logoSubtitle = computed(() => settingsStore.settings.logo_subtitle || 'MERKEZİ')

// Navigation items - simplified with Forum highlighted
const navItems = [
  { path: '/', label: 'Ana Sayfa', icon: Home },
  { path: '/servers', label: 'Sunucular', icon: Server },
  { path: '/forum', label: 'Forum', icon: MessageSquare, highlight: true },
  {
    path: '/community-servers',
    label: 'Topluluk',
    icon: Globe,
    dropdown: true,
    children: [
      { path: '/community-servers', label: 'Sunucu Listesi', icon: Globe },
      { path: '/leaderboard', label: 'Sıralamalar', icon: Trophy }
    ]
  },
  { path: '/jackpot', label: 'Jackpot', icon: Dice5 },
  { path: '/shop', label: 'Sunucu Kirala', icon: ShoppingBag }
]

// Notifications - API'den yüklenir
const notifications = ref([])
const notificationsLoading = ref(false)
let notificationRefreshInterval = null

// Fetch notifications from API
const fetchNotifications = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    const res = await fetch('/api/notifications/?limit=10', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      const notificationsList = Array.isArray(data.notifications) ? data.notifications : []
      notifications.value = notificationsList.map(n => ({
        id: n.id,
        title: n.title,
        message: n.message,
        read: n.is_read,
        time: formatNotificationTime(n.created_at),
        action_url: n.action_url
      }))
      // Yeni bildirim varsa animasyon göster
      if (data.unread_count > 0 && !hasNewNotification.value) {
        hasNewNotification.value = true
      }
    }
  } catch (e) {
    // Sessizce hata yönet
  }
}

// Format notification time
const formatNotificationTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Az önce'
  if (minutes < 60) return `${minutes} dk önce`
  if (hours < 24) return `${hours} saat önce`
  if (days < 7) return `${days} gün önce`
  return date.toLocaleDateString('tr-TR')
}

// Logo error handling with guard to prevent infinite loops
const handleLogoError = (event) => {
  // Prevent infinite error loop - only try fallback once
  if (logoErrorCount.value >= 1) {
    // Already tried fallback, remove src to prevent further errors
    event.target.removeAttribute('src')
    return
  }
  logoErrorCount.value++
  event.target.src = '/logo-navbar.png'
}

// Scroll handling
const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

// Search functions
const expandSearch = () => {
  searchExpanded.value = true
  nextTick(() => {
    searchInput.value?.focus()
  })
}

const collapseSearch = () => {
  if (!searchQuery.value) {
    searchExpanded.value = false
  }
}

// Mobile menu toggle
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
  if (mobileMenuOpen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

// Theme toggle with animation
const toggleTheme = () => {
  themeAnimating.value = true
  themeStore.toggleTheme()
  setTimeout(() => {
    themeAnimating.value = false
  }, 300)
}

// Route active check
const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

// Helper functions
const getInitials = (name) => {
  if (!name) return 'U'
  return name.substring(0, 2).toUpperCase()
}

const getRoleLabel = (role) => {
  const roles = {
    user: 'Üye',
    vip: 'VIP Üye',
    admin: 'Admin',
    superadmin: 'Super Admin'
  }
  return roles[role] || 'Üye'
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

// Navigation functions
const openWallet = (type) => {
  router.push({ path: '/wallet', query: { tab: type } })
}

const navigateTo = (path) => {
  router.push(path)
}

const handleLogout = async () => {
  mobileMenuOpen.value = false
  await authStore.logout()
  router.push('/login')
}

// Notification functions
const handleNotificationPopover = (show) => {
  if (show) {
    hasNewNotification.value = false
    // Popover açıldığında bildirimleri yenile
    fetchNotifications()
  }
}

const markAllAsRead = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    const res = await fetch('/api/notifications/read-all', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      // Lokal state'i güncelle
      notifications.value = notifications.value.map(n => ({ ...n, read: true }))
    }
  } catch (e) {
    // Hata yönetimi
  }
}

const handleNotificationClick = async (notification) => {
  if (!notification.read) {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        await fetch(`/api/notifications/${notification.id}/read`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        notification.read = true
      } catch (e) {
        // Hata yönetimi
      }
    }
  }

  // Eğer action_url varsa yönlendir
  if (notification.action_url) {
    router.push(notification.action_url)
  }
}

// Delete old notifications (older than 30 days)
const cleanupOldNotifications = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    await fetch('/api/notifications/cleanup', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
  } catch (e) {
    // Sessizce hata yönet
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll()

  if (!settingsStore.loaded) {
    settingsStore.fetchSettings()
  }

  // Bildirimleri yükle
  fetchNotifications()

  // 30 saniyede bir bildirimleri yenile
  notificationRefreshInterval = setInterval(fetchNotifications, 30000)

  // Eski bildirimleri temizle (sayfa yüklendiğinde bir kez)
  cleanupOldNotifications()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.body.style.overflow = ''

  // Interval'i temizle
  if (notificationRefreshInterval) {
    clearInterval(notificationRefreshInterval)
  }
})

// Watch for route changes to close mobile menu
watch(() => route.path, () => {
  mobileMenuOpen.value = false
  document.body.style.overflow = ''
})

// Reset logo error count when logo URL changes
watch(logoUrl, () => {
  logoErrorCount.value = 0
})
</script>

<style scoped>
/* ============================================
   NAVBAR BASE STYLES
   ============================================ */
.navbar-glass {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* When mobile menu is open, increase navbar z-index to allow overlay and menu to work */
.navbar-menu-open {
  z-index: 99999;
}

/* Override container for navbar - full width */
.navbar-glass .container-main {
  padding-left: 12px;
  padding-right: 12px;
  max-width: none;
  width: 100%;
}

.navbar-light {
  background: rgba(255, 255, 255, 0.85);
  border-color: rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

.navbar-dark {
  background: rgba(24, 24, 27, 0.85);
  border-color: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

.navbar-scrolled {
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.navbar-light.navbar-scrolled {
  background: rgba(255, 255, 255, 0.95);
}

.navbar-dark.navbar-scrolled {
  background: rgba(24, 24, 27, 0.95);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  transition: height 0.3s ease;
  width: 100%;
}

.navbar-content-shrink {
  height: 56px;
}

/* Left side - logo & nav */
.navbar-left {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

/* Right side actions - don't shrink */
.navbar-actions {
  flex-shrink: 0;
}

/* ============================================
   MOBILE MENU BUTTON (Hamburger)
   ============================================ */
.mobile-menu-btn {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.mobile-menu-btn:hover {
  background: rgba(249, 115, 22, 0.1);
}

.hamburger-line {
  display: block;
  width: 20px;
  height: 2px;
  background: currentColor;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger-line-1 { transform: translateY(-6px); }
.hamburger-line-2 { opacity: 1; }
.hamburger-line-3 { transform: translateY(6px); }

.mobile-menu-btn-active .hamburger-line-1 {
  transform: translateY(0) rotate(45deg);
}

.mobile-menu-btn-active .hamburger-line-2 {
  opacity: 0;
}

.mobile-menu-btn-active .hamburger-line-3 {
  transform: translateY(-2px) rotate(-45deg);
}

/* ============================================
   LOGO STYLES
   ============================================ */
.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  padding: 4px 8px;
  border-radius: 10px;
  transition: all 0.3s ease;
  position: relative;
  flex-shrink: 0;
}

.logo-wrapper:hover {
  background: rgba(249, 115, 22, 0.08);
}

.logo-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-img {
  position: relative;
  z-index: 2;
  transition: transform 0.4s ease, filter 0.4s ease;
  filter: drop-shadow(0 2px 8px rgba(249, 115, 22, 0.3));
}

.logo-wrapper:hover .logo-img {
  transform: scale(1.05);
  filter: drop-shadow(0 4px 16px rgba(249, 115, 22, 0.5));
}

.logo-glow {
  position: absolute;
  inset: -12px;
  background: radial-gradient(ellipse at center, rgba(249, 115, 22, 0.4) 0%, transparent 70%);
  filter: blur(16px);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
  z-index: 1;
}

.logo-wrapper:hover .logo-glow {
  opacity: 1;
  animation: glowPulse 2s ease-in-out infinite;
}

.logo-pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid rgba(249, 115, 22, 0.3);
  opacity: 0;
  pointer-events: none;
  z-index: 0;
}

.logo-wrapper:hover .logo-pulse {
  animation: logoPulse 1.5s ease-out infinite;
}

@keyframes glowPulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
}

@keyframes logoPulse {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(1.5); opacity: 0; }
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.logo-main {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #f97316 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.08em;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}

.logo-sub {
  font-size: 11px;
  font-weight: 700;
  color: var(--n-text-color-3, #94a3b8);
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

/* ============================================
   NAVIGATION LINKS
   ============================================ */
.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--n-text-color-3, #64748b);
  text-decoration: none;
  transition: color 0.2s;
  overflow: hidden;
  white-space: nowrap;
}

/* Hide nav link text on smaller screens, show only icons */
.nav-link-text {
  display: none;
}

@media (min-width: 1280px) {
  .nav-link-text {
    display: inline;
  }
}

.nav-link:hover {
  color: var(--n-text-color, #f8fafc);
}

/* Highlighted nav link (e.g., Forum) - Enhanced with pulse animation */
.nav-link-highlight {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: 1px solid rgba(249, 115, 22, 0.5);
  color: white !important;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  animation: forum-link-pulse 3s ease-in-out infinite;
}

@keyframes forum-link-pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  }
  50% {
    box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
  }
}

.nav-link-highlight:hover {
  background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
  border-color: rgba(249, 115, 22, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
}

.nav-link-highlight .nav-link-text {
  color: white !important;
}

.nav-link-underline {
  position: absolute;
  bottom: 4px;
  left: 14px;
  right: 14px;
  height: 2px;
  background: linear-gradient(90deg, #f97316, #fb923c);
  border-radius: 2px;
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-link:hover .nav-link-underline {
  transform: scaleX(1);
}

.nav-link-active-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(251, 146, 60, 0.1) 100%);
  border-radius: 8px;
  z-index: -1;
  animation: activeSlideIn 0.3s ease forwards;
}

/* Dropdown Trigger */
.nav-dropdown-trigger {
  background: none;
  border: none;
  cursor: pointer;
}

.dropdown-chevron {
  margin-left: 2px;
  transition: transform 0.2s ease;
}

.nav-dropdown-trigger:hover .dropdown-chevron {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.nav-dropdown-menu {
  display: flex;
  flex-direction: column;
  min-width: 180px;
  padding: 6px;
  background: var(--n-color, #18181b);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.nav-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  color: var(--n-text-color-3, #a1a1aa);
  text-decoration: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-dropdown-item:hover {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.nav-dropdown-item-active {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

@keyframes activeSlideIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

.nav-link-active {
  color: #f97316 !important;
}

.nav-link-active .nav-link-underline {
  transform: scaleX(1);
}

/* ============================================
   SEARCH
   ============================================ */
.search-container {
  position: relative;
}

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: var(--n-text-color-3);
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn:hover {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  height: 38px;
  border-radius: 10px;
  background: var(--n-input-color, rgba(0, 0, 0, 0.1));
  border: 1px solid rgba(249, 115, 22, 0.3);
  animation: searchExpand 0.3s ease forwards;
}

@keyframes searchExpand {
  from { width: 38px; opacity: 0; }
  to { width: 200px; opacity: 1; }
}

.search-icon {
  color: var(--n-text-color-3);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--n-text-color);
  min-width: 0;
}

.search-input::placeholder {
  color: var(--n-text-color-3);
}

.search-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: transparent;
  border: none;
  color: var(--n-text-color-3);
  cursor: pointer;
  transition: all 0.2s;
}

.search-close:hover {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

/* ============================================
   LEVEL & XP BADGE
   ============================================ */
.level-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px 3px 3px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.08) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.level-badge:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.12) 100%);
  border-color: rgba(139, 92, 246, 0.3);
  transform: translateY(-1px);
}

.level-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.4);
}

.level-number {
  font-size: 12px;
  font-weight: 800;
  color: white;
  line-height: 1;
}

.level-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 50px;
}

.level-label {
  font-size: 10px;
  font-weight: 600;
  color: #a78bfa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1;
}

.xp-bar {
  width: 100%;
  height: 4px;
  background: rgba(139, 92, 246, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.xp-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.5);
}

/* ============================================
   STREAK BADGE
   ============================================ */
.streak-badge {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: default;
  transition: all 0.2s ease;
}

.streak-icon {
  filter: drop-shadow(0 0 4px currentColor);
}

.streak-count {
  line-height: 1;
}

/* Streak Tiers */
.streak-starter {
  background: linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(107, 114, 128, 0.1) 100%);
  border: 1px solid rgba(107, 114, 128, 0.3);
  color: #9ca3af;
}

.streak-common {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.1) 100%);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.streak-rare {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}

.streak-epic {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #8b5cf6;
}

.streak-legendary {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.25) 0%, rgba(234, 179, 8, 0.15) 100%);
  border: 1px solid rgba(249, 115, 22, 0.4);
  color: #f97316;
  animation: legendaryGlow 2s ease-in-out infinite;
}

@keyframes legendaryGlow {
  0%, 100% {
    box-shadow: 0 0 8px rgba(249, 115, 22, 0.3);
  }
  50% {
    box-shadow: 0 0 16px rgba(249, 115, 22, 0.5), 0 0 24px rgba(234, 179, 8, 0.3);
  }
}

/* ============================================
   WALLET BADGES
   ============================================ */
.wallet-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.wallet-badge-tl {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.1) 100%);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.wallet-badge-tl:hover {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.25) 0%, rgba(34, 197, 94, 0.15) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
}

.wallet-badge-armor {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(249, 115, 22, 0.1) 100%);
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.2);
}

.wallet-badge-armor:hover {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.25) 0%, rgba(249, 115, 22, 0.15) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.2);
}

.wallet-icon {
  font-weight: 700;
}

.wallet-icon-svg {
  flex-shrink: 0;
}

.wallet-amount {
  font-variant-numeric: tabular-nums;
}

/* ============================================
   THEME TOGGLE
   ============================================ */
.theme-toggle {
  background: transparent;
  border: none;
  padding: 4px;
  cursor: pointer;
}

.theme-toggle-track {
  width: 38px;
  height: 20px;
  border-radius: 10px;
  background: var(--n-input-color, rgba(0, 0, 0, 0.1));
  position: relative;
  transition: background 0.3s;
}

.theme-toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);
}

.theme-toggle-thumb-dark {
  transform: translateX(18px);
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.theme-icon {
  color: white;
  transition: transform 0.3s ease;
}

.theme-icon-rotate {
  transform: rotate(360deg);
}

/* ============================================
   NOTIFICATIONS
   ============================================ */
.notification-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: var(--n-text-color-3);
  cursor: pointer;
  transition: all 0.2s;
}

.notification-btn:hover {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.notification-btn-bounce {
  animation: bellBounce 0.5s ease-in-out infinite;
}

@keyframes bellBounce {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(15deg); }
  50% { transform: rotate(0); }
  75% { transform: rotate(-15deg); }
}

.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: badgePop 0.3s ease;
}

@keyframes badgePop {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.notification-dropdown {
  width: 320px;
  max-height: 400px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--n-divider-color);
}

.notification-title {
  font-size: 15px;
  font-weight: 600;
}

.notification-mark-read {
  background: transparent;
  border: none;
  color: #f97316;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.notification-mark-read:hover {
  background: rgba(249, 115, 22, 0.1);
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.notification-item {
  position: relative;
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  animation: notificationSlideIn 0.3s ease forwards;
  opacity: 0;
}

@keyframes notificationSlideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.notification-item:hover {
  background: var(--n-hover-color);
}

.notification-item-unread {
  background: rgba(249, 115, 22, 0.05);
}

.notification-item-indicator {
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f97316;
}

.notification-item-content {
  flex: 1;
  min-width: 0;
}

.notification-item-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 2px;
}

.notification-item-message {
  font-size: 12px;
  color: var(--n-text-color-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-item-time {
  font-size: 11px;
  color: var(--n-text-color-3);
  margin-top: 4px;
}

.notification-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px;
  color: var(--n-text-color-3);
  font-size: 13px;
}

.notification-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--n-divider-color);
  text-align: center;
}

.notification-view-all {
  font-size: 13px;
  font-weight: 500;
  color: #f97316;
  text-decoration: none;
  transition: opacity 0.2s;
}

.notification-view-all:hover {
  opacity: 0.8;
}

/* ============================================
   USER MENU
   ============================================ */
.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.user-menu-trigger:hover {
  background: var(--n-hover-color);
}

.user-avatar-wrapper {
  position: relative;
}

.user-avatar {
  border: 2px solid transparent;
  background-clip: padding-box;
}

.user-status-ring {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--n-card-color, #fff);
  background: #6b7280;
}

.user-status-ring.large {
  width: 14px;
  height: 14px;
}

.user-status-online {
  background: #22c55e;
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  50% { box-shadow: 0 0 0 4px rgba(34, 197, 94, 0); }
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.user-chevron {
  color: var(--n-text-color-3);
  transition: transform 0.2s;
}

.user-menu-trigger:hover .user-chevron {
  transform: translateY(2px);
}

.user-dropdown {
  width: 240px;
  padding: 8px;
}

.user-dropdown-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--n-hover-color);
}

.user-dropdown-avatar-wrapper {
  position: relative;
}

.user-dropdown-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-dropdown-name {
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-dropdown-role {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.user-dropdown-divider {
  height: 1px;
  background: var(--n-divider-color);
  margin: 8px 0;
}

.user-dropdown-menu {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  background: transparent;
  border: none;
  font-size: 14px;
  color: var(--n-text-color);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.user-dropdown-item:hover {
  background: var(--n-hover-color);
  color: #f97316;
}

.user-dropdown-item:hover :deep(.n-icon) {
  color: #f97316;
}

.user-dropdown-item-admin {
  color: #f97316;
}

.user-dropdown-item-logout {
  color: #ef4444;
}

.user-dropdown-item-logout:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* ============================================
   LOGIN BUTTON
   ============================================ */
.login-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(249, 115, 22, 0.4);
}

/* ============================================
   MOBILE MENU
   ============================================ */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 99998;
}

.mobile-overlay-enter-active,
.mobile-overlay-leave-active {
  transition: opacity 0.3s ease;
}

.mobile-overlay-enter-from,
.mobile-overlay-leave-to {
  opacity: 0;
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 300px;
  max-width: 85vw;
  height: 100vh;
  z-index: 99999;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
}

.mobile-menu-light {
  background: #ffffff;
}

.mobile-menu-dark {
  background: #18181b;
}

.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  transform: translateX(100%);
}

.mobile-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--n-divider-color);
}

.mobile-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.mobile-logo-img {
  height: 32px;
  width: auto;
}

.mobile-logo-text {
  font-size: 18px;
  font-weight: 800;
  color: #f97316;
}

.mobile-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: var(--n-text-color);
  cursor: pointer;
  transition: background 0.2s;
}

.mobile-close-btn:hover {
  background: var(--n-hover-color);
}

.mobile-wallet {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--n-divider-color);
}

.mobile-wallet-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  border-radius: 10px;
  background: var(--n-hover-color);
  cursor: pointer;
  transition: background 0.2s;
}

.mobile-wallet-item:hover {
  background: rgba(249, 115, 22, 0.1);
}

.mobile-wallet-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--n-text-color-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.mobile-wallet-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--n-text-color);
}

.mobile-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  color: var(--n-text-color);
  text-decoration: none;
  transition: all 0.2s;
  animation: mobileNavSlideIn 0.3s ease forwards;
  opacity: 0;
}

@keyframes mobileNavSlideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.mobile-nav-item:hover {
  background: var(--n-hover-color);
}

.mobile-nav-item-active {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(249, 115, 22, 0.1) 100%);
  color: #f97316;
}

/* Mobile Nav Group (for dropdowns) */
.mobile-nav-group {
  margin: 8px 0;
  padding: 0 8px;
}

.mobile-nav-group-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--n-text-color-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mobile-nav-child {
  padding-left: 24px;
  font-size: 14px;
}

.mobile-nav-arrow {
  margin-left: auto;
  color: var(--n-text-color-3);
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.2s;
}

.mobile-nav-item:hover .mobile-nav-arrow {
  opacity: 1;
  transform: translateX(0);
}

.mobile-user-section {
  padding: 16px 20px;
  border-top: 1px solid var(--n-divider-color);
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.mobile-user-details {
  display: flex;
  flex-direction: column;
}

.mobile-user-name {
  font-size: 15px;
  font-weight: 600;
}

.mobile-user-role {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.mobile-logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.mobile-logout-btn:hover {
  background: rgba(239, 68, 68, 0.15);
}

.mobile-login {
  padding: 16px 20px;
  border-top: 1px solid var(--n-divider-color);
}

.mobile-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.mobile-login-btn:hover {
  opacity: 0.9;
}

/* ============================================
   RESPONSIVE BREAKPOINTS
   ============================================ */
@media (max-width: 1024px) {
  .navbar-content {
    height: 60px;
  }

  .navbar-content-shrink {
    height: 54px;
  }
}

@media (max-width: 768px) {
  .navbar-content {
    height: 56px;
  }

  .navbar-content-shrink {
    height: 52px;
  }

  .logo-main {
    font-size: 18px;
  }

  .logo-sub {
    font-size: 10px;
  }

  .search-container {
    display: none;
  }
}

@media (max-width: 640px) {
  .logo-text {
    display: none;
  }

  .wallet-badge {
    padding: 4px 10px;
    font-size: 12px;
  }
}

/* ============================================
   DARK MODE SPECIFIC
   ============================================ */
.navbar-dark .nav-link:hover {
  color: #f8fafc;
}

.navbar-light .nav-link:hover {
  color: #1e293b;
}

/* ============================================
   POPOVER OVERRIDES
   ============================================ */
:deep(.notification-popover),
:deep(.user-menu-popover) {
  padding: 0 !important;
  border-radius: 16px !important;
  overflow: hidden;
}
</style>
