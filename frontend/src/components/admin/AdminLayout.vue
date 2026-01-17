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
  ChevronRight
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)
const pendingPayments = ref(0)

// Fetch pending payments count
const fetchPendingCount = async () => {
  try {
    const response = await fetch('/api/admin/dashboard')
    if (response.ok) {
      const data = await response.json()
      pendingPayments.value = data.pending_payments || 0
    }
  } catch (e) {
    console.error('Pending count fetch error:', e)
  }
}

// Fetch on mount
fetchPendingCount()

const menuItems = [
  { path: '/admin', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/users', label: 'Kullanıcılar', icon: Users },
  { path: '/admin/servers', label: 'Sunucular', icon: Server },
  { path: '/admin/payments', label: 'Ödemeler', icon: CreditCard },
  { path: '/admin/packages', label: 'Paketler', icon: Package },
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
  background: var(--bg-primary);
}

/* Sidebar */
.admin-sidebar {
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
}

.admin-sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: var(--gradient-primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: var(--bg-primary);
}

.logo-text {
  font-weight: 700;
  font-size: 18px;
}

.collapse-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.collapsed .collapse-btn {
  display: none;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.2s;
  margin-bottom: 4px;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  font-size: 14px;
}

.nav-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(255, 107, 0, 0.15);
  color: var(--primary-color);
}

.collapsed .nav-item {
  justify-content: center;
  padding: 12px;
}

.collapsed .nav-item span {
  display: none;
}

.badge {
  margin-left: auto;
  background: var(--primary-color);
  color: var(--bg-primary);
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

/* Footer */
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border-color);
}

.logout-btn {
  color: var(--error-color, #ef4444);
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* Main Content */
.admin-main {
  flex: 1;
  margin-left: 260px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
}

.collapsed + .admin-main {
  margin-left: 72px;
}

/* Top Bar */
.admin-topbar {
  height: 64px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-tertiary);
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
}

/* Content Area */
.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
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
}
</style>
