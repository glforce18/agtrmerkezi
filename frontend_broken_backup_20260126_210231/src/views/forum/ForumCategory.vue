<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Breadcrumb -->
      <div class="mb-6 flex items-center gap-2 text-sm font-hev text-text-secondary">
        <router-link to="/forum" class="hover:text-hev-cyan">Forum</router-link>
        <span>›</span>
        <span class="text-text-primary">{{ category?.name || 'Kategori' }}</span>
      </div>

      <!-- Loading -->
      <div v-if="loading && !category" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin text-6xl text-hev-cyan mb-4">λ</div>
          <p class="text-text-secondary font-hev">Yükleniyor...</p>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="p-6 bg-combine-red bg-opacity-10 border border-combine-red rounded">
        <p class="text-combine-red font-hev">{{ error }}</p>
        <router-link to="/forum" class="mt-4 inline-block px-6 py-2 bg-lambda-orange text-cyber-black font-lambda rounded">
          Foruma Dön
        </router-link>
      </div>

      <!-- Category Content -->
      <template v-else-if="category">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-start justify-between">
            <div class="flex items-start gap-4">
              <div
                class="w-16 h-16 rounded flex items-center justify-center text-3xl"
                :style="{
                  background: `${getCategoryColor(category.slug)}20`,
                  color: getCategoryColor(category.slug),
                  border: `2px solid ${getCategoryColor(category.slug)}`
                }"
              >
                <component :is="getCategoryIcon(category.slug)" :size="32" />
              </div>

              <div>
                <h1 class="text-4xl font-lambda font-bold mb-2"
                  :style="{ color: getCategoryColor(category.slug) }">
                  {{ category.name }}
                </h1>
                <p class="text-text-secondary font-hev mb-3">
                  {{ category.description }}
                </p>
                <div class="flex items-center gap-4 text-sm text-text-secondary font-hev">
                  <span>{{ category.topic_count || 0 }} konu</span>
                  <span>•</span>
                  <span>{{ category.reply_count || 0 }} mesaj</span>
                </div>
              </div>
            </div>

            <router-link
              v-if="isAuthenticated"
              to="/forum/new"
              class="px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all"
            >
              <Plus :size="18" class="inline mr-2" />
              YENİ KONU
            </router-link>
          </div>
        </div>

        <!-- Filters -->
        <div class="mb-4 flex items-center justify-between">
          <div class="flex gap-2">
            <button
              v-for="filter in filters"
              :key="filter.value"
              @click="activeFilter = filter.value"
              class="px-4 py-2 font-lambda text-sm rounded transition-all"
              :class="activeFilter === filter.value
                ? 'bg-hev-cyan text-cyber-black'
                : 'bg-cyber-panel border border-cyber-border text-text-secondary hover:border-hev-cyan'"
            >
              {{ filter.label }}
            </button>
          </div>

          <div class="flex items-center gap-2 text-sm text-text-secondary font-hev">
            <span>Sıralama:</span>
            <select
              v-model="sortBy"
              class="px-3 py-1 bg-cyber-panel border border-cyber-border rounded text-text-primary font-hev outline-none"
            >
              <option value="latest">En Yeni</option>
              <option value="popular">En Popüler</option>
              <option value="replies">En Çok Cevaplanan</option>
            </select>
          </div>
        </div>

        <!-- Topics List -->
        <div v-if="filteredTopics.length === 0" class="text-center py-10 bg-cyber-panel border border-cyber-border rounded">
          <MessageSquare :size="48" class="inline text-text-secondary opacity-30 mb-3" />
          <p class="text-text-secondary font-hev">Bu kategoride henüz konu yok</p>
          <router-link
            v-if="isAuthenticated"
            to="/forum/new"
            class="mt-4 inline-block px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all"
          >
            İLK KONUYU SEN AÇ
          </router-link>
        </div>

        <div v-else class="space-y-2">
          <router-link
            v-for="topic in filteredTopics"
            :key="topic.id"
            :to="`/forum/topic/${topic.id}`"
            class="block bg-cyber-panel border border-cyber-border p-4 rounded hover:border-lambda-orange transition-all group"
          >
            <div class="flex items-start gap-4">
              <!-- Icon/Avatar -->
              <div class="flex flex-col items-center gap-1">
                <div class="w-10 h-10 rounded-full bg-lambda-orange bg-opacity-20 border border-lambda-orange flex items-center justify-center text-lambda-orange font-lambda font-bold">
                  {{ topic.author?.username?.[0]?.toUpperCase() || 'U' }}
                </div>
                <div v-if="topic.is_pinned" class="text-combine-yellow">
                  <Pin :size="14" />
                </div>
              </div>

              <!-- Topic Content -->
              <div class="flex-1">
                <div class="flex items-start justify-between gap-4 mb-2">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <h3 class="font-lambda font-bold text-text-primary group-hover:text-lambda-orange transition-colors">
                        {{ topic.title }}
                      </h3>
                      <span
                        v-if="topic.is_locked"
                        class="text-combine-red"
                        title="Kilitli"
                      >
                        <Lock :size="14" />
                      </span>
                    </div>

                    <div class="flex items-center gap-3 text-xs text-text-secondary font-hev">
                      <span class="flex items-center gap-1">
                        <User :size="12" />
                        {{ topic.author?.username || 'Unknown' }}
                      </span>
                      <span>•</span>
                      <span class="flex items-center gap-1">
                        <Clock :size="12" />
                        {{ formatDate(topic.created_at) }}
                      </span>
                    </div>
                  </div>

                  <!-- Stats -->
                  <div class="flex items-center gap-4">
                    <div class="text-center">
                      <div class="text-lg font-lambda text-hev-cyan">{{ topic.reply_count || 0 }}</div>
                      <div class="text-xs text-text-secondary font-hev">cevap</div>
                    </div>
                    <div class="text-center">
                      <div class="text-lg font-lambda text-combine-green">{{ topic.view_count || 0 }}</div>
                      <div class="text-xs text-text-secondary font-hev">görüntülenme</div>
                    </div>
                  </div>
                </div>

                <!-- Last Reply Info -->
                <div v-if="topic.last_reply" class="mt-2 pt-2 border-t border-cyber-border text-xs text-text-secondary font-hev">
                  Son cevap:
                  <span class="text-text-primary">{{ topic.last_reply.author?.username }}</span>
                  •
                  {{ formatDate(topic.last_reply.created_at) }}
                </div>
              </div>
            </div>
          </router-link>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="mt-6 flex items-center justify-center gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-4 py-2 bg-cyber-panel border border-cyber-border text-text-primary font-lambda rounded hover:border-hev-cyan transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            ‹ Önceki
          </button>

          <button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            class="px-4 py-2 font-lambda rounded transition-all"
            :class="currentPage === page
              ? 'bg-hev-cyan text-cyber-black'
              : 'bg-cyber-panel border border-cyber-border text-text-primary hover:border-hev-cyan'"
          >
            {{ page }}
          </button>

          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-4 py-2 bg-cyber-panel border border-cyber-border text-text-primary font-lambda rounded hover:border-hev-cyan transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Sonraki ›
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import forumAPI from '@/api/forum'
import {
  Plus,
  MessageSquare,
  User,
  Clock,
  Pin,
  Lock,
  FileText,
  HelpCircle,
  Wrench,
  Megaphone,
  Users
} from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref(null)
const category = ref(null)
const topics = ref([])
const currentPage = ref(1)
const perPage = 20
const activeFilter = ref('all')
const sortBy = ref('latest')

const filters = [
  { value: 'all', label: 'Tümü' },
  { value: 'pinned', label: 'Sabitlenmiş' },
  { value: 'unanswered', label: 'Cevaplanmamış' }
]

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const categoryId = computed(() => route.params.id)

const filteredTopics = computed(() => {
  let filtered = [...topics.value]

  // Filter
  switch (activeFilter.value) {
    case 'pinned':
      filtered = filtered.filter(t => t.is_pinned)
      break
    case 'unanswered':
      filtered = filtered.filter(t => (t.reply_count || 0) === 0)
      break
  }

  // Sort
  switch (sortBy.value) {
    case 'latest':
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'popular':
      filtered.sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
      break
    case 'replies':
      filtered.sort((a, b) => (b.reply_count || 0) - (a.reply_count || 0))
      break
  }

  // Pinned topics always on top
  const pinned = filtered.filter(t => t.is_pinned)
  const normal = filtered.filter(t => !t.is_pinned)

  return [...pinned, ...normal].slice((currentPage.value - 1) * perPage, currentPage.value * perPage)
})

const totalPages = computed(() => Math.ceil(topics.value.length / perPage))

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

// Methods
function getCategoryColor(slug) {
  const colorMap = {
    announcements: '#FF6B35',
    general: '#00F5FF',
    support: '#39FF14',
    guides: '#B537F2',
    suggestions: '#FFFD37',
    offtopic: '#FF006E'
  }
  return colorMap[slug] || '#00F5FF'
}

function getCategoryIcon(slug) {
  const iconMap = {
    announcements: Megaphone,
    general: MessageSquare,
    support: HelpCircle,
    guides: FileText,
    suggestions: Wrench,
    offtopic: Users
  }
  return iconMap[slug] || MessageSquare
}

function formatDate(dateString) {
  if (!dateString) return ''

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Az önce'
  if (diffMins < 60) return `${diffMins} dakika önce`
  if (diffHours < 24) return `${diffHours} saat önce`
  if (diffDays < 7) return `${diffDays} gün önce`

  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function loadCategory() {
  loading.value = true
  error.value = null

  try {
    const [categoryRes, topicsRes] = await Promise.all([
      forumAPI.getCategory(categoryId.value),
      forumAPI.getTopicsByCategory(categoryId.value)
    ])

    category.value = categoryRes.data
    topics.value = topicsRes.data.topics || topicsRes.data || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Kategori yüklenemedi'
    console.error('Load category error:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadCategory()
})
</script>

<style scoped>
.bg-lambda-gradient {
  background: linear-gradient(135deg, #FF6B35 0%, #E85D2C 100%);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}
</style>
