<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Player Statistics</h2>
          <p class="text-gray-400 text-sm mt-1">Leaderboard, oyuncu istatistikleri ve performans</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="refreshStats"
            :disabled="loading"
            class="btn-secondary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Yenile
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-4 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Oyuncu</div>
          <div class="text-2xl font-bold text-white mt-1">{{ totalPlayers }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Aktif Oyuncu (7d)</div>
          <div class="text-2xl font-bold text-green-400 mt-1">{{ activePlayers }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Maç</div>
          <div class="text-2xl font-bold text-blue-400 mt-1">{{ totalMatches }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Ortalama K/D</div>
          <div class="text-2xl font-bold text-orange-400 mt-1">{{ averageKD }}</div>
        </div>
      </div>
    </div>

    <!-- Top Players -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Top ELO -->
      <div class="glass-card p-4">
        <h3 class="text-lg font-bold text-white mb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          Top ELO
        </h3>
        <div class="space-y-2">
          <div v-for="(player, idx) in topPlayers.top_elo" :key="player.steam_id" class="flex items-center gap-2 p-2 bg-white/5 rounded">
            <span class="text-gray-400 font-mono text-sm">#{idx + 1}</span>
            <div class="flex-1 min-w-0">
              <div class="text-white text-sm truncate">{{ player.player_name }}</div>
              <div class="text-gray-500 text-xs">ELO: {{ player.elo_rating }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top K/D -->
      <div class="glass-card p-4">
        <h3 class="text-lg font-bold text-white mb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Top K/D
        </h3>
        <div class="space-y-2">
          <div v-for="(player, idx) in topPlayers.top_kd" :key="player.steam_id" class="flex items-center gap-2 p-2 bg-white/5 rounded">
            <span class="text-gray-400 font-mono text-sm">#{idx + 1}</span>
            <div class="flex-1 min-w-0">
              <div class="text-white text-sm truncate">{{ player.player_name }}</div>
              <div class="text-gray-500 text-xs">K/D: {{ player.kd_ratio }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Kills -->
      <div class="glass-card p-4">
        <h3 class="text-lg font-bold text-white mb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
          </svg>
          Top Kills
        </h3>
        <div class="space-y-2">
          <div v-for="(player, idx) in topPlayers.top_kills" :key="player.steam_id" class="flex items-center gap-2 p-2 bg-white/5 rounded">
            <span class="text-gray-400 font-mono text-sm">#{idx + 1}</span>
            <div class="flex-1 min-w-0">
              <div class="text-white text-sm truncate">{{ player.player_name }}</div>
              <div class="text-gray-500 text-xs">Kills: {{ player.total_kills }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Headshots -->
      <div class="glass-card p-4">
        <h3 class="text-lg font-bold text-white mb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          Top Headshots
        </h3>
        <div class="space-y-2">
          <div v-for="(player, idx) in topPlayers.top_headshots" :key="player.steam_id" class="flex items-center gap-2 p-2 bg-white/5 rounded">
            <span class="text-gray-400 font-mono text-sm">#{idx + 1}</span>
            <div class="flex-1 min-w-0">
              <div class="text-white text-sm truncate">{{ player.player_name }}</div>
              <div class="text-gray-500 text-xs">HS: {{ player.headshot_percentage }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Leaderboard -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-white">Leaderboard</h3>
        <div class="flex gap-2">
          <select
            v-model="sortBy"
            @change="fetchLeaderboard"
            class="px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
          >
            <option value="elo_rating">ELO Rating</option>
            <option value="total_kills">Total Kills</option>
            <option value="total_score">Total Score</option>
            <option value="kd_ratio">K/D Ratio</option>
          </select>
          <input
            v-model.number="minPlaytime"
            @change="fetchLeaderboard"
            type="number"
            min="0"
            step="3600"
            placeholder="Min playtime (sec)"
            class="px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none w-40"
          />
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-white/10">
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Rank</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Player</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">ELO</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">K/D</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Kills</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Deaths</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">HS%</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Win Rate</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Playtime</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Last Seen</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="player in leaderboard"
              :key="player.steam_id"
              class="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              <td class="py-3 px-4">
                <span
                  class="inline-flex items-center justify-center w-8 h-8 rounded-full font-bold"
                  :class="{
                    'bg-yellow-500/20 text-yellow-400': player.rank === 1,
                    'bg-gray-400/20 text-gray-300': player.rank === 2,
                    'bg-orange-500/20 text-orange-400': player.rank === 3,
                    'text-gray-400': player.rank > 3
                  }"
                >
                  #{{ player.rank }}
                </span>
              </td>
              <td class="py-3 px-4">
                <div class="text-white font-medium">{{ player.player_name }}</div>
                <div class="text-gray-500 text-xs font-mono">{{ player.steam_id }}</div>
              </td>
              <td class="py-3 px-4">
                <span class="text-yellow-400 font-bold">{{ player.elo_rating }}</span>
              </td>
              <td class="py-3 px-4">
                <span
                  :class="{
                    'text-green-400': player.kd_ratio >= 2,
                    'text-blue-400': player.kd_ratio >= 1 && player.kd_ratio < 2,
                    'text-gray-400': player.kd_ratio < 1
                  }"
                >
                  {{ player.kd_ratio }}
                </span>
              </td>
              <td class="py-3 px-4 text-green-400">{{ player.total_kills }}</td>
              <td class="py-3 px-4 text-red-400">{{ player.total_deaths }}</td>
              <td class="py-3 px-4 text-purple-400">{{ player.headshot_percentage }}%</td>
              <td class="py-3 px-4">
                <span :class="player.win_rate >= 50 ? 'text-green-400' : 'text-gray-400'">
                  {{ player.win_rate }}%
                </span>
              </td>
              <td class="py-3 px-4 text-gray-300">{{ player.playtime_hours }}h</td>
              <td class="py-3 px-4 text-gray-500 text-sm">{{ formatDate(player.last_seen) }}</td>
            </tr>
            <tr v-if="leaderboard.length === 0 && !loading">
              <td colspan="10" class="py-8 text-center text-gray-500">
                Henüz oyuncu istatistiği yok
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="loading" class="py-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    </div>

    <!-- Recent Matches -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-bold text-white mb-4">Recent Matches</h3>
      <div class="space-y-3">
        <div
          v-for="match in recentMatches"
          :key="match.id"
          class="bg-white/5 rounded-lg p-4 flex items-center justify-between"
        >
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-gray-900 rounded-lg flex items-center justify-center">
              <svg class="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <div>
              <div class="text-white font-bold">{{ match.map_name }}</div>
              <div class="text-gray-400 text-sm">{{ match.match_type || 'Deathmatch' }}</div>
              <div class="text-gray-500 text-xs">{{ formatDate(match.match_date) }}</div>
            </div>
          </div>
          <div class="flex items-center gap-6">
            <div v-if="match.team1_score !== null" class="text-center">
              <div class="text-2xl font-bold text-blue-400">{{ match.team1_score }}</div>
              <div class="text-gray-500 text-xs">Team 1</div>
            </div>
            <div v-if="match.team1_score !== null" class="text-gray-600 text-2xl">:</div>
            <div v-if="match.team2_score !== null" class="text-center">
              <div class="text-2xl font-bold text-orange-400">{{ match.team2_score }}</div>
              <div class="text-gray-500 text-xs">Team 2</div>
            </div>
            <div class="text-center ml-4">
              <div class="text-white font-mono">{{ formatDuration(match.duration_seconds) }}</div>
              <div class="text-gray-500 text-xs">Duration</div>
            </div>
          </div>
        </div>
        <div v-if="recentMatches.length === 0 && !loading" class="py-8 text-center text-gray-500">
          Henüz maç verisi yok
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)

// Stats state
const topPlayers = ref({
  top_elo: [],
  top_kd: [],
  top_kills: [],
  top_headshots: []
})
const leaderboard = ref([])
const recentMatches = ref([])
const sortBy = ref('elo_rating')
const minPlaytime = ref(3600)

// Computed stats
const totalPlayers = computed(() => leaderboard.value.length)
const activePlayers = computed(() => {
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  return leaderboard.value.filter(p => new Date(p.last_seen) >= sevenDaysAgo).length
})
const totalMatches = computed(() => recentMatches.value.length)
const averageKD = computed(() => {
  if (leaderboard.value.length === 0) return '0.00'
  const avg = leaderboard.value.reduce((sum, p) => sum + p.kd_ratio, 0) / leaderboard.value.length
  return avg.toFixed(2)
})

const fetchTopPlayers = async () => {
  try {
    const response = await api.getTopPlayers(serverId.value, 5)
    if (response.success) {
      topPlayers.value = response.data || {}
    }
  } catch (error) {
    console.error('Failed to fetch top players:', error)
  }
}

const fetchLeaderboard = async () => {
  loading.value = true
  try {
    const response = await api.getPlayerLeaderboard(serverId.value, {
      sort_by: sortBy.value,
      limit: 100,
      min_playtime: minPlaytime.value
    })
    if (response.success) {
      leaderboard.value = response.data?.leaderboard || []
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Leaderboard yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const fetchRecentMatches = async () => {
  try {
    const response = await api.getRecentMatches(serverId.value, 10)
    if (response.success) {
      recentMatches.value = response.data?.matches || []
    }
  } catch (error) {
    console.error('Failed to fetch matches:', error)
  }
}

const refreshStats = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchTopPlayers(),
      fetchLeaderboard(),
      fetchRecentMatches()
    ])
    toast.show('İstatistikler güncellendi', 'success')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

const formatDuration = (seconds) => {
  if (!seconds) return 'N/A'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onMounted(async () => {
  await refreshStats()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-secondary {
  @apply px-3 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-all flex items-center gap-2;
}
</style>
