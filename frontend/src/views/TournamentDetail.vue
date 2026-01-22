<template>
  <div class="tournament-detail-page">
    <div class="container-main">
      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <n-spin size="large" />
        <span>Turnuva yükleniyor...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <AlertTriangle class="w-16 h-16 text-red-500" />
        <h2>Turnuva Bulunamadı</h2>
        <p>{{ error }}</p>
        <router-link to="/tournaments" class="back-btn">
          <ArrowLeft class="w-4 h-4" />
          Turnuvalara Dön
        </router-link>
      </div>

      <!-- Tournament Content -->
      <template v-else-if="tournament">
        <!-- Header Banner -->
        <div class="tournament-banner">
          <img
            v-if="tournament.banner_url"
            :src="tournament.banner_url"
            :alt="tournament.name"
            class="banner-image"
          />
          <div v-else class="banner-placeholder">
            <Trophy class="w-24 h-24" />
          </div>

          <div class="banner-overlay">
            <!-- Back Button -->
            <router-link to="/tournaments" class="back-link">
              <ArrowLeft class="w-4 h-4" />
              Turnuvalara Dön
            </router-link>

            <!-- Status Badge -->
            <div
              class="status-badge"
              :style="{ background: tournamentsStore.getStatusColor(tournament.status) }"
            >
              {{ tournamentsStore.getStatusLabel(tournament.status) }}
            </div>

            <h1 class="tournament-title">{{ tournament.name }}</h1>

            <div class="tournament-meta">
              <span><Gamepad2 class="w-4 h-4" /> {{ tournamentsStore.getGameLabel(tournament.game_type) }}</span>
              <span><Swords class="w-4 h-4" /> {{ tournamentsStore.getFormatLabel(tournament.format) }}</span>
              <span><Calendar class="w-4 h-4" /> {{ formatDate(tournament.start_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Info Cards -->
        <div class="info-cards">
          <div class="info-card">
            <Users class="card-icon" />
            <div class="card-content">
              <span class="card-value">{{ tournament.participants_count || 0 }} / {{ tournament.max_participants }}</span>
              <span class="card-label">Katılımcı</span>
            </div>
            <div class="card-progress">
              <div
                class="progress-fill"
                :style="{ width: participantPercent + '%' }"
              ></div>
            </div>
          </div>

          <div class="info-card" v-if="tournament.prize_pool">
            <Award class="card-icon gold" />
            <div class="card-content">
              <span class="card-value gold">{{ formatPrize(tournament.prize_pool) }}</span>
              <span class="card-label">Ödül Havuzu</span>
            </div>
          </div>

          <div class="info-card">
            <Clock class="card-icon" />
            <div class="card-content">
              <span class="card-value">{{ countdownText }}</span>
              <span class="card-label">{{ countdownLabel }}</span>
            </div>
          </div>

          <div class="info-card">
            <MapPin class="card-icon" />
            <div class="card-content">
              <span class="card-value">{{ tournament.region || 'Türkiye' }}</span>
              <span class="card-label">Bölge</span>
            </div>
          </div>
        </div>

        <!-- Registration / Action Section -->
        <div class="action-section" v-if="canShowActions">
          <div class="action-content">
            <template v-if="tournament.status === 'registration'">
              <div class="registration-info">
                <h3>Kayıt Açık!</h3>
                <p>Turnuvaya katılmak için hemen kaydol.</p>
                <div class="registration-deadline" v-if="tournament.registration_deadline">
                  <Clock class="w-4 h-4" />
                  Son kayıt: {{ formatDate(tournament.registration_deadline) }}
                </div>
              </div>
            </template>

            <template v-else-if="tournament.status === 'in_progress'">
              <div class="live-info">
                <span class="live-badge">
                  <Zap class="w-4 h-4" />
                  CANLI
                </span>
                <p>Turnuva şu anda devam ediyor!</p>
              </div>
            </template>
          </div>

          <div class="action-buttons">
            <n-button
              v-if="canRegister"
              type="primary"
              size="large"
              @click="handleRegister"
              :loading="registering"
            >
              <template #icon><UserPlus class="w-5 h-5" /></template>
              Turnuvaya Katıl
            </n-button>

            <n-button
              v-else-if="tournament.is_registered && tournament.status === 'registration'"
              size="large"
              @click="handleUnregister"
              :loading="registering"
            >
              <template #icon><UserMinus class="w-5 h-5" /></template>
              Kaydı İptal Et
            </n-button>

            <n-button
              v-if="tournament.is_registered"
              type="primary"
              size="large"
              disabled
            >
              <template #icon><Check class="w-5 h-5" /></template>
              Kayıtlısın
            </n-button>

            <n-button
              v-if="tournament.stream_url && tournament.status === 'in_progress'"
              tag="a"
              :href="tournament.stream_url"
              target="_blank"
              size="large"
            >
              <template #icon><Play class="w-5 h-5" /></template>
              Canlı İzle
            </n-button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tournament-tabs">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'info' }"
            @click="activeTab = 'info'"
          >
            <Info class="w-4 h-4" />
            Bilgiler
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'bracket' }"
            @click="activeTab = 'bracket'"
          >
            <GitBranch class="w-4 h-4" />
            Bracket
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'participants' }"
            @click="activeTab = 'participants'"
          >
            <Users class="w-4 h-4" />
            Katılımcılar
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'prizes' }"
            @click="activeTab = 'prizes'"
          >
            <Award class="w-4 h-4" />
            Ödüller
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'rules' }"
            @click="activeTab = 'rules'"
          >
            <FileText class="w-4 h-4" />
            Kurallar
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          <!-- Info Tab -->
          <div v-if="activeTab === 'info'" class="info-tab">
            <div class="description-section">
              <h3>Turnuva Hakkında</h3>
              <div class="description" v-html="tournament.description || 'Açıklama bulunmuyor.'"></div>
            </div>

            <div class="details-grid">
              <div class="detail-item">
                <span class="detail-label">Başlangıç Tarihi</span>
                <span class="detail-value">{{ formatDate(tournament.start_date, true) }}</span>
              </div>
              <div class="detail-item" v-if="tournament.end_date">
                <span class="detail-label">Bitiş Tarihi</span>
                <span class="detail-value">{{ formatDate(tournament.end_date, true) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Format</span>
                <span class="detail-value">{{ tournamentsStore.getFormatLabel(tournament.format) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Oyun</span>
                <span class="detail-value">{{ tournamentsStore.getGameLabel(tournament.game_type) }}</span>
              </div>
              <div class="detail-item" v-if="tournament.team_size">
                <span class="detail-label">Takım Boyutu</span>
                <span class="detail-value">{{ tournament.team_size }}v{{ tournament.team_size }}</span>
              </div>
              <div class="detail-item" v-if="tournament.map_pool">
                <span class="detail-label">Harita Havuzu</span>
                <span class="detail-value">{{ tournament.map_pool.join(', ') }}</span>
              </div>
            </div>
          </div>

          <!-- Bracket Tab -->
          <div v-if="activeTab === 'bracket'" class="bracket-tab">
            <TournamentBracket :tournament-id="tournament.id" />
          </div>

          <!-- Participants Tab -->
          <div v-if="activeTab === 'participants'" class="participants-tab">
            <div v-if="loadingParticipants" class="loading-participants">
              <n-spin size="small" />
              <span>Katılımcılar yükleniyor...</span>
            </div>

            <div v-else-if="participants.length === 0" class="empty-participants">
              <Users class="w-12 h-12 text-gray-500" />
              <p>Henüz katılımcı yok</p>
            </div>

            <div v-else class="participants-grid">
              <div
                v-for="participant in participants"
                :key="participant.id"
                class="participant-item"
              >
                <n-avatar :size="40" :src="participant.avatar" round>
                  {{ participant.name?.charAt(0).toUpperCase() }}
                </n-avatar>
                <div class="participant-info">
                  <span class="participant-name">{{ participant.name }}</span>
                  <span class="participant-joined">{{ formatDate(participant.joined_at) }}</span>
                </div>
                <div v-if="participant.seed" class="participant-seed">
                  #{{ participant.seed }}
                </div>
              </div>
            </div>
          </div>

          <!-- Prizes Tab -->
          <div v-if="activeTab === 'prizes'" class="prizes-tab">
            <div class="prizes-list">
              <div class="prize-item first">
                <div class="prize-place">
                  <Trophy class="w-8 h-8" />
                  <span>1.</span>
                </div>
                <div class="prize-amount">{{ formatPrize(tournament.prizes?.first || tournament.prize_pool * 0.5) }}</div>
              </div>
              <div class="prize-item second">
                <div class="prize-place">
                  <Medal class="w-7 h-7" />
                  <span>2.</span>
                </div>
                <div class="prize-amount">{{ formatPrize(tournament.prizes?.second || tournament.prize_pool * 0.3) }}</div>
              </div>
              <div class="prize-item third">
                <div class="prize-place">
                  <Medal class="w-6 h-6" />
                  <span>3.</span>
                </div>
                <div class="prize-amount">{{ formatPrize(tournament.prizes?.third || tournament.prize_pool * 0.2) }}</div>
              </div>
            </div>

            <div v-if="tournament.additional_prizes" class="additional-prizes">
              <h4>Ek Ödüller</h4>
              <p>{{ tournament.additional_prizes }}</p>
            </div>
          </div>

          <!-- Rules Tab -->
          <div v-if="activeTab === 'rules'" class="rules-tab">
            <div v-if="tournament.rules" class="rules-content" v-html="tournament.rules"></div>
            <div v-else class="no-rules">
              <FileText class="w-12 h-12 text-gray-500" />
              <p>Kurallar henüz yayınlanmadı.</p>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  Trophy,
  Calendar,
  Users,
  Award,
  Clock,
  ArrowLeft,
  Gamepad2,
  Swords,
  MapPin,
  UserPlus,
  UserMinus,
  Check,
  Play,
  Zap,
  Info,
  GitBranch,
  FileText,
  AlertTriangle,
  Medal
} from 'lucide-vue-next'
import { useTournamentsStore, TournamentStatus } from '@/stores/tournaments'
import { useAuthStore } from '@/stores/auth'
import TournamentBracket from '@/components/game/TournamentBracket.vue'

const route = useRoute()
const message = useMessage()
const tournamentsStore = useTournamentsStore()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref(null)
const tournament = ref(null)
const activeTab = ref('info')
const registering = ref(false)
const participants = ref([])
const loadingParticipants = ref(false)

// Computed
const participantPercent = computed(() => {
  if (!tournament.value?.max_participants) return 0
  return Math.round(((tournament.value.participants_count || 0) / tournament.value.max_participants) * 100)
})

const countdownText = computed(() => {
  if (!tournament.value) return ''

  const status = tournament.value.status
  const startDate = new Date(tournament.value.start_date)
  const now = new Date()
  const diff = startDate - now

  if (status === TournamentStatus.COMPLETED) return 'Tamamlandı'
  if (status === TournamentStatus.IN_PROGRESS) return 'Devam Ediyor'
  if (status === TournamentStatus.CANCELLED) return 'İptal Edildi'

  if (diff <= 0) return 'Başladı'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  if (days > 0) return `${days}g ${hours}s`
  if (hours > 0) return `${hours}s ${minutes}dk`
  return `${minutes}dk`
})

const countdownLabel = computed(() => {
  if (!tournament.value) return ''

  const status = tournament.value.status
  if (status === TournamentStatus.COMPLETED) return 'Durum'
  if (status === TournamentStatus.IN_PROGRESS) return 'Durum'
  if (status === TournamentStatus.CANCELLED) return 'Durum'

  return 'Başlamasına'
})

const canShowActions = computed(() => {
  return tournament.value &&
         (tournament.value.status === TournamentStatus.REGISTRATION ||
          tournament.value.status === TournamentStatus.IN_PROGRESS)
})

const canRegister = computed(() => {
  return tournament.value &&
         tournament.value.status === TournamentStatus.REGISTRATION &&
         !tournament.value.is_registered &&
         (tournament.value.participants_count || 0) < tournament.value.max_participants &&
         authStore.isAuthenticated
})

// Methods
const fetchTournament = async () => {
  const id = route.params.id
  if (!id) return

  loading.value = true
  error.value = null

  const result = await tournamentsStore.fetchTournament(id)

  if (result) {
    tournament.value = result
  } else {
    error.value = 'Turnuva bulunamadı veya yüklenirken bir hata oluştu.'
  }

  loading.value = false
}

const fetchParticipants = async () => {
  if (!tournament.value) return

  loadingParticipants.value = true
  participants.value = await tournamentsStore.fetchParticipants(tournament.value.id)
  loadingParticipants.value = false
}

const handleRegister = async () => {
  if (!authStore.isAuthenticated) {
    message.warning('Kayıt olmak için giriş yapmalısınız.')
    return
  }

  registering.value = true
  const result = await tournamentsStore.registerForTournament(tournament.value.id)
  registering.value = false

  if (result.success) {
    message.success(result.message)
    tournament.value.is_registered = true
    tournament.value.participants_count = (tournament.value.participants_count || 0) + 1
    fetchParticipants()
  } else {
    message.error(result.message)
  }
}

const handleUnregister = async () => {
  registering.value = true
  const result = await tournamentsStore.unregisterFromTournament(tournament.value.id)
  registering.value = false

  if (result.success) {
    message.success(result.message)
    tournament.value.is_registered = false
    tournament.value.participants_count = Math.max(0, (tournament.value.participants_count || 1) - 1)
    fetchParticipants()
  } else {
    message.error(result.message)
  }
}

const formatDate = (dateStr, full = false) => {
  if (!dateStr) return 'TBA'

  const date = new Date(dateStr)

  if (full) {
    return date.toLocaleString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPrize = (amount) => {
  if (!amount) return '₺0'
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 0
  }).format(amount)
}

// Watch for tab changes to load data
watch(activeTab, (newTab) => {
  if (newTab === 'participants' && participants.value.length === 0) {
    fetchParticipants()
  }
})

// Watch for route changes
watch(() => route.params.id, () => {
  fetchTournament()
}, { immediate: true })

onMounted(() => {
  fetchTournament()
})
</script>

<style scoped>
.tournament-detail-page {
  min-height: 100vh;
  padding-bottom: 60px;
}

.container-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 100px 20px;
  text-align: center;
}

.error-state h2 {
  margin: 0;
  font-size: 24px;
  color: var(--text-primary);
}

.error-state p {
  margin: 0;
  color: var(--text-secondary);
}

.back-btn,
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.2s;
}

.back-btn:hover,
.back-link:hover {
  background: var(--bg-tertiary);
  color: #f97316;
}

/* Banner */
.tournament-banner {
  position: relative;
  height: 350px;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 24px;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: var(--text-tertiary);
}

.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.3) 100%);
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.back-link {
  position: absolute;
  top: 24px;
  left: 24px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  color: white;
}

.status-badge {
  position: absolute;
  top: 24px;
  right: 24px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
}

.tournament-title {
  font-size: 36px;
  font-weight: 700;
  color: white;
  margin: 0 0 12px 0;
}

.tournament-meta {
  display: flex;
  gap: 24px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.tournament-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Info Cards */
.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

.card-icon {
  width: 40px;
  height: 40px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.card-icon.gold {
  color: #f59e0b;
}

.card-content {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.card-value.gold {
  color: #f59e0b;
}

.card-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.card-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--bg-tertiary);
}

.card-progress .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #16a34a);
  transition: width 0.3s;
}

/* Action Section */
.action-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(234, 88, 12, 0.05) 100%);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 16px;
  margin-bottom: 24px;
}

.registration-info h3,
.live-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: var(--text-primary);
}

.registration-info p,
.live-info p {
  margin: 0;
  color: var(--text-secondary);
}

.registration-deadline {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 13px;
  color: #f97316;
}

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: #ef4444;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 700;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.action-buttons {
  display: flex;
  gap: 12px;
}

/* Tabs */
.tournament-tabs {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 12px;
  margin-bottom: 24px;
  overflow-x: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn:hover {
  background: var(--bg-tertiary);
}

.tab-btn.active {
  background: #f97316;
  color: white;
}

/* Tab Content */
.tab-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  min-height: 400px;
}

/* Info Tab */
.description-section {
  margin-bottom: 32px;
}

.description-section h3 {
  font-size: 18px;
  margin: 0 0 16px 0;
}

.description {
  color: var(--text-secondary);
  line-height: 1.7;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.detail-label {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}

.detail-value {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

/* Participants Tab */
.loading-participants,
.empty-participants {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: var(--text-secondary);
}

.participants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 10px;
}

.participant-info {
  flex: 1;
  min-width: 0;
}

.participant-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
}

.participant-joined {
  font-size: 12px;
  color: var(--text-tertiary);
}

.participant-seed {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-tertiary);
}

/* Prizes Tab */
.prizes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 500px;
  margin: 0 auto;
}

.prize-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.prize-item.first {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.1) 100%);
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.prize-item.first .prize-place {
  color: #fbbf24;
}

.prize-item.second {
  background: linear-gradient(135deg, rgba(156, 163, 175, 0.2) 0%, rgba(107, 114, 128, 0.1) 100%);
  border: 1px solid rgba(156, 163, 175, 0.3);
}

.prize-item.second .prize-place {
  color: #9ca3af;
}

.prize-item.third {
  background: linear-gradient(135deg, rgba(180, 83, 9, 0.2) 0%, rgba(146, 64, 14, 0.1) 100%);
  border: 1px solid rgba(180, 83, 9, 0.3);
}

.prize-item.third .prize-place {
  color: #b45309;
}

.prize-place {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 700;
}

.prize-amount {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.additional-prizes {
  margin-top: 32px;
  padding: 20px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.additional-prizes h4 {
  margin: 0 0 8px 0;
}

.additional-prizes p {
  margin: 0;
  color: var(--text-secondary);
}

/* Rules Tab */
.rules-content {
  color: var(--text-secondary);
  line-height: 1.8;
}

.rules-content :deep(h1),
.rules-content :deep(h2),
.rules-content :deep(h3) {
  color: var(--text-primary);
  margin-top: 24px;
}

.rules-content :deep(ul),
.rules-content :deep(ol) {
  padding-left: 24px;
}

.no-rules {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .tournament-banner {
    height: 280px;
  }

  .tournament-title {
    font-size: 24px;
  }

  .tournament-meta {
    flex-wrap: wrap;
    gap: 12px;
  }

  .action-section {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .action-buttons {
    flex-direction: column;
    width: 100%;
  }

  .action-buttons .n-button {
    width: 100%;
  }

  .tab-content {
    padding: 16px;
  }
}
</style>
