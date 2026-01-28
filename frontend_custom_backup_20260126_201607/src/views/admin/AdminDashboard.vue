<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-5xl font-lambda font-bold mb-2">
          <span class="text-xen-purple" style="text-shadow: 0 0 20px rgba(181, 55, 242, 0.6)">ADMIN PANEL</span>
        </h1>
        <p class="text-text-secondary font-hev">Sistem yönetimi ve izleme paneli</p>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-cyber-panel border border-lambda-orange rounded-lg p-6 hover:shadow-neon-orange transition-all">
          <div class="flex items-center justify-between mb-3">
            <div class="w-12 h-12 rounded bg-lambda-orange bg-opacity-20 border border-lambda-orange flex items-center justify-center">
              <Users :size="24" class="text-lambda-orange" />
            </div>
            <div class="text-right">
              <div class="text-3xl font-lambda text-lambda-orange">{{ stats.total_users || 0 }}</div>
              <div class="text-xs text-text-secondary font-hev">Toplam Kullanıcı</div>
            </div>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <span class="text-combine-green font-hev">+{{ stats.new_users_today || 0 }}</span>
            <span class="text-text-secondary font-hev">bugün</span>
          </div>
        </div>

        <div class="bg-cyber-panel border border-hev-cyan rounded-lg p-6 hover:shadow-neon-cyan transition-all">
          <div class="flex items-center justify-between mb-3">
            <div class="w-12 h-12 rounded bg-hev-cyan bg-opacity-20 border border-hev-cyan flex items-center justify-center">
              <Server :size="24" class="text-hev-cyan" />
            </div>
            <div class="text-right">
              <div class="text-3xl font-lambda text-hev-cyan">{{ stats.total_servers || 0 }}</div>
              <div class="text-xs text-text-secondary font-hev">Toplam Sunucu</div>
            </div>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <span class="text-combine-green font-hev">{{ stats.active_servers || 0 }}</span>
            <span class="text-text-secondary font-hev">aktif</span>
          </div>
        </div>

        <div class="bg-cyber-panel border border-combine-green rounded-lg p-6 hover:shadow-neon-green transition-all">
          <div class="flex items-center justify-between mb-3">
            <div class="w-12 h-12 rounded bg-combine-green bg-opacity-20 border border-combine-green flex items-center justify-center">
              <DollarSign :size="24" class="text-combine-green" />
            </div>
            <div class="text-right">
              <div class="text-3xl font-lambda text-combine-green">₺{{ formatMoney(stats.revenue_month || 0) }}</div>
              <div class="text-xs text-text-secondary font-hev">Aylık Gelir</div>
            </div>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <span class="text-combine-green font-hev">+{{ stats.revenue_growth || 0 }}%</span>
            <span class="text-text-secondary font-hev">artış</span>
          </div>
        </div>

        <div class="bg-cyber-panel border border-xen-purple rounded-lg p-6 hover:shadow-neon-purple transition-all">
          <div class="flex items-center justify-between mb-3">
            <div class="w-12 h-12 rounded bg-xen-purple bg-opacity-20 border border-xen-purple flex items-center justify-center">
              <MessageSquare :size="24" class="text-xen-purple" />
            </div>
            <div class="text-right">
              <div class="text-3xl font-lambda text-xen-purple">{{ stats.total_topics || 0 }}</div>
              <div class="text-xs text-text-secondary font-hev">Forum Konuları</div>
            </div>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <span class="text-combine-green font-hev">{{ stats.active_discussions || 0 }}</span>
            <span class="text-text-secondary font-hev">aktif</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions & System Status -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <!-- Quick Actions -->
        <div class="lg:col-span-1">
          <div class="bg-cyber-panel border border-cyber-border rounded-lg p-6">
            <h2 class="text-xl font-lambda font-bold text-text-primary mb-4 flex items-center gap-2">
              <Zap :size="20" class="text-combine-yellow" />
              HIZLI İŞLEMLER
            </h2>

            <div class="space-y-2">
              <router-link
                to="/admin/users"
                class="block w-full px-4 py-3 bg-cyber-darker border border-cyber-border text-left rounded hover:border-lambda-orange hover:bg-lambda-orange hover:bg-opacity-10 transition-all group"
              >
                <div class="flex items-center gap-3">
                  <Users :size="18" class="text-lambda-orange" />
                  <div>
                    <div class="font-lambda text-text-primary group-hover:text-lambda-orange">Kullanıcı Yönetimi</div>
                    <div class="text-xs text-text-secondary font-hev">Kullanıcıları görüntüle ve yönet</div>
                  </div>
                </div>
              </router-link>

              <router-link
                to="/admin/servers"
                class="block w-full px-4 py-3 bg-cyber-darker border border-cyber-border text-left rounded hover:border-hev-cyan hover:bg-hev-cyan hover:bg-opacity-10 transition-all group"
              >
                <div class="flex items-center gap-3">
                  <Server :size="18" class="text-hev-cyan" />
                  <div>
                    <div class="font-lambda text-text-primary group-hover:text-hev-cyan">Sunucu Yönetimi</div>
                    <div class="text-xs text-text-secondary font-hev">Sunucuları yönet ve izle</div>
                  </div>
                </div>
              </router-link>

              <button
                class="block w-full px-4 py-3 bg-cyber-darker border border-cyber-border text-left rounded hover:border-combine-green hover:bg-combine-green hover:bg-opacity-10 transition-all group"
              >
                <div class="flex items-center gap-3">
                  <FileText :size="18" class="text-combine-green" />
                  <div>
                    <div class="font-lambda text-text-primary group-hover:text-combine-green">Sistem Logları</div>
                    <div class="text-xs text-text-secondary font-hev">Sistem olaylarını görüntüle</div>
                  </div>
                </div>
              </button>

              <button
                class="block w-full px-4 py-3 bg-cyber-darker border border-cyber-border text-left rounded hover:border-xen-purple hover:bg-xen-purple hover:bg-opacity-10 transition-all group"
              >
                <div class="flex items-center gap-3">
                  <Settings :size="18" class="text-xen-purple" />
                  <div>
                    <div class="font-lambda text-text-primary group-hover:text-xen-purple">Site Ayarları</div>
                    <div class="text-xs text-text-secondary font-hev">Genel ayarları düzenle</div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- System Status -->
        <div class="lg:col-span-2">
          <div class="bg-cyber-panel border border-cyber-border rounded-lg p-6">
            <h2 class="text-xl font-lambda font-bold text-text-primary mb-4 flex items-center gap-2">
              <Activity :size="20" class="text-combine-green" />
              SİSTEM DURUMU
            </h2>

            <div class="space-y-4">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-hev text-text-secondary">CPU Kullanımı</span>
                  <span class="text-sm font-lambda text-lambda-orange">{{ systemStatus.cpu || 0 }}%</span>
                </div>
                <div class="w-full h-2 bg-cyber-darker rounded overflow-hidden">
                  <div
                    class="h-full bg-lambda-orange transition-all duration-500"
                    :style="{ width: `${systemStatus.cpu || 0}%` }"
                  ></div>
                </div>
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-hev text-text-secondary">RAM Kullanımı</span>
                  <span class="text-sm font-lambda text-hev-cyan">{{ systemStatus.ram || 0 }}%</span>
                </div>
                <div class="w-full h-2 bg-cyber-darker rounded overflow-hidden">
                  <div
                    class="h-full bg-hev-cyan transition-all duration-500"
                    :style="{ width: `${systemStatus.ram || 0}%` }"
                  ></div>
                </div>
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-hev text-text-secondary">Disk Kullanımı</span>
                  <span class="text-sm font-lambda text-combine-green">{{ systemStatus.disk || 0 }}%</span>
                </div>
                <div class="w-full h-2 bg-cyber-darker rounded overflow-hidden">
                  <div
                    class="h-full bg-combine-green transition-all duration-500"
                    :style="{ width: `${systemStatus.disk || 0}%` }"
                  ></div>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-cyber-border">
                <div class="text-center">
                  <div class="text-2xl font-lambda text-combine-green mb-1">{{ systemStatus.uptime || '0d' }}</div>
                  <div class="text-xs text-text-secondary font-hev">Uptime</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-lambda text-hev-cyan mb-1">{{ systemStatus.requests_sec || 0 }}</div>
                  <div class="text-xs text-text-secondary font-hev">İstek/sn</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-lambda text-lambda-orange mb-1">{{ systemStatus.active_connections || 0 }}</div>
                  <div class="text-xs text-text-secondary font-hev">Bağlantı</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-cyber-panel border border-cyber-border rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-lambda font-bold text-text-primary flex items-center gap-2">
            <Clock :size="20" class="text-hev-cyan" />
            SON AKTİVİTELER
          </h2>
          <button class="text-sm text-hev-cyan hover:text-hev-cyan-dark font-lambda">
            Tümünü Gör →
          </button>
        </div>

        <div class="space-y-2">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="flex items-start gap-4 p-3 bg-cyber-darker rounded hover:bg-cyber-panel transition-all"
          >
            <div
              class="w-8 h-8 rounded flex items-center justify-center flex-shrink-0"
              :class="getActivityIconClass(activity.type)"
            >
              <component :is="getActivityIcon(activity.type)" :size="16" />
            </div>

            <div class="flex-1">
              <p class="text-sm text-text-primary font-hev">
                <span class="font-lambda text-lambda-orange">{{ activity.user }}</span>
                {{ activity.message }}
              </p>
              <p class="text-xs text-text-secondary font-hev mt-1">
                {{ formatTime(activity.timestamp) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Users,
  Server,
  DollarSign,
  MessageSquare,
  Zap,
  Activity,
  Clock,
  FileText,
  Settings,
  UserPlus,
  ServerCog,
  ShieldAlert,
  CreditCard
} from 'lucide-vue-next'

const stats = ref({
  total_users: 1234,
  new_users_today: 45,
  total_servers: 89,
  active_servers: 67,
  revenue_month: 45000,
  revenue_growth: 12,
  total_topics: 567,
  active_discussions: 89
})

const systemStatus = ref({
  cpu: 45,
  ram: 62,
  disk: 38,
  uptime: '15d 6h',
  requests_sec: 120,
  active_connections: 456
})

const recentActivities = ref([
  {
    id: 1,
    type: 'user_register',
    user: 'newuser123',
    message: 'yeni hesap oluşturdu',
    timestamp: Date.now() - 120000
  },
  {
    id: 2,
    type: 'server_created',
    user: 'admin',
    message: 'yeni sunucu oluşturdu (#45)',
    timestamp: Date.now() - 300000
  },
  {
    id: 3,
    type: 'payment',
    user: 'user456',
    message: '₺199 ödeme yaptı',
    timestamp: Date.now() - 600000
  },
  {
    id: 4,
    type: 'report',
    user: 'moderator1',
    message: 'bir rapor inceledi',
    timestamp: Date.now() - 900000
  }
])

// Methods
function formatMoney(value) {
  return new Intl.NumberFormat('tr-TR').format(value)
}

function formatTime(timestamp) {
  const diff = Date.now() - timestamp
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)

  if (minutes < 1) return 'Az önce'
  if (minutes < 60) return `${minutes} dakika önce`
  if (hours < 24) return `${hours} saat önce`

  return new Date(timestamp).toLocaleString('tr-TR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getActivityIcon(type) {
  const icons = {
    user_register: UserPlus,
    server_created: ServerCog,
    payment: CreditCard,
    report: ShieldAlert
  }
  return icons[type] || Activity
}

function getActivityIconClass(type) {
  const classes = {
    user_register: 'bg-lambda-orange bg-opacity-20 text-lambda-orange',
    server_created: 'bg-hev-cyan bg-opacity-20 text-hev-cyan',
    payment: 'bg-combine-green bg-opacity-20 text-combine-green',
    report: 'bg-combine-red bg-opacity-20 text-combine-red'
  }
  return classes[type] || 'bg-cyber-border text-text-secondary'
}

// Lifecycle
onMounted(() => {
  // Auto-refresh system status every 5 seconds
  setInterval(() => {
    // Simulate changing values
    systemStatus.value.cpu = Math.floor(Math.random() * 30) + 40
    systemStatus.value.ram = Math.floor(Math.random() * 20) + 50
    systemStatus.value.requests_sec = Math.floor(Math.random() * 50) + 100
  }, 5000)
})
</script>

<style scoped>
.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}

.shadow-neon-cyan {
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.6);
}

.shadow-neon-green {
  box-shadow: 0 0 20px rgba(57, 255, 20, 0.6);
}

.shadow-neon-purple {
  box-shadow: 0 0 20px rgba(181, 55, 242, 0.6);
}
</style>
