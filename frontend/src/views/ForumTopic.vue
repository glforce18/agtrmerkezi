<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Breadcrumb -->
      <n-breadcrumb class="mb-4">
        <n-breadcrumb-item @click="router.push('/forum')">
          <HomeIcon class="w-4 h-4 inline mr-1" />
          Forum
        </n-breadcrumb-item>
        <n-breadcrumb-item @click="router.push('/forum/category/1')">
          Genel Tartışma
        </n-breadcrumb-item>
        <n-breadcrumb-item>
          <span class="text-orange-500 truncate">{{ topic?.title }}</span>
        </n-breadcrumb-item>
      </n-breadcrumb>

      <!-- Topic Header -->
      <n-card class="glass-card mb-6">
        <div class="flex items-start justify-between gap-4 mb-4">
          <h1 class="text-3xl font-display font-bold">
            <span class="text-gradient">{{ topic?.title }}</span>
          </h1>
          <div class="flex gap-2">
            <n-tag v-if="topic?.isPinned" type="primary">
              <template #icon><PinIcon class="w-3 h-3" /></template>
              Sabitlenmiş
            </n-tag>
            <n-tag v-if="topic?.isLocked" type="error">
              <template #icon><LockIcon class="w-3 h-3" /></template>
              Kilitli
            </n-tag>
          </div>
        </div>

        <!-- Topic Stats -->
        <div class="flex items-center gap-6 text-sm text-gray-400">
          <div class="flex items-center gap-2">
            <MessageSquareIcon class="w-4 h-4" />
            <span>{{ replies.length }} Yanıt</span>
          </div>
          <div class="flex items-center gap-2">
            <EyeIcon class="w-4 h-4" />
            <span>{{ topic?.views }} Görüntülenme</span>
          </div>
          <div class="flex items-center gap-2">
            <ClockIcon class="w-4 h-4" />
            <span>{{ topic?.created }}</span>
          </div>
        </div>
      </n-card>

      <!-- Original Post -->
      <n-card class="glass-card mb-6">
        <div class="flex gap-6">
          <!-- Author Sidebar -->
          <div class="flex-shrink-0 w-48 text-center">
            <n-avatar
              round
              :size="96"
              :src="topic?.authorAvatar"
              class="mb-3 ring-2 ring-orange-500 ring-offset-2 ring-offset-gray-900"
            />
            <h3 class="font-bold text-lg">{{ topic?.author }}</h3>
            <n-tag type="primary" size="small" class="my-2">{{ topic?.authorRole }}</n-tag>
            <div class="text-xs text-gray-500 space-y-1">
              <p>{{ topic?.authorPosts }} gönderi</p>
              <p>Üyelik: {{ topic?.authorJoined }}</p>
            </div>
          </div>

          <!-- Post Content -->
          <div class="flex-1 min-w-0">
            <div class="prose prose-invert max-w-none mb-4">
              <p class="text-gray-300 whitespace-pre-line">{{ topic?.content }}</p>
            </div>

            <!-- Post Actions -->
            <div class="flex items-center justify-between pt-4 border-t border-white/10">
              <div class="flex gap-2">
                <n-button quaternary size="small" @click="likeTopic">
                  <template #icon><ThumbsUpIcon class="w-4 h-4" /></template>
                  {{ topic?.likes }} Beğeni
                </n-button>
                <n-button quaternary size="small">
                  <template #icon><ShareIcon class="w-4 h-4" /></template>
                  Paylaş
                </n-button>
              </div>
              <div class="flex gap-2">
                <n-button quaternary size="small" type="error">
                  <template #icon><FlagIcon class="w-4 h-4" /></template>
                  Bildir
                </n-button>
              </div>
            </div>
          </div>
        </div>
      </n-card>

      <!-- Replies -->
      <div class="space-y-4 mb-6">
        <n-card
          v-for="(reply, index) in replies"
          :key="reply.id"
          class="glass-card reply-card"
        >
          <div class="flex gap-6">
            <!-- Reply Author Sidebar -->
            <div class="flex-shrink-0 w-48 text-center">
              <n-avatar round :size="64" :src="reply.authorAvatar" class="mb-3" />
              <h4 class="font-semibold">{{ reply.author }}</h4>
              <n-tag :bordered="false" size="tiny" class="my-1">{{ reply.authorRole }}</n-tag>
              <div class="text-xs text-gray-500">
                <p>{{ reply.authorPosts }} gönderi</p>
              </div>
            </div>

            <!-- Reply Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm text-gray-500">#{{ index + 1 }} · {{ reply.created }}</span>
              </div>

              <div class="prose prose-invert prose-sm max-w-none mb-3">
                <p class="text-gray-300">{{ reply.content }}</p>
              </div>

              <!-- Reply Actions -->
              <div class="flex items-center gap-3 pt-3 border-t border-white/10">
                <n-button text size="tiny" @click="likeReply(reply.id)">
                  <template #icon><ThumbsUpIcon class="w-3 h-3" /></template>
                  {{ reply.likes }}
                </n-button>
                <n-button text size="tiny" @click="quoteReply(reply)">
                  <template #icon><QuoteIcon class="w-3 h-3" /></template>
                  Alıntıla
                </n-button>
                <n-button text size="tiny" type="error">
                  <template #icon><FlagIcon class="w-3 h-3" /></template>
                  Bildir
                </n-button>
              </div>
            </div>
          </div>
        </n-card>
      </div>

      <!-- Pagination -->
      <div class="flex justify-center mb-8">
        <n-pagination
          v-model:page="currentPage"
          :page-count="3"
          show-quick-jumper
        />
      </div>

      <!-- Reply Form -->
      <n-card v-if="!topic?.isLocked" class="glass-card">
        <template #header>
          <span class="font-bold">Yanıt Yaz</span>
        </template>

        <n-form @submit.prevent="submitReply" class="space-y-4">
          <n-form-item>
            <n-input
              v-model:value="newReply"
              type="textarea"
              placeholder="Yanıtınızı yazın..."
              :rows="5"
            />
          </n-form-item>

          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-500">Markdown destekleniyor</span>
            <div class="flex gap-2">
              <n-button quaternary>Önizle</n-button>
              <n-button type="primary" attr-type="submit">
                <template #icon><SendIcon class="w-4 h-4" /></template>
                Yanıtla
              </n-button>
            </div>
          </div>
        </n-form>
      </n-card>

      <!-- Locked Message -->
      <n-card v-else class="glass-card text-center py-12">
        <LockIcon class="w-12 h-12 mx-auto mb-4 text-red-500" />
        <h3 class="text-xl font-bold mb-2">Bu Konu Kilitli</h3>
        <p class="text-gray-400">
          Bu konuya yeni yanıt ekleyemezsiniz.
        </p>
      </n-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  HomeIcon,
  MessageSquareIcon,
  EyeIcon,
  ClockIcon,
  PinIcon,
  LockIcon,
  ThumbsUpIcon,
  ShareIcon,
  FlagIcon,
  QuoteIcon,
  SendIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const topicId = route.params.id

const currentPage = ref(1)

const topic = ref({
  id: 1,
  title: 'Yeni güncelleme hakkında düşünceleriniz?',
  content: `Merhaba arkadaşlar,

Yeni güncelleme ile birlikte gelen özellikleri denedim. Özellikle sunucu performansında ciddi bir iyileşme var. Sizin düşünceleriniz neler?

Ben özellikle şu noktaları beğendim:
- Gelişmiş DDoS koruması
- Yeni admin paneli arayüzü
- Otomatik yedekleme sistemi

Sizce en iyi özellik hangisi?`,
  author: 'Player123',
  authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
  authorRole: 'Admin',
  authorPosts: 1234,
  authorJoined: 'Ocak 2023',
  created: '2 saat önce',
  views: 234,
  likes: 12,
  isPinned: true,
  isLocked: false
})

const replies = ref([
  {
    id: 1,
    author: 'AdminUser',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    authorRole: 'Moderatör',
    authorPosts: 856,
    created: '1 saat önce',
    content: 'Kesinlikle katılıyorum! Yeni admin paneli gerçekten çok kullanışlı. Özellikle sunucu metriklerini canlı olarak görebilmek harika.',
    likes: 5
  },
  {
    id: 2,
    author: 'ProGamer',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    authorRole: 'Üye',
    authorPosts: 623,
    created: '45 dakika önce',
    content: 'DDoS koruması sayesinde sunucum artık çok daha stabil çalışıyor. Geçen hafta büyük bir saldırı aldık ama hiç kesinti olmadı. Harika bir güncelleme!',
    likes: 8
  },
  {
    id: 3,
    author: 'NewbieCS',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
    authorRole: 'Yeni Üye',
    authorPosts: 42,
    created: '30 dakika önce',
    content: 'Yeni başladım ama ben de çok memnunum. Dokümantasyon da çok iyi, kurulumu çok kolay yaptım.',
    likes: 3
  }
])

const newReply = ref('')

const submitReply = () => {
  if (newReply.value.trim()) {
    replies.value.push({
      id: replies.value.length + 1,
      author: 'CurrentUser',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=current',
      authorRole: 'Üye',
      authorPosts: 15,
      created: 'Az önce',
      content: newReply.value,
      likes: 0
    })
    newReply.value = ''
    window.$message?.success('Yanıtınız gönderildi')
  }
}

const likeTopic = () => {
  if (topic.value) {
    topic.value.likes++
    window.$message?.success('Beğenildi')
  }
}

const likeReply = (replyId) => {
  const reply = replies.value.find(r => r.id === replyId)
  if (reply) {
    reply.likes++
    window.$message?.success('Beğenildi')
  }
}

const quoteReply = (reply) => {
  newReply.value = `> ${reply.author} yazdı:\n> ${reply.content}\n\n`
  window.$message?.info('Alıntı eklendi')
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

.reply-card {
  transition: all 0.2s ease;
}

.reply-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
}
</style>
