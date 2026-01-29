<template>
  <div class="min-h-screen bg-dark-bg">
    <div class="container mx-auto px-4 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-20">
        <div class="inline-block animate-spin text-primary text-6xl mb-4">⚙️</div>
        <p class="text-text-secondary text-lg">Server loading...</p>
      </div>

      <div v-else-if="server" class="space-y-6">
        <!-- Header -->
        <div class="flex items-center justify-between">
          <div>
            <router-link to="/servers/my" class="text-text-secondary hover:text-primary mb-2 inline-flex items-center gap-2 transition-colors">
              <span>←</span>
              <span>Back to Servers</span>
            </router-link>
            <h1 class="text-4xl font-bold text-text-primary mt-2">
              <span class="text-primary">{{ server.name }}</span>
            </h1>
            <p class="text-text-secondary font-mono mt-1">{{ server.ip_address }}:{{ server.port }}</p>
          </div>
          <div
            class="px-6 py-3 rounded-lg text-sm font-bold uppercase tracking-wider"
            :class="statusClass(server.status)"
          >
            <span class="inline-block w-3 h-3 rounded-full mr-2 animate-pulse" :class="statusDotClass(server.status)"></span>
            {{ statusText(server.status) }}
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="card bg-dark-card border border-dark-border rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-text-muted text-xs uppercase tracking-wide mb-1">Players Online</div>
                <div class="text-3xl font-bold text-green-400">{{ server.current_players }}/{{ server.slots }}</div>
              </div>
              <div class="text-4xl opacity-20">👥</div>
            </div>
          </div>

          <div class="card bg-dark-card border border-dark-border rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-text-muted text-xs uppercase tracking-wide mb-1">Current Map</div>
                <div class="text-lg font-bold text-purple-400 truncate">{{ server.map || 'de_dust2' }}</div>
              </div>
              <div class="text-4xl opacity-20">🗺️</div>
            </div>
          </div>

          <div class="card bg-dark-card border border-dark-border rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-text-muted text-xs uppercase tracking-wide mb-1">Game Type</div>
                <div class="text-lg font-bold text-cyan-400">{{ getGameTypeName(server.game_type) }}</div>
              </div>
              <div class="text-4xl opacity-20">🎮</div>
            </div>
          </div>

          <div class="card bg-dark-card border border-dark-border rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-text-muted text-xs uppercase tracking-wide mb-1">Uptime</div>
                <div class="text-lg font-bold text-primary">24h 32m</div>
              </div>
              <div class="text-4xl opacity-20">⏱️</div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card bg-dark-card border border-dark-border rounded-lg p-6">
          <h2 class="text-xl font-bold text-text-primary mb-4">Server Control</h2>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <button
              v-if="server.status === 'stopped'"
              @click="handleStart"
              class="btn btn-success px-4 py-2 rounded-lg font-semibold transition-all"
            >
              ▶ Start Server
            </button>
            <button
              v-if="server.status === 'running'"
              @click="handleStop"
              class="btn btn-error px-4 py-2 rounded-lg font-semibold transition-all"
            >
              ⏹ Stop Server
            </button>
            <button
              v-if="server.status === 'running'"
              @click="handleRestart"
              class="btn btn-warning px-4 py-2 rounded-lg font-semibold transition-all"
            >
              🔄 Restart
            </button>
            <button
              @click="fetchPlayers"
              class="btn btn-secondary px-4 py-2 rounded-lg font-semibold transition-all"
            >
              👥 Refresh Players
            </button>
          </div>
        </div>

        <!-- RCON Terminal Console -->
        <div class="card bg-dark-elevated border border-dark-border rounded-lg overflow-hidden">
          <div class="p-4 border-b border-dark-border">
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-bold text-text-primary font-mono">
                <span class="text-primary">λ</span> RCON TERMINAL
              </h2>
              <div class="text-xs text-text-muted font-mono">SERVER #{{ server.id }}</div>
            </div>
          </div>

          <!-- Terminal Screen -->
          <div class="terminal">
            <!-- Output Area -->
            <div class="terminal-output" ref="consoleOutput">
              <div class="terminal-boot mb-4">
                <div class="text-green-400 font-mono text-xs">
                  <div>╔═══════════════════════════════════════════════════════════╗</div>
                  <div>║  AGTR Merkezi - Remote Console Access System v3.0        ║</div>
                  <div>║  Connected to: {{ server.name.toUpperCase() }}            ║</div>
                  <div>╚═══════════════════════════════════════════════════════════╝</div>
                </div>
              </div>

              <div v-for="(line, index) in consoleHistory" :key="index" class="terminal-line">
                <div class="terminal-command">
                  <span class="terminal-prompt">root@server-{{ server.id }}:~$</span>
                  <span class="terminal-text">{{ line.command }}</span>
                </div>
                <pre v-if="line.output" class="terminal-response">{{ line.output }}</pre>
                <div v-if="line.error" class="terminal-error">
                  <span class="text-red-400">ERROR:</span> {{ line.error }}
                </div>
              </div>

              <div v-if="executing" class="terminal-line">
                <span class="text-yellow-400 animate-pulse">► Executing command...</span>
              </div>
            </div>

            <!-- Input Area -->
            <div class="terminal-input-wrapper">
              <span class="terminal-prompt">root@server-{{ server.id }}:~$</span>
              <input
                v-model="rconCommand"
                @keyup.enter="executeCommand"
                @keyup.up="navigateHistory('up')"
                @keyup.down="navigateHistory('down')"
                class="terminal-input"
                placeholder="Enter command... (type 'help' for available commands)"
                :disabled="executing"
                ref="terminalInput"
              />
              <span class="terminal-cursor">|</span>
            </div>
          </div>

          <div class="p-4 border-t border-dark-border bg-dark-card">
            <!-- Quick Commands -->
            <p class="text-text-muted text-xs uppercase tracking-wide mb-2">Quick Commands:</p>
            <div class="flex flex-wrap gap-2">
              <button @click="quickCommand('status')" class="quick-cmd">status</button>
              <button @click="quickCommand('users')" class="quick-cmd">users</button>
              <button @click="quickCommand('maps *')" class="quick-cmd">maps</button>
              <button @click="quickCommand('changelevel de_dust2')" class="quick-cmd">de_dust2</button>
              <button @click="quickCommand('say Welcome to AGTR Server!')" class="quick-cmd">announce</button>
              <button @click="quickCommand('stats')" class="quick-cmd">stats</button>
            </div>
          </div>
        </div>

        <!-- Active Players -->
        <div v-if="players.length > 0" class="card bg-dark-card border border-dark-border rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold text-text-primary">Active Players ({{ players.length }})</h2>
            <button @click="fetchPlayers" class="btn btn-secondary text-sm px-4 py-2 rounded-lg">
              🔄 Refresh
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-dark-border">
                  <th class="px-4 py-3 text-left text-text-muted text-xs uppercase tracking-wide">Slot</th>
                  <th class="px-4 py-3 text-left text-text-muted text-xs uppercase tracking-wide">Player Name</th>
                  <th class="px-4 py-3 text-left text-text-muted text-xs uppercase tracking-wide">Steam ID</th>
                  <th class="px-4 py-3 text-left text-text-muted text-xs uppercase tracking-wide">Time</th>
                  <th class="px-4 py-3 text-right text-text-muted text-xs uppercase tracking-wide">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="player in players"
                  :key="player.slot"
                  class="border-b border-dark-border hover:bg-dark-elevated transition-colors"
                >
                  <td class="px-4 py-3 text-cyan-400 font-mono text-sm">#{{ player.slot }}</td>
                  <td class="px-4 py-3 text-text-primary font-semibold">{{ player.name }}</td>
                  <td class="px-4 py-3 text-text-secondary font-mono text-sm">{{ player.steamid }}</td>
                  <td class="px-4 py-3 text-text-secondary text-sm">{{ formatTime(player.time) }}</td>
                  <td class="px-4 py-3 text-right">
                    <button
                      @click="kickPlayer(player.slot, player.name)"
                      class="btn btn-error text-xs px-3 py-1 rounded"
                    >
                      Kick
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Empty Players State -->
        <div v-else class="card bg-dark-card border border-dark-border rounded-lg p-6">
          <div class="text-center py-12">
            <div class="text-6xl mb-4 opacity-30">👻</div>
            <p class="text-text-secondary">No players online</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import serversAPI from '@/api/servers'

const route = useRoute()
const serverId = parseInt(route.params.id)

const server = ref(null)
const loading = ref(true)
const rconCommand = ref('')
const consoleHistory = ref([])
const executing = ref(false)
const consoleOutput = ref(null)
const terminalInput = ref(null)
const players = ref([])

const commandHistory = ref([])
const historyIndex = ref(-1)

onMounted(async () => {
  await fetchServer()
  await fetchPlayers()

  // Focus terminal input
  nextTick(() => {
    if (terminalInput.value) {
      terminalInput.value.focus()
    }
  })
})

const fetchServer = async () => {
  try {
    const response = await serversAPI.getServer(serverId)
    server.value = response.data
  } catch (error) {
    console.error('Failed to fetch server:', error)
  } finally {
    loading.value = false
  }
}

const fetchPlayers = async () => {
  try {
    const response = await serversAPI.getPlayers(serverId)
    players.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch players:', error)
    players.value = []
  }
}

const executeCommand = async () => {
  if (!rconCommand.value.trim() || executing.value) return

  const cmd = rconCommand.value.trim()
  executing.value = true

  // Add to history
  commandHistory.value.push(cmd)
  historyIndex.value = commandHistory.value.length

  try {
    const response = await serversAPI.executeRCON(serverId, cmd)

    consoleHistory.value.push({
      command: cmd,
      output: response.data.output || response.data.message || 'Command executed',
      timestamp: new Date()
    })
  } catch (error) {
    consoleHistory.value.push({
      command: cmd,
      error: error.response?.data?.detail || 'Command failed',
      timestamp: new Date()
    })
  } finally {
    executing.value = false
    rconCommand.value = ''

    // Scroll to bottom
    nextTick(() => {
      if (consoleOutput.value) {
        consoleOutput.value.scrollTop = consoleOutput.value.scrollHeight
      }
    })
  }
}

const quickCommand = (cmd) => {
  rconCommand.value = cmd
  executeCommand()
}

const navigateHistory = (direction) => {
  if (direction === 'up' && historyIndex.value > 0) {
    historyIndex.value--
    rconCommand.value = commandHistory.value[historyIndex.value]
  } else if (direction === 'down' && historyIndex.value < commandHistory.value.length - 1) {
    historyIndex.value++
    rconCommand.value = commandHistory.value[historyIndex.value]
  } else if (direction === 'down' && historyIndex.value === commandHistory.value.length - 1) {
    historyIndex.value = commandHistory.value.length
    rconCommand.value = ''
  }
}

const handleStart = async () => {
  try {
    await serversAPI.startServer(serverId)
    await fetchServer()
  } catch (error) {
    alert('Failed to start server: ' + error.message)
  }
}

const handleStop = async () => {
  try {
    await serversAPI.stopServer(serverId)
    await fetchServer()
  } catch (error) {
    alert('Failed to stop server: ' + error.message)
  }
}

const handleRestart = async () => {
  try {
    await serversAPI.restartServer(serverId)
    await fetchServer()
  } catch (error) {
    alert('Failed to restart server: ' + error.message)
  }
}

const kickPlayer = async (slot, name) => {
  if (!confirm(`Kick player ${name}?`)) return

  try {
    await serversAPI.kickPlayer(serverId, slot)
    await fetchPlayers()
  } catch (error) {
    alert('Failed to kick player: ' + error.message)
  }
}

const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

const getGameTypeName = (game) => {
  const names = {
    'cs16': 'CS 1.6',
    'ag': 'AG',
    'hldm': 'HLDM'
  }
  return names[game] || game
}

// Status helpers
const statusClass = (status) => {
  const classes = {
    running: 'badge-success',
    stopped: 'badge-neutral',
    starting: 'badge-warning',
    error: 'badge-error'
  }
  return classes[status] || classes.stopped
}

const statusDotClass = (status) => {
  const classes = {
    running: 'bg-green-400',
    stopped: 'bg-gray-400',
    starting: 'bg-yellow-400',
    error: 'bg-red-400'
  }
  return classes[status] || classes.stopped
}

const statusText = (status) => {
  const texts = {
    running: 'ONLINE',
    stopped: 'OFFLINE',
    starting: 'STARTING',
    error: 'ERROR'
  }
  return texts[status] || 'OFFLINE'
}
</script>

<style scoped>
/* Terminal Styles */
.terminal {
  background: #0a0a0a;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
}

.terminal-output {
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  color: #10b981;
  font-size: 13px;
  line-height: 1.6;
}

.terminal-output::-webkit-scrollbar {
  width: 8px;
}

.terminal-output::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.3);
}

.terminal-output::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

.terminal-output::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}

.terminal-boot {
  color: #10b981;
}

.terminal-line {
  margin-bottom: 12px;
}

.terminal-command {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.terminal-prompt {
  color: #ff6b35;
  font-weight: bold;
}

.terminal-text {
  color: #06b6d4;
}

.terminal-response {
  color: #9ca3af;
  padding-left: 24px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
}

.terminal-error {
  padding-left: 24px;
  color: #ef4444;
}

.terminal-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #000000;
  border-top: 1px solid #1f2937;
}

.terminal-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #06b6d4;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 13px;
}

.terminal-input::placeholder {
  color: #374151;
}

.terminal-cursor {
  color: #10b981;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* Quick Commands */
.quick-cmd {
  padding: 6px 12px;
  background: rgba(31, 41, 55, 0.5);
  border: 1px solid #374151;
  border-radius: 4px;
  color: #9ca3af;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-cmd:hover {
  background: #1f2937;
  border-color: #4b5563;
  color: #d1d5db;
}

/* Button Styles */
.btn {
  font-weight: 600;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background: #ff6b35;
  color: white;
  border-color: #ff6b35;
}

.btn-primary:hover {
  background: #ff8555;
  border-color: #ff8555;
}

.btn-secondary {
  background: #374151;
  color: #d1d5db;
  border-color: #4b5563;
}

.btn-secondary:hover {
  background: #4b5563;
  border-color: #6b7280;
}

.btn-success {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.btn-success:hover {
  background: #059669;
  border-color: #059669;
}

.btn-error {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

.btn-error:hover {
  background: #dc2626;
  border-color: #dc2626;
}

.btn-warning {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

.btn-warning:hover {
  background: #d97706;
  border-color: #d97706;
}

/* Badge Styles */
.badge-success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-neutral {
  background: rgba(107, 114, 128, 0.1);
  color: #9ca3af;
  border: 1px solid rgba(107, 114, 128, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .terminal-output {
    max-height: 300px;
    font-size: 11px;
  }

  .terminal-input {
    font-size: 12px;
  }
}
</style>
