<!-- CompactServersWidget.vue - Kompakt Sunucu Listesi -->
<template>
  <div class="compact-servers-widget card">
    <div class="widget-header">
      <h3 class="widget-title">
        <span class="title-icon">🎮</span>
        Canlı Sunucular
      </h3>
      <span v-if="!loading" class="server-count">{{ servers.length }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <n-skeleton v-for="i in 3" :key="i" height="50px" width="100%" />
    </div>

    <!-- Server List -->
    <div v-else-if="servers.length > 0" class="server-list">
      <div 
        v-for="server in servers" 
        :key="server.id"
        class="server-item"
        @click="connectServer(server)"
      >
        <div class="server-info">
          <div class="server-name">
            {{ server.name }}
          </div>
          <div class="server-map">
            <span class="map-icon">🗺️</span>
            {{ server.current_map }}
          </div>
        </div>

        <div class="server-stats">
          <div 
            class="player-count"
            :class="getOccupancyClass(server.current_players, server.max_players)"
          >
            <span class="count-current">{{ server.current_players }}</span>
            <span class="count-separator">/</span>
            <span class="count-max">{{ server.max_players }}</span>
          </div>
          <div class="occupancy-bar">
            <div 
              class="occupancy-fill"
              :class="getOccupancyClass(server.current_players, server.max_players)"
              :style="{ width: getOccupancyPercentage(server) + '%' }"
            ></div>
          </div>
        </div>

        <div class="server-status" :class="getOccupancyClass(server.current_players, server.max_players)">
          <span class="status-dot"></span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <span class="empty-icon">😴</span>
      <p class="empty-text">Şu anda aktif sunucu yok</p>
    </div>

    <!-- View All Link -->
    <div v-if="servers.length > 0" class="view-all">
      <n-button 
        text
        type="primary"
        size="small"
        @click="goToServers"
      >
        Tüm Sunucular →
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Props
const props = defineProps({
  servers: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Methods
const getOccupancyPercentage = (server) => {
  return Math.round((server.current_players / server.max_players) * 100)
}

const getOccupancyClass = (current, max) => {
  const percentage = (current / max) * 100
  
  if (percentage >= 90) return 'full'
  if (percentage >= 60) return 'high'
  if (percentage >= 30) return 'medium'
  return 'low'
}

const connectServer = (server) => {
  // Steam protokolü ile bağlan
  window.location.href = `steam://connect/${server.ip}:${server.port}`
}

const goToServers = () => {
  router.push('/servers')
}
</script>

<style scoped>
.compact-servers-widget {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.widget-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.title-icon {
  font-size: 1.3rem;
}

.server-count {
  background: rgba(249, 115, 22, 0.1);
  color: var(--primary);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

/* Server List */
.server-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.server-item {
  display: grid;
  grid-template-columns: 1fr auto 24px;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.server-item:hover {
  background: rgba(249, 115, 22, 0.1);
  transform: translateX(4px);
}

/* Server Info */
.server-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.server-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.server-map {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.map-icon {
  font-size: 0.85rem;
}

/* Server Stats */
.server-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.player-count {
  font-weight: 700;
  font-size: 0.95rem;
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.player-count.low {
  color: #ef4444;
}

.player-count.medium {
  color: #f59e0b;
}

.player-count.high {
  color: #22c55e;
}

.player-count.full {
  color: var(--neon-green);
}

.count-separator {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.count-max {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* Occupancy Bar */
.occupancy-bar {
  width: 60px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.occupancy-fill {
  height: 100%;
  transition: all 0.5s ease;
  border-radius: 2px;
}

.occupancy-fill.low {
  background: #ef4444;
}

.occupancy-fill.medium {
  background: #f59e0b;
}

.occupancy-fill.high {
  background: #22c55e;
}

.occupancy-fill.full {
  background: var(--neon-green);
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 8px rgba(57, 255, 20, 0.5);
  }
  50% {
    box-shadow: 0 0 16px rgba(57, 255, 20, 0.8);
  }
}

/* Server Status Dot */
.server-status {
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: status-pulse 2s infinite;
}

.server-status.low .status-dot {
  background: #ef4444;
  box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
}

.server-status.medium .status-dot {
  background: #f59e0b;
  box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
}

.server-status.high .status-dot {
  background: #22c55e;
  box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
}

.server-status.full .status-dot {
  background: var(--neon-green);
  box-shadow: 0 0 0 0 rgba(57, 255, 20, 0.7);
}

@keyframes status-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 currentColor;
  }
  50% {
    box-shadow: 0 0 0 6px transparent;
  }
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 30px 20px;
}

.empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 10px;
  opacity: 0.5;
}

.empty-text {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: 0;
}

/* View All */
.view-all {
  display: flex;
  justify-content: center;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .server-item {
    grid-template-columns: 1fr auto;
  }
  
  .server-status {
    display: none;
  }
}
</style>
