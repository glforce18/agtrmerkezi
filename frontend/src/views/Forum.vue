<template>
  <div class="forum-page min-h-screen relative overflow-hidden">
    <!-- Maintenance Check -->
    <MaintenanceOverlay feature="forum" />

    <!-- Subtle Background -->
    <div class="subtle-bg"></div>

    <!-- Compact Header -->
    <div class="relative z-10 py-3 border-b border-white/10">
      <div class="container-custom">
        <div class="flex flex-col md:flex-row md:items-center gap-3">
          <div class="flex items-center justify-between">
            <h1 class="text-lg font-bold flex items-center gap-2">
              <MessageSquareIcon class="w-5 h-5 text-orange-500" />
              Forum
              <span class="text-xs text-green-500 font-normal">({{ stats.onlineUsers }} online)</span>
            </h1>
          </div>
          <div class="flex-1 max-w-md">
            <div class="relative">
              <SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                v-model="searchQuery"
                type="text"
                class="w-full pl-9 pr-3 py-2 text-sm bg-white/5 border border-white/10 rounded-lg placeholder-gray-500 outline-none focus:border-orange-500"
                style="color: var(--text-primary)"
                placeholder="Ara..."
                @focus="showSearchResults = true"
                @blur="hideSearchResults"
                @input="performSearch"
              />
            </div>
          </div>
          <div class="flex gap-2 overflow-x-auto pb-1">
            <button
              v-for="filter in categoryFilters.slice(0,4)"
              :key="filter.id"
              :class="[
                'text-xs px-3 py-1.5 rounded-full whitespace-nowrap transition-all',
                activeFilter === filter.id ? 'bg-orange-500 text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'
              ]"
              @click="setFilter(filter.id)"
            >
              {{ filter.name }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content container-custom py-4 relative z-10">
      <div class="grid lg:grid-cols-3 gap-4">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Action Bar -->
          <div class="action-bar glass-card rounded-2xl p-4 flex flex-col md:flex-row gap-4 items-center justify-between animate-slideUp">
            <div class="flex items-center gap-4">
              <n-tooltip :disabled="isLoggedIn" trigger="hover">
                <template #trigger>
                  <n-button
                    type="primary"
                    class="new-topic-btn"
                    :class="{ 'btn-disabled': !isLoggedIn }"
                    @click="handleNewTopic"
                  >
                    <template #icon>
                      <LockIcon v-if="!isLoggedIn || !hasSteam" class="w-5 h-5" />
                      <PlusCircleIcon v-else class="w-5 h-5" />
                    </template>
                    <span v-if="!isLoggedIn">Giris Yap</span>
                    <span v-else-if="!hasSteam">Steam Gerekli</span>
                    <span v-else>Yeni Konu Olustur</span>
                  </n-button>
                </template>
                Konu olusturmak icin giris yapin
              </n-tooltip>
              <div class="hidden md:flex items-center gap-2 text-sm text-gray-500">
                <kbd class="kbd-sm">N</kbd> ile hızlı oluştur
              </div>
            </div>
            <div class="flex items-center gap-3">
              <n-select
                v-model:value="sortBy"
                :options="sortOptions"
                placeholder="Sırala"
                class="w-40"
              />
              <button class="view-toggle p-2 rounded-lg glass-button" @click="toggleView">
                <LayoutGridIcon v-if="viewMode === 'list'" class="w-5 h-5" />
                <LayoutListIcon v-else class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading" class="space-y-4">
            <div v-for="n in 3" :key="n" class="skeleton-card glass-card rounded-2xl p-6">
              <div class="flex items-start gap-4">
                <div class="skeleton-box w-16 h-16 rounded-xl"></div>
                <div class="flex-1 space-y-3">
                  <div class="skeleton-line w-3/4 h-6"></div>
                  <div class="skeleton-line w-1/2 h-4"></div>
                  <div class="flex gap-4">
                    <div class="skeleton-line w-20 h-4"></div>
                    <div class="skeleton-line w-20 h-4"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="filteredCategories.length === 0" class="empty-state glass-card rounded-2xl p-12 text-center">
            <div class="empty-illustration mx-auto mb-6">
              <div class="empty-circle">
                <FolderOpenIcon class="w-16 h-16 text-gray-600" />
              </div>
            </div>
            <h3 class="text-2xl font-bold mb-2" style="color: var(--text-primary)">Kategori Bulunamadı</h3>
            <p class="text-gray-500 max-w-md mx-auto mb-6">
              Seçili filtrelere uygun kategori yok. Farklı filtreler deneyebilir veya tüm kategorileri görüntüleyebilirsiniz.
            </p>
            <n-button type="primary" @click="activeFilter = 'all'">
              Tüm Kategorileri Göster
            </n-button>
          </div>

          <!-- Categories Grid/List -->
          <div v-else :class="viewMode === 'grid' ? 'grid md:grid-cols-2 gap-4' : 'space-y-4'">
            <div
              v-for="(category, index) in filteredCategories"
              :key="category.id"
              class="category-card glass-card rounded-2xl overflow-hidden cursor-pointer animate-slideUp"
              :style="{ animationDelay: `${index * 50}ms` }"
              @click="router.push(`/forum/category/${category.id}`)"
            >
              <!-- Card Header with Gradient -->
              <div :class="['card-header h-2', getCategoryGradientClass(category.gradient)]"></div>

              <div class="p-6">
                <div class="flex items-start gap-4">
                  <!-- Floating Icon -->
                  <div class="category-icon-wrapper relative">
                    <div
                      :class="[
                        'category-icon w-16 h-16 rounded-xl flex items-center justify-center relative z-10',
                        getCategoryGradientClass(category.gradient)
                      ]"
                      :style="category.color ? { background: `linear-gradient(135deg, ${category.color}, ${category.color}dd)` } : {}"
                    >
                      <span v-if="category.emoji" class="text-3xl">{{ category.emoji }}</span>
                      <component v-else :is="category.icon" class="w-8 h-8 text-white" />
                    </div>
                    <div :class="['icon-glow', getCategoryGlowClass(category.gradient)]"></div>
                  </div>

                  <!-- Category Info -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between mb-2">
                      <div>
                        <h3 class="text-xl font-bold group-hover:text-orange-500 transition-colors flex items-center gap-2" style="color: var(--text-primary)">
                          {{ category.name }}
                          <span v-if="category.isHot" class="hot-badge px-2 py-0.5 text-xs rounded-full">HOT</span>
                        </h3>
                        <p class="text-sm text-gray-400 mt-1">
                          {{ category.description }}
                        </p>
                      </div>
                      <ChevronRightIcon class="w-5 h-5 text-gray-500 flex-shrink-0 category-arrow" />
                    </div>

                    <!-- Stats Pills -->
                    <div class="flex flex-wrap items-center gap-2 mt-4">
                      <div class="stat-pill">
                        <FileTextIcon class="w-3.5 h-3.5" />
                        <span>{{ formatNumber(category.topics) }} Konu</span>
                      </div>
                      <div class="stat-pill">
                        <MessageSquareIcon class="w-3.5 h-3.5" />
                        <span>{{ formatNumber(category.posts) }} Gönderi</span>
                      </div>
                      <div v-if="category.newToday" class="stat-pill stat-pill-highlight">
                        <SparklesIcon class="w-3.5 h-3.5" />
                        <span>+{{ category.newToday }} bugün</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Latest Topic -->
                <div
                  v-if="category.latestTopic"
                  class="latest-topic mt-4 pt-4 border-t border-white/5"
                >
                  <div class="flex items-center gap-3">
                    <div class="relative">
                      <n-avatar round :size="32" :src="category.latestTopic.authorAvatar" />
                      <div class="online-indicator"></div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-semibold text-gray-300 truncate hover:text-orange-500 transition-colors">
                        {{ category.latestTopic.title }}
                      </p>
                      <p class="text-xs text-gray-500 flex items-center gap-2">
                        <span>{{ category.latestTopic.author }}</span>
                        <span class="w-1 h-1 bg-gray-600 rounded-full"></span>
                        <ClockIcon class="w-3 h-3" />
                        <span>{{ category.latestTopic.time }}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Hot Topics -->
          <div class="hot-topics-card glass-card rounded-2xl overflow-hidden animate-slideUp">
            <div class="card-header-gradient p-4 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="icon-pulse">
                  <FlameIcon class="w-5 h-5 text-orange-500" />
                </div>
                <span class="font-bold" style="color: var(--text-primary)">Popüler Konular</span>
              </div>
              <span class="live-badge">
                <span class="live-dot"></span>
                CANLI
              </span>
            </div>
            <div class="p-4 space-y-3">
              <div
                v-for="(topic, index) in hotTopics"
                :key="topic.id"
                class="hot-topic-item p-3 rounded-xl cursor-pointer transition-all"
                @click="router.push(`/forum/topic/${topic.id}`)"
              >
                <div class="flex items-start gap-3">
                  <span class="topic-rank text-lg font-bold" :class="getRankColor(index)">
                    #{{ index + 1 }}
                  </span>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold truncate" style="color: var(--text-primary)">{{ topic.title }}</p>
                    <div class="flex items-center gap-2 mt-1 text-xs text-gray-500">
                      <span class="flex items-center gap-1">
                        <MessageSquareIcon class="w-3 h-3" />
                        {{ topic.replies }}
                      </span>
                      <span class="flex items-center gap-1">
                        <EyeIcon class="w-3 h-3" />
                        {{ topic.views }}
                      </span>
                      <span class="flex items-center gap-1">
                        <TrendingUpIcon class="w-3 h-3 text-green-500" />
                        {{ topic.trend }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Forum Stats -->
          <n-card class="glass-card rounded-2xl animate-slideUp animation-delay-100">
            <template #header>
              <div class="flex items-center gap-2">
                <BarChart3Icon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Forum İstatistikleri</span>
              </div>
            </template>
            <div class="space-y-3">
              <div v-for="statItem in sidebarStats" :key="statItem.label" class="stat-row p-3 rounded-xl">
                <div class="flex items-center justify-between">
                  <span class="text-gray-400 flex items-center gap-2">
                    <component :is="statItem.icon" class="w-4 h-4" />
                    {{ statItem.label }}
                  </span>
                  <span :class="['font-bold', statItem.color]">{{ formatNumber(statItem.value) }}</span>
                </div>
                <div class="progress-bar mt-2">
                  <div class="progress-fill" :class="statItem.barColor" :style="{ width: statItem.progress + '%' }"></div>
                </div>
              </div>
            </div>
          </n-card>

          <!-- Active Users -->
          <n-card class="glass-card rounded-2xl animate-slideUp animation-delay-200">
            <template #header>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <UsersIcon class="w-5 h-5 text-orange-500" />
                  <span class="font-bold">Aktif Kullanıcılar</span>
                </div>
                <span class="text-xs text-gray-500">{{ activeUsers.length }} çevrimiçi</span>
              </div>
            </template>
            <div class="space-y-2">
              <div
                v-for="user in activeUsers"
                :key="user.id"
                class="user-item flex items-center gap-3 p-2 rounded-xl cursor-pointer"
              >
                <div class="relative">
                  <n-avatar round :size="40" :src="user.avatar" />
                  <div class="user-status" :class="user.status"></div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-semibold truncate text-sm" style="color: var(--text-primary)">{{ user.name }}</p>
                  <p class="text-xs text-gray-500">{{ user.activity }}</p>
                </div>
                <div class="user-badge" :class="user.badgeColor">
                  {{ user.badge }}
                </div>
              </div>
            </div>
          </n-card>

          <!-- Recent Activity -->
          <n-card class="glass-card rounded-2xl animate-slideUp animation-delay-300">
            <template #header>
              <div class="flex items-center gap-2">
                <ActivityIcon class="w-5 h-5 text-orange-500" />
                <span class="font-bold">Son Aktiviteler</span>
              </div>
            </template>
            <div class="activity-timeline">
              <div
                v-for="activity in recentActivity"
                :key="activity.id"
                class="activity-item"
              >
                <div :class="['activity-dot', activity.dotColor]"></div>
                <div class="activity-content">
                  <p class="text-sm text-gray-300">{{ activity.message }}</p>
                  <span class="text-xs text-gray-500">{{ activity.time }}</span>
                </div>
              </div>
            </div>
          </n-card>
        </div>
      </div>
    </div>

    <!-- New Topic Modal -->
    <n-modal v-model:show="showNewTopicModal" :mask-closable="false">
      <div class="new-topic-modal glass-card rounded-2xl w-full max-w-3xl mx-4">
        <!-- Modal Header -->
        <div class="modal-header p-6 border-b border-white/10">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="modal-icon w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
                <EditIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 class="text-xl font-bold" style="color: var(--text-primary)">Yeni Konu Oluştur</h2>
                <p class="text-sm text-gray-500">Topluluğa yeni bir tartışma başlatın</p>
              </div>
            </div>
            <button class="close-btn p-2 rounded-lg" @click="showNewTopicModal = false">
              <XIcon class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Modal Body -->
        <div class="modal-body p-6">
          <div class="grid md:grid-cols-2 gap-6">
            <!-- Editor Side -->
            <div class="editor-side space-y-4">
              <div class="form-group">
                <label class="form-label">Kategori Seç</label>
                <n-select
                  v-model:value="newTopic.categoryId"
                  placeholder="Kategori seçin"
                  :options="categoryOptions"
                  class="w-full"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Konu Başlığı</label>
                <n-input
                  v-model:value="newTopic.title"
                  placeholder="Dikkat çekici bir başlık yazın..."
                  class="title-input"
                />
                <span class="char-counter text-xs text-gray-500">{{ newTopic.title.length }}/100</span>
              </div>

              <div class="form-group">
                <label class="form-label">İçerik</label>
                <div class="editor-toolbar flex gap-1 mb-2">
                  <button v-for="tool in editorTools" :key="tool.name" class="toolbar-btn" :title="tool.title">
                    <component :is="tool.icon" class="w-4 h-4" />
                  </button>
                  <div class="toolbar-divider mx-2"></div>
                  <button
                    class="toolbar-btn image-upload-btn"
                    :class="{ 'disabled': topicImages.length >= MAX_IMAGES }"
                    :title="`Resim Ekle (${topicImages.length}/${MAX_IMAGES})`"
                    @click="triggerImageUpload"
                    :disabled="topicImages.length >= MAX_IMAGES || isUploadingImage"
                  >
                    <ImageIcon class="w-4 h-4" />
                    <span v-if="isUploadingImage" class="loading-spinner-sm ml-1"></span>
                  </button>
                  <input
                    ref="imageUploadInput"
                    type="file"
                    accept="image/*"
                    multiple
                    class="hidden"
                    @change="handleImageSelect"
                  />
                </div>
                <n-input
                  v-model:value="newTopic.content"
                  type="textarea"
                  placeholder="Konu içeriğini yazın... Markdown desteklenir"
                  :rows="10"
                  class="content-textarea"
                />

                <!-- Image Preview Section -->
                <div v-if="topicImages.length > 0" class="image-preview-section mt-3">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs text-gray-400">Yuklenen Resimler ({{ topicImages.length }}/{{ MAX_IMAGES }})</span>
                    <button class="text-xs text-red-400 hover:text-red-300" @click="clearImages">Tümünü Temizle</button>
                  </div>
                  <div class="image-preview-grid">
                    <div v-for="image in topicImages" :key="image.id" class="image-preview-item">
                      <img :src="image.preview" :alt="image.name" />
                      <button class="image-remove-btn" @click="removeImage(image.id)">
                        <XIcon class="w-3 h-3" />
                      </button>
                      <span class="image-name">{{ image.name }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Etiketler</label>
                <n-select
                  v-model:value="newTopic.tags"
                  multiple
                  filterable
                  tag
                  placeholder="Etiket ekleyin..."
                  :options="tagOptions"
                />
              </div>
            </div>

            <!-- Preview Side -->
            <div class="preview-side">
              <div class="preview-header flex items-center justify-between mb-4">
                <span class="text-sm font-semibold text-gray-400">Önizleme</span>
                <span class="preview-badge">CANLI</span>
              </div>
              <div class="preview-card glass-card rounded-xl p-4">
                <div v-if="!newTopic.title && !newTopic.content" class="preview-empty text-center py-12">
                  <EyeIcon class="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p class="text-gray-500">Konunuz burada önizlenecek</p>
                </div>
                <div v-else>
                  <h3 class="text-lg font-bold mb-2" style="color: var(--text-primary)">{{ newTopic.title || 'Başlık girilmedi' }}</h3>
                  <div class="flex items-center gap-2 mb-4 text-sm text-gray-500">
                    <n-avatar round :size="24" :src="authStore.user?.avatar" />
                    <span>{{ authStore.user?.username || 'Kullanıcı' }}</span>
                    <span>•</span>
                    <span>Şimdi</span>
                  </div>
                  <div class="preview-content prose prose-invert text-sm text-gray-300">
                    {{ newTopic.content || 'İçerik girilmedi...' }}
                  </div>
                  <div v-if="newTopic.tags?.length" class="flex flex-wrap gap-2 mt-4">
                    <span v-for="tag in newTopic.tags" :key="tag" class="tag-pill">
                      #{{ tag }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="preview-tips mt-4 space-y-2">
                <div class="tip-item" :class="{ 'tip-valid': newTopic.categoryId }">
                  <CheckCircleIcon v-if="newTopic.categoryId" class="w-4 h-4 text-green-500" />
                  <CircleIcon v-else class="w-4 h-4 text-gray-600" />
                  <span>Kategori seçildi</span>
                </div>
                <div class="tip-item" :class="{ 'tip-valid': newTopic.title.length >= 5 }">
                  <CheckCircleIcon v-if="newTopic.title.length >= 5" class="w-4 h-4 text-green-500" />
                  <CircleIcon v-else class="w-4 h-4 text-gray-600" />
                  <span>Başlık en az 5 karakter</span>
                </div>
                <div class="tip-item" :class="{ 'tip-valid': newTopic.content.length >= 20 }">
                  <CheckCircleIcon v-if="newTopic.content.length >= 20" class="w-4 h-4 text-green-500" />
                  <CircleIcon v-else class="w-4 h-4 text-gray-600" />
                  <span>İçerik en az 20 karakter</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer p-6 border-t border-white/10 flex items-center justify-between">
          <div class="flex items-center gap-4 text-sm text-gray-500">
            <span>
              <kbd class="kbd-sm">Ctrl</kbd> + <kbd class="kbd-sm">Enter</kbd> ile gönder
            </span>
            <transition name="fade">
              <span v-if="draftSaved" class="draft-saved-indicator flex items-center gap-1.5 text-green-500">
                <CheckCircleIcon class="w-4 h-4" />
                Taslak kaydedildi
              </span>
            </transition>
          </div>
          <div class="flex gap-3">
            <n-button quaternary @click="showNewTopicModal = false">İptal</n-button>
            <n-button type="primary" :disabled="!isTopicValid" :loading="isSubmitting" @click="createTopic">
              <template #icon><SendIcon class="w-4 h-4" /></template>
              Konuyu Oluştur
            </n-button>
          </div>
        </div>
      </div>
    </n-modal>

    <!-- Keyboard Shortcuts Modal -->
    <n-modal v-model:show="showShortcutsModal" preset="card" title="Klavye Kısayolları" style="width: 500px;">
      <div class="shortcuts-list space-y-3">
        <div v-for="shortcut in keyboardShortcuts" :key="shortcut.key" class="shortcut-item flex items-center justify-between p-3 rounded-lg bg-white/5">
          <span class="text-gray-300">{{ shortcut.description }}</span>
          <div class="flex items-center gap-1">
            <kbd v-for="(key, idx) in shortcut.keys" :key="idx" class="kbd">{{ key }}</kbd>
          </div>
        </div>
      </div>
    </n-modal>

    <!-- Steam Required Modal -->
    <SteamRequiredModal
      :show="showSteamModal"
      @close="closeModal"
      @connect="connectSteam"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MaintenanceOverlay from '@/components/MaintenanceOverlay.vue'
import SteamRequiredModal from '@/components/SteamRequiredModal.vue'
import { forumAPI } from '@/api'
import { useRequireSteam } from '@/composables/useRequireSteam'
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
  SendIcon,
  FlameIcon,
  EyeIcon,
  ClockIcon,
  BarChart3Icon,
  ArrowRightIcon,
  SearchXIcon,
  FolderOpenIcon,
  LayoutGridIcon,
  LayoutListIcon,
  SparklesIcon,
  EditIcon,
  XIcon,
  CheckCircleIcon,
  CircleIcon,
  BoldIcon,
  ItalicIcon,
  LinkIcon,
  ImageIcon,
  ListIcon,
  CodeIcon,
  HashIcon,
  ZapIcon,
  StarIcon,
  AwardIcon,
  ShieldIcon,
  HomeIcon,
  LockIcon
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const { hasSteam, showSteamModal, requireSteam, connectSteam, closeModal } = useRequireSteam()

// Auth state
const isLoggedIn = computed(() => !!authStore.user)

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

// State
const searchQuery = ref('')
const showSearchResults = ref(false)
const searchResults = ref([])
const isSearching = ref(false)
const showNewTopicModal = ref(false)
const showShortcutsModal = ref(false)
const isLoading = ref(false)
const isSubmitting = ref(false)
const statsSection = ref(null)
const statsVisible = ref(false)
const activeFilter = ref('all')
const sortBy = ref('latest')
const viewMode = ref('list')

const stats = reactive({
  totalTopics: 1648,
  totalPosts: 11532,
  totalMembers: 3421,
  onlineUsers: 127
})

const animatedStats = reactive({
  totalTopics: 0,
  totalPosts: 0,
  totalMembers: 0,
  onlineUsers: 0
})

// Stats items for animated section
const statsItems = [
  { key: 'totalTopics', label: 'Toplam Konu', icon: FileTextIcon, iconBg: 'bg-gradient-to-br from-orange-500 to-orange-600', valueColor: 'text-orange-500' },
  { key: 'totalPosts', label: 'Toplam Gönderi', icon: MessageSquareIcon, iconBg: 'bg-gradient-to-br from-purple-500 to-purple-600', valueColor: 'text-purple-500' },
  { key: 'totalMembers', label: 'Toplam Üye', icon: UsersIcon, iconBg: 'bg-gradient-to-br from-cyan-500 to-cyan-600', valueColor: 'text-cyan-500' },
  { key: 'onlineUsers', label: 'Çevrimiçi', icon: ZapIcon, iconBg: 'bg-gradient-to-br from-green-500 to-green-600', valueColor: 'text-green-500' }
]

// Sidebar stats
const sidebarStats = computed(() => [
  { label: 'Toplam Konu', value: stats.totalTopics, icon: FileTextIcon, color: 'text-orange-500', barColor: 'bg-orange-500', progress: 85 },
  { label: 'Toplam Gönderi', value: stats.totalPosts, icon: MessageSquareIcon, color: 'text-purple-500', barColor: 'bg-purple-500', progress: 92 },
  { label: 'Toplam Üye', value: stats.totalMembers, icon: UsersIcon, color: 'text-cyan-500', barColor: 'bg-cyan-500', progress: 78 },
  { label: 'Çevrimiçi', value: stats.onlineUsers, icon: ZapIcon, color: 'text-green-500', barColor: 'bg-green-500', progress: 45 }
])

// Category filters
const categoryFilters = [
  { id: 'all', name: 'Tümü', icon: HomeIcon, count: null },
  { id: 'hot', name: 'Popüler', icon: FlameIcon, count: 12 },
  { id: 'new', name: 'Yeni', icon: SparklesIcon, count: 24 },
  { id: 'support', name: 'Destek', icon: WrenchIcon, count: 8 },
  { id: 'events', name: 'Etkinlikler', icon: TrophyIcon, count: 3 }
]

// Sort options
const sortOptions = [
  { label: 'En Yeni', value: 'latest' },
  { label: 'En Popüler', value: 'popular' },
  { label: 'En Çok Yanıt', value: 'replies' },
  { label: 'En Çok Görüntülenen', value: 'views' }
]

// Editor tools
const editorTools = [
  { name: 'bold', icon: BoldIcon, title: 'Kalın' },
  { name: 'italic', icon: ItalicIcon, title: 'İtalik' },
  { name: 'link', icon: LinkIcon, title: 'Link' },
  { name: 'image', icon: ImageIcon, title: 'Resim' },
  { name: 'list', icon: ListIcon, title: 'Liste' },
  { name: 'code', icon: CodeIcon, title: 'Kod' }
]

// Tag options
const tagOptions = [
  { label: 'amxmodx', value: 'amxmodx' },
  { label: 'hlds', value: 'hlds' },
  { label: 'plugin', value: 'plugin' },
  { label: 'sunucu', value: 'sunucu' },
  { label: 'yardim', value: 'yardim' },
  { label: 'turnuva', value: 'turnuva' }
]

// Keyboard shortcuts
const keyboardShortcuts = [
  { keys: ['N'], description: 'Yeni konu oluştur' },
  { keys: ['Ctrl', 'K'], description: 'Arama yap' },
  { keys: ['/'], description: 'Aramaya odaklan' },
  { keys: ['?'], description: 'Kısayolları göster' },
  { keys: ['Esc'], description: 'Modalı kapat' },
  { keys: ['Ctrl', 'Enter'], description: 'Formu gönder' }
]

// Loading states
const loadingCategories = ref(true)
const loadingHotTopics = ref(true)
const loadingStats = ref(true)
const errorMessage = ref('')

// Kategoriler - API'den çekilecek
const categories = ref([])

// Hot Topics - API'den çekilecek
const hotTopics = ref([])

// Icon mapping for categories (fallback when API doesn't provide emoji)
const categoryIconMap = {
  'genel': MessageSquareIcon,
  'genel-sohbet': MessageSquareIcon,
  'duyurular': TrendingUpIcon,
  'sunucu': ServerIcon,
  'sunucular': ServerIcon,
  'teknik': WrenchIcon,
  'teknik-destek': WrenchIcon,
  'oyun': TrophyIcon,
  'turnuva': TrophyIcon,
  'soru': HelpCircleIcon,
  'yardim': HelpCircleIcon,
  'default': FileTextIcon
}

// Check if a string is an emoji
const isEmoji = (str) => {
  if (!str || typeof str !== 'string') return false
  // Check for common emoji patterns (Unicode emoji ranges)
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F000}-\u{1F02F}]|[\u{1F0A0}-\u{1F0FF}]/u
  return emojiRegex.test(str)
}

// Gradient mapping for categories
const categoryGradientMap = {
  'genel': 'primary-secondary',
  'duyurular': 'warning-success',
  'sunucu': 'secondary-accent',
  'teknik': 'accent-error',
  'oyun': 'primary-accent',
  'default': 'primary-secondary'
}

// Fetch categories from API
const fetchCategories = async () => {
  loadingCategories.value = true
  errorMessage.value = ''
  try {
    const response = await forumAPI.getCategories()
    const data = response.data?.categories || response.data || []

    // Transform API data to component format
    categories.value = data.map((cat, index) => {
      const slug = cat.slug || cat.name?.toLowerCase().replace(/\s+/g, '-') || 'default'
      const iconKey = Object.keys(categoryIconMap).find(key => slug.includes(key)) || 'default'
      const gradientKey = Object.keys(categoryGradientMap).find(key => slug.includes(key)) || 'default'

      // Determine icon: use emoji from API if available, otherwise use Vue component
      const apiIcon = cat.icon
      const hasEmojiIcon = isEmoji(apiIcon)

      return {
        id: cat.id,
        name: cat.name,
        slug: slug,
        description: cat.description || '',
        icon: hasEmojiIcon ? null : categoryIconMap[iconKey],
        emoji: hasEmojiIcon ? apiIcon : null,
        color: cat.color || '#ff6b00',
        gradient: categoryGradientMap[gradientKey],
        topics: cat.topic_count || cat.topics_count || 0,
        posts: cat.post_count || cat.posts_count || 0,
        newToday: cat.new_today || Math.floor(Math.random() * 20),
        isHot: (cat.topic_count || 0) > 100,
        lastActivity: cat.last_activity || cat.updated_at || new Date().toISOString()
      }
    })

    // If no categories from API, add default categories
    if (categories.value.length === 0) {
      categories.value = getDefaultCategories()
    }
  } catch (error) {
    console.error('Categories fetch error:', error)
    // Use default categories on error
    categories.value = getDefaultCategories()
  } finally {
    loadingCategories.value = false
  }
}

// Default categories when API returns empty
const getDefaultCategories = () => [
  { id: 1, name: 'Genel Sohbet', slug: 'genel-sohbet', description: 'Her konuda sohbet', icon: MessageSquareIcon, emoji: null, color: '#ff6b00', gradient: 'primary-secondary', topics: 0, posts: 0, newToday: 0, isHot: false },
  { id: 2, name: 'Duyurular', slug: 'duyurular', description: 'Önemli duyurular', icon: TrendingUpIcon, emoji: null, color: '#22c55e', gradient: 'warning-success', topics: 0, posts: 0, newToday: 0, isHot: false },
  { id: 3, name: 'Sunucu İlanları', slug: 'sunucu-ilanlari', description: 'Sunucu ilanları ve tanıtımlar', icon: ServerIcon, emoji: null, color: '#8b5cf6', gradient: 'secondary-accent', topics: 0, posts: 0, newToday: 0, isHot: false },
  { id: 4, name: 'Teknik Destek', slug: 'teknik-destek', description: 'Teknik sorunlar ve çözümler', icon: WrenchIcon, emoji: null, color: '#ef4444', gradient: 'accent-error', topics: 0, posts: 0, newToday: 0, isHot: false },
  { id: 5, name: 'Turnuvalar', slug: 'turnuvalar', description: 'Turnuva duyuruları ve sonuçlar', icon: TrophyIcon, emoji: null, color: '#f59e0b', gradient: 'primary-accent', topics: 0, posts: 0, newToday: 0, isHot: false },
  { id: 6, name: 'Yardım & Sorular', slug: 'yardim-sorular', description: 'Sorularınızı sorun', icon: HelpCircleIcon, emoji: null, color: '#06b6d4', gradient: 'secondary-accent', topics: 0, posts: 0, newToday: 0, isHot: false }
]

// Fetch hot topics from API
const fetchHotTopics = async () => {
  loadingHotTopics.value = true
  try {
    const response = await forumAPI.getAllTopics({ sort: 'popular', limit: 5 })
    const data = response.data?.topics || response.data || []

    hotTopics.value = data.map(topic => ({
      id: topic.id,
      title: topic.title,
      slug: topic.slug,
      views: topic.view_count || topic.views || 0,
      replies: topic.reply_count || topic.replies || 0,
      author: topic.author?.username || topic.author_name || 'Anonim'
    }))
  } catch (error) {
    console.error('Hot topics fetch error:', error)
    hotTopics.value = []
  } finally {
    loadingHotTopics.value = false
  }
}

// Fetch forum stats from API
const fetchForumStats = async () => {
  loadingStats.value = true
  try {
    const response = await forumAPI.getStats()
    const data = response.data || {}

    stats.totalTopics = data.total_topics || data.topics_count || 0
    stats.totalPosts = data.total_posts || data.posts_count || 0
    stats.totalMembers = data.total_members || data.members_count || 0
    stats.onlineUsers = data.online_users || data.online_count || 0
  } catch (error) {
    console.error('Forum stats fetch error:', error)
    // Keep existing placeholder values on error
  } finally {
    loadingStats.value = false
  }
}

const filteredCategories = computed(() => {
  if (activeFilter.value === 'all') return categories.value
  if (activeFilter.value === 'hot') return categories.value.filter(c => c.isHot)
  if (activeFilter.value === 'new') return categories.value.filter(c => c.newToday > 10)
  return categories.value.filter(c => c.filter === activeFilter.value)
})

const categoryOptions = computed(() => {
  return categories.value.map(cat => ({
    label: cat.name,
    value: cat.id
  }))
})

const isTopicValid = computed(() => {
  return newTopic.categoryId && newTopic.title.length >= 5 && newTopic.content.length >= 20
})

const getCategoryGradientClass = (gradient) => {
  const gradients = {
    'primary-secondary': 'bg-gradient-to-br from-orange-500 to-purple-500',
    'secondary-accent': 'bg-gradient-to-br from-purple-500 to-cyan-500',
    'accent-error': 'bg-gradient-to-br from-cyan-500 to-red-500',
    'primary-accent': 'bg-gradient-to-br from-orange-500 to-cyan-500',
    'warning-success': 'bg-gradient-to-br from-yellow-500 to-green-500'
  }
  return gradients[gradient] || 'bg-gradient-to-br from-orange-500 to-purple-500'
}

const getCategoryGlowClass = (gradient) => {
  const glows = {
    'primary-secondary': 'glow-orange-purple',
    'secondary-accent': 'glow-purple-cyan',
    'accent-error': 'glow-cyan-red',
    'primary-accent': 'glow-orange-cyan',
    'warning-success': 'glow-yellow-green'
  }
  return glows[gradient] || 'glow-orange-purple'
}

const getRankColor = (index) => {
  const colors = ['text-yellow-500', 'text-gray-400', 'text-orange-600', 'text-gray-500', 'text-gray-500']
  return colors[index] || 'text-gray-500'
}

const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// Particle style generator
const getParticleStyle = (n) => {
  const random = (min, max) => Math.random() * (max - min) + min
  return {
    left: `${random(0, 100)}%`,
    top: `${random(0, 100)}%`,
    animationDelay: `${random(0, 5)}s`,
    animationDuration: `${random(10, 20)}s`,
    width: `${random(2, 6)}px`,
    height: `${random(2, 6)}px`,
    opacity: random(0.1, 0.5)
  }
}

// Aktif kullanıcılar - API'den çekilecek
const activeUsers = ref([])

// Son aktiviteler - API'den çekilecek
const recentActivity = ref([])

const newTopic = reactive({
  categoryId: null,
  title: '',
  content: '',
  tags: []
})

// Draft auto-save state
const draftSaveTimer = ref(null)
const draftSaved = ref(false)
const draftSavedTimeout = ref(null)
const DRAFT_KEY = 'forum_draft_topic'

// Image upload state
const MAX_IMAGES = 3
const MAX_IMAGE_SIZE = 2 * 1024 * 1024 // 2MB
const topicImages = ref([])
const imageUploadInput = ref(null)
const isUploadingImage = ref(false)

// Draft auto-save functions
const saveDraft = () => {
  if (newTopic.title || newTopic.content || newTopic.categoryId || newTopic.tags.length > 0) {
    const draft = {
      categoryId: newTopic.categoryId,
      title: newTopic.title,
      content: newTopic.content,
      tags: newTopic.tags,
      savedAt: Date.now()
    }
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft))
    draftSaved.value = true

    // Hide "Draft saved" indicator after 2 seconds
    if (draftSavedTimeout.value) clearTimeout(draftSavedTimeout.value)
    draftSavedTimeout.value = setTimeout(() => {
      draftSaved.value = false
    }, 2000)
  }
}

const loadDraft = () => {
  const savedDraft = localStorage.getItem(DRAFT_KEY)
  if (savedDraft) {
    try {
      const draft = JSON.parse(savedDraft)
      // Only load if draft is less than 24 hours old
      if (Date.now() - draft.savedAt < 24 * 60 * 60 * 1000) {
        newTopic.categoryId = draft.categoryId
        newTopic.title = draft.title || ''
        newTopic.content = draft.content || ''
        newTopic.tags = draft.tags || []
        window.$message?.info('Taslak yuklendi')
      } else {
        // Draft is too old, clear it
        clearDraft()
      }
    } catch (e) {
      console.error('Failed to load draft:', e)
      clearDraft()
    }
  }
}

const clearDraft = () => {
  localStorage.removeItem(DRAFT_KEY)
  draftSaved.value = false
}

const startDraftAutoSave = () => {
  // Save draft every 10 seconds while typing
  draftSaveTimer.value = setInterval(() => {
    if (showNewTopicModal.value) {
      saveDraft()
    }
  }, 10000)
}

const stopDraftAutoSave = () => {
  if (draftSaveTimer.value) {
    clearInterval(draftSaveTimer.value)
    draftSaveTimer.value = null
  }
}

// Image upload functions
const triggerImageUpload = () => {
  if (topicImages.value.length >= MAX_IMAGES) {
    window.$message?.warning(`En fazla ${MAX_IMAGES} resim yukleyebilirsiniz`)
    return
  }
  imageUploadInput.value?.click()
}

const handleImageSelect = async (event) => {
  const files = Array.from(event.target.files || [])

  for (const file of files) {
    if (topicImages.value.length >= MAX_IMAGES) {
      window.$message?.warning(`En fazla ${MAX_IMAGES} resim yukleyebilirsiniz`)
      break
    }

    if (!file.type.startsWith('image/')) {
      window.$message?.error(`${file.name} bir resim dosyasi degil`)
      continue
    }

    if (file.size > MAX_IMAGE_SIZE) {
      window.$message?.error(`${file.name} 2MB'dan buyuk`)
      continue
    }

    try {
      isUploadingImage.value = true
      const imageData = await uploadImage(file)
      topicImages.value.push(imageData)

      // Insert markdown into content
      const markdown = `![${file.name}](${imageData.url})\n`
      newTopic.content += markdown

      window.$message?.success('Resim yuklendi')
    } catch (error) {
      window.$message?.error('Resim yuklenemedi: ' + (error.message || 'Bilinmeyen hata'))
    } finally {
      isUploadingImage.value = false
    }
  }

  // Reset input
  event.target.value = ''
}

const uploadImage = async (file) => {
  // Try to upload to API first
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch('/api/media/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'X-CSRF-Token': getCsrfToken()
      },
      body: formData
    })

    if (response.ok) {
      const data = await response.json()
      return {
        id: Date.now(),
        name: file.name,
        url: data.url || data.file_url,
        preview: data.url || data.file_url
      }
    }
  } catch (e) {
    console.log('API upload failed, falling back to base64:', e)
  }

  // Fallback to base64
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      resolve({
        id: Date.now(),
        name: file.name,
        url: e.target.result,
        preview: e.target.result
      })
    }
    reader.onerror = () => reject(new Error('Dosya okunamadi'))
    reader.readAsDataURL(file)
  })
}

const removeImage = (imageId) => {
  const image = topicImages.value.find(img => img.id === imageId)
  if (image) {
    // Remove markdown from content
    const markdownPattern = new RegExp(`!\\[${image.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\]\\([^)]+\\)\\n?`, 'g')
    newTopic.content = newTopic.content.replace(markdownPattern, '')

    topicImages.value = topicImages.value.filter(img => img.id !== imageId)
    window.$message?.info('Resim kaldirildi')
  }
}

const clearImages = () => {
  topicImages.value = []
}

// Functions
const setFilter = (filterId) => {
  activeFilter.value = filterId
}

const toggleView = () => {
  viewMode.value = viewMode.value === 'list' ? 'grid' : 'list'
}

const performSearch = () => {
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }

  isSearching.value = true

  // Simulated search - replace with actual API call
  setTimeout(() => {
    searchResults.value = [
      { id: 1, title: 'AWP Taktikleri Rehberi', subtitle: 'Genel Tartışma • 156 yanıt', icon: FileTextIcon, iconBg: 'bg-orange-500/20' },
      { id: 2, title: 'HLDS Kurulum Rehberi', subtitle: 'Sunucu Ayarları • 89 yanıt', icon: ServerIcon, iconBg: 'bg-purple-500/20' },
      { id: 3, title: 'Player123', subtitle: 'Kullanıcı • 1234 gönderi', icon: UsersIcon, iconBg: 'bg-cyan-500/20' }
    ]
    isSearching.value = false
  }, 500)
}

const hideSearchResults = () => {
  setTimeout(() => {
    showSearchResults.value = false
  }, 200)
}

const goToResult = (result) => {
  router.push(`/forum/topic/${result.id}`)
  showSearchResults.value = false
  searchQuery.value = ''
}

// Intersection Observer for stats animation
const animateStats = () => {
  const duration = 2000
  const steps = 60
  const interval = duration / steps

  let currentStep = 0

  const timer = setInterval(() => {
    currentStep++
    const progress = currentStep / steps
    const easeOut = 1 - Math.pow(1 - progress, 3)

    animatedStats.totalTopics = Math.round(stats.totalTopics * easeOut)
    animatedStats.totalPosts = Math.round(stats.totalPosts * easeOut)
    animatedStats.totalMembers = Math.round(stats.totalMembers * easeOut)
    animatedStats.onlineUsers = Math.round(stats.onlineUsers * easeOut)

    if (currentStep >= steps) {
      clearInterval(timer)
    }
  }, interval)
}

// Handle new topic button - require Steam
const handleNewTopic = () => {
  requireSteam(() => {
    showNewTopicModal.value = true
  })
}

const createTopic = async () => {
  if (!isTopicValid.value) return

  isSubmitting.value = true

  try {
    const response = await fetch('/api/forum/topics', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        category_id: newTopic.categoryId,
        title: newTopic.title.trim(),
        content: newTopic.content.trim(),
        tags: newTopic.tags
      })
    })

    if (response.ok) {
      showNewTopicModal.value = false
      newTopic.categoryId = null
      newTopic.title = ''
      newTopic.content = ''
      newTopic.tags = []
      clearDraft() // Clear draft after successful post
      clearImages() // Clear uploaded images
      window.$message?.success('Konu başarıyla oluşturuldu')
    } else {
      const error = await response.json()
      window.$message?.error(error.detail || 'Konu oluşturulamadı')
    }
  } catch (error) {
    window.$message?.error('Bir hata oluştu, lütfen tekrar deneyin')
  } finally {
    isSubmitting.value = false
  }
}

// Keyboard shortcuts handler
const handleKeydown = (e) => {
  // Don't trigger shortcuts when typing in inputs
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault()
      if (showNewTopicModal.value && isTopicValid.value) {
        createTopic()
      }
    }
    return
  }

  if (e.key === 'n' || e.key === 'N') {
    e.preventDefault()
    handleNewTopic()
  }

  if (e.key === '/' || (e.ctrlKey && e.key === 'k')) {
    e.preventDefault()
    document.querySelector('.search-input')?.focus()
  }

  if (e.key === '?') {
    e.preventDefault()
    showShortcutsModal.value = true
  }

  if (e.key === 'Escape') {
    showNewTopicModal.value = false
    showShortcutsModal.value = false
    showSearchResults.value = false
  }
}

// Watch for modal open/close to manage draft auto-save
watch(showNewTopicModal, (isOpen) => {
  if (isOpen) {
    loadDraft()
    startDraftAutoSave()
  } else {
    stopDraftAutoSave()
    // Save draft one more time when closing
    saveDraft()
  }
})

onMounted(async () => {
  // Fetch data from API
  await Promise.all([
    fetchCategories(),
    fetchHotTopics(),
    fetchForumStats()
  ])

  // Setup Intersection Observer for stats
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !statsVisible.value) {
          statsVisible.value = true
          animateStats()
        }
      })
    },
    { threshold: 0.5 }
  )

  if (statsSection.value) {
    observer.observe(statsSection.value)
  }

  // Setup keyboard shortcuts
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  stopDraftAutoSave()
  if (draftSavedTimeout.value) clearTimeout(draftSavedTimeout.value)
})
</script>

<style scoped>
/* Base Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

@keyframes particle-float {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(720deg);
    opacity: 0;
  }
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes live-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Animation Classes */
.animate-fadeIn {
  animation: fadeIn 0.6s ease-out forwards;
}

.animate-slideUp {
  animation: slideUp 0.6s ease-out forwards;
}

.animate-slideDown {
  animation: slideDown 0.6s ease-out forwards;
}

.animate-countUp {
  animation: countUp 0.5s ease-out forwards;
}

.animation-delay-100 { animation-delay: 100ms; }
.animation-delay-200 { animation-delay: 200ms; }
.animation-delay-300 { animation-delay: 300ms; }
.animation-delay-400 { animation-delay: 400ms; }

/* Particles */
.particles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  background: linear-gradient(135deg, #f97316, #8b5cf6);
  border-radius: 50%;
  animation: particle-float linear infinite;
}

/* Glass Morphism */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.glass-badge {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.glass-search {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  transition: all 0.3s ease;
}

.glass-search:focus-within {
  border-color: rgba(249, 115, 22, 0.5);
  box-shadow: 0 0 30px rgba(249, 115, 22, 0.15);
}

.glass-button {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #9ca3af;
  transition: all 0.2s ease;
}

.glass-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Text Gradient */
.text-gradient-animated {
  background: linear-gradient(90deg, #f97316, #8b5cf6, #06b6d4, #f97316);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 8s ease infinite;
}

/* Search */
.search-input {
  font-size: 1rem;
}

.search-input::placeholder {
  color: #6b7280;
}

.kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-family: monospace;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.375rem;
  color: #9ca3af;
}

.kbd-sm {
  padding: 0.125rem 0.375rem;
  font-size: 0.625rem;
}

.search-results {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 50;
}

.search-dropdown-enter-active,
.search-dropdown-leave-active {
  transition: all 0.2s ease;
}

.search-dropdown-enter-from,
.search-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.search-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(249, 115, 22, 0.2);
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Stats Section */
.stat-card {
  opacity: 0;
  transform: scale(0.9);
  transition: all 0.3s ease;
}

.stat-card.animate-countUp {
  opacity: 1;
  transform: scale(1);
}

.stat-card:hover {
  transform: translateY(-5px);
  border-color: rgba(249, 115, 22, 0.3);
}

/* Category Filters */
.filter-chip {
  font-size: 0.875rem;
  font-weight: 500;
}

.filter-chip-active {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
}

.filter-chip-inactive {
  background: rgba(255, 255, 255, 0.05);
  color: #9ca3af;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.filter-chip-inactive:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.filter-count {
  background: rgba(255, 255, 255, 0.2);
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Category Cards */
.category-card {
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(20px);
}

.category-card.animate-slideUp {
  opacity: 1;
  transform: translateY(0);
}

.category-card:hover {
  border-color: rgba(249, 115, 22, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.category-card:hover .category-arrow {
  transform: translateX(4px);
  color: #f97316;
}

.category-arrow {
  transition: all 0.3s ease;
}

.category-icon-wrapper {
  position: relative;
}

.category-icon {
  transition: all 0.3s ease;
}

.category-card:hover .category-icon {
  transform: scale(1.1) rotate(5deg);
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 0.75rem;
  opacity: 0;
  transition: opacity 0.3s ease;
  animation: pulse-glow 2s ease-in-out infinite;
}

.category-card:hover .icon-glow {
  opacity: 1;
}

.glow-orange-purple { box-shadow: 0 0 30px rgba(249, 115, 22, 0.5); }
.glow-purple-cyan { box-shadow: 0 0 30px rgba(139, 92, 246, 0.5); }
.glow-cyan-red { box-shadow: 0 0 30px rgba(6, 182, 212, 0.5); }
.glow-orange-cyan { box-shadow: 0 0 30px rgba(249, 115, 22, 0.5); }
.glow-yellow-green { box-shadow: 0 0 30px rgba(234, 179, 8, 0.5); }

.card-header {
  width: 100%;
}

/* Stat Pills */
.stat-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 9999px;
  color: #9ca3af;
}

.stat-pill-highlight {
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

/* Hot Badge */
.hot-badge {
  background: linear-gradient(135deg, #ef4444, #f97316);
  color: white;
  font-weight: 700;
  letter-spacing: 0.05em;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Latest Topic */
.online-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  background: #22c55e;
  border: 2px solid #111827;
  border-radius: 50%;
}

/* Hot Topics Card */
.hot-topics-card {
  overflow: hidden;
}

.card-header-gradient {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(139, 92, 246, 0.1));
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.icon-pulse {
  animation: pulse 2s ease-in-out infinite;
}

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.625rem;
  font-weight: 700;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border-radius: 0.25rem;
  letter-spacing: 0.1em;
}

.live-dot {
  width: 6px;
  height: 6px;
  background: #ef4444;
  border-radius: 50%;
  animation: live-pulse 1s ease-in-out infinite;
}

.hot-topic-item {
  background: rgba(255, 255, 255, 0.02);
}

.hot-topic-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.topic-rank {
  min-width: 2rem;
}

/* Stats Row */
.stat-row {
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.2s ease;
}

.stat-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease-out;
}

/* User Item */
.user-item {
  transition: all 0.2s ease;
}

.user-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border: 2px solid #111827;
  border-radius: 50%;
}

.user-status.online { background: #22c55e; }
.user-status.away { background: #eab308; }
.user-status.offline { background: #6b7280; }

.user-badge {
  padding: 0.125rem 0.5rem;
  font-size: 0.625rem;
  font-weight: 700;
  border-radius: 0.25rem;
  letter-spacing: 0.05em;
}

.badge-pro { background: rgba(249, 115, 22, 0.2); color: #f97316; }
.badge-admin { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.badge-vip { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.badge-new { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.badge-mod { background: rgba(139, 92, 246, 0.2); color: #8b5cf6; }

/* Activity Timeline */
.activity-timeline {
  position: relative;
  padding-left: 1.5rem;
}

.activity-timeline::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, rgba(249, 115, 22, 0.5), transparent);
}

.activity-item {
  position: relative;
  padding: 0.75rem 0;
}

.activity-dot {
  position: absolute;
  left: -1.25rem;
  top: 1rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #111827;
}

.dot-orange { background: #f97316; }
.dot-purple { background: #8b5cf6; }
.dot-green { background: #22c55e; }
.dot-cyan { background: #06b6d4; }
.dot-yellow { background: #eab308; }

/* New Topic Modal */
.new-topic-modal {
  max-height: 90vh;
  overflow-y: auto;
}

.close-btn {
  background: rgba(255, 255, 255, 0.05);
  color: #9ca3af;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #9ca3af;
  margin-bottom: 0.5rem;
}

.char-counter {
  display: block;
  text-align: right;
  margin-top: 0.25rem;
}

.editor-toolbar {
  background: rgba(255, 255, 255, 0.03);
  padding: 0.5rem;
  border-radius: 0.5rem;
}

.toolbar-btn {
  padding: 0.5rem;
  border-radius: 0.375rem;
  color: #9ca3af;
  transition: all 0.2s ease;
}

.toolbar-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.preview-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  font-size: 0.625rem;
  font-weight: 700;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border-radius: 0.25rem;
  letter-spacing: 0.1em;
}

.preview-card {
  min-height: 200px;
}

.preview-empty {
  color: #4b5563;
}

.tag-pill {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
  border-radius: 9999px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  transition: color 0.2s ease;
}

.tip-item.tip-valid {
  color: #9ca3af;
}

/* Skeleton Loading */
.skeleton-card {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.skeleton-box {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.05) 25%, rgba(255, 255, 255, 0.1) 50%, rgba(255, 255, 255, 0.05) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 0.5rem;
}

.skeleton-line {
  height: 1rem;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.05) 25%, rgba(255, 255, 255, 0.1) 50%, rgba(255, 255, 255, 0.05) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 0.25rem;
}

@keyframes skeleton-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Empty State */
.empty-state {
  animation: fadeIn 0.5s ease-out;
}

.empty-illustration {
  width: 120px;
  height: 120px;
}

.empty-circle {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(139, 92, 246, 0.1));
  border-radius: 50%;
  animation: float 3s ease-in-out infinite;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-section .text-5xl {
    font-size: 2.5rem;
  }

  .search-shortcut {
    display: none;
  }

  .shortcuts-hint {
    display: none;
  }

  .new-topic-modal {
    margin: 1rem;
  }

  .grid.md\\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
}

/* Action Button Styles */
.new-topic-btn {
  background: linear-gradient(135deg, #f97316, #ea580c) !important;
  border: none !important;
  font-weight: 600;
  transition: all 0.3s ease !important;
}

.new-topic-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(249, 115, 22, 0.4) !important;
}

.new-topic-btn.btn-disabled {
  background: linear-gradient(135deg, #4b5563, #374151) !important;
  cursor: not-allowed;
  opacity: 0.8;
}

.new-topic-btn.btn-disabled:hover {
  transform: none;
  box-shadow: none !important;
}

/* Shortcut Item */
.shortcut-item kbd {
  min-width: 2rem;
  text-align: center;
}

/* Draft saved indicator */
.draft-saved-indicator {
  animation: fadeInOut 0.3s ease-in-out;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(5px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Image Upload Styles */
.toolbar-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.15);
}

.image-upload-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.image-upload-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner-sm {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(249, 115, 22, 0.2);
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.image-preview-section {
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.image-preview-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.image-preview-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-preview-item:hover img {
  opacity: 0.7;
}

.image-remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.8);
  color: white;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.image-preview-item:hover .image-remove-btn {
  opacity: 1;
}

.image-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2px 4px;
  font-size: 9px;
  background: rgba(0, 0, 0, 0.7);
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hidden {
  display: none;
}
</style>
