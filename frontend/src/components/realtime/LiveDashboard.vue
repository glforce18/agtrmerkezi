<template>
  <div class="live-dashboard">
    <div class="connection-indicator">
      <span :class="['status-dot', isConnected ? 'connected' : 'disconnected']"></span>
      <span class="status-text">
        {{ isConnected ? 'Canlı' : 'Bağlantı Yok' }}
      </span>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🖥️</div>
        <div class="stat-content">
          <h3>{{ dashboardStats.total_online }}</h3>
          <p>Aktif Sunucu</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <h3>{{ dashboardStats.total_players }}</h3>
          <p>Online Oyuncu</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <h3>{{ formatCurrency(dashboardStats.today_revenue) }}</h3>
          <p>Bugünkü Gelir</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-content">
          <h3>{{ dashboardStats.active_users }}</h3>
          <p>Aktif Kullanıcı</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useDashboardWS } from '@/composables/useWebSocket'
import { useRealtimeStore } from '@/stores/realtime'
import { formatCurrency } from '@/utils/formatters'

const realtimeStore = useRealtimeStore()
const { dashboardStats, isConnected } = useDashboardWS()

// Update store when stats change
onMounted(() => {
  realtimeStore.setConnectionStatus('dashboard', true)
})

onUnmounted(() => {
  realtimeStore.setConnectionStatus('dashboard', false)
})
</script>

<style scoped>
.live-dashboard {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}

.connection-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 1.5rem;
  font-size: 14px;
  color: var(--text-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.connected {
  background: #10b981;
}

.status-dot.disconnected {
  background: #ef4444;
  animation: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
}

.stat-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.stat-content p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}
</style>
