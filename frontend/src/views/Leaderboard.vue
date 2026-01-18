<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="mb-12 text-center">
        <h1 class="text-5xl font-display font-bold mb-4">
          <span class="text-gradient">Lider Tablosu</span>
        </h1>
        <p class="text-xl text-gray-400 max-w-2xl mx-auto">
          En iyi oyuncular, popüler sunucular ve aktif kullanıcılar
        </p>
      </div>

      <!-- Category Tabs -->
      <div class="mb-8 flex justify-center">
        <n-tabs v-model:value="activeCategory" type="segment">
          <n-tab name="players">
            <div class="flex items-center gap-2">
              <TrophyIcon class="w-4 h-4" />
              <span>En İyi Oyuncular</span>
            </div>
          </n-tab>
          <n-tab name="servers">
            <div class="flex items-center gap-2">
              <ServerIcon class="w-4 h-4" />
              <span>Popüler Sunucular</span>
            </div>
          </n-tab>
          <n-tab name="users">
            <div class="flex items-center gap-2">
              <UsersIcon class="w-4 h-4" />
              <span>Aktif Kullanıcılar</span>
            </div>
          </n-tab>
        </n-tabs>
      </div>

      <!-- Filters -->
      <n-card class="glass-card mb-6">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <n-input v-model:value="searchQuery" placeholder="Ara...">
              <template #prefix>
                <SearchIcon class="w-4 h-4 text-gray-400" />
              </template>
            </n-input>
          </div>
          <div class="flex gap-2">
            <n-select v-model:value="timeFilter" :options="timeOptions" style="width: 140px;" />
            <n-select v-model:value="sortBy" :options="sortOptions" style="width: 140px;" />
          </div>
        </div>
      </n-card>

      <!-- Top 3 Podium (Only for players) -->
      <div v-if="activeCategory === 'players' && filteredData.length >= 3" class="mb-8">
        <div class="grid grid-cols-3 gap-4 max-w-4xl mx-auto">
          <!-- 2nd Place -->
          <div class="flex flex-col items-center mt-12">
            <n-card class="glass-card text-center w-full relative podium-card">
              <div class="absolute -top-6 left-1/2 -translate-x-1/2">
                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-slate-400 to-slate-600 flex items-center justify-center border-4 border-gray-800 shadow-lg">
                  <span class="text-2xl font-bold text-white">2</span>
                </div>
              </div>
              <div class="pt-8">
                <n-avatar
                  round
                  :size="80"
                  :src="filteredData[1].avatar"
                  class="mb-3 ring-2 ring-slate-400 ring-offset-2 ring-offset-gray-900"
                />
                <h3 class="font-bold text-lg mb-1">{{ filteredData[1].name }}</h3>
                <n-tag size="small" :bordered="false" class="mb-3">{{ filteredData[1].rank }}</n-tag>
                <div class="text-3xl font-bold text-gray-400 mb-2">{{ filteredData[1].score }}</div>
                <div class="text-xs text-gray-500">Skor</div>
              </div>
            </n-card>
          </div>

          <!-- 1st Place -->
          <div class="flex flex-col items-center">
            <n-card class="glass-card text-center w-full relative border-2 border-orange-500 podium-card">
              <div class="absolute -top-8 left-1/2 -translate-x-1/2">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center border-4 border-gray-800 shadow-xl animate-pulse">
                  <CrownIcon class="w-8 h-8 text-white" />
                </div>
              </div>
              <div class="pt-10">
                <n-avatar
                  round
                  :size="96"
                  :src="filteredData[0].avatar"
                  class="mb-3 ring-2 ring-orange-500 ring-offset-4 ring-offset-gray-900"
                />
                <h3 class="font-bold text-xl mb-1">{{ filteredData[0].name }}</h3>
                <n-tag type="primary" size="small" class="mb-3">{{ filteredData[0].rank }}</n-tag>
                <div class="text-4xl font-bold text-orange-500 mb-2">{{ filteredData[0].score }}</div>
                <div class="text-xs text-gray-500">Skor</div>
              </div>
            </n-card>
          </div>

          <!-- 3rd Place -->
          <div class="flex flex-col items-center mt-12">
            <n-card class="glass-card text-center w-full relative podium-card">
              <div class="absolute -top-6 left-1/2 -translate-x-1/2">
                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-amber-700 to-amber-900 flex items-center justify-center border-4 border-gray-800 shadow-lg">
                  <span class="text-2xl font-bold text-white">3</span>
                </div>
              </div>
              <div class="pt-8">
                <n-avatar
                  round
                  :size="80"
                  :src="filteredData[2].avatar"
                  class="mb-3 ring-2 ring-amber-700 ring-offset-2 ring-offset-gray-900"
                />
                <h3 class="font-bold text-lg mb-1">{{ filteredData[2].name }}</h3>
                <n-tag size="small" :bordered="false" class="mb-3">{{ filteredData[2].rank }}</n-tag>
                <div class="text-3xl font-bold text-amber-700 mb-2">{{ filteredData[2].score }}</div>
                <div class="text-xs text-gray-500">Skor</div>
              </div>
            </n-card>
          </div>
        </div>
      </div>

      <!-- Leaderboard Table -->
      <n-card class="glass-card">
        <n-data-table
          :columns="tableColumns"
          :data="paginatedData"
          :bordered="false"
          :single-line="false"
          :row-class-name="getRowClass"
        />

        <!-- Pagination -->
        <div class="flex justify-center p-6 border-t border-white/10">
          <n-pagination
            v-model:page="currentPage"
            :page-count="totalPages"
            show-quick-jumper
          />
        </div>
      </n-card>

      <!-- Stats Cards -->
      <div class="grid md:grid-cols-3 gap-6 mt-8">
        <n-card class="glass-card stat-card">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-full bg-orange-500/20 flex items-center justify-center">
              <TrophyIcon class="w-8 h-8 text-orange-500" />
            </div>
            <div>
              <p class="text-sm text-gray-400">Toplam Yarışmacı</p>
              <h3 class="text-2xl font-bold">{{ totalCompetitors }}</h3>
            </div>
          </div>
        </n-card>

        <n-card class="glass-card stat-card">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center">
              <ActivityIcon class="w-8 h-8 text-purple-500" />
            </div>
            <div>
              <p class="text-sm text-gray-400">Aktif Şu An</p>
              <h3 class="text-2xl font-bold">{{ activeNow }}</h3>
            </div>
          </div>
        </n-card>

        <n-card class="glass-card stat-card">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-full bg-cyan-500/20 flex items-center justify-center">
              <ZapIcon class="w-8 h-8 text-cyan-500" />
            </div>
            <div>
              <p class="text-sm text-gray-400">En Yüksek Skor</p>
              <h3 class="text-2xl font-bold">{{ highestScore }}</h3>
            </div>
          </div>
        </n-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { NAvatar, NTag, NProgress } from 'naive-ui'
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

const timeOptions = [
  { label: 'Tüm Zamanlar', value: 'all' },
  { label: 'Bugün', value: 'today' },
  { label: 'Bu Hafta', value: 'week' },
  { label: 'Bu Ay', value: 'month' }
]

const sortOptions = [
  { label: 'Sıralama', value: 'rank' },
  { label: 'Skor', value: 'score' },
  { label: 'Kills', value: 'kills' },
  { label: 'İsabet', value: 'accuracy' }
]

// Dynamic table columns based on category
const tableColumns = computed(() => {
  const baseColumns = [
    {
      title: 'Sıra',
      key: 'position',
      width: 80,
      render: (row) => {
        if (row.position <= 3) {
          const bgClass = row.position === 1 ? 'from-yellow-400 to-yellow-600' :
                         row.position === 2 ? 'from-slate-400 to-slate-600' :
                         'from-amber-700 to-amber-900'
          return h('div', {
            class: `w-8 h-8 rounded-full flex items-center justify-center font-bold text-white bg-gradient-to-br ${bgClass}`
          }, row.position)
        }
        return h('span', { class: 'font-semibold text-gray-500' }, `#${row.position}`)
      }
    },
    {
      title: activeCategory.value === 'players' ? 'Oyuncu' : activeCategory.value === 'servers' ? 'Sunucu' : 'Kullanıcı',
      key: 'name',
      render: (row) => {
        return h('div', { class: 'flex items-center gap-3' }, [
          activeCategory.value !== 'servers' ?
            h(NAvatar, { round: true, size: 48, src: row.avatar }) :
            h('div', { class: 'w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500 to-purple-500 flex items-center justify-center' }, [
              h(ServerIcon, { class: 'w-6 h-6 text-white' })
            ]),
          h('div', {}, [
            h('div', { class: 'font-bold' }, row.name),
            h('div', { class: 'text-sm text-gray-500' }, row.rank || row.region || row.role)
          ])
        ])
      }
    }
  ]

  if (activeCategory.value === 'players') {
    baseColumns.push(
      {
        title: 'K/D',
        key: 'kd',
        render: (row) => h('span', { class: 'font-mono font-semibold' }, row.kd)
      },
      {
        title: 'İsabet',
        key: 'accuracy',
        render: (row) => h('div', { class: 'flex items-center gap-2' }, [
          h(NProgress, { type: 'line', percentage: row.accuracy, showIndicator: false, status: 'warning' }),
          h('span', { class: 'text-sm font-semibold' }, `${row.accuracy}%`)
        ])
      }
    )
  }

  if (activeCategory.value === 'servers') {
    baseColumns.push(
      {
        title: 'Oyuncular',
        key: 'players',
        render: (row) => h('span', { class: 'font-semibold' }, `${row.players}/${row.maxPlayers}`)
      },
      {
        title: 'Map',
        key: 'map',
        render: (row) => h('code', { class: 'text-xs text-orange-500' }, row.map)
      }
    )
  }

  if (activeCategory.value === 'users') {
    baseColumns.push(
      {
        title: 'Sunucu',
        key: 'servers',
        render: (row) => h(NTag, { type: 'primary', size: 'small' }, () => row.servers)
      },
      {
        title: 'Forum',
        key: 'posts',
        render: (row) => h(NTag, { type: 'info', size: 'small' }, () => row.posts)
      }
    )
  }

  baseColumns.push({
    title: 'Skor',
    key: 'score',
    render: (row) => h('div', { class: 'flex items-center gap-2' }, [
      h(TrendingUpIcon, { class: 'w-4 h-4 text-green-500' }),
      h('span', { class: 'font-bold text-lg' }, row.score)
    ])
  })

  return baseColumns
})

const getRowClass = (row, index) => {
  return index < 3 ? 'bg-orange-500/5' : ''
}

// Mock data for players
const playersData = ref([
  { id: 1, position: 1, name: 'ProGamer_TR', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player1', rank: 'Global Elite', score: 9842, kills: 15234, deaths: 4521, kd: '3.37', accuracy: 78 },
  { id: 2, position: 2, name: 'SniperKing', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player2', rank: 'Supreme Master', score: 8923, kills: 13456, deaths: 4123, kd: '3.26', accuracy: 82 },
  { id: 3, position: 3, name: 'HeadShot_Pro', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player3', rank: 'Legendary Eagle', score: 8234, kills: 12345, deaths: 3987, kd: '3.10', accuracy: 75 },
  { id: 4, position: 4, name: 'CS_Legend', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player4', rank: 'Distinguished Master', score: 7845, kills: 11234, deaths: 3654, kd: '3.07', accuracy: 73 },
  { id: 5, position: 5, name: 'AimBot_Wannabe', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player5', rank: 'Master Guardian Elite', score: 7456, kills: 10987, deaths: 3598, kd: '3.05', accuracy: 71 },
  { id: 6, position: 6, name: 'Clutch_Master', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player6', rank: 'Master Guardian', score: 7123, kills: 10456, deaths: 3456, kd: '3.02', accuracy: 69 },
  { id: 7, position: 7, name: 'Spray_Control', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player7', rank: 'Gold Nova Master', score: 6789, kills: 9876, deaths: 3289, kd: '3.00', accuracy: 68 },
  { id: 8, position: 8, name: 'AWP_Dragon', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player8', rank: 'Gold Nova III', score: 6456, kills: 9345, deaths: 3123, kd: '2.99', accuracy: 80 },
  { id: 9, position: 9, name: 'Flash_Bang', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player9', rank: 'Gold Nova II', score: 6123, kills: 8987, deaths: 3012, kd: '2.98', accuracy: 66 },
  { id: 10, position: 10, name: 'Smoke_Criminal', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=player10', rank: 'Gold Nova I', score: 5876, kills: 8654, deaths: 2923, kd: '2.96', accuracy: 65 }
])

const serversData = ref([
  { id: 1, position: 1, name: 'AGTR Public #1', region: 'EU West', score: 9876, players: 28, maxPlayers: 32, map: 'de_dust2' },
  { id: 2, position: 2, name: 'Pro Arena DM', region: 'EU Central', score: 8954, players: 24, maxPlayers: 24, map: 'de_inferno' },
  { id: 3, position: 3, name: 'Zombie Mod Paradise', region: 'US East', score: 8234, players: 31, maxPlayers: 32, map: 'zm_dust' }
])

const usersData = ref([
  { id: 1, position: 1, name: 'AdminUser', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin1', role: 'Administrator', score: 15234, servers: 12, posts: 856 },
  { id: 2, position: 2, name: 'ModeratorPro', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin2', role: 'Moderator', score: 12456, servers: 8, posts: 623 },
  { id: 3, position: 3, name: 'CommunityLead', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin3', role: 'Community Manager', score: 10987, servers: 5, posts: 1234 }
])

const currentData = computed(() => {
  switch (activeCategory.value) {
    case 'players': return playersData.value
    case 'servers': return serversData.value
    case 'users': return usersData.value
    default: return []
  }
})

const filteredData = computed(() => {
  let data = [...currentData.value]
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item => item.name.toLowerCase().includes(query))
  }
  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / itemsPerPage))
const totalCompetitors = computed(() => currentData.value.length)
const activeNow = computed(() => Math.floor(currentData.value.length * 0.65))
const highestScore = computed(() => currentData.value.length > 0 ? currentData.value[0].score : 0)
</script>

<style scoped>
.text-gradient {
  background: linear-gradient(to right, #f97316, #8b5cf6, #06b6d4);
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
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(249, 115, 22, 0.3);
}

.podium-card {
  transition: all 0.2s ease;
}

.podium-card:hover {
  transform: translateY(-4px);
}
</style>
