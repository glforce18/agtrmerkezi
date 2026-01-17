<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="relative py-20 lg:py-32 overflow-hidden">
      <!-- Background Gradient -->
      <div class="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-orange-500/5"></div>

      <div class="container-custom relative z-10">
        <div class="text-center max-w-4xl mx-auto">
          <!-- Lambda Logo -->
          <div class="mb-8 animate-fade-in">
            <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 shadow-2xl shadow-orange-500/30">
              <span class="text-5xl font-bold text-white">λ</span>
            </div>
          </div>

          <!-- Title -->
          <h1 class="text-4xl sm:text-5xl lg:text-7xl font-display font-bold mb-6 animate-slide-up">
            <span>AGTR</span>
            <span class="text-gradient-orange"> Merkezi</span>
          </h1>

          <!-- Subtitle -->
          <p class="text-lg sm:text-xl opacity-80 mb-4 animate-slide-up" style="animation-delay: 0.1s">
            Counter-Strike 1.6 Turkiye Toplulugu
          </p>
          <p class="text-base sm:text-lg opacity-60 mb-10 max-w-2xl mx-auto animate-slide-up" style="animation-delay: 0.2s">
            Binlerce oyuncunun bulustugu, turnuvalarin duzenlendigi,
            sunucularin paylasildigi Half-Life evreninin en buyuk Turk toplulugu.
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up" style="animation-delay: 0.3s">
            <router-link to="/forum">
              <button class="btn-gaming w-full sm:w-auto">
                <MessageSquareIcon class="w-5 h-5" />
                Forum'a Katil
              </button>
            </router-link>
            <router-link to="/leaderboard">
              <button class="btn-outline-gaming w-full sm:w-auto">
                <TrophyIcon class="w-5 h-5" />
                Siralamalar
              </button>
            </router-link>
            <router-link to="/servers">
              <button class="btn-outline-gaming w-full sm:w-auto">
                <ServerIcon class="w-5 h-5" />
                Sunucular
              </button>
            </router-link>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-20 max-w-4xl mx-auto">
          <StatCard
            v-for="stat in stats"
            :key="stat.label"
            :icon="stat.icon"
            :value="stat.value"
            :label="stat.label"
            :color="stat.color"
          />
        </div>
      </div>
    </section>

    <!-- Latest Forum Topics -->
    <section class="py-16 section-alt">
      <div class="container-custom">
        <SectionHeader
          title="Son Forum Konulari"
          :icon="MessageSquareIcon"
          link="/forum"
          link-text="Tumunu Gor"
        />

        <div class="space-y-3">
          <TopicCard
            v-for="topic in latestTopics"
            :key="topic.id"
            :topic="topic"
          />
        </div>
      </div>
    </section>

    <!-- Top Players -->
    <section class="py-16">
      <div class="container-custom">
        <SectionHeader
          title="En Iyi Oyuncular"
          :icon="TrophyIcon"
          link="/leaderboard"
          link-text="Tum Siralama"
        />

        <div class="grid md:grid-cols-3 gap-6">
          <PlayerCard
            v-for="(player, index) in topPlayers"
            :key="player.id"
            :player="player"
            :rank="index + 1"
          />
        </div>
      </div>
    </section>

    <!-- Popular Servers -->
    <section class="py-16 section-alt">
      <div class="container-custom">
        <SectionHeader
          title="Populer Sunucular"
          :icon="ServerIcon"
          link="/servers"
          link-text="Tum Sunucular"
        />

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ServerCard
            v-for="server in popularServers"
            :key="server.id"
            :server="server"
          />
        </div>
      </div>
    </section>

    <!-- Active Events -->
    <section class="py-16">
      <div class="container-custom">
        <SectionHeader
          title="Aktif Turnuvalar"
          :icon="CalendarIcon"
          centered
        />

        <div class="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <EventCard
            v-for="event in activeEvents"
            :key="event.id"
            :event="event"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import {
  ServerIcon,
  MessageSquareIcon,
  TrophyIcon,
  UsersIcon,
  CalendarIcon,
  ClockIcon,
  EyeIcon,
  UserIcon,
  ActivityIcon,
  ArrowRightIcon,
  CrownIcon
} from 'lucide-vue-next'

// ============================================
// Sub-components (inline for modularity)
// ============================================

// Stat Card Component
const StatCard = {
  props: ['icon', 'value', 'label', 'color'],
  template: `
    <div class="glass-card p-6 text-center card-hover-lift">
      <component :is="icon" class="w-8 h-8 mx-auto mb-3" :class="color" />
      <div class="text-2xl sm:text-3xl font-bold mb-1">{{ value }}</div>
      <div class="text-sm opacity-60">{{ label }}</div>
    </div>
  `
}

// Section Header Component
const SectionHeader = {
  props: ['title', 'icon', 'link', 'linkText', 'centered'],
  components: { ArrowRightIcon },
  template: `
    <div class="flex items-center justify-between mb-8" :class="centered ? 'justify-center' : ''">
      <h2 class="text-2xl sm:text-3xl font-display font-bold flex items-center gap-3">
        <component :is="icon" class="w-8 h-8 text-orange-500" />
        {{ title }}
      </h2>
      <router-link v-if="link" :to="link" class="hidden sm:flex items-center gap-1 text-sm text-orange-500 hover:text-orange-400 transition-colors">
        {{ linkText }}
        <ArrowRightIcon class="w-4 h-4" />
      </router-link>
    </div>
  `
}

// Topic Card Component
const TopicCard = {
  props: ['topic'],
  components: { MessageSquareIcon, UserIcon, EyeIcon, ClockIcon },
  template: `
    <div class="glass-card p-4 cursor-pointer card-hover-lift">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center flex-shrink-0">
          <MessageSquareIcon class="w-6 h-6 text-white" />
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-bold truncate">{{ topic.title }}</h3>
          <div class="flex flex-wrap items-center gap-3 text-sm opacity-60 mt-1">
            <span class="flex items-center gap-1">
              <UserIcon class="w-3 h-3" />
              {{ topic.author }}
            </span>
            <span class="flex items-center gap-1">
              <MessageSquareIcon class="w-3 h-3" />
              {{ topic.replies }}
            </span>
            <span class="flex items-center gap-1">
              <EyeIcon class="w-3 h-3" />
              {{ topic.views }}
            </span>
            <span class="hidden sm:flex items-center gap-1">
              <ClockIcon class="w-3 h-3" />
              {{ topic.lastActivity }}
            </span>
          </div>
        </div>
        <span class="badge-gaming hidden sm:inline">{{ topic.category }}</span>
      </div>
    </div>
  `
}

// Player Card Component
const PlayerCard = {
  props: ['player', 'rank'],
  template: `
    <div class="glass-card p-6 card-hover-lift" :class="rankBorderClass">
      <div class="flex items-center gap-4 mb-4">
        <div class="relative">
          <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
            <span class="text-2xl font-bold text-white">{{ player.name.substring(0, 2).toUpperCase() }}</span>
          </div>
          <div class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" :class="rankBgClass">
            #{{ rank }}
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-bold text-lg truncate">{{ player.name }}</h3>
          <p class="text-sm opacity-60 truncate">{{ player.title }}</p>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 text-center mb-4">
        <div>
          <div class="text-lg font-bold text-green-500">{{ player.kills }}</div>
          <div class="text-xs opacity-60">Kills</div>
        </div>
        <div>
          <div class="text-lg font-bold text-red-500">{{ player.deaths }}</div>
          <div class="text-xs opacity-60">Deaths</div>
        </div>
        <div>
          <div class="text-lg font-bold text-yellow-500">{{ player.kd }}</div>
          <div class="text-xs opacity-60">K/D</div>
        </div>
      </div>

      <div>
        <div class="flex justify-between text-xs opacity-60 mb-1">
          <span>Seviye</span>
          <span>{{ player.level }}</span>
        </div>
        <div class="progress-bar h-2">
          <div class="progress-fill" :style="{ width: (player.level % 100) + '%' }"></div>
        </div>
      </div>
    </div>
  `,
  computed: {
    rankBorderClass() {
      const classes = { 1: 'border-yellow-500/50', 2: 'border-gray-400/50', 3: 'border-orange-600/50' }
      return classes[this.rank] || ''
    },
    rankBgClass() {
      const classes = { 1: 'bg-yellow-500', 2: 'bg-gray-400', 3: 'bg-orange-600' }
      return classes[this.rank] || 'bg-gray-500'
    }
  }
}

// Server Card Component
const ServerCard = {
  props: ['server'],
  components: { ServerIcon, UsersIcon, ActivityIcon },
  template: `
    <div class="glass-card p-6 card-hover-lift">
      <div class="flex items-start justify-between mb-4">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center">
            <ServerIcon class="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 class="font-bold truncate">{{ server.name }}</h3>
            <p class="text-sm opacity-60">{{ server.map }}</p>
          </div>
        </div>
        <div class="status-online"></div>
      </div>

      <div class="flex items-center justify-between text-sm mb-4">
        <div class="flex items-center gap-2 opacity-70">
          <UsersIcon class="w-4 h-4" />
          <span class="font-bold">{{ server.players }}/{{ server.maxPlayers }}</span>
        </div>
        <span class="badge-gaming">{{ server.mode }}</span>
      </div>

      <div class="flex items-center justify-between text-xs opacity-60">
        <span class="flex items-center gap-1">
          <ActivityIcon class="w-3 h-3" />
          {{ server.ping }}ms
        </span>
        <span>{{ server.country }}</span>
      </div>
    </div>
  `
}

// Event Card Component
const EventCard = {
  props: ['event'],
  components: { TrophyIcon, CalendarIcon, UsersIcon, CrownIcon },
  template: `
    <div class="glass-card p-6 card-hover-lift">
      <div class="flex items-start gap-4">
        <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center flex-shrink-0">
          <TrophyIcon class="w-8 h-8 text-white" />
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-bold text-lg mb-2">{{ event.title }}</h3>
          <p class="text-sm opacity-60 mb-3 truncate-2">{{ event.description }}</p>
          <div class="flex flex-wrap items-center gap-3 text-xs opacity-60">
            <span class="flex items-center gap-1">
              <CalendarIcon class="w-3 h-3" />
              {{ event.date }}
            </span>
            <span class="flex items-center gap-1">
              <UsersIcon class="w-3 h-3" />
              {{ event.participants }} katilimci
            </span>
            <span class="flex items-center gap-1 text-yellow-500">
              <CrownIcon class="w-3 h-3" />
              {{ event.prize }}
            </span>
          </div>
        </div>
      </div>
    </div>
  `
}

// ============================================
// Data
// ============================================

const stats = ref([
  { icon: markRaw(UsersIcon), value: '25K+', label: 'Uye', color: 'text-orange-500' },
  { icon: markRaw(ServerIcon), value: '150+', label: 'Aktif Sunucu', color: 'text-cyan-500' },
  { icon: markRaw(MessageSquareIcon), value: '50K+', label: 'Forum Konusu', color: 'text-purple-500' },
  { icon: markRaw(TrophyIcon), value: '3', label: 'Aktif Turnuva', color: 'text-yellow-500' }
])

const latestTopics = ref([
  { id: 1, title: 'CS 1.6 En Iyi Ayarlar 2024', author: 'ProGamer', replies: 47, views: 1230, lastActivity: '5 dk once', category: 'Rehberler' },
  { id: 2, title: 'Yeni Aim Map Koleksiyonu', author: 'MapMaker', replies: 23, views: 856, lastActivity: '1 saat once', category: 'Maplar' },
  { id: 3, title: 'Turnuva Kayitlari Basladi!', author: 'Admin159', replies: 89, views: 2341, lastActivity: '2 saat once', category: 'Duyurular' },
  { id: 4, title: 'En Iyi AWP Taktikleri', author: 'Sniper', replies: 34, views: 945, lastActivity: '3 saat once', category: 'Taktikler' }
])

const topPlayers = ref([
  { id: 1, name: 'ShadowKiller', title: 'Legendary Player', kills: 15234, deaths: 4521, kd: 3.37, level: 87 },
  { id: 2, name: 'HeadHunter', title: 'Elite Sniper', kills: 13890, deaths: 5123, kd: 2.71, level: 79 },
  { id: 3, name: 'FastFingers', title: 'Pro Rifler', kills: 12456, deaths: 5789, kd: 2.15, level: 73 }
])

const popularServers = ref([
  { id: 1, name: 'AGTR Public #1', map: 'de_dust2', players: 28, maxPlayers: 32, mode: 'Public', ping: 12, country: 'TR' },
  { id: 2, name: 'Deathmatch Arena', map: 'de_inferno', players: 24, maxPlayers: 24, mode: 'DM', ping: 8, country: 'TR' },
  { id: 3, name: 'Zombie Escape', map: 'zm_dust', players: 31, maxPlayers: 32, mode: 'Zombie', ping: 15, country: 'TR' }
])

const activeEvents = ref([
  { id: 1, title: '5v5 CS 1.6 Turnuvasi', description: 'Aylik sampiyonluk turnuvasi, kayitlar devam ediyor!', date: '25 Ocak 2024', participants: 16, prize: '500₺' },
  { id: 2, title: 'AWP Only Kupasi', description: 'Sadece AWP, en iyi sniper kim olacak?', date: '28 Ocak 2024', participants: 32, prize: '250₺' }
])
</script>

<style scoped>
/* Ensure proper stacking for glass cards */
.glass-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

/* Badge styling override for consistency */
.badge-gaming {
  font-size: 0.7rem;
  padding: 0.2rem 0.6rem;
}
</style>
