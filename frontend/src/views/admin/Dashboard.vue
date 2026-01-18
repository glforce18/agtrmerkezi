<template>
  <AdminLayout>
    <div class="dashboard">
      <!-- Stats Grid -->
      <div class="stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="stat-card">
          <div class="stat-icon" :class="stat.color">
            <component :is="stat.icon" :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
          <div v-if="stat.change" class="stat-change" :class="stat.change > 0 ? 'positive' : 'negative'">
            <TrendingUp v-if="stat.change > 0" :size="16" />
            <TrendingDown v-else :size="16" />
            <span>{{ Math.abs(stat.change) }}%</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="section">
        <h2 class="section-title">Hızlı İşlemler</h2>
        <div class="quick-actions">
          <router-link to="/admin/users" class="action-card">
            <Users :size="28" />
            <span>Kullanıcılar</span>
          </router-link>
          <router-link to="/admin/payments" class="action-card">
            <CreditCard :size="28" />
            <span>Ödemeler</span>
          </router-link>
          <router-link to="/admin/servers" class="action-card">
            <Server :size="28" />
            <span>Sunucular</span>
          </router-link>
          <router-link to="/admin/packages" class="action-card">
            <Package :size="28" />
            <span>Paketler</span>
          </router-link>
        </div>
      </div>

      <!-- Recent Activity & Pending Payments -->
      <div class="grid-2">
        <!-- Recent Activity -->
        <div class="card">
          <div class="card-header">
            <h3>Son Aktiviteler</h3>
            <button class="btn-text" @click="refreshActivity">
              <RefreshCw :size="16" />
            </button>
          </div>
          <div class="card-body">
            <div v-if="loading" class="loading">
              <Loader2 :size="24" class="spin" />
            </div>
            <div v-else-if="activities.length === 0" class="empty">
              Henüz aktivite yok
            </div>
            <div v-else class="activity-list">
              <div v-for="activity in activities" :key="activity.id" class="activity-item">
                <div class="activity-icon" :class="activity.type">
                  <component :is="getActivityIcon(activity.type)" :size="16" />
                </div>
                <div class="activity-content">
                  <span class="activity-text">{{ activity.message }}</span>
                  <span class="activity-time">{{ formatTime(activity.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending Payments -->
        <div class="card">
          <div class="card-header">
            <h3>Bekleyen Ödemeler</h3>
            <router-link to="/admin/payments" class="btn-text">Tümü</router-link>
          </div>
          <div class="card-body">
            <div v-if="pendingPayments.length === 0" class="empty">
              Bekleyen ödeme yok
            </div>
            <div v-else class="payment-list">
              <div v-for="payment in pendingPayments" :key="payment.id" class="payment-item">
                <div class="payment-user">
                  <img :src="getUserAvatar(payment.username)" alt="" class="avatar" />
                  <span>{{ payment.username }}</span>
                </div>
                <span class="payment-amount">{{ payment.amount }} ₺</span>
                <div class="payment-actions">
                  <button class="btn-approve" @click="approvePayment(payment.id)">
                    <Check :size="16" />
                  </button>
                  <button class="btn-reject" @click="rejectPayment(payment.id)">
                    <X :size="16" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
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
  Loader2,
  UserPlus,
  ShoppingCart,
  AlertTriangle,
  Check,
  X
} from 'lucide-vue-next'
import { formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()
const loading = ref(false)

const stats = ref([
  { label: 'Toplam Kullanıcı', value: '0', icon: Users, color: 'blue', change: 0 },
  { label: 'Aktif Sunucu', value: '0', icon: Server, color: 'green', change: 0 },
  { label: 'Bu Ay Gelir', value: '0 ₺', icon: DollarSign, color: 'purple', change: 0 },
  { label: 'Bekleyen Ödeme', value: '0', icon: CreditCard, color: 'orange' }
])

const activities = ref([])
const pendingPayments = ref([])

// Get CSRF token from cookie
const getCsrfToken = () => {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrf_token') return value
  }
  return null
}

const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authStore.token}`
  }
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }
  return headers
}

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/dashboard', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      // API returns: users.total, servers.total, servers.running, payments.pending, payments.month_revenue
      stats.value[0].value = data.users?.total?.toString() || '0'
      stats.value[1].value = data.servers?.running?.toString() || '0'
      stats.value[2].value = `${data.payments?.month_revenue || 0} ₺`
      stats.value[3].value = data.payments?.pending?.toString() || '0'
    }
  } catch (error) {
    console.error('Dashboard fetch error:', error)
  }

  try {
    const paymentsRes = await fetch('/api/admin/payments?status=pending&limit=10', {
      headers: getHeaders()
    })
    if (paymentsRes.ok) {
      const data = await paymentsRes.json()
      pendingPayments.value = data.payments || []
    }
  } catch (error) {
    console.error('Pending payments fetch error:', error)
  }

  loading.value = false
}

const refreshActivity = () => {
  fetchDashboardData()
}

const getActivityIcon = (type) => {
  const icons = {
    user: UserPlus,
    payment: ShoppingCart,
    server: Server,
    warning: AlertTriangle
  }
  return icons[type] || Activity
}

const formatTime = (date) => {
  if (!date) return ''
  return formatDistanceToNow(new Date(date), { addSuffix: true, locale: tr })
}

const getUserAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}`
}

const approvePayment = async (id) => {
  if (!confirm('Bu ödemeyi onaylamak istediğinize emin misiniz?')) return

  try {
    const response = await fetch(`/api/admin/payments/${id}/approve`, {
      method: 'POST',
      headers: getHeaders()
    })
    if (response.ok) {
      pendingPayments.value = pendingPayments.value.filter(p => p.id !== id)
      stats.value[3].value = (parseInt(stats.value[3].value) - 1).toString()
    }
  } catch (error) {
    console.error('Approve error:', error)
  }
}

const rejectPayment = async (id) => {
  const reason = prompt('Red sebebi:')
  if (!reason) return

  try {
    const response = await fetch(`/api/admin/payments/${id}/reject`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ reason })
    })
    if (response.ok) {
      pendingPayments.value = pendingPayments.value.filter(p => p.id !== id)
      stats.value[3].value = (parseInt(stats.value[3].value) - 1).toString()
    }
  } catch (error) {
    console.error('Reject error:', error)
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue { background: rgba(59, 130, 246, 0.15); color: var(--info-color, #3b82f6); }
.stat-icon.green { background: rgba(16, 185, 129, 0.15); color: var(--success-color, #10b981); }
.stat-icon.purple { background: rgba(139, 92, 246, 0.15); color: var(--secondary-color, #8b5cf6); }
.stat-icon.orange { background: rgba(255, 107, 0, 0.15); color: var(--primary-color, #ff6b00); }

.stat-info {
  flex: 1;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 8px;
}

.stat-change.positive {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
}

.stat-change.negative {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color, #ef4444);
}

.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.action-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.action-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.action-card svg {
  color: var(--primary-color);
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-text {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 14px;
  text-decoration: none;
}

.card-body {
  padding: 24px;
  max-height: 400px;
  overflow-y: auto;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.user { background: rgba(59, 130, 246, 0.15); color: var(--info-color, #3b82f6); }
.activity-icon.payment { background: rgba(16, 185, 129, 0.15); color: var(--success-color, #10b981); }
.activity-icon.server { background: rgba(255, 107, 0, 0.15); color: var(--primary-color, #ff6b00); }
.activity-icon.warning { background: rgba(245, 158, 11, 0.15); color: var(--warning-color, #f59e0b); }

.activity-content {
  flex: 1;
}

.activity-text {
  display: block;
  font-size: 14px;
  color: var(--text-primary);
}

.activity-time {
  font-size: 12px;
  color: var(--text-muted);
}

.payment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.payment-user {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.payment-amount {
  font-weight: 600;
  color: var(--success-color);
}

.payment-actions {
  display: flex;
  gap: 8px;
}

.btn-approve, .btn-reject {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-approve {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color, #10b981);
}

.btn-approve:hover {
  background: var(--success-color, #10b981);
  color: white;
}

.btn-reject {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color, #ef4444);
}

.btn-reject:hover {
  background: var(--error-color, #ef4444);
  color: white;
}
</style>
