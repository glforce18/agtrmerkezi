<template>
  <div class="console-page">
    <!-- Header with Tabs -->
    <div class="console-header">
      <div class="header-content">
        <h2>🖥️ Console</h2>
        <div class="tabs">
          <button
            @click="activeTab = 'rcon'"
            :class="['tab-btn', { active: activeTab === 'rcon' }]"
          >
            ⌨️ RCON
          </button>
          <button
            @click="activeTab = 'chat'"
            :class="['tab-btn', { active: activeTab === 'chat' }]"
          >
            💬 Live Chat
          </button>
        </div>
      </div>
      <div class="quick-commands" v-if="activeTab === 'rcon'">
        <button @click="executeQuickCommand('status')" class="quick-btn" title="Server durumunu göster">
          📊 Status
        </button>
        <button @click="executeQuickCommand('stats')" class="quick-btn" title="Server istatistikleri">
          📈 Stats
        </button>
        <button @click="showMapDialog = true" class="quick-btn" title="Harita değiştir">
          🗺️ Changelevel
        </button>
        <button @click="executeQuickCommand('restart')" class="quick-btn confirm-btn" title="Sunucuyu yeniden başlat">
          🔄 Restart
        </button>
      </div>
    </div>

    <!-- RCON Console -->
    <div v-if="activeTab === 'rcon'" class="console-output" ref="outputArea">
      <div v-if="consoleLines.length === 0" class="empty-state">
        <p>Console hazır. Komut girmek için aşağıdaki input alanını kullanın.</p>
        <p class="hint">Örnek komutlar: status, users, changelevel crossfire, say "Merhaba!"</p>
      </div>

      <div v-for="(line, index) in consoleLines" :key="index" class="console-line">
        <span class="console-prompt">{{ line.prompt }}</span>
        <span class="console-text" :class="{ 'console-error': line.isError }">{{ line.text }}</span>
      </div>
    </div>

    <!-- Live Chat View -->
    <div v-if="activeTab === 'chat'" class="chat-output" ref="chatArea">
      <div v-if="chatMessages.length === 0" class="empty-state">
        <p>Canlı chat izleniyor...</p>
        <p class="hint">Oyuncular chat'e mesaj yazdığında burada görünecek</p>
      </div>

      <div v-for="(msg, index) in chatMessages" :key="index" class="chat-message">
        <span class="chat-time">{{ msg.time }}</span>
        <span class="chat-player" :style="{ color: msg.color }">{{ msg.player }}:</span>
        <span class="chat-text">{{ msg.message }}</span>
      </div>
    </div>

    <!-- Command Input (RCON only) -->
    <div v-if="activeTab === 'rcon'" class="console-input-container">
      <div class="input-wrapper">
        <span class="prompt-symbol">rcon></span>
        <input
          v-model="currentCommand"
          @keyup.enter="executeCommand"
          @keyup.up="navigateHistory('up')"
          @keyup.down="navigateHistory('down')"
          type="text"
          class="console-input"
          placeholder="Komut girin (örn: status, changelevel crossfire)"
          :disabled="isExecuting"
        />
        <button @click="executeCommand" :disabled="!currentCommand.trim() || isExecuting" class="send-btn">
          {{ isExecuting ? '⏳' : '▶️' }} Gönder
        </button>
      </div>
      <div class="console-hints">
        <span class="hint-text">↑↓ Geçmiş komutlar</span>
        <span class="hint-text">Enter: Komutu çalıştır</span>
      </div>
    </div>

    <!-- Map Change Dialog -->
    <div v-if="showMapDialog" class="modal-overlay" @click="showMapDialog = false">
      <div class="modal-content" @click.stop>
        <h3>Harita Değiştir</h3>
        <div class="map-selection">
          <div class="popular-maps">
            <h4>Popüler Haritalar</h4>
            <div class="map-grid">
              <button
                v-for="map in popularMaps"
                :key="map"
                @click="changeMap(map)"
                class="map-btn"
              >
                {{ map }}
              </button>
            </div>
          </div>
          <div class="custom-map">
            <h4>Özel Harita</h4>
            <input
              v-model="customMapName"
              @keyup.enter="changeMap(customMapName)"
              type="text"
              placeholder="Harita adını girin"
              class="map-input"
            />
            <button @click="changeMap(customMapName)" :disabled="!customMapName.trim()" class="btn-primary">
              Değiştir
            </button>
          </div>
        </div>
        <button @click="showMapDialog = false" class="btn-secondary">İptal</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/api/client'

const route = useRoute()
const serverId = route.params.id

// Tab management
const activeTab = ref('rcon')

// RCON Console
const consoleLines = ref([])
const currentCommand = ref('')
const commandHistory = ref([])
const historyIndex = ref(-1)
const isExecuting = ref(false)
const outputArea = ref(null)

// Live Chat
const chatMessages = ref([])
const chatArea = ref(null)
const chatPollInterval = ref(null)
const lastChatLine = ref(0)

const showMapDialog = ref(false)
const customMapName = ref('')

const popularMaps = [
  'crossfire',
  'boot_camp',
  'bounce',
  'datacore',
  'stalkyard',
  'undertow',
  'lambda_bunker',
  'gasworks'
]

const addConsoleLine = (text, isCommand = false, isError = false) => {
  consoleLines.value.push({
    prompt: isCommand ? '>' : '',
    text,
    isError
  })

  // Auto-scroll to bottom
  nextTick(() => {
    if (outputArea.value) {
      outputArea.value.scrollTop = outputArea.value.scrollHeight
    }
  })
}

const executeCommand = async () => {
  const command = currentCommand.value.trim()
  if (!command || isExecuting.value) return

  // Debug logging
  console.log('[CONSOLE] Executing command:', command)
  console.log('[CONSOLE] Panel mode:', localStorage.getItem('panel_mode'))
  console.log('[CONSOLE] Panel token:', localStorage.getItem('panel_token') ? 'EXISTS' : 'MISSING')
  console.log('[CONSOLE] Server ID:', serverId)

  // Add command to console
  addConsoleLine(command, true)

  // Add to history
  commandHistory.value.unshift(command)
  if (commandHistory.value.length > 50) {
    commandHistory.value.pop()
  }
  historyIndex.value = -1

  // Clear input
  currentCommand.value = ''
  isExecuting.value = true

  try {
    const response = await apiClient.post(`/servers/${serverId}/rcon`, {
      command: command
    })

    console.log('[CONSOLE] Response:', response.data)

    if (response.data.success) {
      const output = response.data.output || '(Komut çalıştırıldı, çıktı yok)'
      // Split output by newlines for better formatting
      const lines = output.split('\n')
      lines.forEach(line => {
        if (line.trim()) {
          addConsoleLine(line)
        }
      })
    } else {
      addConsoleLine(`❌ Hata: ${response.data.error || 'Bilinmeyen hata'}`, false, true)
    }
  } catch (error) {
    console.error('[CONSOLE] Command execution error:', error)
    if (error.response?.data?.detail) {
      addConsoleLine(`❌ ${error.response.data.detail}`, false, true)
    } else {
      addConsoleLine(`❌ Komut çalıştırılamadı: ${error.message}`, false, true)
    }
  } finally {
    isExecuting.value = false
  }
}

const executeQuickCommand = async (cmd) => {
  if (cmd === 'restart') {
    if (!confirm('Sunucuyu yeniden başlatmak istediğinizden emin misiniz?')) {
      return
    }
  }

  currentCommand.value = cmd
  await executeCommand()
}

const changeMap = async (mapName) => {
  if (!mapName || !mapName.trim()) return

  currentCommand.value = `changelevel ${mapName.trim()}`
  showMapDialog.value = false
  customMapName.value = ''
  await executeCommand()
}

const navigateHistory = (direction) => {
  if (commandHistory.value.length === 0) return

  if (direction === 'up') {
    if (historyIndex.value < commandHistory.value.length - 1) {
      historyIndex.value++
      currentCommand.value = commandHistory.value[historyIndex.value]
    }
  } else if (direction === 'down') {
    if (historyIndex.value > 0) {
      historyIndex.value--
      currentCommand.value = commandHistory.value[historyIndex.value]
    } else if (historyIndex.value === 0) {
      historyIndex.value = -1
      currentCommand.value = ''
    }
  }
}

const fetchLiveChat = async () => {
  try {
    const response = await apiClient.get(`/servers/${serverId}/live-chat`, {
      params: { since_line: lastChatLine.value }
    })

    if (response.data.messages && response.data.messages.length > 0) {
      response.data.messages.forEach(msg => {
        chatMessages.value.push(msg)
      })

      // Keep only last 100 messages
      if (chatMessages.value.length > 100) {
        chatMessages.value = chatMessages.value.slice(-100)
      }

      // Update last line
      lastChatLine.value = response.data.last_line

      // Auto-scroll to bottom
      nextTick(() => {
        if (chatArea.value) {
          chatArea.value.scrollTop = chatArea.value.scrollHeight
        }
      })
    }
  } catch (error) {
    console.error('[CHAT] Failed to fetch live chat:', error)
  }
}

const startChatPolling = () => {
  // Initial fetch
  fetchLiveChat()

  // Poll every 5 seconds
  chatPollInterval.value = setInterval(fetchLiveChat, 5000)
}

const stopChatPolling = () => {
  if (chatPollInterval.value) {
    clearInterval(chatPollInterval.value)
    chatPollInterval.value = null
  }
}

onMounted(() => {
  addConsoleLine('='.repeat(60))
  addConsoleLine('🖥️  AGTR Merkezi - Remote Console (RCON)')
  addConsoleLine('='.repeat(60))
  addConsoleLine('')

  // Start live chat polling
  startChatPolling()
})

onUnmounted(() => {
  stopChatPolling()
})
</script>

<style scoped>
.console-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 180px);
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
}

.console-header {
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

.console-header h2 {
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
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
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

.quick-commands {
  display: flex;
  gap: 10px;
}

.quick-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.quick-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.confirm-btn {
  background: rgba(239, 68, 68, 0.3);
}

.confirm-btn:hover {
  background: rgba(239, 68, 68, 0.5);
}

.console-output {
  flex: 1;
  background: #0d1117;
  color: #c9d1d9;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  padding: 20px;
  overflow-y: auto;
  line-height: 1.6;
}

.console-output::-webkit-scrollbar {
  width: 8px;
}

.console-output::-webkit-scrollbar-track {
  background: #161b22;
}

.console-output::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}

.console-output::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}

/* Live Chat Styles */
.chat-output {
  flex: 1;
  background: #0d1117;
  color: #c9d1d9;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  padding: 20px;
  overflow-y: auto;
  line-height: 1.8;
}

.chat-output::-webkit-scrollbar {
  width: 8px;
}

.chat-output::-webkit-scrollbar-track {
  background: #161b22;
}

.chat-output::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}

.chat-output::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}

.chat-message {
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.chat-message:hover {
  background: rgba(56, 139, 253, 0.1);
}

.chat-time {
  color: #6e7681;
  font-size: 12px;
  margin-right: 12px;
  font-family: 'Courier New', monospace;
}

.chat-player {
  font-weight: bold;
  margin-right: 8px;
}

.chat-text {
  color: #c9d1d9;
}

.empty-state {
  text-align: center;
  color: #8b949e;
  padding: 40px;
}

.empty-state .hint {
  margin-top: 10px;
  font-size: 13px;
  color: #6e7681;
}

.console-line {
  margin-bottom: 4px;
  word-wrap: break-word;
}

.console-prompt {
  color: #58a6ff;
  margin-right: 8px;
  font-weight: bold;
}

.console-text {
  color: #c9d1d9;
}

.console-error {
  color: #f85149;
}

.console-input-container {
  background: #161b22;
  border-top: 1px solid #30363d;
  padding: 15px;
  flex-shrink: 0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 10px 15px;
}

.prompt-symbol {
  color: #58a6ff;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  font-size: 16px;
}

.console-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #c9d1d9;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  outline: none;
}

.console-input::placeholder {
  color: #6e7681;
}

.console-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  background: #238636;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  background: #2ea043;
}

.send-btn:disabled {
  background: #21262d;
  color: #6e7681;
  cursor: not-allowed;
}

.console-hints {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  padding-left: 10px;
}

.hint-text {
  color: #6e7681;
  font-size: 12px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a1a;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 30px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  color: #c9d1d9;
  margin-top: 0;
  margin-bottom: 20px;
}

.modal-content h4 {
  color: #8b949e;
  font-size: 14px;
  margin-top: 20px;
  margin-bottom: 10px;
}

.map-selection {
  margin-bottom: 20px;
}

.map-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.map-btn {
  background: #21262d;
  color: #c9d1d9;
  border: 1px solid #30363d;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
}

.map-btn:hover {
  background: #30363d;
  border-color: #58a6ff;
  transform: translateY(-2px);
}

.custom-map {
  margin-top: 20px;
}

.map-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid #30363d;
  color: #c9d1d9;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 14px;
}

.map-input:focus {
  outline: none;
  border-color: #58a6ff;
}

.btn-primary {
  background: #238636;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 10px;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #2ea043;
}

.btn-primary:disabled {
  background: #21262d;
  color: #6e7681;
  cursor: not-allowed;
}

.btn-secondary {
  background: #21262d;
  color: #c9d1d9;
  border: 1px solid #30363d;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #30363d;
}
</style>
