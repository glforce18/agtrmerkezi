<template>
  <div class="installation-monitor">
    <div class="monitor-header">
      <h1>Server Installation Monitor</h1>
      <p class="subtitle">Real-time installation progress and logs</p>
    </div>

    <!-- No Installing Servers -->
    <div v-if="!loading && installingServers.length === 0" class="empty-state">
      <div class="empty-icon">✅</div>
      <h3>No Active Installations</h3>
      <p>All servers are installed successfully or not in installing state.</p>
      <button @click="loadInstallingServers" class="btn btn-secondary">
        🔄 Refresh
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading installation status...</p>
    </div>

    <!-- Installing Servers List -->
    <div v-if="!loading && installingServers.length > 0" class="servers-list">
      <div class="refresh-info">
        <span>Auto-refreshing every 2 seconds</span>
        <button @click="loadInstallingServers" class="btn btn-sm btn-secondary">
          🔄 Refresh Now
        </button>
      </div>

      <div
        v-for="server in installingServers"
        :key="server.server_id"
        class="install-card"
      >
        <!-- Server Header -->
        <div class="card-header">
          <div class="server-info">
            <h3>Server #{{ server.server_id }}</h3>
            <span class="server-name">{{ server.server_name }}</span>
          </div>
          <div class="status-badge" :class="server.status">
            {{ server.status.toUpperCase() }}
          </div>
        </div>

        <!-- Installation Logs -->
        <div class="log-viewer">
          <div class="log-header">
            <h4>📋 Installation Log</h4>
            <span class="log-count">{{ server.log_entries.length }} entries</span>
          </div>

          <div class="log-entries" ref="logContainer">
            <div
              v-for="(entry, idx) in server.log_entries"
              :key="idx"
              :class="['log-entry', entry.level.toLowerCase()]"
            >
              <span class="timestamp">{{ formatTime(entry.timestamp) }}</span>
              <span class="level">{{ entry.level }}</span>
              <span class="message">{{ entry.message }}</span>
            </div>

            <div v-if="server.log_entries.length === 0" class="no-logs">
              No log entries found for this server yet.
            </div>
          </div>
        </div>

        <!-- Errors Section -->
        <div v-if="server.errors.length > 0" class="errors-section">
          <div class="errors-header">
            <h4>⚠️ Errors ({{ server.errors.length }})</h4>
          </div>
          <div class="errors-list">
            <div v-for="(error, idx) in server.errors" :key="idx" class="error-item">
              <span class="error-time">{{ formatTime(error.timestamp) }}</span>
              <span class="error-message">{{ error.message }}</span>
            </div>
          </div>
        </div>

        <!-- Server Stats -->
        <div class="server-stats">
          <div class="stat">
            <span class="stat-label">Total Entries:</span>
            <span class="stat-value">{{ server.total_entries || server.log_entries.length }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Errors:</span>
            <span class="stat-value error">{{ server.errors.length }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Last Update:</span>
            <span class="stat-value">{{ formatTime(server.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import apiClient from '@/api/client'

export default {
  name: 'ServerInstallationMonitor',

  setup() {
    const loading = ref(true)
    const installingServers = ref([])
    let refreshInterval = null

    const loadInstallingServers = async () => {
      try {
        // Get all servers with CREATING or INSTALLING status
        const serversResponse = await apiClient.get('/admin/servers', {
          params: {
            status_filter: 'creating,installing,pending'
          }
        })

        const servers = serversResponse.data.data || serversResponse.data

        // Load installation logs for each
        if (servers && servers.length > 0) {
          const detailedServers = await Promise.all(
            servers.map(async (server) => {
              try {
                const logResponse = await apiClient.get(
                  `/admin/shared-system/servers/${server.id}/installation-log`,
                  {
                    params: { lines: 50 }
                  }
                )
                return {
                  ...server,
                  ...logResponse.data
                }
              } catch (err) {
                console.error(`Failed to load logs for server ${server.id}:`, err)
                return {
                  ...server,
                  log_entries: [],
                  errors: [],
                  message: 'Failed to load logs'
                }
              }
            })
          )

          installingServers.value = detailedServers
        } else {
          installingServers.value = []
        }
      } catch (err) {
        console.error('Failed to load installing servers:', err)
        installingServers.value = []
      } finally {
        loading.value = false
      }
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return 'N/A'
      try {
        const date = new Date(timestamp)
        return date.toLocaleTimeString()
      } catch {
        return timestamp
      }
    }

    onMounted(() => {
      loadInstallingServers()

      // Auto-refresh every 2 seconds
      refreshInterval = setInterval(loadInstallingServers, 2000)
    })

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })

    return {
      loading,
      installingServers,
      loadInstallingServers,
      formatTime
    }
  }
}
</script>

<style scoped>
.installation-monitor {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.monitor-header {
  margin-bottom: 30px;
}

.monitor-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 5px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 10px;
}

.empty-state p {
  color: #666;
  margin-bottom: 20px;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.servers-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.refresh-info {
  background: #e3f2fd;
  padding: 12px 20px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #1976d2;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.install-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.server-info h3 {
  margin: 0 0 5px 0;
  font-size: 20px;
}

.server-name {
  font-size: 14px;
  opacity: 0.9;
}

.status-badge {
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.status-badge.creating,
.status-badge.installing {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.log-viewer {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.log-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.log-count {
  font-size: 12px;
  color: #666;
  background: #f0f0f0;
  padding: 4px 10px;
  border-radius: 12px;
}

.log-entries {
  background: #1e1e1e;
  border-radius: 4px;
  padding: 15px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #d4d4d4;
}

.log-entry {
  display: flex;
  gap: 10px;
  padding: 4px 0;
  border-bottom: 1px solid #2d2d2d;
}

.log-entry:last-child {
  border-bottom: none;
}

.timestamp {
  color: #858585;
  min-width: 80px;
}

.level {
  min-width: 60px;
  font-weight: 600;
}

.level.info {
  color: #4fc3f7;
}

.level.warning {
  color: #ffb74d;
}

.level.error, .level.critical {
  color: #e57373;
}

.message {
  flex: 1;
  word-break: break-word;
}

.no-logs {
  text-align: center;
  color: #858585;
  padding: 20px;
}

.errors-section {
  padding: 20px;
  background: #fff3cd;
  border-bottom: 1px solid #e0e0e0;
}

.errors-header h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #856404;
}

.errors-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-item {
  background: white;
  padding: 10px;
  border-radius: 4px;
  border-left: 3px solid #e74c3c;
  display: flex;
  gap: 10px;
}

.error-time {
  color: #666;
  font-size: 12px;
  min-width: 80px;
}

.error-message {
  flex: 1;
  color: #c0392b;
  font-size: 13px;
}

.server-stats {
  padding: 15px 20px;
  background: #f8f9fa;
  display: flex;
  gap: 30px;
}

.stat {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.stat-label {
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-weight: 600;
  color: #333;
}

.stat-value.error {
  color: #e74c3c;
}
</style>
