<template>
  <div class="forum-page">
    <!-- Scroll Progress -->
    <ScrollProgress />

    <!-- Keyboard Shortcuts -->
    <KeyboardShortcuts />

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
      <!-- Minimal Stats Bar -->
      <header class="forum-stats-bar">
        <div class="stats-bar-left">
          <span class="stats-bar-title">AGTR Forum</span>
          <span class="stats-bar-divider">|</span>
          <span class="stats-bar-online">
            <span class="online-dot"></span>
            {{ stats.onlineUsers }} çevrimiçi
          </span>
        </div>
        <div class="stats-bar-right">
          <span class="stats-bar-item">
            <FileTextIcon class="w-3 h-3" />
            {{ animatedStats.topics }} konu
          </span>
          <span class="stats-bar-item">
            <MessageSquareIcon class="w-3 h-3" />
            {{ animatedStats.posts }} gönderi
          </span>
          <span class="stats-bar-item">
            <UsersIcon class="w-3 h-3" />
            {{ animatedStats.members }} üye
          </span>
        </div>
      </header>

      <!-- Quick Actions -->
      <div class="forum-actions">
        <button class="btn-primary btn-glow" @click="handleNewTopic" :disabled="!isLoggedIn || !hasSteam">
          <PlusIcon class="w-5 h-5" />
          <span>{{ !isLoggedIn ? 'Giris Yap' : (!hasSteam ? 'Steam Bagla' : 'Yeni Konu Ac') }}</span>
        </button>

        <div class="search-box">
          <SearchIcon class="search-icon w-5 h-5" />
          <input v-model="searchQuery" type="text" placeholder="Konu veya kullanıcı ara..." @input="performSearch" />
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

      <!-- Quick Filters -->
      <QuickFilters :activeFilter="activeFilter" @filter="activeFilter = $event" />

      <!-- Main Content Grid -->
      <div class="forum-grid">
        <!-- Games Column -->
        <div class="games-column stagger-children">
          <!-- CS 1.6 Section -->
          <section class="game-section">
            <div class="game-card game-card--cs16 game-card-glow">
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
                <p class="game-desc">Sunucu ilanlari, AMX Mod X, plugin paylaşimi, turnuvalar</p>
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
            <div class="game-card game-card--halflife game-card-glow">
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
            <div class="game-card game-card--community game-card-glow">
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
          <!-- Pinned Topics -->
          <PinnedTopicsSection :topics="pinnedTopics" :maxShow="3" />

          <!-- Hot Topics -->
          <div class="sidebar-card">
            <div class="sidebar-header">
              <FlameIcon class="w-4 h-4 text-orange-500" />
              <h3>Popüler Konular</h3>
            </div>
            <div class="hot-topics">
              <router-link
                v-for="(topic, index) in hotTopics"
                :key="topic.id"
                :to="`/forum/topic/${topic.id}`"
                class="hot-topic topic-hover-enhanced"
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

          <!-- Tags Cloud Widget -->
          <TagsCloudWidget :activeTag="activeTag" @tag-click="handleTagFilter" />

          <!-- Recent Viewed Widget -->
          <RecentViewedWidget ref="recentViewedRef" />

          <!-- Recent Activity -->
          <div class="sidebar-card">
            <div class="sidebar-header">
              <ActivityIcon class="w-4 h-4 text-cyan-500" />
              <h3>Son Aktivite</h3>
            </div>
            <div class="activity-feed">
              <div v-for="n in 4" :key="n" class="activity-item">
                <div class="activity-avatar avatar-online-ring">
                  <div class="online-dot"></div>
                </div>
                <div class="activity-content">
                  <span class="activity-user">Kullanıcı{{ n }}</span>
                  <span class="activity-action">yeni konu acti</span>
                </div>
                <span class="activity-time">{{ n }}dk</span>
              </div>
            </div>
          </div>

          <!-- Game Showcase (kompakt) -->
          <div class="sidebar-card sidebar-card--showcase">
            <div class="sidebar-header">
              <SparklesIcon class="w-4 h-4 text-yellow-500" />
              <h3>Oyunlar</h3>
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
              <h2><PlusIcon class="w-5 h-5" /> Yeni Konu Oluştur</h2>
              <button @click="showNewTopicModal = false" class="modal-close">
                <XIcon class="w-6 h-6" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Kategori</label>
                <select v-model="newTopic.categoryId">
                  <option value="">Kategori seçin...</option>
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
                <label>Başlık</label>
                <input v-model="newTopic.title" type="text" placeholder="Konu basligi..." maxlength="100" />
              </div>
              <div class="form-group">
                <label>İçerik</label>
                <textarea v-model="newTopic.content" placeholder="Konu içeriği..." rows="6"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button @click="showNewTopicModal = false" class="btn-secondary">İptal</button>
              <button @click="createTopic" class="btn-primary" :disabled="!isTopicValid || isSubmitting">
                {{ isSubmitting ? 'Gönderiliyor...' : 'Oluştur' }}
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
// New components
import KeyboardShortcuts from '@/components/forum/KeyboardShortcuts.vue'
import ScrollProgress from '@/components/forum/ScrollProgress.vue'
import QuickFilters from '@/components/forum/QuickFilters.vue'
import TagsCloudWidget from '@/components/forum/TagsCloudWidget.vue'
import RecentViewedWidget from '@/components/forum/RecentViewedWidget.vue'
import PinnedTopicsSection from '@/components/forum/PinnedTopicsSection.vue'
// Styles
import '@/assets/styles/forum-enhancements.css'
import {
  SearchIcon, PlusIcon, FileTextIcon, MessageSquareIcon, UsersIcon,
  FlameIcon, FolderIcon, ChevronRightIcon, XIcon, TargetIcon,
  Gamepad2Icon, TrendingUpIcon, ClockIcon, ActivityIcon, SparklesIcon,
  ChevronUpIcon, HashIcon
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
const activeTag = ref(null)
const categories = ref([])
const hotTopics = ref([])
const pinnedTopics = ref([])
const showBackToTop = ref(false)
const recentViewedRef = ref(null)

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
  { id: 'all', label: 'Tümu', icon: FolderIcon },
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

const fetchPinnedTopics = async () => {
  try {
    const response = await forumAPI.getAllTopics({ pinned: true, limit: 10 })
    const data = response?.topics || response || []
    pinnedTopics.value = data.map(t => ({
      id: t.id,
      title: t.title,
      replies: t.reply_count || 0,
      views: t.view_count || 0
    }))
  } catch (error) { console.error('Pinned topics error:', error) }
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
    alert(error.response?.data?.detail || 'Konu oluşturulamadi')
  } finally { isSubmitting.value = false }
}

const performSearch = debounce(() => {
  if (searchQuery.value.length >= 2) router.push({ path: '/forum', query: { q: searchQuery.value } })
}, 500)

// Tag filter
const handleTagFilter = (tag) => {
  if (activeTag.value === tag) {
    activeTag.value = null
  } else {
    activeTag.value = tag
    router.push({ path: '/forum', query: { tag } })
  }
}

// Keyboard shortcut
const handleKeydown = (e) => {
  const tagName = document.activeElement?.tagName
  if (tagName === 'INPUT' || tagName === 'TEXTAREA') return

  switch (e.key) {
    case '/':
      if (!e.ctrlKey && !e.metaKey) {
        e.preventDefault()
        document.querySelector('.search-box input')?.focus()
      }
      break
    case 't':
    case 'T':
      scrollToTop()
      break
    case 'n':
    case 'N':
      e.preventDefault()
      handleNewTopic()
      break
    case 'j':
    case 'J':
      // Navigate to next topic
      navigateTopic(1)
      break
    case 'k':
    case 'K':
      // Navigate to previous topic
      navigateTopic(-1)
      break
  }
}

// Topic navigation with J/K keys
let currentTopicIndex = -1
const navigateTopic = (direction) => {
  const topics = document.querySelectorAll('.hot-topic, .category-item')
  if (topics.length === 0) return

  currentTopicIndex += direction
  if (currentTopicIndex < 0) currentTopicIndex = topics.length - 1
  if (currentTopicIndex >= topics.length) currentTopicIndex = 0

  const topic = topics[currentTopicIndex]
  topic.focus()
  topic.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('scroll', handleScroll)
  isLoading.value = true
  await Promise.all([fetchCategories(), fetchHotTopics(), fetchPinnedTopics(), fetchStats(), loadGameAssets()])
  isLoading.value = false
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('scroll', handleScroll)
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
  padding: 12px;
  position: relative;
  z-index: 1;
}

/* Minimal Stats Bar */
.forum-stats-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  margin-bottom: 10px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
}

.stats-bar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stats-bar-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #f97316, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats-bar-divider {
  color: rgba(255,255,255,0.2);
}

.stats-bar-online {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #22c55e;
}

.online-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.stats-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-bar-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: rgba(255,255,255,0.6);
}

.stats-bar-item svg {
  color: #f97316;
}

@media (max-width: 600px) {
  .forum-stats-bar {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  .stats-bar-right {
    gap: 12px;
  }
}

/* Actions - Sticky */
.forum-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 12px;
  position: sticky;
  top: 60px;
  z-index: 100;
  background: rgba(11, 15, 20, 0.95);
  backdrop-filter: blur(10px);
  padding: 8px 12px;
  margin-left: -12px;
  margin-right: -12px;
  border-radius: 10px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
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
  padding: 10px 14px 10px 40px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
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
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255,255,255,0.4);
  width: 18px;
  height: 18px;
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
  gap: 4px;
  padding: 6px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: rgba(255,255,255,0.6);
  font-size: 12px;
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
  grid-template-columns: 1fr 260px;
  gap: 12px;
}

@media (max-width: 1200px) {
  .forum-grid { grid-template-columns: 1fr; }
}

@media (max-width: 1024px) {
  .forum-sidebar { display: none; }
}

/* Game Cards - 3 Column Layout */
.games-column {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

@media (max-width: 1200px) {
  .games-column {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .games-column {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .games-column {
    grid-template-columns: 1fr;
  }
}

.game-card {
  position: relative;
  border-radius: 12px;
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
  padding: 12px 14px;
}

.game-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.game-card__content--simple {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(124, 58, 237, 0.1));
}

.game-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.game-logo {
  height: 32px;
  max-width: 120px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.5));
}

.game-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
}

.game-title svg {
  width: 20px;
  height: 20px;
}

.game-title--community {
  color: #a78bfa;
}

.game-badge {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 3px 8px;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  border-radius: 50px;
  color: #fff;
  font-size: 10px;
  font-weight: 500;
}

.badge-count {
  font-weight: 700;
  font-size: 11px;
}

.game-desc {
  color: rgba(255,255,255,0.8);
  font-size: 11px;
  margin: 0;
  line-height: 1.3;
}

/* Categories */
.game-categories {
  position: relative;
  z-index: 1;
  padding: 6px;
  background: rgba(0,0,0,0.2);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s;
}

.category-item:hover {
  background: rgba(255,255,255,0.08);
}

.category-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
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
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-meta {
  display: flex;
  gap: 8px;
  font-size: 10px;
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
  padding: 20px;
  text-align: center;
  color: rgba(255,255,255,0.4);
  font-size: 13px;
}

/* Sidebar */
.forum-sidebar {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 12px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.sidebar-header h3 {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.sidebar-header svg {
  width: 16px;
  height: 16px;
}

/* Hot Topics */
.hot-topics {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hot-topic {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s;
}

.hot-topic:hover {
  background: rgba(255,255,255,0.06);
  transform: translateX(4px);
}

.hot-rank {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 6px;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}

.hot-info {
  flex: 1;
  min-width: 0;
}

.hot-title {
  display: block;
  font-size: 12px;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 1px;
}

.hot-meta {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

.hot-meta svg {
  width: 10px;
  height: 10px;
}

/* Activity Feed */
.activity-feed {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.activity-avatar {
  width: 26px;
  height: 26px;
  background: linear-gradient(135deg, #f97316, #8b5cf6);
  border-radius: 50%;
}

.activity-content {
  flex: 1;
  font-size: 11px;
}

.activity-user {
  color: #fff;
  font-weight: 500;
}

.activity-action {
  color: rgba(255,255,255,0.5);
  margin-left: 3px;
}

.activity-time {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
}

/* Showcase */
.showcase-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.showcase-item {
  position: relative;
  aspect-ratio: 2/3;
  border-radius: 8px;
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
  padding: 6px;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: #fff;
  font-size: 10px;
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
  bottom: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
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

.back-to-top svg {
  width: 20px;
  height: 20px;
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
  .forum-container { padding: 8px; }
  .forum-hero { padding: 12px 14px; }
  .hero-title { font-size: 24px; }
  .hero-stats { gap: 6px; }
  .stat-card { padding: 6px 10px; }
  .forum-actions { flex-direction: column; align-items: stretch; gap: 6px; }
  .search-box { max-width: none; }
  .action-filters { justify-content: center; }
  .game-card__content { padding: 12px; }
  .back-to-top { bottom: 16px; right: 16px; width: 40px; height: 40px; }
}
</style>
