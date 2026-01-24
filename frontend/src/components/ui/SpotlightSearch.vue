<template>
  <Teleport to="body">
    <Transition name="spotlight">
      <div v-if="isOpen" class="spotlight-overlay" @click.self="close">
        <div class="spotlight-container">
          <!-- Search Input -->
          <div class="spotlight-input-wrapper">
            <SearchIcon class="spotlight-search-icon" />
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              class="spotlight-input"
              placeholder="Ara... (kullanici, konu, sunucu, turnuva)"
              @keydown="handleKeydown"
            />
            <div class="spotlight-shortcuts">
              <kbd class="spotlight-key">ESC</kbd>
              <span class="spotlight-key-label">kapat</span>
            </div>
          </div>

          <!-- Category Filters -->
          <div class="spotlight-filters" v-if="!query">
            <button
              v-for="cat in categories"
              :key="cat.id"
              class="spotlight-filter-btn"
              :class="{ active: selectedCategory === cat.id }"
              @click="selectedCategory = cat.id"
            >
              <component :is="cat.icon" class="w-4 h-4" />
              {{ cat.label }}
            </button>
          </div>

          <!-- Results -->
          <div class="spotlight-results" v-if="query || selectedCategory">
            <!-- Loading State -->
            <div v-if="loading" class="spotlight-loading">
              <div class="spotlight-loading-spinner"></div>
              <span>Araniyor...</span>
            </div>

            <!-- Results List -->
            <template v-else-if="groupedResults.length > 0">
              <div v-for="group in groupedResults" :key="group.category" class="spotlight-group">
                <div class="spotlight-category-header">
                  <component :is="getCategoryIcon(group.category)" class="w-4 h-4" />
                  {{ getCategoryLabel(group.category) }}
                  <span class="spotlight-category-count">{{ group.items.length }}</span>
                </div>
                <div class="spotlight-items">
                  <div
                    v-for="(item, idx) in group.items"
                    :key="item.id"
                    class="spotlight-item"
                    :class="{ active: activeIndex === getGlobalIndex(group.category, idx) }"
                    @click="selectItem(item)"
                    @mouseenter="activeIndex = getGlobalIndex(group.category, idx)"
                  >
                    <div class="spotlight-item-icon" :class="item.type">
                      <component :is="getItemIcon(item)" class="w-5 h-5" />
                    </div>
                    <div class="spotlight-item-content">
                      <div class="spotlight-item-title" v-html="highlightMatch(item.title)"></div>
                      <div class="spotlight-item-subtitle">{{ item.subtitle }}</div>
                    </div>
                    <div class="spotlight-item-meta" v-if="item.meta">
                      {{ item.meta }}
                    </div>
                    <ArrowRightIcon class="spotlight-item-arrow" />
                  </div>
                </div>
              </div>
            </template>

            <!-- No Results -->
            <div v-else-if="query && !loading" class="spotlight-empty">
              <SearchXIcon class="spotlight-empty-icon" />
              <span class="spotlight-empty-title">Sonuc bulunamadi</span>
              <span class="spotlight-empty-subtitle">"{{ query }}" icin sonuc yok</span>
            </div>

            <!-- Quick Actions (when no query) -->
            <div v-else-if="!query && quickActions.length > 0" class="spotlight-quick-actions">
              <div class="spotlight-category-header">
                <ZapIcon class="w-4 h-4" />
                Hizli Islemler
              </div>
              <div class="spotlight-items">
                <div
                  v-for="(action, idx) in quickActions"
                  :key="action.id"
                  class="spotlight-item"
                  :class="{ active: activeIndex === idx }"
                  @click="executeAction(action)"
                  @mouseenter="activeIndex = idx"
                >
                  <div class="spotlight-item-icon action">
                    <component :is="action.icon" class="w-5 h-5" />
                  </div>
                  <div class="spotlight-item-content">
                    <div class="spotlight-item-title">{{ action.label }}</div>
                    <div class="spotlight-item-subtitle">{{ action.description }}</div>
                  </div>
                  <div class="spotlight-shortcut" v-if="action.shortcut">
                    <kbd v-for="key in action.shortcut" :key="key" class="spotlight-key">{{ key }}</kbd>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Searches -->
          <div class="spotlight-recent" v-if="!query && recentSearches.length > 0">
            <div class="spotlight-recent-header">
              <ClockIcon class="w-4 h-4" />
              <span>Son Aramalar</span>
              <button class="spotlight-clear-btn" @click="clearRecentSearches">Temizle</button>
            </div>
            <div class="spotlight-recent-items">
              <button
                v-for="recent in recentSearches"
                :key="recent"
                class="spotlight-recent-item"
                @click="query = recent"
              >
                <HistoryIcon class="w-4 h-4" />
                {{ recent }}
              </button>
            </div>
          </div>

          <!-- Footer -->
          <div class="spotlight-footer">
            <div class="spotlight-footer-hint">
              <kbd class="spotlight-key">↑↓</kbd>
              <span>gezin</span>
              <kbd class="spotlight-key">Enter</kbd>
              <span>sec</span>
              <kbd class="spotlight-key">Tab</kbd>
              <span>kategori</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import {
  SearchIcon,
  SearchXIcon,
  ArrowRightIcon,
  UserIcon,
  MessageSquareIcon,
  ServerIcon,
  TrophyIcon,
  ShoppingBagIcon,
  ZapIcon,
  ClockIcon,
  HistoryIcon,
  HomeIcon,
  SettingsIcon,
  PlusCircleIcon,
  LogInIcon
} from 'lucide-vue-next'

const router = useRouter()

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

// State
const inputRef = ref(null)
const query = ref('')
const loading = ref(false)
const results = ref([])
const activeIndex = ref(0)
const selectedCategory = ref(null)
const recentSearches = ref([])

// Computed
const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const categories = [
  { id: 'all', label: 'Tumu', icon: SearchIcon },
  { id: 'users', label: 'Kullanicilar', icon: UserIcon },
  { id: 'topics', label: 'Konular', icon: MessageSquareIcon },
  { id: 'servers', label: 'Sunucular', icon: ServerIcon },
  { id: 'tournaments', label: 'Turnuvalar', icon: TrophyIcon }
]

const quickActions = [
  { id: 'home', label: 'Ana Sayfaya Git', description: 'Ana sayfayi ac', icon: HomeIcon, action: () => router.push('/'), shortcut: ['G', 'H'] },
  { id: 'forum', label: 'Yeni Konu Olustur', description: 'Forum\'da yeni konu ac', icon: PlusCircleIcon, action: () => router.push('/forum/new'), shortcut: ['G', 'N'] },
  { id: 'servers', label: 'Sunucularim', description: 'Sunucularini yonet', icon: ServerIcon, action: () => router.push('/servers'), shortcut: ['G', 'S'] },
  { id: 'shop', label: 'Magaza', description: 'Sunucu kirala', icon: ShoppingBagIcon, action: () => router.push('/shop'), shortcut: ['G', 'M'] },
  { id: 'settings', label: 'Ayarlar', description: 'Profil ayarlari', icon: SettingsIcon, action: () => router.push('/profile/settings'), shortcut: ['G', 'A'] }
]

const groupedResults = computed(() => {
  if (!results.value.length) return []

  const groups = {}
  results.value.forEach(item => {
    if (!groups[item.type]) {
      groups[item.type] = []
    }
    groups[item.type].push(item)
  })

  return Object.entries(groups).map(([category, items]) => ({
    category,
    items: items.slice(0, 5) // Max 5 per category
  }))
})

// Methods
const close = () => {
  isOpen.value = false
  query.value = ''
  activeIndex.value = 0
  selectedCategory.value = null
}

const getCategoryIcon = (category) => {
  const icons = {
    users: UserIcon,
    topics: MessageSquareIcon,
    servers: ServerIcon,
    tournaments: TrophyIcon,
    shop: ShoppingBagIcon
  }
  return icons[category] || SearchIcon
}

const getCategoryLabel = (category) => {
  const labels = {
    users: 'Kullanicilar',
    topics: 'Forum Konulari',
    servers: 'Sunucular',
    tournaments: 'Turnuvalar',
    shop: 'Magaza'
  }
  return labels[category] || category
}

const getItemIcon = (item) => {
  return getCategoryIcon(item.type)
}

const getGlobalIndex = (category, localIndex) => {
  let globalIndex = 0
  for (const group of groupedResults.value) {
    if (group.category === category) {
      return globalIndex + localIndex
    }
    globalIndex += group.items.length
  }
  return globalIndex
}

const highlightMatch = (text) => {
  if (!query.value) return text
  const regex = new RegExp(`(${query.value})`, 'gi')
  return text.replace(regex, '<mark class="spotlight-highlight">$1</mark>')
}

const selectItem = (item) => {
  // Save to recent searches
  saveRecentSearch(query.value)

  // Navigate based on type
  switch (item.type) {
    case 'users':
      router.push(`/profile/${item.id}`)
      break
    case 'topics':
      router.push(`/forum/topic/${item.id}`)
      break
    case 'servers':
      router.push(`/server/${item.id}`)
      break
    case 'tournaments':
      router.push(`/tournament/${item.id}`)
      break
    default:
      if (item.url) router.push(item.url)
  }

  close()
}

const executeAction = (action) => {
  if (action.action) {
    action.action()
  }
  close()
}

const handleKeydown = (e) => {
  const totalItems = query.value
    ? groupedResults.value.reduce((sum, g) => sum + g.items.length, 0)
    : quickActions.length

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      activeIndex.value = (activeIndex.value + 1) % totalItems
      break
    case 'ArrowUp':
      e.preventDefault()
      activeIndex.value = (activeIndex.value - 1 + totalItems) % totalItems
      break
    case 'Enter':
      e.preventDefault()
      if (query.value && groupedResults.value.length > 0) {
        let currentIdx = 0
        for (const group of groupedResults.value) {
          for (const item of group.items) {
            if (currentIdx === activeIndex.value) {
              selectItem(item)
              return
            }
            currentIdx++
          }
        }
      } else if (!query.value && quickActions[activeIndex.value]) {
        executeAction(quickActions[activeIndex.value])
      }
      break
    case 'Escape':
      close()
      break
    case 'Tab':
      e.preventDefault()
      const catIndex = categories.findIndex(c => c.id === selectedCategory.value)
      selectedCategory.value = categories[(catIndex + 1) % categories.length].id
      break
  }
}

// Search API
const searchAPI = async (searchQuery, category) => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      q: searchQuery,
      limit: 20
    })
    if (category && category !== 'all') {
      params.append('type', category)
    }

    const response = await fetch(`/api/search?${params}`)
    if (response.ok) {
      const data = await response.json()
      results.value = data.results || []
    }
  } catch (err) {
    console.error('Search error:', err)
    results.value = []
  } finally {
    loading.value = false
  }
}

const debouncedSearch = useDebounceFn((q, cat) => {
  if (q.length >= 2) {
    searchAPI(q, cat)
  } else {
    results.value = []
  }
}, 300)

// Recent searches
const loadRecentSearches = () => {
  try {
    const saved = localStorage.getItem('spotlight_recent_searches')
    recentSearches.value = saved ? JSON.parse(saved) : []
  } catch {
    recentSearches.value = []
  }
}

const saveRecentSearch = (search) => {
  if (!search || search.length < 2) return
  const searches = recentSearches.value.filter(s => s !== search)
  searches.unshift(search)
  recentSearches.value = searches.slice(0, 5)
  localStorage.setItem('spotlight_recent_searches', JSON.stringify(recentSearches.value))
}

const clearRecentSearches = () => {
  recentSearches.value = []
  localStorage.removeItem('spotlight_recent_searches')
}

// Keyboard shortcut (Ctrl+K / Cmd+K)
const handleGlobalKeydown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    isOpen.value = !isOpen.value
  }
}

// Watchers
watch(query, (newQuery) => {
  activeIndex.value = 0
  debouncedSearch(newQuery, selectedCategory.value)
})

watch(selectedCategory, (newCat) => {
  if (query.value) {
    debouncedSearch(query.value, newCat)
  }
})

watch(isOpen, async (open) => {
  if (open) {
    await nextTick()
    inputRef.value?.focus()
    loadRecentSearches()
  }
})

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped>
.spotlight-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  justify-content: center;
  padding-top: 15vh;
}

.spotlight-container {
  width: 100%;
  max-width: 640px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.spotlight-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #27272a;
}

.spotlight-search-icon {
  width: 20px;
  height: 20px;
  color: #71717a;
  flex-shrink: 0;
}

.spotlight-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 16px;
  color: #fafafa;
}

.spotlight-input::placeholder {
  color: #52525b;
}

.spotlight-shortcuts {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #52525b;
  font-size: 12px;
}

.spotlight-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: #27272a;
  border: 1px solid #3f3f46;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #a1a1aa;
}

.spotlight-key-label {
  margin-left: 4px;
}

.spotlight-filters {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  border-bottom: 1px solid #27272a;
  overflow-x: auto;
}

.spotlight-filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #27272a;
  border: 1px solid transparent;
  border-radius: 8px;
  color: #a1a1aa;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.spotlight-filter-btn:hover {
  background: #3f3f46;
  color: #fafafa;
}

.spotlight-filter-btn.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
}

.spotlight-results {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.spotlight-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px;
  color: #71717a;
}

.spotlight-loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #27272a;
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spotlight-group {
  margin-bottom: 8px;
}

.spotlight-category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 600;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.spotlight-category-count {
  margin-left: auto;
  padding: 2px 6px;
  background: #27272a;
  border-radius: 10px;
  font-size: 10px;
}

.spotlight-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.spotlight-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
}

.spotlight-item:hover,
.spotlight-item.active {
  background: rgba(249, 115, 22, 0.1);
}

.spotlight-item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #27272a;
  color: #a1a1aa;
  flex-shrink: 0;
  transition: all 0.15s;
}

.spotlight-item.active .spotlight-item-icon,
.spotlight-item:hover .spotlight-item-icon {
  background: #f97316;
  color: white;
}

.spotlight-item-icon.users { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
.spotlight-item-icon.topics { background: rgba(6, 182, 212, 0.15); color: #22d3ee; }
.spotlight-item-icon.servers { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.spotlight-item-icon.tournaments { background: rgba(234, 179, 8, 0.15); color: #facc15; }
.spotlight-item-icon.action { background: rgba(249, 115, 22, 0.15); color: #fb923c; }

.spotlight-item-content {
  flex: 1;
  min-width: 0;
}

.spotlight-item-title {
  font-size: 14px;
  font-weight: 500;
  color: #fafafa;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spotlight-item-title :deep(.spotlight-highlight) {
  background: rgba(249, 115, 22, 0.3);
  color: #fb923c;
  padding: 0 2px;
  border-radius: 2px;
}

.spotlight-item-subtitle {
  font-size: 12px;
  color: #71717a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spotlight-item-meta {
  font-size: 12px;
  color: #52525b;
  white-space: nowrap;
}

.spotlight-item-arrow {
  width: 16px;
  height: 16px;
  color: #52525b;
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.15s;
}

.spotlight-item:hover .spotlight-item-arrow,
.spotlight-item.active .spotlight-item-arrow {
  opacity: 1;
  transform: translateX(0);
}

.spotlight-shortcut {
  display: flex;
  gap: 4px;
}

.spotlight-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.spotlight-empty-icon {
  width: 48px;
  height: 48px;
  color: #3f3f46;
  margin-bottom: 16px;
}

.spotlight-empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #a1a1aa;
  margin-bottom: 4px;
}

.spotlight-empty-subtitle {
  font-size: 14px;
  color: #52525b;
}

.spotlight-recent {
  padding: 12px 20px;
  border-top: 1px solid #27272a;
}

.spotlight-recent-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #71717a;
}

.spotlight-clear-btn {
  margin-left: auto;
  padding: 4px 8px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: #f97316;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.15s;
}

.spotlight-clear-btn:hover {
  background: rgba(249, 115, 22, 0.1);
}

.spotlight-recent-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.spotlight-recent-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #27272a;
  border: none;
  border-radius: 8px;
  color: #a1a1aa;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.spotlight-recent-item:hover {
  background: #3f3f46;
  color: #fafafa;
}

.spotlight-footer {
  padding: 12px 20px;
  border-top: 1px solid #27272a;
  background: #0f0f12;
}

.spotlight-footer-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #52525b;
}

.spotlight-footer-hint .spotlight-key {
  margin-right: 4px;
}

.spotlight-quick-actions {
  padding: 8px 0;
}

/* Transitions */
.spotlight-enter-active {
  transition: all 0.2s ease-out;
}

.spotlight-leave-active {
  transition: all 0.15s ease-in;
}

.spotlight-enter-from {
  opacity: 0;
}

.spotlight-enter-from .spotlight-container {
  transform: scale(0.95) translateY(-20px);
}

.spotlight-leave-to {
  opacity: 0;
}

.spotlight-leave-to .spotlight-container {
  transform: scale(0.95) translateY(-10px);
}

/* Mobile */
@media (max-width: 640px) {
  .spotlight-overlay {
    padding: 16px;
    padding-top: 10vh;
  }

  .spotlight-container {
    max-height: 80vh;
  }

  .spotlight-shortcuts {
    display: none;
  }
}
</style>
