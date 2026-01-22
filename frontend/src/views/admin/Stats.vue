<template>
  <AdminLayout>
    <div class="stats-page">
      <!-- Header -->
      <header class="page-header">
        <div class="header-left">
          <h1>Platform Istatistikleri</h1>
          <p>Kullanici ve Steam baglanti istatistikleri</p>
        </div>
        <div class="header-right">
          <n-button type="primary" @click="refreshAll" :loading="loading">
            <template #icon><RefreshCw :size="16" :class="{ 'spin': loading }" /></template>
            Yenile
          </n-button>
        </div>
      </header>

      <!-- Overview Cards -->
      <section class="overview-section">
        <div class="stats-grid">
          <div class="stat-card users">
            <div class="stat-background">
              <Users :size="80" />
            </div>
            <div class="stat-content">
              <div class="stat-icon">
                <Users :size="24" />
              </div>
              <div class="stat-value">{{ formatNumber(overview.total_users) }}</div>
              <div class="stat-label">Toplam Kullanici</div>
              <div class="stat-meta">
                <span class="meta-item">
                  <TrendingUp :size="14" />
                  +{{ overview.registrations?.today || 0 }} bugun
                </span>
              </div>
            </div>
          </div>

          <div class="stat-card steam">
            <div class="stat-background">
              <Gamepad2 :size="80" />
            </div>
            <div class="stat-content">
              <div class="stat-icon steam-icon">
                <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                  <path d="M12 2C6.477 2 2 6.477 2 12c0 4.832 3.437 8.871 8 9.8V14.6l-1.5-1.4A3.5 3.5 0 1 1 12 6.5c1.933 0 3.5 1.567 3.5 3.5 0 .623-.163 1.21-.45 1.718L22 14.293V4.707L17.293 0H4.707L0 4.707v14.586L4.707 24h14.586L24 19.293V4.707L22 2.707V12l-3.5-1.5A3.5 3.5 0 0 0 12 2z"/>
                </svg>
              </div>
              <div class="stat-value">{{ formatNumber(overview.steam_linked) }}</div>
              <div class="stat-label">Steam Bagli</div>
              <div class="stat-percent">%{{ overview.steam_percentage || 0 }}</div>
            </div>
          </div>

          <div class="stat-card verified">
            <div class="stat-background">
              <Mail :size="80" />
            </div>
            <div class="stat-content">
              <div class="stat-icon">
                <MailCheck :size="24" />
              </div>
              <div class="stat-value">{{ formatNumber(overview.email_verified) }}</div>
              <div class="stat-label">Email Dogrulanmis</div>
              <div class="stat-percent">%{{ overview.email_verified_percentage || 0 }}</div>
            </div>
          </div>

          <div class="stat-card security">
            <div class="stat-background">
              <Shield :size="80" />
            </div>
            <div class="stat-content">
              <div class="stat-icon">
                <ShieldCheck :size="24" />
              </div>
              <div class="stat-value">{{ formatNumber(overview.two_fa_enabled) }}</div>
              <div class="stat-label">2FA Aktif</div>
              <div class="stat-percent">%{{ overview.two_fa_percentage || 0 }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Charts Section -->
      <section class="charts-section">
        <div class="charts-row">
          <!-- Registration Chart -->
          <div class="chart-card">
            <div class="chart-header">
              <h3><TrendingUp :size="18" /> Kayit Grafigi</h3>
              <n-select
                v-model:value="selectedDays"
                :options="dayOptions"
                size="small"
                style="width: 120px"
                @update:value="fetchRegistrationStats"
              />
            </div>
            <div class="chart-content">
              <div class="chart-legend">
                <div class="legend-item">
                  <span class="legend-color total"></span>
                  <span>Toplam</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color steam"></span>
                  <span>Steam</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color non-steam"></span>
                  <span>Normal</span>
                </div>
              </div>
              <div class="chart-bars-container">
                <div class="chart-bars" v-if="registrationData.daily_registrations?.length">
                  <div
                    v-for="(item, index) in registrationData.daily_registrations.slice(-14)"
                    :key="index"
                    class="chart-bar-group"
                    :title="`${item.date}: ${item.count} kayit`"
                  >
                    <div class="bar-wrapper">
                      <div
                        class="bar total-bar"
                        :style="{ height: getBarHeight(item.count) + '%' }"
                      ></div>
                      <div
                        class="bar steam-bar"
                        :style="{ height: getBarHeight(registrationData.steam_registrations?.[index]?.count || 0) + '%' }"
                      ></div>
                    </div>
                    <span class="bar-label">{{ formatDate(item.date) }}</span>
                  </div>
                </div>
                <div v-else class="no-data">
                  <BarChart3 :size="40" />
                  <span>Veri bulunamadi</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Steam vs Non-Steam Pie -->
          <div class="chart-card">
            <div class="chart-header">
              <h3><PieChart :size="18" /> Steam Dagilimi</h3>
            </div>
            <div class="chart-content pie-chart-content">
              <div class="pie-chart-wrapper">
                <div class="pie-chart">
                  <div
                    class="pie-segment steam-segment"
                    :style="{ '--percentage': steamBreakdown.steam_percentage || 0 }"
                  ></div>
                  <div class="pie-center">
                    <span class="pie-value">%{{ steamBreakdown.steam_percentage || 0 }}</span>
                    <span class="pie-label">Steam</span>
                  </div>
                </div>
              </div>
              <div class="pie-legend">
                <div class="pie-legend-item">
                  <div class="pie-legend-color steam"></div>
                  <div class="pie-legend-info">
                    <span class="pie-legend-label">Steam Bagli</span>
                    <span class="pie-legend-value">{{ formatNumber(steamBreakdown.steam_linked) }}</span>
                  </div>
                </div>
                <div class="pie-legend-item">
                  <div class="pie-legend-color non-steam"></div>
                  <div class="pie-legend-info">
                    <span class="pie-legend-label">Normal Kayit</span>
                    <span class="pie-legend-value">{{ formatNumber(steamBreakdown.non_steam_users) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Metrics -->
        <div class="activity-section">
          <div class="chart-card full-width">
            <div class="chart-header">
              <h3><Activity :size="18" /> Aktivite Metrikleri (Son {{ activityDays }} Gun)</h3>
              <n-select
                v-model:value="activityDays"
                :options="activityDayOptions"
                size="small"
                style="width: 120px"
                @update:value="fetchActivityStats"
              />
            </div>
            <div class="activity-grid">
              <div class="activity-card">
                <div class="activity-icon users">
                  <UserCheck :size="20" />
                </div>
                <div class="activity-info">
                  <span class="activity-value">{{ formatNumber(activityData.user_activity?.active_users) }}</span>
                  <span class="activity-label">Aktif Kullanici</span>
                </div>
                <div class="activity-breakdown">
                  <div class="breakdown-item">
                    <span class="breakdown-label">Steam:</span>
                    <span class="breakdown-value">{{ formatNumber(activityData.user_activity?.steam_active) }}</span>
                  </div>
                  <div class="breakdown-item">
                    <span class="breakdown-label">Diger:</span>
                    <span class="breakdown-value">{{ formatNumber(activityData.user_activity?.non_steam_active) }}</span>
                  </div>
                </div>
              </div>

              <div class="activity-card">
                <div class="activity-icon logins">
                  <LogIn :size="20" />
                </div>
                <div class="activity-info">
                  <span class="activity-value">{{ formatNumber(activityData.user_activity?.total_logins) }}</span>
                  <span class="activity-label">Toplam Giris</span>
                </div>
              </div>

              <div class="activity-card">
                <div class="activity-icon forum">
                  <MessageSquare :size="20" />
                </div>
                <div class="activity-info">
                  <span class="activity-value">{{ formatNumber((activityData.forum_activity?.new_topics || 0) + (activityData.forum_activity?.new_posts || 0)) }}</span>
                  <span class="activity-label">Forum Aktivitesi</span>
                </div>
                <div class="activity-breakdown">
                  <div class="breakdown-item">
                    <span class="breakdown-label">Konu:</span>
                    <span class="breakdown-value">{{ formatNumber(activityData.forum_activity?.new_topics) }}</span>
                  </div>
                  <div class="breakdown-item">
                    <span class="breakdown-label">Yorum:</span>
                    <span class="breakdown-value">{{ formatNumber(activityData.forum_activity?.new_posts) }}</span>
                  </div>
                </div>
              </div>

              <div class="activity-card">
                <div class="activity-icon revenue">
                  <DollarSign :size="20" />
                </div>
                <div class="activity-info">
                  <span class="activity-value">{{ formatCurrency(activityData.financial_activity?.total_revenue) }}</span>
                  <span class="activity-label">Toplam Gelir</span>
                </div>
                <div class="activity-breakdown">
                  <div class="breakdown-item">
                    <span class="breakdown-label">Steam:</span>
                    <span class="breakdown-value">{{ formatCurrency(activityData.financial_activity?.steam_user_revenue) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Steam Engagement Section -->
      <section class="engagement-section">
        <div class="chart-card full-width">
          <div class="chart-header">
            <h3><Target :size="18" /> Steam Kullanici Analizi</h3>
          </div>
          <div class="engagement-grid">
            <div class="engagement-stat">
              <div class="engagement-circle paying">
                <span class="engagement-value">{{ steamBreakdown.steam_engagement?.paying_users || 0 }}</span>
              </div>
              <span class="engagement-label">Odeme Yapan Steam Kullanicisi</span>
              <span class="engagement-percent">%{{ steamBreakdown.steam_engagement?.paying_percentage || 0 }}</span>
            </div>
            <div class="engagement-stat">
              <div class="engagement-circle servers">
                <span class="engagement-value">{{ steamBreakdown.steam_engagement?.server_owners || 0 }}</span>
              </div>
              <span class="engagement-label">Sunucu Sahibi Steam Kullanicisi</span>
            </div>
            <div class="engagement-stat">
              <div class="engagement-circle verified">
                <span class="engagement-value">{{ steamBreakdown.steam_with_verified_email || 0 }}</span>
              </div>
              <span class="engagement-label">Email Dogrulamis Steam Kullanicisi</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent Users Table -->
      <section class="recent-users-section">
        <div class="chart-card full-width">
          <div class="chart-header">
            <h3><UserPlus :size="18" /> Son Kayit Olan Kullanicilar</h3>
            <div class="header-actions">
              <n-switch v-model:value="steamOnlyFilter" size="small">
                <template #checked>Steam</template>
                <template #unchecked>Tumu</template>
              </n-switch>
              <n-button quaternary size="small" @click="fetchRecentUsers">
                <RefreshCw :size="14" />
              </n-button>
            </div>
          </div>
          <div class="table-container">
            <n-data-table
              :columns="userColumns"
              :data="recentUsers"
              :loading="loadingUsers"
              :bordered="false"
              :single-line="false"
              size="small"
              striped
            />
          </div>
        </div>
      </section>

      <!-- Top Spenders Table -->
      <section class="top-spenders-section">
        <div class="chart-card full-width">
          <div class="chart-header">
            <h3><Crown :size="18" /> En Cok Harcama Yapanlar (Son 30 Gun)</h3>
          </div>
          <div class="table-container">
            <n-data-table
              :columns="spenderColumns"
              :data="topSpenders"
              :loading="loadingSpenders"
              :bordered="false"
              :single-line="false"
              size="small"
              striped
            />
          </div>
        </div>
      </section>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch, h } from 'vue'
import { useMessage } from 'naive-ui'
import { NTag, NAvatar, NTooltip } from 'naive-ui'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { api } from '@/services/api'
import { formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

import {
  Users,
  Gamepad2,
  Mail,
  MailCheck,
  Shield,
  ShieldCheck,
  RefreshCw,
  TrendingUp,
  PieChart,
  Activity,
  UserCheck,
  LogIn,
  MessageSquare,
  DollarSign,
  Target,
  UserPlus,
  Crown,
  BarChart3,
  CheckCircle,
  XCircle,
  Server
} from 'lucide-vue-next'

const message = useMessage()

// Loading states
const loading = ref(false)
const loadingUsers = ref(false)
const loadingSpenders = ref(false)

// Data
const overview = ref({})
const steamBreakdown = ref({})
const registrationData = ref({})
const activityData = ref({})
const recentUsers = ref([])
const topSpenders = ref([])

// Filters
const selectedDays = ref(30)
const activityDays = ref(7)
const steamOnlyFilter = ref(false)

const dayOptions = [
  { label: '7 Gun', value: 7 },
  { label: '14 Gun', value: 14 },
  { label: '30 Gun', value: 30 },
  { label: '90 Gun', value: 90 }
]

const activityDayOptions = [
  { label: '7 Gun', value: 7 },
  { label: '14 Gun', value: 14 },
  { label: '30 Gun', value: 30 }
]

// Table columns
const userColumns = [
  {
    title: 'Kullanici',
    key: 'username',
    render(row) {
      return h('div', { class: 'user-cell' }, [
        h(NAvatar, {
          size: 32,
          round: true,
          src: `https://api.dicebear.com/7.x/initials/svg?seed=${row.username}&backgroundColor=f97316`
        }),
        h('div', { class: 'user-info' }, [
          h('span', { class: 'username' }, row.username),
          h('span', { class: 'email' }, row.email)
        ])
      ])
    }
  },
  {
    title: 'Steam',
    key: 'has_steam',
    width: 100,
    render(row) {
      if (row.has_steam) {
        return h(NTooltip, { trigger: 'hover' }, {
          trigger: () => h(NTag, { type: 'info', size: 'small', round: true }, { default: () => 'Steam' }),
          default: () => row.steam_id
        })
      }
      return h(NTag, { type: 'default', size: 'small', round: true }, { default: () => 'Yok' })
    }
  },
  {
    title: 'Email',
    key: 'email_verified',
    width: 100,
    render(row) {
      return row.email_verified
        ? h(CheckCircle, { size: 18, color: '#10b981' })
        : h(XCircle, { size: 18, color: '#64748b' })
    }
  },
  {
    title: 'Durum',
    key: 'status',
    width: 100,
    render(row) {
      const statusMap = {
        active: { type: 'success', label: 'Aktif' },
        banned: { type: 'error', label: 'Banlı' },
        suspended: { type: 'warning', label: 'Askıda' },
        pending: { type: 'default', label: 'Beklemede' }
      }
      const status = statusMap[row.status] || statusMap.pending
      return h(NTag, { type: status.type, size: 'small' }, { default: () => status.label })
    }
  },
  {
    title: 'Bakiye',
    key: 'balance',
    width: 120,
    render(row) {
      return h('div', { class: 'balance-cell' }, [
        h('span', { class: 'balance-real' }, formatCurrency(row.balance)),
        h('span', { class: 'balance-coin' }, `${row.balance_coin || 0} Coin`)
      ])
    }
  },
  {
    title: 'Kayit Tarihi',
    key: 'created_at',
    width: 150,
    render(row) {
      if (!row.created_at) return '-'
      return formatTimeAgo(row.created_at)
    }
  }
]

const spenderColumns = [
  {
    title: 'Sira',
    key: 'rank',
    width: 60,
    render(row, index) {
      const medals = ['gold', 'silver', 'bronze']
      if (index < 3) {
        return h('div', { class: `rank-medal ${medals[index]}` }, index + 1)
      }
      return h('span', { class: 'rank-number' }, index + 1)
    }
  },
  {
    title: 'Kullanici',
    key: 'username',
    render(row) {
      return h('div', { class: 'user-cell' }, [
        h(NAvatar, {
          size: 32,
          round: true,
          src: `https://api.dicebear.com/7.x/initials/svg?seed=${row.username}&backgroundColor=f97316`
        }),
        h('div', { class: 'user-info' }, [
          h('span', { class: 'username' }, row.username),
          row.has_steam ? h(NTag, { type: 'info', size: 'tiny', round: true }, { default: () => 'Steam' }) : null
        ])
      ])
    }
  },
  {
    title: 'Toplam Harcama',
    key: 'total_spent',
    width: 150,
    render(row) {
      return h('span', { class: 'total-spent' }, formatCurrency(row.total_spent))
    }
  },
  {
    title: 'Islem Sayisi',
    key: 'payment_count',
    width: 120,
    render(row) {
      return h(NTag, { type: 'default', size: 'small' }, { default: () => `${row.payment_count} islem` })
    }
  }
]

// Helper functions
const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return num.toLocaleString('tr-TR')
}

const formatCurrency = (amount) => {
  if (amount === undefined || amount === null) return '0 TL'
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0
  }).format(amount)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getDate()}/${date.getMonth() + 1}`
}

const formatTimeAgo = (dateStr) => {
  if (!dateStr) return '-'
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true, locale: tr })
  } catch {
    return dateStr
  }
}

const getBarHeight = (value) => {
  if (!registrationData.value.daily_registrations?.length) return 0
  const maxValue = Math.max(...registrationData.value.daily_registrations.map(d => d.count)) || 1
  return Math.max((value / maxValue) * 100, 5)
}

// API functions
const fetchOverview = async () => {
  try {
    const data = await api.get('/admin/stats/users/overview')
    overview.value = data
  } catch (error) {
    console.error('Overview fetch error:', error)
  }
}

const fetchSteamBreakdown = async () => {
  try {
    const data = await api.get('/admin/stats/users/steam-breakdown')
    steamBreakdown.value = data
  } catch (error) {
    console.error('Steam breakdown fetch error:', error)
  }
}

const fetchRegistrationStats = async () => {
  try {
    const data = await api.get('/admin/stats/users/registrations', { days: selectedDays.value })
    registrationData.value = data
  } catch (error) {
    console.error('Registration stats fetch error:', error)
  }
}

const fetchActivityStats = async () => {
  try {
    const data = await api.get('/admin/stats/activity/overview', { days: activityDays.value })
    activityData.value = data
  } catch (error) {
    console.error('Activity stats fetch error:', error)
  }
}

const fetchRecentUsers = async () => {
  loadingUsers.value = true
  try {
    const data = await api.get('/admin/stats/users/recent', { limit: 20, steam_only: steamOnlyFilter.value })
    recentUsers.value = data.users || []
  } catch (error) {
    console.error('Recent users fetch error:', error)
  }
  loadingUsers.value = false
}

const fetchTopSpenders = async () => {
  loadingSpenders.value = true
  try {
    const data = await api.get('/admin/stats/users/top-spenders', { limit: 10, days: 30 })
    topSpenders.value = data.top_spenders || []
  } catch (error) {
    console.error('Top spenders fetch error:', error)
  }
  loadingSpenders.value = false
}

const refreshAll = async () => {
  loading.value = true
  await Promise.all([
    fetchOverview(),
    fetchSteamBreakdown(),
    fetchRegistrationStats(),
    fetchActivityStats(),
    fetchRecentUsers(),
    fetchTopSpenders()
  ])
  message.success('Istatistikler guncellendi')
  loading.value = false
}

// Watch for filter changes
watch(steamOnlyFilter, () => {
  fetchRecentUsers()
})

// Lifecycle
onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.stats-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 8px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  font-size: 14px;
}

/* Overview Section */
.overview-section {
  margin-bottom: 32px;
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

.stat-card.users {
  border-left: 4px solid #3b82f6;
}

.stat-card.steam {
  border-left: 4px solid #1b2838;
  background: linear-gradient(135deg, rgba(27, 40, 56, 0.3) 0%, rgba(255, 255, 255, 0.03) 100%);
}

.stat-card.verified {
  border-left: 4px solid #10b981;
}

.stat-card.security {
  border-left: 4px solid #8b5cf6;
}

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

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  margin-bottom: 16px;
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.stat-card.steam .stat-icon {
  background: linear-gradient(135deg, rgba(27, 40, 56, 0.8) 0%, rgba(102, 192, 244, 0.3) 100%);
  color: #66c0f4;
}

.stat-card.steam .stat-icon.steam-icon svg {
  width: 24px;
  height: 24px;
  fill: #66c0f4;
}

.stat-card.verified .stat-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.stat-card.security .stat-icon {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.stat-percent {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(102, 192, 244, 0.15);
  color: #66c0f4;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.stat-card.verified .stat-percent {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.stat-card.security .stat-percent {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.stat-meta {
  margin-top: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #10b981;
}

/* Charts Section */
.charts-section {
  margin-bottom: 32px;
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  overflow: hidden;
}

.chart-card.full-width {
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.chart-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-content {
  padding: 24px;
}

/* Bar Chart */
.chart-legend {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.total {
  background: #3b82f6;
}

.legend-color.steam {
  background: #66c0f4;
}

.legend-color.non-steam {
  background: #64748b;
}

.chart-bars-container {
  height: 200px;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 100%;
  padding-bottom: 30px;
}

.chart-bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-wrapper {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
}

.bar {
  width: 100%;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
  position: absolute;
  bottom: 0;
}

.total-bar {
  background: linear-gradient(180deg, #3b82f6 0%, rgba(59, 130, 246, 0.5) 100%);
}

.steam-bar {
  background: linear-gradient(180deg, #66c0f4 0%, rgba(102, 192, 244, 0.7) 100%);
}

.bar-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 8px;
  white-space: nowrap;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.3);
  gap: 12px;
}

/* Pie Chart */
.pie-chart-content {
  display: flex;
  align-items: center;
  gap: 40px;
}

.pie-chart-wrapper {
  flex-shrink: 0;
}

.pie-chart {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: conic-gradient(
    #66c0f4 0deg calc(var(--percentage) * 3.6deg),
    #64748b calc(var(--percentage) * 3.6deg) 360deg
  );
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-center {
  width: 100px;
  height: 100px;
  background: rgba(24, 24, 28, 0.95);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pie-value {
  font-size: 24px;
  font-weight: 700;
  color: #66c0f4;
}

.pie-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.pie-legend {
  flex: 1;
}

.pie-legend-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.pie-legend-item:last-child {
  border-bottom: none;
}

.pie-legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.pie-legend-color.steam {
  background: #66c0f4;
}

.pie-legend-color.non-steam {
  background: #64748b;
}

.pie-legend-info {
  display: flex;
  flex-direction: column;
}

.pie-legend-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.pie-legend-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

/* Activity Grid */
.activity-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 24px;
}

.activity-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 20px;
}

.activity-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  margin-bottom: 16px;
}

.activity-icon.users {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.activity-icon.logins {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.activity-icon.forum {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.activity-icon.revenue {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.activity-info {
  margin-bottom: 12px;
}

.activity-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
  margin-bottom: 4px;
}

.activity-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.activity-breakdown {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.breakdown-label {
  color: rgba(255, 255, 255, 0.4);
}

.breakdown-value {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* Engagement Section */
.engagement-section {
  margin-bottom: 32px;
}

.engagement-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  padding: 40px;
}

.engagement-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.engagement-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.engagement-circle.paying {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.05) 100%);
  border: 2px solid rgba(16, 185, 129, 0.3);
}

.engagement-circle.servers {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.05) 100%);
  border: 2px solid rgba(59, 130, 246, 0.3);
}

.engagement-circle.verified {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 2px solid rgba(139, 92, 246, 0.3);
}

.engagement-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.engagement-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.engagement-percent {
  font-size: 13px;
  color: #10b981;
  font-weight: 600;
}

/* Tables */
.table-container {
  padding: 16px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-weight: 600;
  color: #fff;
}

.email {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.balance-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.balance-real {
  font-weight: 600;
  color: #10b981;
}

.balance-coin {
  font-size: 11px;
  color: #f97316;
}

.rank-medal {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
}

.rank-medal.gold {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #000;
}

.rank-medal.silver {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  color: #fff;
}

.rank-medal.bronze {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  color: #fff;
}

.rank-number {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.total-spent {
  font-weight: 700;
  color: #10b981;
  font-size: 15px;
}

/* Animations */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .activity-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .charts-row {
    grid-template-columns: 1fr;
  }

  .engagement-grid {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .activity-grid {
    grid-template-columns: 1fr;
  }

  .pie-chart-content {
    flex-direction: column;
  }
}
</style>
