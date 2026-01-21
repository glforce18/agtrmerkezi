<template>
  <div class="monitoring-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h2 class="dashboard-title">Sunucu Monitörü</h2>
        <span class="live-indicator" :class="{ active: isConnected }">
          <span class="pulse"></span>
          {{ isConnected ? 'Canlı' : 'Bağlantı Kesik' }}
        </span>
      </div>
      <div class="header-right">
        <select v-model="timeRange" class="time-select">
          <option value="1h">Son 1 Saat</option>
          <option value="6h">Son 6 Saat</option>
          <option value="24h">Son 24 Saat</option>
          <option value="7d">Son 7 Gün</option>
        </select>
        <button class="refresh-btn" @click="refreshData" :disabled="isLoading">
          <svg :class="{ spinning: isLoading }" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Overview Cards -->
    <div class="overview-grid">
      <div class="overview-card cpu">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="4" y="4" width="16" height="16" rx="2"/>
            <rect x="9" y="9" width="6" height="6"/>
            <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 15h3M1 9h3M1 15h3"/>
          </svg>
        </div>
        <div class="card-content">
          <span class="card-label">CPU Kullanımı</span>
          <span class="card-value">{{ currentStats.cpu }}%</span>
          <div class="mini-bar">
            <div class="mini-bar-fill" :style="{ width: `${currentStats.cpu}%` }" :class="getUsageClass(currentStats.cpu)"></div>
          </div>
        </div>
      </div>

      <div class="overview-card ram">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 19v-8a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8"/>
            <path d="M6 19h12"/>
            <path d="M3 19h18"/>
            <path d="M9 9V6a3 3 0 0 1 6 0v3"/>
          </svg>
        </div>
        <div class="card-content">
          <span class="card-label">RAM Kullanımı</span>
          <span class="card-value">{{ currentStats.ram }}%</span>
          <div class="mini-bar">
            <div class="mini-bar-fill" :style="{ width: `${currentStats.ram}%` }" :class="getUsageClass(currentStats.ram)"></div>
          </div>
        </div>
      </div>

      <div class="overview-card network">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12.55a11 11 0 0 1 14.08 0M1.42 9a16 16 0 0 1 21.16 0M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/>
          </svg>
        </div>
        <div class="card-content">
          <span class="card-label">Ağ Trafiği</span>
          <span class="card-value">{{ formatBytes(currentStats.networkIn) }}/s</span>
          <span class="card-sub">↑ {{ formatBytes(currentStats.networkOut) }}/s</span>
        </div>
      </div>

      <div class="overview-card players">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="card-content">
          <span class="card-label">Toplam Oyuncu</span>
          <span class="card-value">{{ currentStats.players }}</span>
          <span class="card-sub">{{ currentStats.maxPlayers }} kapasite</span>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-grid">
      <!-- CPU & RAM Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>CPU & RAM Kullanımı</h3>
          <div class="chart-legend">
            <span class="legend-item cpu"><span class="dot"></span> CPU</span>
            <span class="legend-item ram"><span class="dot"></span> RAM</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="cpuRamChart"></canvas>
        </div>
      </div>

      <!-- Network Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>Ağ Trafiği</h3>
          <div class="chart-legend">
            <span class="legend-item network-in"><span class="dot"></span> Gelen</span>
            <span class="legend-item network-out"><span class="dot"></span> Giden</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="networkChart"></canvas>
        </div>
      </div>

      <!-- Players Chart -->
      <div class="chart-card full-width">
        <div class="chart-header">
          <h3>Oyuncu Sayısı</h3>
          <div class="chart-stats">
            <span>Ortalama: {{ avgPlayers }}</span>
            <span>Maksimum: {{ maxPlayers }}</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="playersChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Server Status Table -->
    <div class="status-section">
      <div class="section-header">
        <h3>Sunucu Durumları</h3>
        <div class="status-filters">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            class="filter-btn"
            :class="{ active: activeFilter === filter.value }"
            @click="activeFilter = filter.value"
          >
            {{ filter.label }}
            <span class="count">{{ getFilterCount(filter.value) }}</span>
          </button>
        </div>
      </div>

      <div class="status-table">
        <div class="table-header">
          <span class="col-status">Durum</span>
          <span class="col-name">Sunucu</span>
          <span class="col-players">Oyuncu</span>
          <span class="col-cpu">CPU</span>
          <span class="col-ram">RAM</span>
          <span class="col-uptime">Uptime</span>
        </div>
        <TransitionGroup name="list" tag="div" class="table-body">
          <div
            v-for="server in filteredServers"
            :key="server.id"
            class="table-row"
            :class="{ warning: server.cpu > 80 || server.ram > 80 }"
          >
            <span class="col-status">
              <span class="status-dot" :class="server.status"></span>
            </span>
            <span class="col-name">
              <strong>{{ server.name }}</strong>
              <small>{{ server.ip }}:{{ server.port }}</small>
            </span>
            <span class="col-players">
              <span class="player-count">{{ server.players }}/{{ server.maxPlayers }}</span>
              <div class="player-bar">
                <div class="player-bar-fill" :style="{ width: `${(server.players / server.maxPlayers) * 100}%` }"></div>
              </div>
            </span>
            <span class="col-cpu" :class="getUsageClass(server.cpu)">{{ server.cpu }}%</span>
            <span class="col-ram" :class="getUsageClass(server.ram)">{{ server.ram }}%</span>
            <span class="col-uptime">{{ formatUptime(server.uptime) }}</span>
          </div>
        </TransitionGroup>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { wsManager } from '@/services/WebSocketManager'

const props = defineProps({
  serverId: {
    type: [String, Number],
    default: null
  }
})

// State
const timeRange = ref('1h')
const isConnected = ref(false)
const isLoading = ref(false)
const activeFilter = ref('all')

// Chart refs
const cpuRamChart = ref(null)
const networkChart = ref(null)
const playersChart = ref(null)

// Chart instances
let cpuRamChartInstance = null
let networkChartInstance = null
let playersChartInstance = null

// Current stats
const currentStats = ref({
  cpu: 0,
  ram: 0,
  networkIn: 0,
  networkOut: 0,
  players: 0,
  maxPlayers: 0
})

// Historical data
const historyData = ref({
  timestamps: [],
  cpu: [],
  ram: [],
  networkIn: [],
  networkOut: [],
  players: []
})

// Servers data
const servers = ref([])

// Status filters
const statusFilters = [
  { label: 'Tümü', value: 'all' },
  { label: 'Çevrimiçi', value: 'online' },
  { label: 'Çevrimdışı', value: 'offline' },
  { label: 'Uyarı', value: 'warning' }
]

// Computed
const filteredServers = computed(() => {
  if (activeFilter.value === 'all') return servers.value
  if (activeFilter.value === 'warning') {
    return servers.value.filter(s => s.cpu > 80 || s.ram > 80)
  }
  return servers.value.filter(s => s.status === activeFilter.value)
})

const avgPlayers = computed(() => {
  if (historyData.value.players.length === 0) return 0
  const sum = historyData.value.players.reduce((a, b) => a + b, 0)
  return Math.round(sum / historyData.value.players.length)
})

const maxPlayers = computed(() => {
  if (historyData.value.players.length === 0) return 0
  return Math.max(...historyData.value.players)
})

// Methods
function getUsageClass(value) {
  if (value >= 90) return 'critical'
  if (value >= 70) return 'warning'
  return 'normal'
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatUptime(seconds) {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const mins = Math.floor((seconds % 3600) / 60)

  if (days > 0) return `${days}g ${hours}s`
  if (hours > 0) return `${hours}s ${mins}d`
  return `${mins}d`
}

function getFilterCount(filter) {
  if (filter === 'all') return servers.value.length
  if (filter === 'warning') {
    return servers.value.filter(s => s.cpu > 80 || s.ram > 80).length
  }
  return servers.value.filter(s => s.status === filter).length
}

async function refreshData() {
  isLoading.value = true
  try {
    // Fetch historical data based on time range
    const response = await fetch(`/api/monitoring/stats?range=${timeRange.value}`)
    if (response.ok) {
      const data = await response.json()
      historyData.value = data.history
      servers.value = data.servers
      updateCharts()
    }
  } catch (error) {
    console.error('Failed to fetch monitoring data:', error)
  } finally {
    isLoading.value = false
  }
}

function updateCharts() {
  // Update CPU & RAM chart
  if (cpuRamChartInstance) {
    cpuRamChartInstance.data.labels = historyData.value.timestamps
    cpuRamChartInstance.data.datasets[0].data = historyData.value.cpu
    cpuRamChartInstance.data.datasets[1].data = historyData.value.ram
    cpuRamChartInstance.update('none')
  }

  // Update Network chart
  if (networkChartInstance) {
    networkChartInstance.data.labels = historyData.value.timestamps
    networkChartInstance.data.datasets[0].data = historyData.value.networkIn
    networkChartInstance.data.datasets[1].data = historyData.value.networkOut
    networkChartInstance.update('none')
  }

  // Update Players chart
  if (playersChartInstance) {
    playersChartInstance.data.labels = historyData.value.timestamps
    playersChartInstance.data.datasets[0].data = historyData.value.players
    playersChartInstance.update('none')
  }
}

function initCharts() {
  // Check if Chart.js is available
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js not loaded')
    return
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index'
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(15, 15, 26, 0.9)',
        borderColor: 'rgba(249, 115, 22, 0.3)',
        borderWidth: 1,
        titleColor: '#fff',
        bodyColor: '#a0a0b0',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)'
        },
        ticks: {
          color: '#6b7280'
        }
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)'
        },
        ticks: {
          color: '#6b7280'
        }
      }
    }
  }

  // CPU & RAM Chart
  if (cpuRamChart.value) {
    cpuRamChartInstance = new Chart(cpuRamChart.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'CPU',
            data: [],
            borderColor: '#f97316',
            backgroundColor: 'rgba(249, 115, 22, 0.1)',
            fill: true,
            tension: 0.4
          },
          {
            label: 'RAM',
            data: [],
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        ...chartOptions,
        scales: {
          ...chartOptions.scales,
          y: {
            ...chartOptions.scales.y,
            min: 0,
            max: 100
          }
        }
      }
    })
  }

  // Network Chart
  if (networkChart.value) {
    networkChartInstance = new Chart(networkChart.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Gelen',
            data: [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true,
            tension: 0.4
          },
          {
            label: 'Giden',
            data: [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: chartOptions
    })
  }

  // Players Chart
  if (playersChart.value) {
    playersChartInstance = new Chart(playersChart.value, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Oyuncu',
            data: [],
            backgroundColor: 'rgba(249, 115, 22, 0.6)',
            borderColor: '#f97316',
            borderWidth: 1,
            borderRadius: 4
          }
        ]
      },
      options: {
        ...chartOptions,
        scales: {
          ...chartOptions.scales,
          y: {
            ...chartOptions.scales.y,
            min: 0
          }
        }
      }
    })
  }
}

function handleRealtimeUpdate(data) {
  // Update current stats
  currentStats.value = {
    cpu: data.cpu,
    ram: data.ram,
    networkIn: data.networkIn,
    networkOut: data.networkOut,
    players: data.players,
    maxPlayers: data.maxPlayers
  }

  // Add to history (keep last 60 data points)
  const now = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })

  historyData.value.timestamps.push(now)
  historyData.value.cpu.push(data.cpu)
  historyData.value.ram.push(data.ram)
  historyData.value.networkIn.push(data.networkIn)
  historyData.value.networkOut.push(data.networkOut)
  historyData.value.players.push(data.players)

  // Keep only last 60 points
  const maxPoints = 60
  if (historyData.value.timestamps.length > maxPoints) {
    historyData.value.timestamps.shift()
    historyData.value.cpu.shift()
    historyData.value.ram.shift()
    historyData.value.networkIn.shift()
    historyData.value.networkOut.shift()
    historyData.value.players.shift()
  }

  updateCharts()

  // Update servers list
  if (data.servers) {
    servers.value = data.servers
  }
}

// WebSocket connection
let unsubscribe = null

onMounted(() => {
  // Initialize charts
  initCharts()

  // Load initial data
  refreshData()

  // Subscribe to real-time updates
  unsubscribe = wsManager.subscribe('monitoring', (data) => {
    isConnected.value = true
    handleRealtimeUpdate(data)
  })

  // Connect to monitoring channel
  wsManager.connect('monitoring', '/ws/monitoring')
})

onUnmounted(() => {
  // Cleanup
  if (unsubscribe) unsubscribe()
  if (cpuRamChartInstance) cpuRamChartInstance.destroy()
  if (networkChartInstance) networkChartInstance.destroy()
  if (playersChartInstance) playersChartInstance.destroy()
})

watch(timeRange, () => {
  refreshData()
})

// Generate demo data for development
function generateDemoData() {
  const now = new Date()
  const timestamps = []
  const cpu = []
  const ram = []
  const networkIn = []
  const networkOut = []
  const players = []

  for (let i = 59; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60000)
    timestamps.push(time.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }))
    cpu.push(Math.floor(Math.random() * 40) + 30)
    ram.push(Math.floor(Math.random() * 30) + 40)
    networkIn.push(Math.floor(Math.random() * 1024 * 1024) + 512 * 1024)
    networkOut.push(Math.floor(Math.random() * 512 * 1024) + 256 * 1024)
    players.push(Math.floor(Math.random() * 50) + 10)
  }

  historyData.value = { timestamps, cpu, ram, networkIn, networkOut, players }

  currentStats.value = {
    cpu: cpu[cpu.length - 1],
    ram: ram[ram.length - 1],
    networkIn: networkIn[networkIn.length - 1],
    networkOut: networkOut[networkOut.length - 1],
    players: players[players.length - 1],
    maxPlayers: 128
  }

  servers.value = [
    { id: 1, name: 'CS 1.6 Public #1', ip: '185.193.xx.xx', port: 27015, status: 'online', players: 24, maxPlayers: 32, cpu: 45, ram: 52, uptime: 259200 },
    { id: 2, name: 'CS 1.6 Public #2', ip: '185.193.xx.xx', port: 27016, status: 'online', players: 18, maxPlayers: 32, cpu: 38, ram: 48, uptime: 172800 },
    { id: 3, name: 'Half-Life DM', ip: '185.193.xx.xx', port: 27017, status: 'online', players: 8, maxPlayers: 16, cpu: 82, ram: 65, uptime: 86400 },
    { id: 4, name: 'CS 1.6 Zombie', ip: '185.193.xx.xx', port: 27018, status: 'offline', players: 0, maxPlayers: 32, cpu: 0, ram: 0, uptime: 0 },
  ]

  updateCharts()
}

// For development, generate demo data
if (import.meta.env.DEV) {
  setTimeout(generateDemoData, 500)
}
</script>

<style scoped>
.monitoring-dashboard {
  padding: 24px;
  background: var(--bg-secondary, #12121f);
  min-height: 100vh;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dashboard-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #ef4444;
}

.live-indicator.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.live-indicator .pulse {
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-select {
  padding: 8px 12px;
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  border-color: var(--primary, #f97316);
  color: var(--primary, #f97316);
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Overview Grid */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}

.overview-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  transition: all 0.2s;
}

.overview-card:hover {
  border-color: var(--primary, #f97316);
  transform: translateY(-2px);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 12px;
  color: var(--primary, #f97316);
}

.overview-card.ram .card-icon {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.overview-card.network .card-icon {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.overview-card.players .card-icon {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.card-content {
  flex: 1;
}

.card-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.card-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.card-sub {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.mini-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
  background: var(--primary, #f97316);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.mini-bar-fill.warning {
  background: #f59e0b;
}

.mini-bar-fill.critical {
  background: #ef4444;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  padding: 20px;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.legend-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-item.cpu .dot { background: #f97316; }
.legend-item.ram .dot { background: #8b5cf6; }
.legend-item.network-in .dot { background: #10b981; }
.legend-item.network-out .dot { background: #3b82f6; }

.chart-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

.chart-container {
  height: 200px;
}

/* Status Section */
.status-section {
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 12px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.status-filters {
  display: flex;
  gap: 8px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-color, #2a2a4a);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: var(--primary, #f97316);
  color: var(--text-primary);
}

.filter-btn.active {
  background: var(--primary, #f97316);
  border-color: var(--primary, #f97316);
  color: white;
}

.filter-btn .count {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 11px;
}

.filter-btn.active .count {
  background: rgba(255, 255, 255, 0.2);
}

/* Status Table */
.status-table {
  width: 100%;
}

.table-header {
  display: grid;
  grid-template-columns: 60px 2fr 1fr 80px 80px 100px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border-color, #2a2a4a);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row {
  display: grid;
  grid-template-columns: 60px 2fr 1fr 80px 80px 100px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #2a2a4a);
  align-items: center;
  transition: background 0.2s;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.table-row.warning {
  background: rgba(245, 158, 11, 0.05);
}

.table-row:last-child {
  border-bottom: none;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #6b7280;
}

.status-dot.online {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-dot.offline {
  background: #ef4444;
}

.col-name strong {
  display: block;
  color: var(--text-primary);
  font-weight: 600;
}

.col-name small {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 2px;
}

.col-players {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.player-count {
  font-size: 14px;
  color: var(--text-primary);
}

.player-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.player-bar-fill {
  height: 100%;
  background: var(--primary, #f97316);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.col-cpu, .col-ram {
  font-weight: 600;
  color: var(--text-primary);
}

.col-cpu.warning, .col-ram.warning {
  color: #f59e0b;
}

.col-cpu.critical, .col-ram.critical {
  color: #ef4444;
}

.col-uptime {
  color: var(--text-secondary);
  font-size: 13px;
}

/* List transitions */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Mobile */
@media (max-width: 768px) {
  .monitoring-dashboard {
    padding: 16px;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .table-header {
    display: none;
  }

  .table-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 16px;
  }

  .col-status {
    order: 1;
  }

  .col-name {
    order: 2;
    flex: 1;
  }

  .col-players {
    order: 3;
    width: 100%;
  }

  .col-cpu, .col-ram, .col-uptime {
    font-size: 12px;
  }
}
</style>
