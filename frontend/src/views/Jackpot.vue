<template>
  <div class="jackpot-page">
    <!-- Maintenance Check -->
    <MaintenanceOverlay feature="jackpot" />

    <!-- Animated Background -->
    <div class="animated-bg">
      <div class="bg-glow glow-1"></div>
      <div class="bg-glow glow-2"></div>
      <div class="bg-glow glow-3"></div>
    </div>

    <!-- Header -->
    <div class="jackpot-header">
      <div class="header-left">
        <div class="logo-container">
          <div class="logo-glow"></div>
          <TrophyIcon :size="40" class="logo-icon" />
        </div>
        <div class="title-section">
          <h1 class="title">
            <span class="title-main">JACKPOT</span>
            <span class="title-glow">JACKPOT</span>
          </h1>
          <div class="round-badge">
            <span class="round-text">TUR #{{ currentRound?.round_number || '---' }}</span>
            <span class="status-indicator" :class="currentRound?.status">
              <span class="status-dot"></span>
              {{ statusText }}
            </span>
          </div>
        </div>
      </div>

      <div class="header-stats">
        <div class="stat-card balance-card">
          <div class="stat-icon-wrap">
            <WalletIcon :size="20" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ formatArmor(balance) }}</span>
            <span class="stat-label">Bakiyen</span>
          </div>
        </div>
        <div class="stat-card pot-card">
          <div class="stat-glow"></div>
          <div class="stat-icon-wrap gold">
            <CoinsIcon :size="20" />
          </div>
          <div class="stat-content">
            <span class="stat-value gold">{{ formatArmor(currentRound?.total_pot || 0) }}</span>
            <span class="stat-label">Toplam Havuz</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Game Area -->
    <div class="game-container">
      <!-- Spinner Section - CS:GO Style Horizontal -->
      <div class="spinner-section">
        <!-- Ambient Glow -->
        <div class="spinner-ambient"></div>

        <!-- Countdown Display -->
        <Transition name="countdown-fade">
          <div v-if="countdown > 0" class="countdown-display">
            <div class="countdown-ring">
              <svg viewBox="0 0 100 100">
                <circle class="countdown-track" cx="50" cy="50" r="45" />
                <circle
                  class="countdown-progress"
                  cx="50" cy="50" r="45"
                  :style="{ strokeDashoffset: countdownOffset }"
                />
              </svg>
              <div class="countdown-inner">
                <span class="countdown-number">{{ countdown }}</span>
                <span class="countdown-text">saniye</span>
              </div>
            </div>
            <div class="countdown-pulse"></div>
          </div>
        </Transition>

        <!-- Horizontal Spinner -->
        <div class="spinner-container" :class="{ 'has-winner': winner && !isSpinning }">
          <!-- Winner Line (Ortadaki çizgi) -->
          <div class="winner-line">
            <div class="winner-line-inner"></div>
            <div class="winner-arrow top"></div>
            <div class="winner-arrow bottom"></div>
          </div>

          <!-- Spinner Track -->
          <div class="spinner-track" ref="spinnerTrackRef">
            <div class="track-overlay left"></div>
            <div class="track-overlay right"></div>

            <div
              class="spinner-items"
              ref="spinnerItemsRef"
              :style="spinnerStyle"
              :class="{ spinning: isSpinning }"
            >
              <div
                v-for="(item, index) in spinnerItems"
                :key="index"
                class="spinner-item"
                :style="{ '--player-color': item.color }"
              >
                <div class="item-glow" :style="{ background: item.color }"></div>
                <img
                  :src="getAvatarUrl(item.avatar, item.username)"
                  :alt="`${item.username} avatar`"
                  class="spinner-avatar"
                  loading="lazy"
                  @error="(e) => e.target.src = getDefaultAvatar(item.username)"
                />
                <span class="spinner-name">{{ item.username }}</span>
                <span class="spinner-chance">{{ item.win_chance?.toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Winner Display - EPIC WIN EXPERIENCE -->
        <Teleport to="body">
          <Transition name="winner-popup">
            <div v-if="winner && !isSpinning" class="jackpot-win-overlay" @click="closeWinnerDisplay">
              <div class="jackpot-burst">
                <span v-for="i in 30" :key="i" class="jackpot-burst-particle"
                  :style="{
                    '--tx': `${(Math.random() - 0.5) * 400}px`,
                    '--ty': `${(Math.random() - 0.5) * 400}px`,
                    background: ['#ff6b00', '#ffcc00', '#00ff88', '#00d4ff', '#ff3366'][i % 5],
                    animationDelay: `${i * 0.05}s`
                  }">
                </span>
              </div>
              <div class="jackpot-winner-card">
                <div class="winner-crown-epic">
                  <CrownIcon :size="48" />
                </div>
                <img
                  :src="getAvatarUrl(winner.avatar, winner.username)"
                  :alt="`Kazanan: ${winner.username}`"
                  class="jackpot-winner-avatar"
                  @error="(e) => e.target.src = getDefaultAvatar(winner.username)"
                />
                <div class="jackpot-winner-name">{{ winner.username }}</div>
                <div class="jackpot-prize-amount">{{ formatArmor(winner.amount) }}</div>
                <div class="jackpot-prize-label">ARMOR KAZANDI!</div>
                <button class="winner-close-btn" @click="closeWinnerDisplay">
                  Kapat
                </button>
              </div>
            </div>
          </Transition>
        </Teleport>

        <!-- Pot Display -->
        <div class="pot-display" v-if="!winner && countdown <= 0">
          <div class="pot-container">
            <div class="pot-glow"></div>
            <div class="pot-icon">
              <TrophyIcon :size="32" />
            </div>
            <div class="pot-info">
              <span class="pot-label">TOPLAM HAVUZ</span>
              <span class="pot-amount">{{ formatArmor(currentRound?.total_pot || 0) }}</span>
              <span class="pot-currency">ARMOR</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Players & Bets Section -->
      <div class="players-section">
        <div class="section-header">
          <div class="header-title">
            <UsersIcon :size="20" />
            <h2>Katılımcılar</h2>
          </div>
          <span class="player-count">
            <span class="count-num">{{ players.length }}</span> oyuncu
          </span>
        </div>

        <div class="players-list" v-if="players.length > 0">
          <div
            v-for="(player, index) in sortedPlayers"
            :key="player.user_id"
            class="player-card"
            :style="{ '--player-color': player.color, '--rank': index }"
          >
            <div class="player-rank">#{{ index + 1 }}</div>
            <img :src="getAvatarUrl(player.avatar, player.username)" :alt="`${player.username} avatar`" class="player-avatar" loading="lazy" @error="(e) => e.target.src = getDefaultAvatar(player.username)" />
            <div class="player-info">
              <span class="player-name">{{ player.username }}</span>
              <span class="player-bet">
                <CoinsIcon :size="12" />
                {{ formatArmor(player.total_bet) }}
              </span>
            </div>
            <div class="player-chance">
              <div class="chance-ring">
                <svg viewBox="0 0 36 36">
                  <circle class="chance-track" cx="18" cy="18" r="16" />
                  <circle
                    class="chance-progress"
                    cx="18" cy="18" r="16"
                    :style="{
                      strokeDashoffset: 100 - player.win_chance,
                      stroke: player.color
                    }"
                  />
                </svg>
                <span class="chance-value">{{ player.win_chance.toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="no-players">
          <div class="empty-icon-wrap">
            <UsersIcon :size="48" />
          </div>
          <p class="empty-title">Henüz katılımcı yok</p>
          <p class="empty-subtitle">İlk bahsi sen yap!</p>
        </div>
      </div>
    </div>

    <!-- Bet Section -->
    <div class="bet-section" v-if="!isSpinning && currentRound?.status !== 'finished'">
      <div class="bet-container">
        <div class="bet-header">
          <ZapIcon :size="24" />
          <span>BAHİS YAP</span>
        </div>

        <div class="bet-form">
          <div class="bet-input-group" :class="{ 'bet-input-error': betValidation.hasError, 'bet-input-success': betValidation.isValid }">
            <div class="input-icon">
              <CoinsIcon :size="20" />
            </div>
            <input
              v-model.number="betAmount"
              type="number"
              :min="minBet"
              :max="maxBet"
              placeholder="Bahis miktarı"
              class="bet-input"
              @input="validateBetAmount"
            />
            <span class="input-suffix">ARMOR</span>
          </div>
          <div v-if="betValidation.message" class="bet-validation-message" :class="{ 'bet-validation-error': betValidation.hasError }">
            {{ betValidation.message }}
          </div>

          <div class="quick-bets">
            <button @click="betAmount = 10" class="quick-btn" :class="{ active: betAmount === 10 }">
              <span class="btn-value">10</span>
            </button>
            <button @click="betAmount = 50" class="quick-btn" :class="{ active: betAmount === 50 }">
              <span class="btn-value">50</span>
            </button>
            <button @click="betAmount = 100" class="quick-btn" :class="{ active: betAmount === 100 }">
              <span class="btn-value">100</span>
            </button>
            <button @click="betAmount = 500" class="quick-btn" :class="{ active: betAmount === 500 }">
              <span class="btn-value">500</span>
            </button>
            <button @click="betAmount = balance" class="quick-btn all-in">
              <FlameIcon :size="16" />
              <span class="btn-value">ALL IN</span>
            </button>
          </div>

          <button
            @click="placeBet"
            class="bet-btn"
            :class="{ 'no-steam': !hasSteam }"
            :disabled="!canBet || betting"
          >
            <div class="btn-glow"></div>
            <Loader2Icon v-if="betting" :size="24" class="spin" />
            <template v-else-if="!hasSteam">
              <LockIcon :size="24" />
              <span>Steam Gerekli</span>
            </template>
            <template v-else>
              <RocketIcon :size="24" />
              <span>BAHİS YAP</span>
            </template>
          </button>
        </div>

        <div class="bet-info">
          <div class="info-item">
            <span class="info-label">Min:</span>
            <span class="info-value">{{ minBet }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Max:</span>
            <span class="info-value">{{ maxBet }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Komisyon:</span>
            <span class="info-value">{{ houseCut }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- History Section -->
    <div class="history-section">
      <div class="section-title">
        <HistoryIcon :size="20" />
        <h2>Son Turlar</h2>
      </div>
      <div class="history-grid">
        <div
          v-for="round in recentRounds"
          :key="round.id"
          class="history-card"
        >
          <div class="history-header">
            <span class="history-round">#{{ round.round_number }}</span>
            <span class="history-pot">{{ formatArmor(round.total_pot) }} ₳</span>
          </div>
          <div class="history-winner-row">
            <CrownIcon :size="14" />
            <span class="history-winner">{{ round.winner_username }}</span>
          </div>
          <div class="history-amount">
            +{{ formatArmor(round.winner_amount) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Provably Fair -->
    <div class="fairness-section">
      <button @click="showFairnessModal = true" class="fairness-btn">
        <ShieldCheckIcon :size="20" />
        <span>Provably Fair</span>
        <ChevronRightIcon :size="16" />
      </button>
    </div>

    <!-- Fairness Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showFairnessModal" class="modal-overlay" @click.self="showFairnessModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <div class="modal-title">
                <ShieldCheckIcon :size="24" />
                <h3>Provably Fair Doğrulama</h3>
              </div>
              <button @click="showFairnessModal = false" class="close-btn">
                <XIcon :size="20" />
              </button>
            </div>
            <div class="modal-body">
              <p>Her tur başında sunucu bir seed oluşturur ve hash'ini gösterir. Tur bitince gerçek seed açıklanır.</p>
              <div class="fairness-info">
                <div class="info-row">
                  <span class="info-label">Mevcut Tur Hash:</span>
                  <code>{{ currentRound?.server_seed_hash?.slice(0, 32) }}...</code>
                </div>
              </div>
              <p class="small">Kazanan, sunucu seed + client seed kombinasyonuyla hesaplanır.</p>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Steam Required Modal -->
    <SteamRequiredModal
      :show="showSteamModal"
      @close="closeModal"
      @connect="connectSteam"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { useRequireSteam } from '@/composables/useRequireSteam'
import MaintenanceOverlay from '@/components/MaintenanceOverlay.vue'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import {
  Trophy as TrophyIcon,
  Users as UsersIcon,
  Loader2 as Loader2Icon,
  ShieldCheck as ShieldCheckIcon,
  X as XIcon,
  Wallet as WalletIcon,
  Coins as CoinsIcon,
  Crown as CrownIcon,
  Zap as ZapIcon,
  Flame as FlameIcon,
  Rocket as RocketIcon,
  History as HistoryIcon,
  ChevronRight as ChevronRightIcon,
  Lock as LockIcon
} from 'lucide-vue-next'

const authStore = useAuthStore()
const message = useMessage()
const { hasSteam, showSteamModal, requireSteam, connectSteam, closeModal } = useRequireSteam()

// State
const currentRound = ref(null)
const players = ref([])
const recentRounds = ref([])
const betAmount = ref(100)
const betting = ref(false)

// Bet validation
const betValidation = reactive({ hasError: false, isValid: false, message: '' })
const isSpinning = ref(false)
const winner = ref(null)
const showFairnessModal = ref(false)
const wheelRotation = ref(0)

// WebSocket state
const ws = ref(null)
const wsConnected = ref(false)
const countdown = ref(0)
let reconnectTimeout = null
let heartbeatInterval = null
let isUnmounting = false
let isMounted = false // Track component mount state for async operations
let isReconnecting = false // Prevent reconnect race condition

// Animation frame tracking for cleanup
let animationFrameId = null
let nestedAnimationFrameId = null // Track nested animation frame

// AudioContext singleton for sound effects
let sharedAudioContext = null
const getAudioContext = () => {
  if (!sharedAudioContext) {
    sharedAudioContext = new (window.AudioContext || window.webkitAudioContext)()
  }
  return sharedAudioContext
}

// Constants - defaults, overridden by API
const DEFAULT_MIN_BET = 10
const DEFAULT_MAX_BET = 1000
const DEFAULT_HOUSE_CUT = 5
const COUNTDOWN_MAX = 30

// Dynamic bet limits from API
const minBet = computed(() => currentRound.value?.min_bet || DEFAULT_MIN_BET)
const maxBet = computed(() => currentRound.value?.max_bet || DEFAULT_MAX_BET)
const houseCut = computed(() => currentRound.value?.house_cut || DEFAULT_HOUSE_CUT)

// Renk paleti - Gaming style
const colors = [
  '#ff6b00', '#00d4ff', '#00ff88', '#ffcc00', '#ff3366',
  '#9945ff', '#ff0099', '#00ffcc', '#88ff00', '#ff6600'
]

// Computed
const balance = computed(() => authStore.user?.balance_coin || 0)

const countdownOffset = computed(() => {
  const circumference = 2 * Math.PI * 45
  const progress = countdown.value / COUNTDOWN_MAX
  return circumference * (1 - progress)
})

const statusText = computed(() => {
  if (!currentRound.value) return 'Yükleniyor...'
  if (countdown.value > 0) return `${countdown.value}s`
  if (isSpinning.value) return 'Dönüyor'
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
  return betAmount.value >= minBet.value &&
         betAmount.value <= maxBet.value &&
         betAmount.value <= balance.value &&
         currentRound.value?.status !== 'finished' &&
         !isSpinning.value
})

const wheelStyle = computed(() => ({
  transform: `rotate(${wheelRotation.value}deg)`
}))

// Spinner için ref ve state
const spinnerTrackRef = ref(null)
const spinnerItemsRef = ref(null)
const spinnerOffset = ref(0)
const spinnerItemsList = ref([]) // Sabit spinner items listesi

// Spinner items - rolling başladığında generate edilecek
const spinnerItems = computed(() => {
  // Eğer rolling için özel liste varsa onu kullan
  if (spinnerItemsList.value.length > 0) {
    return spinnerItemsList.value
  }

  // Yoksa oyunculardan oluştur (bekleme ekranı için)
  if (players.value.length === 0) return []

  return generateSpinnerItems(players.value)
})

// Spinner items oluştur
const generateSpinnerItems = (playerList, winnerId = null) => {
  if (!playerList || playerList.length === 0) return []

  const items = []
  const repeatCount = 80

  // Her oyuncuyu kazanma şansına göre tekrarla
  for (let i = 0; i < repeatCount; i++) {
    // Sıralı döngü - ağırlıklı
    const playerIndex = i % playerList.length
    const player = playerList[playerIndex]

    if (player) {
      items.push({
        ...player,
        index: i,
        color: player.color || getPlayerColor(playerIndex)
      })
    }
  }

  // Kazanan varsa, ortaya yakın bir yere yerleştir
  if (winnerId && items.length > 0) {
    const winnerPlayer = playerList.find(p => p.user_id === winnerId)
    if (winnerPlayer) {
      // Ortaya yakın pozisyonlara kazananı ekle
      const centerIndex = Math.floor(items.length * 0.7)
      items[centerIndex] = {
        ...winnerPlayer,
        index: centerIndex,
        color: winnerPlayer.color || getPlayerColor(0)
      }
    }
  }

  return items
}

// Spinner style
const spinnerStyle = computed(() => ({
  transform: `translateX(${spinnerOffset.value}px)`
}))

// Methods
const formatArmor = (amount) => {
  if (!amount) return '0'
  return amount.toLocaleString('tr-TR')
}

const getDefaultAvatar = (username) => {
  // Dicebear ile kullanıcı adından avatar oluştur
  const name = username || 'user'
  return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(name)}&backgroundColor=ff6b00,00d4ff,00ff88,ffcc00,ff3366,9945ff`
}

const getAvatarUrl = (avatar, username) => {
  // Avatar yoksa veya geçersizse varsayılan kullan
  if (!avatar || avatar === '' || avatar === 'null' || avatar === 'undefined') {
    return getDefaultAvatar(username)
  }
  // Tam URL ise direkt kullan
  if (avatar.startsWith('http')) return avatar
  // Göreceli yol ise /static/ ekle
  if (avatar.startsWith('/')) return avatar
  return `/static/${avatar}`
}

const getPlayerColor = (index) => {
  return colors[index % colors.length]
}

const validateBetAmount = () => {
  const amount = betAmount.value
  if (!amount || amount === 0) {
    betValidation.hasError = false
    betValidation.isValid = false
    betValidation.message = ''
  } else if (amount < minBet.value) {
    betValidation.hasError = true
    betValidation.isValid = false
    betValidation.message = `Minimum bahis: ${minBet.value} ARMOR`
  } else if (amount > maxBet.value) {
    betValidation.hasError = true
    betValidation.isValid = false
    betValidation.message = `Maksimum bahis: ${maxBet.value} ARMOR`
  } else if (amount > balance.value) {
    betValidation.hasError = true
    betValidation.isValid = false
    betValidation.message = `Yetersiz bakiye. Mevcut: ${formatArmor(balance.value)} ARMOR`
  } else {
    betValidation.hasError = false
    betValidation.isValid = true
    betValidation.message = ''
  }
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
    } else {
      console.warn('Jackpot round fetch failed:', res.status)
    }
  } catch (e) {
    console.error('Error fetching jackpot round:', e.message)
  }
}

const fetchHistory = async () => {
  try {
    const res = await fetch('/api/games/jackpot/history?limit=10')
    if (res.ok) {
      recentRounds.value = await res.json()
    } else {
      console.warn('Jackpot history fetch failed:', res.status)
    }
  } catch (e) {
    console.error('Error fetching jackpot history:', e.message)
  }
}

// CSRF token helper
const getCsrfToken = () => {
  const match = document.cookie.match(/csrf_token=([^;]+)/)
  return match ? match[1] : ''
}

const placeBet = async () => {
  if (!canBet.value) return

  // Steam hesabi kontrolu
  if (!requireSteam()) return

  betting.value = true
  try {
    const token = localStorage.getItem('access_token')
    const csrfToken = getCsrfToken()
    const res = await fetch('/api/games/jackpot/bet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-CSRF-Token': csrfToken
      },
      body: JSON.stringify({ amount: betAmount.value })
    })

    if (res.ok) {
      const data = await res.json()
      // Refresh round info
      await fetchCurrentRound()
      // Update balance
      authStore.fetchUser().catch(err => {
        console.error('Failed to fetch user after bet:', err)
      })
      message.success('Bahis başarıyla yapıldı')
    } else {
      const error = await res.json()
      message.error(error.detail || 'Bahis yapılamadı')
    }
  } catch (e) {
    message.error('Bahis yapılırken hata oluştu')
  } finally {
    betting.value = false
  }
}

// WebSocket connection
const connectWebSocket = () => {
  // Don't connect if component is unmounting
  if (isUnmounting || !isMounted) return

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws/jackpot`

  ws.value = new WebSocket(wsUrl)

  ws.value.onopen = () => {
    // Check if component is still mounted before sending auth
    if (!isMounted || isUnmounting) return

    wsConnected.value = true

    // Authenticate if logged in
    const token = localStorage.getItem('access_token')
    if (token && ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ action: 'auth', token }))
    }
  }

  ws.value.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data)
      handleWebSocketMessage(message)
    } catch {
      // Parse error - ignore invalid messages
    }
  }

  ws.value.onclose = () => {
    wsConnected.value = false
    // Reconnect after 3 seconds if not unmounting and not already reconnecting
    if (!isUnmounting && !isReconnecting) {
      isReconnecting = true
      reconnectTimeout = setTimeout(() => {
        isReconnecting = false
        if (!isUnmounting) {
          connectWebSocket()
        }
      }, 3000)
    }
  }

  ws.value.onerror = () => {
    // WebSocket error - handled by onclose
  }
}

const handleWebSocketMessage = (message) => {
  switch (message.type) {
    case 'round_info':
      // İlk bağlantıda veya state güncellemesinde
      updateRoundInfo(message.data)
      break

    case 'new_bet':
      // Yeni bahis geldi
      handleNewBet(message.data)
      // Tur bilgisini güncelle
      if (message.data) {
        fetchCurrentRound().catch(err => {
          console.error('Failed to fetch current round after new bet:', err)
        })
      }
      break

    case 'round_update':
      // Tur bilgisi güncellendi
      updateRoundInfo(message.data)

      // countdown_start mesajı gelirse geri sayımı başlat
      if (message.data?.type === 'countdown_start') {
        startCountdown(message.data.countdown || 30)
      }
      // new_round mesajı gelirse temizle
      if (message.data?.new_round) {
        winner.value = null
        isSpinning.value = false
        spinnerOffset.value = 0
        countdown.value = 0
      }
      break

    case 'countdown':
      // Geri sayım - direkt seconds değeri
      countdown.value = message.seconds
      break

    case 'rolling':
      // Çark dönüyor
      startSpinAnimation(message.data)
      break

    case 'winner':
      // Kazanan belirlendi
      showWinner(message.data)
      break

    case 'auth_success':
      // Auth successful
      break

    case 'pong':
    case 'ping':
      // Heartbeat response
      break
  }
}

const updateRoundInfo = (data) => {
  if (!data) return
  currentRound.value = data
  players.value = data.players?.map((p, i) => ({
    ...p,
    color: getPlayerColor(i)
  })) || []

  if (data.winner) {
    winner.value = data.winner
  }

  // Yeni tur başladıysa her şeyi temizle
  if (data.new_round) {
    winner.value = null
    isSpinning.value = false
    wheelRotation.value = 0
    countdown.value = 0
    spinnerOffset.value = 0
    spinnerItemsList.value = [] // Spinner listesini temizle
  }
}

const handleNewBet = () => {
  // Yeni bahis animasyonu - Players listesi round_update ile güncellenecek
}

const startCountdown = (seconds) => {
  // Sadece WebSocket'ten gelen sayıları kullan
  countdown.value = seconds
}

const startSpinAnimation = (data) => {
  isSpinning.value = true
  winner.value = null
  countdown.value = 0

  // Oyuncu listesini al - WebSocket'ten gelen veya mevcut
  const playerList = data.players || players.value

  if (!playerList || playerList.length === 0) {
    isSpinning.value = false
    return
  }

  // Spinner items'ı oluştur - kazananı ortaya yerleştir
  spinnerItemsList.value = generateSpinnerItems(
    playerList.map((p, i) => ({ ...p, color: p.color || getPlayerColor(i) })),
    data.winner_id
  )

  // Item genişliği (CSS ile senkronize)
  const itemWidth = 140 // px

  // Kazananın indexini bul
  const winnerIndex = Math.floor(spinnerItemsList.value.length * 0.7) // Ortaya yakın

  // Hedef pozisyon - kazanan ortada duracak şekilde
  const trackWidth = spinnerTrackRef.value?.offsetWidth || 800
  const centerOffset = trackWidth / 2 - itemWidth / 2

  // Toplam kaydırma miktarı (negatif = sola kaydır)
  const targetOffset = -(winnerIndex * itemWidth) + centerOffset

  // Animasyonu başlat - sağdan başla
  spinnerOffset.value = itemWidth * 10 // Sağdan başla

  // Ses efekti için tick counter
  let lastTickIndex = 0

  // requestAnimationFrame ile smooth animasyon
  const duration = (data.duration || 8) * 1000
  const startTime = Date.now()
  const startOffset = spinnerOffset.value

  const animate = () => {
    // Check if component is unmounting
    if (isUnmounting) {
      animationFrameId = null
      return
    }

    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    // Cubic ease-out - yavaşlayarak dur
    const easeOut = 1 - Math.pow(1 - progress, 4)

    spinnerOffset.value = startOffset + (targetOffset - startOffset) * easeOut

    // Tick ses efekti (her item geçişinde)
    const currentItemIndex = Math.abs(Math.floor(spinnerOffset.value / itemWidth))
    if (currentItemIndex !== lastTickIndex) {
      lastTickIndex = currentItemIndex
      playTickSound()
    }

    if (progress < 1) {
      animationFrameId = requestAnimationFrame(animate)
    } else {
      animationFrameId = null
      isSpinning.value = false
      playWinSound()
    }
  }

  // Bir sonraki frame'de başlat (DOM güncellemesi için bekle)
  animationFrameId = requestAnimationFrame(() => {
    // Check if component is still mounted
    if (isUnmounting) {
      animationFrameId = null
      return
    }
    nestedAnimationFrameId = requestAnimationFrame(animate)
  })
}

// Ses efektleri - using shared AudioContext singleton
const playTickSound = () => {
  // Basit tick sesi
  try {
    const audioContext = getAudioContext()
    if (audioContext.state === 'suspended') {
      audioContext.resume()
    }
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    oscillator.frequency.value = 800
    oscillator.type = 'sine'
    gainNode.gain.value = 0.1

    oscillator.start()
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.05)
    oscillator.stop(audioContext.currentTime + 0.05)
  } catch (e) {
    // Ses çalamazsa sessizce devam et
  }
}

const playWinSound = () => {
  // Kazanma sesi
  try {
    const audioContext = getAudioContext()
    if (audioContext.state === 'suspended') {
      audioContext.resume()
    }
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    oscillator.frequency.value = 523.25 // C5
    oscillator.type = 'sine'
    gainNode.gain.value = 0.3

    oscillator.start()

    // Melodi
    setTimeout(() => oscillator.frequency.value = 659.25, 100) // E5
    setTimeout(() => oscillator.frequency.value = 783.99, 200) // G5

    gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.5)
    oscillator.stop(audioContext.currentTime + 0.5)
  } catch (e) {
    // Ses çalamazsa sessizce devam et
  }
}

const calculateWinnerAngle = (winnerIndex) => {
  let angle = 0
  for (let i = 0; i < winnerIndex; i++) {
    angle += (players.value[i]?.win_chance || 0) / 100 * 360
  }
  // Segment'in ortasına gel
  angle += (players.value[winnerIndex]?.win_chance || 0) / 100 * 180
  return angle
}

const showWinner = (data) => {
  winner.value = {
    user_id: data.winner_id,
    username: data.winner_username,
    amount: data.winner_amount,
    avatar: players.value.find(p => p.user_id === data.winner_id)?.avatar
  }

  // Epic win ses efekti
  playWinSound()

  // History'yi güncelle
  fetchHistory().catch(err => {
    console.error('Failed to fetch history after winner:', err)
  })

  // Bakiye güncelle
  authStore.fetchUser().catch(err => {
    console.error('Failed to fetch user after winner:', err)
  })
}

const closeWinnerDisplay = () => {
  winner.value = null
}

// Heartbeat gönder
const startHeartbeat = () => {
  heartbeatInterval = setInterval(() => {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ action: 'ping' }))
    }
  }, 30000)
}

onMounted(() => {
  isMounted = true

  // İlk veri yükle with error handling
  fetchCurrentRound().catch(err => {
    console.error('Failed to fetch current round on mount:', err)
  })
  fetchHistory().catch(err => {
    console.error('Failed to fetch history on mount:', err)
  })

  // WebSocket bağlan
  connectWebSocket()
  startHeartbeat()
})

onUnmounted(() => {
  isUnmounting = true
  isMounted = false

  // Cancel any pending animation frames
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }

  // Cancel nested animation frame
  if (nestedAnimationFrameId) {
    cancelAnimationFrame(nestedAnimationFrameId)
    nestedAnimationFrameId = null
  }

  // Heartbeat interval temizle
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }

  // Reconnect timeout temizle
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout)
    reconnectTimeout = null
  }

  // Reset reconnecting state
  isReconnecting = false

  // WebSocket kapat
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }

  // Close shared AudioContext to free resources - check state before closing
  if (sharedAudioContext && sharedAudioContext.state !== 'closed') {
    sharedAudioContext.close().catch(err => {
      // Only log if it's not an expected close error
      if (err.name !== 'InvalidStateError') {
        console.error('Failed to close AudioContext:', err)
      }
    })
    sharedAudioContext = null
  }
})
</script>

<style scoped>
.jackpot-page {
  padding: 16px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  min-height: 100vh;
}

/* Animated Background */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.15;
  animation: float 20s ease-in-out infinite;
}

.glow-1 {
  width: 600px;
  height: 600px;
  background: #ff6b00;
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}

.glow-2 {
  width: 500px;
  height: 500px;
  background: #9945ff;
  bottom: -100px;
  left: -100px;
  animation-delay: -7s;
}

.glow-3 {
  width: 400px;
  height: 400px;
  background: #00d4ff;
  top: 50%;
  left: 50%;
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(-30px, 30px) scale(0.9); }
  75% { transform: translate(-50px, -30px) scale(1.05); }
}

/* Header */
.jackpot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(20, 20, 30, 0.9) 0%, rgba(30, 30, 45, 0.9) 100%);
  border-radius: 20px;
  border: 1px solid rgba(255, 107, 0, 0.2);
  box-shadow: 0 0 40px rgba(255, 107, 0, 0.1);
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-container {
  position: relative;
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(255, 107, 0, 0.4) 0%, transparent 70%);
  animation: pulse 2s ease-in-out infinite;
}

.logo-icon {
  color: #ff6b00;
  filter: drop-shadow(0 0 10px rgba(255, 107, 0, 0.5));
  z-index: 1;
}

.title {
  position: relative;
  margin: 0;
}

.title-main {
  display: block;
  font-size: 42px;
  font-weight: 900;
  background: linear-gradient(135deg, #ff6b00 0%, #ffcc00 50%, #ff6b00 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 4px;
  text-shadow: none;
}

.title-glow {
  position: absolute;
  top: 0;
  left: 0;
  font-size: 42px;
  font-weight: 900;
  color: #ff6b00;
  letter-spacing: 4px;
  filter: blur(20px);
  opacity: 0.5;
  z-index: -1;
}

.round-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.round-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-indicator.waiting {
  background: rgba(255, 200, 0, 0.2);
  color: #ffc800;
  border: 1px solid rgba(255, 200, 0, 0.3);
}

.status-indicator.active {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.status-indicator.spinning {
  background: rgba(255, 107, 0, 0.2);
  color: #ff6b00;
  border: 1px solid rgba(255, 107, 0, 0.3);
}

.status-indicator.finished {
  background: rgba(100, 100, 100, 0.2);
  color: #888;
  border: 1px solid rgba(100, 100, 100, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.header-stats {
  display: flex;
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.stat-card.pot-card {
  border-color: rgba(255, 107, 0, 0.3);
}

.stat-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(255, 107, 0, 0.1) 0%, transparent 70%);
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.stat-icon-wrap.gold {
  background: rgba(255, 107, 0, 0.2);
  color: #ff6b00;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #fff;
}

.stat-value.gold {
  background: linear-gradient(135deg, #ff6b00 0%, #ffcc00 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Game Container */
.game-container {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

/* Spinner Section */
.spinner-section {
  background: linear-gradient(135deg, rgba(20, 20, 30, 0.95) 0%, rgba(30, 30, 45, 0.95) 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 107, 0, 0.2);
  padding: 32px;
  position: relative;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.spinner-ambient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center top, rgba(255, 107, 0, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

/* Countdown */
.countdown-display {
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.countdown-ring {
  position: relative;
  width: 100px;
  height: 100px;
}

.countdown-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.countdown-track {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 4;
}

.countdown-progress {
  fill: none;
  stroke: #ff6b00;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s linear;
  filter: drop-shadow(0 0 8px rgba(255, 107, 0, 0.5));
}

.countdown-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.countdown-number {
  font-size: 36px;
  font-weight: 900;
  color: #ff6b00;
  line-height: 1;
  text-shadow: 0 0 20px rgba(255, 107, 0, 0.5);
}

.countdown-text {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.countdown-pulse {
  position: absolute;
  inset: -10px;
  border: 2px solid rgba(255, 107, 0, 0.3);
  border-radius: 50%;
  animation: countdown-pulse 1s ease-out infinite;
}

@keyframes countdown-pulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.countdown-fade-enter-active,
.countdown-fade-leave-active {
  transition: all 0.5s ease;
}

.countdown-fade-enter-from,
.countdown-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) scale(0.8);
}

/* Spinner Container */
.spinner-container {
  width: 100%;
  position: relative;
  padding: 30px 0;
  margin-top: 60px;
}

.spinner-container.has-winner {
  opacity: 0.3;
}

/* Winner Line */
.winner-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 6px;
  transform: translateX(-50%);
  z-index: 10;
}

.winner-line-inner {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, #ff6b00 20%, #ff6b00 80%, transparent 100%);
  box-shadow: 0 0 30px rgba(255, 107, 0, 0.8), 0 0 60px rgba(255, 107, 0, 0.4);
}

.winner-arrow {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 16px solid transparent;
  border-right: 16px solid transparent;
}

.winner-arrow.top {
  top: 0;
  border-top: 20px solid #ff6b00;
  filter: drop-shadow(0 0 10px rgba(255, 107, 0, 0.8));
}

.winner-arrow.bottom {
  bottom: 0;
  border-bottom: 20px solid #ff6b00;
  filter: drop-shadow(0 0 10px rgba(255, 107, 0, 0.8));
}

/* Spinner Track */
.spinner-track {
  width: 100%;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 16px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  position: relative;
  box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.5);
}

.track-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 120px;
  z-index: 5;
  pointer-events: none;
}

.track-overlay.left {
  left: 0;
  background: linear-gradient(to right, rgba(20, 20, 30, 1), transparent);
}

.track-overlay.right {
  right: 0;
  background: linear-gradient(to left, rgba(20, 20, 30, 1), transparent);
}

/* Spinner Items */
.spinner-items {
  display: flex;
  padding: 16px 0;
  will-change: transform;
}

.spinner-item {
  flex-shrink: 0;
  width: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 12px;
  position: relative;
  border-left: 4px solid var(--player-color);
  background: linear-gradient(180deg, rgba(var(--player-color), 0.1) 0%, transparent 100%);
}

.item-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  filter: blur(4px);
  opacity: 0.6;
}

.spinner-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  border: 3px solid var(--player-color);
  background: rgba(0, 0, 0, 0.5);
  object-fit: cover;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.spinner-name {
  margin-top: 10px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  text-align: center;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.spinner-chance {
  font-size: 11px;
  font-weight: 600;
  color: var(--player-color);
  margin-top: 4px;
}

/* Pot Display */
.pot-display {
  margin-top: 32px;
}

.pot-container {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 40px;
  background: linear-gradient(135deg, rgba(255, 107, 0, 0.1) 0%, rgba(255, 200, 0, 0.05) 100%);
  border-radius: 20px;
  border: 2px solid rgba(255, 107, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.pot-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(255, 107, 0, 0.2) 0%, transparent 70%);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.pot-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 107, 0, 0.2);
  border-radius: 16px;
  color: #ff6b00;
}

.pot-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pot-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.pot-amount {
  font-size: 40px;
  font-weight: 900;
  background: linear-gradient(135deg, #ff6b00 0%, #ffcc00 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.pot-currency {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  letter-spacing: 2px;
}

/* Winner Display */
.winner-display {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.95);
  border-radius: 24px;
  z-index: 20;
}

.winner-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #ff6b00;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  animation: particle-burst 2s ease-out infinite;
  animation-delay: var(--delay);
}

@keyframes particle-burst {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
  }
  100% {
    transform: translate(calc(-50% + var(--tx, 100px)), calc(-50% + var(--ty, -100px))) scale(1);
    opacity: 0;
  }
}

.particle:nth-child(1) { --tx: 150px; --ty: -80px; }
.particle:nth-child(2) { --tx: -120px; --ty: -100px; }
.particle:nth-child(3) { --tx: 80px; --ty: 120px; }
.particle:nth-child(4) { --tx: -150px; --ty: 60px; }
.particle:nth-child(5) { --tx: 100px; --ty: -150px; }
.particle:nth-child(6) { --tx: -80px; --ty: 140px; }
.particle:nth-child(7) { --tx: 180px; --ty: 40px; }
.particle:nth-child(8) { --tx: -160px; --ty: -60px; }
.particle:nth-child(9) { --tx: 60px; --ty: 160px; }
.particle:nth-child(10) { --tx: -100px; --ty: -140px; }
.particle:nth-child(11) { --tx: 140px; --ty: 100px; }
.particle:nth-child(12) { --tx: -180px; --ty: 20px; }
.particle:nth-child(13) { --tx: 120px; --ty: -120px; }
.particle:nth-child(14) { --tx: -60px; --ty: 180px; }
.particle:nth-child(15) { --tx: 200px; --ty: -20px; }
.particle:nth-child(16) { --tx: -140px; --ty: -120px; }
.particle:nth-child(17) { --tx: 40px; --ty: 200px; }
.particle:nth-child(18) { --tx: -200px; --ty: 80px; }
.particle:nth-child(19) { --tx: 160px; --ty: 140px; }
.particle:nth-child(20) { --tx: -40px; --ty: -180px; }

.winner-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.winner-crown {
  color: #ffcc00;
  margin-bottom: 16px;
  animation: bounce 1s ease-in-out infinite;
  filter: drop-shadow(0 0 15px rgba(255, 200, 0, 0.5));
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.winner-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #ff6b00;
  margin-bottom: 20px;
  box-shadow: 0 0 40px rgba(255, 107, 0, 0.5);
  animation: winner-glow 2s ease-in-out infinite;
}

@keyframes winner-glow {
  0%, 100% { box-shadow: 0 0 40px rgba(255, 107, 0, 0.5); }
  50% { box-shadow: 0 0 60px rgba(255, 107, 0, 0.8); }
}

.winner-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.winner-label {
  font-size: 16px;
  color: #ffcc00;
  font-weight: 800;
  letter-spacing: 4px;
  text-shadow: 0 0 20px rgba(255, 200, 0, 0.5);
}

.winner-name {
  font-size: 32px;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

.winner-amount {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 28px;
  font-weight: 800;
  color: #00ff88;
  text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
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
  background: linear-gradient(135deg, rgba(20, 20, 30, 0.95) 0%, rgba(30, 30, 45, 0.95) 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 24px;
  backdrop-filter: blur(10px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.7);
}

.header-title h2 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.player-count {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.count-num {
  color: #ff6b00;
  font-weight: 700;
}

.players-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 340px;
  overflow-y: auto;
  padding-right: 8px;
}

.players-list::-webkit-scrollbar {
  width: 6px;
}

.players-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.players-list::-webkit-scrollbar-thumb {
  background: rgba(255, 107, 0, 0.3);
  border-radius: 3px;
}

.player-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.player-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--player-color);
  box-shadow: 0 0 10px var(--player-color);
}

.player-card:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
  border-color: var(--player-color);
  transform: translateX(4px);
}

.player-rank {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.3);
  min-width: 28px;
}

.player-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid var(--player-color);
  object-fit: cover;
}

.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  display: block;
  font-weight: 700;
  color: #fff;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.player-bet {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 2px;
}

.player-bet svg {
  color: #ffcc00;
}

.player-chance {
  flex-shrink: 0;
}

.chance-ring {
  position: relative;
  width: 48px;
  height: 48px;
}

.chance-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.chance-track {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 3;
}

.chance-progress {
  fill: none;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 100;
  transition: stroke-dashoffset 0.5s ease;
}

.chance-value {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  color: var(--player-color);
}

.no-players {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon-wrap {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.2);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 8px;
}

.empty-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.3);
  margin: 0;
}

/* Bet Section */
.bet-section {
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.bet-container {
  background: linear-gradient(135deg, rgba(20, 20, 30, 0.95) 0%, rgba(30, 30, 45, 0.95) 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 107, 0, 0.2);
  padding: 28px;
  backdrop-filter: blur(10px);
}

.bet-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  color: #ff6b00;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 2px;
}

.bet-form {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.bet-input-group {
  position: relative;
  flex: 1;
  min-width: 220px;
}

.input-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #ffcc00;
  z-index: 1;
}

.bet-input {
  width: 100%;
  padding: 18px 90px 18px 52px;
  font-size: 20px;
  font-weight: 700;
  background: rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: #fff;
  outline: none;
  transition: all 0.3s ease;
}

.bet-input:focus {
  border-color: #ff6b00;
  box-shadow: 0 0 20px rgba(255, 107, 0, 0.2);
}

.bet-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.input-suffix {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.4);
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 1px;
}

.quick-bets {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 14px 22px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.quick-btn:hover {
  background: rgba(255, 107, 0, 0.1);
  border-color: rgba(255, 107, 0, 0.3);
  color: #ff6b00;
  transform: translateY(-2px);
}

.quick-btn.active {
  background: rgba(255, 107, 0, 0.2);
  border-color: #ff6b00;
  color: #ff6b00;
}

.quick-btn.all-in {
  background: linear-gradient(135deg, rgba(255, 51, 102, 0.2) 0%, rgba(255, 51, 102, 0.1) 100%);
  border-color: rgba(255, 51, 102, 0.4);
  color: #ff3366;
}

.quick-btn.all-in:hover {
  background: linear-gradient(135deg, rgba(255, 51, 102, 0.3) 0%, rgba(255, 51, 102, 0.2) 100%);
  border-color: #ff3366;
  box-shadow: 0 0 20px rgba(255, 51, 102, 0.3);
}

.bet-btn {
  position: relative;
  padding: 18px 48px;
  background: linear-gradient(135deg, #ff6b00 0%, #ff9500 100%);
  border: none;
  border-radius: 16px;
  color: #000;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.btn-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.bet-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 40px rgba(255, 107, 0, 0.4);
}

.bet-btn:hover:not(:disabled) .btn-glow {
  opacity: 1;
}

.bet-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.bet-btn.no-steam {
  background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
  border: 2px solid #66c0f4;
}

.bet-btn.no-steam:hover:not(:disabled) {
  background: linear-gradient(135deg, #1b2838 0%, #2a475e 100%);
  box-shadow: 0 10px 40px rgba(102, 192, 244, 0.3);
}

.bet-info {
  display: flex;
  gap: 32px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.info-value {
  font-size: 14px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.7);
}

/* History Section */
.history-section {
  background: linear-gradient(135deg, rgba(20, 20, 30, 0.95) 0%, rgba(30, 30, 45, 0.95) 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 28px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  color: rgba(255, 255, 255, 0.7);
}

.section-title h2 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.history-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 18px;
  transition: all 0.3s ease;
}

.history-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 107, 0, 0.2);
  transform: translateY(-2px);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-round {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.history-pot {
  font-size: 14px;
  font-weight: 700;
  color: #ffcc00;
}

.history-winner-row {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #ff6b00;
  margin-bottom: 8px;
}

.history-winner {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.history-amount {
  font-size: 18px;
  font-weight: 800;
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

/* Fairness Section */
.fairness-section {
  text-align: center;
  position: relative;
  z-index: 1;
}

.fairness-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.fairness-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.3);
  color: #00d4ff;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: linear-gradient(135deg, rgba(30, 30, 45, 0.98) 0%, rgba(20, 20, 30, 0.98) 100%);
  border-radius: 24px;
  width: 90%;
  max-width: 500px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #00d4ff;
}

.modal-title h3 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.close-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.modal-body {
  padding: 28px;
}

.modal-body p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 20px;
  line-height: 1.6;
}

.modal-body .small {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.fairness-info {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row .info-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.info-row code {
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  color: #00d4ff;
  background: rgba(0, 212, 255, 0.1);
  padding: 12px;
  border-radius: 8px;
  word-break: break-all;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-content,
.modal-fade-leave-to .modal-content {
  transform: scale(0.95) translateY(20px);
}

/* Spin Animation */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Epic Winner Crown */
.winner-crown-epic {
  color: #ffcc00;
  margin-bottom: 20px;
  animation: crownBounce 1s ease-in-out infinite;
  filter: drop-shadow(0 0 20px rgba(255, 200, 0, 0.6));
}

@keyframes crownBounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-10px) scale(1.1); }
}

/* Winner Close Button */
.winner-close-btn {
  margin-top: 32px;
  padding: 14px 48px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.winner-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.05);
}

/* Responsive */
@media (max-width: 1024px) {
  .game-container {
    grid-template-columns: 1fr;
  }

  .jackpot-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .header-left {
    flex-direction: column;
  }

  .header-stats {
    width: 100%;
    justify-content: center;
  }

  .bet-form {
    flex-direction: column;
    align-items: stretch;
  }

  .bet-input-group {
    width: 100%;
  }

  .quick-bets {
    justify-content: center;
  }

  .bet-btn {
    width: 100%;
    justify-content: center;
  }

  .bet-info {
    justify-content: center;
    flex-wrap: wrap;
  }

  .history-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .jackpot-page {
    padding: 16px;
  }

  .title-main,
  .title-glow {
    font-size: 28px;
  }

  .stat-card {
    padding: 12px 16px;
  }

  .stat-value {
    font-size: 18px;
  }

  .pot-amount {
    font-size: 28px;
  }

  .history-grid {
    grid-template-columns: 1fr;
  }

  .quick-btn {
    padding: 12px 16px;
  }
}

/* Bet Validation Styles */
.bet-input-error .bet-input {
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2) !important;
}

.bet-input-success .bet-input {
  border-color: #22c55e !important;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2) !important;
}

.bet-validation-message {
  font-size: 12px;
  margin-top: 8px;
  padding: 6px 12px;
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border-radius: 6px;
  text-align: center;
}

.bet-validation-error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
</style>
