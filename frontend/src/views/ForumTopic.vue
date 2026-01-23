<template>
  <ForumLayout
    :show-right-sidebar="false"
    :full-width="false"
    class="forum-page"
  >
    <!-- Left Sidebar: Category Navigation -->
    <template #sidebar-left>
      <ForumSidebar
        :categories="allCategories"
        :active-category="topic?.categoryId"
        :stats="sidebarStats"
        @category-click="handleCategoryClick"
      />
    </template>

    <!-- Main Content -->
    <template #default>
      <!-- Breadcrumb -->
      <nav class="forum-breadcrumb-enhanced" aria-label="Gezinti">
        <a href="#" @click.prevent="router.push('/forum')" class="forum-breadcrumb-item">
          <HomeIcon class="w-4 h-4" />
          <span>Forum</span>
        </a>
        <ChevronRightIcon class="w-4 h-4 forum-breadcrumb-separator" />
        <a href="#" @click.prevent="router.push(`/forum/category/${topic?.categoryId || 1}`)" class="forum-breadcrumb-item">
          <FolderIcon class="w-4 h-4" />
          <span>{{ topic?.categoryName || 'Kategori' }}</span>
        </a>
        <ChevronRightIcon class="w-4 h-4 forum-breadcrumb-separator" />
        <span class="forum-breadcrumb-current">
          <FileTextIcon class="w-4 h-4" />
          {{ topic?.title }}
        </span>
      </nav>

      <!-- Topic Header -->
      <section class="forum-topic-header">
        <div class="forum-topic-header__badges">
          <span v-if="topic?.isPinned" class="forum-badge-enhanced forum-badge-enhanced--warning">
            <PinIcon class="w-3 h-3" />
            Sabitlenmis
          </span>
          <span v-if="topic?.isLocked" class="forum-badge-enhanced forum-badge-enhanced--error">
            <LockIcon class="w-3 h-3" />
            Kilitli
          </span>
          <span v-if="topic?.isHot" class="forum-badge-enhanced forum-badge-enhanced--hot">
            <FlameIcon class="w-3 h-3" />
            Populer
          </span>
          <span v-if="topic?.isSolved" class="forum-badge-enhanced forum-badge-enhanced--success">
            <CheckCircleIcon class="w-3 h-3" />
            Cozuldu
          </span>
        </div>
        <h1 class="forum-heading-enhanced forum-heading--xl">{{ topic?.title }}</h1>
        <div class="forum-topic-header__stats">
          <span class="forum-stat-enhanced">
            <span class="forum-stat-enhanced__icon"><MessageSquareIcon class="w-3.5 h-3.5" /></span>
            <span class="forum-stat-enhanced__value">{{ replies.length }}</span>
            <span class="forum-stat-enhanced__label">Yanit</span>
          </span>
          <span class="forum-stat-enhanced">
            <span class="forum-stat-enhanced__icon"><EyeIcon class="w-3.5 h-3.5" /></span>
            <span class="forum-stat-enhanced__value">{{ topic?.views }}</span>
            <span class="forum-stat-enhanced__label">Goruntulenme</span>
          </span>
          <span class="forum-stat-enhanced">
            <span class="forum-stat-enhanced__icon"><HeartIcon class="w-3.5 h-3.5" /></span>
            <span class="forum-stat-enhanced__value">{{ topic?.likes }}</span>
            <span class="forum-stat-enhanced__label">Begeni</span>
          </span>
          <span class="forum-stat-enhanced">
            <span class="forum-stat-enhanced__icon"><ClockIcon class="w-3.5 h-3.5" /></span>
            <span class="forum-stat-enhanced__value">{{ topic?.created }}</span>
          </span>
          <span v-if="wsViewerCount > 0" class="forum-stat-enhanced forum-stat-enhanced--success">
            <span class="forum-live-dot"></span>
            <span class="forum-stat-enhanced__icon"><UsersIcon class="w-3.5 h-3.5" /></span>
            <span class="forum-stat-enhanced__value">{{ wsViewerCount }}</span>
            <span class="forum-stat-enhanced__label">izliyor</span>
          </span>
        </div>
      </section>

      <!-- Loading State -->
      <template v-if="isLoading">
        <ForumSkeleton type="post-card" />
        <ForumSkeleton v-for="n in 3" :key="n" type="post-card" />
      </template>

      <template v-else>
        <!-- Best Answer (if exists) -->
        <ForumBestAnswer
          v-if="bestAnswer"
          :post="bestAnswer"
          :marked-by="topic?.author"
          @goto="scrollToReply(bestAnswer.id)"
        />

        <!-- Original Post -->
        <ForumPostCard
          :post="formatPostForCard(topic)"
          :show-level="true"
          :show-level-ring="true"
          :show-actions="true"
          :can-interact="isLoggedIn"
          @like="likeTopic"
          @reply="scrollToReplyForm"
          @quote="quotePost(topic)"
          @share="showShareModal = true"
          @report="reportTopic"
          @action="handleTopicAction"
        />

        <!-- Typing Indicator -->
        <Transition name="fade">
          <div v-if="typingUsers.length > 0" class="forum-typing-indicator">
            <div class="forum-typing-dots">
              <span></span><span></span><span></span>
            </div>
            <span class="forum-meta">
              <strong>{{ typingUsers.map(u => u.username || u).join(', ') }}</strong> yaziyor...
            </span>
          </div>
        </Transition>

        <!-- Replies Section -->
        <section class="forum-replies-section">
          <div class="forum-replies-header">
            <h2 class="forum-heading forum-heading--md">
              <MessageSquareIcon class="w-5 h-5" />
              Yanitlar ({{ replies.length }})
            </h2>
            <n-select
              v-model:value="sortOrder"
              :options="sortOptions"
              size="small"
              style="width: 150px"
            />
          </div>

          <!-- Replies List -->
          <div class="forum-replies-list">
            <ForumPostCard
              v-for="(reply, index) in sortedReplies"
              :key="reply.id"
              :id="`reply-${reply.id}`"
              :post="formatReplyForCard(reply, index)"
              :show-level="true"
              :show-level-ring="true"
              :show-actions="true"
              :can-interact="isLoggedIn"
              :class="{ 'forum-reply--highlighted': highlightedReplyId === reply.id }"
              @like="() => likeReply(reply.id)"
              @reply="() => replyToUser(reply)"
              @quote="() => quoteReply(reply)"
              @report="() => reportReply(reply)"
              @action="(e) => handleReplyAction(e, reply)"
            />
          </div>

          <!-- Load More Button -->
          <div v-if="canLoadMoreReplies" class="forum-load-more">
            <button
              class="forum-load-more__btn"
              :disabled="isLoadingMoreReplies"
              @click="loadMoreReplies"
            >
              <template v-if="isLoadingMoreReplies">
                <span class="forum-loading-dots"><span></span><span></span><span></span></span>
                Yanitlar yukleniyor...
              </template>
              <template v-else>
                <ChevronDownIcon class="w-5 h-5" />
                Daha fazla yanit yukle ({{ allSortedReplies.length - displayedRepliesCount }} kaldi)
              </template>
            </button>
          </div>

          <!-- Loading More Skeleton -->
          <template v-if="isLoadingMoreReplies">
            <ForumSkeleton v-for="n in 3" :key="n" type="post-card" />
          </template>
        </section>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="forum-pagination">
          <n-pagination
            v-model:page="currentPage"
            :page-count="totalPages"
            :page-slot="7"
            show-quick-jumper
          />
        </div>

        <!-- Reply Form -->
        <section
          v-if="!topic?.isLocked"
          ref="replyFormRef"
          id="reply-form"
          class="forum-reply-form"
        >
          <!-- Steam Required Notice -->
          <div v-if="!hasSteam" class="forum-steam-notice">
            <div class="forum-steam-notice__icon">
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10c-4.6 0-8.45-3.08-9.64-7.27l3.83 1.58a2.84 2.84 0 0 0 2.78 2.27c1.56 0 2.83-1.27 2.83-2.83v-.13l3.4-2.43h.08c2.08 0 3.77-1.69 3.77-3.77s-1.69-3.77-3.77-3.77-3.77 1.69-3.77 3.77v.05l-2.37 3.46-.16-.01c-.55 0-1.08.16-1.53.45L2 11.54A10 10 0 0 1 12 2z"/>
              </svg>
            </div>
            <div class="forum-steam-notice__content">
              <p>Steam hesabi baglayarak yanit yazabilirsiniz</p>
              <span class="forum-meta">Topluluk guvenligi icin Steam dogrulamasi gereklidir</span>
            </div>
            <n-button size="small" type="info" @click="connectSteam">
              Steam Bagla
            </n-button>
          </div>

          <!-- Quote Preview -->
          <Transition name="slide-down">
            <div v-if="quotedReply" class="forum-reply-preview">
              <div class="forum-reply-preview__header">
                <QuoteIcon class="w-4 h-4" />
                <span><strong>{{ quotedReply.author }}</strong> kullanicisina yanit veriyorsunuz:</span>
              </div>
              <div class="forum-quote-content">
                {{ quotedReply.content.substring(0, 200) }}{{ quotedReply.content.length > 200 ? '...' : '' }}
              </div>
              <button class="forum-reply-preview__close" @click="clearQuote" type="button">
                <XIcon class="w-4 h-4" />
              </button>
            </div>
          </Transition>

          <div class="forum-reply-form__content">
            <h3 class="forum-heading forum-heading--sm">
              <EditIcon class="w-5 h-5" />
              Yanit Yaz
            </h3>

            <form @submit.prevent="submitReply">
              <!-- Editor Toolbar -->
              <div class="forum-editor-toolbar-enhanced">
                <button
                  v-for="tool in editorTools"
                  :key="tool.action"
                  type="button"
                  class="forum-toolbar-btn-enhanced"
                  :title="tool.label"
                  @click="applyFormat(tool.action)"
                >
                  <component :is="tool.icon" class="w-4 h-4" />
                </button>
                <div class="forum-toolbar-divider-enhanced"></div>
                <button
                  type="button"
                  class="forum-toolbar-btn-enhanced forum-toolbar-btn-labeled"
                  :class="{ 'forum-toolbar-btn-enhanced--active': showPreview }"
                  @click="showPreview = !showPreview"
                >
                  <EyeIcon class="w-4 h-4" />
                  <span>Onizle</span>
                </button>
              </div>

              <!-- Editor -->
              <div class="forum-editor" :class="{ 'forum-editor--split': showPreview }">
                <div class="forum-editor__input">
                  <n-input
                    ref="editorRef"
                    v-model:value="newReply"
                    type="textarea"
                    placeholder="Yanitinizi yazin... Markdown kullanabilirsiniz. (min 5 karakter)"
                    :rows="8"
                    :status="replyValidation.status"
                    @input="handleTyping"
                    @blur="validateReply"
                  />
                  <div v-if="replyValidation.message" class="forum-reply-validation-error">
                    {{ replyValidation.message }}
                  </div>
                </div>
                <Transition name="fade">
                  <div v-if="showPreview" class="forum-editor__preview">
                    <div class="forum-meta">Onizleme</div>
                    <div class="forum-body" v-html="previewContent"></div>
                  </div>
                </Transition>
              </div>

              <!-- Form Footer -->
              <div class="forum-reply-form__footer">
                <div class="forum-reply-form__counter">
                  <span>{{ newReply.length }} / 10000 karakter</span>
                  <n-progress
                    type="line"
                    :percentage="(newReply.length / 10000) * 100"
                    :show-indicator="false"
                    :height="4"
                    style="width: 100px"
                    :color="newReply.length > 9000 ? '#ef4444' : '#f97316'"
                  />
                </div>
                <div class="forum-reply-form__actions">
                  <n-button quaternary @click="saveDraft">
                    <template #icon><SaveIcon class="w-4 h-4" /></template>
                    Taslak Kaydet
                  </n-button>
                  <n-button
                    type="primary"
                    attr-type="submit"
                    :disabled="!isReplyValid || isSubmitting"
                    :loading="isSubmitting"
                  >
                    <template #icon><SendIcon class="w-4 h-4" /></template>
                    Yanitla
                  </n-button>
                </div>
              </div>
            </form>
          </div>
        </section>

        <!-- Locked Topic Message -->
        <div v-else class="forum-locked-message">
          <LockIcon class="w-16 h-16" />
          <h3 class="forum-heading forum-heading--lg">Bu Konu Kilitli</h3>
          <p class="forum-meta">Bu konuya yeni yanit ekleyemezsiniz. Daha fazla bilgi icin moderatorlerle iletisime gecin.</p>
        </div>
      </template>
    </template>
  </ForumLayout>

  <!-- Floating Action Bar -->
  <Transition name="slide-up">
    <div v-if="showFloatingBar" class="forum-floating-bar forum-scrollbar-hidden">
      <button class="forum-floating-bar__btn forum-fab-mini" :class="{ liked: hasLikedTopic }" @click="likeTopic" type="button">
        <HeartIcon class="w-5 h-5" />
        <span>{{ topic?.likes }}</span>
      </button>
      <div class="forum-floating-bar__divider"></div>
      <button class="forum-floating-bar__btn forum-fab-mini" @click="showShareModal = true" type="button">
        <Share2Icon class="w-5 h-5" />
      </button>
      <button class="forum-floating-bar__btn forum-fab-mini" @click="reportTopic" type="button">
        <FlagIcon class="w-5 h-5" />
      </button>
      <div class="forum-floating-bar__divider"></div>
      <button class="forum-floating-bar__btn forum-fab-mini" @click="scrollToReplyForm" type="button">
        <MessageSquareIcon class="w-5 h-5" />
      </button>
      <button class="forum-floating-bar__btn forum-fab-mini" @click="scrollToTop" type="button">
        <ArrowUpIcon class="w-5 h-5" />
      </button>
    </div>
  </Transition>

  <!-- Share Modal -->
  <n-modal v-model:show="showShareModal" preset="card" title="Paylas" class="forum-modal-enhanced" style="max-width: 400px">
    <div class="forum-share-modal">
      <div class="forum-share-modal__url">
        <n-input :value="shareUrl" readonly />
        <n-button type="primary" class="forum-btn-enhanced forum-btn-enhanced--primary" @click="copyShareUrl">
          <template #icon><CopyIcon class="w-4 h-4" /></template>
          Kopyala
        </n-button>
      </div>
      <div class="forum-share-modal__social">
        <button
          v-for="social in socialShareOptions"
          :key="social.name"
          class="forum-share-modal__social-btn forum-btn-enhanced"
          :style="{ '--color': social.color }"
          @click="shareToSocial(social)"
          type="button"
        >
          <component :is="social.icon" class="w-5 h-5" />
          <span>{{ social.name }}</span>
        </button>
      </div>
    </div>
  </n-modal>

  <!-- Report Modal -->
  <n-modal v-model:show="showReportModal" preset="card" title="Icerik Bildir" class="forum-modal-enhanced" style="max-width: 500px">
    <n-form :model="reportForm">
      <n-form-item label="Bildirim Nedeni">
        <n-radio-group v-model:value="reportForm.reason">
          <div v-for="reason in reportReasons" :key="reason.value" class="forum-report-option">
            <n-radio :value="reason.value">{{ reason.label }}</n-radio>
          </div>
        </n-radio-group>
      </n-form-item>
      <n-form-item label="Ek Aciklama">
        <n-input v-model:value="reportForm.description" type="textarea" :rows="4" placeholder="Daha fazla detay ekleyin..." class="forum-reply-textarea" />
      </n-form-item>
    </n-form>
    <template #footer>
      <div class="forum-modal-footer-enhanced">
        <n-button class="forum-btn-enhanced forum-btn-enhanced--secondary" @click="showReportModal = false">Iptal</n-button>
        <n-button type="error" class="forum-btn-enhanced" @click="submitReport">
          <template #icon><FlagIcon class="w-4 h-4" /></template>
          Bildir
        </n-button>
      </div>
    </template>
  </n-modal>

  <!-- Edit Topic Modal -->
  <n-modal v-model:show="showEditTopicModal" preset="card" title="Konu Duzenle" class="forum-modal-enhanced" style="max-width: 600px">
    <n-form :model="editTopicForm">
      <n-form-item label="Baslik">
        <n-input v-model:value="editTopicForm.title" placeholder="Konu basligi..." maxlength="200" show-count />
      </n-form-item>
      <n-form-item label="Icerik">
        <n-input v-model:value="editTopicForm.content" type="textarea" :rows="10" placeholder="Konu icerigi..." maxlength="10000" show-count />
      </n-form-item>
    </n-form>
    <template #footer>
      <div class="forum-modal-footer-enhanced">
        <n-button class="forum-btn-enhanced forum-btn-enhanced--secondary" @click="showEditTopicModal = false">Iptal</n-button>
        <n-button type="primary" class="forum-btn-enhanced forum-btn-enhanced--primary" @click="saveEditTopic">
          <template #icon><SaveIcon class="w-4 h-4" /></template>
          Kaydet
        </n-button>
      </div>
    </template>
  </n-modal>

  <!-- Edit Reply Modal -->
  <n-modal v-model:show="showEditReplyModal" preset="card" title="Yanit Duzenle" class="forum-modal-enhanced" style="max-width: 600px">
    <n-form>
      <n-form-item label="Icerik">
        <n-input v-model:value="editReplyContent" type="textarea" :rows="8" placeholder="Yanit icerigi..." maxlength="10000" show-count />
      </n-form-item>
    </n-form>
    <template #footer>
      <div class="forum-modal-footer-enhanced">
        <n-button class="forum-btn-enhanced forum-btn-enhanced--secondary" @click="cancelEditReply">Iptal</n-button>
        <n-button type="primary" class="forum-btn-enhanced forum-btn-enhanced--primary" @click="saveEditReply(editingReplyId)">
          <template #icon><SaveIcon class="w-4 h-4" /></template>
          Kaydet
        </n-button>
      </div>
    </template>
  </n-modal>

  <!-- Steam Required Modal -->
  <SteamRequiredModal
    :show="showSteamModal"
    @close="closeModal"
    @connect="connectSteam"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useForumTopicWS } from '@/composables/useWebSocket'
import { useRequireSteam } from '@/composables/useRequireSteam'
import { useRequireAuth } from '@/composables/useRequireAuth'
import { useAuthStore } from '@/stores/auth'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import { ForumLayout, ForumSidebar, ForumPostCard, ForumBestAnswer, ForumSkeleton } from '@/components/forum'
import {
  HomeIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  FolderIcon,
  FileTextIcon,
  MessageSquareIcon,
  EyeIcon,
  ClockIcon,
  PinIcon,
  LockIcon,
  FlameIcon,
  HeartIcon,
  Share2Icon,
  FlagIcon,
  QuoteIcon,
  SendIcon,
  EditIcon,
  XIcon,
  SaveIcon,
  CopyIcon,
  ArrowUpIcon,
  BoldIcon,
  ItalicIcon,
  CodeIcon,
  ListIcon,
  ImageIcon,
  LinkIcon,
  CheckCircleIcon,
  UsersIcon,
  HelpCircleIcon,
  ShieldIcon,
  ZapIcon,
  TwitterIcon,
  FacebookIcon,
  LinkedinIcon,
  MailIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// Make topicId reactive - updates when route changes
// Note: route.params.id might be a slug, so we use topic.value?.id for API calls
const topicId = computed(() => route.params.id)

// Helper to get the actual numeric topic ID for API calls
const getTopicId = () => topic.value?.id || topicId.value

// Stores
const authStore = useAuthStore()

// Steam & Auth
const { hasSteam, showSteamModal, requireSteam, connectSteam, closeModal } = useRequireSteam()
const { isLoggedIn, requireAuth } = useRequireAuth()

// Admin check
const isAdmin = computed(() => ['admin', 'superadmin', 'moderator'].includes(authStore.user?.role) || authStore.user?.is_admin)

// Get CSRF token from cookie
const getCsrfToken = () => {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrf_token') return value
  }
  return null
}

// Refs
const replyFormRef = ref(null)
const editorRef = ref(null)

// State
const isLoading = ref(true)
const fetchError = ref(null)
const currentPage = ref(1)
const totalPages = ref(1)
const sortOrder = ref('oldest')
const showFloatingBar = ref(false)
const showPreview = ref(false)
const showReportModal = ref(false)
const showShareModal = ref(false)
const isSubmitting = ref(false)
const hasLikedTopic = ref(false)
const highlightedReplyId = ref(null)
const quotedReply = ref(null)
const newReply = ref('')

// Reply validation
const replyValidation = reactive({ status: undefined, message: '' })

// Lazy loading
const REPLIES_PER_PAGE = 10
const displayedRepliesCount = ref(REPLIES_PER_PAGE)
const isLoadingMoreReplies = ref(false)

// WebSocket state
const wsViewerCount = ref(0)
const wsViewers = ref([])
const typingUsers = ref([])
let forumWS = null

// Timeout tracking for cleanup
let highlightTimeout = null
let loadMoreTimeout = null
let typingUserTimeouts = new Map()

// Data
const topic = ref(null)
const replies = ref([])
const bestAnswer = ref(null)

// Categories for sidebar
const allCategories = ref([
  { id: 1, name: 'Genel Tartisma', icon: MessageSquareIcon, topics: 156, color: '#f97316' },
  { id: 2, name: 'Sorular & Cevaplar', icon: HelpCircleIcon, topics: 89, color: '#8b5cf6' },
  { id: 3, name: 'Duyurular', icon: ZapIcon, topics: 12, color: '#22c55e' },
  { id: 4, name: 'Kurallar', icon: ShieldIcon, topics: 5, color: '#ef4444' }
])

const sidebarStats = computed(() => ({
  totalTopics: 262,
  totalPosts: replies.value.length + 1,
  totalMembers: 1250
}))

// Sort options
const sortOptions = [
  { label: 'En Eski', value: 'oldest' },
  { label: 'En Yeni', value: 'newest' },
  { label: 'En Cok Begenilen', value: 'likes' }
]

// Editor tools
const editorTools = [
  { action: 'bold', icon: BoldIcon, label: 'Kalin' },
  { action: 'italic', icon: ItalicIcon, label: 'Italik' },
  { action: 'code', icon: CodeIcon, label: 'Kod' },
  { action: 'quote', icon: QuoteIcon, label: 'Alinti' },
  { action: 'list', icon: ListIcon, label: 'Liste' },
  { action: 'link', icon: LinkIcon, label: 'Link' },
  { action: 'image', icon: ImageIcon, label: 'Resim' }
]

// Report reasons
const reportReasons = [
  { label: 'Spam veya reklam', value: 'spam' },
  { label: 'Hakaret veya kufur', value: 'abuse' },
  { label: 'Yaniltici bilgi', value: 'misleading' },
  { label: 'Telif hakki ihlali', value: 'copyright' },
  { label: 'Diger', value: 'other' }
]

const reportForm = ref({ reason: null, description: '' })

// Social share
const socialShareOptions = [
  { name: 'Twitter', icon: TwitterIcon, color: '#1DA1F2' },
  { name: 'Facebook', icon: FacebookIcon, color: '#4267B2' },
  { name: 'LinkedIn', icon: LinkedinIcon, color: '#0077B5' },
  { name: 'E-posta', icon: MailIcon, color: '#EA4335' }
]

// Computed
const allSortedReplies = computed(() => {
  const sorted = [...replies.value]
  switch (sortOrder.value) {
    case 'newest': return sorted.reverse()
    case 'likes': return sorted.sort((a, b) => b.likes - a.likes)
    default: return sorted
  }
})

const sortedReplies = computed(() => allSortedReplies.value.slice(0, displayedRepliesCount.value))
const canLoadMoreReplies = computed(() => displayedRepliesCount.value < allSortedReplies.value.length)

const previewContent = computed(() => renderMarkdown(newReply.value || '*Onizleme icin bir seyler yazin...*'))
const shareUrl = computed(() => `${window.location.origin}/forum/topic/${topicId.value}`)
const isReplyValid = computed(() => newReply.value.trim().length >= 5)

// Methods
function renderMarkdown(content) {
  if (!content) return ''
  try {
    return DOMPurify.sanitize(marked(content, { breaks: true, gfm: true }))
  } catch (e) {
    return content
  }
}

function formatPostForCard(post) {
  if (!post) return null

  // Handle author as object or string
  const authorObj = typeof post.author === 'object' ? post.author : null
  const authorName = authorObj ? authorObj.username : post.author
  const authorAvatar = authorObj ? authorObj.avatar : post.authorAvatar
  const authorRole = authorObj ? authorObj.role : post.authorRole
  const authorLevel = authorObj ? authorObj.level : post.authorLevel
  const authorPostCount = authorObj ? authorObj.post_count : post.authorPosts
  const authorJoinedDate = authorObj?.joined_at
    ? new Date(authorObj.joined_at).toLocaleDateString('tr-TR', { month: 'short', year: 'numeric' })
    : post.authorJoined

  return {
    id: post.id,
    content: post.content,
    htmlContent: renderMarkdown(post.content),
    author: authorName || 'Anonim',
    authorAvatar: authorAvatar,
    authorRole: authorRole || 'Uye',
    authorLevel: authorLevel || 1,
    authorXp: post.authorXp || 0,
    authorXpProgress: post.authorXpProgress || 50,
    authorPosts: authorPostCount || 0,
    authorJoined: authorJoinedDate || 'Bilinmiyor',
    authorOnline: post.authorOnline || false,
    authorBadges: post.authorBadges || [],
    created: post.created || formatDate(post.created_at),
    likes: post.likes || 0,
    hasLiked: hasLikedTopic.value,
    isEdited: post.isEdited || post.is_edited,
    isBestAnswer: post.isBestAnswer || post.is_best_answer
  }
}

// Format date helper
function formatDate(dateStr) {
  if (!dateStr) return 'Bilinmiyor'
  try {
    return new Date(dateStr).toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

function formatReplyForCard(reply, index) {
  // Handle author as object or string
  const authorObj = typeof reply.author === 'object' ? reply.author : null
  const authorName = authorObj ? authorObj.username : reply.author
  const authorAvatar = authorObj ? authorObj.avatar : reply.authorAvatar
  const authorRole = authorObj ? authorObj.role : reply.authorRole
  const authorLevel = authorObj ? authorObj.level : reply.authorLevel
  const authorPostCount = authorObj ? authorObj.post_count : reply.authorPosts
  const authorJoinedDate = authorObj?.joined_at
    ? new Date(authorObj.joined_at).toLocaleDateString('tr-TR', { month: 'short', year: 'numeric' })
    : reply.authorJoined

  return {
    id: reply.id,
    content: reply.content,
    htmlContent: renderMarkdown(reply.content),
    author: authorName || 'Anonim',
    authorAvatar: authorAvatar,
    authorRole: authorRole || 'Uye',
    authorLevel: authorLevel || 1,
    authorXp: reply.authorXp || 0,
    authorXpProgress: reply.authorXpProgress || 50,
    authorPosts: authorPostCount || 0,
    authorJoined: authorJoinedDate || 'Bilinmiyor',
    authorOnline: reply.authorOnline || false,
    authorBadges: reply.authorBadges || [],
    created: reply.created || formatDate(reply.created_at),
    likes: reply.likes || 0,
    hasLiked: reply.hasLiked || false,
    isEdited: reply.isEdited || reply.is_edited,
    isBestAnswer: reply.isBestAnswer || reply.is_best_answer,
    replyNumber: index + 1
  }
}

function handleCategoryClick(cat) {
  router.push(`/forum/category/${cat.id}`)
}

async function likeTopic() {
  if (!requireAuth({ message: 'Begenmek icin giris yapmaniz gerekiyor', redirect: false })) return
  // BUGFIX: Add null check for topic
  if (!topic.value || topic.value.likes === undefined) return

  const wasLiked = hasLikedTopic.value
  // Optimistic update
  hasLikedTopic.value = !hasLikedTopic.value
  topic.value.likes += hasLikedTopic.value ? 1 : -1

  try {
    const response = await fetch(`/api/forum/topics/${getTopicId()}/like`, {
      method: wasLiked ? 'DELETE' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (!response.ok) {
      // Revert on error
      hasLikedTopic.value = wasLiked
      topic.value.likes += wasLiked ? 1 : -1
      window.$message?.error('Begeni islemi basarisiz')
    } else {
      window.$message?.success(hasLikedTopic.value ? 'Begenildi' : 'Begeni kaldirildi')
    }
  } catch (error) {
    // Revert on error
    hasLikedTopic.value = wasLiked
    topic.value.likes += wasLiked ? 1 : -1
    console.error('Like error:', error)
  }
}

async function likeReply(replyId) {
  if (!requireAuth({ message: 'Begenmek icin giris yapmaniz gerekiyor', redirect: false })) return
  const reply = replies.value.find(r => r.id === replyId)
  // BUGFIX: Add null check for reply and likes
  if (!reply || reply.likes === undefined) return

  const wasLiked = reply.hasLiked
  // Optimistic update
  reply.hasLiked = !reply.hasLiked
  reply.likes += reply.hasLiked ? 1 : -1

  try {
    const response = await fetch(`/api/forum/replies/${replyId}/like`, {
      method: wasLiked ? 'DELETE' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (!response.ok) {
      // Revert on error
      reply.hasLiked = wasLiked
      reply.likes += wasLiked ? 1 : -1
      window.$message?.error('Begeni islemi basarisiz')
    } else {
      window.$message?.success(reply.hasLiked ? 'Begenildi' : 'Begeni kaldirildi')
    }
  } catch (error) {
    // Revert on error
    reply.hasLiked = wasLiked
    reply.likes += wasLiked ? 1 : -1
    console.error('Like reply error:', error)
  }
}

// Bookmark topic
const isBookmarked = ref(false)
async function bookmarkTopic() {
  if (!requireAuth({ message: 'Yer imi eklemek icin giris yapmaniz gerekiyor', redirect: false })) return

  const wasBookmarked = isBookmarked.value
  isBookmarked.value = !isBookmarked.value

  try {
    const response = await fetch(`/api/forum/topics/${getTopicId()}/bookmark`, {
      method: wasBookmarked ? 'DELETE' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (!response.ok) {
      isBookmarked.value = wasBookmarked
      window.$message?.error('Yer imi islemi basarisiz')
    } else {
      window.$message?.success(isBookmarked.value ? 'Yer imine eklendi' : 'Yer iminden cikarildi')
    }
  } catch (error) {
    isBookmarked.value = wasBookmarked
    console.error('Bookmark error:', error)
  }
}

// Subscribe to topic
const isTopicSubscribed = ref(false)
async function subscribeToTopic() {
  if (!requireAuth({ message: 'Takip etmek icin giris yapmaniz gerekiyor', redirect: false })) return

  const wasSubscribed = isTopicSubscribed.value
  isTopicSubscribed.value = !isTopicSubscribed.value

  try {
    const response = await fetch(`/api/forum/topics/${getTopicId()}/subscribe`, {
      method: wasSubscribed ? 'DELETE' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (!response.ok) {
      isTopicSubscribed.value = wasSubscribed
      window.$message?.error('Takip islemi basarisiz')
    } else {
      window.$message?.success(isTopicSubscribed.value ? 'Konu takip ediliyor' : 'Takip iptal edildi')
    }
  } catch (error) {
    isTopicSubscribed.value = wasSubscribed
    console.error('Subscribe error:', error)
  }
}

// Mark best answer
async function markBestAnswer(replyId) {
  if (!isLoggedIn.value) {
    window.$message?.warning('Bu islemi yapmak icin giris yapin')
    return
  }

  // Only topic author can mark best answer
  if (topic.value?.author !== authStore.user?.username && !authStore.user?.is_admin) {
    window.$message?.warning('Sadece konu sahibi en iyi yaniti isaretleyebilir')
    return
  }

  try {
    const response = await fetch(`/api/forum/replies/${replyId}/best`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (response.ok) {
      // Update local state
      replies.value.forEach(r => {
        r.isBestAnswer = r.id === replyId
      })
      const bestReply = replies.value.find(r => r.id === replyId)
      bestAnswer.value = bestReply
      topic.value.isSolved = true
      window.$message?.success('En iyi yanit isaretlendi')
    } else {
      window.$message?.error('Islem basarisiz')
    }
  } catch (error) {
    console.error('Mark best answer error:', error)
    window.$message?.error('Bir hata olustu')
  }
}

// Pin/unpin topic (admin only)
async function togglePinTopic() {
  if (!isAdmin.value) return

  const wasPinned = topic.value?.isPinned
  topic.value.isPinned = !topic.value.isPinned

  try {
    const response = await fetch(`/api/forum/topics/${getTopicId()}/pin`, {
      method: wasPinned ? 'DELETE' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (!response.ok) {
      topic.value.isPinned = wasPinned
      window.$message?.error('Sabitleme islemi basarisiz')
    } else {
      window.$message?.success(topic.value.isPinned ? 'Konu sabitlendi' : 'Sabitleme kaldirildi')
    }
  } catch (error) {
    topic.value.isPinned = wasPinned
    console.error('Pin error:', error)
  }
}

// Lock/unlock topic (admin only)
async function toggleLockTopic() {
  if (!isAdmin.value) return

  const wasLocked = topic.value?.isLocked
  topic.value.isLocked = !topic.value.isLocked

  try {
    const response = await fetch(`/api/forum/topics/${getTopicId()}/lock`, {
      method: wasLocked ? 'DELETE' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (!response.ok) {
      topic.value.isLocked = wasLocked
      window.$message?.error('Kilitleme islemi basarisiz')
    } else {
      window.$message?.success(topic.value.isLocked ? 'Konu kilitlendi' : 'Kilit kaldirildi')
    }
  } catch (error) {
    topic.value.isLocked = wasLocked
    console.error('Lock error:', error)
  }
}

// Delete topic (admin or owner)
async function deleteTopic() {
  const canDelete = isAdmin.value || topic.value?.author === authStore.user?.username

  if (!canDelete) {
    window.$message?.warning('Bu konuyu silme yetkiniz yok')
    return
  }

  if (!window.confirm('Bu konuyu silmek istediginizden emin misiniz?')) {
    return
  }

  try {
    const response = await fetch(`/api/forum/topics/${getTopicId()}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (response.ok) {
      window.$message?.success('Konu silindi')
      router.push('/forum')
    } else {
      window.$message?.error('Konu silinemedi')
    }
  } catch (error) {
    console.error('Delete topic error:', error)
    window.$message?.error('Bir hata olustu')
  }
}

// Delete reply
async function deleteReply(replyId) {
  const reply = replies.value.find(r => r.id === replyId)
  const canDelete = isAdmin.value || reply?.author === authStore.user?.username

  if (!canDelete) {
    window.$message?.warning('Bu yaniti silme yetkiniz yok')
    return
  }

  if (!window.confirm('Bu yaniti silmek istediginizden emin misiniz?')) {
    return
  }

  try {
    const response = await fetch(`/api/forum/replies/${replyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      }
    })

    if (response.ok) {
      replies.value = replies.value.filter(r => r.id !== replyId)
      window.$message?.success('Yanit silindi')
    } else {
      window.$message?.error('Yanit silinemedi')
    }
  } catch (error) {
    console.error('Delete reply error:', error)
    window.$message?.error('Bir hata olustu')
  }
}

function quotePost(post) {
  quotedReply.value = post
  const quoteText = `> @${post.author} yazdi:\n> ${post.content.replace(/\n/g, '\n> ')}\n\n`
  newReply.value = quoteText + newReply.value
  scrollToReplyForm()
}

function quoteReply(reply) {
  quotedReply.value = reply
  const quoteText = `> @${reply.author} yazdi:\n> ${reply.content.replace(/\n/g, '\n> ')}\n\n`
  newReply.value = quoteText + newReply.value
  scrollToReplyForm()
}

function replyToUser(reply) {
  newReply.value = `@${reply.author} ` + newReply.value
  scrollToReplyForm()
}

function clearQuote() {
  quotedReply.value = null
}

function scrollToReply(replyId) {
  // Ensure the reply is in view by checking if we need to load more
  const replyIndex = allSortedReplies.value.findIndex(r => r.id === replyId)
  if (replyIndex >= displayedRepliesCount.value) {
    // Need to load more replies to show this one
    displayedRepliesCount.value = replyIndex + 1
  }

  // Use nextTick to ensure DOM is updated before scrolling
  nextTick(() => {
    const element = document.getElementById(`reply-${replyId}`)
    if (element) {
      highlightedReplyId.value = replyId
      // Use scrollIntoView with offset for better positioning
      const headerOffset = 80
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      })

      // Focus the element for accessibility
      element.setAttribute('tabindex', '-1')
      element.focus({ preventScroll: true })

      // Clear any existing highlight timeout before setting a new one
      if (highlightTimeout) {
        clearTimeout(highlightTimeout)
      }
      highlightTimeout = setTimeout(() => {
        highlightedReplyId.value = null
        highlightTimeout = null
        element.removeAttribute('tabindex')
      }, 2000)
    }
  })
}

function scrollToReplyForm() {
  nextTick(() => {
    const element = document.getElementById('reply-form')
    if (element) {
      const headerOffset = 80
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      })

      // Focus the editor after scroll completes
      setTimeout(() => {
        editorRef.value?.focus()
      }, 500)
    }
  })
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
  // Focus the topic header for accessibility
  nextTick(() => {
    const header = document.querySelector('.forum-topic-header h1')
    if (header) {
      header.setAttribute('tabindex', '-1')
      header.focus({ preventScroll: true })
    }
  })
}

function loadMoreReplies() {
  isLoadingMoreReplies.value = true
  // Clear any existing load more timeout
  if (loadMoreTimeout) {
    clearTimeout(loadMoreTimeout)
  }
  loadMoreTimeout = setTimeout(() => {
    displayedRepliesCount.value += REPLIES_PER_PAGE
    isLoadingMoreReplies.value = false
    loadMoreTimeout = null
  }, 500)
}

function applyFormat(action) {
  const formats = {
    bold: { prefix: '**', suffix: '**' },
    italic: { prefix: '*', suffix: '*' },
    code: { prefix: '`', suffix: '`' },
    codeblock: { prefix: '```\n', suffix: '\n```' },
    quote: { prefix: '> ', suffix: '' },
    list: { prefix: '- ', suffix: '' },
    link: { prefix: '[', suffix: '](url)' },
    image: { prefix: '![alt](', suffix: ')' },
    heading: { prefix: '## ', suffix: '' },
    hr: { prefix: '\n---\n', suffix: '' }
  }
  const format = formats[action]
  if (format) {
    newReply.value += `${format.prefix}text${format.suffix}`
  }
}

// Mention suggestions
const mentionSuggestions = ref([])
const showMentionDropdown = ref(false)
const mentionQuery = ref('')
const mentionDropdownPosition = ref({ top: 0, left: 0 })

async function handleMentionInput(e) {
  const text = newReply.value
  const cursorPos = e.target?.selectionStart || text.length
  const textBefore = text.substring(0, cursorPos)

  // Find @ pattern
  const mentionMatch = textBefore.match(/@(\w*)$/)

  if (mentionMatch) {
    mentionQuery.value = mentionMatch[1]

    // Fetch mention suggestions
    if (mentionQuery.value.length >= 1) {
      try {
        const response = await fetch(`/api/forum/mentions/search?q=${mentionQuery.value}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        if (response.ok) {
          const data = await response.json()
          mentionSuggestions.value = data.users || []
          showMentionDropdown.value = mentionSuggestions.value.length > 0
        }
      } catch (error) {
        console.error('Mention search error:', error)
      }
    } else {
      // Show recent users from replies
      const uniqueAuthors = [...new Set(replies.value.map(r => r.author))].slice(0, 5)
      mentionSuggestions.value = uniqueAuthors.map(a => ({ username: a }))
      showMentionDropdown.value = mentionSuggestions.value.length > 0
    }
  } else {
    showMentionDropdown.value = false
  }
}

function selectMention(user) {
  const text = newReply.value
  const cursorPos = document.activeElement?.selectionStart || text.length
  const textBefore = text.substring(0, cursorPos)
  const textAfter = text.substring(cursorPos)

  // Replace @query with @username
  const newTextBefore = textBefore.replace(/@\w*$/, `@${user.username} `)
  newReply.value = newTextBefore + textAfter
  showMentionDropdown.value = false
}

function handleTyping() {
  if (forumWS && hasSteam.value) {
    forumWS.sendTyping()
  }
}

function validateReply() {
  const trimmedReply = newReply.value.trim()
  if (trimmedReply.length === 0) {
    replyValidation.status = undefined
    replyValidation.message = ''
  } else if (trimmedReply.length < 5) {
    replyValidation.status = 'error'
    replyValidation.message = 'Yanıt en az 5 karakter olmalıdır'
  } else {
    replyValidation.status = 'success'
    replyValidation.message = ''
  }
}

function saveDraft() {
  localStorage.setItem(`forum_draft_${topicId.value}`, newReply.value)
  window.$message?.success('Taslak kaydedildi')
}

async function submitReply() {
  if (!requireSteam(() => {})) return
  if (!newReply.value.trim()) return

  isSubmitting.value = true
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`
    }
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      headers['X-CSRF-Token'] = csrfToken
    }

    const response = await fetch(`/api/forum/topics/${getTopicId()}/replies`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        content: newReply.value.trim(),
        quoted_reply_id: quotedReply.value?.id
      })
    })

    if (response.ok) {
      let data = null
      try {
        data = await response.json()
      } catch (jsonError) {
        // Response body may be empty on success
        console.warn('Response JSON parse warning:', jsonError)
      }
      newReply.value = ''
      quotedReply.value = null
      localStorage.removeItem(`forum_draft_${topicId.value}`)
      window.$message?.success('Yanıt gönderildi')
      fetchTopic()
    } else {
      let errorMessage = 'Yanıt gönderilemedi'
      try {
        const error = await response.json()
        errorMessage = error.detail || errorMessage
      } catch (jsonError) {
        // Could not parse error response
        console.warn('Error response JSON parse warning:', jsonError)
      }
      window.$message?.error(errorMessage)
    }
  } catch (error) {
    console.error('Submit reply error:', error)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      window.$message?.error('Ağ bağlantısı hatası, lütfen internet bağlantınızı kontrol edin')
    } else {
      window.$message?.error('Bir hata oluştu, lütfen tekrar deneyin')
    }
  } finally {
    isSubmitting.value = false
  }
}

// Current item being reported
const reportingItem = ref(null)

function reportTopic() {
  if (!requireAuth({ message: 'Bildirmek icin giris yapmaniz gerekiyor', redirect: false })) return
  reportingItem.value = { type: 'topic', id: topicId }
  showReportModal.value = true
}

function reportReply(reply) {
  if (!requireAuth({ message: 'Bildirmek icin giris yapmaniz gerekiyor', redirect: false })) return
  reportingItem.value = { type: 'reply', id: reply.id }
  showReportModal.value = true
}

async function submitReport() {
  if (!reportForm.value.reason) {
    window.$message?.warning('Lutfen bir neden secin')
    return
  }

  try {
    const endpoint = reportingItem.value?.type === 'topic'
      ? `/api/forum/topics/${getTopicId()}/report`
      : `/api/forum/replies/${reportingItem.value?.id}/report`

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      },
      body: JSON.stringify({
        reason: reportForm.value.reason,
        description: reportForm.value.description
      })
    })

    if (response.ok) {
      window.$message?.success('Bildiriminiz alindi')
    } else {
      window.$message?.error('Bildirim gonderilemedi')
    }
  } catch (error) {
    console.error('Report error:', error)
    window.$message?.error('Bir hata olustu')
  } finally {
    showReportModal.value = false
    reportForm.value = { reason: null, description: '' }
    reportingItem.value = null
  }
}

// Edit topic
const showEditTopicModal = ref(false)
const editTopicForm = ref({ title: '', content: '' })

function openEditTopic() {
  if (!topic.value) return
  if (topic.value.author !== authStore.user?.username && !isAdmin.value) {
    window.$message?.warning('Bu konuyu duzenleme yetkiniz yok')
    return
  }
  editTopicForm.value = {
    title: topic.value.title || '',
    content: topic.value.content || ''
  }
  showEditTopicModal.value = true
}

async function saveEditTopic() {
  if (editTopicForm.value.title.trim().length < 5) {
    window.$message?.warning('Baslik en az 5 karakter olmalidir')
    return
  }
  if (editTopicForm.value.content.trim().length < 20) {
    window.$message?.warning('Icerik en az 20 karakter olmalidir')
    return
  }

  try {
    const response = await fetch(`/api/forum/topics/${getTopicId()}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      },
      body: JSON.stringify({
        title: editTopicForm.value.title.trim(),
        content: editTopicForm.value.content.trim()
      })
    })

    if (response.ok) {
      topic.value.title = editTopicForm.value.title.trim()
      topic.value.content = editTopicForm.value.content.trim()
      topic.value.isEdited = true
      showEditTopicModal.value = false
      window.$message?.success('Konu guncellendi')
    } else {
      window.$message?.error('Konu guncellenemedi')
    }
  } catch (error) {
    console.error('Edit topic error:', error)
    window.$message?.error('Bir hata olustu')
  }
}

// Edit reply
const editingReplyId = ref(null)
const editReplyContent = ref('')
const showEditReplyModal = ref(false)

function startEditReply(reply) {
  if (reply.author !== authStore.user?.username && !isAdmin.value) {
    window.$message?.warning('Bu yaniti duzenleme yetkiniz yok')
    return
  }
  editingReplyId.value = reply.id
  editReplyContent.value = reply.content
  showEditReplyModal.value = true
}

function cancelEditReply() {
  editingReplyId.value = null
  editReplyContent.value = ''
  showEditReplyModal.value = false
}

async function saveEditReply(replyId) {
  if (editReplyContent.value.trim().length < 5) {
    window.$message?.warning('Yanit en az 5 karakter olmalidir')
    return
  }

  try {
    const response = await fetch(`/api/forum/replies/${replyId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken() || ''
      },
      body: JSON.stringify({
        content: editReplyContent.value.trim()
      })
    })

    if (response.ok) {
      const reply = replies.value.find(r => r.id === replyId)
      if (reply) {
        reply.content = editReplyContent.value.trim()
        reply.isEdited = true
      }
      editingReplyId.value = null
      editReplyContent.value = ''
      showEditReplyModal.value = false
      window.$message?.success('Yanit guncellendi')
    } else {
      window.$message?.error('Yanit guncellenemedi')
    }
  } catch (error) {
    console.error('Edit reply error:', error)
    window.$message?.error('Bir hata olustu')
  }
}

// Handle topic card actions (edit, delete, copy-link)
function handleTopicAction({ action, post }) {
  switch (action) {
    case 'edit':
      openEditTopic()
      break
    case 'delete':
      deleteTopic()
      break
    case 'copy-link':
      navigator.clipboard.writeText(`${window.location.origin}/forum/topic/${getTopicId()}`)
      window.$message?.success('Link kopyalandi')
      break
  }
}

// Handle reply card actions (edit, delete, copy-link)
function handleReplyAction({ action, post }, reply) {
  switch (action) {
    case 'edit':
      startEditReply(reply)
      break
    case 'delete':
      deleteReply(reply.id)
      break
    case 'copy-link':
      navigator.clipboard.writeText(`${window.location.origin}/forum/topic/${getTopicId()}#reply-${reply.id}`)
      window.$message?.success('Link kopyalandi')
      break
  }
}

// Keyboard shortcuts
function handleKeydown(e) {
  // Don't trigger shortcuts when typing in inputs
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
    // Ctrl+Enter to submit reply
    if (e.ctrlKey && e.key === 'Enter' && newReply.value.trim().length >= 5) {
      e.preventDefault()
      submitReply()
    }
    return
  }

  // R - Focus reply form
  if (e.key === 'r' || e.key === 'R') {
    e.preventDefault()
    scrollToReplyForm()
  }

  // Q - Quote selected text or topic
  if (e.key === 'q' || e.key === 'Q') {
    e.preventDefault()
    if (topic.value) {
      quotePost(topic.value)
    }
  }

  // L - Like topic
  if (e.key === 'l' || e.key === 'L') {
    e.preventDefault()
    likeTopic()
  }

  // B - Bookmark topic
  if (e.key === 'b' || e.key === 'B') {
    e.preventDefault()
    bookmarkTopic()
  }

  // S - Share topic
  if (e.key === 's' || e.key === 'S') {
    e.preventDefault()
    showShareModal.value = true
  }

  // ? - Show shortcuts help
  if (e.key === '?') {
    e.preventDefault()
    window.$message?.info('Kisayollar: R=Yanit, Q=Alinti, L=Begen, B=Yerimine Ekle, S=Paylas')
  }

  // Escape - Close modals
  if (e.key === 'Escape') {
    showShareModal.value = false
    showReportModal.value = false
    showEditTopicModal.value = false
  }
}

function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value)
  window.$message?.success('Link kopyalandi')
}

function shareToSocial(social) {
  const urls = {
    Twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl.value)}&text=${encodeURIComponent(topic.value?.title)}`,
    Facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl.value)}`,
    LinkedIn: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl.value)}`,
    'E-posta': `mailto:?subject=${encodeURIComponent(topic.value?.title)}&body=${encodeURIComponent(shareUrl.value)}`
  }
  window.open(urls[social.name], '_blank')
}

// WebSocket
function initWebSocket() {
  forumWS = useForumTopicWS(topicId.value, {
    onNewReply: (reply) => {
      const exists = replies.value.find(r => r.id === reply.id)
      if (!exists) {
        replies.value.push({
          id: reply.id,
          content: reply.content,
          author: reply.author?.username || 'Unknown',
          authorAvatar: reply.author?.avatar,
          authorRole: 'Uye',
          authorLevel: 15,
          created: 'Az once',
          likes: 0,
          hasLiked: false
        })
        window.$message?.info(`${reply.author?.username || 'Birisi'} yeni bir yanit yazdi`)
      }
    },
    onUserTyping: (user) => {
      const idx = typingUsers.value.findIndex(u => u.id === user.id)
      if (idx === -1) typingUsers.value.push(user)
      // Clear any existing timeout for this user
      if (typingUserTimeouts.has(user.id)) {
        clearTimeout(typingUserTimeouts.get(user.id))
      }
      // Set a new timeout to remove typing indicator
      const timeoutId = setTimeout(() => {
        const removeIdx = typingUsers.value.findIndex(u => u.id === user.id)
        if (removeIdx !== -1) typingUsers.value.splice(removeIdx, 1)
        typingUserTimeouts.delete(user.id)
      }, 3000)
      typingUserTimeouts.set(user.id, timeoutId)
    },
    onViewersUpdate: (count, viewers) => {
      wsViewerCount.value = count
      wsViewers.value = viewers
    }
  })
}

// Fetch data - with race condition protection
let fetchTopicAbortController = null
async function fetchTopic() {
  // Cancel any pending fetch request
  if (fetchTopicAbortController) {
    fetchTopicAbortController.abort()
  }
  fetchTopicAbortController = new AbortController()

  isLoading.value = true
  fetchError.value = null

  try {
    const response = await fetch(`/api/forum/topics/${topicId.value}`, {
      signal: fetchTopicAbortController.signal
    })

    if (response.ok) {
      const data = await response.json()
      topic.value = data.topic
      replies.value = data.replies || []
      bestAnswer.value = data.bestAnswer || null
      // Set like status from API response
      hasLikedTopic.value = data.topic?.hasLiked || false
    } else if (response.status === 404) {
      fetchError.value = 'Konu bulunamadi'
      window.$message?.error('Konu bulunamadi')
    } else if (response.status === 403) {
      fetchError.value = 'Bu konuyu goruntuleme yetkiniz yok'
      window.$message?.error('Bu konuyu goruntuleme yetkiniz yok')
    } else {
      fetchError.value = 'Konu yuklenemedi'
      window.$message?.error('Konu yuklenemedi')
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      // Request was cancelled, ignore
      return
    }
    console.error('Failed to fetch topic:', error)
    fetchError.value = 'Konu yuklenirken bir hata olustu'
    if (error instanceof TypeError && error.message.includes('fetch')) {
      window.$message?.error('Ag baglantisi hatasi')
    }
  } finally {
    isLoading.value = false
    fetchTopicAbortController = null
  }
}

// Scroll handler
function handleScroll() {
  showFloatingBar.value = window.scrollY > 400
}

// Load draft
function loadDraft() {
  const draft = localStorage.getItem(`forum_draft_${topicId.value}`)
  if (draft) {
    newReply.value = draft
  }
}

// Draft auto-save
let draftAutoSaveTimer = null
function startDraftAutoSave() {
  if (draftAutoSaveTimer) clearInterval(draftAutoSaveTimer)
  draftAutoSaveTimer = setInterval(() => {
    if (newReply.value.trim()) {
      localStorage.setItem(`forum_draft_${topicId.value}`, newReply.value)
    }
  }, 10000) // Save every 10 seconds
}

function stopDraftAutoSave() {
  if (draftAutoSaveTimer) {
    clearInterval(draftAutoSaveTimer)
    draftAutoSaveTimer = null
  }
}

// Lifecycle
onMounted(() => {
  fetchTopic()
  initWebSocket()
  loadDraft()
  startDraftAutoSave()
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (forumWS) forumWS.disconnect?.()
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('keydown', handleKeydown)
  stopDraftAutoSave()

  // Save draft on unmount
  if (newReply.value.trim()) {
    localStorage.setItem(`forum_draft_${topicId.value}`, newReply.value)
  }

  // Clean up all timeouts
  if (highlightTimeout) {
    clearTimeout(highlightTimeout)
    highlightTimeout = null
  }
  if (loadMoreTimeout) {
    clearTimeout(loadMoreTimeout)
    loadMoreTimeout = null
  }
  // Clear all typing user timeouts
  typingUserTimeouts.forEach((timeoutId) => {
    clearTimeout(timeoutId)
  })
  typingUserTimeouts.clear()
})
</script>

<style scoped>
/* ===== Visual Enhancement ===== */
.forum-page {
  position: relative;
}

.forum-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139, 92, 246, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 100% 50%, rgba(249, 115, 22, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse 50% 30% at 0% 80%, rgba(34, 211, 238, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* Topic Header */
.forum-topic-header {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(11, 15, 20, 0.98) 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: var(--forum-radius-lg);
  padding: 32px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.1);
  transition: all 0.3s ease;
}

.forum-topic-header:hover {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.15);
}

.forum-topic-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--forum-brand), var(--forum-accent), var(--forum-purple));
  animation: gradient-flow 4s ease infinite;
  background-size: 200% 100%;
}

@keyframes gradient-flow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.forum-topic-header::after {
  content: '';
  position: absolute;
  top: 4px;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.forum-topic-header__badges {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.forum-topic-header__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.forum-stat-pill--live {
  background: rgba(34, 197, 94, 0.1);
  color: var(--forum-success);
}

.forum-live-dot {
  width: 8px;
  height: 8px;
  background: var(--forum-success);
  border-radius: 50%;
  animation: forum-pulse 2s ease-in-out infinite;
}

@keyframes forum-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Replies Section */
.forum-replies-section {
  margin-bottom: 24px;
}

.forum-replies-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.forum-replies-header .forum-heading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.forum-replies-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.forum-reply--highlighted {
  animation: forum-highlight 2s ease;
}

@keyframes forum-highlight {
  0%, 100% { box-shadow: none; }
  50% { box-shadow: 0 0 0 3px var(--forum-accent); }
}

/* Load More */
.forum-load-more {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.forum-load-more__btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 15, 20, 0.95) 100%);
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-radius: var(--forum-radius);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.forum-load-more__btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.1), transparent);
  transition: left 0.5s ease;
}

.forum-load-more__btn:hover:not(:disabled) {
  border-color: rgba(34, 211, 238, 0.6);
  color: var(--forum-accent);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(34, 211, 238, 0.15);
}

.forum-load-more__btn:hover:not(:disabled)::before {
  left: 100%;
}

.forum-load-more__btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Typing Indicator */
.forum-typing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-radius: var(--forum-radius);
  margin-bottom: 16px;
  animation: typing-glow 2s ease-in-out infinite;
}

@keyframes typing-glow {
  0%, 100% { box-shadow: 0 0 0 rgba(34, 211, 238, 0); }
  50% { box-shadow: 0 0 20px rgba(34, 211, 238, 0.2); }
}

.forum-typing-dots {
  display: flex;
  gap: 4px;
}

.forum-typing-dots span {
  width: 6px;
  height: 6px;
  background: var(--forum-accent);
  border-radius: 50%;
  animation: forum-typing 1.4s infinite;
}

.forum-typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.forum-typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes forum-typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* Reply Form */
.forum-reply-form {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(11, 15, 20, 0.98) 100%);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: var(--forum-radius-lg);
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.forum-reply-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f97316, #22d3ee);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.forum-reply-form:focus-within {
  border-color: rgba(249, 115, 22, 0.5);
  box-shadow: 0 8px 32px rgba(249, 115, 22, 0.1);
}

.forum-reply-form:focus-within::before {
  opacity: 1;
}

.forum-steam-notice {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: rgba(102, 192, 244, 0.1);
  border-bottom: 1px solid var(--forum-border);
}

.forum-steam-notice__icon {
  color: #66c0f4;
}

.forum-steam-notice__content {
  flex: 1;
}

.forum-steam-notice__content p {
  color: var(--text-primary);
  margin: 0;
}

.forum-quote-preview {
  position: relative;
  padding: 16px 24px;
  background: var(--forum-bg-hover);
  border-bottom: 1px solid var(--forum-border);
}

.forum-quote-preview__header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--forum-muted);
  margin-bottom: 8px;
}

.forum-quote-preview__content {
  color: var(--text-primary);
  font-size: 14px;
  padding-left: 12px;
  border-left: 3px solid var(--forum-accent);
}

.forum-quote-preview__close {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 4px;
  color: var(--forum-muted);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.forum-quote-preview__close:hover {
  background: var(--forum-bg-card);
  color: var(--text-primary);
}

.forum-reply-form__content {
  padding: 24px;
}

.forum-reply-form__content .forum-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

/* Editor Toolbar */
.forum-editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--forum-bg-hover);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius-sm) var(--forum-radius-sm) 0 0;
}

.forum-editor-toolbar__btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 6px;
  color: var(--forum-muted);
  transition: all 0.2s ease;
}

.forum-editor-toolbar__btn:hover,
.forum-editor-toolbar__btn.active {
  background: var(--forum-bg-card);
  color: var(--forum-accent);
}

.forum-editor-toolbar__divider {
  width: 1px;
  height: 24px;
  background: var(--forum-border);
  margin: 0 8px;
}

/* Editor */
.forum-editor {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.forum-editor__input {
  flex: 1;
}

.forum-reply-validation-error {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

.forum-editor--split .forum-editor__input {
  flex: 1;
}

.forum-editor__preview {
  flex: 1;
  padding: 16px;
  background: var(--forum-bg-hover);
  border: 1px solid var(--forum-border);
  border-radius: 0 0 var(--forum-radius-sm) var(--forum-radius-sm);
  max-height: 300px;
  overflow-y: auto;
}

.forum-editor__preview .forum-meta {
  margin-bottom: 12px;
}

/* Form Footer */
.forum-reply-form__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forum-reply-form__counter {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--forum-muted);
  font-size: 14px;
}

.forum-reply-form__actions {
  display: flex;
  gap: 12px;
}

/* Locked Message */
.forum-locked-message {
  text-align: center;
  padding: 60px 24px;
  background: var(--forum-bg-card);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius-lg);
  color: var(--forum-danger);
}

.forum-locked-message .forum-heading {
  margin: 24px 0 12px;
}

/* Floating Bar */
.forum-floating-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--forum-bg-panel);
  border: 1px solid var(--forum-border);
  border-radius: 50px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 100;
}

.forum-floating-bar__btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 20px;
  color: var(--forum-muted);
  transition: all 0.2s ease;
}

.forum-floating-bar__btn:hover {
  background: var(--forum-bg-hover);
  color: var(--text-primary);
}

.forum-floating-bar__btn.liked {
  color: var(--forum-danger);
}

.forum-floating-bar__divider {
  width: 1px;
  height: 24px;
  background: var(--forum-border);
}

/* Share Modal */
.forum-share-modal__url {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.forum-share-modal__social {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.forum-share-modal__social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: var(--forum-bg-hover);
  border: 1px solid var(--forum-border);
  border-radius: var(--forum-radius-sm);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.forum-share-modal__social-btn:hover {
  background: var(--color);
  color: white;
}

/* Report Option */
.forum-report-option {
  padding: 8px 0;
}

/* Modal Footer */
.forum-modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Loading Dots */
.forum-loading-dots {
  display: flex;
  gap: 4px;
}

.forum-loading-dots span {
  width: 6px;
  height: 6px;
  background: var(--forum-muted);
  border-radius: 50%;
  animation: forum-loading 1s infinite;
}

.forum-loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.forum-loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes forum-loading {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateX(-50%) translateY(100px);
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .forum-topic-header {
    padding: 24px;
  }

  .forum-floating-bar {
    bottom: 16px;
    padding: 8px 16px;
  }

  .forum-editor {
    flex-direction: column;
  }

  .forum-reply-form__footer {
    flex-direction: column;
    gap: 16px;
  }

  .forum-reply-form__counter,
  .forum-reply-form__actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
