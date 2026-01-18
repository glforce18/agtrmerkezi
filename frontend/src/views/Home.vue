<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="py-16 lg:py-24">
      <div class="container-main text-center">
        <!-- Logo -->
        <div class="mb-8">
          <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 shadow-lg">
            <span class="text-4xl font-bold text-white">A</span>
          </div>
        </div>

        <!-- Title -->
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
          <span>AGTR</span>
          <span class="text-gradient-orange"> Merkezi</span>
        </h1>

        <!-- Subtitle -->
        <p class="text-lg opacity-70 mb-4">Counter-Strike 1.6 Turkiye Toplulugu</p>
        <p class="text-base opacity-50 mb-10 max-w-2xl mx-auto">
          Binlerce oyuncunun bulustugu, turnuvalarin duzenlendigi,
          sunucularin paylasildigi Half-Life evreninin en buyuk Turk toplulugu.
        </p>

        <!-- CTA Buttons -->
        <n-space justify="center">
          <router-link to="/forum">
            <n-button type="primary" size="large">
              <template #icon><n-icon><MessageSquare /></n-icon></template>
              Forum'a Katil
            </n-button>
          </router-link>
          <router-link to="/leaderboard">
            <n-button size="large">
              <template #icon><n-icon><Trophy /></n-icon></template>
              Siralamalar
            </n-button>
          </router-link>
          <router-link to="/servers">
            <n-button size="large">
              <template #icon><n-icon><Server /></n-icon></template>
              Sunucular
            </n-button>
          </router-link>
        </n-space>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-16 max-w-4xl mx-auto">
          <n-card v-for="stat in stats" :key="stat.label" size="small">
            <div class="text-center">
              <n-icon :component="stat.icon" size="28" :color="stat.color" class="mb-2" />
              <div class="text-2xl font-bold">{{ stat.value }}</div>
              <div class="text-sm opacity-60">{{ stat.label }}</div>
            </div>
          </n-card>
        </div>
      </div>
    </section>

    <!-- Latest Forum Topics -->
    <section class="py-12" :class="isDark ? 'bg-zinc-900/50' : 'bg-zinc-50'">
      <div class="container-main">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold flex items-center gap-2">
            <n-icon :component="MessageSquare" color="#f97316" size="28" />
            Son Forum Konulari
          </h2>
          <router-link to="/forum">
            <n-button text type="primary">
              Tumunu Gor
              <template #icon><n-icon><ArrowRight /></n-icon></template>
            </n-button>
          </router-link>
        </div>

        <n-list bordered>
          <n-list-item v-for="topic in latestTopics" :key="topic.id">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center flex-shrink-0">
                <n-icon :component="MessageSquare" color="white" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="font-semibold truncate">{{ topic.title }}</div>
                <n-space size="small" class="text-xs opacity-60">
                  <span>{{ topic.author }}</span>
                  <span>{{ topic.replies }} yanit</span>
                  <span>{{ topic.views }} goruntulenme</span>
                </n-space>
              </div>
              <n-tag type="warning" size="small">{{ topic.category }}</n-tag>
            </div>
          </n-list-item>
        </n-list>
      </div>
    </section>

    <!-- Top Players -->
    <section class="py-12">
      <div class="container-main">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold flex items-center gap-2">
            <n-icon :component="Trophy" color="#f97316" size="28" />
            En Iyi Oyuncular
          </h2>
          <router-link to="/leaderboard">
            <n-button text type="primary">
              Tum Siralama
              <template #icon><n-icon><ArrowRight /></n-icon></template>
            </n-button>
          </router-link>
        </div>

        <div class="grid md:grid-cols-3 gap-4">
          <n-card v-for="(player, index) in topPlayers" :key="player.id">
            <div class="flex items-center gap-4 mb-4">
              <div class="relative">
                <n-avatar :size="56" round :style="{ background: 'linear-gradient(135deg, #f97316, #ea580c)' }">
                  {{ player.name.substring(0, 2).toUpperCase() }}
                </n-avatar>
                <n-tag
                  :type="index === 0 ? 'warning' : index === 1 ? 'default' : 'error'"
                  size="small"
                  round
                  class="absolute -bottom-1 -right-1"
                >
                  #{{ index + 1 }}
                </n-tag>
              </div>
              <div class="flex-1 min-w-0">
                <div class="font-bold truncate">{{ player.name }}</div>
                <div class="text-sm opacity-60 truncate">{{ player.title }}</div>
              </div>
            </div>

            <n-grid :cols="3" :x-gap="8">
              <n-gi>
                <n-statistic label="Kills" :value="player.kills">
                  <template #prefix><span class="text-green-500">+</span></template>
                </n-statistic>
              </n-gi>
              <n-gi>
                <n-statistic label="Deaths" :value="player.deaths">
                  <template #prefix><span class="text-red-500">-</span></template>
                </n-statistic>
              </n-gi>
              <n-gi>
                <n-statistic label="K/D" :value="player.kd" />
              </n-gi>
            </n-grid>

            <n-progress
              type="line"
              :percentage="player.level % 100"
              :indicator-placement="'inside'"
              class="mt-4"
            />
            <div class="text-xs opacity-60 mt-1">Seviye {{ player.level }}</div>
          </n-card>
        </div>
      </div>
    </section>

    <!-- Popular Servers -->
    <section class="py-12" :class="isDark ? 'bg-zinc-900/50' : 'bg-zinc-50'">
      <div class="container-main">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold flex items-center gap-2">
            <n-icon :component="Server" color="#f97316" size="28" />
            Populer Sunucular
          </h2>
          <router-link to="/servers">
            <n-button text type="primary">
              Tum Sunucular
              <template #icon><n-icon><ArrowRight /></n-icon></template>
            </n-button>
          </router-link>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <n-card v-for="server in popularServers" :key="server.id">
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center">
                  <n-icon :component="Server" color="white" />
                </div>
                <div>
                  <div class="font-semibold">{{ server.name }}</div>
                  <div class="text-sm opacity-60">{{ server.map }}</div>
                </div>
              </div>
              <n-badge dot type="success" />
            </div>

            <div class="flex items-center justify-between text-sm">
              <n-space size="small" align="center">
                <n-icon :component="Users" size="16" />
                <span class="font-semibold">{{ server.players }}/{{ server.maxPlayers }}</span>
              </n-space>
              <n-tag type="info" size="small">{{ server.mode }}</n-tag>
            </div>

            <div class="flex items-center justify-between text-xs opacity-60 mt-3">
              <span>{{ server.ping }}ms ping</span>
              <span>{{ server.country }}</span>
            </div>
          </n-card>
        </div>
      </div>
    </section>

    <!-- Active Events -->
    <section class="py-12">
      <div class="container-main">
        <h2 class="text-2xl font-bold flex items-center gap-2 justify-center mb-6">
          <n-icon :component="Calendar" color="#f97316" size="28" />
          Aktif Turnuvalar
        </h2>

        <div class="grid md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          <n-card v-for="event in activeEvents" :key="event.id">
            <div class="flex items-start gap-4">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <n-icon :component="Trophy" color="white" size="28" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="font-bold text-lg mb-1">{{ event.title }}</div>
                <div class="text-sm opacity-60 mb-3 line-clamp-2">{{ event.description }}</div>
                <n-space size="small">
                  <n-tag size="small">
                    <template #icon><n-icon :component="Calendar" /></template>
                    {{ event.date }}
                  </n-tag>
                  <n-tag size="small">
                    <template #icon><n-icon :component="Users" /></template>
                    {{ event.participants }} katilimci
                  </n-tag>
                  <n-tag type="warning" size="small">
                    <template #icon><n-icon :component="Crown" /></template>
                    {{ event.prize }}
                  </n-tag>
                </n-space>
              </div>
            </div>
          </n-card>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue'
import { useThemeStore } from '@/stores/theme'
import {
  Server,
  MessageSquare,
  Trophy,
  Users,
  Calendar,
  ArrowRight,
  Crown
} from 'lucide-vue-next'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

const stats = ref([
  { icon: markRaw(Users), value: '25K+', label: 'Uye', color: '#f97316' },
  { icon: markRaw(Server), value: '150+', label: 'Aktif Sunucu', color: '#06b6d4' },
  { icon: markRaw(MessageSquare), value: '50K+', label: 'Forum Konusu', color: '#8b5cf6' },
  { icon: markRaw(Trophy), value: '3', label: 'Aktif Turnuva', color: '#eab308' }
])

const latestTopics = ref([
  { id: 1, title: 'CS 1.6 En Iyi Ayarlar 2024', author: 'ProGamer', replies: 47, views: 1230, category: 'Rehberler' },
  { id: 2, title: 'Yeni Aim Map Koleksiyonu', author: 'MapMaker', replies: 23, views: 856, category: 'Maplar' },
  { id: 3, title: 'Turnuva Kayitlari Basladi!', author: 'Admin159', replies: 89, views: 2341, category: 'Duyurular' },
  { id: 4, title: 'En Iyi AWP Taktikleri', author: 'Sniper', replies: 34, views: 945, category: 'Taktikler' }
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
  { id: 1, title: '5v5 CS 1.6 Turnuvasi', description: 'Aylik sampiyonluk turnuvasi, kayitlar devam ediyor!', date: '25 Ocak 2024', participants: 16, prize: '500 TL' },
  { id: 2, title: 'AWP Only Kupasi', description: 'Sadece AWP, en iyi sniper kim olacak?', date: '28 Ocak 2024', participants: 32, prize: '250 TL' }
])
</script>
