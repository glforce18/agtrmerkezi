<template>
  <div class="live-server-stats">
    <div class="header">
      <h3>Canlı Sunucu İstatistikleri</h3>
      <span :class="['status-badge', stats?.status]">
        {{ stats?.status || 'offline' }}
      </span>
    </div>

    <div v-if="loading" class="loading">Yükleniyor...</div>

    <div v-else-if="stats" class="stats-content">
      <div class="stat-row">
        <span class="label">Oyuncular:</span>
        <span class="value">{{ stats.players }}/{{ stats.max_players }}</span>
      </div>

      <div class="stat-row">
        <span class="label">Harita:</span>
        <span class="value">{{ stats.map }}</span>
      </div>

      <div class="stat-row">
        <span class="label">CPU:</span>
        <span class="value">{{ stats.cpu }}%</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${stats.cpu}%` }"></div>
        </div>
      </div>

      <div class="stat-row">
        <span class="label">RAM:</span>
        <span class="value">{{ stats.ram }}%</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${stats.ram}%` }"></div>
        </div>
      </div>

      <div class="stat-row">
        <span class="label">Uptime:</span>
        <span class="value">{{ formatUptime(stats.uptime) }}</span>
      </div>
    </div>

    <div v-else class="no-data">
      Sunucu verisi alınamadı
    </div>
  </div>
</template>

<script setup>
import { useServerStatsWS } from '@/composables/useWebSocket'

const props = defineProps({
  serverId: {
    type: Number,
    required: true
  }
})

const { stats, loading, isConnected, requestStats } = useServerStatsWS(props.serverId)

function formatUptime(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}s ${minutes}d`
}
</script>

<style scoped>
.live-server-stats {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header h3 {
  margin: 0;
  font-size: 18px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.running {
  background: rgba(16, 185, 129, 0.25);
  color: var(--success-color, #10b981);
}

.status-badge.offline {
  background: rgba(239, 68, 68, 0.25);
  color: var(--error-color, #ef4444);
}

.loading, .no-data {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.stat-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-row .label {
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-row .value {
  font-weight: 600;
  color: var(--text-primary);
}

.progress-bar {
  grid-column: 2;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}
</style>
