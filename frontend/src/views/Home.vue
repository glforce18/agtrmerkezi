<template>
  <div class="home-page min-h-screen overflow-hidden">
    <!-- Subtle Background -->
    <div class="hero-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>

      <!-- Floating Game Weapons -->
      <div class="floating-weapons">
        <GameIcon name="weapon-ak47" class="floating-weapon weapon-1" size="xl" color="rgba(249, 115, 22, 0.15)" />
        <GameIcon name="weapon-awp" class="floating-weapon weapon-2" size="xl" color="rgba(139, 92, 246, 0.12)" />
        <GameIcon name="weapon-m4a1" class="floating-weapon weapon-3" size="lg" color="rgba(6, 182, 212, 0.12)" />
        <GameIcon name="weapon-deagle" class="floating-weapon weapon-4" size="lg" color="rgba(249, 115, 22, 0.1)" />
        <GameIcon name="weapon-knife" class="floating-weapon weapon-5" size="md" color="rgba(239, 68, 68, 0.12)" />
        <GameIcon name="weapon-crowbar" class="floating-weapon weapon-6" size="lg" color="rgba(249, 115, 22, 0.15)" />
      </div>
    </div>

    <!-- Compact Header -->
    <section class="pt-4 pb-2">
      <div class="container-main">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
              <span class="text-white font-bold text-lg">A</span>
            </div>
            <div>
              <h1 class="text-xl font-bold">{{ logoText }}</h1>
              <p class="text-sm text-gray-400">{{ animatedOnline }}+ oyuncu aktif</p>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <router-link to="/forum">
              <button class="btn-primary-cta muzzle-flash-hover text-sm py-2 px-4">
                <MessageSquare class="w-4 h-4" />
                Forum
              </button>
            </router-link>
            <router-link to="/servers">
              <button class="btn-secondary-cta muzzle-flash-hover text-sm py-2 px-4">
                <Server class="w-4 h-4" />
                Sunucular
              </button>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Forum Showcase - Ana Forum Bölümü (60%/40% Grid) -->
    <section class="forum-topics-showcase py-2 relative">
      <div class="container-main relative z-10">
        <!-- Forum Grid Layout - 60%/40% -->
        <div class="forum-main-grid">
          <!-- Sol Taraf: Forum İçeriği (60%) -->
          <div class="forum-content-main">
            <!-- Canlı Aktivite -->
            <LiveActivityFeed :activities="liveActivities" />

            <!-- Trend Konular -->
            <TrendingTopicsSection
              :topics="trendingTopics"
              :loading="loadingTrending"
            />

            <!-- Popüler ve Son Konular -->
            <div class="forum-showcase-grid">
              <PopularTopicsSection />
              <RecentTopicsSection />
            </div>

            <!-- Tüm Konuları Gör Butonu -->
            <div class="forum-view-all">
              <router-link to="/forum" class="forum-view-all-btn">
                <MessageSquare class="w-5 h-5" />
                Tüm Konuları Gör
                <ArrowRight class="w-4 h-4" />
              </router-link>
            </div>
          </div>

          <!-- Sağ Sidebar (40%) -->
          <aside class="forum-sidebar">
            <!-- Hızlı Erişim -->
            <div class="quick-access-card">
              <h3 class="sidebar-card-title">
                <Zap class="w-5 h-5" />
                Hızlı Erişim
              </h3>
              <div class="quick-access-buttons">
                <router-link to="/forum" class="quick-btn quick-btn-primary">
                  <MessageSquare class="w-4 h-4" />
                  Forum'a Git
                </router-link>
                <router-link
                  :to="isLoggedIn ? '/forum/new-topic' : '/login'"
                  class="quick-btn quick-btn-success"
                >
                  <MessageCircle class="w-4 h-4" />
                  Yeni Konu Aç
                </router-link>
              </div>
            </div>

            <!-- Online Kullanıcılar -->
            <OnlineUsersWidget
              :users="onlineUsers"
              :total="forumStats.onlineUsers"
            />

            <!-- Canlı Sunucular -->
            <CompactServersWidget
              :servers="sidebarServers"
              :loading="loadingSidebarServers"
            />

            <!-- Kategoriler -->
            <QuickCategoriesWidget
              :categories="forumCategories"
              :maxDisplay="6"
            />
          </aside>
        </div>
      </div>
    </section>

    <!-- Active Tournaments Section - Sadece aktif etkinlik varsa göster -->
    <section v-if="activeEvents.length > 0" class="tournaments-section py-4 relative">
      <div class="section-glow section-glow-left"></div>
      <div class="container-main relative z-10">
        <div class="section-header mb-3 text-center">
          <div class="section-badge mx-auto">
            <Flame class="w-4 h-4" />
            <span>Aktif Etkinlikler</span>
          </div>
          <h2 class="section-title justify-center">
            <Calendar class="section-icon" />
            Turnuvalar & Etkinlikler
          </h2>
          <p class="section-subtitle">Heyecan verici turnuvalara katıl ve ödülleri kazan</p>
        </div>

        <div class="tournaments-grid grid md:grid-cols-2 gap-4 max-w-5xl mx-auto">
          <div
            v-for="(event, index) in activeEvents"
            :key="event.id"
            class="tournament-card"
            :style="{ animationDelay: `${index * 0.15}s` }"
          >
            <div class="tournament-badge">
              <Trophy class="w-5 h-5" />
              TURNUVA
            </div>
            <div class="tournament-content">
              <h3 class="tournament-title">{{ event.title }}</h3>
              <p class="tournament-desc">{{ event.description }}</p>

              <div class="tournament-info">
                <div class="info-item">
                  <Calendar class="w-4 h-4" />
                  <span>{{ event.date }}</span>
                </div>
                <div class="info-item">
                  <Users class="w-4 h-4" />
                  <span>{{ event.participants }} Katılımcı</span>
                </div>
              </div>

              <div class="tournament-prize">
                <Crown class="w-5 h-5" />
                <span class="prize-amount">{{ event.prize }}</span>
                <span class="prize-label">Ödül</span>
              </div>

              <div class="tournament-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: `${(event.participants / event.maxParticipants) * 100}%` }"></div>
                </div>
                <span class="progress-text">{{ event.participants }}/{{ event.maxParticipants }} kayıt</span>
              </div>
            </div>

            <div class="tournament-actions">
              <n-tooltip :disabled="isLoggedIn" trigger="hover">
                <template #trigger>
                  <n-button
                    type="primary"
                    block
                    :class="{ 'btn-disabled': !isLoggedIn }"
                    @click="joinTournament(event)"
                  >
                    <template #icon>
                      <Lock v-if="!isLoggedIn" class="w-4 h-4" />
                      <Zap v-else class="w-4 h-4" />
                    </template>
                    {{ isLoggedIn ? 'Hemen Katil' : 'Giriş Yap' }}
                  </n-button>
                </template>
                Turnuvaya katilmak icin giriş yapin
              </n-tooltip>
            </div>

            <div class="tournament-glow"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA Section -->
    <section class="cta-section py-6 relative">
      <div class="cta-background">
        <div class="cta-gradient"></div>
        <div class="cta-pattern"></div>
      </div>
      <div class="container-main relative z-10 text-center">
        <h2 class="cta-title mb-3">
          Topluluğumuza <span class="text-gradient">Katıl</span>
        </h2>
        <p class="cta-description mb-4 max-w-2xl mx-auto">
          Binlerce CS 1.6 oyuncusuyla tanışmayı, turnuvalara katılmayi ve
          en iyi sunucularda oynamayı mı bekliyorsun? Hemen ücretsiz kayıt ol!
        </p>
        <div class="cta-buttons-final flex flex-wrap justify-center gap-6">
          <router-link to="/register">
            <button class="btn-primary-cta muzzle-flash-hover recoil-click">
              <UserPlus class="w-6 h-6" />
              Ücretsiz Kayıt Ol
            </button>
          </router-link>
          <a :href="discordUrl" target="_blank" rel="noopener">
            <button class="btn-discord muzzle-flash-hover">
              <MessageCircle class="w-5 h-5" />
              Discord'a Katıl
            </button>
          </a>
        </div>

        <!-- Social Proof -->
        <div class="social-proof mt-6">
          <div class="avatars-stack">
            <div v-for="i in 5" :key="i" class="stack-avatar" :style="{ zIndex: 5 - i }">
              <n-avatar :size="40" round :style="{ background: `hsl(${i * 60}, 70%, 50%)` }">
                {{ String.fromCharCode(64 + i) }}
              </n-avatar>
            </div>
          </div>
          <p class="social-text">
            <span class="social-count">25,000+</span> oyuncu aramiza katıldi
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useSettingsStore } from '@/stores/settings'
import { useClansStore } from '@/stores/clans'
import { useAuthStore } from '@/stores/auth'
import { useRequireSteam } from '@/composables/useRequireSteam'
import { useGameAssets } from '@/composables/useGameAssets'
import GameIcon from '@/components/game/GameIcon.vue'
import ActivityFeed from '@/components/social/ActivityFeed.vue'
import PopularTopicsSection from '@/components/forum/PopularTopicsSection.vue'
import RecentTopicsSection from '@/components/forum/RecentTopicsSection.vue'
import LiveActivityFeed from '@/components/forum/LiveActivityFeed.vue'
import TrendingTopicsSection from '@/components/forum/TrendingTopicsSection.vue'
import OnlineUsersWidget from '@/components/sidebar/OnlineUsersWidget.vue'
import CompactServersWidget from '@/components/sidebar/CompactServersWidget.vue'
import QuickCategoriesWidget from '@/components/sidebar/QuickCategoriesWidget.vue'
import '@/assets/styles/ui-enhancements.css'
import {
  Server,
  MessageSquare,
  Trophy,
  Users,
  Calendar,
  ArrowRight,
  Crown,
  Medal,
  Award,
  Zap,
  Flame,
  Heart,
  Sparkles,
  UserPlus,
  MessageCircle,
  Eye,
  Play,
  Signal,
  MapPin,
  ChevronDown,
  Crosshair,
  Target,
  Gamepad2,
  Swords,
  Shield,
  Star,
  TrendingUp,
  Activity,
  Lock
} from 'lucide-vue-next'

const router = useRouter()
const themeStore = useThemeStore()
const settingsStore = useSettingsStore()
const authStore = useAuthStore()
const { hasSteam, requireSteam } = useRequireSteam()
const { getGames, getGameAssets } = useGameAssets()

// Games data
const gamesList = ref([
  { slug: 'cs16', name: 'Counter-Strike 1.6', icon: '🔫', gradient: 'linear-gradient(135deg, #ff6b00 0%, #1a1a2e 100%)' },
  { slug: 'halflife', name: 'Half-Life', icon: '🎮', gradient: 'linear-gradient(135deg, #ff8c00 0%, #1a1a2e 100%)' },
  { slug: 'css', name: 'CS: Source', icon: '🎯', gradient: 'linear-gradient(135deg, #2a9d8f 0%, #1a1a2e 100%)' },
  { slug: 'csgo', name: 'CS:GO', icon: '💣', gradient: 'linear-gradient(135deg, #e63946 0%, #1a1a2e 100%)' },
  { slug: 'tf2', name: 'Team Fortress 2', icon: '🏰', gradient: 'linear-gradient(135deg, #b5838d 0%, #1a1a2e 100%)' },
  { slug: 'sven', name: 'Sven Co-op', icon: '👥', gradient: 'linear-gradient(135deg, #457b9d 0%, #1a1a2e 100%)' }
])
const gameAssets = ref({})

// Auth state
const isLoggedIn = computed(() => !!authStore.user)
const clansStore = useClansStore()
const isDark = computed(() => themeStore.isDark)

// Activity section data
const recruitingClans = computed(() => clansStore.recruitingClans.slice(0, 3))
const onlineCount = ref(0)
const activeServers = ref(0)
const todayTopics = ref(0)

// Logo settings
const logoUrl = computed(() => settingsStore.settings.logo_url || '/logo-navbar.png')
const logoText = computed(() => settingsStore.settings.logo_text || 'AGTR')
const logoSubtitle = computed(() => settingsStore.settings.logo_subtitle || 'MERKEZI')
const discordUrl = computed(() => settingsStore.settings.discord_url || '#')

const handleLogoError = (e) => {
  e.target.style.display = 'none'
}

// Refs for animations
const logoRef = ref(null)
const titleRef = ref(null)
const statsSection = ref(null)

// Typing animation
const typingPhrases = [
  'Counter-Strike 1.6 Türkiye Topluluğu',
  'En İyi CS 1.6 Sunucuları',
  'Turnuvalar ve Etkinlikler',
  'Binlerce Aktif Oyuncu'
]
const typingText = ref('')
const currentPhraseIndex = ref(0)
const isDeleting = ref(false)
const typingSpeed = ref(100)

// Animated counters
const animatedOnline = ref(0)
const animatedStats = ref([
  { icon: markRaw(Users), value: 25000, animated: 0, suffix: '+', label: 'Kayıtlı Üye', color: '#f97316', barWidth: '85%' },
  { icon: markRaw(Server), value: 150, animated: 0, suffix: '+', label: 'Aktif Sunucu', color: '#06b6d4', barWidth: '75%' },
  { icon: markRaw(MessageSquare), value: 50000, animated: 0, suffix: '+', label: 'Forum Konusu', color: '#8b5cf6', barWidth: '90%' },
  { icon: markRaw(Trophy), value: 12, animated: 0, suffix: '', label: 'Aktif Turnuva', color: '#eab308', barWidth: '60%' }
])

// Particle styles
const getParticleStyle = (index) => {
  const size = Math.random() * 4 + 1
  const duration = Math.random() * 20 + 10
  const delay = Math.random() * 10
  const x = Math.random() * 100
  const y = Math.random() * 100

  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${x}%`,
    top: `${y}%`,
    animationDuration: `${duration}s`,
    animationDelay: `${delay}s`
  }
}

// Data
// Data - API'den çekilecek
const latestTopics = ref([])
const topPlayers = ref([])
const popularServers = ref([])
const activeEvents = ref([])

// Forum-focused data for sidebar
const liveActivities = ref([])
const trendingTopics = ref([])
const onlineUsers = ref([])
const sidebarServers = ref([])
const forumCategories = ref([])
const forumStats = ref({
  onlineUsers: 0,
  totalTopics: 0,
  topicsToday: 0,
  totalReplies: 0
})

// Loading states
const loadingTopics = ref(true)
const loadingPlayers = ref(true)
const loadingServers = ref(true)
const loadingEvents = ref(true)
const loadingLiveActivity = ref(true)
const loadingTrending = ref(true)
const loadingOnlineUsers = ref(true)
const loadingSidebarServers = ref(true)

// Fetch functions
const fetchLatestTopics = async () => {
  loadingTopics.value = true
  try {
    const response = await fetch('/api/forum/topics?limit=5&sort=newest')
    if (response.ok) {
      const data = await response.json()
      const topics = Array.isArray(data?.topics) ? data.topics : []
      latestTopics.value = topics.slice(0, 5).map(t => ({
        id: t?.id,
        title: t?.title || '',
        author: t?.author?.username || t?.author_name || 'Anonim',
        replies: t?.replies_count || t?.reply_count || 0,
        views: t?.views || t?.view_count || 0,
        category: t?.category?.name || t?.category_name || 'Genel'
      }))
    }
  } catch (error) {
    console.error('Topics fetch error:', error)
  } finally {
    loadingTopics.value = false
  }
}

const fetchTopPlayers = async () => {
  loadingPlayers.value = true
  try {
    const response = await fetch('/api/leaderboard?period=week&limit=5')
    if (response.ok) {
      const data = await response.json()
      topPlayers.value = (data.leaderboard || []).map((p, i) => ({
        id: p.user_id || i + 1,
        name: p.username || 'Oyuncu',
        title: getRankTitle(p.total_points || 0),
        kills: Math.round((p.total_points || 0) * 10),
        deaths: Math.round((p.total_points || 0) * 3),
        kd: ((p.total_points || 0) / 100).toFixed(2),
        level: Math.min(99, Math.floor((p.total_points || 0) / 100) + 1)
      }))
    }
  } catch (error) {
    console.error('Leaderboard fetch error:', error)
  } finally {
    loadingPlayers.value = false
  }
}

const fetchPopularServers = async () => {
  loadingServers.value = true
  try {
    const response = await fetch('/api/servers/live?limit=6')
    if (response.ok) {
      const data = await response.json()
      popularServers.value = (data.servers || []).map(s => ({
        id: s.id,
        name: s.name || 'Sunucu',
        map: s.current_map || s.map || 'unknown',
        players: s.players || s.current_players || 0,
        maxPlayers: s.max_players || 32,
        mode: getGameMode(s.game_type),
        ping: s.ping || 0,
        country: s.country || 'TR',
        online: s.is_online ?? true
      }))
    }
  } catch (error) {
    console.error('Servers fetch error:', error)
  } finally {
    loadingServers.value = false
  }
}

const fetchActiveEvents = async () => {
  loadingEvents.value = true
  try {
    const response = await fetch('/api/tournament/tournaments?status=active&limit=2')
    if (response.ok) {
      const data = await response.json()
      activeEvents.value = (data.tournaments || []).slice(0, 2).map(e => ({
        id: e.id,
        title: e.name || e.title,
        description: e.description || '',
        date: e.start_date ? new Date(e.start_date).toLocaleDateString('tr-TR') : '',
        participants: e.current_participants || e.participants_count || 0,
        maxParticipants: e.max_participants || 16,
        prize: e.prize_pool || e.prize || ''
      }))
    }
  } catch (error) {
    console.error('Events fetch error:', error)
  } finally {
    loadingEvents.value = false
  }
}

const fetchLiveStats = async () => {
  try {
    const response = await fetch('/api/stats')
    if (response.ok) {
      const data = await response.json()
      onlineCount.value = data.online_users || Math.floor(Math.random() * 100) + 50
      activeServers.value = data.active_servers || 0
      todayTopics.value = data.today_topics || 0
    }
  } catch (error) {
    console.error('Stats fetch error:', error)
  }
}

// ============== FORUM ODAKLI FETCH FONKSİYONLARI ==============

const fetchForumStats = async () => {
  try {
    const response = await fetch('/api/forum/stats')
    if (response.ok) {
      const data = await response.json()
      forumStats.value = {
        onlineUsers: data.onlineUsers || 0,
        totalTopics: data.totalTopics || 0,
        topicsToday: data.topicsToday || 0,
        totalReplies: data.totalReplies || 0
      }
    }
  } catch (error) {
    console.debug('Forum stats not available:', error)
  }
}

const fetchLiveActivity = async () => {
  loadingLiveActivity.value = true
  try {
    const response = await fetch('/api/forum/live-activity?limit=10')
    if (response.ok) {
      const data = await response.json()
      liveActivities.value = data.activities || []
    }
  } catch (error) {
    console.debug('Live activity not available:', error)
  } finally {
    loadingLiveActivity.value = false
  }
}

const fetchTrendingTopics = async () => {
  loadingTrending.value = true
  try {
    const response = await fetch('/api/forum/trending?days=7&limit=5')
    if (response.ok) {
      const data = await response.json()
      trendingTopics.value = data.topics || []
    }
  } catch (error) {
    console.debug('Trending topics not available:', error)
  } finally {
    loadingTrending.value = false
  }
}

const fetchOnlineUsers = async () => {
  loadingOnlineUsers.value = true
  try {
    const response = await fetch('/api/forum/online-users?limit=12')
    if (response.ok) {
      const data = await response.json()
      onlineUsers.value = data.users || []
      if (data.total) {
        forumStats.value.onlineUsers = data.total
      }
    }
  } catch (error) {
    console.debug('Online users not available:', error)
  } finally {
    loadingOnlineUsers.value = false
  }
}

const fetchSidebarServers = async () => {
  loadingSidebarServers.value = true
  try {
    const response = await fetch('/api/servers/live?limit=3')
    if (response.ok) {
      const data = await response.json()
      sidebarServers.value = (data.servers || []).slice(0, 3)
    }
  } catch (error) {
    console.debug('Servers not available:', error)
  } finally {
    loadingSidebarServers.value = false
  }
}

const fetchForumCategories = async () => {
  try {
    const response = await fetch('/api/forum/categories')
    if (response.ok) {
      const data = await response.json()
      forumCategories.value = data.categories || []
    }
  } catch (error) {
    console.debug('Categories not available:', error)
  }
}

const getRankTitle = (points) => {
  if (points >= 10000) return 'Legendary Player'
  if (points >= 5000) return 'Elite Player'
  if (points >= 2000) return 'Pro Player'
  if (points >= 1000) return 'Skilled Player'
  if (points >= 500) return 'Regular Player'
  return 'New Player'
}

const getGameMode = (gameType) => {
  const modes = {
    'cs16': 'CS 1.6',
    'ag': 'AG',
    'hldm': 'HLDM',
    'cscz': 'CS:CZ'
  }
  return modes[gameType] || gameType || 'Public'
}

// communityHighlights kaldırıldı - yeterli veri olduğunda API'den çekilecek

// Helper functions
const formatNumber = (num) => {
  return new Intl.NumberFormat('tr-TR').format(num)
}

const getModeType = (mode) => {
  const types = {
    Public: 'success',
    DM: 'warning',
    Zombie: 'error',
    AWP: 'info',
    Surf: 'primary',
    '5v5': 'default'
  }
  return types[mode] || 'default'
}

const getCategoryType = (category) => {
  const types = {
    Rehberler: 'info',
    Maplar: 'success',
    Duyurular: 'warning',
    Taktikler: 'primary'
  }
  return types[category] || 'default'
}

const getPingClass = (ping) => {
  if (ping < 20) return 'text-green-500'
  if (ping < 50) return 'text-yellow-500'
  return 'text-red-500'
}

const getPlayerGradient = (index) => {
  const gradients = [
    'linear-gradient(135deg, #ffd700, #ff8c00)',
    'linear-gradient(135deg, #c0c0c0, #808080)',
    'linear-gradient(135deg, #cd7f32, #8b4513)',
    'linear-gradient(135deg, #f97316, #ea580c)',
    'linear-gradient(135deg, #8b5cf6, #7c3aed)'
  ]
  return gradients[index] || gradients[3]
}

const connectServer = (server) => {
  // Steam connect protocol
  window.location.href = `steam://connect/${server.ip || 'agtr.com.tr'}:27015`
}

// Tournament join handler
const joinTournament = (event) => {
  requireSteam(() => {
    // Navigate to tournament details or registration page
    router.push(`/events/${event.id}`)
  })
}

// Game assets loading
const loadGameAssets = async () => {
  for (const game of gamesList.value) {
    try {
      const assets = await getGameAssets(game.slug, null, 10)
      const assetMap = {}
      assets.forEach(asset => {
        assetMap[asset.asset_type] = asset.file_path
      })
      gameAssets.value = { ...gameAssets.value, [game.slug]: assetMap }
    } catch (e) {
      // Asset loading error - silently fail
    }
  }
}

// Navigate to game forum/page
const navigateToGame = (slug) => {
  const forumMap = {
    cs16: '/forum/category/cs16',
    halflife: '/forum/category/half-life-ag',
    css: '/forum',
    csgo: '/forum',
    tf2: '/forum',
    sven: '/forum'
  }
  router.push(forumMap[slug] || '/forum')
}

// Animation functions
let typingInterval = null
let counterInterval = null

const typeText = () => {
  const currentPhrase = typingPhrases[currentPhraseIndex.value]

  if (isDeleting.value) {
    typingText.value = currentPhrase.substring(0, typingText.value.length - 1)
    typingSpeed.value = 50
  } else {
    typingText.value = currentPhrase.substring(0, typingText.value.length + 1)
    typingSpeed.value = 100
  }

  if (!isDeleting.value && typingText.value === currentPhrase) {
    setTimeout(() => { isDeleting.value = true }, 2000)
  } else if (isDeleting.value && typingText.value === '') {
    isDeleting.value = false
    currentPhraseIndex.value = (currentPhraseIndex.value + 1) % typingPhrases.length
  }
}

const animateCounters = () => {
  const duration = 2000
  const steps = 60
  const stepDuration = duration / steps

  let currentStep = 0
  counterInterval = setInterval(() => {
    currentStep++
    const progress = currentStep / steps

    // Easing function
    const easeOutQuart = 1 - Math.pow(1 - progress, 4)

    animatedStats.value.forEach((stat) => {
      stat.animated = Math.floor(stat.value * easeOutQuart)
    })

    animatedOnline.value = Math.floor(1250 * easeOutQuart)

    if (currentStep >= steps) {
      clearInterval(counterInterval)
    }
  }, stepDuration)
}

// Intersection Observer for scroll animations
let observer = null

onMounted(() => {
  // Fetch settings
  if (!settingsStore.loaded) {
    settingsStore.fetchSettings()
  }

  // Fetch real data from API
  fetchLatestTopics()
  fetchTopPlayers()
  fetchPopularServers()
  fetchActiveEvents()

  // Fetch forum-focused data for sidebar
  fetchForumStats()
  fetchLiveActivity()
  fetchTrendingTopics()
  fetchOnlineUsers()
  fetchSidebarServers()
  fetchForumCategories()

  // Load game assets (banners, logos)
  loadGameAssets()

  // Fetch clans for sidebar
  clansStore.fetchClans({ reset: true })

  // Fetch live stats
  fetchLiveStats()

  // Start typing animation
  typingInterval = setInterval(typeText, typingSpeed.value)

  // Animate counters when stats section is visible
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounters()
          observer.disconnect()
        }
      })
    },
    { threshold: 0.3 }
  )

  if (statsSection.value) {
    observer.observe(statsSection.value)
  }
})

onUnmounted(() => {
  if (typingInterval) clearInterval(typingInterval)
  if (counterInterval) clearInterval(counterInterval)
  if (observer) observer.disconnect()
})
</script>

<style scoped>
/* ===== Global Styles ===== */
.home-page {
  background: linear-gradient(180deg, #0f0f1a 0%, #18181c 100%);
  color: #f8fafc;
}

/* ===== Animated Background ===== */
.hero-background {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  animation: orbFloat 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.4) 0%, transparent 70%);
  top: -200px;
  left: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
  top: 50%;
  right: -150px;
  animation-delay: -7s;
}

.orb-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.3) 0%, transparent 70%);
  bottom: -100px;
  left: 30%;
  animation-delay: -14s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(0, 50px) scale(0.9); }
  75% { transform: translate(-50px, -25px) scale(1.05); }
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(249, 115, 22, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(249, 115, 22, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, black 40%, transparent 100%);
}

.particles-container {
  position: absolute;
  inset: 0;
}

.particle {
  position: absolute;
  background: rgba(249, 115, 22, 0.6);
  border-radius: 50%;
  animation: particleFloat linear infinite;
}

@keyframes particleFloat {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(720deg);
    opacity: 0;
  }
}

/* ===== Hero Section ===== */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

/* Floating Icons */
.floating-icons {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.floating-icon {
  position: absolute;
  color: rgba(249, 115, 22, 0.3);
  animation: iconFloat 6s ease-in-out infinite;
}

.icon-1 { top: 15%; left: 10%; animation-delay: 0s; }
.icon-2 { top: 25%; right: 15%; animation-delay: 1s; }
.icon-3 { bottom: 30%; left: 8%; animation-delay: 2s; }
.icon-4 { bottom: 20%; right: 10%; animation-delay: 3s; }
.icon-5 { top: 40%; left: 20%; animation-delay: 4s; }

@keyframes iconFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.3; }
  50% { transform: translateY(-20px) rotate(10deg); opacity: 0.6; }
}

/* Hero Logo */
.hero-logo-wrapper {
  display: flex;
  justify-content: center;
  position: relative;
  animation: fadeInDown 1s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-logo-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-hexagon {
  position: relative;
  z-index: 2;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(249, 115, 22, 0.05) 100%);
  border-radius: 30px;
  border: 2px solid rgba(249, 115, 22, 0.3);
  animation: logoFloat 4s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

.hero-logo-img {
  width: auto;
  height: 80px;
  max-height: 90px;
  object-fit: contain;
  filter: drop-shadow(0 4px 30px rgba(249, 115, 22, 0.5));
}

.hero-logo-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 26px;
}

.hero-logo-fallback span {
  color: white;
  font-size: 56px;
  font-weight: 800;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.logo-ring {
  position: absolute;
  border: 2px solid rgba(249, 115, 22, 0.2);
  border-radius: 50%;
  animation: ringExpand 3s ease-out infinite;
}

.ring-1 { inset: -20px; animation-delay: 0s; }
.ring-2 { inset: -40px; animation-delay: 0.5s; }
.ring-3 { inset: -60px; animation-delay: 1s; }

@keyframes ringExpand {
  0% { transform: scale(0.8); opacity: 0.8; }
  100% { transform: scale(1.2); opacity: 0; }
}

.hero-logo-glow {
  position: absolute;
  inset: -60px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.4) 0%, transparent 70%);
  filter: blur(40px);
  animation: glowPulse 3s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

/* Hero Title */
.hero-title {
  font-size: clamp(2.5rem, 8vw, 5rem);
  font-weight: 800;
  line-height: 1.1;
  animation: fadeInUp 1s ease-out 0.3s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.title-main {
  display: inline-block;
  background: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-right: 0.3em;
}

.title-accent {
  display: inline-block;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #f97316 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}

/* Subtitle */
.subtitle-wrapper {
  animation: fadeInUp 1s ease-out 0.5s both;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #f97316;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.cursor {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.hero-description {
  animation: fadeInUp 1s ease-out 0.7s both;
}

/* CTA Buttons */
.cta-buttons {
  animation: fadeInUp 1s ease-out 0.9s both;
}

.cta-primary {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(249, 115, 22, 0.4);
  transition: all 0.3s ease !important;
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(249, 115, 22, 0.5);
}

.cta-secondary {
  border: 2px solid rgba(249, 115, 22, 0.4) !important;
  background: rgba(249, 115, 22, 0.1) !important;
  transition: all 0.3s ease !important;
}

.cta-secondary:hover {
  border-color: #f97316 !important;
  background: rgba(249, 115, 22, 0.2) !important;
  transform: translateY(-2px);
}

/* Live Badge */
.live-badge {
  background: rgba(249, 115, 22, 0.15);
  border: 1px solid rgba(249, 115, 22, 0.3);
  animation: fadeInUp 1s ease-out 1.1s both;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: livePulse 2s infinite;
}

@keyframes livePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
  50% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
}

/* Scroll Indicator */
.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  animation: fadeIn 1s ease-out 1.5s both;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.mouse {
  width: 26px;
  height: 40px;
  border: 2px solid rgba(249, 115, 22, 0.5);
  border-radius: 13px;
  display: flex;
  justify-content: center;
  padding-top: 8px;
}

.wheel {
  width: 4px;
  height: 8px;
  background: #f97316;
  border-radius: 2px;
  animation: scroll 2s infinite;
}

@keyframes scroll {
  0% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(8px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

.scroll-arrow {
  width: 20px;
  height: 20px;
  color: rgba(249, 115, 22, 0.5);
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(5px); }
}

/* ===== Stats Section ===== */
.stats-section {
  position: relative;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
}

.stats-bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent, rgba(249, 115, 22, 0.05), transparent);
  pointer-events: none;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out both;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(249, 115, 22, 0.3);
  transform: translateY(-5px);
}

.stat-icon-wrapper {
  position: relative;
  display: inline-flex;
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 16px;
}

.stat-icon-glow {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  opacity: 0;
  filter: blur(20px);
  transition: opacity 0.3s ease;
}

.stat-card:hover .stat-icon-glow {
  opacity: 0.3;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 4px;
}

.counter {
  background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.suffix {
  color: #f97316;
  font-size: 1.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 16px;
}

.stat-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.stat-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease-out;
}

/* ===== Section Styles ===== */
.section-glow {
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  filter: blur(150px);
  opacity: 0.3;
  pointer-events: none;
}

.section-glow-right {
  right: -200px;
  top: 50%;
  transform: translateY(-50%);
  background: radial-gradient(circle, rgba(249, 115, 22, 0.5) 0%, transparent 70%);
}

.section-glow-left {
  left: -200px;
  top: 50%;
  transform: translateY(-50%);
  background: radial-gradient(circle, rgba(139, 92, 246, 0.5) 0%, transparent 70%);
}

.section-header {
  margin-bottom: 48px;
}

.section-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(249, 115, 22, 0.15);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #f97316;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.section-icon {
  width: 32px;
  height: 32px;
  color: #f97316;
}

.section-subtitle {
  color: #94a3b8;
  font-size: 1.125rem;
}

/* ===== Server Cards ===== */
.server-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  animation: fadeInUp 0.6s ease-out both;
  position: relative;
  overflow: hidden;
}

/* Animated border gradient */
.server-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(135deg, transparent 40%, rgba(249, 115, 22, 0.5) 50%, transparent 60%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.4s ease;
}

/* Scan line effect on hover */
.server-card::after {
  content: '';
  position: absolute;
  top: -100%;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(249, 115, 22, 0.1) 50%,
    transparent 100%
  );
  transition: top 0.6s ease;
  pointer-events: none;
}

.server-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(249, 115, 22, 0.4);
  transform: translateY(-8px) scale(1.02);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.3),
    0 0 30px rgba(249, 115, 22, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.server-card:hover::before {
  opacity: 1;
  animation: borderRotate 3s linear infinite;
}

.server-card:hover::after {
  top: 100%;
}

@keyframes borderRotate {
  0% {
    background: linear-gradient(0deg, transparent 40%, rgba(249, 115, 22, 0.5) 50%, transparent 60%);
  }
  25% {
    background: linear-gradient(90deg, transparent 40%, rgba(139, 92, 246, 0.5) 50%, transparent 60%);
  }
  50% {
    background: linear-gradient(180deg, transparent 40%, rgba(6, 182, 212, 0.5) 50%, transparent 60%);
  }
  75% {
    background: linear-gradient(270deg, transparent 40%, rgba(34, 197, 94, 0.5) 50%, transparent 60%);
  }
  100% {
    background: linear-gradient(360deg, transparent 40%, rgba(249, 115, 22, 0.5) 50%, transparent 60%);
  }
}

.server-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.server-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-online {
  color: #22c55e;
}

.status-online .status-dot {
  background: #22c55e;
  animation: livePulse 2s infinite;
}

.status-offline {
  color: #ef4444;
}

.status-offline .status-dot {
  background: #ef4444;
}

.server-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.server-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(6, 182, 212, 0.1));
  border-radius: 12px;
  color: #06b6d4;
}

.server-name {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 2px;
}

.server-map {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: #94a3b8;
}

.server-players {
  margin-bottom: 16px;
}

.players-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.players-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #f97316);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.players-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: #94a3b8;
}

.players-count {
  font-weight: 700;
  color: #f8fafc;
}

.server-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.server-ping {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: #94a3b8;
}

.view-all-btn {
  background: transparent !important;
  border: 2px solid rgba(249, 115, 22, 0.4) !important;
  transition: all 0.3s ease !important;
}

.view-all-btn:hover {
  border-color: #f97316 !important;
  background: rgba(249, 115, 22, 0.1) !important;
}

/* ===== Split Section (Forum & Leaderboard) ===== */
.split-section {
  background: rgba(0, 0, 0, 0.2);
}

.forum-panel,
.leaderboard-panel {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.25rem;
  font-weight: 700;
}

.panel-link {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f97316;
  font-size: 0.875rem;
  font-weight: 600;
  transition: gap 0.3s ease;
}

.panel-link:hover {
  gap: 8px;
}

/* Topics List */
.topics-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.topic-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.4s ease-out both;
}

.topic-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.topic-avatar {
  flex-shrink: 0;
}

.avatar-ring {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 10px;
  font-weight: 700;
  color: white;
}

.topic-content {
  flex: 1;
  min-width: 0;
}

.topic-title {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  color: #94a3b8;
}

.meta-author {
  color: #f97316;
}

.meta-dot {
  width: 3px;
  height: 3px;
  background: #64748b;
  border-radius: 50%;
}

.meta-stats {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Leaderboard List */
.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.player-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.player-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.player-item.rank-1 {
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.2);
}

.player-item.rank-2 {
  background: rgba(192, 192, 192, 0.1);
  border: 1px solid rgba(192, 192, 192, 0.2);
}

.player-item.rank-3 {
  background: rgba(205, 127, 50, 0.1);
  border: 1px solid rgba(205, 127, 50, 0.2);
}

.rank-badge {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.875rem;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  color: #1a1a1a;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #808080);
  color: #1a1a1a;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #8b4513);
  color: white;
}

.rank-badge:not(.rank-1):not(.rank-2):not(.rank-3) {
  background: rgba(255, 255, 255, 0.1);
  color: #94a3b8;
}

.player-avatar {
  position: relative;
}

.player-level {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: #f97316;
  color: white;
  font-size: 0.625rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 6px;
}

.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-title {
  font-size: 0.75rem;
  color: #94a3b8;
}

.player-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value-small {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
}

.stat-label-small {
  font-size: 0.625rem;
  color: #64748b;
  text-transform: uppercase;
}

/* ===== Tournament Cards ===== */
.tournament-card {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out both;
}

.tournament-card:hover {
  border-color: rgba(139, 92, 246, 0.4);
  transform: translateY(-5px);
}

.tournament-card:hover .tournament-glow {
  opacity: 1;
}

.tournament-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.1));
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #a78bfa;
  margin-bottom: 16px;
}

.tournament-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.tournament-desc {
  color: #94a3b8;
  margin-bottom: 20px;
  line-height: 1.6;
}

.tournament-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  color: #94a3b8;
}

.tournament-prize {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(234, 179, 8, 0.1));
  border-radius: 12px;
  margin-bottom: 20px;
}

.tournament-prize svg {
  color: #eab308;
}

.prize-amount {
  font-size: 1.25rem;
  font-weight: 800;
  color: #eab308;
}

.prize-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.tournament-progress {
  margin-bottom: 20px;
}

.progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
  border-radius: 3px;
}

.progress-text {
  font-size: 0.75rem;
  color: #94a3b8;
}

.tournament-glow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.5s ease;
  pointer-events: none;
}

/* Disabled Button State */
.btn-disabled {
  background: linear-gradient(135deg, #4b5563, #374151) !important;
  cursor: not-allowed;
  opacity: 0.8;
}

.btn-disabled:hover {
  transform: none !important;
  box-shadow: none !important;
}

/* ===== Community Highlights ===== */
.highlight-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out both;
}

.highlight-card:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateY(-5px);
}

.highlight-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  margin: 0 auto 16px;
}

.highlight-title {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.highlight-desc {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 16px;
  line-height: 1.6;
}

.highlight-stat {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  color: #f97316;
}

.stat-text {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
}

/* ===== CTA Section ===== */
.cta-section {
  position: relative;
  overflow: hidden;
}

.cta-background {
  position: absolute;
  inset: 0;
}

.cta-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,
    transparent 0%,
    rgba(249, 115, 22, 0.1) 50%,
    transparent 100%
  );
}

.cta-pattern {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 25% 25%, rgba(249, 115, 22, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
}

.cta-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
}

.text-gradient {
  background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cta-description {
  font-size: 1.125rem;
  color: #94a3b8;
  line-height: 1.8;
}

.cta-btn-primary {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(249, 115, 22, 0.4);
  padding: 0 32px !important;
  height: 52px !important;
}

.cta-btn-discord {
  background: #5865f2 !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(88, 101, 242, 0.4);
  padding: 0 32px !important;
  height: 52px !important;
}

.btn-discord {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 40px;
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: #5865f2;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(88, 101, 242, 0.4);
  transition: all 0.3s ease;
}

.btn-discord:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(88, 101, 242, 0.5);
}

/* Social Proof */
.social-proof {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatars-stack {
  display: flex;
}

.stack-avatar {
  margin-left: -12px;
  border: 3px solid #18181c;
  border-radius: 50%;
}

.stack-avatar:first-child {
  margin-left: 0;
}

.social-text {
  color: #94a3b8;
}

.social-count {
  color: #f97316;
  font-weight: 700;
}

/* ===== Responsive ===== */
@media (max-width: 1024px) {
  .floating-icons {
    display: none;
  }

  .hero-section {
    padding-top: 80px;
    padding-bottom: 100px;
  }

  .logo-hexagon {
    width: 100px;
    height: 100px;
  }

  .hero-logo-img {
    height: 60px;
  }

  .stat-value {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .title-line-1 {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .section-title {
    font-size: 1.5rem;
    flex-wrap: wrap;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .player-stats {
    display: none;
  }

  .cta-buttons-final {
    flex-direction: column;
  }

  .cta-btn-primary,
  .cta-btn-discord {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 1.75rem;
  }

  .stat-icon-wrapper {
    padding: 12px;
  }

  .stat-icon-wrapper svg {
    width: 24px;
    height: 24px;
  }

  .scroll-indicator {
    display: none;
  }
}

/* ===== Floating Game Weapons ===== */
.floating-weapons {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

.floating-weapon {
  position: absolute;
  animation: weaponFloat 15s ease-in-out infinite;
  filter: drop-shadow(0 0 20px currentColor);
}

.weapon-1 {
  top: 12%;
  left: 8%;
  animation-delay: 0s;
  animation-duration: 18s;
}

.weapon-2 {
  top: 20%;
  right: 10%;
  animation-delay: -3s;
  animation-duration: 20s;
  transform: rotate(-15deg);
}

.weapon-3 {
  bottom: 35%;
  left: 5%;
  animation-delay: -6s;
  animation-duration: 16s;
  transform: rotate(10deg);
}

.weapon-4 {
  bottom: 25%;
  right: 8%;
  animation-delay: -9s;
  animation-duration: 17s;
}

.weapon-5 {
  top: 45%;
  left: 15%;
  animation-delay: -12s;
  animation-duration: 19s;
  transform: rotate(-20deg);
}

.weapon-6 {
  top: 60%;
  right: 15%;
  animation-delay: -5s;
  animation-duration: 21s;
  transform: rotate(25deg);
}

@keyframes weaponFloat {
  0%, 100% {
    transform: translateY(0) rotate(var(--rotate, 0deg));
    opacity: 0.6;
  }
  25% {
    transform: translateY(-20px) rotate(calc(var(--rotate, 0deg) + 5deg));
    opacity: 0.8;
  }
  50% {
    transform: translateY(-10px) rotate(calc(var(--rotate, 0deg) - 3deg));
    opacity: 0.5;
  }
  75% {
    transform: translateY(-25px) rotate(calc(var(--rotate, 0deg) + 8deg));
    opacity: 0.7;
  }
}

/* Hide floating weapons on smaller screens */
@media (max-width: 1024px) {
  .floating-weapons {
    display: none;
  }
}

/* ===== Activity Section ===== */
.activity-section {
  background: rgba(0, 0, 0, 0.2);
}

.sidebar-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1rem;
}

.clans-mini-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.clan-mini-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.clan-mini-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.clan-mini-logo {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.875rem;
  color: white;
}

.clan-mini-info {
  flex: 1;
  min-width: 0;
}

.clan-mini-name {
  display: block;
  font-weight: 600;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.clan-mini-members {
  display: block;
  font-size: 0.75rem;
  color: #94a3b8;
}

.empty-mini {
  padding: 16px;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 10px;
  color: #f97316;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.sidebar-link:hover {
  background: rgba(249, 115, 22, 0.2);
  border-color: rgba(249, 115, 22, 0.4);
  gap: 10px;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quick-stat {
  text-align: center;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
}

.stat-num {
  display: block;
  font-size: 1.25rem;
  font-weight: 800;
  margin-bottom: 4px;
}

.stat-txt {
  display: block;
  font-size: 0.625rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Activity Section Responsive */
@media (max-width: 1024px) {
  .activity-section .grid {
    grid-template-columns: 1fr;
  }

  .activity-section .lg\\:col-span-2 {
    order: 1;
  }
}

/* ===== Forum Showcase Section ===== */
.forum-showcase {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.forum-categories-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (max-width: 768px) {
  .forum-categories-grid {
    grid-template-columns: 1fr;
  }
}

.forum-category-showcase {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  text-decoration: none;
  color: inherit;
}

.forum-category-showcase:hover {
  transform: translateY(-5px) scale(1.02);
  border-color: rgba(255, 255, 255, 0.2);
}

.forum-category-showcase:hover .category-shine {
  transform: translateX(100%);
}

.forum-category-showcase:hover .category-arrow {
  transform: translateX(5px);
  opacity: 1;
}

.forum-category-showcase:hover .category-icon-glow {
  opacity: 0.6;
}

/* Category-specific colors */
.hl-category {
  border-left: 4px solid #f97316;
}

.hl-category:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.4);
}

.hl-category .category-icon-glow {
  background: #f97316;
}

.cs-category {
  border-left: 4px solid #3b82f6;
}

.cs-category:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
}

.cs-category .category-icon-glow {
  background: #3b82f6;
}

.community-category {
  border-left: 4px solid #10b981;
}

.community-category:hover {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.4);
}

.community-category .category-icon-glow {
  background: #10b981;
}

.support-category {
  border-left: 4px solid #8b5cf6;
}

.support-category:hover {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.4);
}

.support-category .category-icon-glow {
  background: #8b5cf6;
}

.category-icon-wrapper {
  position: relative;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  flex-shrink: 0;
}

.category-emoji {
  font-size: 32px;
  z-index: 1;
}

.category-icon-glow {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  opacity: 0;
  filter: blur(20px);
  transition: opacity 0.4s ease;
}

.category-content {
  flex: 1;
  min-width: 0;
}

.category-name {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 4px;
  color: #f8fafc;
}

.category-desc {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 12px;
  line-height: 1.5;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  font-size: 0.75rem;
  color: #cbd5e1;
  transition: all 0.3s ease;
}

.forum-category-showcase:hover .category-tag {
  background: rgba(255, 255, 255, 0.1);
}

.category-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  color: #94a3b8;
  opacity: 0.5;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.category-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  transition: transform 0.6s ease;
  pointer-events: none;
}

.btn-forum-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 32px;
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: none;
  border-radius: 14px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
  transition: all 0.3s ease;
}

.btn-forum-cta:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(249, 115, 22, 0.5);
}

/* Responsive for forum showcase */
@media (max-width: 640px) {
  .forum-category-showcase {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .category-tags {
    justify-content: center;
  }

  .category-arrow {
    display: none;
  }
}

/* ===== Games Showcase Section ===== */
.games-showcase {
  background: linear-gradient(180deg, rgba(15, 15, 26, 0.8) 0%, rgba(24, 24, 28, 0.9) 100%);
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.game-showcase-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: #131a22;
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
}

.game-showcase-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.3);
}

.game-banner-wrapper {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.game-banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.game-showcase-card:hover .game-banner-img {
  transform: scale(1.08);
}

.game-banner-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.game-placeholder-icon {
  font-size: 64px;
  filter: drop-shadow(0 4px 20px rgba(0,0,0,0.5));
}

.game-banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 50%, transparent 100%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 20px;
}

.game-logo-img {
  max-width: 180px;
  max-height: 80px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.8));
}

.game-name-text {
  font-size: 24px;
  font-weight: 700;
  color: white;
  text-shadow: 0 4px 12px rgba(0,0,0,0.8);
}

.game-card-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(0,0,0,0.3);
}

.game-icon-small {
  font-size: 20px;
}

.game-name-small {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.game-arrow {
  color: #94a3b8;
  transition: all 0.3s ease;
}

.game-showcase-card:hover .game-arrow {
  color: #f97316;
  transform: translateX(4px);
}

@media (max-width: 640px) {
  .games-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .game-logo-img {
    max-width: 120px;
    max-height: 50px;
  }

  .game-name-text {
    font-size: 16px;
  }

  .game-card-footer {
    padding: 10px 12px;
  }

  .game-name-small {
    font-size: 12px;
  }
}

/* ===== Forum Topics Showcase Section ===== */
.forum-topics-showcase {
  background: rgba(0, 0, 0, 0.2);
  position: relative;
}

.forum-showcase-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Override section margins for nested components */
.forum-showcase-grid :deep(.popular-topics-section),
.forum-showcase-grid :deep(.recent-topics-section) {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .forum-showcase-grid {
    gap: 12px;
  }
}

/* ============== FORUM MAIN GRID - 60%/40% LAYOUT ============== */

.forum-main-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 16px;
  align-items: start;
}

@media (max-width: 1200px) {
  .forum-main-grid {
    grid-template-columns: 1fr 300px;
    gap: 12px;
  }
}

@media (max-width: 1024px) {
  .forum-main-grid {
    grid-template-columns: 1fr;
  }

  .forum-sidebar {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .forum-sidebar {
    grid-template-columns: 1fr;
  }
}

/* Forum Content Main */
.forum-content-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Forum View All Button */
.forum-view-all {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.forum-view-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
}

.forum-view-all-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
}

.forum-view-all-btn:active {
  transform: translateY(0);
}

/* Forum Sidebar */
.forum-sidebar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: sticky;
  top: 80px;
}

/* Quick Access Card */
.quick-access-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: #f8fafc;
}

.sidebar-card-title svg {
  color: #f97316;
  width: 16px;
  height: 16px;
}

.quick-access-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.quick-btn-primary {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
}

.quick-btn-primary:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
}

.quick-btn-success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
}

.quick-btn-success:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
}

/* Sidebar widgets override */
.forum-sidebar :deep(.online-users-widget),
.forum-sidebar :deep(.compact-servers-widget),
.forum-sidebar :deep(.quick-categories-widget) {
  margin: 0;
}
</style>
