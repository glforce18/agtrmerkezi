<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Loading -->
      <div v-if="loading && !topic" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin text-6xl text-hev-cyan mb-4">λ</div>
          <p class="text-text-secondary font-hev">Konu yükleniyor...</p>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="p-6 bg-combine-red bg-opacity-10 border border-combine-red rounded">
        <p class="text-combine-red font-hev">{{ error }}</p>
        <router-link to="/forum" class="mt-4 inline-block px-6 py-2 bg-lambda-orange text-cyber-black font-lambda rounded">
          Foruma Dön
        </router-link>
      </div>

      <!-- Topic Content -->
      <template v-else-if="topic">
        <!-- Breadcrumb -->
        <div class="mb-6 flex items-center gap-2 text-sm font-hev text-text-secondary">
          <router-link to="/forum" class="hover:text-hev-cyan">Forum</router-link>
          <span>›</span>
          <router-link :to="`/forum/category/${topic.category?.id}`" class="hover:text-hev-cyan">
            {{ topic.category?.name }}
          </router-link>
          <span>›</span>
          <span class="text-text-primary">{{ topic.title }}</span>
        </div>

        <!-- Topic Header -->
        <div class="bg-cyber-panel border border-cyber-border rounded-lg p-6 mb-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <h1 class="text-3xl font-lambda font-bold text-text-primary">
                  {{ topic.title }}
                </h1>
                <span v-if="topic.is_pinned" class="text-combine-yellow" title="Sabitlenmiş">
                  <Pin :size="20" />
                </span>
                <span v-if="topic.is_locked" class="text-combine-red" title="Kilitli">
                  <Lock :size="20" />
                </span>
              </div>

              <div class="flex items-center gap-4 text-sm text-text-secondary font-hev">
                <span class="flex items-center gap-1">
                  <User :size="14" />
                  {{ topic.author?.username || 'Unknown' }}
                </span>
                <span>•</span>
                <span class="flex items-center gap-1">
                  <Clock :size="14" />
                  {{ formatDate(topic.created_at) }}
                </span>
                <span>•</span>
                <span class="flex items-center gap-1">
                  <Eye :size="14" />
                  {{ topic.view_count || 0 }} görüntülenme
                </span>
                <span>•</span>
                <span class="flex items-center gap-1">
                  <MessageSquare :size="14" />
                  {{ topic.reply_count || 0 }} cevap
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div v-if="isAuthenticated" class="flex gap-2">
              <button
                @click="toggleBookmark"
                class="px-4 py-2 bg-cyber-darker border border-cyber-border text-text-secondary hover:border-combine-yellow hover:text-combine-yellow font-lambda text-sm rounded transition-all"
                :class="{ 'border-combine-yellow text-combine-yellow': topic.is_bookmarked }"
              >
                <Bookmark :size="16" :fill="topic.is_bookmarked ? 'currentColor' : 'none'" class="inline" />
              </button>
              <button
                v-if="canEdit"
                class="px-4 py-2 bg-cyber-darker border border-cyber-border text-text-secondary hover:border-lambda-orange hover:text-lambda-orange font-lambda text-sm rounded transition-all"
              >
                <Edit :size="16" class="inline mr-1" />
                Düzenle
              </button>
            </div>
          </div>

          <!-- Topic Content -->
          <div class="prose prose-invert max-w-none">
            <div class="text-text-primary font-body leading-relaxed" v-html="topic.content"></div>
          </div>

          <!-- Reactions -->
          <div class="mt-6 pt-4 border-t border-cyber-border">
            <div class="flex items-center gap-2">
              <button
                v-for="reaction in reactions"
                :key="reaction.type"
                @click="reactToTopic(reaction.type)"
                class="px-3 py-2 bg-cyber-darker border border-cyber-border rounded hover:border-lambda-orange transition-all"
                :class="{ 'border-lambda-orange': topic.user_reaction === reaction.type }"
              >
                <span class="text-lg">{{ reaction.emoji }}</span>
                <span class="ml-1 text-sm font-lambda text-text-secondary">
                  {{ topic.reactions?.[reaction.type] || 0 }}
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- Replies -->
        <div class="mb-6">
          <h2 class="text-2xl font-lambda font-bold text-text-primary mb-4">
            CEVAPLAR ({{ replies.length }})
          </h2>

          <div v-if="replies.length === 0" class="text-center py-10 bg-cyber-panel border border-cyber-border rounded">
            <MessageSquare :size="48" class="inline text-text-secondary opacity-30 mb-3" />
            <p class="text-text-secondary font-hev">Henüz cevap yok. İlk cevabı sen yaz!</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="reply in replies"
              :key="reply.id"
              class="bg-cyber-panel border border-cyber-border rounded-lg p-6 hover:border-lambda-orange transition-all"
            >
              <div class="flex gap-4">
                <!-- Author Info -->
                <div class="w-24 flex flex-col items-center text-center">
                  <div class="w-16 h-16 rounded-full bg-lambda-orange bg-opacity-20 border border-lambda-orange flex items-center justify-center text-lambda-orange font-lambda font-bold text-xl mb-2">
                    {{ reply.author?.username?.[0]?.toUpperCase() || 'U' }}
                  </div>
                  <div class="text-sm font-lambda text-text-primary mb-1">
                    {{ reply.author?.username || 'Unknown' }}
                  </div>
                  <div class="text-xs text-text-secondary font-hev">
                    {{ reply.author?.role || 'Member' }}
                  </div>
                  <div class="text-xs text-text-secondary font-hev mt-1">
                    {{ reply.author?.post_count || 0 }} mesaj
                  </div>
                </div>

                <!-- Reply Content -->
                <div class="flex-1">
                  <div class="flex items-center justify-between mb-3">
                    <div class="text-xs text-text-secondary font-hev flex items-center gap-2">
                      <Clock :size="12" />
                      {{ formatDate(reply.created_at) }}
                      <span v-if="reply.edited_at" class="text-combine-yellow">
                        (düzenlendi: {{ formatDate(reply.edited_at) }})
                      </span>
                    </div>

                    <div class="flex gap-2">
                      <button
                        v-if="canEditReply(reply)"
                        class="text-text-secondary hover:text-lambda-orange transition-all"
                      >
                        <Edit :size="14" />
                      </button>
                      <button
                        v-if="canDeleteReply(reply)"
                        class="text-text-secondary hover:text-combine-red transition-all"
                      >
                        <Trash :size="14" />
                      </button>
                    </div>
                  </div>

                  <div class="prose prose-invert max-w-none mb-4">
                    <div class="text-text-primary font-body leading-relaxed" v-html="reply.content"></div>
                  </div>

                  <!-- Reply Reactions -->
                  <div class="flex items-center gap-2">
                    <button
                      v-for="reaction in reactions"
                      :key="reaction.type"
                      @click="reactToReply(reply.id, reaction.type)"
                      class="px-2 py-1 bg-cyber-darker border border-cyber-border rounded text-xs hover:border-lambda-orange transition-all"
                      :class="{ 'border-lambda-orange': reply.user_reaction === reaction.type }"
                    >
                      <span>{{ reaction.emoji }}</span>
                      <span class="ml-1 font-lambda text-text-secondary">
                        {{ reply.reactions?.[reaction.type] || 0 }}
                      </span>
                    </button>
                    <button
                      class="px-2 py-1 text-xs text-text-secondary hover:text-hev-cyan font-lambda transition-all"
                    >
                      <Reply :size="14" class="inline mr-1" />
                      Yanıtla
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Reply Form -->
        <div v-if="isAuthenticated && !topic.is_locked" class="bg-cyber-panel border border-cyber-border rounded-lg p-6">
          <h3 class="text-xl font-lambda font-bold text-text-primary mb-4">CEVAP YAZ</h3>

          <form @submit.prevent="submitReply">
            <textarea
              v-model="replyContent"
              rows="6"
              placeholder="Cevabınızı buraya yazın..."
              class="w-full bg-cyber-darker border border-cyber-border rounded p-4 text-text-primary font-body outline-none focus:border-hev-cyan transition-all resize-none"
              required
            ></textarea>

            <div class="flex items-center justify-between mt-4">
              <div class="text-xs text-text-secondary font-hev">
                Markdown formatı desteklenmektedir
              </div>

              <button
                type="submit"
                :disabled="!replyContent.trim() || submitting"
                class="px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <Send :size="16" class="inline mr-2" />
                CEVAP GÖNDER
              </button>
            </div>
          </form>
        </div>

        <!-- Login Prompt -->
        <div v-else-if="!isAuthenticated" class="text-center py-10 bg-cyber-panel border border-cyber-border rounded">
          <p class="text-text-secondary font-hev mb-4">Cevap yazmak için giriş yapmalısınız</p>
          <router-link
            to="/login"
            class="inline-block px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all"
          >
            GİRİŞ YAP
          </router-link>
        </div>

        <!-- Locked Notice -->
        <div v-else class="text-center py-6 bg-combine-red bg-opacity-10 border border-combine-red rounded">
          <Lock :size="32" class="inline text-combine-red mb-2" />
          <p class="text-combine-red font-hev">Bu konu kilitlenmiştir</p>
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
  Pin,
  Lock,
  User,
  Clock,
  Eye,
  MessageSquare,
  Bookmark,
  Edit,
  Trash,
  Reply,
  Send
} from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref(null)
const topic = ref(null)
const replies = ref([])
const replyContent = ref('')
const submitting = ref(false)

const reactions = [
  { type: 'like', emoji: '👍' },
  { type: 'love', emoji: '❤️' },
  { type: 'laugh', emoji: '😄' },
  { type: 'wow', emoji: '😮' },
  { type: 'sad', emoji: '😢' }
]

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const userId = computed(() => authStore.user?.id)
const isAdmin = computed(() => authStore.isAdmin)
const topicId = computed(() => route.params.id)

const canEdit = computed(() => {
  if (!topic.value) return false
  return isAdmin.value || topic.value.author?.id === userId.value
})

// Methods
function canEditReply(reply) {
  return isAdmin.value || reply.author?.id === userId.value
}

function canDeleteReply(reply) {
  return isAdmin.value || reply.author?.id === userId.value
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

  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadTopic() {
  loading.value = true
  error.value = null

  try {
    const [topicRes, repliesRes] = await Promise.all([
      forumAPI.getTopic(topicId.value),
      forumAPI.getReplies(topicId.value)
    ])

    topic.value = topicRes.data
    replies.value = repliesRes.data.replies || repliesRes.data || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Konu yüklenemedi'
    console.error('Load topic error:', err)
  } finally {
    loading.value = false
  }
}

async function submitReply() {
  if (!replyContent.value.trim() || submitting.value) return

  submitting.value = true
  try {
    const response = await forumAPI.createReply(topicId.value, {
      content: replyContent.value
    })

    replies.value.push(response.data)
    replyContent.value = ''

    // Increment reply count
    if (topic.value) {
      topic.value.reply_count = (topic.value.reply_count || 0) + 1
    }
  } catch (err) {
    console.error('Submit reply error:', err)
    alert(err.response?.data?.detail || 'Cevap gönderilemedi')
  } finally {
    submitting.value = false
  }
}

async function reactToTopic(reactionType) {
  if (!isAuthenticated.value) {
    alert('Tepki vermek için giriş yapmalısınız')
    return
  }

  try {
    await forumAPI.reactToTopic(topicId.value, reactionType)
    // Update local state
    if (!topic.value.reactions) topic.value.reactions = {}
    topic.value.reactions[reactionType] = (topic.value.reactions[reactionType] || 0) + 1
    topic.value.user_reaction = reactionType
  } catch (err) {
    console.error('React to topic error:', err)
  }
}

async function reactToReply(replyId, reactionType) {
  if (!isAuthenticated.value) {
    alert('Tepki vermek için giriş yapmalısınız')
    return
  }

  try {
    await forumAPI.reactToReply(topicId.value, replyId, reactionType)
    // Update local state
    const reply = replies.value.find(r => r.id === replyId)
    if (reply) {
      if (!reply.reactions) reply.reactions = {}
      reply.reactions[reactionType] = (reply.reactions[reactionType] || 0) + 1
      reply.user_reaction = reactionType
    }
  } catch (err) {
    console.error('React to reply error:', err)
  }
}

async function toggleBookmark() {
  if (!isAuthenticated.value) return

  try {
    if (topic.value.is_bookmarked) {
      await forumAPI.removeBookmark(topicId.value)
      topic.value.is_bookmarked = false
    } else {
      await forumAPI.bookmarkTopic(topicId.value)
      topic.value.is_bookmarked = true
    }
  } catch (err) {
    console.error('Toggle bookmark error:', err)
  }
}

// Lifecycle
onMounted(() => {
  loadTopic()
})
</script>

<style scoped>
.bg-lambda-gradient {
  background: linear-gradient(135deg, #FF6B35 0%, #E85D2C 100%);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}

.prose {
  color: inherit;
}

.prose p {
  margin-bottom: 1rem;
}

.prose a {
  color: #00F5FF;
  text-decoration: underline;
}

.prose code {
  background: rgba(0, 0, 0, 0.5);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
  color: #39FF14;
}
</style>
