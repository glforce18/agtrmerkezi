<template>
  <div class="players-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>👥 Oyuncu Yönetimi</h2>
        <span class="player-count">{{ players.length }} Oyuncu Online</span>
      </div>
      <div class="header-right">
        <button @click="refreshPlayers" :disabled="loading" class="btn-refresh">
          <span :class="{ spinning: loading }">🔄</span> Yenile
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && players.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>Oyuncu listesi yükleniyor...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && players.length === 0" class="empty-state">
      <div class="empty-icon">🎮</div>
      <h3>Sunucuda oyuncu yok</h3>
      <p>Şu anda sunucuda aktif oyuncu bulunmuyor</p>
    </div>

    <!-- Players Table -->
    <div v-else class="players-table-container">
      <table class="players-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Oyuncu İsmi</th>
            <th>Steam ID</th>
            <th>Frag</th>
            <th>Süre</th>
            <th>Ping</th>
            <th class="actions-col">İşlemler</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="player in players" :key="player.userid" class="player-row">
            <td class="player-id">{{ player.id }}</td>
            <td class="player-name">
              <div class="name-cell">
                <span class="name-text">{{ player.name }}</span>
              </div>
            </td>
            <td class="player-steamid">
              <code>{{ player.uniqueid }}</code>
            </td>
            <td class="player-frag">{{ player.frag }}</td>
            <td class="player-time">{{ player.time }}</td>
            <td class="player-ping">
              <span class="ping-badge" :class="getPingClass(player.ping)">
                {{ player.ping }}ms
              </span>
            </td>
            <td class="actions-col">
              <div class="action-buttons">
                <button
                  @click="sendMessage(player)"
                  class="btn-action btn-message"
                  title="Mesaj gönder"
                >
                  💬
                </button>
                <button
                  @click="kickPlayer(player)"
                  class="btn-action btn-kick"
                  title="Oyuncuyu at"
                >
                  ⚡
                </button>
                <button
                  @click="banPlayer(player)"
                  class="btn-action btn-ban"
                  title="Oyuncuyu yasakla"
                >
                  🚫
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Message Dialog -->
    <div v-if="showMessageDialog" class="modal-overlay" @click="showMessageDialog = false">
      <div class="modal-content" @click.stop>
        <h3>💬 Oyuncuya Mesaj Gönder</h3>
        <p class="modal-subtitle">{{ selectedPlayer?.name }}</p>

        <textarea
          v-model="messageText"
          placeholder="Mesajınızı yazın..."
          class="message-input"
          rows="4"
        ></textarea>

        <div class="modal-actions">
          <button @click="confirmSendMessage" :disabled="!messageText.trim()" class="btn-primary">
            Gönder
          </button>
          <button @click="showMessageDialog = false" class="btn-secondary">
            İptal
          </button>
        </div>
      </div>
    </div>

    <!-- Kick Confirm Dialog -->
    <div v-if="showKickDialog" class="modal-overlay" @click="showKickDialog = false">
      <div class="modal-content" @click.stop>
        <h3>⚡ Oyuncuyu At</h3>
        <p class="modal-subtitle">{{ selectedPlayer?.name }}</p>
        <p class="warning-text">Bu oyuncuyu sunucudan atmak istediğinizden emin misiniz?</p>

        <input
          v-model="kickReason"
          type="text"
          placeholder="Sebep (opsiyonel)"
          class="reason-input"
        />

        <div class="modal-actions">
          <button @click="confirmKick" class="btn-danger">
            Oyuncuyu At
          </button>
          <button @click="showKickDialog = false" class="btn-secondary">
            İptal
          </button>
        </div>
      </div>
    </div>

    <!-- Ban Confirm Dialog -->
    <div v-if="showBanDialog" class="modal-overlay" @click="showBanDialog = false">
      <div class="modal-content" @click.stop>
        <h3>🚫 Oyuncuyu Yasakla</h3>
        <p class="modal-subtitle">{{ selectedPlayer?.name }}</p>
        <p class="warning-text">Bu oyuncu Steam ID'si ile kalıcı olarak yasaklanacak!</p>

        <div class="ban-info">
          <strong>Steam ID:</strong> <code>{{ selectedPlayer?.uniqueid }}</code>
        </div>

        <input
          v-model="banReason"
          type="text"
          placeholder="Sebep (opsiyonel)"
          class="reason-input"
        />

        <div class="modal-actions">
          <button @click="confirmBan" class="btn-danger">
            Kalıcı Yasakla
          </button>
          <button @click="showBanDialog = false" class="btn-secondary">
            İptal
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/api/client'

const route = useRoute()
const serverId = route.params.id

const players = ref([])
const loading = ref(false)
const refreshInterval = ref(null)

const showMessageDialog = ref(false)
const showKickDialog = ref(false)
const showBanDialog = ref(false)
const selectedPlayer = ref(null)
const messageText = ref('')
const kickReason = ref('')
const banReason = ref('')

const fetchPlayers = async () => {
  try {
    loading.value = true
    const response = await apiClient.get(`/servers/${serverId}/players`)

    if (response.data.success) {
      players.value = response.data.players
    }
  } catch (error) {
    console.error('[PLAYERS] Failed to fetch players:', error)
  } finally {
    loading.value = false
  }
}

const refreshPlayers = () => {
  fetchPlayers()
}

const sendMessage = (player) => {
  selectedPlayer.value = player
  messageText.value = ''
  showMessageDialog.value = true
}

const confirmSendMessage = async () => {
  if (!messageText.value.trim()) return

  try {
    await apiClient.post(`/servers/${serverId}/rcon`, {
      command: `say "${messageText.value}"`
    })

    showMessageDialog.value = false
    messageText.value = ''
  } catch (error) {
    console.error('[PLAYERS] Failed to send message:', error)
    alert('Mesaj gönderilemedi!')
  }
}

const kickPlayer = (player) => {
  selectedPlayer.value = player
  kickReason.value = ''
  showKickDialog.value = true
}

const confirmKick = async () => {
  try {
    const reason = kickReason.value.trim() || 'Kicked by admin'
    await apiClient.post(`/servers/${serverId}/rcon`, {
      command: `kick #${selectedPlayer.value.userid} "${reason}"`
    })

    showKickDialog.value = false
    kickReason.value = ''

    // Refresh player list after 1 second
    setTimeout(fetchPlayers, 1000)
  } catch (error) {
    console.error('[PLAYERS] Failed to kick player:', error)
    alert('Oyuncu atılamadı!')
  }
}

const banPlayer = (player) => {
  selectedPlayer.value = player
  banReason.value = ''
  showBanDialog.value = true
}

const confirmBan = async () => {
  try {
    const reason = banReason.value.trim() || 'Banned by admin'
    // Use banid command with 0 minutes (permanent ban)
    await apiClient.post(`/servers/${serverId}/rcon`, {
      command: `banid 0 ${selectedPlayer.value.uniqueid} kick`
    })

    // Also add to listid.cfg
    await apiClient.post(`/servers/${serverId}/rcon`, {
      command: `writeid`
    })

    showBanDialog.value = false
    banReason.value = ''

    // Refresh player list after 1 second
    setTimeout(fetchPlayers, 1000)
  } catch (error) {
    console.error('[PLAYERS] Failed to ban player:', error)
    alert('Oyuncu yasaklanamadı!')
  }
}

const getPingClass = (ping) => {
  if (ping < 50) return 'ping-good'
  if (ping < 100) return 'ping-ok'
  return 'ping-bad'
}

onMounted(() => {
  fetchPlayers()

  // Auto-refresh every 10 seconds
  refreshInterval.value = setInterval(fetchPlayers, 10000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.players-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.header-left h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.player-count {
  font-size: 14px;
  opacity: 0.9;
}

.btn-refresh {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #8b949e;
}

.spinner {
  border: 4px solid #30363d;
  border-top: 4px solid #58a6ff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #c9d1d9;
  margin-bottom: 10px;
}

.players-table-container {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 12px;
  overflow: hidden;
}

.players-table {
  width: 100%;
  border-collapse: collapse;
}

.players-table thead {
  background: #161b22;
}

.players-table th {
  padding: 15px;
  text-align: left;
  color: #8b949e;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #30363d;
}

.players-table tbody tr {
  border-bottom: 1px solid #21262d;
  transition: background 0.2s ease;
}

.players-table tbody tr:hover {
  background: #161b22;
}

.players-table td {
  padding: 15px;
  color: #c9d1d9;
  font-size: 14px;
}

.player-id {
  color: #6e7681;
  font-weight: bold;
}

.player-name .name-text {
  font-weight: 500;
}

.player-steamid code {
  background: #21262d;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #58a6ff;
}

.ping-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.ping-good {
  background: rgba(46, 160, 67, 0.2);
  color: #3fb950;
}

.ping-ok {
  background: rgba(210, 153, 34, 0.2);
  color: #d29922;
}

.ping-bad {
  background: rgba(248, 81, 73, 0.2);
  color: #f85149;
}

.actions-col {
  width: 180px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-action {
  background: #21262d;
  border: 1px solid #30363d;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s ease;
}

.btn-action:hover {
  transform: translateY(-2px);
}

.btn-message:hover {
  background: #238636;
  border-color: #2ea043;
}

.btn-kick:hover {
  background: #d29922;
  border-color: #e2a822;
}

.btn-ban:hover {
  background: #da3633;
  border-color: #f85149;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  color: #c9d1d9;
  margin: 0 0 10px 0;
}

.modal-subtitle {
  color: #8b949e;
  margin-bottom: 20px;
  font-size: 14px;
}

.warning-text {
  color: #f85149;
  margin-bottom: 20px;
  padding: 12px;
  background: rgba(248, 81, 73, 0.1);
  border-left: 3px solid #f85149;
  border-radius: 4px;
}

.ban-info {
  background: #161b22;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  color: #c9d1d9;
}

.message-input,
.reason-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid #30363d;
  color: #c9d1d9;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 20px;
  font-family: inherit;
  resize: vertical;
}

.message-input:focus,
.reason-input:focus {
  outline: none;
  border-color: #58a6ff;
}

.modal-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #238636;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2ea043;
}

.btn-primary:disabled {
  background: #21262d;
  color: #6e7681;
  cursor: not-allowed;
}

.btn-danger {
  background: #da3633;
  color: white;
}

.btn-danger:hover {
  background: #f85149;
}

.btn-secondary {
  background: #21262d;
  color: #c9d1d9;
  border: 1px solid #30363d;
}

.btn-secondary:hover {
  background: #30363d;
}
</style>
