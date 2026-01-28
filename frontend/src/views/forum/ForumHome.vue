<template>
  <div class="container mx-auto px-4 py-8 max-w-[1400px]">
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
        <!-- Header -->
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-text-primary mb-2">Forum</h1>
          <p class="text-text-secondary">Topluluğumuzla bağlantıda kalın, sorularınızı sorun</p>
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

        <!-- Search & New Topic -->
        <div class="flex gap-3 mb-6">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Konu ara..."
              class="input"
              @input="handleSearch"
            />
          </div>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/forum/topic/new"
            class="btn btn-primary whitespace-nowrap"
          >
            + Yeni Konu
          </router-link>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="space-y-4">
          <div v-for="i in 5" :key="i" class="skeleton h-32 rounded-lg"></div>
        </div>

        <!-- Topics List -->
        <div v-else-if="filteredTopics.length" class="space-y-3">
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
  let result = topics.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(topic =>
      topic.title.toLowerCase().includes(query) ||
      (topic.content && topic.content.toLowerCase().includes(query))
    )
  }

  // Sort filter
  switch (currentFilter.value) {
    case 'popular':
      result = [...result].sort((a, b) => (b.post_count || 0) - (a.post_count || 0))
      break
    case 'unanswered':
      result = result.filter(t => (t.post_count || 0) === 0)
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
    categories.value = response.data
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const fetchTopics = async () => {
  try {
    loading.value = true
    const response = await forumAPI.getTopics({ limit: 20, sort: currentFilter.value })
    topics.value = response.data.topics || response.data
    hasMore.value = (response.data.topics || response.data).length >= 20
  } catch (error) {
    console.error('Failed to fetch topics:', error)
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    // Mock stats - in production, add actual API call
    stats.value = {
      total_topics: 1234,
      total_replies: 5678,
      total_users: 890,
      online_users: 42
    }

    // Mock trending topics
    trendingTopics.value = topics.value.slice(0, 5)

    // Mock online users
    onlineUsers.value = []
  } catch (error) {
    console.error('Failed to fetch stats:', error)
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
</script>
