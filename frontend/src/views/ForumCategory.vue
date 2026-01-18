<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Breadcrumb -->
      <n-breadcrumb class="mb-4">
        <n-breadcrumb-item @click="router.push('/forum')">
          <HomeIcon class="w-4 h-4 inline mr-1" />
          Forum
        </n-breadcrumb-item>
        <n-breadcrumb-item>
          <span class="text-orange-500">{{ category?.name }}</span>
        </n-breadcrumb-item>
      </n-breadcrumb>

      <!-- Category Header -->
      <n-card class="glass-card mb-6">
        <div class="flex items-start gap-4">
          <div
            :class="[
              'w-16 h-16 rounded-lg flex items-center justify-center flex-shrink-0',
              category?.gradient ? getCategoryGradient(category.gradient) : 'bg-gradient-to-br from-orange-500 to-purple-500'
            ]"
          >
            <component :is="category?.icon || MessageSquareIcon" class="w-8 h-8 text-white" />
          </div>
          <div class="flex-1">
            <h1 class="text-3xl font-display font-bold mb-2">
              <span class="text-gradient">{{ category?.name || 'Kategori' }}</span>
            </h1>
            <p class="text-gray-400">{{ category?.description }}</p>
            <div class="flex items-center gap-6 text-sm mt-3">
              <div class="flex items-center gap-2 text-gray-400">
                <FileTextIcon class="w-4 h-4" />
                <span>{{ topics.length }} Konu</span>
              </div>
              <div class="flex items-center gap-2 text-gray-400">
                <MessageSquareIcon class="w-4 h-4" />
                <span>{{ totalPosts }} Gönderi</span>
              </div>
            </div>
          </div>
          <n-button type="primary" @click="showNewTopicModal = true">
            <template #icon><PlusCircleIcon class="w-4 h-4" /></template>
            Yeni Konu
          </n-button>
        </div>
      </n-card>

      <!-- Filters & Sort -->
      <n-card class="glass-card mb-6">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <n-input v-model:value="searchQuery" placeholder="Konularda ara...">
              <template #prefix>
                <SearchIcon class="w-4 h-4 text-gray-400" />
              </template>
            </n-input>
          </div>
          <div class="flex gap-2">
            <n-select
              v-model:value="sortBy"
              :options="sortOptions"
              style="width: 150px;"
            />
          </div>
        </div>
      </n-card>

      <!-- Topics List -->
      <div class="space-y-3">
        <n-card
          v-for="topic in filteredTopics"
          :key="topic.id"
          class="glass-card cursor-pointer topic-card"
          @click="router.push(`/forum/topic/${topic.id}`)"
        >
          <div class="flex items-start gap-4">
            <!-- Author Avatar -->
            <n-avatar round :size="48" :src="topic.authorAvatar" />

            <!-- Topic Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-4 mb-2">
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-bold hover:text-orange-500 transition-colors truncate">
                    {{ topic.title }}
                  </h3>
                  <div class="flex items-center gap-3 text-sm text-gray-400 mt-1">
                    <span class="flex items-center gap-1">
                      <UserIcon class="w-3 h-3" />
                      {{ topic.author }}
                    </span>
                    <span class="flex items-center gap-1">
                      <ClockIcon class="w-3 h-3" />
                      {{ topic.created }}
                    </span>
                  </div>
                </div>

                <div class="flex flex-col items-end gap-2 flex-shrink-0">
                  <n-tag v-if="topic.isPinned" type="primary" size="small">
                    <template #icon><PinIcon class="w-3 h-3" /></template>
                  </n-tag>
                  <n-tag v-if="topic.isLocked" type="error" size="small">
                    <template #icon><LockIcon class="w-3 h-3" /></template>
                  </n-tag>
                </div>
              </div>

              <!-- Topic Stats -->
              <div class="flex items-center gap-6 text-sm">
                <div class="flex items-center gap-2 text-gray-400">
                  <MessageSquareIcon class="w-4 h-4" />
                  <span>{{ topic.replies }} Yanıt</span>
                </div>
                <div class="flex items-center gap-2 text-gray-400">
                  <EyeIcon class="w-4 h-4" />
                  <span>{{ topic.views }} Görüntülenme</span>
                </div>
                <div class="flex items-center gap-2 text-gray-400">
                  <ThumbsUpIcon class="w-4 h-4" />
                  <span>{{ topic.likes }} Beğeni</span>
                </div>
              </div>

              <!-- Last Reply -->
              <div
                v-if="topic.lastReply"
                class="mt-3 pt-3 border-t border-white/10 flex items-center justify-between"
              >
                <div class="flex items-center gap-2">
                  <n-avatar round :size="24" :src="topic.lastReply.avatar" />
                  <span class="text-sm text-gray-400">
                    Son yanıt: <span class="text-orange-500">{{ topic.lastReply.author }}</span>
                    • {{ topic.lastReply.time }}
                  </span>
                </div>
                <ChevronRightIcon class="w-5 h-5 text-gray-500" />
              </div>
            </div>
          </div>
        </n-card>

        <!-- Empty State -->
        <n-card v-if="filteredTopics.length === 0" class="glass-card text-center py-16">
          <n-empty description="Konu Bulunamadı">
            <template #icon>
              <MessageSquareIcon class="w-12 h-12 text-gray-500" />
            </template>
            <template #extra>
              <n-button type="primary" @click="showNewTopicModal = true">
                <template #icon><PlusCircleIcon class="w-4 h-4" /></template>
                İlk Konuyu Siz Açın
              </n-button>
            </template>
          </n-empty>
        </n-card>
      </div>

      <!-- Pagination -->
      <div v-if="filteredTopics.length > 0" class="flex justify-center mt-8">
        <n-pagination
          v-model:page="currentPage"
          :page-count="10"
          show-quick-jumper
        />
      </div>
    </div>

    <!-- New Topic Modal -->
    <n-modal v-model:show="showNewTopicModal" preset="card" title="Yeni Konu Oluştur" style="width: 600px;">
      <n-form @submit.prevent="createTopic" class="space-y-4">
        <n-form-item label="Konu Başlığı">
          <n-input v-model:value="newTopic.title" placeholder="Başlık girin..." />
        </n-form-item>

        <n-form-item label="İçerik">
          <n-input
            v-model:value="newTopic.content"
            type="textarea"
            placeholder="Konu içeriği..."
            :rows="8"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="flex gap-3 justify-end">
          <n-button quaternary @click="showNewTopicModal = false">İptal</n-button>
          <n-button type="primary" @click="createTopic">
            <template #icon><SendIcon class="w-4 h-4" /></template>
            Konuyu Oluştur
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeIcon,
  MessageSquareIcon,
  FileTextIcon,
  PlusCircleIcon,
  SearchIcon,
  UserIcon,
  ClockIcon,
  PinIcon,
  LockIcon,
  EyeIcon,
  ThumbsUpIcon,
  ChevronRightIcon,
  SendIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const categoryId = route.params.id

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

const searchQuery = ref('')
const sortBy = ref('latest')
const showNewTopicModal = ref(false)
const currentPage = ref(1)

const sortOptions = [
  { label: 'En Yeni', value: 'latest' },
  { label: 'Popüler', value: 'popular' },
  { label: 'En Çok Yanıt', value: 'mostReplies' },
  { label: 'En Eski', value: 'oldest' }
]

const category = ref({
  id: 1,
  name: 'Genel Tartışma',
  description: 'CS 1.6 hakkında genel konular',
  icon: MessageSquareIcon,
  gradient: 'primary-secondary'
})

const getCategoryGradient = (gradient) => {
  const gradients = {
    'primary-secondary': 'bg-gradient-to-br from-orange-500 to-purple-500',
    'secondary-accent': 'bg-gradient-to-br from-purple-500 to-cyan-500',
    'accent-error': 'bg-gradient-to-br from-cyan-500 to-red-500',
    'primary-accent': 'bg-gradient-to-br from-orange-500 to-cyan-500',
    'warning-success': 'bg-gradient-to-br from-yellow-500 to-green-500'
  }
  return gradients[gradient] || 'bg-gradient-to-br from-orange-500 to-purple-500'
}

const topics = ref([
  {
    id: 1,
    title: 'Yeni güncelleme hakkında düşünceleriniz?',
    author: 'Player123',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
    created: '2 saat önce',
    replies: 45,
    views: 234,
    likes: 12,
    isPinned: true,
    isLocked: false,
    lastReply: {
      author: 'AdminUser',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a1',
      time: '5 dakika önce'
    }
  },
  {
    id: 2,
    title: 'En iyi CS 1.6 map önerileriniz',
    author: 'ProGamer',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    created: '5 saat önce',
    replies: 28,
    views: 156,
    likes: 8,
    isPinned: false,
    isLocked: false,
    lastReply: {
      author: 'MapMaster',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a2',
      time: '1 saat önce'
    }
  },
  {
    id: 3,
    title: '[DUYURU] Forum Kuralları - Lütfen Okuyun',
    author: 'AdminUser',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    created: '1 hafta önce',
    replies: 0,
    views: 489,
    likes: 23,
    isPinned: true,
    isLocked: true,
    lastReply: null
  },
  {
    id: 4,
    title: 'AWP kullanım taktikleri',
    author: 'SniperKing',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
    created: '1 gün önce',
    replies: 67,
    views: 423,
    likes: 31,
    isPinned: false,
    isLocked: false,
    lastReply: {
      author: 'NewbieCS',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a4',
      time: '30 dakika önce'
    }
  }
])

const totalPosts = computed(() => {
  return topics.value.reduce((sum, topic) => sum + topic.replies, 0)
})

const filteredTopics = computed(() => {
  let filtered = topics.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.title.toLowerCase().includes(query) ||
      t.author.toLowerCase().includes(query)
    )
  }

  if (sortBy.value === 'latest') {
    filtered = [...filtered].sort((a, b) => b.id - a.id)
  } else if (sortBy.value === 'popular') {
    filtered = [...filtered].sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'mostReplies') {
    filtered = [...filtered].sort((a, b) => b.replies - a.replies)
  }

  return filtered
})

const newTopic = reactive({
  title: '',
  content: ''
})

const createTopic = async () => {
  if (!newTopic.title || newTopic.title.trim().length < 5) {
    window.$message?.warning('Başlık en az 5 karakter olmalıdır')
    return
  }
  if (!newTopic.content || newTopic.content.trim().length < 20) {
    window.$message?.warning('İçerik en az 20 karakter olmalıdır')
    return
  }

  try {
    const response = await fetch('/api/forum/topics', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        category_id: categoryId,
        title: newTopic.title.trim(),
        content: newTopic.content.trim()
      })
    })

    if (response.ok) {
      showNewTopicModal.value = false
      newTopic.title = ''
      newTopic.content = ''
      window.$message?.success('Konu başarıyla oluşturuldu')
      router.go(0)
    } else {
      const error = await response.json()
      window.$message?.error(error.detail || 'Konu oluşturulamadı')
    }
  } catch (error) {
    window.$message?.error('Bir hata oluştu, lütfen tekrar deneyin')
  }
}
</script>

<style scoped>
.text-gradient {
  background: linear-gradient(to right, #f97316, #8b5cf6, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.topic-card {
  transition: all 0.2s ease;
}

.topic-card:hover {
  border-color: rgba(249, 115, 22, 0.5);
  transform: translateX(4px);
}
</style>
