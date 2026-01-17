<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Breadcrumb -->
      <div class="breadcrumbs mb-4 animate-slide-down">
        <ul>
          <li>
            <router-link to="/forum" class="flex items-center gap-2 hover:text-primary transition-colors">
              <HomeIcon class="w-4 h-4" />
              Forum
            </router-link>
          </li>
          <li>
            <span class="text-primary">{{ category?.name }}</span>
          </li>
        </ul>
      </div>

      <!-- Category Header -->
      <BaseCard variant="glass" class="mb-6 animate-slide-up">
        <div class="p-6">
          <div class="flex items-start gap-4">
            <div
              :class="[
                'w-16 h-16 rounded-lg flex items-center justify-center flex-shrink-0',
                category?.gradient ? `bg-gradient-to-br ${category.gradient}` : 'bg-gradient-to-br from-primary to-secondary'
              ]"
            >
              <component :is="category?.icon || MessageSquareIcon" class="w-8 h-8 text-white" />
            </div>
            <div class="flex-1">
              <h1 class="text-3xl font-display font-bold mb-2">
                <span class="neon-text">{{ category?.name || 'Kategori' }}</span>
              </h1>
              <p class="opacity-60">{{ category?.description }}</p>
              <div class="flex items-center gap-6 text-sm mt-3">
                <div class="flex items-center gap-2 opacity-60">
                  <FileTextIcon class="w-4 h-4" />
                  <span>{{ topics.length }} Konu</span>
                </div>
                <div class="flex items-center gap-2 opacity-60">
                  <MessageSquareIcon class="w-4 h-4" />
                  <span>{{ totalPosts }} Gönderi</span>
                </div>
              </div>
            </div>
            <BaseButton variant="gaming" @click="showNewTopicModal = true">
              <PlusCircleIcon class="w-4 h-4 mr-2" />
              Yeni Konu
            </BaseButton>
          </div>
        </div>
      </BaseCard>

      <!-- Filters & Sort -->
      <BaseCard variant="glass" class="mb-6 animate-slide-up" style="animation-delay: 0.1s">
        <div class="p-4">
          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1">
              <BaseInput
                v-model="searchQuery"
                placeholder="Konularda ara..."
                :icon="SearchIcon"
              />
            </div>
            <div class="flex gap-2">
              <select v-model="sortBy" class="select select-bordered select-sm bg-base-200">
                <option value="latest">En Yeni</option>
                <option value="popular">Popüler</option>
                <option value="mostReplies">En Çok Yanıt</option>
                <option value="oldest">En Eski</option>
              </select>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Topics List -->
      <div class="space-y-3 animate-slide-up" style="animation-delay: 0.2s">
        <BaseCard
          v-for="topic in filteredTopics"
          :key="topic.id"
          variant="glass"
          class="card-hover group cursor-pointer"
          @click="router.push(`/forum/topic/${topic.id}`)"
        >
          <div class="p-6">
            <div class="flex items-start gap-4">
              <!-- Author Avatar -->
              <div class="avatar flex-shrink-0">
                <div class="w-12 h-12 rounded-full ring ring-primary ring-offset-2 ring-offset-slate-900">
                  <img :src="topic.authorAvatar" />
                </div>
              </div>

              <!-- Topic Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-4 mb-2">
                  <div class="flex-1 min-w-0">
                    <h3 class="text-lg font-bold group-hover:text-primary transition-colors truncate">
                      {{ topic.title }}
                    </h3>
                    <div class="flex items-center gap-3 text-sm opacity-60 mt-1">
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
                    <div
                      v-if="topic.isPinned"
                      class="badge badge-primary badge-sm"
                      title="Sabitlenmiş"
                    >
                      <PinIcon class="w-3 h-3" />
                    </div>
                    <div
                      v-if="topic.isLocked"
                      class="badge badge-error badge-sm"
                      title="Kilitli"
                    >
                      <LockIcon class="w-3 h-3" />
                    </div>
                  </div>
                </div>

                <!-- Topic Stats -->
                <div class="flex items-center gap-6 text-sm">
                  <div class="flex items-center gap-2 opacity-60">
                    <MessageSquareIcon class="w-4 h-4" />
                    <span>{{ topic.replies }} Yanıt</span>
                  </div>
                  <div class="flex items-center gap-2 opacity-60">
                    <EyeIcon class="w-4 h-4" />
                    <span>{{ topic.views }} Görüntülenme</span>
                  </div>
                  <div class="flex items-center gap-2 opacity-60">
                    <ThumbsUpIcon class="w-4 h-4" />
                    <span>{{ topic.likes }} Beğeni</span>
                  </div>
                </div>

                <!-- Last Reply -->
                <div
                  v-if="topic.lastReply"
                  class="mt-3 pt-3 border-t border-base-300 flex items-center justify-between"
                >
                  <div class="flex items-center gap-2">
                    <div class="avatar">
                      <div class="w-6 h-6 rounded-full">
                        <img :src="topic.lastReply.avatar" />
                      </div>
                    </div>
                    <span class="text-sm opacity-60">
                      Son yanıt: <span class="text-primary">{{ topic.lastReply.author }}</span>
                      • {{ topic.lastReply.time }}
                    </span>
                  </div>
                  <ChevronRightIcon class="w-5 h-5 opacity-40" />
                </div>
              </div>
            </div>
          </div>
        </BaseCard>

        <!-- Empty State -->
        <BaseCard v-if="filteredTopics.length === 0" variant="glass" class="text-center py-16">
          <div class="max-w-md mx-auto">
            <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-base-200 flex items-center justify-center">
              <MessageSquareIcon class="w-12 h-12 opacity-40" />
            </div>
            <h3 class="text-2xl font-bold mb-2">Konu Bulunamadı</h3>
            <p class="opacity-60 mb-6">
              Bu kategoride henüz konu yok veya aramanıza uygun sonuç bulunamadı.
            </p>
            <BaseButton variant="gaming" @click="showNewTopicModal = true">
              <PlusCircleIcon class="w-5 h-5 mr-2" />
              İlk Konuyu Siz Açın
            </BaseButton>
          </div>
        </BaseCard>
      </div>

      <!-- Pagination -->
      <div v-if="filteredTopics.length > 0" class="flex justify-center mt-8 animate-slide-up" style="animation-delay: 0.3s">
        <div class="join">
          <button class="join-item btn btn-sm">«</button>
          <button class="join-item btn btn-sm btn-active">1</button>
          <button class="join-item btn btn-sm">2</button>
          <button class="join-item btn btn-sm">3</button>
          <button class="join-item btn btn-sm">»</button>
        </div>
      </div>
    </div>

    <!-- New Topic Modal -->
    <div v-if="showNewTopicModal" class="modal modal-open">
      <div class="modal-box max-w-2xl">
        <h3 class="font-bold text-lg mb-4">Yeni Konu Oluştur</h3>

        <form @submit.prevent="createTopic" class="space-y-4">
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
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
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
const categoryId = route.params.id

const category = ref({
  id: 1,
  name: 'Genel Tartışma',
  description: 'CS 1.6 hakkında genel konular',
  icon: MessageSquareIcon,
  gradient: 'from-primary to-secondary'
})

const searchQuery = ref('')
const sortBy = ref('latest')
const showNewTopicModal = ref(false)

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

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.title.toLowerCase().includes(query) ||
      t.author.toLowerCase().includes(query)
    )
  }

  // Sort
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
  // Validate form before submission
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
        category_id: categoryId,
        title: newTopic.title.trim(),
        content: newTopic.content.trim()
      })
    })

    if (response.ok) {
      showNewTopicModal.value = false
      newTopic.title = ''
      newTopic.content = ''
      // Refresh page to show new topic
      router.go(0)
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
