<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="mb-12 text-center animate-slide-down">
        <h1 class="text-5xl font-display font-bold mb-4">
          <span class="neon-text">Lider Tablosu</span>
        </h1>
        <p class="text-xl opacity-60 max-w-2xl mx-auto">
          En iyi oyuncular, popüler sunucular ve aktif kullanıcılar
        </p>
      </div>

      <!-- Category Tabs -->
      <div class="mb-8 animate-slide-up">
        <div class="tabs tabs-boxed bg-base-200/50 backdrop-blur-sm justify-center">
          <a
            class="tab"
            :class="{ 'tab-active': activeCategory === 'players' }"
            @click="activeCategory = 'players'"
          >
            <TrophyIcon class="w-4 h-4 mr-2" />
            En İyi Oyuncular
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeCategory === 'servers' }"
            @click="activeCategory = 'servers'"
          >
            <ServerIcon class="w-4 h-4 mr-2" />
            Popüler Sunucular
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': activeCategory === 'users' }"
            @click="activeCategory = 'users'"
          >
            <UsersIcon class="w-4 h-4 mr-2" />
            Aktif Kullanıcılar
          </a>
        </div>
      </div>

      <!-- Filters -->
      <BaseCard variant="glass" class="mb-6 animate-slide-up" style="animation-delay: 0.1s">
        <div class="p-4">
          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1">
              <BaseInput
                v-model="searchQuery"
                placeholder="Ara..."
                :icon="SearchIcon"
              />
            </div>
            <div class="flex gap-2">
              <select v-model="timeFilter" class="select select-bordered select-sm bg-base-200">
                <option value="all">Tüm Zamanlar</option>
                <option value="today">Bugün</option>
                <option value="week">Bu Hafta</option>
                <option value="month">Bu Ay</option>
              </select>
              <select v-model="sortBy" class="select select-bordered select-sm bg-base-200">
                <option value="rank">Sıralama</option>
                <option value="score">Skor</option>
                <option value="kills">Kills</option>
                <option value="accuracy">İsabet</option>
              </select>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Top 3 Podium (Only for players) -->
      <div v-if="activeCategory === 'players' && filteredData.length >= 3" class="mb-8 animate-slide-up" style="animation-delay: 0.2s">
        <div class="grid grid-cols-3 gap-4 max-w-4xl mx-auto">
          <!-- 2nd Place -->
          <div class="flex flex-col items-center mt-12">
            <BaseCard variant="glass" class="card-hover text-center w-full relative">
              <div class="absolute -top-6 left-1/2 -translate-x-1/2">
                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-slate-400 to-slate-600 flex items-center justify-center border-4 border-base-300 shadow-lg">
                  <span class="text-2xl font-bold text-white">2</span>
                </div>
              </div>
              <div class="p-6 pt-8">
                <div class="avatar mb-3">
                  <div class="w-20 h-20 rounded-full ring ring-slate-400 ring-offset-2 ring-offset-slate-900">
                    <img :src="filteredData[1].avatar" />
                  </div>
                </div>
                <h3 class="font-bold text-lg mb-1">{{ filteredData[1].name }}</h3>
                <div class="badge badge-sm badge-ghost mb-3">{{ filteredData[1].rank }}</div>
                <div class="text-3xl font-bold opacity-60 mb-2">{{ filteredData[1].score }}</div>
                <div class="text-xs opacity-50">Skor</div>
              </div>
            </BaseCard>
          </div>

          <!-- 1st Place -->
          <div class="flex flex-col items-center">
            <BaseCard variant="glass" class="card-hover text-center w-full relative border-2 border-primary">
              <div class="absolute -top-8 left-1/2 -translate-x-1/2">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center border-4 border-base-300 shadow-xl animate-pulse-slow">
                  <CrownIcon class="w-8 h-8 text-white" />
                </div>
              </div>
              <div class="p-6 pt-10">
                <div class="avatar mb-3">
                  <div class="w-24 h-24 rounded-full ring ring-primary ring-offset-4 ring-offset-slate-900">
                    <img :src="filteredData[0].avatar" />
                  </div>
                </div>
                <h3 class="font-bold text-xl mb-1">{{ filteredData[0].name }}</h3>
                <div class="badge badge-sm badge-primary mb-3">{{ filteredData[0].rank }}</div>
                <div class="text-4xl font-bold text-primary mb-2">{{ filteredData[0].score }}</div>
                <div class="text-xs opacity-50">Skor</div>
              </div>
            </BaseCard>
          </div>

          <!-- 3rd Place -->
          <div class="flex flex-col items-center mt-12">
            <BaseCard variant="glass" class="card-hover text-center w-full relative">
              <div class="absolute -top-6 left-1/2 -translate-x-1/2">
                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-amber-700 to-amber-900 flex items-center justify-center border-4 border-base-300 shadow-lg">
                  <span class="text-2xl font-bold text-white">3</span>
                </div>
              </div>
              <div class="p-6 pt-8">
                <div class="avatar mb-3">
                  <div class="w-20 h-20 rounded-full ring ring-amber-700 ring-offset-2 ring-offset-slate-900">
                    <img :src="filteredData[2].avatar" />
                  </div>
                </div>
                <h3 class="font-bold text-lg mb-1">{{ filteredData[2].name }}</h3>
                <div class="badge badge-sm badge-ghost mb-3">{{ filteredData[2].rank }}</div>
                <div class="text-3xl font-bold text-amber-700 mb-2">{{ filteredData[2].score }}</div>
                <div class="text-xs opacity-50">Skor</div>
              </div>
            </BaseCard>
          </div>
        </div>
      </div>

      <!-- Leaderboard Table -->
      <BaseCard variant="glass" class="animate-slide-up" style="animation-delay: 0.3s">
        <div class="overflow-x-auto">
          <table class="table">
            <thead>
              <tr>
                <th class="w-16">Sıra</th>
                <th>{{ activeCategory === 'players' ? 'Oyuncu' : activeCategory === 'servers' ? 'Sunucu' : 'Kullanıcı' }}</th>
                <th v-if="activeCategory === 'players'">K/D</th>
                <th v-if="activeCategory === 'players'">İsabet</th>
                <th v-if="activeCategory === 'servers'">Oyuncular</th>
                <th v-if="activeCategory === 'servers'">Map</th>
                <th v-if="activeCategory === 'users'">Sunucu</th>
                <th v-if="activeCategory === 'users'">Forum</th>
                <th>Skor</th>
                <th class="w-32">İşlemler</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in paginatedData"
                :key="item.id"
                class="hover"
                :class="{ 'bg-primary/5': index < 3 }"
              >
                <td>
                  <div class="flex items-center justify-center">
                    <div
                      v-if="item.position <= 3"
                      :class="[
                        'w-8 h-8 rounded-full flex items-center justify-center font-bold text-white',
                        item.position === 1 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600' :
                        item.position === 2 ? 'bg-gradient-to-br from-slate-400 to-slate-600' :
                        'bg-gradient-to-br from-amber-700 to-amber-900'
                      ]"
                    >
                      {{ item.position }}
                    </div>
                    <span v-else class="font-semibold opacity-60">#{{ item.position }}</span>
                  </div>
                </td>
                <td>
                  <div class="flex items-center gap-3">
                    <div class="avatar" v-if="activeCategory !== 'servers'">
                      <div class="w-12 h-12 rounded-full ring ring-primary ring-offset-2 ring-offset-slate-900">
                        <img :src="item.avatar" />
                      </div>
                    </div>
                    <div class="avatar" v-else>
                      <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                        <ServerIcon class="w-6 h-6 text-white" />
                      </div>
                    </div>
                    <div>
                      <div class="font-bold">{{ item.name }}</div>
                      <div class="text-sm opacity-50">{{ item.rank || item.region || item.role }}</div>
                    </div>
                  </div>
                </td>
                <td v-if="activeCategory === 'players'">
                  <span class="font-mono font-semibold">{{ item.kd }}</span>
                </td>
                <td v-if="activeCategory === 'players'">
                  <div class="flex items-center gap-2">
                    <div class="w-20 bg-base-200/50 rounded-full h-2">
                      <div
                        class="bg-gradient-to-r from-primary to-secondary h-full rounded-full"
                        :style="{ width: `${item.accuracy}%` }"
                      ></div>
                    </div>
                    <span class="text-sm font-semibold">{{ item.accuracy }}%</span>
                  </div>
                </td>
                <td v-if="activeCategory === 'servers'">
                  <span class="font-semibold">{{ item.players }}/{{ item.maxPlayers }}</span>
                </td>
                <td v-if="activeCategory === 'servers'">
                  <code class="text-xs text-primary">{{ item.map }}</code>
                </td>
                <td v-if="activeCategory === 'users'">
                  <span class="badge badge-sm badge-primary">{{ item.servers }}</span>
                </td>
                <td v-if="activeCategory === 'users'">
                  <span class="badge badge-sm badge-secondary">{{ item.posts }}</span>
                </td>
                <td>
                  <div class="flex items-center gap-2">
                    <TrendingUpIcon class="w-4 h-4 text-success" />
                    <span class="font-bold text-lg">{{ item.score }}</span>
                  </div>
                </td>
                <td>
                  <div class="flex gap-1">
                    <button class="btn btn-xs btn-ghost" title="Profil">
                      <UserIcon class="w-3 h-3" />
                    </button>
                    <button class="btn btn-xs btn-ghost" title="İstatistikler">
                      <BarChartIcon class="w-3 h-3" />
                    </button>
                    <button class="btn btn-xs btn-ghost" title="Paylaş">
                      <ShareIcon class="w-3 h-3" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="flex justify-center p-6 border-t border-base-300">
          <div class="join">
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              «
            </button>
            <button
              v-for="page in totalPages"
              :key="page"
              class="join-item btn btn-sm"
              :class="{ 'btn-active': currentPage === page }"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              »
            </button>
          </div>
        </div>
      </BaseCard>

      <!-- Stats Cards -->
      <div class="grid md:grid-cols-3 gap-6 mt-8 animate-slide-up" style="animation-delay: 0.4s">
        <BaseCard variant="glass" class="card-hover">
          <div class="p-6">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                <TrophyIcon class="w-8 h-8 text-primary" />
              </div>
              <div>
                <p class="text-sm opacity-60">Toplam Yarışmacı</p>
                <h3 class="text-2xl font-bold">{{ totalCompetitors }}</h3>
              </div>
            </div>
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="p-6">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 rounded-full bg-secondary/20 flex items-center justify-center">
                <ActivityIcon class="w-8 h-8 text-secondary" />
              </div>
              <div>
                <p class="text-sm opacity-60">Aktif Şu An</p>
                <h3 class="text-2xl font-bold">{{ activeNow }}</h3>
              </div>
            </div>
          </div>
        </BaseCard>

        <BaseCard variant="glass" class="card-hover">
          <div class="p-6">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center">
                <ZapIcon class="w-8 h-8 text-accent" />
              </div>
              <div>
                <p class="text-sm opacity-60">En Yüksek Skor</p>
                <h3 class="text-2xl font-bold">{{ highestScore }}</h3>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import {
  TrophyIcon,
  ServerIcon,
  UsersIcon,
  SearchIcon,
  CrownIcon,
  TrendingUpIcon,
  UserIcon,
  BarChart3Icon as BarChartIcon,
  Share2Icon as ShareIcon,
  ActivityIcon,
  ZapIcon
} from 'lucide-vue-next'

const activeCategory = ref('players')
const searchQuery = ref('')
const timeFilter = ref('all')
const sortBy = ref('rank')
const currentPage = ref(1)
const itemsPerPage = 10

// Mock data for players
const playersData = ref([
  {
    id: 1,
    position: 1,
    name: 'ProGamer_TR',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player1',
    rank: 'Global Elite',
    score: 9842,
    kills: 15234,
    deaths: 4521,
    kd: '3.37',
    accuracy: 78
  },
  {
    id: 2,
    position: 2,
    name: 'SniperKing',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player2',
    rank: 'Supreme Master',
    score: 8923,
    kills: 13456,
    deaths: 4123,
    kd: '3.26',
    accuracy: 82
  },
  {
    id: 3,
    position: 3,
    name: 'HeadShot_Pro',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player3',
    rank: 'Legendary Eagle',
    score: 8234,
    kills: 12345,
    deaths: 3987,
    kd: '3.10',
    accuracy: 75
  },
  {
    id: 4,
    position: 4,
    name: 'CS_Legend',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player4',
    rank: 'Distinguished Master',
    score: 7845,
    kills: 11234,
    deaths: 3654,
    kd: '3.07',
    accuracy: 73
  },
  {
    id: 5,
    position: 5,
    name: 'AimBot_Wannabe',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player5',
    rank: 'Master Guardian Elite',
    score: 7456,
    kills: 10987,
    deaths: 3598,
    kd: '3.05',
    accuracy: 71
  },
  {
    id: 6,
    position: 6,
    name: 'Clutch_Master',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player6',
    rank: 'Master Guardian',
    score: 7123,
    kills: 10456,
    deaths: 3456,
    kd: '3.02',
    accuracy: 69
  },
  {
    id: 7,
    position: 7,
    name: 'Spray_Control',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player7',
    rank: 'Gold Nova Master',
    score: 6789,
    kills: 9876,
    deaths: 3289,
    kd: '3.00',
    accuracy: 68
  },
  {
    id: 8,
    position: 8,
    name: 'AWP_Dragon',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player8',
    rank: 'Gold Nova III',
    score: 6456,
    kills: 9345,
    deaths: 3123,
    kd: '2.99',
    accuracy: 80
  },
  {
    id: 9,
    position: 9,
    name: 'Flash_Bang',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player9',
    rank: 'Gold Nova II',
    score: 6123,
    kills: 8987,
    deaths: 3012,
    kd: '2.98',
    accuracy: 66
  },
  {
    id: 10,
    position: 10,
    name: 'Smoke_Criminal',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player10',
    rank: 'Gold Nova I',
    score: 5876,
    kills: 8654,
    deaths: 2923,
    kd: '2.96',
    accuracy: 65
  }
])

// Mock data for servers
const serversData = ref([
  {
    id: 1,
    position: 1,
    name: 'AGTR Public #1',
    region: 'EU West',
    score: 9876,
    players: 28,
    maxPlayers: 32,
    map: 'de_dust2'
  },
  {
    id: 2,
    position: 2,
    name: 'Pro Arena DM',
    region: 'EU Central',
    score: 8954,
    players: 24,
    maxPlayers: 24,
    map: 'de_inferno'
  },
  {
    id: 3,
    position: 3,
    name: 'Zombie Mod Paradise',
    region: 'US East',
    score: 8234,
    players: 31,
    maxPlayers: 32,
    map: 'zm_dust'
  }
])

// Mock data for users
const usersData = ref([
  {
    id: 1,
    position: 1,
    name: 'AdminUser',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin1',
    role: 'Administrator',
    score: 15234,
    servers: 12,
    posts: 856
  },
  {
    id: 2,
    position: 2,
    name: 'ModeratorPro',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin2',
    role: 'Moderator',
    score: 12456,
    servers: 8,
    posts: 623
  },
  {
    id: 3,
    position: 3,
    name: 'CommunityLead',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin3',
    role: 'Community Manager',
    score: 10987,
    servers: 5,
    posts: 1234
  }
])

const currentData = computed(() => {
  switch (activeCategory.value) {
    case 'players':
      return playersData.value
    case 'servers':
      return serversData.value
    case 'users':
      return usersData.value
    default:
      return []
  }
})

const filteredData = computed(() => {
  let data = [...currentData.value]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      item.name.toLowerCase().includes(query)
    )
  }

  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / itemsPerPage)
})

const totalCompetitors = computed(() => {
  return currentData.value.length
})

const activeNow = computed(() => {
  return Math.floor(currentData.value.length * 0.65)
})

const highestScore = computed(() => {
  if (currentData.value.length === 0) return 0
  return currentData.value[0].score
})
</script>

<style scoped>
.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

@keyframes pulse-slow {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 2s ease-in-out infinite;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-down {
  animation: slideDown 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}
</style>
