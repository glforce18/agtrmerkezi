<template>
  <div class="home-page min-h-screen overflow-hidden">
    <!-- Subtle Background -->
    <div class="hero-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
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
              <button class="btn-primary-cta text-sm py-2 px-4">
                <MessageSquare class="w-4 h-4" />
                Forum
              </button>
            </router-link>
            <router-link to="/servers">
              <button class="btn-secondary-cta text-sm py-2 px-4">
                <Server class="w-4 h-4" />
                Sunucular
              </button>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section py-4 relative" ref="statsSection">
      <div class="container-main relative z-10">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div
            v-for="(stat, index) in animatedStats"
            :key="stat.label"
            class="stat-card group"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="stat-icon-wrapper">
              <component :is="stat.icon" :style="{ color: stat.color }" class="w-8 h-8" />
              <div class="stat-icon-glow" :style="{ background: stat.color }"></div>
            </div>
            <div class="stat-value">
              <span class="counter">{{ stat.animated }}</span>
              <span class="suffix">{{ stat.suffix }}</span>
            </div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-bar">
              <div class="stat-bar-fill" :style="{ background: stat.color, width: stat.barWidth }"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Servers Section -->
    <section class="servers-section py-20 relative">
      <div class="section-glow section-glow-right"></div>
      <div class="container-main relative z-10">
        <div class="section-header mb-12">
          <div class="section-badge">
            <Zap class="w-4 h-4" />
            <span>Canli</span>
          </div>
          <h2 class="section-title">
            <Server class="section-icon" />
            Popüler Sunucular
          </h2>
          <p class="section-subtitle">Topluluğumuzun en aktif sunucularında oyna</p>
        </div>

        <div class="servers-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="(server, index) in popularServers"
            :key="server.id"
            class="server-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="server-header">
              <div class="server-status" :class="server.online ? 'status-online' : 'status-offline'">
                <span class="status-dot"></span>
                {{ server.online ? 'Çevrimiçi' : 'Çevrimdışı' }}
              </div>
              <n-tag :type="getModeType(server.mode)" size="small" round>
                {{ server.mode }}
              </n-tag>
            </div>

            <div class="server-info">
              <div class="server-icon">
                <Server class="w-6 h-6" />
              </div>
              <div class="server-details">
                <h3 class="server-name">{{ server.name }}</h3>
                <p class="server-map">
                  <MapPin class="w-4 h-4" />
                  {{ server.map }}
                </p>
              </div>
            </div>

            <div class="server-players">
              <div class="players-bar">
                <div
                  class="players-fill"
                  :style="{ width: `${(server.players / server.maxPlayers) * 100}%` }"
                ></div>
              </div>
              <div class="players-info">
                <Users class="w-4 h-4" />
                <span class="players-count">{{ server.players }}</span>
                <span class="players-divider">/</span>
                <span class="players-max">{{ server.maxPlayers }}</span>
              </div>
            </div>

            <div class="server-footer">
              <div class="server-ping">
                <Signal class="w-4 h-4" :class="getPingClass(server.ping)" />
                <span>{{ server.ping }}ms</span>
              </div>
              <n-button size="small" type="primary" @click="connectServer(server)">
                <template #icon><Play class="w-4 h-4" /></template>
                Bağlan
              </n-button>
            </div>
          </div>
        </div>

        <div class="text-center mt-10">
          <router-link to="/servers">
            <n-button size="large" class="view-all-btn">
              Tüm Sunucuları Gör
              <template #icon><ArrowRight class="w-5 h-5" /></template>
            </n-button>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Forum & Leaderboard Split Section -->
    <section class="split-section py-20 relative">
      <div class="container-main relative z-10">
        <div class="grid lg:grid-cols-2 gap-8">
          <!-- Latest Forum Topics -->
          <div class="forum-panel">
            <div class="panel-header">
              <div class="panel-title">
                <MessageSquare class="w-6 h-6 text-orange-500" />
                <h3>Son Forum Konulari</h3>
              </div>
              <router-link to="/forum" class="panel-link">
                Tümünü Gör <ArrowRight class="w-4 h-4" />
              </router-link>
            </div>

            <div class="topics-list">
              <div
                v-for="(topic, index) in latestTopics"
                :key="topic.id"
                class="topic-item"
                :style="{ animationDelay: `${index * 0.05}s` }"
              >
                <div class="topic-avatar">
                  <div class="avatar-ring">
                    {{ topic.author.substring(0, 1).toUpperCase() }}
                  </div>
                </div>
                <div class="topic-content">
                  <h4 class="topic-title">{{ topic.title }}</h4>
                  <div class="topic-meta">
                    <span class="meta-author">{{ topic.author }}</span>
                    <span class="meta-dot"></span>
                    <span class="meta-stats">
                      <MessageCircle class="w-3 h-3" /> {{ topic.replies }}
                    </span>
                    <span class="meta-stats">
                      <Eye class="w-3 h-3" /> {{ topic.views }}
                    </span>
                  </div>
                </div>
                <n-tag :type="getCategoryType(topic.category)" size="small">
                  {{ topic.category }}
                </n-tag>
              </div>
            </div>
          </div>

          <!-- Top Players Leaderboard -->
          <div class="leaderboard-panel">
            <div class="panel-header">
              <div class="panel-title">
                <Trophy class="w-6 h-6 text-yellow-500" />
                <h3>En İyi Oyuncular</h3>
              </div>
              <router-link to="/leaderboard" class="panel-link">
                Tüm Sıralama <ArrowRight class="w-4 h-4" />
              </router-link>
            </div>

            <div class="leaderboard-list">
              <div
                v-for="(player, index) in topPlayers"
                :key="player.id"
                class="player-item"
                :class="`rank-${index + 1}`"
              >
                <div class="player-rank">
                  <div class="rank-badge" :class="`rank-${index + 1}`">
                    <Crown v-if="index === 0" class="w-4 h-4" />
                    <Medal v-else-if="index === 1" class="w-4 h-4" />
                    <Award v-else-if="index === 2" class="w-4 h-4" />
                    <span v-else>{{ index + 1 }}</span>
                  </div>
                </div>
                <div class="player-avatar">
                  <n-avatar :size="48" round :style="{ background: getPlayerGradient(index) }">
                    {{ player.name.substring(0, 2).toUpperCase() }}
                  </n-avatar>
                  <div class="player-level">{{ player.level }}</div>
                </div>
                <div class="player-info">
                  <h4 class="player-name">{{ player.name }}</h4>
                  <p class="player-title">{{ player.title }}</p>
                </div>
                <div class="player-stats">
                  <div class="stat-item">
                    <span class="stat-value-small text-green-500">{{ formatNumber(player.kills) }}</span>
                    <span class="stat-label-small">Kills</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value-small text-orange-500">{{ player.kd }}</span>
                    <span class="stat-label-small">K/D</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Active Tournaments Section -->
    <section class="tournaments-section py-20 relative">
      <div class="section-glow section-glow-left"></div>
      <div class="container-main relative z-10">
        <div class="section-header mb-12 text-center">
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

        <div class="tournaments-grid grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
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
                <span class="prize-label">Odul</span>
              </div>

              <div class="tournament-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: `${(event.participants / event.maxParticipants) * 100}%` }"></div>
                </div>
                <span class="progress-text">{{ event.participants }}/{{ event.maxParticipants }} kayıt</span>
              </div>
            </div>

            <div class="tournament-actions">
              <n-button type="primary" block>
                <template #icon><Zap class="w-4 h-4" /></template>
                Hemen Katıl
              </n-button>
            </div>

            <div class="tournament-glow"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Community Highlights -->
    <section class="community-section py-20 relative">
      <div class="container-main relative z-10">
        <div class="section-header mb-12 text-center">
          <div class="section-badge mx-auto">
            <Sparkles class="w-4 h-4" />
            <span>Topluluk</span>
          </div>
          <h2 class="section-title justify-center">
            <Heart class="section-icon" />
            Topluluk Vurgulari
          </h2>
          <p class="section-subtitle">Toplulugumuzdaki en son gelismeler</p>
        </div>

        <div class="highlights-grid grid md:grid-cols-3 gap-6">
          <div
            v-for="(highlight, index) in communityHighlights"
            :key="index"
            class="highlight-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="highlight-icon" :style="{ background: highlight.gradient }">
              <component :is="highlight.icon" class="w-6 h-6 text-white" />
            </div>
            <h3 class="highlight-title">{{ highlight.title }}</h3>
            <p class="highlight-desc">{{ highlight.description }}</p>
            <div class="highlight-stat">
              <span class="stat-number">{{ highlight.stat }}</span>
              <span class="stat-text">{{ highlight.statLabel }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA Section -->
    <section class="cta-section py-24 relative">
      <div class="cta-background">
        <div class="cta-gradient"></div>
        <div class="cta-pattern"></div>
      </div>
      <div class="container-main relative z-10 text-center">
        <h2 class="cta-title mb-6">
          Toplulugumuza <span class="text-gradient">Katıl</span>
        </h2>
        <p class="cta-description mb-10 max-w-2xl mx-auto">
          Binlerce CS 1.6 oyuncusuyla tanışmayı, turnuvalara katılmayi ve
          en iyi sunucularda oynamayı mı bekliyorsun? Hemen ücretsiz kayıt ol!
        </p>
        <div class="cta-buttons-final flex flex-wrap justify-center gap-6">
          <router-link to="/register">
            <button class="btn-primary-cta">
              <UserPlus class="w-6 h-6" />
              Ücretsiz Kayıt Ol
            </button>
          </router-link>
          <a :href="discordUrl" target="_blank" rel="noopener">
            <button class="btn-discord">
              <MessageCircle class="w-5 h-5" />
              Discord'a Katıl
            </button>
          </a>
        </div>

        <!-- Social Proof -->
        <div class="social-proof mt-16">
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
import { useThemeStore } from '@/stores/theme'
import { useSettingsStore } from '@/stores/settings'
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
  Activity
} from 'lucide-vue-next'

const themeStore = useThemeStore()
const settingsStore = useSettingsStore()
const isDark = computed(() => themeStore.isDark)

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
  'Counter-Strike 1.6 Turkiye Toplulugu',
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
const latestTopics = ref([
  { id: 1, title: 'CS 1.6 En İyi Ayarlar 2024', author: 'ProGamer', replies: 47, views: 1230, category: 'Rehberler' },
  { id: 2, title: 'Yeni Aim Map Koleksiyonu', author: 'MapMaker', replies: 23, views: 856, category: 'Maplar' },
  { id: 3, title: 'Turnuva Kayıtları Başladı!', author: 'Admin159', replies: 89, views: 2341, category: 'Duyurular' },
  { id: 4, title: 'En İyi AWP Taktikleri', author: 'Sniper', replies: 34, views: 945, category: 'Taktikler' },
  { id: 5, title: 'Yeni Başlayanlara CS 1.6 Rehberi', author: 'Mentor', replies: 56, views: 1567, category: 'Rehberler' }
])

const topPlayers = ref([
  { id: 1, name: 'ShadowKiller', title: 'Legendary Player', kills: 15234, deaths: 4521, kd: 3.37, level: 87 },
  { id: 2, name: 'HeadHunter', title: 'Elite Sniper', kills: 13890, deaths: 5123, kd: 2.71, level: 79 },
  { id: 3, name: 'FastFingers', title: 'Pro Rifler', kills: 12456, deaths: 5789, kd: 2.15, level: 73 },
  { id: 4, name: 'NightOwl', title: 'Tactical Master', kills: 11234, deaths: 6012, kd: 1.87, level: 68 },
  { id: 5, name: 'StormBreaker', title: 'Rising Star', kills: 10567, deaths: 6234, kd: 1.70, level: 62 }
])

const popularServers = ref([
  { id: 1, name: 'AGTR Public #1', map: 'de_dust2', players: 28, maxPlayers: 32, mode: 'Public', ping: 12, country: 'TR', online: true },
  { id: 2, name: 'Deathmatch Arena', map: 'de_inferno', players: 24, maxPlayers: 24, mode: 'DM', ping: 8, country: 'TR', online: true },
  { id: 3, name: 'Zombie Escape', map: 'zm_dust', players: 31, maxPlayers: 32, mode: 'Zombie', ping: 15, country: 'TR', online: true },
  { id: 4, name: 'AWP Only Server', map: 'awp_india', players: 18, maxPlayers: 20, mode: 'AWP', ping: 10, country: 'TR', online: true },
  { id: 5, name: 'Surf Paradise', map: 'surf_ski2', players: 14, maxPlayers: 24, mode: 'Surf', ping: 18, country: 'TR', online: true },
  { id: 6, name: 'Competitive 5v5', map: 'de_nuke', players: 10, maxPlayers: 10, mode: '5v5', ping: 5, country: 'TR', online: true }
])

const activeEvents = ref([
  {
    id: 1,
    title: '5v5 CS 1.6 Sampiyonasi',
    description: 'Aylık şampiyonluk turnuvası. En iyi takımlar karşı karşıya!',
    date: '25 Ocak 2024',
    participants: 12,
    maxParticipants: 16,
    prize: '500 TL'
  },
  {
    id: 2,
    title: 'AWP Only Kupasi',
    description: 'Sadece AWP kullanarak yeteneklerini göster. En iyi sniper kim?',
    date: '28 Ocak 2024',
    participants: 28,
    maxParticipants: 32,
    prize: '250 TL'
  }
])

const communityHighlights = ref([
  {
    icon: markRaw(Star),
    title: 'Haftanin Oyuncusu',
    description: 'ShadowKiller bu hafta 1500+ kill ile zirvede!',
    stat: '1,523',
    statLabel: 'kills',
    gradient: 'linear-gradient(135deg, #f97316, #ea580c)'
  },
  {
    icon: markRaw(TrendingUp),
    title: 'En Aktif Forum',
    description: 'Strateji bölümü bu hafta en çok ziyaret edilen forum.',
    stat: '2.3K',
    statLabel: 'mesaj',
    gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
  },
  {
    icon: markRaw(Activity),
    title: 'Sunucu Rekoru',
    description: 'AGTR Public #1 yeni oyuncu rekoru kirdi!',
    stat: '32/32',
    statLabel: 'oyuncu',
    gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)'
  }
])

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
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out both;
}

.server-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(249, 115, 22, 0.3);
  transform: translateY(-5px);
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
</style>
