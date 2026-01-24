<!-- Navbar.vue - Forum Linki Vurgulanmış Versiyon -->
<template>
  <nav class="navbar">
    <div class="nav-container">
      
      <!-- Logo & Brand -->
      <div class="nav-left">
        <router-link to="/" class="logo">
          <span class="logo-icon">🔶</span>
          <span class="logo-text">AGTR</span>
        </router-link>
      </div>

      <!-- Navigation Links -->
      <div class="nav-center" :class="{ 'mobile-menu-open': mobileMenuOpen }">
        <router-link to="/" class="nav-link">
          <span class="link-icon">🏠</span>
          <span class="link-text">Ana Sayfa</span>
        </router-link>
        
        <!-- FORUM LİNKİ - VURGULANMIŞ -->
        <router-link to="/forum" class="nav-link nav-link-forum">
          <span class="link-icon">💬</span>
          <span class="link-text">Forum</span>
          <span v-if="unreadCount > 0" class="notification-badge">
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </span>
        </router-link>
        
        <router-link to="/servers" class="nav-link">
          <span class="link-icon">🎮</span>
          <span class="link-text">Sunucular</span>
        </router-link>
        
        <router-link to="/jackpot" class="nav-link">
          <span class="link-icon">🎰</span>
          <span class="link-text">Jackpot</span>
        </router-link>
      </div>

      <!-- Right Side -->
      <div class="nav-right">
        
        <!-- Online Indicator -->
        <div class="online-indicator">
          <span class="online-dot"></span>
          <span class="online-count">{{ onlineUsers }}</span>
          <span class="online-label">online</span>
        </div>

        <!-- Notifications -->
        <div class="notification-icon" @click="toggleNotifications">
          <span>🔔</span>
          <span v-if="notificationCount > 0" class="notification-badge-small">
            {{ notificationCount }}
          </span>
        </div>

        <!-- User Menu -->
        <n-dropdown 
          v-if="authStore.isAuthenticated" 
          :options="userMenuOptions"
          @select="handleUserMenuSelect"
        >
          <div class="user-avatar">
            <img :src="authStore.user?.avatar_url" :alt="authStore.user?.username" />
            <div class="user-level-badge">{{ authStore.user?.level }}</div>
          </div>
        </n-dropdown>

        <!-- Login Button -->
        <n-button 
          v-else
          type="primary"
          @click="router.push('/login')"
          class="login-button"
        >
          Giriş Yap
        </n-button>

        <!-- Mobile Menu Toggle -->
        <button class="mobile-menu-toggle" @click="toggleMobileMenu">
          <span class="hamburger-icon" :class="{ 'active': mobileMenuOpen }">
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

// State
const mobileMenuOpen = ref(false)
const onlineUsers = ref(0)
const unreadCount = ref(0)
const notificationCount = ref(0)

// User Menu Options
const userMenuOptions = computed(() => [
  {
    label: 'Profilim',
    key: 'profile',
    icon: '👤'
  },
  {
    label: 'Cüzdan',
    key: 'wallet',
    icon: '💰'
  },
  {
    label: 'Ayarlar',
    key: 'settings',
    icon: '⚙️'
  },
  {
    type: 'divider'
  },
  {
    label: 'Çıkış Yap',
    key: 'logout',
    icon: '🚪'
  }
])

// Methods
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const toggleNotifications = () => {
  // Notifications modal açılacak
  console.log('Notifications clicked')
}

const handleUserMenuSelect = (key) => {
  if (key === 'logout') {
    authStore.logout()
    router.push('/')
  } else {
    router.push(`/${key}`)
  }
}

const fetchOnlineCount = async () => {
  try {
    const response = await api.get('/forum/online-users')
    onlineUsers.value = response.total
  } catch (error) {
    console.error('Online count yüklenemedi:', error)
  }
}

const fetchUnreadCount = async () => {
  if (!authStore.isAuthenticated) return
  
  try {
    const response = await api.get('/forum/unread-count')
    unreadCount.value = response.count
  } catch (error) {
    console.error('Unread count yüklenemedi:', error)
  }
}

// Lifecycle
let intervalId
onMounted(() => {
  fetchOnlineCount()
  fetchUnreadCount()
  
  // Her 30 saniyede bir güncelle
  intervalId = setInterval(() => {
    fetchOnlineCount()
    fetchUnreadCount()
  }, 30000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<style scoped>
.navbar {
  background: var(--bg-card);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 2rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.logo-text {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Navigation Links */
.nav-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.nav-link.router-link-active {
  color: var(--text-primary);
}

/* FORUM LİNKİ - VURGULANMIŞ */
.nav-link-forum {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white !important;
  padding: 10px 20px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  animation: forum-pulse 3s infinite;
  position: relative;
}

@keyframes forum-pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  }
  50% {
    box-shadow: 0 6px 20px rgba(249, 115, 22, 0.6);
  }
}

.nav-link-forum:hover {
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
}

.nav-link-forum .link-icon {
  font-size: 1.2rem;
}

/* Notification Badge */
.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 700;
  min-width: 18px;
  text-align: center;
  animation: badge-bounce 1s infinite;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.5);
}

@keyframes badge-bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

/* Online Indicator */
.online-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(57, 255, 20, 0.1);
  border-radius: 20px;
  font-size: 0.9rem;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: var(--neon-green);
  border-radius: 50%;
  animation: dot-pulse 2s infinite;
}

@keyframes dot-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(57, 255, 20, 0.7);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(57, 255, 20, 0);
  }
}

.online-count {
  color: var(--neon-green);
  font-weight: 700;
}

.online-label {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* Nav Right */
.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-icon {
  position: relative;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.notification-icon:hover {
  background: rgba(255, 255, 255, 0.05);
}

.notification-badge-small {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #ef4444;
  color: white;
  padding: 2px 5px;
  border-radius: 8px;
  font-size: 0.6rem;
  font-weight: 700;
  min-width: 14px;
  text-align: center;
}

/* User Avatar */
.user-avatar {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--primary);
}

.user-avatar:hover img {
  border-color: var(--primary-light);
  transform: scale(1.1);
}

.user-level-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: var(--primary);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 700;
  border: 2px solid var(--bg-card);
}

/* Mobile Menu */
.mobile-menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}

.hamburger-icon {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 24px;
}

.hamburger-icon span {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--text-primary);
  transition: all 0.3s ease;
}

.hamburger-icon.active span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger-icon.active span:nth-child(2) {
  opacity: 0;
}

.hamburger-icon.active span:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -7px);
}

/* Responsive */
@media (max-width: 768px) {
  .nav-center {
    position: fixed;
    top: 65px;
    left: 0;
    right: 0;
    flex-direction: column;
    background: var(--bg-card);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px;
    gap: 12px;
    transform: translateY(-100%);
    opacity: 0;
    transition: all 0.3s ease;
    pointer-events: none;
  }
  
  .nav-center.mobile-menu-open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: all;
  }
  
  .nav-link {
    width: 100%;
    justify-content: center;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .online-indicator {
    font-size: 0.8rem;
    padding: 4px 10px;
  }
  
  .online-label {
    display: none;
  }
}
</style>
