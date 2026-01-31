<template>
  <div class="logs-page">
    <!-- Header with Tabs -->
    <div class="logs-header">
      <div class="header-content">
        <h2>📜 Server Logs</h2>
        <div class="tabs">
          <button
            @click="activeTab = 'plugin'"
            :class="['tab-btn', { active: activeTab === 'plugin' }]"
          >
            🔌 Plugin Logs
          </button>
          <button
            @click="activeTab = 'error'"
            :class="['tab-btn', { active: activeTab === 'error' }]"
          >
            ❌ Error Logs
          </button>
          <button
            @click="activeTab = 'chat'"
            :class="['tab-btn', { active: activeTab === 'chat' }]"
          >
            💬 Chat Logs
          </button>
        </div>
      </div>

      <!-- Controls -->
      <div class="controls">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="🔍 Ara..."
            class="search-input"
          />
        </div>

        <button
          @click="togglePause"
          :class="['btn-control', { active: isPaused }]"
          :title="isPaused ? 'Devam Et' : 'Duraklat'"
        >
          {{ isPaused ? '▶️' : '⏸️' }}
        </button>

        <button
          @click="clearLogs"
          class="btn-control"
          title="Temizle"
        >
          🧹
        </button>

        <button
          @click="downloadLogs"
          class="btn-control"
          title="İndir"
        >
          💾
        </button>

        <button
          @click="fetchLogs(true)"
          :disabled="loading"
          class="btn-control"
          title="Yenile"
        >
          <span :class="{ spinning: loading }">🔄</span>
        </button>
      </div>
    </div>

    <!-- Log Content -->
    <div class="log-container" ref="logArea">
      <!-- Empty State -->
      <div v-if="!loading && filteredLines.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>{{ searchQuery ? 'Sonuç bulunamadı' : 'Log dosyası boş' }}</h3>
        <p v-if="searchQuery">
          "{{ searchQuery }}" için eşleşen satır bulunamadı
        </p>
        <p v-else>
          {{ getTabDescription() }}
        </p>
      </div>

      <!-- Log Lines -->
      <div v-else class="log-lines">
        <div
          v-for="(line, index) in filteredLines"
          :key="index"
          :class="['log-line', getLineClass(line)]"
        >
          <span class="line-number">{{ line.number }}</span>
          <span class="line-content">{{ line.text }}</span>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <span>Log yükleniyor...</span>
      </div>
    </div>

    <!-- Footer Stats -->
    <div class="logs-footer">
      <div class="stats">
        <span class="stat-item">
          📊 Toplam: <strong>{{ logLines.length }}</strong> satır
        </span>
        <span v-if="searchQuery" class="stat-item">
          🔍 Bulunan: <strong>{{ filteredLines.length }}</strong> satır
        </span>
        <span class="stat-item">
          {{ isPaused ? '⏸️ Duraklatıldı' : '🔄 Canlı' }}
        </span>
        <span class="stat-item">
          📁 {{ getTabName() }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/api/client'

const route = useRoute()
const serverId = route.params.id

const activeTab = ref('plugin')
const logLines = ref([])
const searchQuery = ref('')
const isPaused = ref(false)
const loading = ref(false)
const pollInterval = ref(null)
const logArea = ref(null)
const lastLineCount = ref(0)

const filteredLines = computed(() => {
  if (!searchQuery.value) return logLines.value

  const query = searchQuery.value.toLowerCase()
  return logLines.value.filter(line =>
    line.text.toLowerCase().includes(query)
  )
})

const getTabName = () => {
  const names = {
    plugin: 'L*.log',
    error: 'error*.log',
    chat: 'monster*.log'
  }
  return names[activeTab.value] || 'Unknown'
}

const getTabDescription = () => {
  const descriptions = {
    plugin: 'AMX Mod X plugin logları burada görünecek',
    error: 'Plugin hata logları burada görünecek',
    chat: 'Oyuncu chat mesajları burada görünecek'
  }
  return descriptions[activeTab.value] || ''
}

const getLineClass = (line) => {
  const text = line.text.toLowerCase()

  if (activeTab.value === 'error' || text.includes('error') || text.includes('failed')) {
    return 'line-error'
  }
  if (text.includes('warning') || text.includes('warn')) {
    return 'line-warning'
  }
  if (text.includes('info') || text.includes('started') || text.includes('loaded')) {
    return 'line-info'
  }
  if (activeTab.value === 'chat') {
    return 'line-chat'
  }

  return ''
}

const fetchLogs = async (force = false) => {
  if (isPaused.value && !force) return

  try {
    loading.value = true

    const response = await apiClient.get(`/servers/${serverId}/logs`, {
      params: {
        type: activeTab.value,
        lines: 200
      }
    })

    if (response.data.success) {
      const newLines = response.data.lines.map((text, index) => ({
        number: index + 1,
        text: text
      }))

      // Only auto-scroll if new lines were added
      const shouldScroll = newLines.length > lastLineCount.value
      lastLineCount.value = newLines.length

      logLines.value = newLines

      if (shouldScroll && !isPaused.value) {
        nextTick(() => {
          scrollToBottom()
        })
      }
    }
  } catch (error) {
    console.error('[LOGS] Failed to fetch logs:', error)
  } finally {
    loading.value = false
  }
}

const scrollToBottom = () => {
  if (logArea.value) {
    logArea.value.scrollTop = logArea.value.scrollHeight
  }
}

const togglePause = () => {
  isPaused.value = !isPaused.value
}

const clearLogs = () => {
  logLines.value = []
  lastLineCount.value = 0
}

const downloadLogs = () => {
  const content = logLines.value.map(line => line.text).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `server_${serverId}_${activeTab.value}_logs_${Date.now()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const startPolling = () => {
  fetchLogs()
  pollInterval.value = setInterval(() => {
    if (!isPaused.value) {
      fetchLogs()
    }
  }, 5000) // Poll every 5 seconds
}

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

// Watch tab changes
watch(activeTab, () => {
  clearLogs()
  fetchLogs(true)
})

onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.logs-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 180px);
  background: #0d1117;
  border-radius: 12px;
  overflow: hidden;
}

.logs-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  color: white;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
}

.tabs {
  display: flex;
  gap: 10px;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.tab-btn.active {
  background: rgba(255, 255, 255, 0.4);
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn-control {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s ease;
  min-width: 40px;
}

.btn-control:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-control:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-control.active {
  background: rgba(255, 255, 255, 0.4);
}

.spinning {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.log-container {
  flex: 1;
  background: #0d1117;
  overflow-y: auto;
  position: relative;
  padding: 0;
}

.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: #161b22;
}

.log-container::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8b949e;
  padding: 40px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #c9d1d9;
  margin-bottom: 10px;
}

.log-lines {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-line {
  display: flex;
  padding: 4px 15px;
  border-bottom: 1px solid #161b22;
  transition: background 0.1s ease;
}

.log-line:hover {
  background: #161b22;
}

.line-number {
  color: #6e7681;
  min-width: 50px;
  text-align: right;
  margin-right: 15px;
  user-select: none;
  flex-shrink: 0;
}

.line-content {
  color: #c9d1d9;
  word-break: break-word;
  white-space: pre-wrap;
}

.line-error .line-content {
  color: #f85149;
  background: rgba(248, 81, 73, 0.1);
  padding: 2px 4px;
  border-left: 3px solid #f85149;
}

.line-warning .line-content {
  color: #d29922;
  background: rgba(210, 153, 34, 0.1);
  padding: 2px 4px;
  border-left: 3px solid #d29922;
}

.line-info .line-content {
  color: #58a6ff;
}

.line-chat .line-content {
  color: #a371f7;
}

.loading-indicator {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #161b22;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #c9d1d9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.spinner {
  border: 3px solid #30363d;
  border-top: 3px solid #58a6ff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

.logs-footer {
  background: #161b22;
  border-top: 1px solid #30363d;
  padding: 12px 20px;
  flex-shrink: 0;
}

.stats {
  display: flex;
  gap: 20px;
  color: #8b949e;
  font-size: 13px;
}

.stat-item strong {
  color: #c9d1d9;
  font-weight: 600;
}
</style>
