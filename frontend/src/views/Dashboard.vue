<template>
  <div class="min-h-screen py-8">
    <div class="container-custom">
      <!-- Welcome Header -->
      <div class="mb-8">
        <h1 class="text-3xl sm:text-4xl font-display font-bold mb-2">
          Hoş Geldin, <span class="text-gradient">{{ user?.username || 'Oyuncu' }}!</span>
        </h1>
        <p class="text-gray-400">
          İşte senin için hazırladığımız özet ve son aktiviteler
        </p>
      </div>

      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <n-card class="stat-card" :class="'border-yellow-500/30 hover:border-yellow-500/60'">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">Seviye</span>
            <TrophyIcon class="w-5 h-5 text-yellow-500" />
          </div>
          <div class="text-2xl sm:text-3xl font-bold mb-2">{{ playerStats.level }}</div>
          <n-progress
            type="line"
            :percentage="playerStats.levelProgress"
            :show-indicator="false"
            status="warning"
            class="mb-2"
          />
          <div class="text-xs text-gray-400">{{ playerStats.xpCurrent }}/{{ playerStats.xpNeeded }} XP</div>
        </n-card>

        <n-card class="stat-card" :class="'border-green-500/30 hover:border-green-500/60'">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">K/D Oranı</span>
            <ActivityIcon class="w-5 h-5 text-green-500" />
          </div>
          <div class="text-2xl sm:text-3xl font-bold text-green-500 mb-2">{{ playerStats.kd }}</div>
          <div class="text-xs text-gray-400">{{ playerStats.kills }} / {{ playerStats.deaths }}</div>
        </n-card>

        <n-card class="stat-card" :class="'border-purple-500/30 hover:border-purple-500/60'">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">Sıralaman</span>
            <CrownIcon class="w-5 h-5 text-purple-500" />
          </div>
          <div class="text-2xl sm:text-3xl font-bold text-purple-500 mb-2">#{{ playerStats.rank }}</div>
          <div class="text-xs text-gray-400">Tüm oyuncular arasında</div>
        </n-card>

        <n-card class="stat-card" :class="'border-cyan-500/30 hover:border-cyan-500/60'">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-400">Toplam Süre</span>
            <ClockIcon class="w-5 h-5 text-cyan-500" />
          </div>
          <div class="text-2xl sm:text-3xl font-bold text-cyan-500 mb-2">{{ playerStats.playtime }}h</div>
          <div class="text-xs text-gray-400">Son 30 gün: {{ playerStats.playtimeMonth }}h</div>
        </n-card>
      </div>

      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Recent Activity -->
          <n-card title="Son Aktiviteler" class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <ActivityIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Son Aktiviteler</span>
              </div>
            </template>
            <div class="space-y-3">
              <div
                v-for="activity in recentActivity"
                :key="activity.id"
                class="flex items-start gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-all"
              >
                <div
                  class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                  :class="getActivityIconBg(activity.type)"
                >
                  <component :is="getActivityIcon(activity.type)" class="w-5 h-5 text-white" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm">{{ activity.message }}</p>
                  <p class="text-xs text-gray-400 mt-1">{{ activity.time }}</p>
                </div>
              </div>
            </div>
          </n-card>

          <!-- Achievements -->
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <AwardIcon class="w-5 h-5 text-yellow-500" />
                <span class="font-bold">Son Kazanılan Rozetler</span>
              </div>
            </template>
            <div class="grid grid-cols-2 gap-4">
              <div
                v-for="achievement in recentAchievements"
                :key="achievement.id"
                class="p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-all cursor-pointer"
              >
                <div class="text-3xl mb-2">{{ achievement.icon }}</div>
                <h3 class="font-bold text-sm mb-1">{{ achievement.title }}</h3>
                <p class="text-xs text-gray-400">{{ achievement.description }}</p>
                <n-tag type="warning" size="small" class="mt-2">+{{ achievement.xp }} XP</n-tag>
              </div>
            </div>
          </n-card>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <n-card class="glass-card">
            <template #header>
              <span class="font-bold">Hızlı İşlemler</span>
            </template>
            <div class="space-y-2">
              <router-link to="/servers" class="block">
                <n-button type="primary" block class="justify-start">
                  <template #icon><ServerIcon class="w-4 h-4" /></template>
                  Sunuculara Göz At
                </n-button>
              </router-link>
              <router-link to="/forum" class="block">
                <n-button block quaternary class="justify-start">
                  <template #icon><MessageSquareIcon class="w-4 h-4" /></template>
                  Forum'da Yeni Konu
                </n-button>
              </router-link>
              <router-link to="/leaderboard" class="block">
                <n-button block quaternary class="justify-start">
                  <template #icon><TrophyIcon class="w-4 h-4" /></template>
                  Sıralamaya Göz At
                </n-button>
              </router-link>
              <router-link to="/profile" class="block">
                <n-button block quaternary class="justify-start">
                  <template #icon><UserIcon class="w-4 h-4" /></template>
                  Profilimi Düzenle
                </n-button>
              </router-link>
            </div>
          </n-card>

          <!-- Friends Online -->
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center justify-between w-full">
                <span class="font-bold">Çevrimiçi Arkadaşlar</span>
                <n-tag type="success" size="small" round>{{ friendsOnline.length }}</n-tag>
              </div>
            </template>
            <div class="space-y-3">
              <div
                v-for="friend in friendsOnline"
                :key="friend.id"
                class="flex items-center gap-3 cursor-pointer hover:bg-white/5 p-2 rounded-lg transition-all"
              >
                <div class="relative">
                  <n-avatar
                    round
                    :style="{ backgroundColor: '#f97316' }"
                  >
                    {{ friend.name.substring(0, 2) }}
                  </n-avatar>
                  <div class="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-green-500 border-2 border-gray-900"></div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate">{{ friend.name }}</p>
                  <p class="text-xs text-gray-400 truncate">{{ friend.status }}</p>
                </div>
              </div>
            </div>
          </n-card>

          <!-- Active Tournaments -->
          <n-card class="glass-card">
            <template #header>
              <span class="font-bold">Aktif Turnuvalar</span>
            </template>
            <div class="space-y-3">
              <div
                v-for="tournament in activeTournaments"
                :key="tournament.id"
                class="p-3 rounded-lg bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 hover:border-purple-500/50 transition-all cursor-pointer"
              >
                <h4 class="font-bold text-sm mb-1">{{ tournament.name }}</h4>
                <div class="flex items-center justify-between text-xs text-gray-400">
                  <span>{{ tournament.date }}</span>
                  <span class="text-yellow-500 font-bold">{{ tournament.prize }}</span>
                </div>
                <n-button size="small" secondary block class="mt-2">Katıl</n-button>
              </div>
            </div>
          </n-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  TrophyIcon,
  ActivityIcon,
  CrownIcon,
  ClockIcon,
  ServerIcon,
  MessageSquareIcon,
  UserIcon,
  AwardIcon,
  TargetIcon
} from 'lucide-vue-next'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// Activity helpers
const getActivityIconBg = (type) => {
  const classes = {
    kill: 'bg-red-500',
    achievement: 'bg-yellow-500',
    forum: 'bg-blue-500',
    level: 'bg-purple-500',
    server: 'bg-green-500'
  }
  return classes[type] || 'bg-gray-500'
}

const getActivityIcon = (type) => {
  const icons = {
    kill: TargetIcon,
    achievement: AwardIcon,
    forum: MessageSquareIcon,
    level: TrophyIcon,
    server: ServerIcon
  }
  return icons[type] || ActivityIcon
}

// Data
const playerStats = ref({
  level: 42,
  levelProgress: 67,
  xpCurrent: 3400,
  xpNeeded: 5000,
  kd: 2.45,
  kills: 12456,
  deaths: 5089,
  rank: 127,
  playtime: 456,
  playtimeMonth: 48
})

const recentActivity = ref([
  { id: 1, type: 'kill', message: 'AGTR Public #1 sunucusunda 25 kill yaptın!', time: '10 dakika önce' },
  { id: 2, type: 'achievement', message: '"Headshot Master" rozetini kazandın!', time: '1 saat önce' },
  { id: 3, type: 'forum', message: '"En İyi AWP Taktikleri" konusuna yanıt verdin', time: '3 saat önce' },
  { id: 4, type: 'level', message: "Seviye 42'ye ulaştın!", time: '5 saat önce' }
])

const recentAchievements = ref([
  { id: 1, icon: '🎯', title: 'Headshot Master', description: '100 headshot yap', xp: 500 },
  { id: 2, icon: '⚡', title: 'Speed Demon', description: '10 saniyede 5 kill', xp: 300 },
  { id: 3, icon: '🛡️', title: 'Survivor', description: '10 maç boyunca ölme', xp: 750 },
  { id: 4, icon: '👑', title: 'MVP', description: '5 maç üst üste MVP', xp: 1000 }
])

const friendsOnline = ref([
  { id: 1, name: 'ProGamer123', status: 'AGTR Public #1' },
  { id: 2, name: 'SnipeKing', status: 'Deathmatch Arena' },
  { id: 3, name: 'RushMaster', status: 'Menüde' }
])

const activeTournaments = ref([
  { id: 1, name: '5v5 Aylık Turnuva', date: '25 Ocak', prize: '500₺' },
  { id: 2, name: 'AWP Only Cup', date: '28 Ocak', prize: '250₺' }
])
</script>

<style scoped>
.text-gradient {
  background: linear-gradient(to right, #f97316, #fb923c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}
</style>
