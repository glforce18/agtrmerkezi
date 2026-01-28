<template>
  <div class="relative min-h-screen">
    <!-- Background -->
    <div class="fixed inset-0 z-0">
      <img :src="getBackgroundImage('scifi')" alt="" class="absolute inset-0 w-full h-full object-cover opacity-55" />
      <div class="absolute inset-0 bg-gradient-to-b from-dark-bg/50 via-dark-bg/60 to-dark-bg/70"></div>
    </div>

    <div class="container mx-auto px-4 py-8 max-w-[1400px] relative z-10">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Left Sidebar - Categories -->
      <div class="lg:col-span-3 hidden lg:block">
        <CategorySidebar
          :categories="categories"
          :selected-category="null"
          :selected-filter="currentFilter"
          @filter-change="handleFilterChange"
        />
      </div>

      <!-- Main Content -->
      <div class="lg:col-span-6">
        <!-- Enhanced Header -->
        <div class="relative mb-8 p-6 rounded-2xl bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border border-primary/20 backdrop-blur-sm overflow-hidden">
          <div class="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl"></div>
          <div class="relative">
            <div class="flex items-center gap-3 mb-3">
              <div class="p-2 bg-primary/10 rounded-xl">
                <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"/>
                </svg>
              </div>
              <div>
                <h1 class="text-4xl font-bold bg-gradient-to-r from-text-primary via-primary to-orange-500 bg-clip-text text-transparent">Forum</h1>
                <p class="text-text-secondary text-sm mt-1">Topluluğumuzla bağlantıda kalın, sorularınızı sorun ve deneyimlerinizi paylaşın</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Mobile Category Filter -->
        <div class="lg:hidden mb-6">
          <button
            @click="showMobileFilters = !showMobileFilters"
            class="btn btn-secondary w-full"
          >
            {{ currentFilterLabel }}
            <span class="ml-2">{{ showMobileFilters ? '▲' : '▼' }}</span>
          </button>

          <div v-if="showMobileFilters" class="card p-4 mt-2">
            <div class="space-y-2">
              <button
                v-for="filter in filters"
                :key="filter.value"
                @click="handleFilterChange(filter.value); showMobileFilters = false"
                class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors"
                :class="currentFilter === filter.value ? 'bg-primary/10 text-primary' : 'text-text-secondary hover:bg-dark-hover'"
              >
                {{ filter.icon }} {{ filter.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- Enhanced Search & New Topic -->
        <div class="flex gap-3 mb-8">
          <div class="flex-1 relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Konularda ara..."
              class="w-full pl-11 pr-4 py-3 bg-dark-elevated/80 border border-dark-border/50 rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
              @input="handleSearch"
            />
          </div>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/forum/topic/new"
            class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-orange-600 hover:from-primary/90 hover:to-orange-500 text-white font-semibold rounded-xl shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/40 transition-all duration-300 hover:scale-105 whitespace-nowrap"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Yeni Konu
          </router-link>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="space-y-4">
          <div v-for="i in 5" :key="i" class="skeleton h-32 rounded-lg"></div>
        </div>

        <!-- Topics List -->
        <div v-else-if="filteredTopics.length" class="space-y-6">
          <TopicCard
            v-for="topic in filteredTopics"
            :key="topic.id"
            :topic="topic"
          />

          <!-- Load More -->
          <div v-if="hasMore" class="text-center pt-4">
            <button @click="loadMore" class="btn btn-secondary">
              Daha Fazla Yükle
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-state card">
          <div class="empty-state-icon">💬</div>
          <p class="empty-state-title">Henüz konu yok</p>
          <p class="empty-state-description">
            {{ searchQuery ? 'Aramanızla eşleşen konu bulunamadı' : 'İlk konuyu siz açın!' }}
          </p>
          <router-link v-if="!searchQuery && authStore.isAuthenticated" to="/forum/topic/new" class="btn btn-primary mt-4">
            İlk Konuyu Aç
          </router-link>
        </div>
      </div>

      <!-- Right Sidebar - Stats -->
      <div class="lg:col-span-3 hidden xl:block">
        <ForumStats
          :stats="stats"
          :trending-topics="trendingTopics"
          :online-users="onlineUsers"
        />
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import forumAPI from '@/api/forum'
import CategorySidebar from '@/components/forum/CategorySidebar.vue'
import ForumStats from '@/components/forum/ForumStats.vue'
import TopicCard from '@/components/forum/TopicCard.vue'

const authStore = useAuthStore()

const loading = ref(true)
const categories = ref([])
const topics = ref([])
const stats = ref({})
const trendingTopics = ref([])
const onlineUsers = ref([])
const searchQuery = ref('')
const currentFilter = ref('recent')
const showMobileFilters = ref(false)
const hasMore = ref(false)

const filters = [
  { value: 'recent', label: 'Son Konular', icon: '🕒' },
  { value: 'popular', label: 'Popüler', icon: '🔥' },
  { value: 'unanswered', label: 'Yanıtsız', icon: '💬' },
  { value: 'solved', label: 'Çözüldü', icon: '✅' }
]

const currentFilterLabel = computed(() => {
  const filter = filters.find(f => f.value === currentFilter.value)
  return filter ? `${filter.icon} ${filter.label}` : 'Filtrele'
})

const filteredTopics = computed(() => {
  // Ensure topics.value is always an array
  let result = Array.isArray(topics.value) ? topics.value : []

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(topic =>
      topic.title?.toLowerCase().includes(query) ||
      (topic.content && topic.content.toLowerCase().includes(query))
    )
  }

  // Sort filter
  switch (currentFilter.value) {
    case 'popular':
      result = [...result].sort((a, b) => (b.reply_count || 0) - (a.reply_count || 0))
      break
    case 'unanswered':
      result = result.filter(t => (t.reply_count || 0) === 0)
      break
    case 'solved':
      result = result.filter(t => t.is_solved)
      break
    default: // recent
      result = [...result].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  return result
})

onMounted(async () => {
  await Promise.all([
    fetchCategories(),
    fetchTopics(),
    fetchStats()
  ])
})

const fetchCategories = async () => {
  try {
    const response = await forumAPI.getCategories()
    // Ensure categories is always an array
    categories.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Failed to fetch categories:', error)
    categories.value = [] // Ensure it's always an array
    // Show error to user
    if (window.showToast) {
      window.showToast('Kategoriler yüklenemedi', 'error')
    }
  }
}

const fetchTopics = async () => {
  try {
    loading.value = true
    const response = await forumAPI.getTopics({ limit: 20, sort: currentFilter.value })
    // API format: { success: true, data: [...], pagination: {...} }
    const data = response.data.data || response.data
    topics.value = Array.isArray(data) ? data : []
    // Safe pagination access
    const pagination = response.data.pagination
    hasMore.value = pagination ? (pagination.total_pages > pagination.page) : false
  } catch (error) {
    console.error('Failed to fetch topics:', error)
    topics.value = [] // Ensure it's always an array
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    // Fetch real stats from API
    const statsResponse = await forumAPI.getForumStats()
    stats.value = statsResponse.data || {
      total_topics: 0,
      total_replies: 0,
      total_users: 0,
      online_users: 0
    }

    // Fetch trending topics from API
    try {
      const trendingResponse = await forumAPI.getTrendingTopics({ limit: 5 })
      const trendingData = trendingResponse.data.data || trendingResponse.data
      trendingTopics.value = Array.isArray(trendingData) ? trendingData : []
    } catch (error) {
      console.error('Failed to fetch trending topics:', error)
      trendingTopics.value = []
    }

    // Online users can be empty for now (feature not implemented yet)
    onlineUsers.value = []
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    stats.value = {
      total_topics: 0,
      total_replies: 0,
      total_users: 0,
      online_users: 0
    }
  }
}

const handleFilterChange = (filter) => {
  currentFilter.value = filter
  fetchTopics()
}

const handleSearch = () => {
  // Search is done client-side via computed property
  // For production, consider server-side search
}

const loadMore = () => {
  // Implement pagination
  console.log('Load more topics')
}

// Background image helper
const getBackgroundImage = (name) => {
  const baseUrl = window.location.origin
  return `${baseUrl}/static/images/backgrounds/${name}.jpg`
}
</script>
