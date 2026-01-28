<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h1 class="text-5xl font-lambda font-bold mb-2">
              <span class="text-hev-cyan" style="text-shadow: 0 0 20px rgba(0, 245, 255, 0.6)">FORUM</span>
            </h1>
            <p class="text-text-secondary font-hev">Toplulukla bağlan, sorular sor, deneyimlerini paylaş</p>
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

        <!-- Stats -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-cyber-panel border border-cyber-border p-4 rounded">
            <div class="text-2xl font-lambda text-lambda-orange">{{ stats.total_topics || 0 }}</div>
            <div class="text-text-secondary text-sm font-hev">Toplam Konu</div>
          </div>
          <div class="bg-cyber-panel border border-cyber-border p-4 rounded">
            <div class="text-2xl font-lambda text-hev-cyan">{{ stats.total_replies || 0 }}</div>
            <div class="text-text-secondary text-sm font-hev">Toplam Mesaj</div>
          </div>
          <div class="bg-cyber-panel border border-cyber-border p-4 rounded">
            <div class="text-2xl font-lambda text-combine-green">{{ stats.active_users || 0 }}</div>
            <div class="text-text-secondary text-sm font-hev">Aktif Kullanıcı</div>
          </div>
          <div class="bg-cyber-panel border border-cyber-border p-4 rounded">
            <div class="text-2xl font-lambda text-xen-purple">{{ stats.total_categories || 0 }}</div>
            <div class="text-text-secondary text-sm font-hev">Kategori</div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin text-6xl text-hev-cyan mb-4">λ</div>
          <p class="text-text-secondary font-hev">Forum yükleniyor...</p>
        </div>
      </div>

      <!-- Content -->
      <template v-else>
        <!-- Categories -->
        <div class="mb-8">
          <h2 class="text-2xl font-lambda font-bold text-text-primary mb-4">KATEGORİLER</h2>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <router-link
              v-for="category in categories"
              :key="category.id"
              :to="`/forum/category/${category.id}`"
              class="bg-cyber-panel border border-cyber-border p-6 rounded-lg hover:border-hev-cyan transition-all group"
            >
              <div class="flex items-start gap-4">
                <div
                  class="w-12 h-12 rounded flex items-center justify-center text-2xl"
                  :style="{
                    background: `${getCategoryColor(category.slug)}20`,
                    color: getCategoryColor(category.slug),
                    border: `1px solid ${getCategoryColor(category.slug)}`
                  }"
                >
                  <component :is="getCategoryIcon(category.slug)" :size="24" />
                </div>

                <div class="flex-1">
                  <h3 class="font-lambda font-bold text-text-primary mb-1 group-hover:text-hev-cyan transition-colors">
                    {{ category.name }}
                  </h3>
                  <p class="text-text-secondary text-sm font-hev mb-2">
                    {{ category.description }}
                  </p>
                  <div class="flex items-center gap-4 text-xs text-text-secondary font-hev">
                    <span>{{ category.topic_count || 0 }} konu</span>
                    <span>{{ category.reply_count || 0 }} mesaj</span>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Latest Topics -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-lambda font-bold text-text-primary">SON KONULAR</h2>

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
          </div>

          <div v-if="filteredTopics.length === 0" class="text-center py-10 bg-cyber-panel border border-cyber-border rounded">
            <MessageSquare :size="48" class="inline text-text-secondary opacity-30 mb-3" />
            <p class="text-text-secondary font-hev">Henüz konu yok</p>
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
                          <Tag :size="12" />
                          {{ topic.category?.name }}
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
                      <div class="text-center" v-if="topic.reactions">
                        <div class="text-lg font-lambda text-lambda-orange">{{ topic.reactions.total || 0 }}</div>
                        <div class="text-xs text-text-secondary font-hev">tepki</div>
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
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import forumAPI from '@/api/forum'
import {
  Plus,
  MessageSquare,
  User,
  Tag,
  Clock,
  Pin,
  Lock,
  FileText,
  HelpCircle,
  Wrench,
  Trophy,
  Megaphone,
  Users
} from 'lucide-vue-next'

const authStore = useAuthStore()

const loading = ref(false)
const categories = ref([])
const topics = ref([])
const stats = ref({})
const activeFilter = ref('all')

const filters = [
  { value: 'all', label: 'Tümü' },
  { value: 'latest', label: 'En Yeni' },
  { value: 'popular', label: 'Popüler' },
  { value: 'unanswered', label: 'Cevaplanmamış' }
]

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)

const filteredTopics = computed(() => {
  let filtered = [...topics.value]

  switch (activeFilter.value) {
    case 'latest':
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'popular':
      filtered.sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
      break
    case 'unanswered':
      filtered = filtered.filter(t => (t.reply_count || 0) === 0)
      break
  }

  return filtered.slice(0, 20) // Show top 20
})

// Methods
function getCategoryColor(slug) {
  const colorMap = {
    announcements: '#FF6B35', // Lambda orange
    general: '#00F5FF', // HEV cyan
    support: '#39FF14', // Combine green
    guides: '#B537F2', // Xen purple
    suggestions: '#FFFD37', // Combine yellow
    offtopic: '#FF006E' // Pink
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

async function loadData() {
  loading.value = true
  try {
    const [categoriesRes, topicsRes] = await Promise.all([
      forumAPI.getCategories(),
      forumAPI.getTopics({ limit: 50 })
    ])

    categories.value = categoriesRes.data.categories || categoriesRes.data || []
    topics.value = topicsRes.data.topics || topicsRes.data || []

    // Calculate stats
    stats.value = {
      total_topics: topics.value.length,
      total_replies: topics.value.reduce((sum, t) => sum + (t.reply_count || 0), 0),
      total_categories: categories.value.length,
      active_users: new Set(topics.value.map(t => t.author?.id).filter(Boolean)).size
    }
  } catch (err) {
    console.error('Load forum data error:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadData()
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
