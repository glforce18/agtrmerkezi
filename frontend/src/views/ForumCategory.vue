<template>
  <div class="min-h-screen category-page">
    <!-- Animated Background Elements -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="container-custom py-8 relative z-10">
      <!-- Enhanced Breadcrumb with Animated Transitions -->
      <Transition name="breadcrumb-slide" appear>
        <nav class="breadcrumb-container mb-6">
          <div class="breadcrumb-inner">
            <TransitionGroup name="breadcrumb-item" tag="div" class="flex items-center gap-2">
              <button
                key="home"
                @click="router.push('/forum')"
                class="breadcrumb-item group"
              >
                <div class="breadcrumb-icon-wrapper">
                  <HomeIcon class="w-4 h-4" />
                </div>
                <span class="breadcrumb-text">Forum</span>
                <div class="breadcrumb-arrow">
                  <ChevronRightIcon class="w-4 h-4" />
                </div>
              </button>

              <div key="current" class="breadcrumb-current">
                <div class="current-icon-pulse"></div>
                <FolderIcon class="w-4 h-4 text-orange-500 mr-2 relative z-10" />
                <span class="text-orange-500 font-medium">{{ category?.name }}</span>
              </div>
            </TransitionGroup>
          </div>

          <!-- Online Users Indicator -->
          <div class="online-users-indicator">
            <div class="online-dot"></div>
            <UsersIcon class="w-4 h-4" />
            <span class="online-count">{{ onlineUsers }}</span>
            <span class="online-label">cevrimici</span>
          </div>
        </nav>
      </Transition>

      <!-- Category Hero Section with Stats Overlay -->
      <Transition name="hero-fade" appear>
        <section class="category-hero mb-8">
          <div class="hero-background">
            <div class="hero-gradient"></div>
            <div class="hero-pattern"></div>
            <div class="hero-shine"></div>
          </div>

          <div class="hero-content">
            <div class="flex flex-col lg:flex-row items-start lg:items-center gap-6">
              <!-- Category Icon with Animation -->
              <div class="category-icon-wrapper">
                <div
                  :class="[
                    'category-icon',
                    category?.gradient ? getCategoryGradient(category.gradient) : 'bg-gradient-to-br from-orange-500 to-purple-500'
                  ]"
                >
                  <component :is="category?.icon || MessageSquareIcon" class="w-10 h-10 text-white" />
                </div>
                <div class="icon-ring"></div>
                <div class="icon-ring delay-500"></div>
                <div class="icon-ring delay-1000"></div>
                <div class="icon-particles">
                  <span v-for="n in 6" :key="n" class="particle" :style="{ '--i': n }"></span>
                </div>
              </div>

              <!-- Category Info -->
              <div class="flex-1">
                <div class="hero-badge-row">
                  <span class="category-type-badge">
                    <LayersIcon class="w-3.5 h-3.5" />
                    Kategori
                  </span>
                  <span class="topic-count-badge">
                    <FileTextIcon class="w-3.5 h-3.5" />
                    {{ topics.length }} Konu
                  </span>
                </div>
                <h1 class="hero-title">
                  <span class="title-gradient">{{ category?.name || 'Kategori' }}</span>
                </h1>
                <p class="hero-description">{{ category?.description }}</p>

                <!-- Stats Overlay -->
                <div class="stats-overlay">
                  <div
                    class="stat-item"
                    v-for="(stat, index) in categoryStats"
                    :key="stat.label"
                    :style="{ animationDelay: `${index * 100}ms` }"
                  >
                    <div class="stat-icon-wrapper">
                      <component :is="stat.icon" class="w-5 h-5" />
                    </div>
                    <div class="stat-content">
                      <span class="stat-number" :data-value="stat.value">{{ formatNumber(stat.value) }}</span>
                      <span class="stat-label">{{ stat.label }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- New Topic Button -->
              <div class="hero-action">
                <n-button
                  type="primary"
                  size="large"
                  class="new-topic-btn"
                  @click="showNewTopicModal = true"
                >
                  <template #icon>
                    <PlusCircleIcon class="w-5 h-5" />
                  </template>
                  Yeni Konu Ac
                </n-button>
              </div>
            </div>
          </div>
        </section>
      </Transition>

      <!-- Enhanced Filters & Sort with Animated Transitions -->
      <Transition name="filter-slide" appear>
        <section class="filter-section mb-6">
          <div class="filter-card glass-morphism">
            <div class="flex flex-col lg:flex-row gap-4 items-stretch lg:items-center">
              <!-- Search Input -->
              <div class="flex-1 search-wrapper" :class="{ focused: searchFocused }">
                <div class="search-icon">
                  <SearchIcon class="w-5 h-5" />
                </div>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Konularda ara..."
                  class="search-input"
                  @focus="searchFocused = true"
                  @blur="searchFocused = false"
                />
                <Transition name="fade">
                  <button
                    v-if="searchQuery"
                    @click="searchQuery = ''"
                    class="search-clear"
                  >
                    <XIcon class="w-4 h-4" />
                  </button>
                </Transition>
                <div class="search-glow"></div>
              </div>

              <!-- View Mode Toggle -->
              <div class="view-mode-toggle">
                <button
                  @click="viewMode = 'list'"
                  :class="['view-btn', { active: viewMode === 'list' }]"
                  title="Liste Gorunumu"
                >
                  <ListIcon class="w-4 h-4" />
                </button>
                <button
                  @click="viewMode = 'compact'"
                  :class="['view-btn', { active: viewMode === 'compact' }]"
                  title="Kompakt Gorunum"
                >
                  <LayoutGridIcon class="w-4 h-4" />
                </button>
                <div class="view-indicator" :class="viewMode"></div>
              </div>

              <!-- Sort Options with Animation -->
              <div class="sort-wrapper">
                <div class="sort-dropdown" :class="{ open: sortDropdownOpen }">
                  <button class="sort-trigger" @click="sortDropdownOpen = !sortDropdownOpen">
                    <component :is="currentSortOption.icon" class="w-4 h-4" />
                    <span>{{ currentSortOption.label }}</span>
                    <ChevronDownIcon class="w-4 h-4 dropdown-arrow" />
                  </button>
                  <Transition name="dropdown-slide">
                    <div v-if="sortDropdownOpen" class="sort-dropdown-menu glass-morphism">
                      <button
                        v-for="option in sortOptions"
                        :key="option.value"
                        @click="handleSortChange(option.value)"
                        :class="['sort-option', { active: sortBy === option.value }]"
                      >
                        <component :is="option.icon" class="w-4 h-4" />
                        <span>{{ option.label }}</span>
                        <CheckIcon v-if="sortBy === option.value" class="w-4 h-4 check-icon" />
                      </button>
                    </div>
                  </Transition>
                </div>
              </div>

              <!-- Infinite Scroll Toggle -->
              <div class="infinite-scroll-toggle">
                <label class="toggle-label">
                  <span class="toggle-text">
                    <InfinityIcon class="w-4 h-4" />
                    Sonsuz Kaydirma
                  </span>
                  <div class="toggle-switch" :class="{ active: infiniteScrollEnabled }">
                    <input
                      type="checkbox"
                      v-model="infiniteScrollEnabled"
                      class="toggle-input"
                    />
                    <div class="toggle-slider">
                      <div class="slider-dot"></div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            <!-- Active Filters Display -->
            <Transition name="filters-expand">
              <div v-if="searchQuery || sortBy !== 'latest'" class="active-filters">
                <span class="filters-label">Aktif Filtreler:</span>
                <TransitionGroup name="filter-tag" tag="div" class="filters-list">
                  <span v-if="searchQuery" key="search" class="filter-tag">
                    <SearchIcon class="w-3 h-3" />
                    "{{ searchQuery }}"
                    <button @click="searchQuery = ''"><XIcon class="w-3 h-3" /></button>
                  </span>
                  <span v-if="sortBy !== 'latest'" key="sort" class="filter-tag">
                    <ArrowUpDownIcon class="w-3 h-3" />
                    {{ currentSortOption.label }}
                    <button @click="sortBy = 'latest'"><XIcon class="w-3 h-3" /></button>
                  </span>
                </TransitionGroup>
              </div>
            </Transition>
          </div>
        </section>
      </Transition>

      <!-- Topics List with Enhanced Cards -->
      <TransitionGroup
        :name="viewMode === 'list' ? 'topic-list' : 'topic-grid'"
        tag="div"
        :class="['topics-container', viewMode === 'compact' ? 'compact-view' : 'list-view']"
        @before-leave="beforeLeave"
      >
        <article
          v-for="(topic, index) in displayedTopics"
          :key="topic.id"
          class="topic-card-wrapper"
          :style="{ '--delay': `${index * 50}ms` }"
          @mouseenter="handleTopicHover($event, topic)"
          @mouseleave="handleTopicLeave"
        >
          <div
            :class="['topic-card', 'glass-morphism', { 'compact': viewMode === 'compact' }]"
            @click="router.push(`/forum/topic/${topic.id}`)"
          >
            <!-- Hover Glow Effect -->
            <div class="card-glow"></div>
            <div class="card-border-glow"></div>

            <!-- Hot/Trending Indicator -->
            <Transition name="trending-pulse">
              <div v-if="topic.isHot" class="trending-indicator">
                <div class="trending-flame">
                  <FlameIcon class="w-4 h-4" />
                </div>
                <span class="trending-text">Trend</span>
              </div>
            </Transition>

            <!-- Card Content -->
            <div class="card-inner">
              <!-- Left Section: Author Avatar -->
              <div v-if="viewMode === 'list'" class="topic-author-section">
                <div class="author-avatar-wrapper">
                  <n-avatar
                    round
                    :size="56"
                    :src="topic.authorAvatar"
                    class="author-avatar"
                  />
                  <div class="avatar-status" :class="{ online: topic.authorOnline }">
                    <span class="status-pulse"></span>
                  </div>
                  <div class="avatar-ring"></div>
                </div>

                <!-- Animated Badges -->
                <div class="topic-badges">
                  <Transition name="badge-pop">
                    <div v-if="topic.isPinned" class="badge badge-pinned">
                      <PinIcon class="w-3 h-3" />
                      <span>Sabit</span>
                    </div>
                  </Transition>
                  <Transition name="badge-pop">
                    <div v-if="topic.isLocked" class="badge badge-locked">
                      <LockIcon class="w-3 h-3" />
                      <span>Kilitli</span>
                    </div>
                  </Transition>
                  <Transition name="badge-pop">
                    <div v-if="topic.isHot" class="badge badge-hot">
                      <FlameIcon class="w-3 h-3" />
                      <span>Populer</span>
                    </div>
                  </Transition>
                </div>
              </div>

              <!-- Main Content -->
              <div class="topic-main">
                <div class="topic-header">
                  <!-- Topic Type Badge -->
                  <div class="topic-type-badges">
                    <span :class="['type-badge', `type-${topic.type || 'discussion'}`]">
                      <component :is="getTypeIcon(topic.type)" class="w-3 h-3" />
                      {{ getTypeLabel(topic.type) }}
                    </span>
                    <span v-if="topic.isPinned && viewMode === 'compact'" class="compact-badge pinned">
                      <PinIcon class="w-3 h-3" />
                    </span>
                    <span v-if="topic.isLocked && viewMode === 'compact'" class="compact-badge locked">
                      <LockIcon class="w-3 h-3" />
                    </span>
                  </div>

                  <h3 class="topic-title">{{ topic.title }}</h3>
                  <div class="topic-meta">
                    <span class="meta-item author-meta">
                      <n-avatar v-if="viewMode === 'compact'" round :size="20" :src="topic.authorAvatar" class="meta-avatar" />
                      <UserIcon v-else class="w-3.5 h-3.5" />
                      <span class="author-name-link">{{ topic.author }}</span>
                    </span>
                    <span class="meta-divider"></span>
                    <span class="meta-item">
                      <ClockIcon class="w-3.5 h-3.5" />
                      {{ topic.created }}
                    </span>
                  </div>
                </div>

                <!-- Topic Preview (on hover) -->
                <Transition name="preview-expand">
                  <div v-if="hoveredTopic === topic.id && topic.preview && viewMode === 'list'" class="topic-preview">
                    <p>{{ topic.preview }}</p>
                  </div>
                </Transition>

                <!-- Topic Stats -->
                <div class="topic-stats">
                  <div class="stat" title="Yanitlar">
                    <MessageSquareIcon class="w-4 h-4" />
                    <span class="stat-value">{{ topic.replies }}</span>
                    <span v-if="viewMode === 'list'" class="stat-label">Yanit</span>
                  </div>
                  <div class="stat" title="Goruntulenme">
                    <EyeIcon class="w-4 h-4" />
                    <span class="stat-value">{{ formatNumber(topic.views) }}</span>
                    <span v-if="viewMode === 'list'" class="stat-label">Goruntulenme</span>
                  </div>
                  <div class="stat" title="Begeni">
                    <ThumbsUpIcon class="w-4 h-4" />
                    <span class="stat-value">{{ topic.likes }}</span>
                    <span v-if="viewMode === 'list'" class="stat-label">Begeni</span>
                  </div>
                </div>
              </div>

              <!-- Last Reply Section -->
              <div v-if="viewMode === 'list'" class="topic-last-reply">
                <template v-if="topic.lastReply">
                  <div class="last-reply-header">
                    <span class="last-reply-label">Son Yanit</span>
                    <span class="last-reply-time">{{ topic.lastReply.time }}</span>
                  </div>
                  <div class="last-reply-author">
                    <n-avatar round :size="28" :src="topic.lastReply.avatar" />
                    <span class="author-name">{{ topic.lastReply.author }}</span>
                  </div>
                </template>
                <template v-else>
                  <div class="no-reply">
                    <MessageSquareIcon class="w-5 h-5 text-gray-500" />
                    <span>Henuz yanit yok</span>
                  </div>
                </template>

                <!-- Arrow Indicator -->
                <div class="arrow-indicator">
                  <ArrowRightIcon class="w-5 h-5" />
                </div>
              </div>
            </div>

            <!-- Progress Bar (for popular topics) -->
            <div v-if="topic.isHot" class="popularity-bar">
              <div class="bar-fill" :style="{ width: `${Math.min(topic.views / 5, 100)}%` }"></div>
              <div class="bar-shine"></div>
            </div>
          </div>
        </article>
      </TransitionGroup>

      <!-- Loading Indicator for Infinite Scroll -->
      <Transition name="fade">
        <div v-if="infiniteScrollEnabled && isLoadingMore" class="loading-more">
          <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
          </div>
          <span>Daha fazla konu yukleniyor...</span>
        </div>
      </Transition>

      <!-- Scroll Sentinel for Infinite Scroll -->
      <div v-if="infiniteScrollEnabled" ref="scrollSentinel" class="scroll-sentinel"></div>

      <!-- Enhanced Empty State -->
      <Transition name="empty-bounce" appear>
        <section v-if="filteredTopics.length === 0" class="empty-state">
          <div class="empty-card glass-morphism">
            <div class="empty-illustration">
              <div class="empty-icon-wrapper">
                <div class="empty-icon-bg"></div>
                <MessageSquareIcon class="w-16 h-16" />
              </div>
              <div class="empty-circles">
                <div class="circle"></div>
                <div class="circle"></div>
                <div class="circle"></div>
              </div>
              <div class="empty-particles">
                <span v-for="n in 12" :key="n" class="particle" :style="{ '--i': n }"></span>
              </div>
            </div>

            <h3 class="empty-title">Henuz Konu Yok</h3>
            <p class="empty-description">
              Bu kategoride henuz bir konu acilmamis. Ilk konuyu acarak tartismayi baslatin!
            </p>

            <div class="empty-actions">
              <n-button type="primary" size="large" class="empty-cta" @click="showNewTopicModal = true">
                <template #icon><PlusCircleIcon class="w-5 h-5" /></template>
                Ilk Konuyu Ac
              </n-button>
              <n-button quaternary size="large" @click="router.push('/forum')">
                <template #icon><ArrowLeftIcon class="w-5 h-5" /></template>
                Foruma Don
              </n-button>
            </div>

            <div class="empty-suggestions">
              <p class="suggestions-title">Populer Kategoriler</p>
              <div class="suggestions-list">
                <button class="suggestion-chip" v-for="cat in popularCategories" :key="cat.id" @click="router.push(`/forum/category/${cat.id}`)">
                  <component :is="cat.icon" class="w-4 h-4" />
                  {{ cat.name }}
                </button>
              </div>
            </div>
          </div>
        </section>
      </Transition>

      <!-- Animated Pagination -->
      <Transition name="pagination-slide" appear>
        <section v-if="!infiniteScrollEnabled && filteredTopics.length > 0" class="pagination-section">
          <div class="pagination-wrapper glass-morphism">
            <button
              class="pagination-btn prev"
              :disabled="currentPage === 1"
              @click="changePage(currentPage - 1)"
            >
              <ChevronLeftIcon class="w-5 h-5" />
              <span>Onceki</span>
            </button>

            <div class="pagination-numbers">
              <TransitionGroup name="page-number">
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  :class="['page-btn', { active: page === currentPage, ellipsis: page === '...' }]"
                  :disabled="page === '...'"
                  @click="page !== '...' && changePage(page)"
                >
                  <span class="page-number-text">{{ page }}</span>
                  <span v-if="page === currentPage" class="page-active-bg"></span>
                </button>
              </TransitionGroup>
            </div>

            <button
              class="pagination-btn next"
              :disabled="currentPage === totalPages"
              @click="changePage(currentPage + 1)"
            >
              <span>Sonraki</span>
              <ChevronRightIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="pagination-info">
            <div class="page-info-box">
              <span class="current-range">{{ (currentPage - 1) * itemsPerPage + 1 }}-{{ Math.min(currentPage * itemsPerPage, filteredTopics.length) }}</span>
              <span class="info-separator">/</span>
              <span class="total-count">{{ filteredTopics.length }}</span>
            </div>
            <span class="info-text">konu gosteriliyor</span>
            <div class="page-progress">
              <div class="progress-fill" :style="{ width: `${(currentPage / totalPages) * 100}%` }"></div>
            </div>
          </div>
        </section>
      </Transition>
    </div>

    <!-- Enhanced New Topic Modal -->
    <n-modal
      v-model:show="showNewTopicModal"
      :mask-closable="false"
      class="topic-modal"
    >
      <div class="modal-content glass-morphism">
        <div class="modal-header">
          <div class="modal-icon">
            <EditIcon class="w-6 h-6 text-orange-500" />
          </div>
          <div>
            <h2 class="modal-title">Yeni Konu Olustur</h2>
            <p class="modal-subtitle">Topluluga paylasmak istediginiz konuyu yazin</p>
          </div>
          <button class="modal-close" @click="showNewTopicModal = false">
            <XIcon class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="createTopic" class="modal-form">
          <!-- Topic Type Selection -->
          <div class="form-group">
            <label class="form-label">
              <TagIcon class="w-4 h-4" />
              Konu Tipi
            </label>
            <div class="topic-type-selector">
              <button
                v-for="type in topicTypes"
                :key="type.value"
                type="button"
                :class="['type-option', { active: newTopic.type === type.value }]"
                @click="newTopic.type = type.value"
              >
                <component :is="type.icon" class="w-4 h-4" />
                <span>{{ type.label }}</span>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">
              <TypeIcon class="w-4 h-4" />
              Konu Basligi
            </label>
            <div class="input-wrapper">
              <input
                v-model="newTopic.title"
                type="text"
                placeholder="Dikkat cekici bir baslik girin..."
                class="form-input"
                :class="{ error: titleError }"
              />
              <span class="char-count" :class="{ warning: newTopic.title.length > 80 }">{{ newTopic.title.length }}/100</span>
            </div>
            <Transition name="error-shake">
              <p v-if="titleError" class="error-text">{{ titleError }}</p>
            </Transition>
          </div>

          <div class="form-group">
            <label class="form-label">
              <FileTextIcon class="w-4 h-4" />
              Icerik
            </label>
            <div class="textarea-wrapper">
              <textarea
                v-model="newTopic.content"
                placeholder="Konu iceriginizi detayli bir sekilde aciklayin..."
                class="form-textarea"
                :class="{ error: contentError }"
                rows="8"
              ></textarea>
              <span class="char-count" :class="{ warning: newTopic.content.length > 4500 }">{{ newTopic.content.length }}/5000</span>
            </div>
            <Transition name="error-shake">
              <p v-if="contentError" class="error-text">{{ contentError }}</p>
            </Transition>
          </div>

          <div class="form-group">
            <label class="form-label">
              <HashIcon class="w-4 h-4" />
              Etiketler (Opsiyonel)
            </label>
            <div class="tags-input">
              <TransitionGroup name="tag-pop" tag="div" class="tags-list">
                <span v-for="tag in newTopic.tags" :key="tag" class="tag">
                  {{ tag }}
                  <button type="button" @click="removeTag(tag)">
                    <XIcon class="w-3 h-3" />
                  </button>
                </span>
              </TransitionGroup>
              <input
                v-model="tagInput"
                type="text"
                placeholder="Etiket ekle..."
                class="tag-input"
                @keydown.enter.prevent="addTag"
                @keydown.comma.prevent="addTag"
              />
            </div>
            <p class="form-hint">Enter veya virgul ile etiket ekleyin (max 5)</p>
          </div>
        </form>

        <div class="modal-footer">
          <n-button quaternary size="large" @click="showNewTopicModal = false">
            Iptal
          </n-button>
          <n-button
            type="primary"
            size="large"
            :loading="isCreating"
            @click="createTopic"
          >
            <template #icon><SendIcon class="w-5 h-5" /></template>
            Konuyu Olustur
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- Quick Preview Tooltip -->
    <Teleport to="body">
      <Transition name="preview-tooltip">
        <div
          v-if="previewTooltip.show && viewMode === 'list'"
          class="preview-tooltip glass-morphism"
          :style="{ top: `${previewTooltip.y}px`, left: `${previewTooltip.x}px` }"
        >
          <div class="preview-header">
            <span :class="['preview-type-badge', `type-${previewTooltip.topic?.type || 'discussion'}`]">
              <component :is="getTypeIcon(previewTooltip.topic?.type)" class="w-3 h-3" />
              {{ getTypeLabel(previewTooltip.topic?.type) }}
            </span>
            <span class="preview-title">{{ previewTooltip.topic?.title }}</span>
          </div>
          <p class="preview-text">{{ previewTooltip.topic?.preview }}</p>
          <div class="preview-stats">
            <span><MessageSquareIcon class="w-3.5 h-3.5" /> {{ previewTooltip.topic?.replies }}</span>
            <span><EyeIcon class="w-3.5 h-3.5" /> {{ previewTooltip.topic?.views }}</span>
            <span><ThumbsUpIcon class="w-3.5 h-3.5" /> {{ previewTooltip.topic?.likes }}</span>
          </div>
          <div class="preview-footer">
            <span>Tiklayarak konuyu goruntuleyin</span>
            <ArrowRightIcon class="w-4 h-4" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeIcon,
  MessageSquareIcon,
  FileTextIcon,
  PlusCircleIcon,
  SearchIcon,
  UserIcon,
  UsersIcon,
  ClockIcon,
  PinIcon,
  LockIcon,
  EyeIcon,
  ThumbsUpIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  ChevronDownIcon,
  SendIcon,
  XIcon,
  FolderIcon,
  FlameIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  ArrowUpDownIcon,
  EditIcon,
  TypeIcon,
  TagIcon,
  HashIcon,
  TrendingUpIcon,
  CalendarIcon,
  StarIcon,
  HelpCircleIcon,
  ShieldIcon,
  ZapIcon,
  ListIcon,
  LayoutGridIcon,
  CheckIcon,
  InfinityIcon,
  LayersIcon,
  MessageCircleQuestionIcon,
  MegaphoneIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const categoryId = route.params.id

// Refs
const searchQuery = ref('')
const searchFocused = ref(false)
const sortBy = ref('latest')
const sortDropdownOpen = ref(false)
const viewMode = ref('list')
const showNewTopicModal = ref(false)
const currentPage = ref(1)
const itemsPerPage = ref(10)
const infiniteScrollEnabled = ref(false)
const isLoadingMore = ref(false)
const loadedItems = ref(10)
const hoveredTopic = ref(null)
const scrollSentinel = ref(null)
const isCreating = ref(false)
const tagInput = ref('')
const titleError = ref('')
const contentError = ref('')
const onlineUsers = ref(23)

// Preview tooltip state
const previewTooltip = reactive({
  show: false,
  x: 0,
  y: 0,
  topic: null
})

// Topic types
const topicTypes = [
  { value: 'discussion', label: 'Tartisma', icon: MessageSquareIcon },
  { value: 'question', label: 'Soru', icon: MessageCircleQuestionIcon },
  { value: 'announcement', label: 'Duyuru', icon: MegaphoneIcon }
]

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

// Sort options with icons
const sortOptions = [
  { label: 'En Yeni', value: 'latest', icon: CalendarIcon },
  { label: 'Populer', value: 'popular', icon: TrendingUpIcon },
  { label: 'En Cok Yanit', value: 'mostReplies', icon: MessageSquareIcon },
  { label: 'En Eski', value: 'oldest', icon: ClockIcon }
]

const currentSortOption = computed(() => {
  return sortOptions.find(o => o.value === sortBy.value) || sortOptions[0]
})

// Category data
const category = ref({
  id: 1,
  name: 'Genel Tartisma',
  description: 'CS 1.6 hakkinda genel konular, sorular ve paylasimlar icin acik tartisma alani',
  icon: MessageSquareIcon,
  gradient: 'primary-secondary'
})

// Category stats computed
const categoryStats = computed(() => [
  { label: 'Konu', value: topics.value.length, icon: FileTextIcon },
  { label: 'Gonderi', value: totalPosts.value, icon: MessageSquareIcon },
  { label: 'Uye', value: 156, icon: UserIcon },
  { label: 'Goruntulenme', value: totalViews.value, icon: EyeIcon }
])

// Popular categories for empty state
const popularCategories = [
  { id: 1, name: 'Genel Tartisma', icon: MessageSquareIcon },
  { id: 2, name: 'Sorular & Cevaplar', icon: HelpCircleIcon },
  { id: 3, name: 'Duyurular', icon: ZapIcon },
  { id: 4, name: 'Kurallar', icon: ShieldIcon }
]

// Format number utility
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num
}

// Get type icon
const getTypeIcon = (type) => {
  const icons = {
    discussion: MessageSquareIcon,
    question: MessageCircleQuestionIcon,
    announcement: MegaphoneIcon
  }
  return icons[type] || MessageSquareIcon
}

// Get type label
const getTypeLabel = (type) => {
  const labels = {
    discussion: 'Tartisma',
    question: 'Soru',
    announcement: 'Duyuru'
  }
  return labels[type] || 'Tartisma'
}

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

// Topics data
const topics = ref([
  {
    id: 1,
    title: 'Yeni guncelleme hakkinda dusunceleriniz?',
    author: 'Player123',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
    authorOnline: true,
    created: '2 saat once',
    replies: 45,
    views: 234,
    likes: 12,
    isPinned: true,
    isLocked: false,
    isHot: true,
    type: 'discussion',
    preview: 'Yeni guncelleme ile gelen degisiklikler hakkinda goruslerinizi paylasalim. Ozellikle silah dengesi ve harita degisiklikleri...',
    lastReply: {
      author: 'AdminUser',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a1',
      time: '5 dakika once'
    }
  },
  {
    id: 2,
    title: 'En iyi CS 1.6 map onerileriniz',
    author: 'ProGamer',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    authorOnline: false,
    created: '5 saat once',
    replies: 28,
    views: 156,
    likes: 8,
    isPinned: false,
    isLocked: false,
    isHot: false,
    type: 'question',
    preview: 'Klasiklerin disinda oynamasi keyifli map onerilerinizi bekliyorum. AWP haritalari, aim haritalari dahil...',
    lastReply: {
      author: 'MapMaster',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a2',
      time: '1 saat once'
    }
  },
  {
    id: 3,
    title: '[DUYURU] Forum Kurallari - Lutfen Okuyun',
    author: 'AdminUser',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    authorOnline: true,
    created: '1 hafta once',
    replies: 0,
    views: 489,
    likes: 23,
    isPinned: true,
    isLocked: true,
    isHot: false,
    type: 'announcement',
    preview: 'Forum kurallari ve topluluk rehberi. Tum uyelerimizin okumasi zorunludur. Kurallara uymayan icerikler silinecektir.',
    lastReply: null
  },
  {
    id: 4,
    title: 'AWP kullanim taktikleri',
    author: 'SniperKing',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
    authorOnline: false,
    created: '1 gun once',
    replies: 67,
    views: 423,
    likes: 31,
    isPinned: false,
    isLocked: false,
    isHot: true,
    type: 'discussion',
    preview: 'AWP ile profesyonel seviyede oynamak icin bilmeniz gereken taktikler, pozisyonlar ve ipuclari...',
    lastReply: {
      author: 'NewbieCS',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a4',
      time: '30 dakika once'
    }
  },
  {
    id: 5,
    title: 'Yeni baslayanlar icin rehber',
    author: 'GuideWriter',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=5',
    authorOnline: true,
    created: '3 gun once',
    replies: 34,
    views: 567,
    likes: 45,
    isPinned: false,
    isLocked: false,
    isHot: false,
    type: 'discussion',
    preview: 'CS 1.6\'ya yeni baslayanlar icin kapsamli bir rehber hazirladim. Temel ayarlar, silah secimi, takim calismasi...',
    lastReply: {
      author: 'Newbie2024',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a5',
      time: '2 saat once'
    }
  },
  {
    id: 6,
    title: 'Klan araniyor - Rekabetci oyuncular',
    author: 'CompetitivePlayer',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=6',
    authorOnline: false,
    created: '4 gun once',
    replies: 12,
    views: 189,
    likes: 5,
    isPinned: false,
    isLocked: false,
    isHot: false,
    type: 'question',
    preview: 'Aktif ve rekabetci bir klan ariyorum. 5+ yil CS deneyimim var. Turnuva tecribem mevcut...',
    lastReply: {
      author: 'ClanLeader',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=a6',
      time: '5 saat once'
    }
  }
])

// Computed values
const totalPosts = computed(() => {
  return topics.value.reduce((sum, topic) => sum + topic.replies + 1, 0)
})

const totalViews = computed(() => {
  return topics.value.reduce((sum, topic) => sum + topic.views, 0)
})

const filteredTopics = computed(() => {
  let filtered = [...topics.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.title.toLowerCase().includes(query) ||
      t.author.toLowerCase().includes(query) ||
      t.preview?.toLowerCase().includes(query)
    )
  }

  // Always show pinned topics first
  const pinned = filtered.filter(t => t.isPinned)
  const unpinned = filtered.filter(t => !t.isPinned)

  // Sort unpinned topics
  if (sortBy.value === 'latest') {
    unpinned.sort((a, b) => b.id - a.id)
  } else if (sortBy.value === 'popular') {
    unpinned.sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'mostReplies') {
    unpinned.sort((a, b) => b.replies - a.replies)
  } else if (sortBy.value === 'oldest') {
    unpinned.sort((a, b) => a.id - b.id)
  }

  return [...pinned, ...unpinned]
})

const displayedTopics = computed(() => {
  if (infiniteScrollEnabled.value) {
    return filteredTopics.value.slice(0, loadedItems.value)
  }
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredTopics.value.slice(start, start + itemsPerPage.value)
})

const totalPages = computed(() => {
  return Math.ceil(filteredTopics.value.length / itemsPerPage.value)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')

    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)

    for (let i = start; i <= end; i++) pages.push(i)

    if (current < total - 2) pages.push('...')
    pages.push(total)
  }

  return pages
})

// New topic form
const newTopic = reactive({
  title: '',
  content: '',
  tags: [],
  type: 'discussion'
})

// Methods
const handleSortChange = (value) => {
  sortBy.value = value
  sortDropdownOpen.value = false
  currentPage.value = 1
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const handleTopicHover = (event, topic) => {
  hoveredTopic.value = topic.id

  // Update tooltip position
  const rect = event.currentTarget.getBoundingClientRect()
  previewTooltip.x = rect.right + 16
  previewTooltip.y = rect.top
  previewTooltip.topic = topic

  // Show tooltip after a small delay
  setTimeout(() => {
    if (hoveredTopic.value === topic.id) {
      previewTooltip.show = true
    }
  }, 300)
}

const handleTopicLeave = () => {
  hoveredTopic.value = null
  previewTooltip.show = false
}

const beforeLeave = (el) => {
  const { marginLeft, marginTop, width, height } = window.getComputedStyle(el)
  el.style.left = `${el.offsetLeft - parseFloat(marginLeft)}px`
  el.style.top = `${el.offsetTop - parseFloat(marginTop)}px`
  el.style.width = width
  el.style.height = height
}

const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !newTopic.tags.includes(tag) && newTopic.tags.length < 5) {
    newTopic.tags.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (tag) => {
  const index = newTopic.tags.indexOf(tag)
  if (index > -1) {
    newTopic.tags.splice(index, 1)
  }
}

const validateForm = () => {
  titleError.value = ''
  contentError.value = ''

  if (!newTopic.title || newTopic.title.trim().length < 5) {
    titleError.value = 'Baslik en az 5 karakter olmalidir'
    return false
  }
  if (newTopic.title.length > 100) {
    titleError.value = 'Baslik 100 karakterden uzun olamaz'
    return false
  }
  if (!newTopic.content || newTopic.content.trim().length < 20) {
    contentError.value = 'Icerik en az 20 karakter olmalidir'
    return false
  }
  if (newTopic.content.length > 5000) {
    contentError.value = 'Icerik 5000 karakterden uzun olamaz'
    return false
  }
  return true
}

const createTopic = async () => {
  if (!validateForm()) return

  isCreating.value = true

  try {
    const response = await fetch('/api/forum/topics', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        category_id: categoryId,
        title: newTopic.title.trim(),
        content: newTopic.content.trim(),
        tags: newTopic.tags,
        type: newTopic.type
      })
    })

    if (response.ok) {
      showNewTopicModal.value = false
      newTopic.title = ''
      newTopic.content = ''
      newTopic.tags = []
      newTopic.type = 'discussion'
      window.$message?.success('Konu basariyla olusturuldu')
      router.go(0)
    } else {
      const error = await response.json()
      window.$message?.error(error.detail || 'Konu olusturulamadi')
    }
  } catch (error) {
    window.$message?.error('Bir hata olustu, lutfen tekrar deneyin')
  } finally {
    isCreating.value = false
  }
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (sortDropdownOpen.value && !event.target.closest('.sort-dropdown')) {
    sortDropdownOpen.value = false
  }
}

// Infinite scroll observer
let observer = null

const setupInfiniteScroll = () => {
  if (!scrollSentinel.value) return

  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && !isLoadingMore.value) {
        loadMoreTopics()
      }
    },
    { threshold: 0.1 }
  )

  observer.observe(scrollSentinel.value)
}

const loadMoreTopics = async () => {
  if (loadedItems.value >= filteredTopics.value.length) return

  isLoadingMore.value = true

  // Simulate loading delay
  await new Promise(resolve => setTimeout(resolve, 500))

  loadedItems.value += 5
  isLoadingMore.value = false
}

// Watchers
watch(infiniteScrollEnabled, async (enabled) => {
  if (enabled) {
    loadedItems.value = 10
    await nextTick()
    setupInfiniteScroll()
  } else if (observer) {
    observer.disconnect()
    observer = null
  }
})

watch(searchQuery, () => {
  currentPage.value = 1
  loadedItems.value = 10
})

// Lifecycle
onMounted(() => {
  if (infiniteScrollEnabled.value) {
    setupInfiniteScroll()
  }
  document.addEventListener('click', handleClickOutside)

  // Simulate online users change
  setInterval(() => {
    onlineUsers.value = Math.floor(Math.random() * 10) + 20
  }, 30000)
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Base Animations */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.05); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes ring-pulse {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.5); opacity: 0; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(249, 115, 22, 0.3); }
  50% { box-shadow: 0 0 40px rgba(249, 115, 22, 0.5); }
}

@keyframes particle-float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 0;
  }
  25% {
    opacity: 1;
  }
  75% {
    opacity: 1;
  }
  100% {
    transform: translate(calc(cos(var(--i) * 60deg) * 50px), calc(sin(var(--i) * 60deg) * 50px)) rotate(360deg);
    opacity: 0;
  }
}

@keyframes online-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.5; }
}

@keyframes trending-glow {
  0%, 100% { filter: drop-shadow(0 0 5px rgba(251, 146, 60, 0.5)); }
  50% { filter: drop-shadow(0 0 15px rgba(251, 146, 60, 0.8)); }
}

@keyframes shine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes orb-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(10px, -10px) scale(1.05); }
  50% { transform: translate(0, -20px) scale(1); }
  75% { transform: translate(-10px, -10px) scale(0.95); }
}

.delay-500 { animation-delay: 0.5s; }
.delay-1000 { animation-delay: 1s; }

/* Background Elements */
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  animation: orb-float 8s ease-in-out infinite;
}

.bg-orb-1 {
  top: -100px;
  right: -100px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.15) 0%, transparent 70%);
  animation-delay: 0s;
}

.bg-orb-2 {
  bottom: -150px;
  left: -150px;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
  animation-delay: -3s;
}

.bg-orb-3 {
  top: 50%;
  left: 50%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.08) 0%, transparent 70%);
  animation-delay: -5s;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(ellipse at center, black 20%, transparent 70%);
}

/* Glass Morphism */
.glass-morphism {
  background: rgba(17, 17, 17, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

/* Breadcrumb Styles */
.breadcrumb-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(17, 17, 17, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.breadcrumb-inner {
  display: flex;
  align-items: center;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  color: #9ca3af;
  transition: all 0.3s ease;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
}

.breadcrumb-item:hover {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}

.breadcrumb-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 6px;
  margin-right: 8px;
  transition: all 0.3s ease;
}

.breadcrumb-item:hover .breadcrumb-icon-wrapper {
  background: rgba(249, 115, 22, 0.2);
  transform: scale(1.1);
}

.breadcrumb-text {
  font-weight: 500;
}

.breadcrumb-arrow {
  display: flex;
  align-items: center;
  margin-left: 8px;
  color: #4b5563;
  transition: all 0.3s ease;
}

.breadcrumb-item:hover .breadcrumb-arrow {
  color: #f97316;
  transform: translateX(4px);
}

.breadcrumb-current {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.current-icon-pulse {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(249, 115, 22, 0.2) 0%, transparent 70%);
  animation: pulse-slow 2s ease-in-out infinite;
}

/* Online Users Indicator */
.online-users-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 20px;
  font-size: 0.85rem;
  color: #22c55e;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: online-pulse 2s ease-in-out infinite;
}

.online-count {
  font-weight: 700;
}

.online-label {
  color: #9ca3af;
  font-size: 0.75rem;
}

/* Hero Section */
.category-hero {
  position: relative;
  padding: 40px;
  border-radius: 24px;
  overflow: hidden;
  background: rgba(17, 17, 17, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  animation: fadeInUp 0.6s ease forwards;
}

.hero-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, transparent 50%, rgba(139, 92, 246, 0.1) 100%);
}

.hero-pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle at 2px 2px, rgba(255, 255, 255, 0.05) 1px, transparent 0);
  background-size: 32px 32px;
}

.hero-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
  animation: shine 8s ease-in-out infinite;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.category-type-badge,
.topic-count-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  color: #9ca3af;
}

.topic-count-badge {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.2);
}

.category-icon-wrapper {
  position: relative;
  flex-shrink: 0;
}

.category-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  box-shadow: 0 10px 30px rgba(249, 115, 22, 0.3);
  animation: glow-pulse 3s ease-in-out infinite;
}

.icon-ring {
  position: absolute;
  inset: -8px;
  border: 2px solid rgba(249, 115, 22, 0.3);
  border-radius: 28px;
  animation: ring-pulse 2s ease-out infinite;
}

.icon-particles {
  position: absolute;
  inset: -20px;
  pointer-events: none;
}

.icon-particles .particle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 4px;
  height: 4px;
  background: #f97316;
  border-radius: 50%;
  animation: particle-float 3s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.5s);
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 8px;
  line-height: 1.2;
}

.title-gradient {
  background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #f97316 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s linear infinite;
}

.hero-description {
  color: #9ca3af;
  font-size: 1rem;
  max-width: 600px;
  line-height: 1.6;
}

.stats-overlay {
  display: flex;
  gap: 24px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  animation-fill-mode: forwards;
}

.stat-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 10px;
  color: #f97316;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  color: #6b7280;
  font-size: 0.75rem;
}

.hero-action {
  flex-shrink: 0;
}

.new-topic-btn {
  padding: 14px 28px !important;
  font-weight: 600 !important;
  border-radius: 14px !important;
  background: linear-gradient(135deg, #f97316, #ea580c) !important;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4) !important;
  transition: all 0.3s ease !important;
  position: relative;
  overflow: hidden;
}

.new-topic-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.new-topic-btn:hover::before {
  left: 100%;
}

.new-topic-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(249, 115, 22, 0.5) !important;
}

/* Filter Section */
.filter-section {
  position: relative;
  animation: fadeInUp 0.5s ease 0.2s forwards;
  opacity: 0;
  animation-fill-mode: forwards;
}

.filter-card {
  padding: 20px 24px;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
}

.search-wrapper.focused .search-glow {
  opacity: 1;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: #6b7280;
  z-index: 1;
  transition: color 0.3s ease;
}

.search-wrapper.focused .search-icon {
  color: #f97316;
}

.search-input {
  width: 100%;
  padding: 14px 44px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: rgba(249, 115, 22, 0.5);
  background: rgba(249, 115, 22, 0.05);
}

.search-input::placeholder {
  color: #6b7280;
}

.search-glow {
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.3), rgba(139, 92, 246, 0.2));
  border-radius: 14px;
  opacity: 0;
  z-index: -1;
  filter: blur(8px);
  transition: opacity 0.3s ease;
}

.search-clear {
  position: absolute;
  right: 12px;
  padding: 6px;
  color: #6b7280;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.search-clear:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

/* View Mode Toggle */
.view-mode-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  position: relative;
}

.view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  color: #6b7280;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.view-btn:hover {
  color: #9ca3af;
}

.view-btn.active {
  color: #f97316;
}

.view-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 36px;
  height: 36px;
  background: rgba(249, 115, 22, 0.15);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 8px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.view-indicator.compact {
  transform: translateX(40px);
}

/* Sort Dropdown */
.sort-wrapper {
  flex-shrink: 0;
}

.sort-dropdown {
  position: relative;
}

.sort-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.sort-trigger:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.dropdown-arrow {
  transition: transform 0.3s ease;
}

.sort-dropdown.open .dropdown-arrow {
  transform: rotate(180deg);
}

.sort-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 180px;
  padding: 8px;
  z-index: 100;
}

.sort-option {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  color: #9ca3af;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.sort-option:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.sort-option.active {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.check-icon {
  margin-left: auto;
}

/* Infinite Scroll Toggle */
.infinite-scroll-toggle {
  flex-shrink: 0;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.toggle-text {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #9ca3af;
  font-size: 0.875rem;
  white-space: nowrap;
}

.toggle-switch {
  position: relative;
  width: 52px;
  height: 28px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  transition: background 0.3s ease;
  overflow: hidden;
}

.toggle-switch.active {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.toggle-input {
  opacity: 0;
  position: absolute;
  inset: 0;
  cursor: pointer;
}

.toggle-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-switch.active .toggle-slider {
  transform: translateX(24px);
}

.slider-dot {
  width: 8px;
  height: 8px;
  background: #6b7280;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.toggle-switch.active .slider-dot {
  background: #f97316;
}

/* Active Filters */
.active-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.filters-label {
  color: #6b7280;
  font-size: 0.8rem;
}

.filters-list {
  display: flex;
  gap: 8px;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 6px;
  color: #f97316;
  font-size: 0.8rem;
}

.filter-tag button {
  display: flex;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.filter-tag button:hover {
  opacity: 1;
}

/* Topics Container */
.topics-container {
  position: relative;
}

.topics-container.list-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.topics-container.compact-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.topic-card-wrapper {
  animation: fadeInUp 0.4s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

/* Topic Card */
.topic-card {
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.topic-card:hover {
  transform: translateY(-4px);
  border-color: rgba(249, 115, 22, 0.3);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(249, 115, 22, 0.2);
}

.card-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(249, 115, 22, 0.15) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.topic-card:hover .card-glow {
  opacity: 1;
}

.card-border-glow {
  position: absolute;
  inset: -1px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.5), transparent, rgba(139, 92, 246, 0.3));
  border-radius: 17px;
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s ease;
}

.topic-card:hover .card-border-glow {
  opacity: 1;
}

/* Trending Indicator */
.trending-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(239, 68, 68, 0.1));
  border: 1px solid rgba(251, 146, 60, 0.3);
  border-radius: 20px;
  z-index: 2;
}

.trending-flame {
  display: flex;
  color: #fb923c;
  animation: trending-glow 1.5s ease-in-out infinite;
}

.trending-text {
  font-size: 0.7rem;
  font-weight: 700;
  color: #fb923c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-inner {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 20px;
  padding: 24px;
  position: relative;
}

.topic-card.compact .card-inner {
  grid-template-columns: 1fr;
  gap: 12px;
  padding: 20px;
}

/* Author Section */
.topic-author-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.author-avatar-wrapper {
  position: relative;
}

.author-avatar {
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.topic-card:hover .author-avatar {
  border-color: rgba(249, 115, 22, 0.5);
}

.avatar-ring {
  position: absolute;
  inset: -4px;
  border: 2px solid rgba(249, 115, 22, 0);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.topic-card:hover .avatar-ring {
  border-color: rgba(249, 115, 22, 0.3);
  transform: scale(1.1);
}

.avatar-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 14px;
  height: 14px;
  background: #6b7280;
  border: 3px solid #111;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-status.online {
  background: #22c55e;
}

.status-pulse {
  position: absolute;
  inset: 0;
  background: #22c55e;
  border-radius: 50%;
  animation: online-pulse 2s ease-in-out infinite;
}

/* Badges */
.topic-badges {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-pinned {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.3);
  animation: glow-pulse 2s ease-in-out infinite;
}

.badge-locked {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-hot {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(251, 146, 60, 0.1));
  color: #fb923c;
  border: 1px solid rgba(251, 146, 60, 0.3);
}

.compact-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
}

.compact-badge.pinned {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.compact-badge.locked {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Topic Type Badges */
.topic-type-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.type-discussion {
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(96, 165, 250, 0.3);
}

.type-question {
  background: rgba(167, 139, 250, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(167, 139, 250, 0.3);
}

.type-announcement {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

/* Topic Main Content */
.topic-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.topic-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.topic-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.4;
  transition: color 0.3s ease;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.topic-card:hover .topic-title {
  color: #f97316;
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 0.8rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.author-meta {
  transition: color 0.2s ease;
}

.author-meta:hover {
  color: #f97316;
}

.author-name-link {
  font-weight: 500;
}

.meta-avatar {
  margin-right: 2px;
}

.meta-divider {
  width: 4px;
  height: 4px;
  background: #4b5563;
  border-radius: 50%;
}

/* Topic Preview */
.topic-preview {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border-left: 3px solid #f97316;
}

.topic-preview p {
  color: #9ca3af;
  font-size: 0.875rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Topic Stats */
.topic-stats {
  display: flex;
  gap: 16px;
}

.topic-card.compact .topic-stats {
  gap: 12px;
}

.topic-stats .stat {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 0.85rem;
  transition: color 0.3s ease;
}

.topic-stats .stat:hover {
  color: #f97316;
}

.topic-stats .stat-value {
  font-weight: 600;
  color: #9ca3af;
}

.topic-stats .stat-label {
  color: #6b7280;
}

/* Last Reply Section */
.topic-last-reply {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 8px;
  min-width: 140px;
  padding-left: 20px;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
}

.last-reply-header {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.last-reply-label {
  font-size: 0.7rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.last-reply-time {
  font-size: 0.8rem;
  color: #9ca3af;
}

.last-reply-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.last-reply-author .author-name {
  font-size: 0.85rem;
  color: #f97316;
  font-weight: 500;
}

.no-reply {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  font-size: 0.8rem;
}

.arrow-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 8px;
  color: #f97316;
  transition: all 0.3s ease;
}

.topic-card:hover .arrow-indicator {
  background: #f97316;
  color: #fff;
  transform: translateX(4px);
}

/* Popularity Bar */
.popularity-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fb923c);
  border-radius: 0 3px 3px 0;
  transition: width 0.5s ease;
  position: relative;
}

.bar-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shine 2s ease-in-out infinite;
}

/* Loading More */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 32px;
  color: #9ca3af;
}

.loading-spinner {
  position: relative;
  width: 32px;
  height: 32px;
}

.spinner-ring {
  position: absolute;
  inset: 0;
  border: 3px solid transparent;
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-ring:nth-child(2) {
  inset: 4px;
  border-top-color: #fb923c;
  animation-duration: 0.8s;
  animation-direction: reverse;
}

.spinner-ring:nth-child(3) {
  inset: 8px;
  border-top-color: #fdba74;
  animation-duration: 0.6s;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.scroll-sentinel {
  height: 1px;
}

/* Empty State */
.empty-state {
  padding: 40px 0;
  animation: fadeInUp 0.6s ease forwards;
}

.empty-card {
  padding: 60px 40px;
  text-align: center;
}

.empty-illustration {
  position: relative;
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.empty-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  color: #f97316;
  animation: float 3s ease-in-out infinite;
  z-index: 1;
}

.empty-icon-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(139, 92, 246, 0.1));
  border-radius: 50%;
}

.empty-circles {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-circles .circle {
  position: absolute;
  border: 2px dashed rgba(249, 115, 22, 0.2);
  border-radius: 50%;
  animation: ring-pulse 3s ease-out infinite;
}

.empty-circles .circle:nth-child(1) { width: 140px; height: 140px; animation-delay: 0s; }
.empty-circles .circle:nth-child(2) { width: 180px; height: 180px; animation-delay: 0.5s; }
.empty-circles .circle:nth-child(3) { width: 220px; height: 220px; animation-delay: 1s; }

.empty-particles {
  position: absolute;
  inset: -30px;
}

.empty-particles .particle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  background: #f97316;
  border-radius: 50%;
  animation: particle-float 4s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.3s);
}

.empty-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.empty-description {
  color: #9ca3af;
  font-size: 1rem;
  max-width: 400px;
  margin: 0 auto 32px;
  line-height: 1.6;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.empty-cta {
  animation: glow-pulse 2s ease-in-out infinite;
}

.empty-suggestions {
  padding-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.suggestions-title {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 16px;
}

.suggestions-list {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  color: #9ca3af;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.suggestion-chip:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
  transform: translateY(-2px);
}

/* Pagination */
.pagination-section {
  margin-top: 40px;
  animation: fadeInUp 0.5s ease 0.3s forwards;
  opacity: 0;
  animation-fill-mode: forwards;
}

.pagination-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #9ca3af;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.pagination-btn:not(:disabled):hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
  transform: translateX(-4px);
}

.pagination-btn.next:not(:disabled):hover {
  transform: translateX(4px);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-numbers {
  display: flex;
  gap: 6px;
}

.page-btn {
  position: relative;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: #9ca3af;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
}

.page-number-text {
  position: relative;
  z-index: 1;
}

.page-active-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #f97316, #ea580c);
  z-index: 0;
}

.page-btn:not(.ellipsis):hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
  transform: translateY(-2px);
}

.page-btn.active {
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
}

.page-btn.ellipsis {
  cursor: default;
  color: #6b7280;
}

.pagination-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  font-size: 0.875rem;
  color: #9ca3af;
}

.page-info-box {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 6px;
}

.current-range {
  color: #f97316;
  font-weight: 600;
}

.info-separator {
  color: #6b7280;
}

.total-count {
  color: var(--text-primary);
  font-weight: 500;
}

.page-progress {
  width: 100px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-left: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fb923c);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* Modal Styles */
.modal-content {
  width: 100%;
  max-width: 640px;
  padding: 0;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.05), transparent);
}

.modal-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 12px;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.modal-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
}

.modal-close {
  margin-left: auto;
  padding: 8px;
  color: #6b7280;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.modal-form {
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Topic Type Selector */
.topic-type-selector {
  display: flex;
  gap: 8px;
}

.type-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.type-option:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.type-option.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.5);
  color: #f97316;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #d1d5db;
}

.input-wrapper,
.textarea-wrapper {
  position: relative;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: rgba(249, 115, 22, 0.5);
  background: rgba(249, 115, 22, 0.05);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.form-input.error,
.form-textarea.error {
  border-color: rgba(239, 68, 68, 0.5);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #6b7280;
}

.form-textarea {
  resize: vertical;
  min-height: 150px;
}

.char-count {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 0.75rem;
  color: #6b7280;
  transition: color 0.2s ease;
}

.char-count.warning {
  color: #f97316;
}

.error-text {
  font-size: 0.8rem;
  color: #ef4444;
}

.form-hint {
  font-size: 0.75rem;
  color: #6b7280;
}

.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(249, 115, 22, 0.15);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 6px;
  color: #f97316;
  font-size: 0.8rem;
}

.tag button {
  display: flex;
  color: #f97316;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.tag button:hover {
  opacity: 1;
}

.tag-input {
  flex: 1;
  min-width: 100px;
  padding: 4px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.tag-input:focus {
  outline: none;
}

.tag-input::placeholder {
  color: #6b7280;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(0, 0, 0, 0.2);
}

/* Preview Tooltip */
.preview-tooltip {
  position: fixed;
  z-index: 9999;
  max-width: 360px;
  padding: 16px;
  pointer-events: none;
}

.preview-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.preview-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  width: fit-content;
}

.preview-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.4;
}

.preview-text {
  color: #9ca3af;
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 12px;
}

.preview-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.preview-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  font-size: 0.8rem;
}

.preview-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #f97316;
}

/* Transitions */
.breadcrumb-slide-enter-active,
.breadcrumb-slide-leave-active {
  transition: all 0.5s ease;
}

.breadcrumb-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.hero-fade-enter-active {
  transition: all 0.6s ease;
}

.hero-fade-enter-from {
  opacity: 0;
  transform: scale(0.98);
}

.filter-slide-enter-active {
  transition: all 0.5s ease 0.2s;
}

.filter-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.dropdown-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-slide-leave-active {
  transition: all 0.2s ease;
}

.dropdown-slide-enter-from,
.dropdown-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.filters-expand-enter-active {
  transition: all 0.3s ease;
}

.filters-expand-leave-active {
  transition: all 0.2s ease;
}

.filters-expand-enter-from,
.filters-expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  padding-top: 0;
}

.filter-tag-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-tag-leave-active {
  transition: all 0.2s ease;
}

.filter-tag-enter-from,
.filter-tag-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.topic-list-enter-active,
.topic-grid-enter-active {
  transition: all 0.4s ease;
}

.topic-list-leave-active,
.topic-grid-leave-active {
  transition: all 0.3s ease;
  position: absolute;
}

.topic-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.topic-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.topic-grid-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.topic-grid-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.topic-list-move,
.topic-grid-move {
  transition: transform 0.4s ease;
}

.trending-pulse-enter-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.trending-pulse-leave-active {
  transition: all 0.2s ease;
}

.trending-pulse-enter-from,
.trending-pulse-leave-to {
  opacity: 0;
  transform: scale(0) translateX(20px);
}

.badge-pop-enter-active {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.badge-pop-leave-active {
  transition: all 0.2s ease;
}

.badge-pop-enter-from,
.badge-pop-leave-to {
  opacity: 0;
  transform: scale(0);
}

.preview-expand-enter-active {
  transition: all 0.3s ease;
}

.preview-expand-leave-active {
  transition: all 0.2s ease;
}

.preview-expand-enter-from,
.preview-expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding: 0;
  margin: 0;
}

.pagination-slide-enter-active {
  transition: all 0.5s ease 0.3s;
}

.pagination-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-number-enter-active {
  transition: all 0.3s ease;
}

.page-number-leave-active {
  transition: all 0.2s ease;
}

.page-number-enter-from,
.page-number-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.empty-bounce-enter-active {
  transition: all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.empty-bounce-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.error-shake-enter-active {
  animation: shake 0.4s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}

.tag-pop-enter-active {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.tag-pop-leave-active {
  transition: all 0.2s ease;
}

.tag-pop-enter-from,
.tag-pop-leave-to {
  opacity: 0;
  transform: scale(0);
}

.preview-tooltip-enter-active {
  transition: all 0.3s ease;
}

.preview-tooltip-leave-active {
  transition: all 0.2s ease;
}

.preview-tooltip-enter-from,
.preview-tooltip-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Responsive */
@media (max-width: 1024px) {
  .hero-content > div {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-action {
    width: 100%;
  }

  .new-topic-btn {
    width: 100%;
    justify-content: center;
  }

  .stats-overlay {
    flex-wrap: wrap;
  }

  .stat-item {
    flex: 1;
    min-width: 140px;
  }

  .card-inner {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .topic-author-section {
    flex-direction: row;
    justify-content: flex-start;
  }

  .topic-badges {
    flex-direction: row;
  }

  .topic-last-reply {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-left: 0;
    padding-top: 16px;
    min-width: auto;
  }

  .breadcrumb-container {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .online-users-indicator {
    align-self: flex-end;
  }

  .topics-container.compact-view {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .category-hero {
    padding: 24px;
  }

  .hero-title {
    font-size: 1.75rem;
  }

  .filter-card {
    padding: 16px;
  }

  .view-mode-toggle {
    display: none;
  }

  .sort-dropdown {
    width: 100%;
  }

  .sort-trigger {
    width: 100%;
    justify-content: space-between;
  }

  .sort-dropdown-menu {
    left: 0;
    right: 0;
  }

  .pagination-wrapper {
    flex-wrap: wrap;
    padding: 12px 16px;
  }

  .pagination-btn span {
    display: none;
  }

  .modal-content {
    margin: 16px;
  }

  .topic-type-selector {
    flex-direction: column;
  }

  .type-option {
    flex: none;
  }
}
</style>
