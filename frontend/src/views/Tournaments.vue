<template>
  <div class="tournaments-page">
    <!-- Maintenance Check -->
    <MaintenanceOverlay feature="tournaments" />

    <div class="container-main">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">
            <Trophy class="w-8 h-8" />
            Turnuvalar
          </h1>
          <p class="page-description">
            CS 1.6 ve Half-Life turnuvalarına katıl, ödüller kazan!
          </p>
        </div>

        <!-- Quick Stats -->
        <div class="quick-stats">
          <div class="stat-item">
            <span class="stat-value">{{ activeTournaments.length }}</span>
            <span class="stat-label">Aktif Turnuva</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ upcomingTournaments.length }}</span>
            <span class="stat-label">Yaklaşan</span>
          </div>
          <div class="stat-item" v-if="myTournaments.length > 0">
            <span class="stat-value">{{ myTournaments.length }}</span>
            <span class="stat-label">Katıldığın</span>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-tabs">
          <button
            class="filter-tab"
            :class="{ active: !activeFilter }"
            @click="setFilter(null)"
          >
            Tümü
          </button>
          <button
            class="filter-tab"
            :class="{ active: activeFilter === 'registration' }"
            @click="setFilter('registration')"
          >
            <Circle class="w-3 h-3 fill-green-500 text-green-500" />
            Kayıt Açık
          </button>
          <button
            class="filter-tab"
            :class="{ active: activeFilter === 'in_progress' }"
            @click="setFilter('in_progress')"
          >
            <Zap class="w-3 h-3" />
            Devam Eden
          </button>
          <button
            class="filter-tab"
            :class="{ active: activeFilter === 'upcoming' }"
            @click="setFilter('upcoming')"
          >
            <Clock class="w-3 h-3" />
            Yaklaşan
          </button>
          <button
            class="filter-tab"
            :class="{ active: activeFilter === 'completed' }"
            @click="setFilter('completed')"
          >
            <CheckCircle class="w-3 h-3" />
            Tamamlanan
          </button>
        </div>

        <div class="filter-actions">
          <n-select
            v-model:value="gameFilter"
            :options="gameOptions"
            placeholder="Tüm Oyunlar"
            clearable
            style="width: 180px"
            @update:value="handleGameFilter"
          />

          <n-input
            v-model:value="searchQuery"
            placeholder="Turnuva ara..."
            clearable
            @update:value="handleSearch"
          >
            <template #prefix>
              <Search class="w-4 h-4 text-gray-400" />
            </template>
          </n-input>
        </div>
      </div>

      <!-- Featured Tournament -->
      <div v-if="featuredTournament" class="featured-tournament">
        <div class="featured-banner">
          <img
            v-if="featuredTournament.banner_url"
            :src="featuredTournament.banner_url"
            :alt="featuredTournament.name"
          />
          <div v-else class="featured-placeholder">
            <Trophy class="w-20 h-20" />
          </div>
          <div class="featured-overlay">
            <span class="featured-badge">
              <Star class="w-4 h-4" />
              Öne Çıkan
            </span>
            <h2>{{ featuredTournament.name }}</h2>
            <p>{{ featuredTournament.description }}</p>
            <div class="featured-info">
              <span><Calendar class="w-4 h-4" /> {{ formatDate(featuredTournament.start_date) }}</span>
              <span><Users class="w-4 h-4" /> {{ featuredTournament.participants_count || 0 }} / {{ featuredTournament.max_participants }}</span>
              <span v-if="featuredTournament.prize_pool"><Award class="w-4 h-4" /> {{ formatPrize(featuredTournament.prize_pool) }}</span>
            </div>
            <router-link :to="`/tournaments/${featuredTournament.id}`" class="featured-btn">
              Detayları Gör
              <ChevronRight class="w-4 h-4" />
            </router-link>
          </div>
        </div>
      </div>

      <!-- My Tournaments Section -->
      <div v-if="authStore.isAuthenticated && myTournaments.length > 0" class="my-tournaments">
        <h3 class="section-title">
          <User class="w-5 h-5" />
          Turnuvalarım
        </h3>
        <div class="tournaments-scroll">
          <TournamentCard
            v-for="tournament in myTournaments"
            :key="tournament.id"
            :tournament="tournament"
            class="mini-card"
          />
        </div>
      </div>

      <!-- Tournament List -->
      <div class="tournaments-section">
        <h3 class="section-title">
          <Trophy class="w-5 h-5" />
          {{ sectionTitle }}
        </h3>

        <!-- Loading -->
        <div v-if="loading && tournaments.length === 0" class="loading-state">
          <n-spin size="large" />
          <span>Turnuvalar yükleniyor...</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredTournaments.length === 0" class="empty-state">
          <Trophy class="w-16 h-16 text-gray-500" />
          <h3>Turnuva Bulunamadı</h3>
          <p>Şu an için bu kategoride turnuva bulunmuyor.</p>
          <n-button v-if="activeFilter" @click="clearFilters">Filtreleri Temizle</n-button>
        </div>

        <!-- Tournament Grid -->
        <div v-else class="tournaments-grid">
          <TournamentCard
            v-for="tournament in filteredTournaments"
            :key="tournament.id"
            :tournament="tournament"
          />
        </div>

        <!-- Load More -->
        <div v-if="hasMore && !loading" class="load-more">
          <n-button @click="loadMore" :loading="loading">
            Daha Fazla Yükle
          </n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import MaintenanceOverlay from '@/components/MaintenanceOverlay.vue'
import {
  Trophy,
  Calendar,
  Users,
  Award,
  Clock,
  Search,
  Star,
  ChevronRight,
  Circle,
  Zap,
  CheckCircle,
  User
} from 'lucide-vue-next'
import { useTournamentsStore, TournamentStatus, GameType } from '@/stores/tournaments'
import { useAuthStore } from '@/stores/auth'
import TournamentCard from '@/components/game/TournamentCard.vue'

const tournamentsStore = useTournamentsStore()
const authStore = useAuthStore()

const {
  tournaments,
  filteredTournaments,
  upcomingTournaments,
  activeTournaments,
  myTournaments,
  loading,
  pagination
} = storeToRefs(tournamentsStore)

const activeFilter = ref(null)
const gameFilter = ref(null)
const searchQuery = ref('')

const gameOptions = [
  { label: 'Counter-Strike 1.6', value: GameType.CS_16 },
  { label: 'Half-Life', value: GameType.HALF_LIFE },
  { label: 'Diğer', value: GameType.OTHER }
]

// Computed
const hasMore = computed(() => pagination.value.hasMore)

const featuredTournament = computed(() => {
  // Show most important registration-open tournament
  const registration = tournaments.value.find(t =>
    t.status === TournamentStatus.REGISTRATION && t.is_featured
  )
  if (registration) return registration

  // Or any active tournament
  const active = tournaments.value.find(t =>
    t.status === TournamentStatus.IN_PROGRESS && t.is_featured
  )
  if (active) return active

  // Or first registration tournament with prize
  return tournaments.value.find(t =>
    t.status === TournamentStatus.REGISTRATION && t.prize_pool > 0
  )
})

const sectionTitle = computed(() => {
  if (activeFilter.value === 'registration') return 'Kayıt Açık Turnuvalar'
  if (activeFilter.value === 'in_progress') return 'Devam Eden Turnuvalar'
  if (activeFilter.value === 'upcoming') return 'Yaklaşan Turnuvalar'
  if (activeFilter.value === 'completed') return 'Tamamlanan Turnuvalar'
  return 'Tüm Turnuvalar'
})

// Methods
const setFilter = (filter) => {
  activeFilter.value = filter
  tournamentsStore.setFilters({ status: filter })
}

const handleGameFilter = (value) => {
  tournamentsStore.setFilters({ game: value })
}

let searchTimeout = null
const handleSearch = (value) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    tournamentsStore.setFilters({ search: value })
  }, 300)
}

const clearFilters = () => {
  activeFilter.value = null
  gameFilter.value = null
  searchQuery.value = ''
  tournamentsStore.clearFilters()
}

const loadMore = () => {
  tournamentsStore.loadMore()
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'TBA'
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
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

onMounted(() => {
  tournamentsStore.init()
})
</script>

<style scoped>
.tournaments-page {
  min-height: 100vh;
  padding: 24px 0 60px;
}

.container-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 32px;
}

.header-content {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.quick-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-radius: 12px;
  min-width: 100px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #f97316;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover {
  background: var(--bg-tertiary);
}

.filter-tab.active {
  background: rgba(249, 115, 22, 0.1);
  border-color: #f97316;
  color: #f97316;
}

.filter-actions {
  display: flex;
  gap: 12px;
}

/* Featured Tournament */
.featured-tournament {
  margin-bottom: 40px;
}

.featured-banner {
  position: relative;
  height: 300px;
  border-radius: 20px;
  overflow: hidden;
}

.featured-banner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: var(--text-tertiary);
}

.featured-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.5) 50%, transparent 100%);
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}

.featured-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  width: fit-content;
}

.featured-overlay h2 {
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.featured-overlay p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  max-width: 500px;
}

.featured-info {
  display: flex;
  gap: 24px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.featured-info span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.featured-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: white;
  border-radius: 8px;
  font-weight: 600;
  color: #1e293b;
  text-decoration: none;
  width: fit-content;
  margin-top: 8px;
  transition: all 0.2s;
}

.featured-btn:hover {
  background: #f97316;
  color: white;
}

/* My Tournaments */
.my-tournaments {
  margin-bottom: 40px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.tournaments-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 12px;
}

.mini-card {
  min-width: 280px;
  flex-shrink: 0;
}

/* Tournament Grid */
.tournaments-section {
  margin-bottom: 40px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state h3 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .quick-stats {
    width: 100%;
    justify-content: space-between;
  }

  .stat-item {
    flex: 1;
    min-width: auto;
    padding: 12px;
  }

  .stat-value {
    font-size: 24px;
  }

  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-tabs {
    overflow-x: auto;
    padding-bottom: 8px;
    flex-wrap: nowrap;
  }

  .filter-tab {
    white-space: nowrap;
  }

  .filter-actions {
    flex-direction: column;
  }

  .filter-actions :deep(.n-select),
  .filter-actions :deep(.n-input) {
    width: 100% !important;
  }

  .featured-banner {
    height: 250px;
  }

  .featured-overlay {
    padding: 20px;
  }

  .featured-overlay h2 {
    font-size: 24px;
  }

  .featured-info {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>
