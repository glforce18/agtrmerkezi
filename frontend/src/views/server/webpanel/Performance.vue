<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Server Performance</h2>
          <p class="text-gray-400 text-sm mt-1">CPU, RAM, Network monitoring</p>
        </div>
        <div class="flex gap-3">
          <select
            v-model="timeRange"
            @change="fetchPerformanceData"
            class="px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white text-sm focus:border-blue-500 outline-none"
          >
            <option value="1">Last 1 Hour</option>
            <option value="6">Last 6 Hours</option>
            <option value="24">Last 24 Hours</option>
            <option value="168">Last 7 Days</option>
          </select>
          <button
            @click="fetchPerformanceData"
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

      <!-- Current Metrics Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-6 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
            CPU
          </div>
          <div class="text-2xl font-bold" :class="getCpuColor(currentMetrics.cpu_usage)">
            {{ currentMetrics.cpu_usage }}%
          </div>
        </div>

        <div class="bg-white/5 rounded-lg p-4">
          <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            RAM
          </div>
          <div class="text-2xl font-bold text-blue-400">
            {{ currentMetrics.memory_usage }} MB
          </div>
        </div>

        <div class="bg-white/5 rounded-lg p-4">
          <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
            Network In
          </div>
          <div class="text-2xl font-bold text-green-400">
            {{ currentMetrics.network_in }} Mbps
          </div>
        </div>

        <div class="bg-white/5 rounded-lg p-4">
          <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
            Network Out
          </div>
          <div class="text-2xl font-bold text-orange-400">
            {{ currentMetrics.network_out }} Mbps
          </div>
        </div>

        <div class="bg-white/5 rounded-lg p-4">
          <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            FPS
          </div>
          <div class="text-2xl font-bold text-purple-400">
            {{ currentMetrics.fps }}
          </div>
        </div>

        <div class="bg-white/5 rounded-lg p-4">
          <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Ping
          </div>
          <div class="text-2xl font-bold text-yellow-400">
            {{ currentMetrics.ping_avg }} ms
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Summary Stats -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4">Summary ({{ timeRange }}h)</h3>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">CPU Usage</span>
              <span class="text-white">Avg: {{ summary.cpu?.avg }}% | Max: {{ summary.cpu?.max }}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-gradient-to-r from-green-500 to-red-500 h-2 rounded-full" :style="{ width: summary.cpu?.max + '%' }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">Memory Usage</span>
              <span class="text-white">Avg: {{ summary.memory?.avg }} MB | Max: {{ summary.memory?.max }} MB</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-blue-500 h-2 rounded-full" :style="{ width: Math.min(100, (summary.memory?.max / 512) * 100) + '%' }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">Network (In)</span>
              <span class="text-white">Avg: {{ summary.network?.in_avg }} Mbps | Max: {{ summary.network?.in_max }} Mbps</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-green-500 h-2 rounded-full" :style="{ width: Math.min(100, (summary.network?.in_max / 100) * 100) + '%' }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">Network (Out)</span>
              <span class="text-white">Avg: {{ summary.network?.out_avg }} Mbps | Max: {{ summary.network?.out_max }} Mbps</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div class="bg-orange-500 h-2 rounded-full" :style="{ width: Math.min(100, (summary.network?.out_max / 100) * 100) + '%' }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">Players</span>
              <span class="text-white">Avg: {{ summary.players?.avg }} | Max: {{ summary.players?.max }}</span>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">Server Performance</span>
              <span class="text-white">FPS: {{ summary.performance?.fps_avg }} (min: {{ summary.performance?.fps_min }}) | Ping: {{ summary.performance?.ping_avg }} ms</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Current Info -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4">Current Status</h3>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span class="text-gray-400">Current Map</span>
            <span class="text-white font-mono">{{ currentMetrics.current_map }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span class="text-gray-400">Players Online</span>
            <span class="text-white font-bold">{{ currentMetrics.player_count }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span class="text-gray-400">Tick Rate</span>
            <span class="text-purple-400 font-mono">{{ currentMetrics.tick_rate }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span class="text-gray-400">Disk Usage</span>
            <span class="text-gray-300">{{ currentMetrics.disk_usage }} MB</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span class="text-gray-400">Last Update</span>
            <span class="text-gray-500 text-sm">{{ formatTime(currentMetrics.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-bold text-white mb-4">Performance History</h3>

      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="text-gray-400 mt-4">Loading performance data...</p>
      </div>

      <div v-else-if="history.length === 0" class="py-12 text-center text-gray-500">
        Henüz performans verisi yok. Sunucu çalıştığında otomatik olarak toplanacaktır.
      </div>

      <div v-else class="space-y-8">
        <!-- Simple Line Charts using CSS -->
        <div>
          <h4 class="text-white font-medium mb-3">CPU Usage (%)</h4>
          <div class="h-48 bg-gray-900/50 rounded-lg p-4 overflow-x-auto">
            <div class="flex items-end justify-between h-full gap-1" style="min-width: 100%;">
              <div
                v-for="(point, idx) in history.slice(-50)"
                :key="idx"
                class="flex-1 bg-gradient-to-t from-red-500/70 to-yellow-500/70 rounded-t transition-all hover:opacity-80"
                :style="{ height: (point.cpu_usage || 0) + '%', minHeight: '2px' }"
                :title="`CPU: ${point.cpu_usage}%`"
              ></div>
            </div>
          </div>
        </div>

        <div>
          <h4 class="text-white font-medium mb-3">Memory Usage (MB)</h4>
          <div class="h-48 bg-gray-900/50 rounded-lg p-4 overflow-x-auto">
            <div class="flex items-end justify-between h-full gap-1" style="min-width: 100%;">
              <div
                v-for="(point, idx) in history.slice(-50)"
                :key="idx"
                class="flex-1 bg-gradient-to-t from-blue-500/70 to-cyan-500/70 rounded-t transition-all hover:opacity-80"
                :style="{ height: Math.min(100, (point.memory_usage / 512) * 100) + '%', minHeight: '2px' }"
                :title="`RAM: ${point.memory_usage} MB`"
              ></div>
            </div>
          </div>
        </div>

        <div>
          <h4 class="text-white font-medium mb-3">Network Traffic (Mbps)</h4>
          <div class="h-48 bg-gray-900/50 rounded-lg p-4 overflow-x-auto">
            <div class="flex items-end justify-between h-full gap-1" style="min-width: 100%;">
              <div
                v-for="(point, idx) in history.slice(-50)"
                :key="idx"
                class="flex-1 flex flex-col justify-end gap-0.5"
              >
                <div
                  class="bg-orange-500/70 rounded-t transition-all hover:opacity-80"
                  :style="{ height: Math.min(100, (point.network_out / 10) * 100) + '%', minHeight: '1px' }"
                  :title="`Out: ${point.network_out} Mbps`"
                ></div>
                <div
                  class="bg-green-500/70 rounded-t transition-all hover:opacity-80"
                  :style="{ height: Math.min(100, (point.network_in / 10) * 100) + '%', minHeight: '1px' }"
                  :title="`In: ${point.network_in} Mbps`"
                ></div>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-center gap-6 mt-2">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-green-500 rounded"></div>
              <span class="text-gray-400 text-sm">Incoming</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-orange-500 rounded"></div>
              <span class="text-gray-400 text-sm">Outgoing</span>
            </div>
          </div>
        </div>

        <div>
          <h4 class="text-white font-medium mb-3">Server FPS</h4>
          <div class="h-48 bg-gray-900/50 rounded-lg p-4 overflow-x-auto">
            <div class="flex items-end justify-between h-full gap-1" style="min-width: 100%;">
              <div
                v-for="(point, idx) in history.slice(-50)"
                :key="idx"
                class="flex-1 bg-gradient-to-t from-purple-500/70 to-pink-500/70 rounded-t transition-all hover:opacity-80"
                :style="{ height: Math.min(100, (point.fps / 1000) * 100) + '%', minHeight: '2px' }"
                :title="`FPS: ${point.fps}`"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)
const timeRange = ref(24)
const refreshInterval = ref(null)

// Performance state
const currentMetrics = ref({
  timestamp: new Date().toISOString(),
  cpu_usage: 0,
  memory_usage: 0,
  network_in: 0,
  network_out: 0,
  disk_usage: 0,
  player_count: 0,
  tick_rate: 0,
  fps: 0,
  ping_avg: 0,
  ping_max: 0,
  current_map: 'N/A'
})

const summary = ref({
  cpu: { avg: 0, max: 0 },
  memory: { avg: 0, max: 0 },
  network: { in_avg: 0, in_max: 0, out_avg: 0, out_max: 0 },
  players: { avg: 0, max: 0 },
  performance: { fps_avg: 0, fps_min: 0, ping_avg: 0, ping_max: 0 }
})

const history = ref([])

const getCpuColor = (usage) => {
  if (usage >= 80) return 'text-red-400'
  if (usage >= 60) return 'text-orange-400'
  if (usage >= 40) return 'text-yellow-400'
  return 'text-green-400'
}

const fetchCurrentMetrics = async () => {
  try {
    const response = await api.getCurrentPerformance(serverId.value)
    if (response.success) {
      currentMetrics.value = response.data || {}
    }
  } catch (error) {
    console.error('Failed to fetch current metrics:', error)
  }
}

const fetchPerformanceHistory = async () => {
  try {
    const response = await api.getPerformanceHistory(serverId.value, {
      hours: timeRange.value,
      interval: timeRange.value > 24 ? 60 : 5
    })
    if (response.success) {
      history.value = response.data?.history || []
    }
  } catch (error) {
    console.error('Failed to fetch history:', error)
  }
}

const fetchPerformanceSummary = async () => {
  try {
    const response = await api.getPerformanceSummary(serverId.value, timeRange.value)
    if (response.success) {
      summary.value = response.data || {}
    }
  } catch (error) {
    console.error('Failed to fetch summary:', error)
  }
}

const fetchPerformanceData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchCurrentMetrics(),
      fetchPerformanceHistory(),
      fetchPerformanceSummary()
    ])
  } catch (error) {
    toast.show('Performans verileri yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(async () => {
  await fetchPerformanceData()

  // Auto-refresh every 30 seconds
  refreshInterval.value = setInterval(async () => {
    await fetchCurrentMetrics()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
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
