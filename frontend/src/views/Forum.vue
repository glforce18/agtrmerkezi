<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="mb-8 animate-slide-down">
        <h1 class="text-4xl font-display font-bold mb-2">
          <span class="neon-text">Topluluk Forumu</span>
        </h1>
        <p class="opacity-60">
          CS 1.6 topluluğuyla bağlantıda kalın, sorular sorun ve bilginizi paylaşın
        </p>
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Search & New Topic -->
          <BaseCard variant="glass" class="animate-slide-up">
            <div class="p-4">
              <div class="flex flex-col md:flex-row gap-3">
                <div class="flex-1">
                  <BaseInput
                    v-model="searchQuery"
                    placeholder="Forumlarda ara..."
                    :icon="SearchIcon"
                  />
                </div>
                <BaseButton variant="gaming" @click="showNewTopicModal = true">
                  <PlusCircleIcon class="w-4 h-4 mr-2" />
                  Yeni Konu
                </BaseButton>
              </div>
            </div>
          </BaseCard>

          <!-- Categories -->
          <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
            <BaseCard
              v-for="category in categories"
              :key="category.id"
              variant="glass"
              class="card-hover group cursor-pointer"
              @click="router.push(`/forum/category/${category.id}`)"
            >
              <div class="p-6">
                <div class="flex items-start gap-4">
                  <!-- Category Icon -->
                  <div
                    :class="[
                      'w-16 h-16 rounded-lg flex items-center justify-center flex-shrink-0',
                      `bg-gradient-to-br ${category.gradient}`
                    ]"
                  >
                    <component :is="category.icon" class="w-8 h-8 text-white" />
                  </div>

                  <!-- Category Info -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between mb-2">
                      <div>
                        <h3 class="text-xl font-bold group-hover:text-primary transition-colors">
                          {{ category.name }}
                        </h3>
                        <p class="text-sm opacity-60">
                          {{ category.description }}
                        </p>
                      </div>
                    </div>

                    <!-- Stats -->
                    <div class="flex items-center gap-6 text-sm mt-3">
                      <div class="flex items-center gap-2 opacity-60">
                        <FileTextIcon class="w-4 h-4" />
                        <span>{{ category.topics }} Konu</span>
                      </div>
                      <div class="flex items-center gap-2 opacity-60">
                        <MessageSquareIcon class="w-4 h-4" />
                        <span>{{ category.posts }} Gönderi</span>
                      </div>
                    </div>

                    <!-- Latest Topic -->
                    <div
                      v-if="category.latestTopic"
                      class="mt-4 pt-4 border-t border-base-300 flex items-center justify-between"
                    >
                      <div class="flex items-center gap-2 min-w-0">
                        <div class="avatar">
                          <div class="w-6 h-6 rounded-full">
                            <img :src="category.latestTopic.authorAvatar" />
                          </div>
                        </div>
                        <div class="min-w-0 flex-1">
                          <p class="text-sm font-semibold truncate">
                            {{ category.latestTopic.title }}
                          </p>
                          <p class="text-xs opacity-50">
                            {{ category.latestTopic.author }} • {{ category.latestTopic.time }}
                          </p>
                        </div>
                      </div>
                      <ChevronRightIcon class="w-5 h-5 opacity-40 flex-shrink-0" />
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Forum Stats -->
          <BaseCard variant="glass" class="animate-slide-up" style="animation-delay: 0.2s">
            <div class="p-6">
              <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                <TrendingUpIcon class="w-5 h-5 text-primary" />
                Forum İstatistikleri
              </h3>
              <div class="space-y-3">
                <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                  <span class="opacity-60">Toplam Konu</span>
                  <span class="font-bold text-primary">{{ stats.totalTopics }}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                  <span class="opacity-60">Toplam Gönderi</span>
                  <span class="font-bold text-secondary">{{ stats.totalPosts }}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                  <span class="opacity-60">Toplam Üye</span>
                  <span class="font-bold text-accent">{{ stats.totalMembers }}</span>
                </div>
                <div class="flex justify-between items-center p-3 bg-base-200/50 rounded-lg">
                  <span class="opacity-60">Çevrimiçi</span>
                  <span class="font-bold text-success">{{ stats.onlineUsers }}</span>
                </div>
              </div>
            </div>
          </BaseCard>

          <!-- Active Users -->
          <BaseCard variant="glass" class="animate-slide-up" style="animation-delay: 0.3s">
            <div class="p-6">
              <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                <UsersIcon class="w-5 h-5 text-primary" />
                Aktif Kullanıcılar
              </h3>
              <div class="space-y-3">
                <div
                  v-for="user in activeUsers"
                  :key="user.id"
                  class="flex items-center gap-3 p-2 rounded-lg hover:bg-base-200/50 transition-colors cursor-pointer"
                >
                  <div class="avatar online">
                    <div class="w-10 h-10 rounded-full">
                      <img :src="user.avatar" />
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-semibold truncate">{{ user.name }}</p>
                    <p class="text-xs opacity-50">{{ user.posts }} gönderi</p>
                  </div>
                </div>
              </div>
            </div>
          </BaseCard>

          <!-- Recent Activity -->
          <BaseCard variant="glass" class="animate-slide-up" style="animation-delay: 0.4s">
            <div class="p-6">
              <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                <ActivityIcon class="w-5 h-5 text-primary" />
                Son Aktiviteler
              </h3>
              <div class="space-y-3">
                <div
                  v-for="activity in recentActivity"
                  :key="activity.id"
                  class="flex items-start gap-3 p-3 bg-base-200/50 rounded-lg"
                >
                  <div :class="['w-2 h-2 rounded-full mt-2', `bg-${activity.type}`]"></div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm">{{ activity.message }}</p>
                    <span class="text-xs opacity-50">{{ activity.time }}</span>
                  </div>
                </div>
              </div>
            </div>
          </BaseCard>
        </div>
      </div>
    </div>

    <!-- New Topic Modal -->
    <div v-if="showNewTopicModal" class="modal modal-open">
      <div class="modal-box max-w-2xl">
        <h3 class="font-bold text-lg mb-4">Yeni Konu Oluştur</h3>

        <form @submit.prevent="createTopic" class="space-y-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Kategori Seç</span>
            </label>
            <select v-model="newTopic.categoryId" class="select select-bordered bg-base-200">
              <option disabled selected>Kategori seçin</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <BaseInput
            v-model="newTopic.title"
            label="Konu Başlığı"
            placeholder="Başlık girin..."
            required
          />

          <div class="form-control">
            <label class="label">
              <span class="label-text">İçerik</span>
            </label>
            <textarea
              v-model="newTopic.content"
              class="textarea textarea-bordered h-40 bg-base-200"
              placeholder="Konu içeriği..."
              required
            ></textarea>
          </div>

          <div class="flex gap-2">
            <BaseButton variant="gaming" type="submit">
              <SendIcon class="w-4 h-4 mr-2" />
              Konuyu Oluştur
            </BaseButton>
            <BaseButton variant="ghost" type="button" @click="showNewTopicModal = false">
              İptal
            </BaseButton>
          </div>
        </form>
      </div>
      <div class="modal-backdrop" @click="showNewTopicModal = false"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
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
    gradient: 'from-primary to-secondary',
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
    gradient: 'from-secondary to-accent',
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
    gradient: 'from-accent to-error',
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
    gradient: 'from-primary to-accent',
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
    gradient: 'from-warning to-success',
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
  // Validate form before submission
  if (!newTopic.categoryId) {
    alert('Lütfen bir kategori seçin')
    return
  }
  if (!newTopic.title || newTopic.title.trim().length < 5) {
    alert('Başlık en az 5 karakter olmalıdır')
    return
  }
  if (!newTopic.content || newTopic.content.trim().length < 20) {
    alert('İçerik en az 20 karakter olmalıdır')
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
      // Reset form
      newTopic.categoryId = null
      newTopic.title = ''
      newTopic.content = ''
      // Refresh topics list
      // TODO: Implement refresh logic
    } else {
      const error = await response.json()
      alert(error.detail || 'Konu oluşturulamadı')
    }
  } catch (error) {
    alert('Bir hata oluştu, lütfen tekrar deneyin')
  }
}
</script>

<style scoped>
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-down {
  animation: slideDown 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}
</style>
