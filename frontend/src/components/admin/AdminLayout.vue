<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="admin-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <router-link to="/admin" class="logo-link">
          <div class="logo-icon">
            <span>λ</span>
          </div>
          <span v-if="!sidebarCollapsed" class="logo-text">Admin</span>
        </router-link>
        <button class="collapse-btn" @click="toggleSidebar">
          <ChevronLeft v-if="!sidebarCollapsed" :size="20" />
          <ChevronRight v-else :size="20" />
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <component :is="item.icon" :size="20" />
          <span v-if="!sidebarCollapsed">{{ item.label }}</span>
          <span v-if="item.path === '/admin/payments' && pendingPayments > 0 && !sidebarCollapsed" class="badge">{{ pendingPayments }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/" class="nav-item">
          <Home :size="20" />
          <span v-if="!sidebarCollapsed">Siteye Dön</span>
        </router-link>
        <button class="nav-item logout-btn" @click="logout">
          <LogOut :size="20" />
          <span v-if="!sidebarCollapsed">Çıkış</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="admin-main">
      <!-- Top Bar -->
      <header class="admin-topbar">
        <div class="topbar-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="topbar-right">
          <div class="user-menu">
            <img :src="userAvatar" alt="Avatar" class="user-avatar" />
            <span class="user-name">{{ userName }}</span>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="admin-content">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard,
  Users,
  Server,
  CreditCard,
  Package,
  Settings,
  Home,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Image,
  FileText,
  Megaphone,
  Palette,
  MessageSquare,
  Wrench
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)
const pendingPayments = ref(0)

// Fetch pending payments count
const fetchPendingCount = async () => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const response = await fetch('/api/admin/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      // API returns: { payments: { pending: X, ... } }
      pendingPayments.value = data.payments?.pending || 0
    }
  } catch {
    // Pending count fetch error
  }
}

// Fetch on mount
fetchPendingCount()

// Consolidated menu - removed redundant pages
const menuItems = [
  { path: '/admin', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/users', label: 'Kullanıcılar', icon: Users },
  { path: '/admin/servers', label: 'Sunucular', icon: Server },
  { path: '/admin/payments', label: 'Ödemeler', icon: CreditCard },
  { path: '/admin/packages', label: 'Paketler', icon: Package },
  { path: '/admin/forum', label: 'Forum', icon: MessageSquare },
  { path: '/admin/media', label: 'Medya', icon: Image },
  { path: '/admin/pages', label: 'Sayfalar', icon: FileText },
  { path: '/admin/maintenance', label: 'Bakım Modu', icon: Wrench },
  { path: '/admin/settings', label: 'Ayarlar', icon: Settings }
]

const pageTitle = computed(() => {
  const currentItem = menuItems.find(item => item.path === route.path)
  return currentItem?.label || 'Admin Panel'
})

const userName = computed(() => authStore.user?.username || 'Admin')
const userAvatar = computed(() => `https://api.dicebear.com/7.x/initials/svg?seed=${userName.value}`)

const isActive = (path) => {
  if (path === '/admin') {
    return route.path === '/admin'
  }
  return route.path.startsWith(path)
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

/* Sidebar - Gaming Premium Style */
.admin-sidebar {
  width: 280px;
  background: linear-gradient(180deg, rgba(24, 24, 28, 0.98) 0%, rgba(15, 15, 18, 0.98) 100%);
  border-right: 1px solid rgba(249, 115, 22, 0.15);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  backdrop-filter: blur(20px);
}

.admin-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f97316 0%, #fb923c 50%, #f97316 100%);
  background-size: 200% 100%;
  animation: gradientMove 3s linear infinite;
}

@keyframes gradientMove {
  0% { background-position: 0% 0; }
  100% { background-position: 200% 0; }
}

.admin-sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 20px;
  color: #fff;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
  transition: all 0.3s ease;
}

.logo-link:hover .logo-icon {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(249, 115, 22, 0.5);
}

.logo-text {
  font-family: 'Poppins', 'Inter', sans-serif;
  font-weight: 700;
  font-size: 20px;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.collapse-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

.collapsed .collapse-btn {
  display: none;
}

/* Navigation - Enhanced */
.sidebar-nav {
  flex: 1;
  padding: 20px 14px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.2s ease;
  margin-bottom: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  background: transparent;
  width: 100%;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: linear-gradient(180deg, #f97316 0%, #fb923c 100%);
  border-radius: 0 2px 2px 0;
  transition: height 0.2s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}

.nav-item:hover::before {
  height: 20px;
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(249, 115, 22, 0.08) 100%);
  border-color: rgba(249, 115, 22, 0.25);
  color: #f97316;
  font-weight: 600;
}

.nav-item.active::before {
  height: 60%;
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
}

.collapsed .nav-item {
  justify-content: center;
  padding: 14px;
}

.collapsed .nav-item span {
  display: none;
}

.badge {
  margin-left: auto;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.4);
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Footer */
.sidebar-footer {
  padding: 16px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.logout-btn {
  color: #ef4444 !important;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.15) !important;
  border-color: rgba(239, 68, 68, 0.3) !important;
}

.logout-btn::before {
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%) !important;
}

/* Main Content */
.admin-main {
  flex: 1;
  margin-left: 280px;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.collapsed + .admin-main {
  margin-left: 80px;
}

/* Top Bar - Premium Style */
.admin-topbar {
  height: 72px;
  background: linear-gradient(135deg, rgba(24, 24, 28, 0.95) 0%, rgba(30, 30, 35, 0.95) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(20px);
}

.page-title {
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 16px 8px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 50px;
  transition: all 0.2s ease;
}

.user-menu:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(249, 115, 22, 0.2);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(249, 115, 22, 0.3);
  background: var(--bg-tertiary);
}

.user-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

/* Content Area */
.admin-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: transparent;
}

/* Custom Scrollbar for Sidebar */
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(249, 115, 22, 0.3);
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(249, 115, 22, 0.5);
}

/* Responsive */
@media (max-width: 1024px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }

  .admin-sidebar.open {
    transform: translateX(0);
  }

  .admin-main {
    margin-left: 0;
  }

  .admin-topbar {
    padding: 0 20px;
  }

  .admin-content {
    padding: 20px;
  }
}
</style>
