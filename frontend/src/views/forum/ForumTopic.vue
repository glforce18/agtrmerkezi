<template>
  <div class="min-h-screen bg-dark-bg">
    <!-- Loading State -->
    <div v-if="loading" class="container mx-auto px-4 py-12 max-w-5xl">
      <div class="space-y-4">
        <div class="skeleton h-32 rounded-lg"></div>
        <div class="skeleton h-48 rounded-lg"></div>
        <div class="skeleton h-32 rounded-lg"></div>
      </div>
    </div>

    <div v-else-if="topic" class="container mx-auto px-4 py-6 max-w-6xl">
      <!-- Breadcrumb -->
      <nav class="breadcrumb mb-6">
        <router-link to="/forum">Forum</router-link>
        <span>›</span>
        <router-link
          v-if="topic.category"
          :to="`/forum/category/${topic.category.id}`"
        >
          {{ topic.category.name }}
        </router-link>
        <span>›</span>
        <span class="text-text-primary truncate">{{ topic.title }}</span>
      </nav>

      <!-- Topic Header Card -->
      <div class="card p-6 mb-6">
        <!-- Title & Badges -->
        <div class="flex items-start gap-3 mb-4">
          <h1 class="text-2xl md:text-3xl font-bold text-text-primary flex-1">
            {{ topic.title }}
          </h1>
          <div class="flex gap-2 flex-shrink-0">
            <span v-if="topic.is_pinned" class="badge badge-warning">
              📌 Sabitlendi
            </span>
            <span v-if="topic.is_locked" class="badge badge-error">
              🔒 Kilitli
            </span>
            <span v-if="topic.is_solved" class="badge badge-success">
              ✅ Çözüldü
            </span>
          </div>
        </div>

        <!-- Meta Info -->
        <div class="flex flex-wrap items-center gap-4 text-sm text-text-secondary">
          <div class="flex items-center gap-2">
            <div class="avatar avatar-sm">
              <span>{{ getInitials(topic.author?.username) }}</span>
            </div>
            <span class="font-medium">{{ topic.author?.username || 'Anonim' }}</span>
          </div>
          <span>•</span>
          <span>{{ formatDate(topic.created_at) }}</span>
          <span>•</span>
          <span>{{ topic.view_count || 0 }} görüntüleme</span>
          <span>•</span>
          <span class="text-primary">{{ topic.post_count || 0 }} yanıt</span>
        </div>
      </div>

      <!-- Original Post (OP) -->
      <div class="card mb-6">
        <div class="p-6 border-b border-dark-border">
          <!-- Author Info Bar -->
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div class="avatar avatar-lg mb-2">
                <span>{{ getInitials(topic.author?.username) }}</span>
              </div>
              <div class="text-center">
                <div class="text-xs text-text-muted">{{ topic.author?.role || 'Üye' }}</div>
                <div class="text-xs text-text-muted mt-1">
                  {{ topic.author?.post_count || 0 }} mesaj
                </div>
              </div>
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-3">
                <div class="font-semibold text-text-primary">
                  {{ topic.author?.username || 'Anonim' }}
                </div>
                <div class="text-sm text-text-muted">
                  {{ formatDateTime(topic.created_at) }}
                </div>
              </div>

              <!-- Post Content -->
              <div class="prose prose-invert max-w-none">
                <div v-html="formatContent(topic.content)" class="text-text-primary leading-relaxed"></div>
              </div>

              <!-- Signature -->
              <div v-if="topic.author?.signature" class="mt-4 pt-4 border-t border-dark-border/50 text-sm text-text-muted italic">
                {{ topic.author.signature }}
              </div>
            </div>
          </div>
        </div>

        <!-- Post Actions -->
        <div class="px-6 py-3 bg-dark-elevated flex items-center justify-between">
          <div class="flex items-center gap-2">
            <button class="btn btn-ghost text-sm px-3 py-1">
              👍 Beğen ({{ topic.likes || 0 }})
            </button>
            <button class="btn btn-ghost text-sm px-3 py-1">
              🔖 Kaydet
            </button>
            <button class="btn btn-ghost text-sm px-3 py-1">
              🔗 Paylaş
            </button>
          </div>
          <div v-if="canModerate" class="flex items-center gap-2">
            <button class="btn btn-ghost text-sm px-3 py-1 text-status-warning">
              📝 Düzenle
            </button>
            <button class="btn btn-ghost text-sm px-3 py-1 text-status-error">
              🗑️ Sil
            </button>
          </div>
        </div>
      </div>

      <!-- Replies -->
      <div v-if="replies.length" class="space-y-4 mb-6">
        <h2 class="text-xl font-bold text-text-primary px-2">
          Yanıtlar ({{ replies.length }})
        </h2>

        <div
          v-for="(reply, index) in replies"
          :key="reply.id"
          class="card"
        >
          <div class="p-6 border-b border-dark-border">
            <div class="flex items-start gap-4">
              <!-- Avatar -->
              <div class="flex-shrink-0">
                <div class="avatar avatar-md mb-2">
                  <span>{{ getInitials(reply.author?.username) }}</span>
                </div>
                <div class="text-center">
                  <div class="text-xs text-text-muted">{{ reply.author?.role || 'Üye' }}</div>
                </div>
              </div>

              <!-- Reply Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center gap-2">
                    <span class="font-semibold text-text-primary">
                      {{ reply.author?.username || 'Anonim' }}
                    </span>
                    <span v-if="reply.is_best_answer" class="badge badge-success text-xs">
                      ✅ En İyi Cevap
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm text-text-muted">#{{ index + 1 }}</span>
                    <span class="text-sm text-text-muted">{{ formatDateTime(reply.created_at) }}</span>
                  </div>
                </div>

                <!-- Reply Text -->
                <div class="prose prose-invert max-w-none">
                  <div v-html="formatContent(reply.content)" class="text-text-primary leading-relaxed"></div>
                </div>

                <!-- Signature -->
                <div v-if="reply.author?.signature" class="mt-4 pt-4 border-t border-dark-border/50 text-sm text-text-muted italic">
                  {{ reply.author.signature }}
                </div>
              </div>
            </div>
          </div>

          <!-- Reply Actions -->
          <div class="px-6 py-3 bg-dark-elevated flex items-center justify-between">
            <div class="flex items-center gap-2">
              <button class="btn btn-ghost text-sm px-3 py-1">
                👍 Beğen ({{ reply.likes || 0 }})
              </button>
              <button class="btn btn-ghost text-sm px-3 py-1">
                💬 Yanıtla
              </button>
            </div>
            <div v-if="canModerate" class="flex items-center gap-2">
              <button v-if="!reply.is_best_answer" class="btn btn-ghost text-sm px-3 py-1 text-status-success">
                ✅ En İyi Cevap
              </button>
              <button class="btn btn-ghost text-sm px-3 py-1 text-status-error">
                🗑️ Sil
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- No Replies Yet -->
      <div v-else class="empty-state card mb-6">
        <div class="empty-state-icon">💬</div>
        <p class="empty-state-title">Henüz yanıt yok</p>
        <p class="empty-state-description">İlk yanıtı siz verin!</p>
      </div>

      <!-- Reply Form -->
      <div v-if="!topic.is_locked && authStore.isAuthenticated" class="card p-6">
        <h3 class="text-lg font-semibold text-text-primary mb-4">Yanıt Yaz</h3>
        <form @submit.prevent="submitReply">
          <textarea
            v-model="replyContent"
            class="textarea mb-4"
            rows="6"
            placeholder="Yanıtınızı yazın..."
            required
          ></textarea>
          <div class="flex justify-end gap-3">
            <button type="button" class="btn btn-secondary" @click="replyContent = ''">
              İptal
            </button>
            <button type="submit" class="btn btn-primary" :disabled="submitting || !replyContent.trim()">
              {{ submitting ? 'Gönderiliyor...' : 'Yanıt Gönder' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Locked Message -->
      <div v-else-if="topic.is_locked" class="alert alert-warning">
        Bu konu kilitlenmiştir. Yeni yanıt ekleyemezsiniz.
      </div>

      <!-- Login Required -->
      <div v-else class="alert alert-info">
        Yanıt yazmak için <router-link to="/auth/login" class="font-semibold underline">giriş yapın</router-link>.
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="container mx-auto px-4 py-12 max-w-5xl">
      <div class="empty-state card">
        <div class="empty-state-icon">❌</div>
        <p class="empty-state-title">Konu bulunamadı</p>
        <router-link to="/forum" class="btn btn-primary mt-4">
          Foruma Dön
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import forumAPI from '@/api/forum'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const topic = ref(null)
const replies = ref([])
const replyContent = ref('')
const submitting = ref(false)

const canModerate = computed(() => {
  return authStore.user && (authStore.user.is_admin || authStore.user.id === topic.value?.author?.id)
})

onMounted(async () => {
  await fetchTopic()
})

const fetchTopic = async () => {
  try {
    const topicId = route.params.id

    // Fetch topic
    const topicResponse = await forumAPI.getTopic(topicId)
    topic.value = topicResponse.data || null

    // Fetch replies for the topic
    if (topic.value?.id) {
      try {
        const repliesResponse = await forumAPI.getReplies(topic.value.id)
        // API returns: { success: true, data: [...], pagination: {...} }
        const replyData = repliesResponse.data.data || repliesResponse.data
        replies.value = Array.isArray(replyData) ? replyData : []
      } catch (replyError) {
        console.error('Failed to fetch replies:', replyError)
        replies.value = []
      }
    }
  } catch (error) {
    console.error('Failed to fetch topic:', error)
    topic.value = null
    replies.value = []
  } finally {
    loading.value = false
  }
}

const submitReply = async () => {
  if (!replyContent.value.trim() || submitting.value) return

  submitting.value = true
  try {
    await forumAPI.createReply({
      topic_id: topic.value.id,
      content: replyContent.value
    })

    replyContent.value = ''
    await fetchTopic()
  } catch (error) {
    console.error('Failed to submit reply:', error)
    alert('Yanıt gönderilemedi. Lütfen tekrar deneyin.')
  } finally {
    submitting.value = false
  }
}

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const formatContent = (content) => {
  if (!content) return ''
  return content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const formatDateTime = (dateString) => {
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

  return date.toLocaleString('tr-TR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
