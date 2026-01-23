<template>
  <div class="forum-page">
    <!-- Animated Background -->
    <div class="forum-bg">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-particles">
        <div v-for="n in 20" :key="n" class="particle" :style="getParticleStyle(n)"></div>
      </div>
      <div class="bg-glow bg-glow--orange"></div>
      <div class="bg-glow bg-glow--purple"></div>
    </div>

    <div class="forum-container">
      <!-- Epic Hero Section -->
      <header class="forum-hero">
        <div class="hero-content">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            <span>{{ stats.onlineUsers }} Oyuncu Cevrimici</span>
          </div>

          <h1 class="hero-title">
            <span class="title-line">AGTR</span>
            <span class="title-line title-line--accent">MERKEZI</span>
          </h1>

          <p class="hero-subtitle">Turkiye'nin En Buyuk CS 1.6 & Half-Life Toplulugu</p>

          <!-- Animated Stats -->
          <div class="hero-stats">
            <div class="stat-card">
              <div class="stat-icon">
                <FileTextIcon class="w-6 h-6" />
              </div>
              <div class="stat-content">
                <span class="stat-number">{{ animatedStats.topics }}</span>
                <span class="stat-label">Konu</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <MessageSquareIcon class="w-6 h-6" />
              </div>
              <div class="stat-content">
                <span class="stat-number">{{ animatedStats.posts }}</span>
                <span class="stat-label">Gonderi</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <UsersIcon class="w-6 h-6" />
              </div>
              <div class="stat-content">
                <span class="stat-number">{{ animatedStats.members }}</span>
                <span class="stat-label">Uye</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Game Icons -->
        <div class="hero-floating">
          <img v-if="gameAssets.cs16?.icon" :src="gameAssets.cs16.icon" class="floating-icon floating-icon--1" alt="" />
          <img v-if="gameAssets.halflife?.icon" :src="gameAssets.halflife.icon" class="floating-icon floating-icon--2" alt="" />
        </div>
      </header>

      <!-- Quick Actions -->
      <div class="forum-actions">
        <button class="btn-primary btn-glow" @click="handleNewTopic" :disabled="!isLoggedIn">
          <PlusIcon class="w-5 h-5" />
          <span>{{ isLoggedIn ? 'Yeni Konu Ac' : 'Giris Yap' }}</span>
        </button>

        <div class="search-box">
          <SearchIcon class="search-icon w-5 h-5" />
          <input v-model="searchQuery" type="text" placeholder="Konu veya kullanici ara..." @input="performSearch" />
          <kbd class="search-kbd">/</kbd>
        </div>

        <div class="action-filters">
          <button
            v-for="filter in filters"
            :key="filter.id"
            :class="['filter-btn', { active: activeFilter === filter.id }]"
            @click="activeFilter = filter.id"
          >
            <component :is="filter.icon" class="w-4 h-4" />
            {{ filter.label }}
          </button>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="forum-grid">
        <!-- Games Column -->
        <div class="games-column">
          <!-- CS 1.6 Section -->
          <section class="game-section">
            <div class="game-card game-card--cs16">
              <div class="game-card__bg" :style="{ backgroundImage: gameAssets.cs16?.hero ? `url(${gameAssets.cs16.hero})` : 'none' }"></div>
              <div class="game-card__overlay"></div>
              <div class="game-card__content">
                <div class="game-card__header">
                  <img v-if="gameAssets.cs16?.logo" :src="gameAssets.cs16.logo" class="game-logo" alt="Counter-Strike 1.6" />
                  <div v-else class="game-title">
                    <TargetIcon class="w-8 h-8" />
                    <span>Counter-Strike 1.6</span>
                  </div>
                  <div class="game-badge">
                    <span class="badge-count">{{ cs16Categories.length }}</span>
                    Kategori
                  </div>
                </div>
                <p class="game-desc">Sunucu ilanlari, AMX Mod X, plugin paylasimi, turnuvalar</p>
              </div>

              <!-- Categories -->
              <div class="game-categories">
                <router-link
                  v-for="cat in cs16Categories"
                  :key="cat.id"
                  :to="`/forum/category/${cat.slug || cat.id}`"
                  class="category-item"
                >
                  <div class="category-icon" :style="{ background: cat.color || 'var(--orange)' }">
                    <span v-if="cat.emoji">{{ cat.emoji }}</span>
                    <FolderIcon v-else class="w-5 h-5" />
                  </div>
                  <div class="category-info">
                    <h4>{{ cat.name }}</h4>
                    <div class="category-meta">
                      <span><FileTextIcon class="w-3 h-3" /> {{ cat.topics || 0 }}</span>
                      <span><MessageSquareIcon class="w-3 h-3" /> {{ cat.posts || 0 }}</span>
                    </div>
                  </div>
                  <ChevronRightIcon class="category-arrow w-5 h-5" />
                </router-link>

                <div v-if="cs16Categories.length === 0" class="empty-state">
                  Henuz kategori yok
                </div>
              </div>
            </div>
          </section>

          <!-- Half-Life Section -->
          <section class="game-section">
            <div class="game-card game-card--halflife">
              <div class="game-card__bg" :style="{ backgroundImage: gameAssets.halflife?.hero ? `url(${gameAssets.halflife.hero})` : 'none' }"></div>
              <div class="game-card__overlay game-card__overlay--hl"></div>
              <div class="game-card__content">
                <div class="game-card__header">
                  <img v-if="gameAssets.halflife?.logo" :src="gameAssets.halflife.logo" class="game-logo" alt="Half-Life" />
                  <div v-else class="game-title">
                    <Gamepad2Icon class="w-8 h-8" />
                    <span>Half-Life & AG</span>
                  </div>
                  <div class="game-badge game-badge--hl">
                    <span class="badge-count">{{ halflifeCategories.length }}</span>
                    Kategori
                  </div>
                </div>
                <p class="game-desc">Adrenaline Gamer, turnuvalar, modlar ve topluluk</p>
              </div>

              <div class="game-categories">
                <router-link
                  v-for="cat in halflifeCategories"
                  :key="cat.id"
                  :to="`/forum/category/${cat.slug || cat.id}`"
                  class="category-item"
                >
                  <div class="category-icon" :style="{ background: cat.color || 'var(--amber)' }">
                    <span v-if="cat.emoji">{{ cat.emoji }}</span>
                    <FolderIcon v-else class="w-5 h-5" />
                  </div>
                  <div class="category-info">
                    <h4>{{ cat.name }}</h4>
                    <div class="category-meta">
                      <span><FileTextIcon class="w-3 h-3" /> {{ cat.topics || 0 }}</span>
                      <span><MessageSquareIcon class="w-3 h-3" /> {{ cat.posts || 0 }}</span>
                    </div>
                  </div>
                  <ChevronRightIcon class="category-arrow w-5 h-5" />
                </router-link>

                <div v-if="halflifeCategories.length === 0" class="empty-state">
                  Henuz kategori yok
                </div>
              </div>
            </div>
          </section>

          <!-- Community Section -->
          <section class="game-section">
            <div class="game-card game-card--community">
              <div class="game-card__content game-card__content--simple">
                <div class="game-card__header">
                  <div class="game-title game-title--community">
                    <UsersIcon class="w-8 h-8" />
                    <span>Topluluk</span>
                  </div>
                  <div class="game-badge game-badge--purple">
                    <span class="badge-count">{{ communityCategories.length }}</span>
                    Kategori
                  </div>
                </div>
                <p class="game-desc">Genel sohbet, duyurular, destek ve etkinlikler</p>
              </div>

              <div class="game-categories">
                <router-link
                  v-for="cat in communityCategories"
                  :key="cat.id"
                  :to="`/forum/category/${cat.slug || cat.id}`"
                  class="category-item"
                >
                  <div class="category-icon" :style="{ background: cat.color || 'var(--purple)' }">
                    <span v-if="cat.emoji">{{ cat.emoji }}</span>
                    <FolderIcon v-else class="w-5 h-5" />
                  </div>
                  <div class="category-info">
                    <h4>{{ cat.name }}</h4>
                    <div class="category-meta">
                      <span><FileTextIcon class="w-3 h-3" /> {{ cat.topics || 0 }}</span>
                      <span><MessageSquareIcon class="w-3 h-3" /> {{ cat.posts || 0 }}</span>
                    </div>
                  </div>
                  <ChevronRightIcon class="category-arrow w-5 h-5" />
                </router-link>
              </div>
            </div>
          </section>
        </div>

        <!-- Sidebar -->
        <aside class="forum-sidebar">
          <!-- Hot Topics -->
          <div class="sidebar-card">
            <div class="sidebar-header">
              <FlameIcon class="w-5 h-5 text-orange-500" />
              <h3>Populer Konular</h3>
            </div>
            <div class="hot-topics">
              <router-link
                v-for="(topic, index) in hotTopics"
                :key="topic.id"
                :to="`/forum/topic/${topic.id}`"
                class="hot-topic"
              >
                <span class="hot-rank">#{{ index + 1 }}</span>
                <div class="hot-info">
                  <span class="hot-title">{{ topic.title }}</span>
                  <span class="hot-meta">
                    <MessageSquareIcon class="w-3 h-3" /> {{ topic.replies }}
                  </span>
                </div>
              </router-link>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="sidebar-card">
            <div class="sidebar-header">
              <ActivityIcon class="w-5 h-5 text-cyan-500" />
              <h3>Son Aktivite</h3>
            </div>
            <div class="activity-feed">
              <div v-for="n in 5" :key="n" class="activity-item">
                <div class="activity-avatar"></div>
                <div class="activity-content">
                  <span class="activity-user">Kullanici{{ n }}</span>
                  <span class="activity-action">yeni konu acti</span>
                </div>
                <span class="activity-time">{{ n }}dk</span>
              </div>
            </div>
          </div>

          <!-- Game Showcase -->
          <div class="sidebar-card sidebar-card--showcase">
            <div class="sidebar-header">
              <SparklesIcon class="w-5 h-5 text-yellow-500" />
              <h3>Oyun Vitrin</h3>
            </div>
            <div class="showcase-grid">
              <div class="showcase-item" v-if="gameAssets.cs16?.grid">
                <img :src="gameAssets.cs16.grid" alt="CS 1.6" />
                <span>CS 1.6</span>
              </div>
              <div class="showcase-item" v-if="gameAssets.halflife?.grid">
                <img :src="gameAssets.halflife.grid" alt="Half-Life" />
                <span>Half-Life</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- New Topic Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showNewTopicModal" class="modal-overlay" @click.self="showNewTopicModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h2><PlusIcon class="w-5 h-5" /> Yeni Konu Olustur</h2>
              <button @click="showNewTopicModal = false" class="modal-close">
                <XIcon class="w-6 h-6" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Kategori</label>
                <select v-model="newTopic.categoryId">
                  <option value="">Kategori secin...</option>
                  <optgroup label="Counter-Strike 1.6">
                    <option v-for="cat in cs16Categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </optgroup>
                  <optgroup label="Half-Life & AG">
                    <option v-for="cat in halflifeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </optgroup>
                  <optgroup label="Topluluk">
                    <option v-for="cat in communityCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </optgroup>
                </select>
              </div>
              <div class="form-group">
                <label>Baslik</label>
                <input v-model="newTopic.title" type="text" placeholder="Konu basligi..." maxlength="100" />
              </div>
              <div class="form-group">
                <label>Icerik</label>
                <textarea v-model="newTopic.content" placeholder="Konu icerigi..." rows="6"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button @click="showNewTopicModal = false" class="btn-secondary">Iptal</button>
              <button @click="createTopic" class="btn-primary" :disabled="!isTopicValid || isSubmitting">
                {{ isSubmitting ? 'Gonderiliyor...' : 'Olustur' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Steam Required Modal -->
    <SteamRequiredModal :show="showSteamModal" @close="closeModal" @connect="connectSteam" />

    <!-- Back to Top Button -->
    <Transition name="fade">
      <button v-if="showBackToTop" class="back-to-top" @click="scrollToTop" title="Yukarı Çık (T)">
        <ChevronUpIcon class="w-6 h-6" />
      </button>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import { forumAPI } from '@/api'
import { useRequireSteam } from '@/composables/useRequireSteam'
import { useGameAssets } from '@/composables/useGameAssets'
import { debounce } from '@/composables/useDebounce'
import {
  SearchIcon, PlusIcon, FileTextIcon, MessageSquareIcon, UsersIcon,
  FlameIcon, FolderIcon, ChevronRightIcon, XIcon, TargetIcon,
  Gamepad2Icon, TrendingUpIcon, ClockIcon, ActivityIcon, SparklesIcon,
  ChevronUpIcon
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const { hasSteam, showSteamModal, requireSteam, connectSteam, closeModal } = useRequireSteam()
const { getGameAssets } = useGameAssets()

// State
const isLoading = ref(true)
const isSubmitting = ref(false)
const searchQuery = ref('')
const showNewTopicModal = ref(false)
const activeFilter = ref('all')
const categories = ref([])
const hotTopics = ref([])
const showBackToTop = ref(false)

// Scroll handler
const handleScroll = () => {
  showBackToTop.value = window.scrollY > 400
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const stats = reactive({ totalTopics: 0, totalPosts: 0, totalMembers: 0, onlineUsers: 0 })
const animatedStats = reactive({ topics: 0, posts: 0, members: 0 })
const gameAssets = reactive({
  cs16: { hero: null, logo: null, icon: null, grid: null },
  halflife: { hero: null, logo: null, icon: null, grid: null }
})
const newTopic = reactive({ categoryId: '', title: '', content: '' })

const filters = [
  { id: 'all', label: 'Tumu', icon: FolderIcon },
  { id: 'trending', label: 'Trend', icon: TrendingUpIcon },
  { id: 'recent', label: 'Yeni', icon: ClockIcon }
]

// Computed
const isLoggedIn = computed(() => !!authStore.user)
const isTopicValid = computed(() => newTopic.categoryId && newTopic.title.length >= 5 && newTopic.content.length >= 20)

// Filter categories by game_slug (from API) with fallback to keywords
const cs16Keywords = ['cs16', 'cs-', 'counter-strike', 'amxmodx', 'hlds']
const hlKeywords = ['halflife', 'half-life', 'ag-', 'adrenaline', 'hl-']

const cs16Categories = computed(() => categories.value.filter(cat => {
  // Priority: use game_slug from API
  if (cat.game_slug === 'cs16') return true
  // Fallback: keyword matching
  const slug = (cat.slug || '').toLowerCase()
  const name = (cat.name || '').toLowerCase()
  return cs16Keywords.some(kw => slug.includes(kw) || name.includes(kw))
}))

const halflifeCategories = computed(() => categories.value.filter(cat => {
  // Priority: use game_slug from API
  if (cat.game_slug === 'halflife') return true
  // Fallback: keyword matching
  const slug = (cat.slug || '').toLowerCase()
  const name = (cat.name || '').toLowerCase()
  return hlKeywords.some(kw => slug.includes(kw) || name.includes(kw))
}))

const communityCategories = computed(() => categories.value.filter(cat => {
  // Categories without game_slug and not matching game keywords
  if (cat.game_slug) return false
  const slug = (cat.slug || '').toLowerCase()
  const name = (cat.name || '').toLowerCase()
  return !cs16Keywords.some(kw => slug.includes(kw) || name.includes(kw)) &&
         !hlKeywords.some(kw => slug.includes(kw) || name.includes(kw))
}))

// Particle style generator
const getParticleStyle = (n) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  animationDelay: `${Math.random() * 5}s`,
  animationDuration: `${3 + Math.random() * 4}s`
})

// Animate stats
const animateStats = () => {
  const duration = 1500
  const steps = 30
  const interval = duration / steps

  let step = 0
  const timer = setInterval(() => {
    step++
    const progress = step / steps
    animatedStats.topics = Math.floor(stats.totalTopics * progress)
    animatedStats.posts = Math.floor(stats.totalPosts * progress)
    animatedStats.members = Math.floor(stats.totalMembers * progress)

    if (step >= steps) clearInterval(timer)
  }, interval)
}

// Methods
const fetchCategories = async () => {
  try {
    const response = await forumAPI.getCategories()
    const data = response?.categories || response || []
    if (Array.isArray(data)) {
      categories.value = data.map(cat => ({
        id: cat.id,
        name: cat.name,
        slug: cat.slug || cat.name?.toLowerCase().replace(/\s+/g, '-'),
        description: cat.description || '',
        emoji: cat.icon,
        color: cat.color,
        game_slug: cat.game_slug,  // Include game_slug from API
        topics: cat.topic_count || 0,
        posts: cat.post_count || 0,
        parent_id: cat.parent_id
      }))
    }
  } catch (error) { console.error('Categories error:', error) }
}

const fetchHotTopics = async () => {
  try {
    const response = await forumAPI.getAllTopics({ sort: 'popular', limit: 5 })
    const data = response?.topics || response || []
    hotTopics.value = data.map(t => ({ id: t.id, title: t.title, replies: t.reply_count || 0 }))
  } catch (error) { console.error('Hot topics error:', error) }
}

const fetchStats = async () => {
  try {
    const response = await forumAPI.getStats()
    stats.totalTopics = response?.total_topics || 0
    stats.totalPosts = response?.total_posts || 0
    stats.totalMembers = response?.total_members || 0
    stats.onlineUsers = response?.online_users || 0
    animateStats()
  } catch (error) { console.error('Stats error:', error) }
}

const loadGameAssets = async () => {
  try {
    for (const game of ['cs16', 'halflife']) {
      const data = await getGameAssets(game, null, 10)
      if (data?.length) {
        data.forEach(a => {
          if (gameAssets[game]) gameAssets[game][a.asset_type] = a.file_path
        })
      }
    }
  } catch (error) { console.error('Game assets error:', error) }
}

const handleNewTopic = () => {
  if (!isLoggedIn.value) { router.push('/login'); return }
  requireSteam(() => { showNewTopicModal.value = true })
}

const createTopic = async () => {
  if (!isTopicValid.value) return
  isSubmitting.value = true
  try {
    const response = await forumAPI.createTopic({
      category_id: newTopic.categoryId,
      title: newTopic.title.trim(),
      content: newTopic.content.trim()
    })
    showNewTopicModal.value = false
    newTopic.categoryId = ''; newTopic.title = ''; newTopic.content = ''
    const topicId = response?.id || response?.topic?.id
    if (topicId) router.push(`/forum/topic/${topicId}`)
  } catch (error) {
    console.error('Create topic error:', error)
    alert(error.response?.data?.detail || 'Konu olusturulamadi')
  } finally { isSubmitting.value = false }
}

const performSearch = debounce(() => {
  if (searchQuery.value.length >= 2) router.push({ path: '/forum', query: { q: searchQuery.value } })
}, 500)

// Keyboard shortcut
const handleKeydown = (e) => {
  if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return

  if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
    e.preventDefault()
    document.querySelector('.search-box input')?.focus()
  }
  // T tuşu - Yukarı çık
  if (e.key === 't' || e.key === 'T') {
    scrollToTop()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('scroll', handleScroll)
  isLoading.value = true
  await Promise.all([fetchCategories(), fetchHotTopics(), fetchStats(), loadGameAssets()])
  isLoading.value = false
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('scroll', handleScroll)
  // BUGFIX: Clear any pending search debounce timer
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
})
</script>

<style scoped>
/* CSS Variables */
:root {
  --orange: #f97316;
  --amber: #f59e0b;
  --purple: #8b5cf6;
  --cyan: #22d3ee;
}

/* Base */
.forum-page {
  min-height: 100vh;
  background: #050508;
  position: relative;
  overflow-x: hidden;
}

/* Animated Background */
.forum-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(249, 115, 22, 0.15), transparent),
              radial-gradient(ellipse 60% 40% at 100% 100%, rgba(139, 92, 246, 0.1), transparent);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 60% at 50% 0%, black, transparent);
}

.bg-particles {
  position: absolute;
  inset: 0;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(249, 115, 22, 0.6);
  border-radius: 50%;
  animation: float 5s ease-in-out infinite;
}

.particle:nth-child(even) {
  background: rgba(139, 92, 246, 0.6);
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.6; }
  50% { transform: translateY(-30px) scale(1.2); opacity: 1; }
}

.bg-glow {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.4;
  animation: pulse-glow 8s ease-in-out infinite;
}

.bg-glow--orange {
  top: -200px;
  left: -100px;
  background: #f97316;
}

.bg-glow--purple {
  bottom: -200px;
  right: -100px;
  background: #8b5cf6;
  animation-delay: 4s;
}

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.1); opacity: 0.5; }
}

/* Container */
.forum-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  position: relative;
  z-index: 1;
}

/* Hero Section */
.forum-hero {
  position: relative;
  padding: 60px 40px;
  margin-bottom: 32px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 24px;
  overflow: hidden;
}

.forum-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.03;
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 50px;
  color: #22c55e;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 24px;
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.hero-title {
  font-size: 64px;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 16px;
  letter-spacing: -0.03em;
}

.title-line {
  display: block;
  color: #fff;
}

.title-line--accent {
  background: linear-gradient(135deg, #f97316, #f59e0b, #22d3ee);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 18px;
  color: rgba(255,255,255,0.6);
  margin-bottom: 40px;
}

/* Stats */
.hero-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 28px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(249, 115, 22, 0.3);
  transform: translateY(-4px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(139, 92, 246, 0.2));
  border-radius: 12px;
  color: #f97316;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Floating Icons */
.hero-floating {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.floating-icon {
  position: absolute;
  width: 60px;
  height: 60px;
  opacity: 0.15;
  animation: float-icon 6s ease-in-out infinite;
}

.floating-icon--1 { top: 20%; left: 10%; animation-delay: 0s; }
.floating-icon--2 { bottom: 20%; right: 10%; animation-delay: 3s; }

@keyframes float-icon {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

/* Actions - Sticky */
.forum-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 32px;
  position: sticky;
  top: 70px;
  z-index: 100;
  background: rgba(11, 15, 20, 0.95);
  backdrop-filter: blur(10px);
  padding: 16px;
  margin-left: -16px;
  margin-right: -16px;
  padding-left: 16px;
  padding-right: 16px;
  border-radius: 12px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(249, 115, 22, 0.4);
}

.btn-glow {
  position: relative;
}

.btn-glow::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, #f97316, #8b5cf6);
  border-radius: 14px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s;
}

.btn-glow:hover::before { opacity: 1; }

.search-box {
  flex: 1;
  max-width: 400px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  transition: all 0.3s;
}

.search-box input:focus {
  outline: none;
  background: rgba(255,255,255,0.08);
  border-color: #f97316;
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.1);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255,255,255,0.4);
}

.search-kbd {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  padding: 4px 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 6px;
  font-size: 12px;
  color: rgba(255,255,255,0.4);
}

.action-filters {
  display: flex;
  gap: 8px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: rgba(255,255,255,0.6);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover, .filter-btn.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

/* Grid Layout */
.forum-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
}

@media (max-width: 1024px) {
  .forum-grid { grid-template-columns: 1fr; }
  .forum-sidebar { display: none; }
}

/* Game Cards */
.games-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.game-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.4s ease;
}

.game-card:hover {
  border-color: rgba(255,255,255,0.15);
  transform: translateY(-4px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}

.game-card__bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transition: transform 0.6s ease;
}

.game-card:hover .game-card__bg {
  transform: scale(1.05);
}

.game-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.85), rgba(234, 88, 12, 0.7));
}

.game-card__overlay--hl {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.85), rgba(217, 119, 6, 0.7));
}

.game-card--community .game-card__overlay {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(124, 58, 237, 0.2));
}

.game-card__content {
  position: relative;
  z-index: 1;
  padding: 32px;
}

.game-card__content--simple {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(124, 58, 237, 0.1));
}

.game-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.game-logo {
  height: 50px;
  max-width: 180px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.5));
}

.game-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
  font-size: 24px;
  font-weight: 700;
}

.game-title--community {
  color: #a78bfa;
}

.game-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  border-radius: 50px;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
}

.badge-count {
  font-weight: 700;
  font-size: 16px;
}

.game-desc {
  color: rgba(255,255,255,0.8);
  font-size: 14px;
  margin: 0;
}

/* Categories */
.game-categories {
  position: relative;
  z-index: 1;
  padding: 8px;
  background: rgba(0,0,0,0.2);
}

.category-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s;
}

.category-item:hover {
  background: rgba(255,255,255,0.08);
}

.category-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.category-item:hover .category-icon {
  transform: scale(1.1) rotate(5deg);
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-info h4 {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px 0;
}

.category-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}

.category-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.category-arrow {
  color: rgba(255,255,255,0.3);
  transition: all 0.2s;
}

.category-item:hover .category-arrow {
  color: #f97316;
  transform: translateX(4px);
}

.empty-state {
  padding: 32px;
  text-align: center;
  color: rgba(255,255,255,0.4);
}

/* Sidebar */
.forum-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.sidebar-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

/* Hot Topics */
.hot-topics {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hot-topic {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s;
}

.hot-topic:hover {
  background: rgba(255,255,255,0.06);
  transform: translateX(4px);
}

.hot-rank {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 8px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.hot-info {
  flex: 1;
  min-width: 0;
}

.hot-title {
  display: block;
  font-size: 13px;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.hot-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(255,255,255,0.4);
}

/* Activity Feed */
.activity-feed {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.activity-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #f97316, #8b5cf6);
  border-radius: 50%;
}

.activity-content {
  flex: 1;
  font-size: 13px;
}

.activity-user {
  color: #fff;
  font-weight: 500;
}

.activity-action {
  color: rgba(255,255,255,0.5);
  margin-left: 4px;
}

.activity-time {
  font-size: 11px;
  color: rgba(255,255,255,0.3);
}

/* Showcase */
.showcase-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.showcase-item {
  position: relative;
  aspect-ratio: 2/3;
  border-radius: 12px;
  overflow: hidden;
}

.showcase-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.showcase-item:hover img {
  transform: scale(1.1);
}

.showcase-item span {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-content {
  width: 100%;
  max-width: 560px;
  background: #111;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.modal-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  padding: 4px;
  transition: color 0.2s;
}

.modal-close:hover { color: #fff; }

.modal-body { padding: 24px; }

.form-group { margin-bottom: 20px; }

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255,255,255,0.7);
  margin-bottom: 8px;
}

.form-group select,
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  transition: all 0.2s;
}

.form-group select:focus,
.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f97316;
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.1);
}

.form-group textarea { resize: vertical; min-height: 120px; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.btn-secondary {
  padding: 12px 24px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: rgba(255,255,255,0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover { background: rgba(255,255,255,0.1); }

/* Modal Transition */
.modal-enter-active, .modal-leave-active { transition: all 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-content, .modal-leave-to .modal-content { transform: scale(0.95) translateY(20px); }

/* Back to Top Button */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
  z-index: 1000;
  transition: all 0.3s ease;
}

.back-to-top:hover {
  transform: translateY(-4px) scale(1.1);
  box-shadow: 0 8px 30px rgba(249, 115, 22, 0.6);
}

/* Fade Transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Responsive */
@media (max-width: 768px) {
  .forum-container { padding: 16px; }
  .forum-hero { padding: 40px 20px; }
  .hero-title { font-size: 40px; }
  .hero-stats { gap: 12px; }
  .stat-card { padding: 16px 20px; }
  .forum-actions { flex-direction: column; align-items: stretch; }
  .search-box { max-width: none; }
  .action-filters { justify-content: center; }
  .game-card__content { padding: 24px; }
  .back-to-top { bottom: 20px; right: 20px; width: 45px; height: 45px; }
}
</style>
