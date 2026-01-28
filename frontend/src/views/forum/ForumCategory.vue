<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-primary text-4xl mb-4">⏳</div>
      <p class="text-gray-400">Kategori yükleniyor...</p>
    </div>

    <div v-else-if="category">
      <!-- Header -->
      <div class="mb-6">
        <router-link to="/forum" class="text-gray-400 hover:text-primary mb-2 inline-block">
          ← Forum Ana Sayfa
        </router-link>

        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="w-16 h-16 bg-primary/20 rounded-lg flex items-center justify-center">
              <span class="text-4xl">{{ getCategoryIcon(category.slug) }}</span>
            </div>
            <div>
              <h1 class="text-3xl font-lambda font-bold text-white">{{ category.name }}</h1>
              <p class="text-gray-400">{{ category.description || 'Açıklama yok' }}</p>
            </div>
          </div>

          <router-link
            v-if="authStore.isAuthenticated"
            :to="`/forum/topic/new?category=${category.id}`"
            class="btn-primary"
          >
            + Yeni Konu
          </router-link>
        </div>
      </div>

      <!-- Category Stats -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="stat-card">
          <div class="text-gray-400 text-sm mb-1">Toplam Konu</div>
          <div class="text-2xl font-bold text-white">{{ category.topic_count || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="text-gray-400 text-sm mb-1">Toplam Mesaj</div>
          <div class="text-2xl font-bold text-white">{{ category.post_count || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="text-gray-400 text-sm mb-1">Son Aktivite</div>
          <div class="text-lg font-bold text-primary">
            {{ formatDate(category.last_activity_at) || 'Yok' }}
          </div>
        </div>
      </div>

      <!-- Sort and Filter -->
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center space-x-2">
          <span class="text-gray-400 text-sm">Sıralama:</span>
          <select
            v-model="sortBy"
            @change="fetchTopics"
            class="bg-dark-card border border-primary/30 text-white rounded px-3 py-1 text-sm"
          >
            <option value="recent">En Yeni</option>
            <option value="popular">En Popüler</option>
            <option value="replies">En Çok Yanıtlanan</option>
            <option value="views">En Çok Görüntülenen</option>
          </select>
        </div>

        <div class="text-gray-400 text-sm">
          {{ topics.length }} konu gösteriliyor
        </div>
      </div>

      <!-- Topics List -->
      <div v-if="!topics.length" class="text-center py-12 bg-dark-card border border-primary/30 rounded-lg">
        <div class="text-gray-600 text-6xl mb-4">💬</div>
        <h2 class="text-xl font-lambda font-bold text-white mb-2">Henüz konu yok</h2>
        <p class="text-gray-400 mb-6">Bu kategoride ilk konuyu siz açın!</p>
        <router-link
          v-if="authStore.isAuthenticated"
          :to="`/forum/topic/new?category=${category.id}`"
          class="btn-primary inline-block"
        >
          + Yeni Konu Aç
        </router-link>
      </div>

      <div v-else class="space-y-3">
        <!-- Pinned Topics -->
        <div v-if="pinnedTopics.length" class="space-y-3 mb-4">
          <div class="flex items-center space-x-2 mb-2">
            <span class="text-yellow-400 text-xl">📌</span>
            <span class="text-gray-400 text-sm font-semibold">SABİTLENMİŞ KONULAR</span>
          </div>
          <router-link
            v-for="topic in pinnedTopics"
            :key="topic.id"
            :to="`/forum/topic/${topic.id}`"
            class="topic-card pinned"
          >
            <div class="flex items-start space-x-4">
              <!-- Avatar -->
              <div class="flex-shrink-0 w-10 h-10 bg-primary rounded-full flex items-center justify-center">
                <span class="text-white font-bold">{{ getInitials(topic.author?.username) }}</span>
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-1">
                  <h3 class="text-lg font-semibold text-white">{{ topic.title }}</h3>
                  <span v-if="topic.is_locked" class="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded">
                    🔒 Kilitli
                  </span>
                </div>

                <div class="flex items-center space-x-4 text-sm text-gray-400">
                  <span>{{ topic.author?.username || 'Anonim' }}</span>
                  <span>•</span>
                  <span>{{ formatDate(topic.created_at) }}</span>
                </div>
              </div>

              <!-- Stats -->
              <div class="flex items-center space-x-6 text-sm">
                <div class="text-center">
                  <div class="text-white font-bold">{{ topic.view_count || 0 }}</div>
                  <div class="text-gray-400 text-xs">Görüntüleme</div>
                </div>
                <div class="text-center">
                  <div class="text-primary font-bold">{{ topic.reply_count || 0 }}</div>
                  <div class="text-gray-400 text-xs">Yanıt</div>
                </div>
              </div>
            </div>
          </router-link>
        </div>

        <!-- Regular Topics -->
        <router-link
          v-for="topic in regularTopics"
          :key="topic.id"
          :to="`/forum/topic/${topic.id}`"
          class="topic-card"
        >
          <div class="flex items-start space-x-4">
            <!-- Avatar -->
            <div class="flex-shrink-0 w-10 h-10 bg-primary rounded-full flex items-center justify-center">
              <span class="text-white font-bold">{{ getInitials(topic.author?.username) }}</span>
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2 mb-1">
                <h3 class="text-lg font-semibold text-white">{{ topic.title }}</h3>
                <span v-if="topic.is_locked" class="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded">
                  🔒 Kilitli
                </span>
              </div>

              <div class="flex items-center space-x-4 text-sm text-gray-400">
                <span>{{ topic.author?.username || 'Anonim' }}</span>
                <span>•</span>
                <span>{{ formatDate(topic.created_at) }}</span>
              </div>
            </div>

            <!-- Stats -->
            <div class="flex items-center space-x-6 text-sm">
              <div class="text-center">
                <div class="text-white font-bold">{{ topic.view_count || 0 }}</div>
                <div class="text-gray-400 text-xs">Görüntüleme</div>
              </div>
              <div class="text-center">
                <div class="text-primary font-bold">{{ topic.post_count || 0 }}</div>
                <div class="text-gray-400 text-xs">Yanıt</div>
              </div>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center space-x-2 mt-6">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="pagination-btn"
          :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
        >
          ← Önceki
        </button>

        <div class="flex items-center space-x-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="changePage(page)"
            class="pagination-btn"
            :class="{ 'active': page === currentPage }"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="pagination-btn"
          :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
        >
          Sonraki →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import forumAPI from '@/api/forum'

const route = useRoute()
const authStore = useAuthStore()

const categoryId = parseInt(route.params.id)
const category = ref(null)
const topics = ref([])
const loading = ref(true)
const sortBy = ref('recent')
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 20

onMounted(async () => {
  await fetchCategory()
  await fetchTopics()
})

const fetchCategory = async () => {
  try {
    const response = await forumAPI.getCategories()
    const categories = response.data
    category.value = categories.find(c => c.id === categoryId)
  } catch (error) {
    console.error('Failed to fetch category:', error)
  }
}

const fetchTopics = async () => {
  try {
    loading.value = true
    const response = await forumAPI.getTopicsByCategory(categoryId, {
      sort: sortBy.value,
      page: currentPage.value,
      per_page: perPage
    })

    // New modular API format: { success: true, data: [...], pagination: {...} }
    topics.value = response.data.data || []

    // Update pagination if provided
    if (response.data.pagination) {
      totalPages.value = response.data.pagination.total_pages
    }
  } catch (error) {
    console.error('Failed to fetch topics:', error)
    topics.value = []
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchTopics()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const pinnedTopics = computed(() => {
  return topics.value.filter(t => t.is_pinned)
})

const regularTopics = computed(() => {
  return topics.value.filter(t => !t.is_pinned)
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

const getCategoryIcon = (slug) => {
  const icons = {
    'announcements': '📢',
    'general': '💬',
    'help': '❓',
    'bugs': '🐛',
    'suggestions': '💡',
    'servers': '🖥️',
    'plugins': '🔌',
    'maps': '🗺️',
    'off-topic': '🎮'
  }
  return icons[slug] || '📁'
}

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const formatDate = (dateString) => {
  if (!dateString) return ''

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Az önce'
  if (diffMins < 60) return `${diffMins} dakika önce`
  if (diffHours < 24) return `${diffHours} saat önce`
  if (diffDays < 7) return `${diffDays} gün önce`

  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}
</script>

<style scoped>
.btn-primary {
  @apply px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark transition-colors duration-200 font-semibold;
}

.stat-card {
  @apply bg-dark-card border border-primary/30 rounded-lg p-4;
}

.topic-card {
  @apply block bg-dark-card border border-primary/30 rounded-lg p-4 hover:border-primary transition-colors duration-200;
}

.topic-card.pinned {
  @apply border-yellow-500/50 bg-yellow-500/5;
}

.pagination-btn {
  @apply px-4 py-2 bg-dark-card border border-primary/30 text-white rounded hover:bg-primary transition-colors duration-200;
}

.pagination-btn.active {
  @apply bg-primary border-primary;
}
</style>
