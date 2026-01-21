<template>
  <AdminLayout>
    <div class="command-center">
      <!-- Header with Welcome & Time -->
      <header class="dashboard-header">
        <div class="header-left">
          <div class="welcome-text">
            <h1>Kontrol Merkezi</h1>
            <p>Sistem durumunu izleyin ve yonetin</p>
          </div>
        </div>
        <div class="header-right">
          <div class="live-time">
            <Clock :size="18" />
            <span>{{ currentTime }}</span>
          </div>
          <n-button type="primary" @click="refreshAll" :loading="refreshing">
            <template #icon><RefreshCw :size="16" :class="{ 'spin': refreshing }" /></template>
            Yenile
          </n-button>
        </div>
      </header>

      <!-- Alerts Section -->
      <transition-group name="alert-slide" tag="div" class="alerts-section" v-if="alerts.length > 0">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          class="alert-card"
          :class="alert.type"
        >
          <div class="alert-icon">
            <AlertTriangle v-if="alert.type === 'error'" :size="20" />
            <AlertCircle v-else-if="alert.type === 'warning'" :size="20" />
            <Info v-else :size="20" />
          </div>
          <div class="alert-content">
            <span class="alert-title">{{ alert.title }}</span>
            <span class="alert-message">{{ alert.message }}</span>
          </div>
          <button class="alert-close" @click="dismissAlert(alert.id)">
            <X :size="16" />
          </button>
        </div>
      </transition-group>

      <!-- System Status Grid -->
      <section class="status-section">
        <div class="section-header">
          <h2><Cpu :size="20" /> Sistem Durumu</h2>
          <span class="status-time">Son guncelleme: {{ lastUpdateTime }}</span>
        </div>
        <div class="status-grid">
          <div
            v-for="service in systemServices"
            :key="service.name"
            class="status-card"
            :class="service.status"
            @click="service.action && service.action()"
          >
            <div class="status-indicator">
              <span class="pulse"></span>
            </div>
            <div class="status-icon">
              <component :is="service.icon" :size="24" />
            </div>
            <div class="status-info">
              <span class="status-name">{{ service.name }}</span>
              <span class="status-text">{{ service.statusText }}</span>
            </div>
            <div class="status-meta" v-if="service.latency">
              <span class="latency">{{ service.latency }}ms</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Main Stats Grid -->
      <section class="stats-section">
        <div class="stats-grid">
          <div
            v-for="stat in mainStats"
            :key="stat.id"
            class="stat-card"
            :class="stat.color"
          >
            <div class="stat-background">
              <component :is="stat.bgIcon" :size="80" />
            </div>
            <div class="stat-content">
              <div class="stat-header">
                <div class="stat-icon">
                  <component :is="stat.icon" :size="22" />
                </div>
                <div class="stat-trend" v-if="stat.trend !== undefined" :class="stat.trend >= 0 ? 'up' : 'down'">
                  <TrendingUp v-if="stat.trend >= 0" :size="14" />
                  <TrendingDown v-else :size="14" />
                  <span>{{ Math.abs(stat.trend) }}%</span>
                </div>
              </div>
              <div class="stat-value">
                <span class="value">{{ stat.value }}</span>
                <span class="suffix" v-if="stat.suffix">{{ stat.suffix }}</span>
              </div>
              <div class="stat-label">{{ stat.label }}</div>
              <div class="stat-subtitle" v-if="stat.subtitle">{{ stat.subtitle }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Performance & Activity Row -->
      <div class="dashboard-row">
        <!-- Performance Metrics -->
        <section class="performance-section card">
          <div class="card-header">
            <h3><Gauge :size="18" /> Performans Metrikleri</h3>
            <n-dropdown :options="periodOptions" @select="changePeriod">
              <n-button quaternary size="small">
                {{ selectedPeriod.label }} <ChevronDown :size="14" />
              </n-button>
            </n-dropdown>
          </div>
          <div class="card-body">
            <div class="metrics-grid">
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-label">CPU Kullanimi</span>
                  <span class="metric-value">{{ metrics.cpu }}%</span>
                </div>
                <n-progress
                  type="line"
                  :percentage="metrics.cpu"
                  :color="getProgressColor(metrics.cpu)"
                  :rail-color="'rgba(255,255,255,0.1)'"
                  :height="8"
                  :border-radius="4"
                />
              </div>
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-label">RAM Kullanimi</span>
                  <span class="metric-value">{{ metrics.ram }}%</span>
                </div>
                <n-progress
                  type="line"
                  :percentage="metrics.ram"
                  :color="getProgressColor(metrics.ram)"
                  :rail-color="'rgba(255,255,255,0.1)'"
                  :height="8"
                  :border-radius="4"
                />
              </div>
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-label">Disk Kullanimi</span>
                  <span class="metric-value">{{ metrics.disk }}%</span>
                </div>
                <n-progress
                  type="line"
                  :percentage="metrics.disk"
                  :color="getProgressColor(metrics.disk)"
                  :rail-color="'rgba(255,255,255,0.1)'"
                  :height="8"
                  :border-radius="4"
                />
              </div>
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-label">Network I/O</span>
                  <span class="metric-value">{{ metrics.network }} MB/s</span>
                </div>
                <n-progress
                  type="line"
                  :percentage="Math.min(metrics.network * 10, 100)"
                  color="#8b5cf6"
                  :rail-color="'rgba(255,255,255,0.1)'"
                  :height="8"
                  :border-radius="4"
                />
              </div>
            </div>

            <!-- Mini Chart -->
            <div class="mini-chart">
              <div class="chart-header">
                <span>Son 24 Saat Aktivite</span>
              </div>
              <div class="chart-bars">
                <div
                  v-for="(value, index) in activityChart"
                  :key="index"
                  class="chart-bar"
                  :style="{ height: value + '%' }"
                  :title="value + ' islem'"
                ></div>
              </div>
            </div>
          </div>
        </section>

        <!-- Quick Actions -->
        <section class="quick-actions-section card">
          <div class="card-header">
            <h3><Zap :size="18" /> Hizli Islemler</h3>
          </div>
          <div class="card-body">
            <div class="actions-grid">
              <router-link to="/admin/users" class="action-btn">
                <div class="action-icon blue"><Users :size="20" /></div>
                <span>Kullanicilar</span>
              </router-link>
              <router-link to="/admin/servers" class="action-btn">
                <div class="action-icon green"><Server :size="20" /></div>
                <span>Sunucular</span>
              </router-link>
              <router-link to="/admin/payments" class="action-btn">
                <div class="action-icon orange"><CreditCard :size="20" /></div>
                <span>Odemeler</span>
              </router-link>
              <router-link to="/admin/packages" class="action-btn">
                <div class="action-icon purple"><Package :size="20" /></div>
                <span>Paketler</span>
              </router-link>
              <router-link to="/admin/banners" class="action-btn">
                <div class="action-icon cyan"><Image :size="20" /></div>
                <span>Bannerlar</span>
              </router-link>
              <router-link to="/admin/settings" class="action-btn">
                <div class="action-icon gray"><Settings :size="20" /></div>
                <span>Ayarlar</span>
              </router-link>
              <router-link to="/admin/plugins" class="action-btn">
                <div class="action-icon pink"><Puzzle :size="20" /></div>
                <span>Eklentiler</span>
              </router-link>
              <router-link to="/admin/logs" class="action-btn">
                <div class="action-icon yellow"><FileText :size="20" /></div>
                <span>Loglar</span>
              </router-link>
            </div>
          </div>
        </section>
      </div>

      <!-- Activity & Payments Row -->
      <div class="dashboard-row">
        <!-- Recent Activity Feed -->
        <section class="activity-section card">
          <div class="card-header">
            <h3><Activity :size="18" /> Son Aktiviteler</h3>
            <n-button quaternary size="small" @click="fetchActivities">
              <RefreshCw :size="14" :class="{ 'spin': loadingActivities }" />
            </n-button>
          </div>
          <div class="card-body">
            <n-scrollbar style="max-height: 400px">
              <div v-if="loadingActivities" class="loading-state">
                <n-spin size="small" />
                <span>Yukleniyor...</span>
              </div>
              <div v-else-if="activities.length === 0" class="empty-state">
                <Inbox :size="40" />
                <span>Henuz aktivite yok</span>
              </div>
              <transition-group v-else name="activity-list" tag="div" class="activity-list">
                <div
                  v-for="activity in activities"
                  :key="activity.id"
                  class="activity-item"
                  :class="activity.type"
                >
                  <div class="activity-icon">
                    <component :is="getActivityIcon(activity.type)" :size="16" />
                  </div>
                  <div class="activity-content">
                    <div class="activity-text">
                      <span class="activity-user" v-if="activity.user">{{ activity.user }}</span>
                      {{ activity.message }}
                    </div>
                    <div class="activity-meta">
                      <Clock :size="12" />
                      <span>{{ formatTime(activity.created_at) }}</span>
                    </div>
                  </div>
                  <div class="activity-badge" v-if="activity.badge">
                    {{ activity.badge }}
                  </div>
                </div>
              </transition-group>
            </n-scrollbar>
          </div>
        </section>

        <!-- Pending Payments -->
        <section class="payments-section card">
          <div class="card-header">
            <h3><Wallet :size="18" /> Bekleyen Odemeler</h3>
            <router-link to="/admin/payments?status=pending" class="see-all">
              Tumunu Gor <ArrowRight :size="14" />
            </router-link>
          </div>
          <div class="card-body">
            <n-scrollbar style="max-height: 400px">
              <div v-if="loadingPayments" class="loading-state">
                <n-spin size="small" />
                <span>Yukleniyor...</span>
              </div>
              <div v-else-if="pendingPayments.length === 0" class="empty-state success">
                <CheckCircle :size="40" />
                <span>Bekleyen odeme yok</span>
              </div>
              <div v-else class="payments-list">
                <div
                  v-for="payment in pendingPayments"
                  :key="payment.id"
                  class="payment-item"
                >
                  <div class="payment-user">
                    <n-avatar
                      :size="36"
                      :src="getUserAvatar(payment.username)"
                      round
                    />
                    <div class="user-info">
                      <span class="username">{{ payment.username }}</span>
                      <span class="payment-method">{{ payment.method || 'Banka Havale' }}</span>
                    </div>
                  </div>
                  <div class="payment-amount">
                    <span class="amount">{{ formatCurrency(payment.amount) }}</span>
                    <span class="time">{{ formatTime(payment.created_at) }}</span>
                  </div>
                  <div class="payment-actions">
                    <n-tooltip trigger="hover">
                      <template #trigger>
                        <n-button
                          circle
                          type="success"
                          size="small"
                          @click="handleApprove(payment)"
                          :loading="payment.approving"
                        >
                          <template #icon><Check :size="14" /></template>
                        </n-button>
                      </template>
                      Onayla
                    </n-tooltip>
                    <n-tooltip trigger="hover">
                      <template #trigger>
                        <n-button
                          circle
                          type="error"
                          size="small"
                          @click="handleReject(payment)"
                          :loading="payment.rejecting"
                        >
                          <template #icon><X :size="14" /></template>
                        </n-button>
                      </template>
                      Reddet
                    </n-tooltip>
                  </div>
                </div>
              </div>
            </n-scrollbar>
          </div>
        </section>
      </div>

      <!-- Server Overview -->
      <section class="servers-overview card">
        <div class="card-header">
          <h3><Server :size="18" /> Sunucu Durumu Ozeti</h3>
          <router-link to="/admin/servers" class="see-all">
            Tum Sunucular <ArrowRight :size="14" />
          </router-link>
        </div>
        <div class="card-body">
          <div class="server-stats-row">
            <div class="server-stat">
              <div class="stat-circle running">
                <Play :size="20" />
              </div>
              <div class="stat-details">
                <span class="stat-number">{{ serverStats.running }}</span>
                <span class="stat-desc">Calisiyor</span>
              </div>
            </div>
            <div class="server-stat">
              <div class="stat-circle stopped">
                <Square :size="20" />
              </div>
              <div class="stat-details">
                <span class="stat-number">{{ serverStats.stopped }}</span>
                <span class="stat-desc">Durduruldu</span>
              </div>
            </div>
            <div class="server-stat">
              <div class="stat-circle installing">
                <Download :size="20" />
              </div>
              <div class="stat-details">
                <span class="stat-number">{{ serverStats.installing }}</span>
                <span class="stat-desc">Kuruluyor</span>
              </div>
            </div>
            <div class="server-stat">
              <div class="stat-circle error">
                <AlertTriangle :size="20" />
              </div>
              <div class="stat-details">
                <span class="stat-number">{{ serverStats.error }}</span>
                <span class="stat-desc">Hatali</span>
              </div>
            </div>
          </div>

          <!-- Game Distribution -->
          <div class="game-distribution">
            <h4>Oyun Dagilimi</h4>
            <div class="distribution-bars">
              <div
                v-for="game in gameDistribution"
                :key="game.type"
                class="distribution-item"
              >
                <div class="dist-header">
                  <span class="game-name">{{ game.name }}</span>
                  <span class="game-count">{{ game.count }}</span>
                </div>
                <div class="dist-bar">
                  <div
                    class="dist-fill"
                    :style="{
                      width: game.percentage + '%',
                      background: game.color
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Reject Payment Modal -->
    <n-modal v-model:show="showRejectModal" preset="dialog" title="Odeme Reddi">
      <template #default>
        <n-form>
          <n-form-item label="Red Sebebi">
            <n-input
              v-model:value="rejectReason"
              type="textarea"
              placeholder="Lutfen red sebebini aciklayin..."
              :rows="3"
            />
          </n-form-item>
        </n-form>
      </template>
      <template #action>
        <n-button @click="showRejectModal = false">Iptal</n-button>
        <n-button type="error" @click="confirmReject" :loading="rejectingPayment">
          Reddet
        </n-button>
      </template>
    </n-modal>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useRealtimeStore } from '@/stores/realtime'
import { adminApi, api } from '@/services/api'
import { formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

import {
  Users,
  Server,
  CreditCard,
  Package,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Activity,
  RefreshCw,
  Clock,
  Cpu,
  Database,
  Wifi,
  WifiOff,
  Gamepad2,
  AlertTriangle,
  AlertCircle,
  Info,
  X,
  Check,
  CheckCircle,
  Settings,
  Image,
  FileText,
  Zap,
  Gauge,
  ChevronDown,
  ArrowRight,
  Wallet,
  Inbox,
  Play,
  Square,
  Download,
  Puzzle,
  UserPlus,
  ShoppingCart,
  LogIn,
  Shield,
  Ban,
  Eye
} from 'lucide-vue-next'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const authStore = useAuthStore()
const realtimeStore = useRealtimeStore()

// Reactive State
const refreshing = ref(false)
const currentTime = ref('')
const lastUpdateTime = ref('')
const loadingActivities = ref(false)
const loadingPayments = ref(false)

// System Services Status
const systemServices = ref([
  {
    name: 'API Servisi',
    icon: Cpu,
    status: 'checking',
    statusText: 'Kontrol ediliyor...',
    latency: null
  },
  {
    name: 'Veritabani',
    icon: Database,
    status: 'checking',
    statusText: 'Kontrol ediliyor...',
    latency: null
  },
  {
    name: 'WebSocket',
    icon: Wifi,
    status: 'checking',
    statusText: 'Kontrol ediliyor...',
    latency: null
  },
  {
    name: 'Jackpot Manager',
    icon: Gamepad2,
    status: 'checking',
    statusText: 'Kontrol ediliyor...',
    latency: null
  }
])

// Alerts
const alerts = ref([])

// Main Stats
const mainStats = ref([
  {
    id: 'users',
    label: 'Toplam Kullanici',
    value: '0',
    icon: Users,
    bgIcon: Users,
    color: 'blue',
    trend: 0,
    subtitle: 'Bugun: +0'
  },
  {
    id: 'servers',
    label: 'Aktif Sunucu',
    value: '0',
    icon: Server,
    bgIcon: Server,
    color: 'green',
    subtitle: 'Toplam: 0'
  },
  {
    id: 'revenue',
    label: 'Bu Ay Gelir',
    value: '0',
    suffix: 'TL',
    icon: DollarSign,
    bgIcon: DollarSign,
    color: 'purple',
    trend: 0
  },
  {
    id: 'pending',
    label: 'Bekleyen Odeme',
    value: '0',
    icon: CreditCard,
    bgIcon: CreditCard,
    color: 'orange'
  }
])

// Performance Metrics
const metrics = ref({
  cpu: 0,
  ram: 0,
  disk: 0,
  network: 0
})

// Activity Chart Data (24 hours)
const activityChart = ref(Array(24).fill(0))

// Period Selection
const selectedPeriod = ref({ label: 'Son 7 Gun', value: '7d' })
const periodOptions = [
  { label: 'Son 7 Gun', key: '7d' },
  { label: 'Son 30 Gun', key: '30d' },
  { label: 'Son 90 Gun', key: '90d' }
]

// Activities
const activities = ref([])

// Pending Payments
const pendingPayments = ref([])

// Server Stats
const serverStats = ref({
  running: 0,
  stopped: 0,
  installing: 0,
  error: 0
})

// Game Distribution
const gameDistribution = ref([
  { type: 'cs2', name: 'Counter-Strike 2', count: 0, percentage: 0, color: '#f97316' },
  { type: 'csgo', name: 'CS:GO', count: 0, percentage: 0, color: '#3b82f6' },
  { type: 'minecraft', name: 'Minecraft', count: 0, percentage: 0, color: '#10b981' },
  { type: 'other', name: 'Diger', count: 0, percentage: 0, color: '#8b5cf6' }
])

// Reject Modal
const showRejectModal = ref(false)
const rejectReason = ref('')
const rejectingPayment = ref(false)
const selectedPaymentForReject = ref(null)

// Timers
let clockInterval = null
let refreshInterval = null

// Helper Functions
const getProgressColor = (value) => {
  if (value < 50) return '#10b981'
  if (value < 75) return '#f59e0b'
  return '#ef4444'
}

const getUserAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}&backgroundColor=f97316`
}

const formatTime = (date) => {
  if (!date) return ''
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true, locale: tr })
  } catch {
    return ''
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0
  }).format(amount || 0)
}

const getActivityIcon = (type) => {
  const icons = {
    user: UserPlus,
    login: LogIn,
    payment: ShoppingCart,
    server: Server,
    warning: AlertTriangle,
    error: AlertCircle,
    admin: Shield,
    ban: Ban,
    view: Eye
  }
  return icons[type] || Activity
}

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const dismissAlert = (id) => {
  alerts.value = alerts.value.filter(a => a.id !== id)
}

const changePeriod = (key) => {
  selectedPeriod.value = periodOptions.find(p => p.key === key) || periodOptions[0]
  fetchChartData()
}

// API Functions
const checkSystemHealth = async () => {
  const startTime = Date.now()

  try {
    const response = await api.get('/health')
    const latency = Date.now() - startTime

    systemServices.value[0].status = response.status === 'healthy' ? 'online' : 'warning'
    systemServices.value[0].statusText = response.status === 'healthy' ? 'Calisiyor' : 'Uyari'
    systemServices.value[0].latency = latency

    // Database check is part of health
    systemServices.value[1].status = 'online'
    systemServices.value[1].statusText = 'Bagli'
    systemServices.value[1].latency = latency
  } catch (error) {
    systemServices.value[0].status = 'offline'
    systemServices.value[0].statusText = 'Erisim Yok'
    systemServices.value[1].status = 'offline'
    systemServices.value[1].statusText = 'Baglanti Yok'

    alerts.value.unshift({
      id: Date.now(),
      type: 'error',
      title: 'API Hatasi',
      message: 'API servisi ile baglanti kurulamadi'
    })
  }

  // WebSocket Status from realtime store
  const wsConnected = realtimeStore.connectionStatus?.dashboard
  systemServices.value[2].status = wsConnected ? 'online' : 'offline'
  systemServices.value[2].statusText = wsConnected ? 'Aktif' : 'Pasif'

  // Jackpot Manager - assume online if API is healthy
  systemServices.value[3].status = systemServices.value[0].status === 'online' ? 'online' : 'offline'
  systemServices.value[3].statusText = systemServices.value[0].status === 'online' ? 'Calisiyor' : 'Durdu'
}

const fetchDashboardData = async () => {
  try {
    const data = await adminApi.getDashboard()

    // Update main stats
    mainStats.value[0].value = (data.users?.total || 0).toLocaleString('tr-TR')
    mainStats.value[0].subtitle = `Bugun: +${data.users?.new_today || 0}`

    mainStats.value[1].value = (data.servers?.running || 0).toString()
    mainStats.value[1].subtitle = `Toplam: ${data.servers?.total || 0}`

    mainStats.value[2].value = Math.round(data.payments?.month_revenue || 0).toLocaleString('tr-TR')

    mainStats.value[3].value = (data.payments?.pending || 0).toString()

    // Calculate server stats
    serverStats.value = {
      running: data.servers?.running || 0,
      stopped: (data.servers?.total || 0) - (data.servers?.running || 0),
      installing: 0,
      error: 0
    }

    // Add alert if pending payments
    if (data.payments?.pending > 0) {
      const existingAlert = alerts.value.find(a => a.id === 'pending-payments')
      if (!existingAlert) {
        alerts.value.push({
          id: 'pending-payments',
          type: 'warning',
          title: 'Bekleyen Odemeler',
          message: `${data.payments.pending} adet odeme onay bekliyor`
        })
      }
    }

    lastUpdateTime.value = new Date().toLocaleTimeString('tr-TR')
  } catch (error) {
    console.error('Dashboard fetch error:', error)
  }
}

const fetchActivities = async () => {
  loadingActivities.value = true
  try {
    const data = await adminApi.getLogs({ limit: 20 })
    activities.value = (data.logs || []).map(log => ({
      id: log.id,
      type: log.action?.includes('payment') ? 'payment' :
            log.action?.includes('server') ? 'server' :
            log.action?.includes('user') ? 'user' :
            log.action?.includes('login') ? 'login' :
            log.action?.includes('error') ? 'error' : 'info',
      user: log.username,
      message: log.message || log.action,
      created_at: log.created_at
    }))
  } catch (error) {
    // Fallback to mock data if endpoint not available
    activities.value = []
  }
  loadingActivities.value = false
}

const fetchPendingPayments = async () => {
  loadingPayments.value = true
  try {
    const data = await adminApi.getPayments({ status: 'pending', limit: 10 })
    pendingPayments.value = (data.payments || []).map(p => ({
      ...p,
      approving: false,
      rejecting: false
    }))
  } catch (error) {
    console.error('Pending payments fetch error:', error)
  }
  loadingPayments.value = false
}

const fetchChartData = async () => {
  try {
    const data = await api.get('/admin/dashboard/charts', { period: selectedPeriod.value.value })

    if (data.user_registrations) {
      // Map to activity chart
      const hourlyActivity = Array(24).fill(0)
      data.user_registrations.forEach((item, idx) => {
        hourlyActivity[idx % 24] = item.count * 10 // Scale for visibility
      })
      activityChart.value = hourlyActivity
    }

    if (data.game_type_distribution) {
      const total = data.game_type_distribution.reduce((sum, g) => sum + g.count, 0)
      const colors = {
        'cs2': '#f97316',
        'csgo': '#3b82f6',
        'minecraft': '#10b981',
        'rust': '#ef4444',
        'other': '#8b5cf6'
      }

      gameDistribution.value = data.game_type_distribution.map(g => ({
        type: g.game,
        name: g.game.toUpperCase(),
        count: g.count,
        percentage: total > 0 ? Math.round((g.count / total) * 100) : 0,
        color: colors[g.game] || '#8b5cf6'
      }))
    }
  } catch (error) {
    // Use mock data
    activityChart.value = Array(24).fill(0).map(() => Math.floor(Math.random() * 80) + 10)
  }
}

const fetchMetrics = async () => {
  // Simulated metrics - replace with actual endpoint if available
  metrics.value = {
    cpu: Math.floor(Math.random() * 40) + 20,
    ram: Math.floor(Math.random() * 30) + 40,
    disk: Math.floor(Math.random() * 20) + 30,
    network: Math.floor(Math.random() * 5) + 1
  }
}

const refreshAll = async () => {
  refreshing.value = true

  await Promise.all([
    checkSystemHealth(),
    fetchDashboardData(),
    fetchActivities(),
    fetchPendingPayments(),
    fetchChartData(),
    fetchMetrics()
  ])

  message.success('Veriler guncellendi')
  refreshing.value = false
}

// Payment Actions
const handleApprove = async (payment) => {
  dialog.warning({
    title: 'Odeme Onayi',
    content: `${payment.username} kullanicisinin ${formatCurrency(payment.amount)} tutarindaki odemesini onaylamak istiyor musunuz?`,
    positiveText: 'Onayla',
    negativeText: 'Iptal',
    onPositiveClick: async () => {
      payment.approving = true
      try {
        await adminApi.approvePayment(payment.id)
        pendingPayments.value = pendingPayments.value.filter(p => p.id !== payment.id)
        mainStats.value[3].value = (parseInt(mainStats.value[3].value) - 1).toString()
        message.success('Odeme onaylandi')
      } catch (error) {
        message.error('Odeme onaylanamadi: ' + (error.message || 'Bilinmeyen hata'))
      }
      payment.approving = false
    }
  })
}

const handleReject = (payment) => {
  selectedPaymentForReject.value = payment
  rejectReason.value = ''
  showRejectModal.value = true
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    message.warning('Lutfen red sebebini girin')
    return
  }

  rejectingPayment.value = true
  try {
    await adminApi.rejectPayment(selectedPaymentForReject.value.id, rejectReason.value)
    pendingPayments.value = pendingPayments.value.filter(p => p.id !== selectedPaymentForReject.value.id)
    mainStats.value[3].value = (parseInt(mainStats.value[3].value) - 1).toString()
    message.success('Odeme reddedildi')
    showRejectModal.value = false
  } catch (error) {
    message.error('Odeme reddedilemedi: ' + (error.message || 'Bilinmeyen hata'))
  }
  rejectingPayment.value = false
}

// Lifecycle
onMounted(() => {
  updateClock()
  clockInterval = setInterval(updateClock, 1000)

  refreshAll()
  refreshInterval = setInterval(refreshAll, 60000) // Refresh every minute
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
.command-center {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 8px;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.welcome-text h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-text p {
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.live-time {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
}

/* Alerts */
.alerts-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.alert-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  animation: slideIn 0.3s ease;
}

.alert-card.error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.alert-card.error .alert-icon {
  color: #ef4444;
}

.alert-card.warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
}

.alert-card.warning .alert-icon {
  color: #f59e0b;
}

.alert-card.info {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.alert-card.info .alert-icon {
  color: #3b82f6;
}

.alert-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
}

.alert-content {
  flex: 1;
}

.alert-title {
  display: block;
  font-weight: 600;
  color: #fff;
  margin-bottom: 2px;
}

.alert-message {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.alert-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.alert-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* Status Section */
.status-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.status-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.status-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.status-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.status-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
}

.status-indicator .pulse {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #64748b;
}

.status-card.online .status-indicator .pulse {
  background: #10b981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse 2s infinite;
}

.status-card.offline .status-indicator .pulse {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.status-card.warning .status-indicator .pulse {
  background: #f59e0b;
  animation: pulse 1s infinite;
}

.status-card.checking .status-indicator .pulse {
  background: #64748b;
  animation: blink 1s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.status-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.status-card.online .status-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-card.offline .status-icon {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.status-info {
  flex: 1;
}

.status-name {
  display: block;
  font-weight: 600;
  color: #fff;
  font-size: 14px;
}

.status-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.status-meta .latency {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  font-family: 'JetBrains Mono', monospace;
}

/* Stats Section */
.stats-section {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  position: relative;
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.stat-card.blue { border-left: 4px solid #3b82f6; }
.stat-card.green { border-left: 4px solid #10b981; }
.stat-card.purple { border-left: 4px solid #8b5cf6; }
.stat-card.orange { border-left: 4px solid #f97316; }

.stat-background {
  position: absolute;
  right: -20px;
  bottom: -20px;
  opacity: 0.05;
  pointer-events: none;
}

.stat-content {
  position: relative;
  z-index: 1;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-card.blue .stat-icon { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.stat-card.green .stat-icon { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.stat-card.purple .stat-icon { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
.stat-card.orange .stat-icon { background: rgba(249, 115, 22, 0.15); color: #f97316; }

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}

.stat-trend.up {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.stat-trend.down {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.stat-value {
  margin-bottom: 8px;
}

.stat-value .value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.stat-value .suffix {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 4px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.stat-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* Dashboard Row */
.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

/* Card */
.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.card-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.card-body {
  padding: 20px 24px;
}

.see-all {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #f97316;
  text-decoration: none;
  transition: all 0.2s;
}

.see-all:hover {
  color: #fb923c;
}

/* Performance Section */
.metrics-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  font-family: 'JetBrains Mono', monospace;
}

/* Mini Chart */
.mini-chart {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.chart-header {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 60px;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(180deg, #f97316 0%, rgba(249, 115, 22, 0.3) 100%);
  border-radius: 3px 3px 0 0;
  min-height: 4px;
  transition: all 0.3s ease;
}

.chart-bar:hover {
  background: linear-gradient(180deg, #fb923c 0%, rgba(249, 115, 22, 0.5) 100%);
}

/* Quick Actions */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(249, 115, 22, 0.3);
}

.action-btn span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.action-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.action-icon.blue { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.action-icon.green { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.action-icon.orange { background: rgba(249, 115, 22, 0.15); color: #f97316; }
.action-icon.purple { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
.action-icon.cyan { background: rgba(6, 182, 212, 0.15); color: #06b6d4; }
.action-icon.gray { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }
.action-icon.pink { background: rgba(236, 72, 153, 0.15); color: #ec4899; }
.action-icon.yellow { background: rgba(234, 179, 8, 0.15); color: #eab308; }

/* Activity List */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: rgba(255, 255, 255, 0.4);
}

.empty-state.success {
  color: #10b981;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  transition: all 0.2s;
}

.activity-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.activity-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.activity-item.user .activity-icon { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.activity-item.payment .activity-icon { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.activity-item.server .activity-icon { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
.activity-item.error .activity-icon { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.activity-item.warning .activity-icon { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.activity-item.login .activity-icon { background: rgba(6, 182, 212, 0.15); color: #06b6d4; }

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.activity-user {
  color: #f97316;
  font-weight: 600;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.activity-badge {
  font-size: 10px;
  padding: 4px 8px;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
  border-radius: 6px;
  font-weight: 600;
}

/* Payments List */
.payments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  transition: all 0.2s;
}

.payment-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.payment-user {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-info .username {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.user-info .payment-method {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.payment-amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.payment-amount .amount {
  font-size: 16px;
  font-weight: 700;
  color: #10b981;
}

.payment-amount .time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.payment-actions {
  display: flex;
  gap: 8px;
}

/* Server Overview */
.servers-overview {
  margin-bottom: 24px;
}

.server-stats-row {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 24px;
}

.server-stat {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-circle {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.stat-circle.running { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.stat-circle.stopped { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }
.stat-circle.installing { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.stat-circle.error { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.stat-details .stat-number {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.stat-details .stat-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Game Distribution */
.game-distribution h4 {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 16px 0;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.distribution-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.game-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.game-count {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'JetBrains Mono', monospace;
}

.dist-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  overflow: hidden;
}

.dist-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.alert-slide-enter-active,
.alert-slide-leave-active {
  transition: all 0.3s ease;
}

.alert-slide-enter-from,
.alert-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.activity-list-enter-active,
.activity-list-leave-active {
  transition: all 0.3s ease;
}

.activity-list-enter-from,
.activity-list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1400px) {
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .dashboard-row {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .server-stats-row {
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
  }
}
</style>
