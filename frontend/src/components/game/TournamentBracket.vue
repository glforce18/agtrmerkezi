<template>
  <div class="tournament-bracket">
    <!-- Loading -->
    <div v-if="loading" class="bracket-loading">
      <n-spin size="large" />
      <span>Bracket yükleniyor...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="!bracket || rounds.length === 0" class="bracket-empty">
      <GitBranch class="w-16 h-16 text-gray-500" />
      <h3>Bracket Henüz Oluşturulmadı</h3>
      <p>Turnuva başladığında bracket burada görünecek</p>
    </div>

    <!-- Bracket Display -->
    <div v-else class="bracket-container" ref="bracketContainer">
      <div class="bracket-rounds">
        <div
          v-for="(round, roundIndex) in rounds"
          :key="roundIndex"
          class="bracket-round"
        >
          <h4 class="round-title">{{ getRoundTitle(roundIndex) }}</h4>

          <div class="round-matches">
            <div
              v-for="match in round"
              :key="match.id"
              class="bracket-match"
              :class="{
                completed: match.status === 'completed',
                live: match.status === 'live'
              }"
              @click="selectMatch(match)"
            >
              <!-- Team 1 -->
              <div
                class="match-team"
                :class="{
                  winner: match.winner_id === match.team1?.id,
                  loser: match.status === 'completed' && match.winner_id !== match.team1?.id
                }"
              >
                <div class="team-info">
                  <n-avatar v-if="match.team1?.avatar" :size="24" :src="match.team1.avatar" round />
                  <span class="team-name">{{ match.team1?.name || 'TBD' }}</span>
                </div>
                <span class="team-score">{{ match.score1 ?? '-' }}</span>
              </div>

              <!-- VS Divider -->
              <div class="match-divider">
                <span v-if="match.status === 'live'" class="live-badge">LIVE</span>
              </div>

              <!-- Team 2 -->
              <div
                class="match-team"
                :class="{
                  winner: match.winner_id === match.team2?.id,
                  loser: match.status === 'completed' && match.winner_id !== match.team2?.id
                }"
              >
                <div class="team-info">
                  <n-avatar v-if="match.team2?.avatar" :size="24" :src="match.team2.avatar" round />
                  <span class="team-name">{{ match.team2?.name || 'TBD' }}</span>
                </div>
                <span class="team-score">{{ match.score2 ?? '-' }}</span>
              </div>

              <!-- Match Time -->
              <div v-if="match.scheduled_at" class="match-time">
                {{ formatMatchTime(match.scheduled_at) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Champion Display -->
        <div v-if="champion" class="champion-display">
          <div class="champion-trophy">
            <Trophy class="w-12 h-12" />
          </div>
          <div class="champion-info">
            <span class="champion-label">Şampiyon</span>
            <span class="champion-name">{{ champion.name }}</span>
          </div>
        </div>
      </div>

      <!-- Bracket Lines (SVG) -->
      <svg class="bracket-lines" v-if="showLines">
        <template v-for="(round, roundIndex) in rounds.slice(0, -1)" :key="'lines-' + roundIndex">
          <template v-for="(match, matchIndex) in round" :key="'line-' + match.id">
            <path
              v-if="matchIndex % 2 === 0"
              :d="getConnectorPath(roundIndex, matchIndex)"
              class="connector-line"
            />
          </template>
        </template>
      </svg>
    </div>

    <!-- Match Detail Modal -->
    <n-modal v-model:show="showMatchDetail" preset="card" :title="selectedMatch?.team1?.name + ' vs ' + selectedMatch?.team2?.name" style="max-width: 500px;">
      <div v-if="selectedMatch" class="match-detail">
        <div class="detail-teams">
          <div class="detail-team" :class="{ winner: selectedMatch.winner_id === selectedMatch.team1?.id }">
            <n-avatar :size="48" :src="selectedMatch.team1?.avatar" round>
              {{ selectedMatch.team1?.name?.charAt(0) }}
            </n-avatar>
            <span class="detail-name">{{ selectedMatch.team1?.name || 'TBD' }}</span>
            <span class="detail-score">{{ selectedMatch.score1 ?? 0 }}</span>
          </div>

          <div class="detail-vs">VS</div>

          <div class="detail-team" :class="{ winner: selectedMatch.winner_id === selectedMatch.team2?.id }">
            <n-avatar :size="48" :src="selectedMatch.team2?.avatar" round>
              {{ selectedMatch.team2?.name?.charAt(0) }}
            </n-avatar>
            <span class="detail-name">{{ selectedMatch.team2?.name || 'TBD' }}</span>
            <span class="detail-score">{{ selectedMatch.score2 ?? 0 }}</span>
          </div>
        </div>

        <div class="detail-info">
          <div class="info-row">
            <span class="info-label">Durum</span>
            <span class="info-value" :class="selectedMatch.status">
              {{ getMatchStatusLabel(selectedMatch.status) }}
            </span>
          </div>
          <div v-if="selectedMatch.scheduled_at" class="info-row">
            <span class="info-label">Tarih</span>
            <span class="info-value">{{ formatMatchTime(selectedMatch.scheduled_at, true) }}</span>
          </div>
          <div v-if="selectedMatch.map" class="info-row">
            <span class="info-label">Harita</span>
            <span class="info-value">{{ selectedMatch.map }}</span>
          </div>
        </div>

        <!-- Watch Button for Live Matches -->
        <n-button
          v-if="selectedMatch.status === 'live' && selectedMatch.stream_url"
          type="primary"
          block
          tag="a"
          :href="selectedMatch.stream_url"
          target="_blank"
        >
          <template #icon><Play class="w-4 h-4" /></template>
          Canlı İzle
        </n-button>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Trophy, GitBranch, Play } from 'lucide-vue-next'
import { useTournamentsStore } from '@/stores/tournaments'

const props = defineProps({
  tournamentId: {
    type: [String, Number],
    required: true
  },
  bracket: {
    type: Object,
    default: null
  }
})

const tournamentsStore = useTournamentsStore()

const loading = ref(false)
const bracketData = ref(null)
const bracketContainer = ref(null)
const showMatchDetail = ref(false)
const selectedMatch = ref(null)
const showLines = ref(true)

// Computed
const rounds = computed(() => {
  const data = bracketData.value || props.bracket
  if (!data) return []

  // If bracket is already organized by rounds
  if (data.rounds) return data.rounds

  // If bracket is flat list of matches, organize by round
  if (data.matches) {
    const matchesByRound = {}
    data.matches.forEach(match => {
      const round = match.round || 0
      if (!matchesByRound[round]) matchesByRound[round] = []
      matchesByRound[round].push(match)
    })

    return Object.keys(matchesByRound)
      .sort((a, b) => a - b)
      .map(round => matchesByRound[round])
  }

  return []
})

const champion = computed(() => {
  const finalRound = rounds.value[rounds.value.length - 1]
  if (!finalRound || finalRound.length !== 1) return null

  const finalMatch = finalRound[0]
  if (finalMatch.status !== 'completed') return null

  if (finalMatch.winner_id === finalMatch.team1?.id) return finalMatch.team1
  if (finalMatch.winner_id === finalMatch.team2?.id) return finalMatch.team2

  return null
})

// Methods
const fetchBracket = async () => {
  if (props.bracket) {
    bracketData.value = props.bracket
    return
  }

  loading.value = true
  const data = await tournamentsStore.fetchBracket(props.tournamentId)
  bracketData.value = data
  loading.value = false
}

const getRoundTitle = (roundIndex) => {
  const totalRounds = rounds.value.length

  if (roundIndex === totalRounds - 1) return 'Final'
  if (roundIndex === totalRounds - 2) return 'Yarı Final'
  if (roundIndex === totalRounds - 3) return 'Çeyrek Final'

  return `Tur ${roundIndex + 1}`
}

const formatMatchTime = (dateStr, full = false) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)

  if (full) {
    return date.toLocaleString('tr-TR', {
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return date.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getMatchStatusLabel = (status) => {
  const labels = {
    pending: 'Bekliyor',
    scheduled: 'Planlandı',
    live: 'Canlı',
    completed: 'Tamamlandı',
    cancelled: 'İptal'
  }
  return labels[status] || status
}

const selectMatch = (match) => {
  selectedMatch.value = match
  showMatchDetail.value = true
}

const getConnectorPath = (roundIndex, matchIndex) => {
  // This would calculate SVG path for bracket lines
  // Simplified for now - actual implementation would need element positions
  return ''
}

// Watch for bracket prop changes
watch(() => props.bracket, (newBracket) => {
  if (newBracket) {
    bracketData.value = newBracket
  }
}, { immediate: true })

// Fetch bracket on mount if not provided
onMounted(() => {
  if (!props.bracket) {
    fetchBracket()
  }
})
</script>

<style scoped>
.tournament-bracket {
  width: 100%;
  overflow-x: auto;
  padding: 20px 0;
}

.bracket-loading,
.bracket-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.bracket-empty h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.bracket-empty p {
  margin: 0;
  font-size: 14px;
}

.bracket-container {
  position: relative;
  display: inline-block;
  min-width: 100%;
}

.bracket-rounds {
  display: flex;
  gap: 40px;
  padding: 20px;
}

.bracket-round {
  display: flex;
  flex-direction: column;
  min-width: 220px;
}

.round-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--border-color);
}

.round-matches {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  flex: 1;
  gap: 16px;
}

.bracket-match {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bracket-match:hover {
  border-color: #f97316;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.15);
}

.bracket-match.live {
  border-color: #ef4444;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
}

.match-team {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  transition: background 0.2s;
}

.match-team.winner {
  background: rgba(34, 197, 94, 0.1);
}

.match-team.loser {
  opacity: 0.5;
}

.team-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.team-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-score {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 24px;
  text-align: center;
}

.match-team.winner .team-score {
  color: #22c55e;
}

.match-divider {
  height: 1px;
  background: var(--border-color);
  position: relative;
}

.live-badge {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  padding: 2px 8px;
  background: #ef4444;
  color: white;
  font-size: 9px;
  font-weight: 700;
  border-radius: 4px;
  letter-spacing: 1px;
}

.match-time {
  text-align: center;
  padding: 4px;
  font-size: 11px;
  color: var(--text-tertiary);
  background: var(--bg-tertiary);
}

.champion-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  min-width: 150px;
}

.champion-trophy {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 50%;
  color: white;
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.champion-info {
  text-align: center;
}

.champion-label {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.champion-name {
  font-size: 18px;
  font-weight: 700;
  color: #f59e0b;
}

.bracket-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.connector-line {
  fill: none;
  stroke: var(--border-color);
  stroke-width: 2;
}

/* Match Detail Modal */
.match-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.detail-team {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.detail-team.winner {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.detail-name {
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
}

.detail-score {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
}

.detail-team.winner .detail-score {
  color: #22c55e;
}

.detail-vs {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-tertiary);
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.info-value.live {
  color: #ef4444;
}

.info-value.completed {
  color: #22c55e;
}
</style>
