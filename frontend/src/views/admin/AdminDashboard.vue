<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">Admin Paneli</h1>
      <p class="text-gray-400">Sistem yönetimi ve istatistikler</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-primary text-4xl mb-4">⏳</div>
      <p class="text-gray-400">Dashboard yükleniyor...</p>
    </div>

    <div v-else>
      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Total Users -->
        <div class="stat-card-large">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-gray-400 text-sm mb-1">Toplam Kullanıcı</div>
              <div class="text-3xl font-bold text-white">{{ stats.total_users || 0 }}</div>
              <div class="text-green-400 text-sm mt-1">
                +{{ stats.new_users_today || 0 }} bugün
              </div>
            </div>
            <div class="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
              <span class="text-2xl">👥</span>
            </div>
          </div>
        </div>

        <!-- Active Servers -->
        <div class="stat-card-large">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-gray-400 text-sm mb-1">Aktif Sunucular</div>
              <div class="text-3xl font-bold text-white">{{ stats.active_servers || 0 }}</div>
              <div class="text-gray-400 text-sm mt-1">
                / {{ stats.total_servers || 0 }} toplam
              </div>
            </div>
            <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
              <span class="text-2xl">🖥️</span>
            </div>
          </div>
        </div>

        <!-- Revenue -->
        <div class="stat-card-large">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-gray-400 text-sm mb-1">Aylık Gelir</div>
              <div class="text-3xl font-bold text-white">₺{{ formatMoney(stats.monthly_revenue) }}</div>
              <div class="text-green-400 text-sm mt-1">
                +{{ stats.revenue_growth || 0 }}%
              </div>
            </div>
            <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
              <span class="text-2xl">💰</span>
            </div>
          </div>
        </div>

        <!-- Forum Activity -->
        <div class="stat-card-large">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-gray-400 text-sm mb-1">Forum Konuları</div>
              <div class="text-3xl font-bold text-white">{{ stats.total_topics || 0 }}</div>
              <div class="text-gray-400 text-sm mt-1">
                {{ stats.total_replies || 0 }} yanıt
              </div>
            </div>
            <div class="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <span class="text-2xl">💬</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- User Growth Chart -->
        <div class="card">
          <h2 class="text-xl font-bold text-white mb-4">Kullanıcı Büyümesi</h2>
          <div class="h-64 flex items-center justify-center text-gray-400">
            <div class="text-center">
              <div class="text-4xl mb-2">📈</div>
              <p>Grafik yakında eklenecek</p>
            </div>
          </div>
        </div>

        <!-- Server Status Chart -->
        <div class="card">
          <h2 class="text-xl font-bold text-white mb-4">Sunucu Durumları</h2>
          <div class="h-64 flex items-center justify-center text-gray-400">
            <div class="text-center">
              <div class="text-4xl mb-2">📊</div>
              <p>Grafik yakında eklenecek</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity & Quick Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <!-- Recent Users -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-white">Son Kullanıcılar</h2>
            <router-link to="/admin/users" class="text-primary text-sm hover:text-primary-dark">
              Tümü →
            </router-link>
          </div>

          <div v-if="recentUsers.length" class="space-y-3">
            <div v-for="user in recentUsers" :key="user.id" class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
                <span class="text-white font-bold text-sm">{{ getInitials(user.username) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-white font-semibold truncate">{{ user.username }}</div>
                <div class="text-gray-400 text-xs">{{ formatDate(user.created_at) }}</div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-400">
            <div class="text-4xl mb-2">👤</div>
            <p class="text-sm">Henüz kullanıcı yok</p>
          </div>
        </div>

        <!-- Recent Servers -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-white">Son Sunucular</h2>
            <router-link to="/admin/servers" class="text-primary text-sm hover:text-primary-dark">
              Tümü →
            </router-link>
          </div>

          <div v-if="recentServers.length" class="space-y-3">
            <div v-for="server in recentServers" :key="server.id" class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="text-white font-semibold truncate">{{ server.name }}</div>
                <div class="text-gray-400 text-xs">{{ server.ip }}:{{ server.port }}</div>
              </div>
              <div class="badge" :class="statusBadgeClass(server.status)">
                {{ statusText(server.status) }}
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-400">
            <div class="text-4xl mb-2">🖥️</div>
            <p class="text-sm">Henüz sunucu yok</p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card">
          <h2 class="text-lg font-bold text-white mb-4">Hızlı İşlemler</h2>

          <div class="space-y-2">
            <router-link to="/admin/users" class="btn btn-secondary w-full justify-start">
              <span class="text-lg">👥</span>
              <span>Kullanıcı Yönetimi</span>
            </router-link>

            <router-link to="/admin/servers" class="btn btn-secondary w-full justify-start">
              <span class="text-lg">🖥️</span>
              <span>Sunucu Yönetimi</span>
            </router-link>

            <router-link to="/forum" class="btn btn-secondary w-full justify-start">
              <span class="text-lg">💬</span>
              <span>Forum Yönetimi</span>
            </router-link>

            <router-link to="/admin/packages" class="btn btn-secondary w-full justify-start">
              <span class="text-lg">📦</span>
              <span>Paket Yönetimi</span>
            </router-link>

            <router-link to="/admin/payments" class="btn btn-secondary w-full justify-start">
              <span class="text-lg">💳</span>
              <span>Ödeme İşlemleri</span>
            </router-link>

            <router-link to="/admin/settings" class="btn btn-secondary w-full justify-start">
              <span class="text-lg">⚙️</span>
              <span>Sistem Ayarları</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- System Status -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- CPU Usage -->
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-400 text-sm">CPU Kullanımı</span>
            <span class="text-white font-bold">{{ stats.cpu_usage || 0 }}%</span>
          </div>
          <div class="w-full bg-dark-bg rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="usageColor(stats.cpu_usage)"
              :style="{ width: `${stats.cpu_usage || 0}%` }"
            ></div>
          </div>
        </div>

        <!-- Memory Usage -->
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-400 text-sm">RAM Kullanımı</span>
            <span class="text-white font-bold">{{ stats.memory_usage || 0 }}%</span>
          </div>
          <div class="w-full bg-dark-bg rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="usageColor(stats.memory_usage)"
              :style="{ width: `${stats.memory_usage || 0}%` }"
            ></div>
          </div>
        </div>

        <!-- Disk Usage -->
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-400 text-sm">Disk Kullanımı</span>
            <span class="text-white font-bold">{{ stats.disk_usage || 0 }}%</span>
          </div>
          <div class="w-full bg-dark-bg rounded-full h-2">
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
import axios from 'axios'

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
    const response = await axios.get('/api/admin/dashboard/stats')
    stats.value = response.data.stats || stats.value

    // Fetch recent users
    const usersResponse = await axios.get('/api/admin/users/recent?limit=5')
    recentUsers.value = usersResponse.data

    // Fetch recent servers
    const serversResponse = await axios.get('/api/admin/servers/recent?limit=5')
    recentServers.value = serversResponse.data
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
  if (usage >= 90) return 'bg-red-500'
  if (usage >= 75) return 'bg-yellow-500'
  return 'bg-green-500'
}
</script>

<style scoped>
.stat-card-large {
  @apply card hover:border-primary transition-colors duration-200;
}
</style>
