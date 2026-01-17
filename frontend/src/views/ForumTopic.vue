<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Breadcrumb -->
      <div class="breadcrumbs mb-4 animate-slide-down">
        <ul>
          <li>
            <router-link to="/forum" class="hover:text-primary transition-colors">
              <HomeIcon class="w-4 h-4 inline mr-1" />
              Forum
            </router-link>
          </li>
          <li>
            <router-link to="/forum/category/1" class="hover:text-primary transition-colors">
              Genel Tartışma
            </router-link>
          </li>
          <li class="text-primary truncate">{{ topic?.title }}</li>
        </ul>
      </div>

      <!-- Topic Header -->
      <BaseCard variant="glass" class="mb-6 animate-slide-up">
        <div class="p-6">
          <div class="flex items-start justify-between gap-4 mb-4">
            <h1 class="text-3xl font-display font-bold">
              <span class="neon-text">{{ topic?.title }}</span>
            </h1>
            <div class="flex gap-2">
              <div v-if="topic?.isPinned" class="badge badge-primary">
                <PinIcon class="w-3 h-3 mr-1" />
                Sabitlenmiş
              </div>
              <div v-if="topic?.isLocked" class="badge badge-error">
                <LockIcon class="w-3 h-3 mr-1" />
                Kilitli
              </div>
            </div>
          </div>

          <!-- Topic Stats -->
          <div class="flex items-center gap-6 text-sm opacity-60">
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
        </div>
      </BaseCard>

      <!-- Original Post -->
      <BaseCard variant="glass" class="mb-6 animate-slide-up" style="animation-delay: 0.1s">
        <div class="p-6">
          <div class="flex gap-6">
            <!-- Author Sidebar -->
            <div class="flex-shrink-0 w-48 text-center">
              <div class="avatar mb-3">
                <div class="w-24 h-24 rounded-full ring ring-primary ring-offset-2 ring-offset-slate-900">
                  <img :src="topic?.authorAvatar" />
                </div>
              </div>
              <h3 class="font-bold text-lg">{{ topic?.author }}</h3>
              <div class="badge badge-sm badge-primary my-2">{{ topic?.authorRole }}</div>
              <div class="text-xs opacity-50 space-y-1">
                <p>{{ topic?.authorPosts }} gönderi</p>
                <p>Üyelik: {{ topic?.authorJoined }}</p>
              </div>
            </div>

            <!-- Post Content -->
            <div class="flex-1 min-w-0">
              <div class="prose prose-invert max-w-none mb-4">
                <p>{{ topic?.content }}</p>
              </div>

              <!-- Post Actions -->
              <div class="flex items-center justify-between pt-4 border-t border-base-300">
                <div class="flex gap-2">
                  <button class="btn btn-sm btn-ghost" @click="likeTopic">
                    <ThumbsUpIcon class="w-4 h-4 mr-1" />
                    {{ topic?.likes }} Beğeni
                  </button>
                  <button class="btn btn-sm btn-ghost">
                    <ShareIcon class="w-4 h-4 mr-1" />
                    Paylaş
                  </button>
                </div>
                <div class="flex gap-2">
                  <button class="btn btn-sm btn-ghost text-error">
                    <FlagIcon class="w-4 h-4 mr-1" />
                    Bildir
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Replies -->
      <div class="space-y-4 mb-6 animate-slide-up" style="animation-delay: 0.2s">
        <BaseCard
          v-for="(reply, index) in replies"
          :key="reply.id"
          variant="glass"
          class="card-hover"
        >
          <div class="p-6">
            <div class="flex gap-6">
              <!-- Reply Author Sidebar -->
              <div class="flex-shrink-0 w-48 text-center">
                <div class="avatar mb-3">
                  <div class="w-16 h-16 rounded-full">
                    <img :src="reply.authorAvatar" />
                  </div>
                </div>
                <h4 class="font-semibold">{{ reply.author }}</h4>
                <div class="badge badge-xs badge-ghost my-1">{{ reply.authorRole }}</div>
                <div class="text-xs opacity-50">
                  <p>{{ reply.authorPosts }} gönderi</p>
                </div>
              </div>

              <!-- Reply Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-3">
                  <span class="text-sm opacity-50">#{{ index + 1 }} · {{ reply.created }}</span>
                </div>

                <div class="prose prose-invert prose-sm max-w-none mb-3">
                  <p>{{ reply.content }}</p>
                </div>

                <!-- Reply Actions -->
                <div class="flex items-center gap-3 pt-3 border-t border-base-300">
                  <button class="btn btn-xs btn-ghost" @click="likeReply(reply.id)">
                    <ThumbsUpIcon class="w-3 h-3 mr-1" />
                    {{ reply.likes }}
                  </button>
                  <button class="btn btn-xs btn-ghost" @click="quoteReply(reply)">
                    <QuoteIcon class="w-3 h-3 mr-1" />
                    Alıntıla
                  </button>
                  <button class="btn btn-xs btn-ghost text-error">
                    <FlagIcon class="w-3 h-3 mr-1" />
                    Bildir
                  </button>
                </div>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Pagination -->
      <div class="flex justify-center mb-8 animate-slide-up" style="animation-delay: 0.3s">
        <div class="join">
          <button class="join-item btn btn-sm">«</button>
          <button class="join-item btn btn-sm btn-active">1</button>
          <button class="join-item btn btn-sm">2</button>
          <button class="join-item btn btn-sm">3</button>
          <button class="join-item btn btn-sm">»</button>
        </div>
      </div>

      <!-- Reply Form -->
      <BaseCard v-if="!topic?.isLocked" variant="glass" class="animate-slide-up" style="animation-delay: 0.4s">
        <div class="p-6">
          <h3 class="text-xl font-bold mb-4">Yanıt Yaz</h3>

          <form @submit.prevent="submitReply" class="space-y-4">
            <div class="form-control">
              <textarea
                v-model="newReply"
                class="textarea textarea-bordered h-32 bg-base-200"
                placeholder="Yanıtınızı yazın..."
                required
              ></textarea>
            </div>

            <div class="flex justify-between items-center">
              <div class="text-sm opacity-50">
                Markdown destekleniyor
              </div>
              <div class="flex gap-2">
                <BaseButton variant="ghost" type="button">
                  Önizle
                </BaseButton>
                <BaseButton variant="gaming" type="submit">
                  <SendIcon class="w-4 h-4 mr-2" />
                  Yanıtla
                </BaseButton>
              </div>
            </div>
          </form>
        </div>
      </BaseCard>

      <!-- Locked Message -->
      <BaseCard v-else variant="glass" class="text-center py-12 animate-slide-up" style="animation-delay: 0.4s">
        <LockIcon class="w-12 h-12 mx-auto mb-4 text-error" />
        <h3 class="text-xl font-bold mb-2">Bu Konu Kilitli</h3>
        <p class="opacity-60">
          Bu konuya yeni yanıt ekleyemezsiniz.
        </p>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
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

const topic = ref({
  id: 1,
  title: 'Yeni güncelleme hakkında düşünceleriniz?',
  content: 'Merhaba arkadaşlar,\n\nYeni güncelleme ile birlikte gelen özellikleri denedim. Özellikle sunucu performansında ciddi bir iyileşme var. Sizin düşünceleriniz neler?\n\nBen özellikle şu noktaları beğendim:\n- Gelişmiş DDoS koruması\n- Yeni admin paneli arayüzü\n- Otomatik yedekleme sistemi\n\nSizce en iyi özellik hangisi?',
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
  }
}

const likeTopic = () => {
  if (topic.value) {
    topic.value.likes++
  }
}

const likeReply = (replyId) => {
  const reply = replies.value.find(r => r.id === replyId)
  if (reply) {
    reply.likes++
  }
}

const quoteReply = (reply) => {
  newReply.value = `> ${reply.author} yazdı:\n> ${reply.content}\n\n`
}
</script>

<style scoped>
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

.prose {
  @apply opacity-70;
}

.prose p {
  @apply mb-4 leading-relaxed;
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
