<template>
  <div class="jackpot-page">
    <!-- Header -->
    <div class="jackpot-header">
      <div class="header-info">
        <h1 class="title">
          <TrophyIcon :size="32" class="title-icon" />
          JACKPOT
        </h1>
        <div class="round-info">
          Tur #{{ currentRound?.round_number || '---' }}
          <span class="status-badge" :class="currentRound?.status">
            {{ statusText }}
          </span>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat">
          <span class="stat-value">{{ formatCoin(balance) }}</span>
          <span class="stat-label">Bakiyen</span>
        </div>
        <div class="stat highlight">
          <span class="stat-value">{{ formatCoin(currentRound?.total_pot || 0) }}</span>
          <span class="stat-label">Toplam Havuz</span>
        </div>
      </div>
    </div>

    <!-- Main Game Area -->
    <div class="game-container">
      <!-- Wheel/Spinner Section -->
      <div class="wheel-section">
        <div class="wheel-container" :class="{ spinning: isSpinning }">
          <div class="wheel-pointer"></div>
          <div class="wheel" ref="wheelRef" :style="wheelStyle">
            <div
              v-for="(player, index) in players"
              :key="player.user_id"
              class="wheel-segment"
              :style="getSegmentStyle(player, index)"
            >
              <img :src="player.avatar || getDefaultAvatar(player.username)" :alt="player.username" class="segment-avatar" />
            </div>
          </div>
        </div>

        <!-- Winner Display -->
        <Transition name="winner-popup">
          <div v-if="winner" class="winner-display">
            <div class="winner-content">
              <img :src="winner.avatar || getDefaultAvatar(winner.username)" class="winner-avatar" />
              <div class="winner-info">
                <span class="winner-label">KAZANAN!</span>
                <span class="winner-name">{{ winner.username }}</span>
                <span class="winner-amount">{{ formatCoin(winner.amount) }} Coin</span>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Players & Bets Section -->
      <div class="players-section">
        <div class="section-header">
          <h2>Katılımcılar</h2>
          <span class="player-count">{{ players.length }} oyuncu</span>
        </div>

        <div class="players-list" v-if="players.length > 0">
          <div
            v-for="player in sortedPlayers"
            :key="player.user_id"
            class="player-card"
            :style="{ borderColor: player.color }"
          >
            <img :src="player.avatar || getDefaultAvatar(player.username)" class="player-avatar" />
            <div class="player-info">
              <span class="player-name">{{ player.username }}</span>
              <span class="player-bet">{{ formatCoin(player.total_bet) }} Coin</span>
            </div>
            <div class="player-chance">
              <span class="chance-value">{{ player.win_chance.toFixed(1) }}%</span>
              <div class="chance-bar" :style="{ width: player.win_chance + '%', backgroundColor: player.color }"></div>
            </div>
          </div>
        </div>

        <div v-else class="no-players">
          <UsersIcon :size="48" class="empty-icon" />
          <p>Henüz katılımcı yok</p>
          <p class="small">İlk bahsi sen yap!</p>
        </div>
      </div>
    </div>

    <!-- Bet Section -->
    <div class="bet-section" v-if="!isSpinning && currentRound?.status !== 'finished'">
      <div class="bet-form">
        <div class="bet-input-group">
          <input
            v-model.number="betAmount"
            type="number"
            :min="minBet"
            :max="maxBet"
            placeholder="Bahis miktarı"
            class="bet-input"
          />
          <span class="input-suffix">Coin</span>
        </div>

        <div class="quick-bets">
          <button @click="betAmount = 10" class="quick-btn">10</button>
          <button @click="betAmount = 50" class="quick-btn">50</button>
          <button @click="betAmount = 100" class="quick-btn">100</button>
          <button @click="betAmount = 500" class="quick-btn">500</button>
          <button @click="betAmount = balance" class="quick-btn all-in">ALL IN</button>
        </div>

        <button
          @click="placeBet"
          class="bet-btn"
          :disabled="!canBet || betting"
        >
          <Loader2Icon v-if="betting" :size="20" class="spin" />
          <span v-else>BAHİS YAP</span>
        </button>
      </div>

      <div class="bet-info">
        <span>Min: {{ minBet }} Coin</span>
        <span>Max: {{ maxBet }} Coin</span>
        <span>Komisyon: {{ houseCut }}%</span>
      </div>
    </div>

    <!-- History Section -->
    <div class="history-section">
      <h2>Son Turlar</h2>
      <div class="history-list">
        <div
          v-for="round in recentRounds"
          :key="round.id"
          class="history-item"
        >
          <span class="history-round">#{{ round.round_number }}</span>
          <span class="history-pot">{{ formatCoin(round.total_pot) }}</span>
          <span class="history-winner">{{ round.winner_username }}</span>
          <span class="history-amount text-success">+{{ formatCoin(round.winner_amount) }}</span>
        </div>
      </div>
    </div>

    <!-- Provably Fair -->
    <div class="fairness-section">
      <button @click="showFairnessModal = true" class="fairness-btn">
        <ShieldCheckIcon :size="20" />
        Provably Fair
      </button>
    </div>

    <!-- Fairness Modal -->
    <Teleport to="body">
      <div v-if="showFairnessModal" class="modal-overlay" @click.self="showFairnessModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Provably Fair Doğrulama</h3>
            <button @click="showFairnessModal = false" class="close-btn">
              <XIcon :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <p>Her tur başında sunucu bir seed oluşturur ve hash'ini gösterir. Tur bitince gerçek seed açıklanır.</p>
            <div class="fairness-info">
              <div class="info-row">
                <span>Mevcut Tur Hash:</span>
                <code>{{ currentRound?.server_seed_hash?.slice(0, 32) }}...</code>
              </div>
            </div>
            <p class="small">Kazanan, sunucu seed + client seed kombinasyonuyla hesaplanır.</p>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  Trophy as TrophyIcon,
  Users as UsersIcon,
  Loader2 as Loader2Icon,
  ShieldCheck as ShieldCheckIcon,
  X as XIcon
} from 'lucide-vue-next'

const authStore = useAuthStore()

// State
const currentRound = ref(null)
const players = ref([])
const recentRounds = ref([])
const betAmount = ref(100)
const betting = ref(false)
const isSpinning = ref(false)
const winner = ref(null)
const showFairnessModal = ref(false)
const wheelRotation = ref(0)

// Constants
const minBet = 10
const maxBet = 1000
const houseCut = 5

// Renk paleti
const colors = [
  '#ff6b00', '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316'
]

// Computed
const balance = computed(() => authStore.user?.balance_coin || 0)

const statusText = computed(() => {
  if (!currentRound.value) return 'Yükleniyor...'
  switch (currentRound.value.status) {
    case 'waiting': return 'Bekleniyor'
    case 'active': return 'Aktif'
    case 'spinning': return 'Dönüyor'
    case 'finished': return 'Bitti'
    default: return currentRound.value.status
  }
})

const sortedPlayers = computed(() => {
  return [...players.value].sort((a, b) => b.total_bet - a.total_bet)
})

const canBet = computed(() => {
  return betAmount.value >= minBet &&
         betAmount.value <= maxBet &&
         betAmount.value <= balance.value &&
         currentRound.value?.status !== 'finished' &&
         !isSpinning.value
})

const wheelStyle = computed(() => ({
  transform: `rotate(${wheelRotation.value}deg)`
}))

// Methods
const formatCoin = (amount) => {
  if (!amount) return '0'
  return amount.toLocaleString('tr-TR')
}

const getDefaultAvatar = (username) => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${username}`
}

const getPlayerColor = (index) => {
  return colors[index % colors.length]
}

const getSegmentStyle = (player, index) => {
  const totalAngle = 360
  const playerAngle = (player.win_chance / 100) * totalAngle
  let startAngle = 0

  for (let i = 0; i < index; i++) {
    startAngle += (players.value[i].win_chance / 100) * totalAngle
  }

  return {
    '--start-angle': `${startAngle}deg`,
    '--end-angle': `${startAngle + playerAngle}deg`,
    '--color': getPlayerColor(index),
    transform: `rotate(${startAngle}deg)`
  }
}

const fetchCurrentRound = async () => {
  try {
    const res = await fetch('/api/games/jackpot/current')
    if (res.ok) {
      const data = await res.json()
      currentRound.value = data
      players.value = data.players?.map((p, i) => ({
        ...p,
        color: getPlayerColor(i)
      })) || []

      if (data.winner) {
        winner.value = data.winner
      }
    }
  } catch (e) {
    // Error fetching round data - silently fail
  }
}

const fetchHistory = async () => {
  try {
    const res = await fetch('/api/games/jackpot/history?limit=10')
    if (res.ok) {
      recentRounds.value = await res.json()
    }
  } catch (e) {
    // Error fetching history - silently fail
  }
}

const placeBet = async () => {
  if (!canBet.value) return

  betting.value = true
  try {
    const res = await fetch('/api/games/jackpot/bet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: betAmount.value })
    })

    if (res.ok) {
      const data = await res.json()
      // Refresh round info
      await fetchCurrentRound()
      // Update balance
      authStore.fetchUser()
    } else {
      const error = await res.json()
      alert(error.detail || 'Bahis yapılamadı')
    }
  } catch (e) {
    alert('Bahis yapılırken hata oluştu')
  } finally {
    betting.value = false
  }
}

// Polling for updates
let pollInterval = null

onMounted(() => {
  fetchCurrentRound()
  fetchHistory()

  // Poll every 3 seconds
  pollInterval = setInterval(() => {
    fetchCurrentRound()
  }, 3000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.jackpot-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.jackpot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 800;
  color: var(--primary-color);
}

.title-icon {
  color: var(--primary-color);
}

.round-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.waiting { background: var(--warning-color); color: #000; }
.status-badge.active { background: var(--success-color); color: #fff; }
.status-badge.spinning { background: var(--primary-color); color: #fff; }
.status-badge.finished { background: var(--text-muted); color: #fff; }

.header-stats {
  display: flex;
  gap: 32px;
}

.stat {
  text-align: right;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat.highlight .stat-value {
  color: var(--primary-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Game Container */
.game-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  margin-bottom: 32px;
}

/* Wheel Section */
.wheel-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-height: 400px;
}

.wheel-container {
  position: relative;
  width: 320px;
  height: 320px;
}

.wheel-pointer {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-top: 30px solid var(--primary-color);
  z-index: 10;
  filter: drop-shadow(0 4px 8px rgba(255, 107, 0, 0.4));
}

.wheel {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--bg-tertiary);
  border: 4px solid var(--border-color);
  position: relative;
  transition: transform 5s cubic-bezier(0.17, 0.67, 0.12, 0.99);
  overflow: hidden;
}

.wheel-container.spinning .wheel {
  transition: transform 8s cubic-bezier(0.17, 0.67, 0.12, 0.99);
}

.wheel-segment {
  position: absolute;
  width: 50%;
  height: 50%;
  top: 0;
  left: 50%;
  transform-origin: 0 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.segment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #fff;
}

/* Winner Display */
.winner-display {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 16px;
  z-index: 20;
}

.winner-content {
  text-align: center;
}

.winner-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid var(--primary-color);
  margin-bottom: 16px;
}

.winner-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.winner-label {
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 600;
}

.winner-name {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.winner-amount {
  font-size: 32px;
  font-weight: 800;
  color: var(--success-color);
}

.winner-popup-enter-active,
.winner-popup-leave-active {
  transition: all 0.5s ease;
}

.winner-popup-enter-from,
.winner-popup-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* Players Section */
.players-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.player-count {
  color: var(--text-secondary);
  font-size: 14px;
}

.players-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.player-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  border-left: 4px solid;
}

.player-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.player-info {
  flex: 1;
}

.player-name {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
}

.player-bet {
  font-size: 12px;
  color: var(--text-secondary);
}

.player-chance {
  text-align: right;
  min-width: 80px;
}

.chance-value {
  display: block;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.chance-bar {
  height: 4px;
  border-radius: 2px;
  transition: width 0.3s;
}

.no-players {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.3;
}

.no-players .small {
  font-size: 12px;
  opacity: 0.7;
}

/* Bet Section */
.bet-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 24px;
  margin-bottom: 32px;
}

.bet-form {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.bet-input-group {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.bet-input {
  width: 100%;
  padding: 16px 80px 16px 20px;
  font-size: 18px;
  font-weight: 600;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  outline: none;
}

.bet-input:focus {
  border-color: var(--primary-color);
}

.input-suffix {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-weight: 500;
}

.quick-bets {
  display: flex;
  gap: 8px;
}

.quick-btn {
  padding: 12px 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--bg-primary);
}

.quick-btn.all-in {
  background: var(--danger-color);
  border-color: var(--danger-color);
  color: #fff;
}

.bet-btn {
  padding: 16px 48px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 12px;
  color: var(--bg-primary);
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.bet-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 107, 0, 0.4);
}

.bet-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bet-info {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

/* History Section */
.history-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 24px;
  margin-bottom: 32px;
}

.history-section h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 100px;
  gap: 16px;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  align-items: center;
}

.history-round {
  color: var(--text-secondary);
}

.history-pot {
  font-weight: 600;
  color: var(--text-primary);
}

.history-winner {
  color: var(--text-primary);
}

.history-amount {
  text-align: right;
  font-weight: 700;
}

.text-success {
  color: var(--success-color);
}

/* Fairness Section */
.fairness-section {
  text-align: center;
}

.fairness-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.fairness-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  border: 1px solid var(--border-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.modal-body p {
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.modal-body .small {
  font-size: 12px;
}

.fairness-info {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row span {
  font-size: 12px;
  color: var(--text-secondary);
}

.info-row code {
  font-family: monospace;
  font-size: 11px;
  color: var(--primary-color);
  background: var(--bg-primary);
  padding: 8px;
  border-radius: 4px;
  word-break: break-all;
}

/* Spin Animation */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .game-container {
    grid-template-columns: 1fr;
  }

  .jackpot-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .bet-form {
    flex-direction: column;
  }

  .bet-input-group {
    width: 100%;
  }

  .quick-bets {
    flex-wrap: wrap;
    justify-content: center;
  }

  .history-item {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
}
</style>
