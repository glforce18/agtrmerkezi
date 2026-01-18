<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-display font-bold mb-2">
          <span class="text-gradient">Topluluk Forumu</span>
        </h1>
        <p class="text-gray-400">
          CS 1.6 topluluğuyla bağlantıda kalın, sorular sorun ve bilginizi paylaşın
        </p>
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Search & New Topic -->
          <n-card class="glass-card">
            <div class="flex flex-col md:flex-row gap-3">
              <div class="flex-1">
                <n-input v-model:value="searchQuery" placeholder="Forumlarda ara...">
                  <template #prefix>
                    <SearchIcon class="w-4 h-4 text-gray-400" />
                  </template>
                </n-input>
              </div>
              <n-button type="primary" @click="showNewTopicModal = true">
                <template #icon><PlusCircleIcon class="w-4 h-4" /></template>
                Yeni Konu
              </n-button>
            </div>
          </n-card>

          <!-- Categories -->
          <div class="space-y-4">
            <n-card
              v-for="category in categories"
              :key="category.id"
              class="glass-card cursor-pointer category-card"
              @click="router.push(`/forum/category/${category.id}`)"
            >
              <div class="flex items-start gap-4">
                <!-- Category Icon -->
                <div
                  :class="[
                    'w-16 h-16 rounded-lg flex items-center justify-center flex-shrink-0',
                    getCategoryGradient(category.gradient)
                  ]"
                >
                  <component :is="category.icon" class="w-8 h-8 text-white" />
                </div>

                <!-- Category Info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between mb-2">
                    <div>
                      <h3 class="text-xl font-bold hover:text-orange-500 transition-colors">
                        {{ category.name }}
                      </h3>
                      <p class="text-sm text-gray-400">
                        {{ category.description }}
                      </p>
                    </div>
                  </div>

                  <!-- Stats -->
                  <div class="flex items-center gap-6 text-sm mt-3">
                    <div class="flex items-center gap-2 text-gray-400">
                      <FileTextIcon class="w-4 h-4" />
                      <span>{{ category.topics }} Konu</span>
                    </div>
                    <div class="flex items-center gap-2 text-gray-400">
                      <MessageSquareIcon class="w-4 h-4" />
                      <span>{{ category.posts }} Gönderi</span>
                    </div>
                  </div>

                  <!-- Latest Topic -->
                  <div
                    v-if="category.latestTopic"
                    class="mt-4 pt-4 border-t border-white/10 flex items-center justify-between"
                  >
                    <div class="flex items-center gap-2 min-w-0">
                      <n-avatar round :size="24" :src="category.latestTopic.authorAvatar" />
                      <div class="min-w-0 flex-1">
                        <p class="text-sm font-semibold truncate">
                          {{ category.latestTopic.title }}
                        </p>
                        <p class="text-xs text-gray-500">
                          {{ category.latestTopic.author }} • {{ category.latestTopic.time }}
                        </p>
                      </div>
                    </div>
                    <ChevronRightIcon class="w-5 h-5 text-gray-500 flex-shrink-0" />
                  </div>
                </div>
              </div>
            </n-card>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Forum Stats -->
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <TrendingUpIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Forum İstatistikleri</span>
              </div>
            </template>
            <div class="space-y-3">
              <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                <span class="text-gray-400">Toplam Konu</span>
                <span class="font-bold text-orange-500">{{ stats.totalTopics }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                <span class="text-gray-400">Toplam Gönderi</span>
                <span class="font-bold text-purple-500">{{ stats.totalPosts }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                <span class="text-gray-400">Toplam Üye</span>
                <span class="font-bold text-cyan-500">{{ stats.totalMembers }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                <span class="text-gray-400">Çevrimiçi</span>
                <span class="font-bold text-green-500">{{ stats.onlineUsers }}</span>
              </div>
            </div>
          </n-card>

          <!-- Active Users -->
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <UsersIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Aktif Kullanıcılar</span>
              </div>
            </template>
            <div class="space-y-3">
              <div
                v-for="user in activeUsers"
                :key="user.id"
                class="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
              >
                <div class="relative">
                  <n-avatar round :size="40" :src="user.avatar" />
                  <div class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900"></div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-semibold truncate">{{ user.name }}</p>
                  <p class="text-xs text-gray-500">{{ user.posts }} gönderi</p>
                </div>
              </div>
            </div>
          </n-card>

          <!-- Recent Activity -->
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center gap-2">
                <ActivityIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Son Aktiviteler</span>
              </div>
            </template>
            <div class="space-y-3">
              <div
                v-for="activity in recentActivity"
                :key="activity.id"
                class="flex items-start gap-3 p-3 bg-white/5 rounded-lg"
              >
                <div :class="['w-2 h-2 rounded-full mt-2', getActivityColor(activity.type)]"></div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm">{{ activity.message }}</p>
                  <span class="text-xs text-gray-500">{{ activity.time }}</span>
                </div>
              </div>
            </div>
          </n-card>
        </div>
      </div>
    </div>

    <!-- New Topic Modal -->
    <n-modal v-model:show="showNewTopicModal" preset="card" title="Yeni Konu Oluştur" style="width: 600px;">
      <n-form @submit.prevent="createTopic" class="space-y-4">
        <n-form-item label="Kategori Seç">
          <n-select
            v-model:value="newTopic.categoryId"
            placeholder="Kategori seçin"
            :options="categoryOptions"
          />
        </n-form-item>

        <n-form-item label="Konu Başlığı">
          <n-input v-model:value="newTopic.title" placeholder="Başlık girin..." />
        </n-form-item>

        <n-form-item label="İçerik">
          <n-input
            v-model:value="newTopic.content"
            type="textarea"
            placeholder="Konu içeriği..."
            :rows="6"
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
import { useRouter } from 'vue-router'
import {
  SearchIcon,
  PlusCircleIcon,
  FileTextIcon,
  MessageSquareIcon,
  ChevronRightIcon,
  TrendingUpIcon,
  UsersIcon,
  ActivityIcon,
  ServerIcon,
  WrenchIcon,
  HelpCircleIcon,
  TrophyIcon,
  SendIcon
} from 'lucide-vue-next'

const router = useRouter()
const searchQuery = ref('')
const showNewTopicModal = ref(false)

const stats = reactive({
  totalTopics: 0,
  totalPosts: 0,
  totalMembers: 0,
  onlineUsers: 0
})

const categories = ref([
  {
    id: 1,
    name: 'Genel Tartışma',
    description: 'CS 1.6 hakkında genel konular',
    icon: MessageSquareIcon,
    gradient: 'primary-secondary',
    topics: 342,
    posts: 2145,
    latestTopic: {
      title: 'Yeni güncelleme hakkında düşünceleriniz?',
      author: 'Player123',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
      time: '5 dakika önce'
    }
  },
  {
    id: 2,
    name: 'Sunucu Ayarları',
    description: 'Sunucu kurulumu ve yönetimi',
    icon: ServerIcon,
    gradient: 'secondary-accent',
    topics: 256,
    posts: 1834,
    latestTopic: {
      title: 'HLDS Performans İpuçları',
      author: 'AdminUser',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
      time: '12 dakika önce'
    }
  },
  {
    id: 3,
    name: 'Teknik Destek',
    description: 'Sorunlarınız için yardım alın',
    icon: WrenchIcon,
    gradient: 'accent-error',
    topics: 428,
    posts: 3214,
    latestTopic: {
      title: 'Sunucu başlatma hatası',
      author: 'NewbieGamer',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
      time: '20 dakika önce'
    }
  },
  {
    id: 4,
    name: 'Soru & Cevap',
    description: 'Sorularınızı sorun, cevaplar alın',
    icon: HelpCircleIcon,
    gradient: 'primary-accent',
    topics: 534,
    posts: 2876,
    latestTopic: {
      title: 'En iyi map rotasyonu nedir?',
      author: 'ProPlayer',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
      time: '35 dakika önce'
    }
  },
  {
    id: 5,
    name: 'Turnuvalar & Etkinlikler',
    description: 'Topluluk etkinlikleri ve turnuvalar',
    icon: TrophyIcon,
    gradient: 'warning-success',
    topics: 88,
    posts: 1463,
    latestTopic: {
      title: '5v5 Turnuva Kayıtları Açıldı!',
      author: 'EventManager',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=5',
      time: '1 saat önce'
    }
  }
])

const categoryOptions = computed(() => {
  return categories.value.map(cat => ({
    label: cat.name,
    value: cat.id
  }))
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

const getActivityColor = (type) => {
  const colors = {
    primary: 'bg-orange-500',
    secondary: 'bg-purple-500',
    success: 'bg-green-500',
    accent: 'bg-cyan-500'
  }
  return colors[type] || 'bg-gray-500'
}

const activeUsers = ref([
  { id: 1, name: 'Player123', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=u1', posts: 1234 },
  { id: 2, name: 'AdminUser', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=u2', posts: 856 },
  { id: 3, name: 'ProGamer', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=u3', posts: 623 },
  { id: 4, name: 'NewbieCS', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=u4', posts: 142 },
  { id: 5, name: 'MapMaster', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=u5', posts: 387 }
])

const recentActivity = ref([
  { id: 1, type: 'primary', message: 'Player123 yeni bir konu oluşturdu', time: '2 dakika önce' },
  { id: 2, type: 'secondary', message: 'AdminUser bir konuya yanıt verdi', time: '8 dakika önce' },
  { id: 3, type: 'success', message: 'ProGamer bir konuyu beğendi', time: '15 dakika önce' },
  { id: 4, type: 'accent', message: 'NewUser foruma katıldı', time: '23 dakika önce' }
])

const newTopic = reactive({
  categoryId: null,
  title: '',
  content: ''
})

const createTopic = async () => {
  if (!newTopic.categoryId) {
    window.$message?.warning('Lütfen bir kategori seçin')
    return
  }
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category_id: newTopic.categoryId,
        title: newTopic.title.trim(),
        content: newTopic.content.trim()
      })
    })

    if (response.ok) {
      showNewTopicModal.value = false
      newTopic.categoryId = null
      newTopic.title = ''
      newTopic.content = ''
      window.$message?.success('Konu başarıyla oluşturuldu')
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

.category-card {
  transition: all 0.2s ease;
}

.category-card:hover {
  border-color: rgba(249, 115, 22, 0.5);
  transform: translateY(-2px);
}
</style>
