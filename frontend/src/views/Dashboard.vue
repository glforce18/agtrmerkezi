<template>
  <div class="min-h-screen py-8">
    <div class="container-custom">
      <!-- Welcome Header -->
      <div class="mb-8">
        <h1 class="text-3xl sm:text-4xl font-display font-bold mb-2">
          Hos Geldin, <span class="text-gradient-orange">{{ user?.username || 'Oyuncu' }}!</span>
        </h1>
        <p class="opacity-60">
          Iste senin icin hazirladigimiz ozet ve son aktiviteler
        </p>
      </div>

      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Seviye"
          :value="playerStats.level"
          :icon="TrophyIcon"
          color="yellow"
          :progress="playerStats.levelProgress"
          :sub-text="`${playerStats.xpCurrent}/${playerStats.xpNeeded} XP`"
        />
        <StatCard
          title="K/D Orani"
          :value="playerStats.kd"
          :icon="ActivityIcon"
          color="green"
          :sub-text="`${playerStats.kills} / ${playerStats.deaths}`"
        />
        <StatCard
          title="Siralaman"
          :value="`#${playerStats.rank}`"
          :icon="CrownIcon"
          color="purple"
          sub-text="Tum oyuncular arasinda"
        />
        <StatCard
          title="Toplam Sure"
          :value="`${playerStats.playtime}h`"
          :icon="ClockIcon"
          color="cyan"
          :sub-text="`Son 30 gun: ${playerStats.playtimeMonth}h`"
        />
      </div>

      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Recent Activity -->
          <div class="glass-card p-6">
            <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
              <ActivityIcon class="w-5 h-5 text-orange-500" />
              Son Aktiviteler
            </h2>

            <div class="space-y-3">
              <ActivityItem
                v-for="activity in recentActivity"
                :key="activity.id"
                :activity="activity"
              />
            </div>
          </div>

          <!-- Achievements -->
          <div class="glass-card p-6">
            <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
              <AwardIcon class="w-5 h-5 text-yellow-500" />
              Son Kazanilan Rozetler
            </h2>

            <div class="grid grid-cols-2 gap-4">
              <AchievementCard
                v-for="achievement in recentAchievements"
                :key="achievement.id"
                :achievement="achievement"
              />
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <div class="glass-card p-6">
            <h3 class="font-bold mb-4">Hizli Islemler</h3>
            <div class="space-y-2">
              <router-link to="/servers" class="block">
                <button class="btn-gaming w-full justify-start text-sm">
                  <ServerIcon class="w-4 h-4" />
                  Sunuculara Goz At
                </button>
              </router-link>
              <router-link to="/forum" class="block">
                <button class="btn-outline-gaming w-full justify-start text-sm">
                  <MessageSquareIcon class="w-4 h-4" />
                  Forum'da Yeni Konu
                </button>
              </router-link>
              <router-link to="/leaderboard" class="block">
                <button class="btn-outline-gaming w-full justify-start text-sm">
                  <TrophyIcon class="w-4 h-4" />
                  Siralamaya Goz At
                </button>
              </router-link>
              <router-link to="/profile" class="block">
                <button class="btn-outline-gaming w-full justify-start text-sm">
                  <UserIcon class="w-4 h-4" />
                  Profilimi Duzenle
                </button>
              </router-link>
            </div>
          </div>

          <!-- Friends Online -->
          <div class="glass-card p-6">
            <h3 class="font-bold mb-4 flex items-center justify-between">
              <span>Cevrimici Arkadaslar</span>
              <span class="badge-gaming">{{ friendsOnline.length }}</span>
            </h3>
            <div class="space-y-3">
              <FriendItem
                v-for="friend in friendsOnline"
                :key="friend.id"
                :friend="friend"
              />
            </div>
          </div>

          <!-- Active Tournaments -->
          <div class="glass-card p-6">
            <h3 class="font-bold mb-4">Aktif Turnuvalar</h3>
            <div class="space-y-3">
              <TournamentItem
                v-for="tournament in activeTournaments"
                :key="tournament.id"
                :tournament="tournament"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue'
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
  TargetIcon,
  ZapIcon,
  ShieldIcon,
  UsersIcon
} from 'lucide-vue-next'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// ============================================
// Sub-components (inline for modularity)
// ============================================

// Stat Card Component
const StatCard = {
  props: ['title', 'value', 'icon', 'color', 'progress', 'subText'],
  template: `
    <div class="glass-card p-6 card-hover-lift" :class="borderClass">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm opacity-60">{{ title }}</span>
        <component :is="icon" class="w-5 h-5" :class="iconClass" />
      </div>
      <div class="text-2xl sm:text-3xl font-bold mb-2" :class="textClass">{{ value }}</div>
      <div v-if="progress !== undefined" class="progress-bar h-2 mb-2">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="text-xs opacity-60">{{ subText }}</div>
    </div>
  `,
  computed: {
    iconClass() {
      const colors = { yellow: 'text-yellow-500', green: 'text-green-500', purple: 'text-purple-500', cyan: 'text-cyan-500', orange: 'text-orange-500' }
      return colors[this.color] || 'text-orange-500'
    },
    textClass() {
      const colors = { yellow: '', green: 'text-green-500', purple: 'text-purple-500', cyan: 'text-cyan-500', orange: 'text-orange-500' }
      return colors[this.color] || ''
    },
    borderClass() {
      const colors = { yellow: 'hover:border-yellow-500/50', green: 'hover:border-green-500/50', purple: 'hover:border-purple-500/50', cyan: 'hover:border-cyan-500/50', orange: 'hover:border-orange-500/50' }
      return colors[this.color] || 'hover:border-orange-500/50'
    }
  }
}

// Activity Item Component
const ActivityItem = {
  props: ['activity'],
  components: { TargetIcon, AwardIcon, MessageSquareIcon, TrophyIcon, ServerIcon, ActivityIcon },
  template: `
    <div class="flex items-start gap-3 p-3 rounded-lg bg-base-200/50 hover:bg-base-200 transition-all">
      <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" :class="iconBgClass">
        <component :is="getIcon()" class="w-5 h-5 text-white" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm">{{ activity.message }}</p>
        <p class="text-xs opacity-60 mt-1">{{ activity.time }}</p>
      </div>
    </div>
  `,
  computed: {
    iconBgClass() {
      const classes = { kill: 'bg-red-500', achievement: 'bg-yellow-500', forum: 'bg-blue-500', level: 'bg-purple-500', server: 'bg-green-500' }
      return classes[this.activity.type] || 'bg-gray-500'
    }
  },
  methods: {
    getIcon() {
      const icons = { kill: TargetIcon, achievement: AwardIcon, forum: MessageSquareIcon, level: TrophyIcon, server: ServerIcon }
      return icons[this.activity.type] || ActivityIcon
    }
  }
}

// Achievement Card Component
const AchievementCard = {
  props: ['achievement'],
  template: `
    <div class="p-4 rounded-lg bg-base-200/50 hover:bg-base-200 transition-all cursor-pointer">
      <div class="text-3xl mb-2">{{ achievement.icon }}</div>
      <h3 class="font-bold text-sm mb-1">{{ achievement.title }}</h3>
      <p class="text-xs opacity-60">{{ achievement.description }}</p>
      <div class="text-xs text-orange-500 mt-2">+{{ achievement.xp }} XP</div>
    </div>
  `
}

// Friend Item Component
const FriendItem = {
  props: ['friend'],
  template: `
    <div class="flex items-center gap-3 cursor-pointer hover:bg-base-200/50 p-2 rounded-lg transition-all">
      <div class="relative">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
          <span class="text-sm font-bold text-white">{{ friend.name.substring(0, 2) }}</span>
        </div>
        <div class="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-green-500 border-2 border-base-100"></div>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium truncate">{{ friend.name }}</p>
        <p class="text-xs opacity-60 truncate">{{ friend.status }}</p>
      </div>
    </div>
  `
}

// Tournament Item Component
const TournamentItem = {
  props: ['tournament'],
  template: `
    <div class="p-3 rounded-lg bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 hover:border-purple-500/50 transition-all cursor-pointer">
      <h4 class="font-bold text-sm mb-1">{{ tournament.name }}</h4>
      <div class="flex items-center justify-between text-xs opacity-60">
        <span>{{ tournament.date }}</span>
        <span class="text-yellow-500 font-bold">{{ tournament.prize }}</span>
      </div>
      <button class="btn-outline-gaming w-full mt-2 text-xs py-1.5">Katil</button>
    </div>
  `
}

// ============================================
// Data
// ============================================

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
  { id: 1, type: 'kill', message: 'AGTR Public #1 sunucusunda 25 kill yaptin!', time: '10 dakika once' },
  { id: 2, type: 'achievement', message: '"Headshot Master" rozetini kazandin!', time: '1 saat once' },
  { id: 3, type: 'forum', message: '"En Iyi AWP Taktikleri" konusuna yanit verdin', time: '3 saat once' },
  { id: 4, type: 'level', message: "Seviye 42'ye ulastin!", time: '5 saat once' }
])

const recentAchievements = ref([
  { id: 1, icon: '🎯', title: 'Headshot Master', description: '100 headshot yap', xp: 500 },
  { id: 2, icon: '⚡', title: 'Speed Demon', description: '10 saniyede 5 kill', xp: 300 },
  { id: 3, icon: '🛡️', title: 'Survivor', description: '10 mac boyunca olme', xp: 750 },
  { id: 4, icon: '👑', title: 'MVP', description: '5 mac ust uste MVP', xp: 1000 }
])

const friendsOnline = ref([
  { id: 1, name: 'ProGamer123', status: 'AGTR Public #1' },
  { id: 2, name: 'SnipeKing', status: 'Deathmatch Arena' },
  { id: 3, name: 'RushMaster', status: 'Menude' }
])

const activeTournaments = ref([
  { id: 1, name: '5v5 Aylik Turnuva', date: '25 Ocak', prize: '500₺' },
  { id: 2, name: 'AWP Only Cup', date: '28 Ocak', prize: '250₺' }
])
</script>

<style scoped>
/* Dashboard specific styles */
.glass-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
</style>
