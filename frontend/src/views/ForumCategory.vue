<template>
  <ForumLayout
    :show-right-sidebar="true"
    class="forum-page"
  >
    <!-- Left Sidebar: Category Navigation -->
    <template #sidebar-left>
      <ForumSidebar
        :categories="allCategories"
        :active-category="categoryId"
        :stats="sidebarStats"
        @category-click="handleCategoryClick"
      />
    </template>

    <!-- Main Content -->
    <template #default>
      <!-- Category Game Banner -->
      <div v-if="gameBanner" class="forum-category-banner">
        <img :src="gameBanner" :alt="category?.name" class="forum-category-banner__img" />
        <div class="forum-category-banner__overlay">
          <img v-if="gameLogo" :src="gameLogo" :alt="category?.name" class="forum-category-banner__logo" />
        </div>
      </div>

      <!-- Breadcrumb -->
      <nav class="forum-breadcrumb-enhanced" aria-label="Gezinti">
        <a href="#" @click.prevent="router.push('/forum')" class="forum-breadcrumb-item">
          <HomeIcon class="w-4 h-4" />
          <span>Forum</span>
        </a>
        <ChevronRightIcon class="w-4 h-4 forum-breadcrumb-separator" />
        <span class="forum-breadcrumb-current">
          <FolderIcon class="w-4 h-4" />
          {{ category?.name }}
        </span>
      </nav>

      <!-- Category Header -->
      <section class="forum-category-header">
        <div class="forum-category-header__icon forum-category-icon" :style="{ background: category?.color ? `linear-gradient(135deg, ${category.color}, ${adjustColor(category.color, -30)})` : getCategoryGradient(category?.gradient) }">
          <span v-if="category?.icon && typeof category.icon === 'string'" class="text-3xl">{{ category.icon }}</span>
          <MessageSquareIcon v-else class="w-8 h-8 text-white" />
        </div>
        <div class="forum-category-header__info">
          <h1 class="forum-heading-enhanced forum-heading--xl">{{ category?.name || 'Kategori' }}</h1>
          <p class="forum-meta forum-text-body">{{ category?.description }}</p>
          <div class="forum-category-header__stats">
            <span class="forum-stat-enhanced">
              <span class="forum-stat-enhanced__icon">
                <FileTextIcon class="w-3.5 h-3.5" />
              </span>
              <span class="forum-stat-enhanced__value">{{ topics.length }}</span>
              <span class="forum-stat-enhanced__label">Konu</span>
            </span>
            <span class="forum-stat-enhanced">
              <span class="forum-stat-enhanced__icon">
                <MessageSquareIcon class="w-3.5 h-3.5" />
              </span>
              <span class="forum-stat-enhanced__value">{{ totalPosts }}</span>
              <span class="forum-stat-enhanced__label">Gönderi</span>
            </span>
            <span class="forum-stat-enhanced">
              <span class="forum-stat-enhanced__icon">
                <EyeIcon class="w-3.5 h-3.5" />
              </span>
              <span class="forum-stat-enhanced__value">{{ formatNumber(totalViews) }}</span>
              <span class="forum-stat-enhanced__label">Görüntülenme</span>
            </span>
          </div>
        </div>
        <div class="forum-category-header__action">
          <n-tooltip :disabled="isLoggedIn && hasSteam" trigger="hover">
            <template #trigger>
              <n-button
                type="primary"
                size="large"
                class="forum-btn-enhanced forum-btn-enhanced--primary"
                :class="{ 'forum-btn--disabled': !isLoggedIn || !hasSteam }"
                @click="handleNewTopic"
              >
                <template #icon>
                  <LockIcon v-if="!isLoggedIn || !hasSteam" class="w-5 h-5" />
                  <PlusCircleIcon v-else class="w-5 h-5" />
                </template>
                {{ !isLoggedIn ? 'Giris Yap' : (!hasSteam ? 'Steam Bagla' : 'Yeni Konu Ac') }}
              </n-button>
            </template>
            {{ !isLoggedIn ? 'Konu olusturmak icin giris yapin' : 'Konu olusturmak icin Steam hesabinizi baglayin' }}
          </n-tooltip>
        </div>
      </section>

      <!-- Filters & Sort -->
      <section class="forum-filters">
        <div class="forum-filters__search forum-search-enhanced" :class="{ focused: searchFocused }">
          <SearchIcon class="w-5 h-5 forum-search-icon" aria-hidden="true" />
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Konularda ara..."
            class="forum-search-input"
            aria-label="Konularda ara"
            @focus="searchFocused = true"
            @blur="searchFocused = false"
            @keydown.escape="searchQuery = ''"
          />
          <button
            v-if="searchQuery"
            @click="searchQuery = ''"
            class="forum-search-clear"
            aria-label="Aramayi temizle"
            type="button"
          >
            <XIcon class="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        <div class="forum-filters__controls">
          <!-- View Mode Toggle -->
          <div class="forum-view-toggle" role="group" aria-label="Görunum modu">
            <button
              @click="handleViewModeChange('list')"
              :class="['forum-view-toggle__btn', { active: viewMode === 'list' }]"
              :aria-pressed="viewMode === 'list'"
              aria-label="Liste Görunumu"
              title="Liste Görunumu"
            >
              <ListIcon class="w-4 h-4" />
            </button>
            <button
              @click="handleViewModeChange('compact')"
              :class="['forum-view-toggle__btn', { active: viewMode === 'compact' }]"
              :aria-pressed="viewMode === 'compact'"
              aria-label="Kompakt Görunum"
              title="Kompakt Görunum"
            >
              <LayoutGridIcon class="w-4 h-4" />
            </button>
          </div>

          <!-- Sort Dropdown -->
          <div class="forum-sort-dropdown" :class="{ open: sortDropdownOpen }">
            <button class="forum-sort-dropdown__trigger" @click="sortDropdownOpen = !sortDropdownOpen">
              <component :is="currentSortOption.icon" class="w-4 h-4" />
              <span>{{ currentSortOption.label }}</span>
              <ChevronDownIcon class="w-4 h-4" />
            </button>
            <Transition name="dropdown">
              <div v-if="sortDropdownOpen" class="forum-sort-dropdown__menu">
                <button
                  v-for="option in sortOptions"
                  :key="option.value"
                  @click="handleSortChange(option.value)"
                  :class="['forum-sort-dropdown__option', { active: sortBy === option.value }]"
                >
                  <component :is="option.icon" class="w-4 h-4" />
                  <span>{{ option.label }}</span>
                  <CheckIcon v-if="sortBy === option.value" class="w-4 h-4" />
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </section>

      <!-- Topics List -->
      <section class="forum-topics-list" :class="{ 'forum-topics-list--compact': viewMode === 'compact' }">
        <!-- Loading State -->
        <template v-if="isLoading">
          <ForumSkeleton v-for="n in 5" :key="n" type="topic-card" />
        </template>

        <!-- Error State -->
        <div v-else-if="fetchError" class="forum-error-state">
          <div class="forum-error-state__icon">
            <AlertCircleIcon class="w-16 h-16 text-red-500" />
          </div>
          <h3 class="forum-heading forum-heading--md">Bir Hata Olustu</h3>
          <p class="forum-meta">{{ fetchError }}</p>
          <div class="forum-error-state__actions">
            <n-button type="primary" @click="fetchTopics">
              <template #icon><RefreshCwIcon class="w-5 h-5" /></template>
              Tekrar Dene
            </n-button>
            <n-button quaternary @click="router.push('/forum')">
              <template #icon><ArrowLeftIcon class="w-5 h-5" /></template>
              Foruma Don
            </n-button>
          </div>
        </div>

        <!-- Topics -->
        <template v-else-if="displayedTopics.length > 0">
          <ForumTopicCard
            v-for="topic in displayedTopics"
            :key="topic.id"
            :topic="formatTopicForCard(topic)"
            :compact="viewMode === 'compact'"
            :show-badges="true"
            :show-tags="true"
          />
        </template>

        <!-- Empty State -->
        <div v-else class="forum-empty-enhanced">
          <div class="forum-empty-icon">
            <MessageSquareIcon class="w-14 h-14" />
          </div>
          <h3 class="forum-empty-title">Henuz Konu Yok</h3>
          <p class="forum-empty-description">Bu kategoride henuz bir konu acilmamis. Ilk konuyu acarak tartismayi baslatin!</p>
          <div class="forum-empty-actions">
            <n-button type="primary" size="large" class="forum-btn-enhanced forum-btn-enhanced--primary" @click="handleNewTopic" :disabled="!isLoggedIn || !hasSteam">
              <template #icon><PlusCircleIcon class="w-5 h-5" /></template>
              {{ !isLoggedIn ? 'Giris Yap' : (!hasSteam ? 'Steam Bagla' : 'Ilk Konuyu Ac') }}
            </n-button>
            <n-button quaternary size="large" class="forum-btn-enhanced forum-btn-enhanced--secondary" @click="router.push('/forum')">
              <template #icon><ArrowLeftIcon class="w-5 h-5" /></template>
              Foruma Don
            </n-button>
          </div>
        </div>
      </section>

      <!-- Pagination -->
      <section v-if="!isLoading && filteredTopics.length > itemsPerPage" class="forum-pagination-enhanced">
        <button
          class="forum-pagination-btn forum-pagination-btn--nav"
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          <ChevronLeftIcon class="w-5 h-5" />
          <span>Onceki</span>
        </button>

        <div class="forum-pagination__pages">
          <button
            v-for="page in visiblePages"
            :key="page"
            :class="['forum-pagination-btn', { 'forum-pagination-btn--active': page === currentPage, 'forum-pagination-ellipsis': page === '...' }]"
            :disabled="page === '...'"
            @click="page !== '...' && changePage(page)"
          >
            {{ page }}
          </button>
        </div>

        <button
          class="forum-pagination-btn forum-pagination-btn--nav"
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          <span>Sonraki</span>
          <ChevronRightIcon class="w-5 h-5" />
        </button>
      </section>
    </template>

    <!-- Right Sidebar -->
    <template #sidebar-right>
      <!-- Pinned Topics for this category -->
      <PinnedTopicsSection :topics="pinnedTopicsInCategory" :maxShow="5" />

      <!-- Online Users -->
      <div class="forum-sidebar-card">
        <h3 class="forum-sidebar-card__title">
          <UsersIcon class="w-4 h-4" />
          Çevrimiçi Kullanıcılar
        </h3>
        <div class="forum-online-indicator">
          <span class="forum-online-dot"></span>
          <span class="forum-online-count">{{ onlineUsers }}</span>
          <span class="forum-meta">çevrimiçi</span>
        </div>
      </div>

      <!-- Category Stats -->
      <div class="forum-sidebar-card">
        <h3 class="forum-sidebar-card__title">
          <TrendingUpIcon class="w-4 h-4" />
          Kategori Istatistikleri
        </h3>
        <div class="forum-stats-grid">
          <div class="forum-stat-box">
            <span class="forum-stat-box__value">{{ topics.length }}</span>
            <span class="forum-stat-box__label">Toplam Konu</span>
          </div>
          <div class="forum-stat-box">
            <span class="forum-stat-box__value">{{ totalPosts }}</span>
            <span class="forum-stat-box__label">Toplam Gönderi</span>
          </div>
          <div class="forum-stat-box">
            <span class="forum-stat-box__value">{{ formatNumber(totalViews) }}</span>
            <span class="forum-stat-box__label">Görüntülenme</span>
          </div>
        </div>
      </div>

      <!-- Popular Categories -->
      <div class="forum-sidebar-card">
        <h3 class="forum-sidebar-card__title">
          <StarIcon class="w-4 h-4" />
          Popüler Kategoriler
        </h3>
        <div class="forum-sidebar-categories">
          <button
            v-for="cat in popularCategories"
            :key="cat.id"
            class="forum-sidebar-category"
            @click="router.push(`/forum/category/${cat.slug || cat.id}`)"
          >
            <component :is="cat.icon" class="w-4 h-4" />
            <span>{{ cat.name }}</span>
          </button>
        </div>
      </div>
    </template>
  </ForumLayout>

  <!-- New Topic Modal -->
  <n-modal v-model:show="showNewTopicModal" :mask-closable="false" class="forum-modal">
    <div class="forum-modal__content">
      <div class="forum-modal__header">
        <EditIcon class="w-6 h-6 text-orange-500" />
        <div>
          <h2 class="forum-heading forum-heading--lg">Yeni Konu Oluştur</h2>
          <p class="forum-meta">Topluluga paylaşma istediginiz konuyu yazin</p>
        </div>
        <button class="forum-modal__close" @click="showNewTopicModal = false">
          <XIcon class="w-5 h-5" />
        </button>
      </div>

      <form @submit.prevent="createTopic" class="forum-modal__form">
        <!-- Topic Type Selection -->
        <div class="forum-form-group">
          <label class="forum-form-label">
            <TagIcon class="w-4 h-4" />
            Konu Tipi
          </label>
          <div class="forum-type-selector">
            <button
              v-for="type in topicTypes"
              :key="type.value"
              type="button"
              :class="['forum-type-option', { active: newTopic.type === type.value }]"
              @click="newTopic.type = type.value"
            >
              <component :is="type.icon" class="w-4 h-4" />
              <span>{{ type.label }}</span>
            </button>
          </div>
        </div>

        <div class="forum-form-group">
          <label class="forum-form-label">
            <TypeIcon class="w-4 h-4" />
            Konu Basligi
          </label>
          <input
            v-model="newTopic.title"
            type="text"
            placeholder="Dikkat cekici bir başlık girin..."
            class="forum-form-input"
            :class="{ error: titleError }"
          />
          <span class="forum-form-counter" :class="{ warning: newTopic.title.length > 80 }">
            {{ newTopic.title.length }}/100
          </span>
          <p v-if="titleError" class="forum-form-error">{{ titleError }}</p>
        </div>

        <div class="forum-form-group">
          <label class="forum-form-label">
            <FileTextIcon class="w-4 h-4" />
            İçerik
          </label>
          <textarea
            v-model="newTopic.content"
            placeholder="Konu içeriğinizi detayli bir sekilde açıklayin..."
            class="forum-form-textarea"
            :class="{ error: contentError }"
            rows="8"
          ></textarea>
          <span class="forum-form-counter" :class="{ warning: newTopic.content.length > 4500 }">
            {{ newTopic.content.length }}/5000
          </span>
          <p v-if="contentError" class="forum-form-error">{{ contentError }}</p>
        </div>

        <div class="forum-form-group">
          <label class="forum-form-label">
            <HashIcon class="w-4 h-4" />
            Etiketler (Opsiyonel)
          </label>
          <div class="forum-tags-input">
            <span v-for="tag in newTopic.tags" :key="tag" class="forum-tag">
              {{ tag }}
              <button type="button" @click="removeTag(tag)">
                <XIcon class="w-3 h-3" />
              </button>
            </span>
            <input
              v-model="tagInput"
              type="text"
              placeholder="Etiket ekle..."
              @keydown.enter.prevent="addTag"
              @keydown.comma.prevent="addTag"
            />
          </div>
          <p class="forum-form-hint">Enter veya virgul ile etiket ekleyin (max 5)</p>
        </div>
      </form>

      <div class="forum-modal__footer">
        <n-button quaternary size="large" @click="showNewTopicModal = false">
          İptal
        </n-button>
        <n-button type="primary" size="large" :loading="isCreating" @click="createTopic">
          <template #icon><SendIcon class="w-5 h-5" /></template>
          Konuyu Oluştur
        </n-button>
      </div>
    </div>
  </n-modal>

  <!-- Steam Required Modal -->
  <SteamRequiredModal
    :show="showSteamModal"
    @close="closeSteamModal"
    @connect="connectSteam"
  />

  <!-- Back to Top Button -->
  <Transition name="fade">
    <button v-if="showBackToTop" class="back-to-top" @click="scrollToTop" title="Yukarı Çık">
      <ChevronUpIcon class="w-6 h-6" />
    </button>
  </Transition>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameAssets } from '@/composables/useGameAssets'
import { useAuthStore } from '@/stores/auth'
import { useRequireSteam } from '@/composables/useRequireSteam'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import { ForumLayout, ForumSidebar, ForumTopicCard, ForumSkeleton } from '@/components/forum'
import PinnedTopicsSection from '@/components/forum/PinnedTopicsSection.vue'
import {
  HomeIcon,
  MessageSquareIcon,
  FileTextIcon,
  PlusCircleIcon,
  SearchIcon,
  UserIcon,
  UsersIcon,
  ClockIcon,
  PinIcon,
  LockIcon,
  EyeIcon,
  ThumbsUpIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  ChevronDownIcon,
  SendIcon,
  XIcon,
  FolderIcon,
  FlameIcon,
  ArrowLeftIcon,
  EditIcon,
  TypeIcon,
  TagIcon,
  HashIcon,
  TrendingUpIcon,
  CalendarIcon,
  StarIcon,
  HelpCircleIcon,
  ShieldIcon,
  ZapIcon,
  ListIcon,
  LayoutGridIcon,
  CheckIcon,
  MessageCircleQuestionIcon,
  MegaphoneIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  RefreshCwIcon,
  ChevronUpIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const categoryId = route.params.id
const { hasSteam, showSteamModal, requireSteam, connectSteam, closeModal: closeSteamModal } = useRequireSteam()
const { getGameAssets } = useGameAssets()

// Game banner for gaming categories
const gameAssets = ref({})

// Game slug from API - priority over local mapping
const gameSlug = computed(() => {
  // First check category.game_slug from API
  if (category.value?.game_slug) {
    return category.value.game_slug
  }
  // Fallback mapping for old categories or direct URL access
  const categoryToGame = {
    'cs16': 'cs16',
    'counter-strike': 'cs16',
    'cs-taktikler': 'cs16',
    'cs-turnuvalar': 'cs16',
    'cs-modlar': 'cs16',
    'cs-haritalar': 'cs16',
    'cs-medya': 'cs16',
    'half-life-ag': 'halflife',
    'halflife': 'halflife',
    'ag-taktikler': 'halflife',
    'hl-modlar': 'halflife',
    'hl-haritalar': 'halflife',
    'hl-medya': 'halflife'
  }
  const catSlug = category.value?.slug?.toLowerCase()
  return categoryToGame[catSlug] || null
})

const gameBanner = computed(() => gameAssets.value?.hero || null)
const gameLogo = computed(() => gameAssets.value?.logo || null)

const loadGameBanner = async () => {
  const slug = gameSlug.value
  if (slug) {
    try {
      const assets = await getGameAssets(slug, null, 10)
      const assetMap = {}
      assets.forEach(asset => {
        assetMap[asset.asset_type] = asset.file_path
      })
      gameAssets.value = assetMap
    } catch (e) {
      console.error('Failed to load game banner:', e)
    }
  }
}

// Auth state
const isLoggedIn = computed(() => !!authStore.user)

// State persistence keys
const CATEGORY_SORT_KEY = 'forum_category_sort'
const CATEGORY_VIEW_KEY = 'forum_category_view'

// Refs with persistence
const searchQuery = ref('')
const searchFocused = ref(false)
const sortBy = ref(localStorage.getItem(CATEGORY_SORT_KEY) || 'newest')
const sortDropdownOpen = ref(false)
const viewMode = ref(localStorage.getItem(CATEGORY_VIEW_KEY) || 'list')
const showNewTopicModal = ref(false)
const currentPage = ref(1)
const itemsPerPage = ref(10)
const isLoading = ref(true)
const isCreating = ref(false)
const tagInput = ref('')
const titleError = ref('')
const contentError = ref('')
const onlineUsers = ref(23)
const showBackToTop = ref(false)

// Scroll to top function
const scrollToTop = () => { window.scrollTo({ top: 0, behavior: 'smooth' }) }

// Debounce timer ref for search
let searchDebounceTimer = null

// Sort options with icons
const sortOptions = [
  { label: 'En Yeni', value: 'newest', icon: CalendarIcon },
  { label: 'Popüler', value: 'popular', icon: TrendingUpIcon },
  { label: 'En Cok Yanıt', value: 'most_replies', icon: MessageSquareIcon },
  { label: 'En Eski', value: 'oldest', icon: ClockIcon }
]

const currentSortOption = computed(() => {
  return sortOptions.find(o => o.value === sortBy.value) || sortOptions[0]
})

// Category data
const category = ref({
  id: 1,
  name: 'Genel Tartisma',
  description: 'CS 1.6 hakkinda genel konular, sorular ve paylaşimlar icin açık tartisma alani',
  icon: MessageSquareIcon,
  gradient: 'primary-secondary'
})

// All categories for sidebar
const allCategories = ref([
  { id: 1, name: 'Genel Tartisma', icon: MessageSquareIcon, topics: 156, color: '#f97316' },
  { id: 2, name: 'Sorular & Cevaplar', icon: HelpCircleIcon, topics: 89, color: '#8b5cf6' },
  { id: 3, name: 'Duyurular', icon: ZapIcon, topics: 12, color: '#22c55e' },
  { id: 4, name: 'Kurallar', icon: ShieldIcon, topics: 5, color: '#ef4444' }
])

// Sidebar stats
const sidebarStats = computed(() => ({
  totalTopics: topics.value.length,
  totalPosts: totalPosts.value,
  totalMembers: 1250
}))

// Popular categories for sidebar
const popularCategories = [
  { id: 1, name: 'Genel Tartisma', icon: MessageSquareIcon },
  { id: 2, name: 'Sorular & Cevaplar', icon: HelpCircleIcon },
  { id: 3, name: 'Duyurular', icon: ZapIcon },
  { id: 4, name: 'Kurallar', icon: ShieldIcon }
]

// Topic types
const topicTypes = [
  { value: 'discussion', label: 'Tartisma', icon: MessageSquareIcon },
  { value: 'question', label: 'Soru', icon: MessageCircleQuestionIcon },
  { value: 'announcement', label: 'Duyuru', icon: MegaphoneIcon }
]

// Topics data - API'den çekilecek
const topics = ref([])

// Format number utility
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num
}

// Extract author name from item - handles nested objects
const getAuthorName = (item) => {
  if (!item) return 'Anonim'
  if (typeof item.author === 'string' && item.author.trim()) return item.author.trim()
  if (typeof item.author === 'object' && item.author) {
    return item.author.username || item.author.name || 'Anonim'
  }
  return item.author_name || 'Anonim'
}

// Get gradient color
const getCategoryGradient = (gradient) => {
  const gradients = {
    'primary-secondary': 'linear-gradient(135deg, #f97316, #8b5cf6)',
    'secondary-accent': 'linear-gradient(135deg, #8b5cf6, #22d3ee)',
    'accent-error': 'linear-gradient(135deg, #22d3ee, #ef4444)',
    'primary-accent': 'linear-gradient(135deg, #f97316, #22d3ee)',
    'warning-success': 'linear-gradient(135deg, #eab308, #22c55e)'
  }
  return gradients[gradient] || gradients['primary-secondary']
}

// Adjust color brightness
const adjustColor = (color, amount) => {
  if (!color) return '#f97316'
  const hex = color.replace('#', '')
  const num = parseInt(hex, 16)
  const r = Math.max(0, Math.min(255, (num >> 16) + amount))
  const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amount))
  const b = Math.max(0, Math.min(255, (num & 0x0000FF) + amount))
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`
}

// Format topic for ForumTopicCard component
const formatTopicForCard = (topic) => {
  // Handle author as object or string
  const authorObj = typeof topic.author === 'object' ? topic.author : null
  const authorName = authorObj ? (authorObj.username || authorObj.name || 'Anonim') : (topic.author || 'Anonim')
  const authorAvatar = authorObj ? authorObj.avatar : topic.authorAvatar

  return {
    id: topic.id,
    title: topic.title,
    author: authorName,
    authorAvatar: authorAvatar,
    authorOnline: topic.authorOnline,
    created: topic.created,
    replies: topic.replies,
    views: topic.views,
    likes: topic.likes,
    isPinned: topic.isPinned,
    isLocked: topic.isLocked,
    isSolved: topic.isSolved,
    isHot: topic.isHot,
    tags: topic.tags || [],
    lastReply: topic.lastReply,
    preview: topic.preview
  }
}

// Computed values
const totalPosts = computed(() => {
  return topics.value.reduce((sum, topic) => sum + topic.replies + 1, 0)
})

// Pinned topics in this category
const pinnedTopicsInCategory = computed(() => {
  return topics.value
    .filter(t => t.isPinned)
    .map(t => ({
      id: t.id,
      title: t.title,
      replies: t.replies || 0,
      views: t.views || 0
    }))
})

const totalViews = computed(() => {
  return topics.value.reduce((sum, topic) => sum + topic.views, 0)
})

// Active tag filter
const activeTag = ref(null)

// All unique tags from topics
const allTags = computed(() => {
  const tags = new Set()
  topics.value.forEach(t => {
    (t.tags || []).forEach(tag => tags.add(tag))
  })
  return Array.from(tags)
})

// Filter by tag function
const filterByTag = (tag) => {
  if (activeTag.value === tag) {
    activeTag.value = null
  } else {
    activeTag.value = tag
  }
  currentPage.value = 1
}

const filteredTopics = computed(() => {
  let filtered = [...topics.value]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.title.toLowerCase().includes(query) ||
      getAuthorName(t).toLowerCase().includes(query) ||
      t.preview?.toLowerCase().includes(query) ||
      (t.tags || []).some(tag => tag.toLowerCase().includes(query))
    )
  }

  // Tag filter
  if (activeTag.value) {
    filtered = filtered.filter(t =>
      (t.tags || []).includes(activeTag.value)
    )
  }

  // Always show pinned topics first
  const pinned = filtered.filter(t => t.isPinned)
  const unpinned = filtered.filter(t => !t.isPinned)

  // Sort unpinned topics
  if (sortBy.value === 'newest') {
    unpinned.sort((a, b) => b.id - a.id)
  } else if (sortBy.value === 'popular') {
    unpinned.sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'most_replies') {
    unpinned.sort((a, b) => b.replies - a.replies)
  } else if (sortBy.value === 'oldest') {
    unpinned.sort((a, b) => a.id - b.id)
  } else if (sortBy.value === 'most_likes') {
    unpinned.sort((a, b) => (b.likes || 0) - (a.likes || 0))
  } else if (sortBy.value === 'unsolved') {
    // Show unsolved topics first
    unpinned.sort((a, b) => {
      if (a.isSolved && !b.isSolved) return 1
      if (!a.isSolved && b.isSolved) return -1
      return b.id - a.id
    })
  }

  return [...pinned, ...unpinned]
})

const displayedTopics = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredTopics.value.slice(start, start + itemsPerPage.value)
})

const totalPages = computed(() => {
  return Math.ceil(filteredTopics.value.length / itemsPerPage.value)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')

    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)

    for (let i = start; i <= end; i++) pages.push(i)

    if (current < total - 2) pages.push('...')
    pages.push(total)
  }

  return pages
})

// New topic form
const newTopic = reactive({
  title: '',
  content: '',
  tags: [],
  type: 'discussion'
})

// Methods
const handleSortChange = (value) => {
  sortBy.value = value
  sortDropdownOpen.value = false
  currentPage.value = 1
  localStorage.setItem(CATEGORY_SORT_KEY, value)
}

// Handle view mode change with persistence
const handleViewModeChange = (mode) => {
  viewMode.value = mode
  localStorage.setItem(CATEGORY_VIEW_KEY, mode)
}

const handleCategoryClick = (cat) => {
  router.push(`/forum/category/${cat.slug || cat.id}`)
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !newTopic.tags.includes(tag) && newTopic.tags.length < 5) {
    newTopic.tags.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (tag) => {
  const index = newTopic.tags.indexOf(tag)
  if (index > -1) {
    newTopic.tags.splice(index, 1)
  }
}

const validateForm = () => {
  titleError.value = ''
  contentError.value = ''

  if (!newTopic.title || newTopic.title.trim().length < 5) {
    titleError.value = 'Başlık en az 5 karakter olmalidir'
    return false
  }
  if (newTopic.title.length > 100) {
    titleError.value = 'Başlık 100 karakterden uzun olamaz'
    return false
  }
  if (!newTopic.content || newTopic.content.trim().length < 20) {
    contentError.value = 'İçerik en az 20 karakter olmalidir'
    return false
  }
  if (newTopic.content.length > 5000) {
    contentError.value = 'İçerik 5000 karakterden uzun olamaz'
    return false
  }
  return true
}

const handleNewTopic = () => {
  requireSteam(() => {
    showNewTopicModal.value = true
  })
}

// Get CSRF token from cookie
const getCsrfToken = () => {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrf_token') return value
  }
  return null
}

const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authStore.token}`
  }
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken
  }
  return headers
}

const createTopic = async () => {
  // Prevent double submit
  if (isCreating.value) return

  if (!validateForm()) {
    window.$message?.warning('Lutfen formu dogru sekilde doldurun')
    return
  }

  isCreating.value = true

  // Optimistic UI - prepare new topic
  const optimisticTopic = {
    id: Date.now(), // Temporary ID
    title: newTopic.title.trim(),
    author: authStore.user?.username || 'Siz',
    authorAvatar: authStore.user?.avatar,
    authorOnline: true,
    created: 'Az once',
    replies: 0,
    views: 0,
    likes: 0,
    isPinned: false,
    isLocked: false,
    isSolved: false,
    isHot: false,
    tags: [...newTopic.tags],
    preview: newTopic.content.trim().substring(0, 150) + '...'
  }

  try {
    const response = await fetch('/api/forum/topics', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        category_id: category.value?.id || parseInt(categoryId) || categoryId,
        title: newTopic.title.trim(),
        content: newTopic.content.trim(),
        tags: newTopic.tags,
        type: newTopic.type
      })
    })

    if (response.ok) {
      const data = await response.json().catch((e) => { console.warn('JSON parse error:', e); return {} })
      showNewTopicModal.value = false
      newTopic.title = ''
      newTopic.content = ''
      newTopic.tags = []
      newTopic.type = 'discussion'
      window.$message?.success('Konu başarıyla oluşturuldu')

      // Navigate to new topic if ID available, otherwise refresh list
      if (data.id || data.topic?.id) {
        router.push(`/forum/topic/${data.id || data.topic.id}`)
      } else {
        fetchTopics()
      }
    } else {
      const error = await response.json().catch(() => ({}))
      if (response.status === 401) {
        window.$message?.error('Oturum suresi doldu, lutfen tekrar giriş yapin')
        router.push({ name: 'login', query: { redirect: route.fullPath } })
      } else if (response.status === 403) {
        window.$message?.error('Bu işlemi yapma yetkiniz yok')
      } else {
        window.$message?.error(error.detail || 'Konu oluşturulamadi')
      }
    }
  } catch (error) {
    console.error('Create topic error:', error)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      window.$message?.error('Ag bağlantisi hatasi, lutfen internet bağlantinizi kontrol edin')
    } else {
      window.$message?.error('Bir hata oluştu, lutfen tekrar deneyin')
    }
  } finally {
    isCreating.value = false
  }
}

// Error state
const fetchError = ref(null)

// Fetch topics from API
const fetchTopics = async () => {
  isLoading.value = true
  fetchError.value = null
  try {
    const response = await fetch(`/api/forum/categories/${categoryId}/topics`)
    if (response.ok) {
      const data = await response.json()
      // Map API response to frontend format
      topics.value = (data.topics || []).map(t => ({
        id: t.id,
        title: t.title,
        slug: t.slug,
        author: t.author_name || t.author?.username || 'Anonim',
        authorAvatar: t.author_avatar || t.author?.avatar,
        authorOnline: false,
        created: formatDate(t.created_at),
        replies: t.reply_count || 0,
        views: t.view_count || 0,
        likes: t.like_count || 0,
        isPinned: t.is_pinned || false,
        isLocked: t.is_locked || false,
        isSolved: t.is_solved || t.has_best_answer || false,
        isHot: (t.view_count || 0) > 100 || (t.reply_count || 0) > 10,
        tags: t.tags || [],
        lastReply: t.last_reply ? {
          author: t.last_reply.author_name,
          time: formatDate(t.last_reply.created_at)
        } : null,
        preview: t.content ? t.content.substring(0, 150) + '...' : ''
      }))
      if (data.category) {
        category.value = {
          id: data.category.id,
          name: data.category.name,
          slug: data.category.slug,
          description: data.category.description,
          icon: data.category.icon,
          color: data.category.color,
          game_slug: data.category.game_slug
        }
        // Load game banner after category is fetched
        loadGameBanner()
      }
    } else {
      const errorData = await response.json().catch(() => ({}))
      fetchError.value = errorData.detail || `Kategori yüklenemedi (${response.status})`
      console.error('Category fetch failed:', response.status, errorData)
    }
  } catch (error) {
    fetchError.value = 'Bağlanti hatasi oluştu'
    console.error('Failed to fetch topics:', error)
  } finally {
    isLoading.value = false
  }
}

// Format date helper
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (mins < 1) return 'Az once'
  if (mins < 60) return `${mins} dk once`
  if (hours < 24) return `${hours} saat once`
  if (days < 7) return `${days} gun once`
  return date.toLocaleDateString('tr-TR')
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (sortDropdownOpen.value && !event.target.closest('.forum-sort-dropdown')) {
    sortDropdownOpen.value = false
  }
}

// Keyboard handler for modal and shortcuts
const handleKeydown = (event) => {
  // Close modals on Escape
  if (event.key === 'Escape') {
    if (showNewTopicModal.value) {
      showNewTopicModal.value = false
      event.preventDefault()
    }
    if (sortDropdownOpen.value) {
      sortDropdownOpen.value = false
      event.preventDefault()
    }
  }

  // Submit form on Ctrl+Enter when modal is open
  if (event.ctrlKey && event.key === 'Enter' && showNewTopicModal.value) {
    event.preventDefault()
    createTopic()
  }

  // Open new topic modal on 'N' key when not in input
  if (event.key === 'n' || event.key === 'N') {
    if (event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
      event.preventDefault()
      handleNewTopic()
    }
  }
}

// Watchers - Debounced search to prevent excessive filtering
watch(searchQuery, () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
  }, 300)
})

// Watch sortBy for persistence
watch(sortBy, (newSort) => {
  localStorage.setItem('forum_category_sort', newSort)
})

// Infinite scroll
const infiniteScrollEnabled = ref(false)
const loadingMore = ref(false)

const handleScroll = () => {
  // Back to top button visibility
  showBackToTop.value = window.scrollY > 400

  // Infinite scroll logic
  if (!infiniteScrollEnabled.value || loadingMore.value) return

  const scrollHeight = document.documentElement.scrollHeight
  const scrollTop = document.documentElement.scrollTop
  const clientHeight = document.documentElement.clientHeight

  if (scrollTop + clientHeight >= scrollHeight - 200) {
    if (currentPage.value < totalPages.value) {
      loadingMore.value = true
      setTimeout(() => {
        currentPage.value++
        loadingMore.value = false
      }, 300)
    }
  }
}

// Toggle infinite scroll
const toggleInfiniteScroll = () => {
  infiniteScrollEnabled.value = !infiniteScrollEnabled.value
  if (infiniteScrollEnabled.value) {
    window.addEventListener('scroll', handleScroll)
  } else {
    window.removeEventListener('scroll', handleScroll)
  }
}

// Subscribe to category
const isSubscribed = ref(false)
const subscribeToCategory = async () => {
  if (!isLoggedIn.value) {
    window.$message?.warning('Abone olmak icin giriş yapin')
    return
  }

  try {
    const response = await fetch(`/api/forum/categories/${categoryId}/subscribe`, {
      method: isSubscribed.value ? 'DELETE' : 'POST',
      headers: getHeaders()
    })

    if (response.ok) {
      isSubscribed.value = !isSubscribed.value
      window.$message?.success(isSubscribed.value ? 'Kategoriye abone olundu' : 'Abonelik iptal edildi')
    } else {
      window.$message?.error('İşlem başarısız oldu')
    }
  } catch (error) {
    console.error('Subscribe error:', error)
    window.$message?.error('Bir hata oluştu')
  }
}

// Lifecycle
let onlineUsersInterval = null

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
  window.addEventListener('scroll', handleScroll)  // Always listen for back-to-top
  fetchTopics()  // This will also load game banner after category is fetched

  // Load saved sort preference
  const savedSort = localStorage.getItem('forum_category_sort')
  if (savedSort) {
    sortBy.value = savedSort
  }

  // Simulate online users change
  onlineUsersInterval = setInterval(() => {
    onlineUsers.value = Math.floor(Math.random() * 10) + 20
  }, 30000)
})

onUnmounted(() => {
  if (onlineUsersInterval) {
    clearInterval(onlineUsersInterval)
  }
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* ===== Visual Enhancement ===== */
.forum-page {
  position: relative;
}

.forum-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(249, 115, 22, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 100% 50%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse 50% 30% at 0% 80%, rgba(34, 211, 238, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* Floating particles */
.forum-page::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(2px 2px at 10% 20%, rgba(249, 115, 22, 0.3) 50%, transparent 50%),
    radial-gradient(2px 2px at 30% 70%, rgba(139, 92, 246, 0.3) 50%, transparent 50%),
    radial-gradient(2px 2px at 60% 30%, rgba(34, 211, 238, 0.3) 50%, transparent 50%),
    radial-gradient(2px 2px at 80% 60%, rgba(249, 115, 22, 0.3) 50%, transparent 50%),
    radial-gradient(2px 2px at 90% 10%, rgba(139, 92, 246, 0.3) 50%, transparent 50%);
  background-size: 100% 100%;
  animation: float-particles 30s linear infinite;
  pointer-events: none;
  z-index: 0;
  opacity: 0.6;
}

@keyframes float-particles {
  0% { transform: translateY(0); }
  100% { transform: translateY(-20px); }
}

/* Category Header */
.forum-category-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 15, 20, 0.95) 100%);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 12px;
  margin-bottom: 10px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.forum-category-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f97316, #8b5cf6, #22d3ee);
  animation: gradient-flow 3s ease infinite;
}

@keyframes gradient-flow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.forum-category-header:hover {
  border-color: rgba(249, 115, 22, 0.4);
  box-shadow: 0 8px 32px rgba(249, 115, 22, 0.15);
}

.forum-category-header__icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  transition: transform 0.3s ease;
}

.forum-category-header__icon:hover {
  transform: scale(1.05) rotate(5deg);
}

@keyframes icon-glow {
  0%, 100% { box-shadow: 0 8px 24px rgba(249, 115, 22, 0.3); }
  50% { box-shadow: 0 12px 32px rgba(249, 115, 22, 0.5); }
}

.forum-category-header__info {
  flex: 1;
  min-width: 0;
}

.forum-category-header__info .forum-heading {
  margin-bottom: 4px;
  font-size: 1.1rem;
}

.forum-category-header__info .forum-meta {
  margin-bottom: 8px;
  max-width: 600px;
  font-size: 0.85rem;
}

.forum-category-header__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.forum-category-header__action {
  flex-shrink: 0;
}

/* Filters */
.forum-filters {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: 10px;
  margin-bottom: 10px;
}

.forum-filters__search {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.forum-filters__search-icon {
  position: absolute;
  left: 14px;
  color: var(--forum-muted);
  transition: color 0.2s ease;
}

.forum-filters__search.focused .forum-filters__search-icon {
  color: var(--forum-accent);
}

.forum-filters__search-input {
  width: 100%;
  padding: 8px 36px;
  background: var(--forum-bg-hover);
  border: 1px solid var(--forum-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  transition: all 0.2s ease;
}

.forum-filters__search-input:focus {
  outline: none;
  border-color: var(--forum-accent);
  background: var(--forum-bg-card);
}

.forum-filters__search-input::placeholder {
  color: var(--forum-muted);
}

.forum-filters__search-clear {
  position: absolute;
  right: 12px;
  padding: 4px;
  color: var(--forum-muted);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.forum-filters__search-clear:hover {
  color: var(--text-primary);
  background: var(--forum-bg-hover);
}

.forum-filters__controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* View Toggle */
.forum-view-toggle {
  display: flex;
  background: var(--forum-bg-hover);
  border-radius: var(--forum-radius-sm);
  padding: 4px;
}

.forum-view-toggle__btn {
  padding: 6px 10px;
  border-radius: 6px;
  color: var(--forum-muted);
  transition: all 0.2s ease;
}

.forum-view-toggle__btn.active {
  background: var(--forum-bg-card);
  color: var(--forum-accent);
}

.forum-view-toggle__btn:hover:not(.active) {
  color: var(--text-primary);
}

/* Sort Dropdown */
.forum-sort-dropdown {
  position: relative;
}

.forum-sort-dropdown__trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--forum-bg-hover);
  border: 1px solid var(--forum-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.forum-sort-dropdown__trigger:hover {
  border-color: var(--forum-accent);
}

.forum-sort-dropdown__menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 180px;
  background: var(--forum-bg-panel);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius);
  padding: 8px;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.forum-sort-dropdown__option {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 6px;
  color: var(--forum-muted);
  font-size: 14px;
  transition: all 0.2s ease;
}

.forum-sort-dropdown__option:hover {
  background: var(--forum-bg-hover);
  color: var(--text-primary);
}

.forum-sort-dropdown__option.active {
  background: rgba(79, 140, 255, 0.1);
  color: var(--forum-link);
}

/* Topics List */
.forum-topics-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.forum-topics-list--compact {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 8px;
}

/* Empty State */
.forum-empty-state {
  text-align: center;
  padding: 30px 20px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: 12px;
}

.forum-empty-state__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: var(--forum-bg-hover);
  border-radius: 50%;
  margin-bottom: 12px;
  color: var(--forum-muted);
}

.forum-empty-state .forum-heading {
  margin-bottom: 8px;
  font-size: 1rem;
}

.forum-empty-state .forum-meta {
  margin-bottom: 12px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  font-size: 0.85rem;
}

.forum-empty-state__actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* Error State */
.forum-error-state {
  text-align: center;
  padding: 30px 20px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-danger);
  border-radius: 12px;
}

.forum-error-state__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 50%;
  margin-bottom: 12px;
}

.forum-error-state .forum-heading {
  margin-bottom: 8px;
  color: var(--forum-danger);
  font-size: 1rem;
}

.forum-error-state .forum-meta {
  margin-bottom: 12px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  font-size: 0.85rem;
}

.forum-error-state__actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* Pagination */
.forum-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  padding: 10px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: 10px;
}

.forum-pagination__btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--forum-bg-hover);
  border: 1px solid var(--forum-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 12px;
  transition: all 0.2s ease;
}

.forum-pagination__btn:hover:not(:disabled) {
  border-color: var(--forum-accent);
  color: var(--forum-accent);
}

.forum-pagination__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.forum-pagination__pages {
  display: flex;
  gap: 4px;
}

.forum-pagination__page {
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--forum-muted);
  font-size: 12px;
  transition: all 0.2s ease;
}

.forum-pagination__page:hover:not(:disabled):not(.active) {
  background: var(--forum-bg-hover);
  color: var(--text-primary);
}

.forum-pagination__page.active {
  background: var(--forum-accent);
  color: white;
}

.forum-pagination__page.ellipsis {
  cursor: default;
}

/* Sidebar Cards */
.forum-sidebar-card {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 15, 20, 0.95) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 8px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.forum-sidebar-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(249, 115, 22, 0.05), transparent);
  transition: left 0.5s ease;
}

.forum-sidebar-card:hover::before {
  left: 100%;
}

.forum-sidebar-card:hover {
  border-color: rgba(139, 92, 246, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.1);
}

.forum-sidebar-card__title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

/* Online Indicator */
.forum-online-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.forum-online-dot {
  width: 10px;
  height: 10px;
  background: var(--forum-success);
  border-radius: 50%;
  animation: forum-online-pulse 2s ease-in-out infinite;
}

@keyframes forum-online-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

.forum-online-count {
  font-size: 24px;
  font-weight: 700;
  color: var(--forum-success);
}

/* Stats Grid */
.forum-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.forum-stat-box {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 1px solid rgba(34, 211, 238, 0.1);
  border-radius: var(--forum-radius-sm);
  padding: 12px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: default;
}

.forum-stat-box:hover {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-color: rgba(34, 211, 238, 0.3);
  transform: translateY(-2px);
}

.forum-stat-box__value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--forum-accent);
  text-shadow: 0 0 20px rgba(34, 211, 238, 0.5);
}

.forum-stat-box__label {
  font-size: 11px;
  color: var(--forum-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Sidebar Categories */
.forum-sidebar-categories {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.forum-sidebar-category {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--forum-radius-sm);
  color: var(--forum-muted);
  font-size: 14px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.forum-sidebar-category::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #f97316, #8b5cf6);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.forum-sidebar-category:hover {
  background: linear-gradient(90deg, rgba(79, 140, 255, 0.1) 0%, transparent 100%);
  color: var(--forum-link);
  padding-left: 16px;
}

.forum-sidebar-category:hover::before {
  opacity: 1;
}

/* Modal */
.forum-modal__content {
  width: 100%;
  max-width: 600px;
  background: var(--forum-bg-panel);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius-lg);
  overflow: hidden;
}

.forum-modal__header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  border-bottom: 1px solid var(--forum-border);
}

.forum-modal__close {
  margin-left: auto;
  padding: 8px;
  color: var(--forum-muted);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.forum-modal__close:hover {
  background: var(--forum-bg-hover);
  color: var(--text-primary);
}

.forum-modal__form {
  padding: 24px;
}

.forum-modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  background: var(--forum-bg-hover);
  border-top: 1px solid var(--forum-border);
}

/* Form Styles */
.forum-form-group {
  margin-bottom: 20px;
}

.forum-form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.forum-form-input,
.forum-form-textarea {
  width: 100%;
  padding: 12px 16px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius-sm);
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s ease;
}

.forum-form-input:focus,
.forum-form-textarea:focus {
  outline: none;
  border-color: var(--forum-accent);
}

.forum-form-input.error,
.forum-form-textarea.error {
  border-color: var(--forum-danger);
}

.forum-form-textarea {
  resize: vertical;
  min-height: 120px;
}

.forum-form-counter {
  display: block;
  text-align: right;
  font-size: 12px;
  color: var(--forum-muted);
  margin-top: 4px;
}

.forum-form-counter.warning {
  color: var(--forum-danger);
}

.forum-form-error {
  color: var(--forum-danger);
  font-size: 13px;
  margin-top: 6px;
}

.forum-form-hint {
  color: var(--forum-muted);
  font-size: 12px;
  margin-top: 6px;
}

/* Type Selector */
.forum-type-selector {
  display: flex;
  gap: 8px;
}

.forum-type-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius-sm);
  color: var(--forum-muted);
  font-size: 14px;
  transition: all 0.2s ease;
}

.forum-type-option:hover {
  border-color: var(--forum-accent);
  color: var(--text-primary);
}

.forum-type-option.active {
  background: rgba(79, 140, 255, 0.1);
  border-color: var(--forum-link);
  color: var(--forum-link);
}

/* Tags Input */
.forum-tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 12px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius-sm);
}

.forum-tags-input input {
  flex: 1;
  min-width: 100px;
  padding: 4px 0;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 14px;
}

.forum-tags-input input:focus {
  outline: none;
}

.forum-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(79, 140, 255, 0.1);
  border-radius: 20px;
  color: var(--forum-link);
  font-size: 13px;
}

.forum-tag button {
  display: flex;
  color: var(--forum-link);
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.forum-tag button:hover {
  opacity: 1;
}

/* Dropdown Animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Responsive */
@media (max-width: 768px) {
  .forum-category-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 24px;
  }

  .forum-category-header__info .forum-meta {
    margin-left: auto;
    margin-right: auto;
  }

  .forum-category-header__stats {
    justify-content: center;
  }

  .forum-filters {
    flex-direction: column;
  }

  .forum-filters__search {
    width: 100%;
  }

  .forum-filters__controls {
    width: 100%;
    justify-content: space-between;
  }

  .forum-pagination {
    flex-wrap: wrap;
  }
}

/* ===== Category Game Banner ===== */
.forum-category-banner {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
  border: 1px solid rgba(249, 115, 22, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.forum-category-banner::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  pointer-events: none;
}

.forum-category-banner__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.forum-category-banner:hover .forum-category-banner__img {
  transform: scale(1.05);
}

.forum-category-banner__overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.4) 40%, rgba(0,0,0,0.9) 100%),
    linear-gradient(90deg, rgba(249, 115, 22, 0.1) 0%, transparent 50%, rgba(139, 92, 246, 0.1) 100%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 24px;
}

.forum-category-banner__logo {
  max-width: 220px;
  max-height: 80px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.8));
  animation: logo-float 3s ease-in-out infinite;
}

@keyframes logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

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

@media (max-width: 768px) {
  .back-to-top { bottom: 20px; right: 20px; width: 45px; height: 45px; }
  .forum-category-banner {
    height: 140px;
    border-radius: 12px;
    margin-bottom: 16px;
  }

  .forum-category-banner__logo {
    max-width: 140px;
    max-height: 50px;
  }
}
</style>
