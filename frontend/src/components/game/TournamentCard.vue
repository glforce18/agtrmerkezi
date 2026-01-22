<template>
  <div class="tournament-card" :class="[tournament.status]">
    <!-- Banner Image -->
    <div class="tournament-banner">
      <img
        v-if="tournament.banner_url"
        :src="tournament.banner_url"
        :alt="tournament.name"
        class="banner-image"
      />
      <div v-else class="banner-placeholder">
        <Trophy class="w-12 h-12" />
      </div>

      <!-- Status Badge -->
      <div
        class="status-badge"
        :style="{ background: tournamentsStore.getStatusColor(tournament.status) }"
      >
        {{ tournamentsStore.getStatusLabel(tournament.status) }}
      </div>

      <!-- Game Badge -->
      <div class="game-badge">
        <Gamepad2 class="w-3 h-3" />
        {{ tournamentsStore.getGameLabel(tournament.game_type) }}
      </div>
    </div>

    <!-- Content -->
    <div class="tournament-content">
      <h3 class="tournament-name">{{ tournament.name }}</h3>

      <p v-if="tournament.description" class="tournament-description">
        {{ truncatedDescription }}
      </p>

      <!-- Info Grid -->
      <div class="info-grid">
        <div class="info-item">
          <Calendar class="w-4 h-4" />
          <span>{{ formatDate(tournament.start_date) }}</span>
        </div>
        <div class="info-item">
          <Users class="w-4 h-4" />
          <span>{{ tournament.participants_count || 0 }} / {{ tournament.max_participants }}</span>
        </div>
        <div class="info-item">
          <Swords class="w-4 h-4" />
          <span>{{ tournamentsStore.getFormatLabel(tournament.format) }}</span>
        </div>
        <div class="info-item" v-if="tournament.prize_pool">
          <Award class="w-4 h-4" />
          <span>{{ formatPrize(tournament.prize_pool) }}</span>
        </div>
      </div>

      <!-- Prize Pool Highlight -->
      <div v-if="tournament.prize_pool && tournament.prize_pool > 0" class="prize-highlight">
        <span class="prize-label">Ödül Havuzu</span>
        <span class="prize-amount">{{ formatPrize(tournament.prize_pool) }}</span>
      </div>
    </div>

    <!-- Footer -->
    <div class="tournament-footer">
      <div class="footer-left">
        <!-- Registration Progress -->
        <div v-if="isRegistrationOpen" class="registration-progress">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: registrationPercent + '%' }"
            ></div>
          </div>
          <span class="progress-text">{{ registrationText }}</span>
        </div>

        <!-- Countdown -->
        <div v-else-if="hasCountdown" class="countdown">
          <Clock class="w-4 h-4" />
          <span>{{ countdownText }}</span>
        </div>
      </div>

      <div class="footer-right">
        <n-button
          v-if="canRegister && hasSteam"
          type="primary"
          size="small"
          @click.stop="handleRegister"
          :loading="registering"
        >
          <template #icon><UserPlus class="w-4 h-4" /></template>
          Katıl
        </n-button>

        <n-button
          v-else-if="canRegister && !hasSteam"
          size="small"
          class="steam-required-btn"
          @click.stop="handleRegister"
        >
          <template #icon><Lock class="w-4 h-4" /></template>
          Steam Gerekli
        </n-button>

        <n-button
          v-else-if="tournament.is_registered"
          size="small"
          @click.stop="handleUnregister"
          :loading="registering"
        >
          <template #icon><Check class="w-4 h-4" /></template>
          Kayıtlı
        </n-button>

        <router-link
          :to="`/tournaments/${tournament.id}`"
          class="view-btn"
          @click.stop
        >
          Detaylar
          <ChevronRight class="w-4 h-4" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import {
  Trophy,
  Calendar,
  Users,
  Swords,
  Award,
  Clock,
  UserPlus,
  Check,
  ChevronRight,
  Gamepad2,
  Lock
} from 'lucide-vue-next'
import { useTournamentsStore, TournamentStatus } from '@/stores/tournaments'
import { useRequireSteam } from '@/composables/useRequireSteam'

const props = defineProps({
  tournament: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['register', 'unregister'])

const message = useMessage()
const tournamentsStore = useTournamentsStore()
const { hasSteam, requireSteam } = useRequireSteam()

const registering = ref(false)

// Computed
const truncatedDescription = computed(() => {
  if (!props.tournament.description) return ''
  return props.tournament.description.length > 100
    ? props.tournament.description.substring(0, 100) + '...'
    : props.tournament.description
})

const isRegistrationOpen = computed(() => {
  return props.tournament.status === TournamentStatus.REGISTRATION
})

const canRegister = computed(() => {
  return isRegistrationOpen.value &&
         !props.tournament.is_registered &&
         (props.tournament.participants_count || 0) < props.tournament.max_participants
})

const registrationPercent = computed(() => {
  if (!props.tournament.max_participants) return 0
  return Math.min(100, Math.round(
    ((props.tournament.participants_count || 0) / props.tournament.max_participants) * 100
  ))
})

const registrationText = computed(() => {
  const remaining = props.tournament.max_participants - (props.tournament.participants_count || 0)
  return `${remaining} kişilik yer kaldı`
})

const hasCountdown = computed(() => {
  return props.tournament.status === TournamentStatus.UPCOMING &&
         props.tournament.start_date
})

const countdownText = computed(() => {
  if (!props.tournament.start_date) return ''

  const start = new Date(props.tournament.start_date)
  const now = new Date()
  const diff = start - now

  if (diff <= 0) return 'Başladı'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  if (days > 0) return `${days} gün ${hours} saat`
  if (hours > 0) return `${hours} saat`

  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  return `${minutes} dakika`
})

// Methods
const formatDate = (dateStr) => {
  if (!dateStr) return 'TBA'
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPrize = (amount) => {
  if (!amount) return ''
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 0
  }).format(amount)
}

const handleRegister = async () => {
  // Steam hesabi kontrolu
  if (!requireSteam()) return

  registering.value = true
  const result = await tournamentsStore.registerForTournament(props.tournament.id)
  registering.value = false

  if (result.success) {
    message.success(result.message)
    emit('register', props.tournament)
  } else {
    message.error(result.message)
  }
}

const handleUnregister = async () => {
  registering.value = true
  const result = await tournamentsStore.unregisterFromTournament(props.tournament.id)
  registering.value = false

  if (result.success) {
    message.success(result.message)
    emit('unregister', props.tournament)
  } else {
    message.error(result.message)
  }
}
</script>

<style scoped>
.tournament-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.tournament-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

/* Status-specific borders */
.tournament-card.registration {
  border-color: rgba(34, 197, 94, 0.3);
}

.tournament-card.in_progress {
  border-color: rgba(249, 115, 22, 0.3);
}

.tournament-banner {
  position: relative;
  height: 140px;
  overflow: hidden;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
}

.game-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  border-radius: 6px;
  font-size: 11px;
  color: white;
}

.tournament-content {
  padding: 16px;
}

.tournament-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.tournament-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.info-item svg {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.prize-highlight {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(234, 88, 12, 0.05) 100%);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 10px;
}

.prize-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.prize-amount {
  font-size: 18px;
  font-weight: 700;
  color: #f97316;
}

.tournament-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
}

.footer-left {
  flex: 1;
}

.registration-progress {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-bar {
  width: 100px;
  height: 4px;
  background: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #16a34a);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 11px;
  color: var(--text-tertiary);
}

.countdown {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #f97316;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.view-btn:hover {
  color: #f97316;
}

.steam-required-btn {
  background: linear-gradient(135deg, #1b2838, #2a475e) !important;
  border-color: #66c0f4 !important;
  color: #66c0f4 !important;
}

.steam-required-btn:hover {
  background: #66c0f4 !important;
  color: #1b2838 !important;
}
</style>
