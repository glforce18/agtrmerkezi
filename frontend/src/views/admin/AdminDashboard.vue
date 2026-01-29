<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-text-primary mb-1">Admin Paneli</h1>
      <p class="text-text-muted text-sm">Sistem yönetimi ve istatistikler</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-primary text-3xl mb-3">⏳</div>
      <p class="text-text-muted text-sm">Dashboard yükleniyor...</p>
    </div>

    <div v-else>
      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <!-- Total Users -->
        <div class="card p-5">
          <div class="flex items-center justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="text-text-muted text-xs mb-1.5">Toplam Kullanıcı</div>
              <div class="text-2xl font-bold text-text-primary truncate">{{ stats.total_users || 0 }}</div>
              <div class="text-status-success text-xs mt-1">
                +{{ stats.new_users_today || 0 }} bugün
              </div>
            </div>
            <div class="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-xl">👥</span>
            </div>
          </div>
        </div>

        <!-- Active Servers -->
        <div class="card p-5">
          <div class="flex items-center justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="text-text-muted text-xs mb-1.5">Aktif Sunucular</div>
              <div class="text-2xl font-bold text-text-primary truncate">{{ stats.active_servers || 0 }}</div>
              <div class="text-text-muted text-xs mt-1">
                / {{ stats.total_servers || 0 }} toplam
              </div>
            </div>
            <div class="w-10 h-10 bg-status-success/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-xl">🖥️</span>
            </div>
          </div>
        </div>

        <!-- Revenue -->
        <div class="card p-5">
          <div class="flex items-center justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="text-text-muted text-xs mb-1.5">Aylık Gelir</div>
              <div class="text-2xl font-bold text-text-primary truncate">₺{{ formatMoney(stats.monthly_revenue) }}</div>
              <div class="text-status-success text-xs mt-1">
                +{{ stats.revenue_growth || 0 }}%
              </div>
            </div>
            <div class="w-10 h-10 bg-status-success/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-xl">💰</span>
            </div>
          </div>
        </div>

        <!-- Forum Activity -->
        <div class="card p-5">
          <div class="flex items-center justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="text-text-muted text-xs mb-1.5">Forum Konuları</div>
              <div class="text-2xl font-bold text-text-primary truncate">{{ stats.total_topics || 0 }}</div>
              <div class="text-text-muted text-xs mt-1">
                {{ stats.total_replies || 0 }} yanıt
              </div>
            </div>
            <div class="w-10 h-10 bg-status-info/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-xl">💬</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
        <!-- User Growth Chart -->
        <div class="card p-6">
          <h2 class="text-lg font-bold text-text-primary mb-4">Kullanıcı Büyümesi</h2>
          <div class="h-48 flex items-center justify-center text-text-muted">
            <div class="text-center">
              <div class="text-3xl mb-2">📈</div>
              <p class="text-sm">Grafik yakında eklenecek</p>
            </div>
          </div>
        </div>

        <!-- Server Status Chart -->
        <div class="card p-6">
          <h2 class="text-lg font-bold text-text-primary mb-4">Sunucu Durumları</h2>
          <div class="h-48 flex items-center justify-center text-text-muted">
            <div class="text-center">
              <div class="text-3xl mb-2">📊</div>
              <p class="text-sm">Grafik yakında eklenecek</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity & Quick Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
        <!-- Recent Users -->
        <div class="card p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-text-primary">Son Kullanıcılar</h2>
            <router-link to="/admin/users" class="text-primary text-xs hover:text-primary-light">
              Tümü →
            </router-link>
          </div>

          <div v-if="recentUsers.length" class="space-y-2.5">
            <div v-for="user in recentUsers" :key="user.id" class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white font-bold text-xs">{{ getInitials(user.username) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-text-primary font-medium text-sm truncate">{{ user.username }}</div>
                <div class="text-text-muted text-xs">{{ formatDate(user.created_at) }}</div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-6 text-text-muted">
            <div class="text-3xl mb-1.5">👤</div>
            <p class="text-xs">Henüz kullanıcı yok</p>
          </div>
        </div>

        <!-- Recent Servers -->
        <div class="card p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-text-primary">Son Sunucular</h2>
            <router-link to="/admin/servers" class="text-primary text-xs hover:text-primary-light">
              Tümü →
            </router-link>
          </div>

          <div v-if="recentServers.length" class="space-y-2.5">
            <div v-for="server in recentServers" :key="server.id" class="flex items-center justify-between gap-2">
              <div class="flex-1 min-w-0">
                <div class="text-text-primary font-medium text-sm truncate">{{ server.name }}</div>
                <div class="text-text-muted text-xs truncate">{{ server.ip }}:{{ server.port }}</div>
              </div>
              <div class="badge text-xs flex-shrink-0" :class="statusBadgeClass(server.status)">
                {{ statusText(server.status) }}
              </div>
            </div>
          </div>

          <div v-else class="text-center py-6 text-text-muted">
            <div class="text-3xl mb-1.5">🖥️</div>
            <p class="text-xs">Henüz sunucu yok</p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card p-5">
          <h2 class="text-base font-bold text-text-primary mb-4">Hızlı İşlemler</h2>

          <div class="space-y-1.5">
            <router-link to="/admin/users" class="btn btn-secondary w-full text-sm flex items-center gap-2 justify-start">
              <span class="text-base">👥</span>
              <span class="truncate">Kullanıcı Yönetimi</span>
            </router-link>

            <router-link to="/admin/servers" class="btn btn-secondary w-full text-sm flex items-center gap-2 justify-start">
              <span class="text-base">🖥️</span>
              <span class="truncate">Sunucu Yönetimi</span>
            </router-link>

            <router-link to="/admin/server-approval" class="btn btn-secondary w-full text-sm flex items-center gap-2 justify-start">
              <span class="text-base">✅</span>
              <span class="truncate">Sunucu Onay Paneli</span>
            </router-link>

            <router-link to="/forum" class="btn btn-secondary w-full text-sm flex items-center gap-2 justify-start">
              <span class="text-base">💬</span>
              <span class="truncate">Forum Yönetimi</span>
            </router-link>

            <router-link to="/admin/packages" class="btn btn-secondary w-full text-sm flex items-center gap-2 justify-start">
              <span class="text-base">📦</span>
              <span class="truncate">Paket Yönetimi</span>
            </router-link>

            <router-link to="/admin/payments" class="btn btn-secondary w-full text-sm flex items-center gap-2 justify-start">
              <span class="text-base">💳</span>
              <span class="truncate">Ödeme İşlemleri</span>
            </router-link>

            <router-link to="/admin/settings" class="btn btn-secondary w-full text-sm flex items-center gap-2 justify-start">
              <span class="text-base">⚙️</span>
              <span class="truncate">Sistem Ayarları</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- System Status -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- CPU Usage -->
        <div class="card p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-text-muted text-xs">CPU Kullanımı</span>
            <span class="text-text-primary font-bold text-sm">{{ stats.cpu_usage || 0 }}%</span>
          </div>
          <div class="w-full bg-dark-elevated rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="usageColor(stats.cpu_usage)"
              :style="{ width: `${stats.cpu_usage || 0}%` }"
            ></div>
          </div>
        </div>

        <!-- Memory Usage -->
        <div class="card p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-text-muted text-xs">RAM Kullanımı</span>
            <span class="text-text-primary font-bold text-sm">{{ stats.memory_usage || 0 }}%</span>
          </div>
          <div class="w-full bg-dark-elevated rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="usageColor(stats.memory_usage)"
              :style="{ width: `${stats.memory_usage || 0}%` }"
            ></div>
          </div>
        </div>

        <!-- Disk Usage -->
        <div class="card p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-text-muted text-xs">Disk Kullanımı</span>
            <span class="text-text-primary font-bold text-sm">{{ stats.disk_usage || 0 }}%</span>
          </div>
          <div class="w-full bg-dark-elevated rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="usageColor(stats.disk_usage)"
              :style="{ width: `${stats.disk_usage || 0}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

const loading = ref(true)
const stats = ref({
  total_users: 0,
  new_users_today: 0,
  active_servers: 0,
  total_servers: 0,
  monthly_revenue: 0,
  revenue_growth: 0,
  total_topics: 0,
  total_replies: 0,
  cpu_usage: 0,
  memory_usage: 0,
  disk_usage: 0
})

const recentUsers = ref([])
const recentServers = ref([])

onMounted(async () => {
  await fetchDashboardData()
})

const fetchDashboardData = async () => {
  try {
    // Fetch dashboard stats
    const response = await apiClient.get('/admin/dashboard/stats')
    stats.value = response.data.stats || stats.value

    // Fetch recent users (use main users endpoint with limit)
    const usersResponse = await apiClient.get('/admin/users', {
      params: { page: 1, per_page: 5, sort_by: 'created_at', sort_order: 'desc' }
    })
    recentUsers.value = usersResponse.data.data || []

    // Fetch recent servers (use main servers endpoint with limit)
    const serversResponse = await apiClient.get('/admin/servers', {
      params: { page: 1, per_page: 5, sort_by: 'created_at', sort_order: 'desc' }
    })
    recentServers.value = serversResponse.data.data || []
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const formatMoney = (amount) => {
  if (!amount) return '0'
  return new Intl.NumberFormat('tr-TR').format(amount)
}

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const formatDate = (dateString) => {
  if (!dateString) return ''

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffDays === 0) return 'Bugün'
  if (diffDays === 1) return 'Dün'
  if (diffDays < 7) return `${diffDays} gün önce`

  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short'
  })
}

const statusBadgeClass = (status) => {
  const classes = {
    running: 'badge-success',
    stopped: 'badge-secondary',
    starting: 'badge-warning',
    error: 'badge-danger'
  }
  return classes[status] || classes.stopped
}

const statusText = (status) => {
  const texts = {
    running: '● Açık',
    stopped: '● Kapalı',
    starting: '● Başlatılıyor',
    error: '● Hata'
  }
  return texts[status] || '● Kapalı'
}

const usageColor = (usage) => {
  if (usage >= 90) return 'bg-status-error'
  if (usage >= 75) return 'bg-status-warning'
  return 'bg-status-success'
}
</script>
