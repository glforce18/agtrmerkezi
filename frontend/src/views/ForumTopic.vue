<template>
  <div class="forum-topic-page min-h-screen relative">
    <!-- Reading Progress Indicator -->
    <div class="reading-progress-container">
      <div
        class="reading-progress-bar"
        :style="{ width: `${readingProgress}%` }"
      />
    </div>

    <!-- Animated Background -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl animate-float" />
      <div class="absolute top-1/2 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float-delayed" />
      <div class="absolute -bottom-40 right-1/3 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-float" />
    </div>

    <!-- Floating Action Bar -->
    <Transition name="slide-up">
      <div
        v-if="showFloatingBar"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
      >
        <div class="floating-action-bar glass-morphism-strong px-6 py-3 rounded-full flex items-center gap-4">
          <n-tooltip trigger="hover" placement="top">
            <template #trigger>
              <button
                class="fab-button"
                :class="{ 'liked': hasLikedTopic }"
                @click="likeTopic"
              >
                <HeartIcon class="w-5 h-5" :class="{ 'animate-like': likeAnimating }" />
                <span class="fab-count">{{ topic?.likes }}</span>
              </button>
            </template>
            Begeni
          </n-tooltip>

          <div class="h-6 w-px bg-white/20" />

          <n-tooltip trigger="hover" placement="top">
            <template #trigger>
              <button class="fab-button" @click="showShareModal = true">
                <Share2Icon class="w-5 h-5" />
              </button>
            </template>
            Paylas
          </n-tooltip>

          <n-tooltip trigger="hover" placement="top">
            <template #trigger>
              <button class="fab-button" @click="showReportModal = true">
                <FlagIcon class="w-5 h-5" />
              </button>
            </template>
            Bildir
          </n-tooltip>

          <div class="h-6 w-px bg-white/20" />

          <n-tooltip trigger="hover" placement="top">
            <template #trigger>
              <button class="fab-button" @click="scrollToReplyForm">
                <MessageSquareIcon class="w-5 h-5" />
              </button>
            </template>
            Yanıtla
          </n-tooltip>

          <n-tooltip trigger="hover" placement="top">
            <template #trigger>
              <button class="fab-button" @click="scrollToTop">
                <ArrowUpIcon class="w-5 h-5" />
              </button>
            </template>
            Yukari
          </n-tooltip>
        </div>
      </div>
    </Transition>

    <div class="container-custom py-8 relative z-10">
      <!-- Enhanced Breadcrumb Navigation with Category Color -->
      <nav class="breadcrumb-nav glass-morphism mb-6 p-4 rounded-2xl">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3 flex-wrap">
            <button
              class="breadcrumb-item group"
              @click="router.push('/forum')"
            >
              <div class="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 hover:bg-orange-500/20 transition-all duration-300">
                <HomeIcon class="w-4 h-4 text-orange-400 group-hover:scale-110 transition-transform" />
                <span class="text-gray-300 group-hover:text-orange-400 transition-colors">Forum</span>
              </div>
            </button>

            <ChevronRightIcon class="w-4 h-4 text-gray-500" />

            <button
              class="breadcrumb-item group"
              @click="router.push(`/forum/category/${topic?.categoryId || 1}`)"
            >
              <div
                class="flex items-center gap-2 px-3 py-2 rounded-xl transition-all duration-300"
                :style="{
                  background: `${getCategoryColor(topic?.categoryId)}15`,
                  borderLeft: `3px solid ${getCategoryColor(topic?.categoryId)}`
                }"
              >
                <FolderIcon class="w-4 h-4 transition-transform group-hover:scale-110" :style="{ color: getCategoryColor(topic?.categoryId) }" />
                <span class="transition-colors" :style="{ color: getCategoryColor(topic?.categoryId) }">{{ topic?.categoryName || 'Genel Tartisma' }}</span>
              </div>
            </button>

            <ChevronRightIcon class="w-4 h-4 text-gray-500" />

            <div class="flex items-center gap-2 px-3 py-2 rounded-xl bg-orange-500/10 border border-orange-500/30">
              <FileTextIcon class="w-4 h-4 text-orange-500" />
              <span class="text-orange-400 font-medium truncate max-w-[200px] md:max-w-[400px]">{{ topic?.title }}</span>
            </div>
          </div>

          <div class="hidden md:flex items-center gap-2">
            <n-button quaternary size="small" @click="router.back()">
              <template #icon><ArrowLeftIcon class="w-4 h-4" /></template>
              Geri
            </n-button>
          </div>
        </div>
      </nav>

      <!-- Topic Header Card -->
      <div class="glass-morphism-strong rounded-3xl p-6 mb-6 animate-fade-in">
        <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-6">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3 flex-wrap">
              <n-tag
                v-if="topic?.isPinned"
                type="warning"
                round
                class="tag-glow-orange"
              >
                <template #icon><PinIcon class="w-3 h-3" /></template>
                Sabitlenmis
              </n-tag>
              <n-tag
                v-if="topic?.isLocked"
                type="error"
                round
                class="tag-glow-red"
              >
                <template #icon><LockIcon class="w-3 h-3" /></template>
                Kilitli
              </n-tag>
              <n-tag
                v-if="topic?.isHot"
                round
                class="tag-hot"
              >
                <template #icon><FlameIcon class="w-3 h-3" /></template>
                Popüler
              </n-tag>
            </div>

            <h1 class="text-2xl md:text-4xl font-display font-bold mb-4">
              <span class="text-gradient-animated">{{ topic?.title }}</span>
            </h1>

            <!-- Topic Meta Stats -->
            <div class="flex flex-wrap items-center gap-4 text-sm">
              <div class="stat-chip">
                <MessageSquareIcon class="w-4 h-4 text-orange-400" />
                <span>{{ replies.length }} Yanıt</span>
              </div>
              <div class="stat-chip">
                <EyeIcon class="w-4 h-4 text-purple-400" />
                <span>{{ topic?.views }} Görüntülenme</span>
              </div>
              <div class="stat-chip">
                <HeartIcon class="w-4 h-4 text-pink-400" />
                <span>{{ topic?.likes }} Begeni</span>
              </div>
              <div class="stat-chip">
                <ClockIcon class="w-4 h-4 text-cyan-400" />
                <span>{{ topic?.created }}</span>
              </div>
            </div>
          </div>

          <!-- Quick Actions (Desktop) -->
          <div class="hidden lg:flex items-center gap-2">
            <n-button-group>
              <n-button
                :type="hasLikedTopic ? 'primary' : 'default'"
                quaternary
                @click="likeTopic"
              >
                <template #icon>
                  <HeartIcon class="w-4 h-4" :class="{ 'text-red-500 fill-red-500': hasLikedTopic }" />
                </template>
                {{ topic?.likes }}
              </n-button>
              <n-button quaternary @click="showShareModal = true">
                <template #icon><Share2Icon class="w-4 h-4" /></template>
              </n-button>
              <n-button quaternary @click="bookmarkTopic">
                <template #icon>
                  <BookmarkIcon class="w-4 h-4" :class="{ 'text-yellow-500 fill-yellow-500': hasBookmarked }" />
                </template>
              </n-button>
            </n-button-group>
          </div>
        </div>
      </div>

      <!-- Original Post -->
      <div class="post-card glass-morphism-strong rounded-3xl overflow-hidden mb-6 animate-fade-in" style="animation-delay: 0.1s">
        <div class="flex flex-col lg:flex-row">
          <!-- Enhanced Author Sidebar -->
          <div class="author-sidebar lg:w-64 p-6 border-b lg:border-b-0 lg:border-r border-white/10">
            <div class="flex lg:flex-col items-center lg:items-center gap-4 lg:gap-3">
              <!-- Avatar with Status & Level Ring -->
              <div class="relative group">
                <div class="avatar-ring-container">
                  <svg class="avatar-level-ring" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="4"/>
                    <circle
                      cx="60" cy="60" r="54" fill="none"
                      :stroke="getLevelColor(topic?.authorLevel)"
                      stroke-width="4"
                      stroke-linecap="round"
                      :stroke-dasharray="`${(topic?.authorXpProgress || 75) * 3.39} 339`"
                      transform="rotate(-90 60 60)"
                      class="level-progress"
                    />
                  </svg>
                  <n-avatar
                    round
                    :size="96"
                    :src="topic?.authorAvatar"
                    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
                  />
                </div>

                <!-- Online Status -->
                <div
                  class="absolute bottom-2 right-2 w-5 h-5 rounded-full border-3 border-gray-900"
                  :class="topic?.authorOnline ? 'bg-green-500 animate-pulse' : 'bg-gray-500'"
                />

                <!-- Level Badge -->
                <div class="level-badge">
                  <ZapIcon class="w-3 h-3 mr-1" />
                  {{ topic?.authorLevel || 42 }}
                </div>
              </div>

              <!-- Author Info -->
              <div class="text-center lg:text-center flex-1 lg:flex-none">
                <h3 class="font-bold text-lg text-[color:var(--text-primary)] hover:text-orange-400 transition-colors cursor-pointer">
                  {{ topic?.author }}
                </h3>

                <!-- Role Badge -->
                <div class="role-badge-container my-2">
                  <span :class="getRoleBadgeClass(topic?.authorRole)">
                    <component :is="getRoleIcon(topic?.authorRole)" class="w-3 h-3 mr-1" />
                    {{ topic?.authorRole }}
                  </span>
                </div>

                <!-- Badges Row -->
                <div class="flex justify-center gap-1 mb-3">
                  <n-tooltip v-for="badge in topic?.authorBadges || defaultBadges" :key="badge.id">
                    <template #trigger>
                      <div class="badge-icon" :style="{ background: badge.color }">
                        <component :is="getBadgeIcon(badge.icon)" class="w-3 h-3" />
                      </div>
                    </template>
                    {{ badge.name }}
                  </n-tooltip>
                </div>

                <!-- Author Stats Grid -->
                <div class="author-stats-grid">
                  <div class="author-stat-item">
                    <MessageCircleIcon class="w-4 h-4 text-orange-400" />
                    <span class="stat-value">{{ topic?.authorPosts }}</span>
                    <span class="stat-label">Gönderi</span>
                  </div>
                  <div class="author-stat-item">
                    <ThumbsUpIcon class="w-4 h-4 text-pink-400" />
                    <span class="stat-value">{{ topic?.authorLikes || 2341 }}</span>
                    <span class="stat-label">Begeni</span>
                  </div>
                  <div class="author-stat-item full-width">
                    <CalendarIcon class="w-4 h-4 text-cyan-400" />
                    <span class="stat-label">Üyelik: {{ topic?.authorJoined }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Post Content -->
          <div class="flex-1 p-6">
            <div class="flex items-center justify-between mb-4">
              <span class="text-sm text-gray-500 flex items-center gap-2">
                <ClockIcon class="w-4 h-4" />
                {{ topic?.created }}
                <span v-if="topic?.isEdited" class="text-orange-400">(düzenlendi)</span>
              </span>

              <!-- Post Actions Menu -->
              <n-dropdown
                v-if="isOwnPost(topic?.authorId)"
                :options="postActionOptions"
                @select="handlePostAction"
              >
                <n-button quaternary circle size="small">
                  <MoreHorizontalIcon class="w-4 h-4" />
                </n-button>
              </n-dropdown>
            </div>

            <!-- Rendered Markdown Content -->
            <div class="post-content prose prose-invert max-w-none mb-6">
              <div v-html="renderedContent" class="markdown-body" />
            </div>

            <!-- Attachments -->
            <div v-if="topic?.attachments?.length" class="mb-6">
              <h4 class="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <PaperclipIcon class="w-4 h-4" />
                Ekler
              </h4>
              <div class="flex flex-wrap gap-2">
                <a
                  v-for="attachment in topic?.attachments"
                  :key="attachment.id"
                  :href="attachment.url"
                  target="_blank"
                  class="attachment-chip"
                >
                  <FileIcon class="w-4 h-4" />
                  <span>{{ attachment.name }}</span>
                  <span class="text-xs text-gray-500">({{ attachment.size }})</span>
                </a>
              </div>
            </div>

            <!-- Reactions Bar -->
            <div class="reactions-bar flex flex-wrap items-center gap-2 mb-4 pb-4 border-b border-white/10">
              <button
                v-for="reaction in availableReactions"
                :key="reaction.emoji"
                class="reaction-button"
                :class="{ 'active': hasReacted(reaction.emoji) }"
                @click="toggleReaction(reaction.emoji)"
              >
                <span class="text-lg">{{ reaction.emoji }}</span>
                <span v-if="getReactionCount(reaction.emoji) > 0" class="reaction-count">
                  {{ getReactionCount(reaction.emoji) }}
                </span>
              </button>

              <n-popover trigger="click" placement="bottom-start">
                <template #trigger>
                  <button class="reaction-button add-reaction">
                    <PlusIcon class="w-4 h-4" />
                  </button>
                </template>
                <div class="grid grid-cols-6 gap-2 p-2">
                  <button
                    v-for="emoji in allEmojis"
                    :key="emoji"
                    class="emoji-picker-item"
                    @click="addReaction(emoji)"
                  >
                    {{ emoji }}
                  </button>
                </div>
              </n-popover>
            </div>

            <!-- Post Actions -->
            <div class="flex items-center justify-between">
              <div class="flex gap-3">
                <button
                  class="like-button-animated"
                  :class="{ 'liked': hasLikedTopic, 'animating': likeAnimating }"
                  @click="likeTopic"
                >
                  <HeartIcon class="like-icon w-5 h-5" />
                  <span class="like-count">{{ topic?.likes }}</span>
                  <span class="like-text">Begeni</span>
                  <div class="like-particles">
                    <span v-for="i in 6" :key="i" class="particle" />
                  </div>
                </button>
                <n-button size="small" @click="scrollToReplyForm" class="action-button">
                  <template #icon><ReplyIcon class="w-4 h-4" /></template>
                  Yanıtla
                </n-button>
                <n-button size="small" @click="showShareModal = true" class="action-button">
                  <template #icon><Share2Icon class="w-4 h-4" /></template>
                  Paylas
                </n-button>
              </div>
              <n-button size="small" type="error" quaternary @click="showReportModal = true">
                <template #icon><FlagIcon class="w-4 h-4" /></template>
                Bildir
              </n-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <Transition name="fade">
        <div v-if="typingUsers.length > 0" class="typing-indicator glass-morphism rounded-2xl p-4 mb-4">
          <div class="flex items-center gap-3">
            <div class="typing-dots">
              <span /><span /><span />
            </div>
            <span class="text-sm text-gray-400">
              <strong class="text-orange-400">{{ typingUsers.join(', ') }}</strong> yaziyor...
            </span>
          </div>
        </div>
      </Transition>

      <!-- Replies Section -->
      <div class="replies-section space-y-4 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold flex items-center gap-2">
            <MessageSquareIcon class="w-5 h-5 text-orange-400" />
            Yanıtlar ({{ replies.length }})
          </h2>
          <n-select
            v-model:value="sortOrder"
            :options="sortOptions"
            size="small"
            style="width: 150px"
          />
        </div>

        <TransitionGroup name="reply-list" tag="div" class="space-y-4">
          <div
            v-for="(reply, index) in sortedReplies"
            :key="reply.id"
            :id="`reply-${reply.id}`"
            class="reply-card glass-morphism rounded-2xl overflow-hidden"
            :class="{
              'highlighted': highlightedReplyId === reply.id,
              'reply-even': index % 2 === 0,
              'reply-odd': index % 2 === 1
            }"
            :style="{ animationDelay: `${index * 0.05}s` }"
          >
            <div class="flex flex-col lg:flex-row">
              <!-- Reply Author Sidebar -->
              <div class="reply-author-sidebar lg:w-56 p-4 border-b lg:border-b-0 lg:border-r border-white/10">
                <div class="flex lg:flex-col items-center gap-3">
                  <!-- Compact Avatar -->
                  <div class="relative">
                    <div class="avatar-ring-small">
                      <svg class="w-full h-full" viewBox="0 0 80 80">
                        <circle cx="40" cy="40" r="36" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="3"/>
                        <circle
                          cx="40" cy="40" r="36" fill="none"
                          :stroke="getLevelColor(reply.authorLevel)"
                          stroke-width="3"
                          stroke-linecap="round"
                          :stroke-dasharray="`${(reply.authorXpProgress || 50) * 2.26} 226`"
                          transform="rotate(-90 40 40)"
                        />
                      </svg>
                      <n-avatar round :size="56" :src="reply.authorAvatar" class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                    </div>
                    <div
                      class="absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-gray-900"
                      :class="reply.authorOnline ? 'bg-green-500' : 'bg-gray-500'"
                    />
                    <div class="level-badge-small">{{ reply.authorLevel || 15 }}</div>
                  </div>

                  <div class="text-center lg:text-center flex-1 lg:flex-none">
                    <h4 class="font-semibold text-[color:var(--text-primary)] hover:text-orange-400 transition-colors cursor-pointer">
                      {{ reply.author }}
                    </h4>
                    <span :class="getRoleBadgeClass(reply.authorRole, 'small')">
                      {{ reply.authorRole }}
                    </span>
                    <div class="reply-author-stats">
                      <span><MessageCircleIcon class="w-3 h-3" /> {{ reply.authorPosts }}</span>
                      <span><CalendarIcon class="w-3 h-3" /> {{ reply.authorJoined || 'Oca 2024' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Reply Content -->
              <div class="flex-1 p-4">
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center gap-3">
                    <span class="reply-number">#{{ index + 1 }}</span>
                    <span class="text-sm text-gray-500 flex items-center gap-1">
                      <ClockIcon class="w-3 h-3" />
                      {{ reply.created }}
                    </span>
                    <span v-if="reply.isEdited" class="text-xs text-orange-400">(düzenlendi)</span>
                  </div>

                  <!-- Reply Actions Menu -->
                  <div class="flex items-center gap-2">
                    <n-button
                      text
                      size="tiny"
                      @click="scrollToReply(reply.id)"
                      class="text-gray-500 hover:text-orange-400"
                    >
                      <LinkIcon class="w-3 h-3" />
                    </n-button>
                    <n-dropdown
                      v-if="isOwnPost(reply.authorId)"
                      :options="replyActionOptions"
                      @select="(key) => handleReplyAction(key, reply)"
                    >
                      <n-button text size="tiny">
                        <MoreHorizontalIcon class="w-4 h-4" />
                      </n-button>
                    </n-dropdown>
                  </div>
                </div>

                <!-- Quote Preview (if replying to another post) -->
                <div v-if="reply.quotedPost" class="quote-block mb-4">
                  <div class="quote-header">
                    <QuoteIcon class="w-4 h-4 text-orange-400" />
                    <span>{{ reply.quotedPost.author }} yazdi:</span>
                  </div>
                  <div class="quote-content">
                    {{ reply.quotedPost.content }}
                  </div>
                  <button
                    class="quote-jump-btn"
                    @click="scrollToReply(reply.quotedPost.id)"
                  >
                    Orijinal mesaja git
                    <ArrowRightIcon class="w-3 h-3" />
                  </button>
                </div>

                <!-- Reply Content with Markdown -->
                <div class="reply-content prose prose-invert prose-sm max-w-none mb-4">
                  <div v-html="renderMarkdown(reply.content)" class="markdown-body" />
                </div>

                <!-- Reply Reactions -->
                <div class="flex flex-wrap items-center gap-2 mb-3">
                  <button
                    v-for="reaction in reply.reactions || []"
                    :key="reaction.emoji"
                    class="reaction-button-small"
                    :class="{ 'active': reaction.hasReacted }"
                    @click="toggleReplyReaction(reply.id, reaction.emoji)"
                  >
                    <span>{{ reaction.emoji }}</span>
                    <span class="text-xs">{{ reaction.count }}</span>
                  </button>
                </div>

                <!-- Reply Actions -->
                <div class="flex items-center gap-3 pt-3 border-t border-white/10">
                  <button
                    class="reply-like-btn"
                    :class="{ 'liked': reply.hasLiked }"
                    @click="likeReply(reply.id)"
                  >
                    <HeartIcon class="w-4 h-4" />
                    <span>{{ reply.likes }}</span>
                  </button>
                  <n-button text size="tiny" @click="quoteReply(reply)" class="reply-action-btn">
                    <template #icon><QuoteIcon class="w-3 h-3" /></template>
                    Alıntıla
                  </n-button>
                  <n-button text size="tiny" @click="replyToUser(reply)" class="reply-action-btn">
                    <template #icon><AtSignIcon class="w-3 h-3" /></template>
                    Yanıtla
                  </n-button>
                  <n-button text size="tiny" type="error" @click="reportReply(reply)" class="reply-action-btn">
                    <template #icon><FlagIcon class="w-3 h-3" /></template>
                    Bildir
                  </n-button>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <!-- Pagination -->
      <div class="flex justify-center mb-8">
        <div class="glass-morphism rounded-2xl px-6 py-3">
          <n-pagination
            v-model:page="currentPage"
            :page-count="totalPages"
            :page-slot="7"
            show-quick-jumper
          >
            <template #prev>
              <ChevronLeftIcon class="w-4 h-4" />
            </template>
            <template #next>
              <ChevronRightIcon class="w-4 h-4" />
            </template>
          </n-pagination>
        </div>
      </div>

      <!-- Reply Form -->
      <div
        v-if="!topic?.isLocked"
        ref="replyFormRef"
        id="reply-form"
        class="reply-form-container glass-morphism-strong rounded-3xl overflow-hidden animate-fade-in"
      >
        <!-- Quote Preview in Form -->
        <Transition name="slide-down">
          <div v-if="quotedReply" class="quote-form-preview border-b border-white/10 p-4">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2 text-sm text-gray-400">
                  <QuoteIcon class="w-4 h-4 text-orange-400" />
                  <span><strong>{{ quotedReply.author }}</strong> kullanıcısina yanıt veriyorsunuz:</span>
                </div>
                <div class="quote-content text-sm">
                  {{ quotedReply.content.substring(0, 200) }}{{ quotedReply.content.length > 200 ? '...' : '' }}
                </div>
              </div>
              <n-button circle size="small" quaternary @click="clearQuote">
                <XIcon class="w-4 h-4" />
              </n-button>
            </div>
          </div>
        </Transition>

        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-lg flex items-center gap-2">
              <EditIcon class="w-5 h-5 text-orange-400" />
              Yanıt Yaz
            </h3>
            <div class="flex items-center gap-2 text-sm text-gray-500">
              <span>Markdown desteklenir</span>
              <n-tooltip>
                <template #trigger>
                  <HelpCircleIcon class="w-4 h-4 cursor-help" />
                </template>
                <div class="text-xs">
                  **kalın**, *italik*, `kod`, ```kod blogu```<br/>
                  > alıntı, - liste, [link](url)
                </div>
              </n-tooltip>
            </div>
          </div>

          <n-form @submit.prevent="submitReply" class="space-y-4">
            <!-- Rich Text Editor Toolbar -->
            <div class="editor-toolbar">
              <div class="toolbar-group">
                <n-tooltip v-for="tool in editorTools" :key="tool.action">
                  <template #trigger>
                    <button
                      type="button"
                      class="editor-tool-btn"
                      :class="{ 'active': activeFormats.includes(tool.action) }"
                      @click="applyFormat(tool.action)"
                    >
                      <component :is="tool.icon" class="w-4 h-4" />
                    </button>
                  </template>
                  {{ tool.label }}
                </n-tooltip>
              </div>

              <div class="toolbar-divider" />

              <div class="toolbar-group">
                <!-- Emoji Picker -->
                <n-popover trigger="click" placement="bottom">
                  <template #trigger>
                    <button type="button" class="editor-tool-btn">
                      <SmileIcon class="w-4 h-4" />
                    </button>
                  </template>
                  <div class="grid grid-cols-8 gap-1 p-2 max-h-48 overflow-y-auto">
                    <button
                      v-for="emoji in allEmojis"
                      :key="emoji"
                      type="button"
                      class="emoji-picker-item"
                      @click="insertEmoji(emoji)"
                    >
                      {{ emoji }}
                    </button>
                  </div>
                </n-popover>
              </div>

              <div class="toolbar-divider" />

              <!-- Preview Toggle -->
              <button
                type="button"
                class="editor-tool-btn preview-toggle"
                :class="{ 'active': showPreview }"
                @click="showPreview = !showPreview"
              >
                <EyeIcon class="w-4 h-4" />
                <span>Onizle</span>
              </button>
            </div>

            <!-- Editor / Preview Split -->
            <div class="editor-container" :class="{ 'split-view': showPreview }">
              <div class="editor-pane">
                <n-input
                  ref="editorRef"
                  v-model:value="newReply"
                  type="textarea"
                  placeholder="Yanıtinizi yazın... Markdown kullanabilirsiniz."
                  :rows="8"
                  @input="handleTyping"
                  @focus="handleEditorFocus"
                  class="custom-textarea"
                />
              </div>

              <Transition name="fade">
                <div v-if="showPreview" class="preview-pane">
                  <div class="text-xs text-gray-500 mb-2 flex items-center gap-2">
                    <EyeIcon class="w-3 h-3" />
                    Onizleme
                  </div>
                  <div
                    class="preview-content prose prose-invert prose-sm max-w-none"
                    v-html="previewContent"
                  />
                </div>
              </Transition>
            </div>

            <!-- Character Count & Submit -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <span class="text-sm text-gray-500">
                  {{ newReply.length }} / 10000 karakter
                </span>
                <n-progress
                  type="line"
                  :percentage="(newReply.length / 10000) * 100"
                  :show-indicator="false"
                  :height="4"
                  style="width: 100px"
                  :color="newReply.length > 9000 ? '#ef4444' : '#f97316'"
                />
              </div>

              <div class="flex gap-3">
                <n-button quaternary @click="saveDraft">
                  <template #icon><SaveIcon class="w-4 h-4" /></template>
                  Taslak Kaydet
                </n-button>
                <n-button
                  type="primary"
                  attr-type="submit"
                  :disabled="!newReply.trim() || isSubmitting"
                  :loading="isSubmitting"
                  class="submit-btn"
                >
                  <template #icon><SendIcon class="w-4 h-4" /></template>
                  Yanıtla
                </n-button>
              </div>
            </div>
          </n-form>
        </div>
      </div>

      <!-- Locked Topic Message -->
      <div v-else class="locked-message glass-morphism-strong rounded-3xl text-center py-16">
        <div class="locked-icon-container mb-6">
          <LockIcon class="w-16 h-16 text-red-500" />
        </div>
        <h3 class="text-2xl font-bold mb-3">Bu Konu Kilitli</h3>
        <p class="text-gray-400 max-w-md mx-auto">
          Bu konuya yeni yanıt ekleyemezsiniz. Daha fazla bilgi için moderatörlerle iletişime gecin.
        </p>
      </div>
    </div>

    <!-- Report Modal -->
    <n-modal v-model:show="showReportModal" preset="card" title="İçerik Bildir" class="max-w-lg report-modal">
      <div class="report-modal-content">
        <div class="report-icon-container mb-4">
          <FlagIcon class="w-8 h-8 text-red-400" />
        </div>
        <n-form ref="reportFormRef" :model="reportForm" class="space-y-4">
          <n-form-item label="Bildirim Nedeni" path="reason">
            <n-radio-group v-model:value="reportForm.reason" class="report-reasons">
              <div
                v-for="reason in reportReasons"
                :key="reason.value"
                class="report-reason-item"
                :class="{ 'selected': reportForm.reason === reason.value }"
                @click="reportForm.reason = reason.value"
              >
                <n-radio :value="reason.value" />
                <component :is="reason.icon" class="w-4 h-4" />
                <span>{{ reason.label }}</span>
              </div>
            </n-radio-group>
          </n-form-item>
          <n-form-item label="Ek Açıklama" path="description">
            <n-input
              v-model:value="reportForm.description"
              type="textarea"
              placeholder="Daha fazla detay ekleyin..."
              :rows="4"
            />
          </n-form-item>
        </n-form>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button @click="showReportModal = false">İptal</n-button>
          <n-button type="error" @click="submitReport">
            <template #icon><FlagIcon class="w-4 h-4" /></template>
            Bildir
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- Share Modal -->
    <n-modal v-model:show="showShareModal" preset="card" title="Paylas" class="max-w-md share-modal">
      <div class="share-modal-content">
        <div class="share-preview mb-6">
          <div class="share-preview-icon">
            <Share2Icon class="w-6 h-6 text-orange-400" />
          </div>
          <div class="share-preview-text">
            <h4 class="font-semibold text-[color:var(--text-primary)]">{{ topic?.title }}</h4>
            <p class="text-xs text-gray-500">{{ replies.length }} yanıt - {{ topic?.views }} görüntülenme</p>
          </div>
        </div>

        <div class="share-url-container">
          <n-input :value="shareUrl" readonly class="share-url-input" />
          <n-button type="primary" @click="copyShareUrl" class="copy-btn">
            <template #icon><CopyIcon class="w-4 h-4" /></template>
            Kopyala
          </n-button>
        </div>

        <div class="share-divider">
          <span>veya sosyal medyada paylaş</span>
        </div>

        <div class="social-share-grid">
          <button
            v-for="social in socialShareOptions"
            :key="social.name"
            class="social-share-btn"
            :style="{ '--social-color': social.color }"
            @click="shareToSocial(social)"
          >
            <component :is="social.icon" class="w-5 h-5" />
            <span>{{ social.name }}</span>
          </button>
        </div>
      </div>
    </n-modal>

    <!-- Edit Post Modal -->
    <n-modal v-model:show="showEditModal" preset="card" title="Gönderiyi Düzenle" class="max-w-2xl">
      <n-form class="space-y-4">
        <n-form-item label="İçerik">
          <n-input
            v-model:value="editContent"
            type="textarea"
            :rows="8"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="flex justify-end gap-3">
          <n-button @click="showEditModal = false">İptal</n-button>
          <n-button type="primary" @click="saveEdit">
            <template #icon><SaveIcon class="w-4 h-4" /></template>
            Kaydet
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- Delete Confirmation Modal -->
    <n-modal v-model:show="showDeleteModal" preset="dialog" type="error" title="Gönderiyi Sil">
      <template #default>
        Bu gönderiyi silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.
      </template>
      <template #action>
        <div class="flex gap-3">
          <n-button @click="showDeleteModal = false">İptal</n-button>
          <n-button type="error" @click="confirmDelete">
            <template #icon><Trash2Icon class="w-4 h-4" /></template>
            Sil
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
  HomeIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  FolderIcon,
  FileTextIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  MessageSquareIcon,
  MessageCircleIcon,
  EyeIcon,
  ClockIcon,
  PinIcon,
  LockIcon,
  FlameIcon,
  HeartIcon,
  ThumbsUpIcon,
  Share2Icon,
  BookmarkIcon,
  FlagIcon,
  QuoteIcon,
  SendIcon,
  MoreHorizontalIcon,
  EditIcon,
  Trash2Icon,
  LinkIcon,
  AtSignIcon,
  CalendarIcon,
  PaperclipIcon,
  FileIcon,
  PlusIcon,
  XIcon,
  HelpCircleIcon,
  SaveIcon,
  CopyIcon,
  SmileIcon,
  ArrowUpIcon,
  ReplyIcon,
  BoldIcon,
  ItalicIcon,
  CodeIcon,
  ListIcon,
  ImageIcon,
  LinkIcon as Link2Icon,
  StarIcon,
  ShieldIcon,
  AwardIcon,
  ZapIcon,
  CrownIcon,
  TwitterIcon,
  FacebookIcon,
  LinkedinIcon,
  MailIcon,
  AlertTriangleIcon,
  BanIcon,
  CopyrightIcon,
  HelpCircleIcon as OtherIcon,
  UserIcon,
  UsersIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const topicId = route.params.id

// Refs
const replyFormRef = ref(null)
const editorRef = ref(null)
const reportFormRef = ref(null)

// State
const currentPage = ref(1)
const totalPages = ref(5)
const sortOrder = ref('oldest')
const showFloatingBar = ref(false)
const showPreview = ref(false)
const showReportModal = ref(false)
const showShareModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const isSubmitting = ref(false)
const likeAnimating = ref(false)
const hasLikedTopic = ref(false)
const hasBookmarked = ref(false)
const highlightedReplyId = ref(null)
const quotedReply = ref(null)
const editContent = ref('')
const editingItem = ref(null)
const deletingItem = ref(null)
const typingUsers = ref([])
const activeFormats = ref([])
const typingTimeout = ref(null)
const readingProgress = ref(0)

// Current user (mock)
const currentUserId = ref(999)

// Category colors
const categoryColors = {
  1: '#f97316', // Genel - Orange
  2: '#8b5cf6', // Duyurular - Purple
  3: '#06b6d4', // Yardim - Cyan
  4: '#22c55e', // Oneriler - Green
  5: '#ec4899', // Etkinlikler - Pink
  6: '#eab308'  // Rehberler - Yellow
}

// Topic Data
const topic = ref({
  id: 1,
  title: 'Yeni güncelleme hakkında dusunceleriniz?',
  content: `Merhaba arkadaşlar,

Yeni güncelleme ile birlikte gelen özellikleri denedim. Özellikle sunucu performansinda ciddi bir **iyilesme** var. Sizin dusunceleriniz neler?

Ben özellikle su noktalari begendim:
- Gelismis DDoS korumasi
- Yeni admin paneli arayuzu
- Otomatik yedekleme sistemi

\`\`\`javascript
// Ornek yapılandırma
const config = {
  ddosProtection: true,
  autoBackup: '24h',
  adminPanel: 'v2'
};
\`\`\`

> Bu güncelleme gercekten cigir acici!

Sizce en iyi özellik hangisi?`,
  author: 'Player123',
  authorId: 1,
  authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
  authorRole: 'Admin',
  authorLevel: 42,
  authorXpProgress: 75,
  authorPosts: 1234,
  authorLikes: 2341,
  authorJoined: 'Ocak 2023',
  authorOnline: true,
  authorBadges: [
    { id: 1, name: 'Kurucu', icon: 'crown', color: 'linear-gradient(135deg, #f97316, #ea580c)' },
    { id: 2, name: 'Gelistirici', icon: 'code', color: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' },
    { id: 3, name: 'VIP', icon: 'star', color: 'linear-gradient(135deg, #eab308, #ca8a04)' }
  ],
  categoryId: 1,
  categoryName: 'Genel Tartisma',
  created: '2 saat önce',
  views: 234,
  likes: 12,
  isPinned: true,
  isLocked: false,
  isHot: true,
  isEdited: false,
  attachments: [
    { id: 1, name: 'screenshot.png', size: '245 KB', url: '#' },
    { id: 2, name: 'config.json', size: '2 KB', url: '#' }
  ],
  reactions: [
    { emoji: '👍', count: 8, hasReacted: false },
    { emoji: '❤️', count: 5, hasReacted: true },
    { emoji: '🔥', count: 3, hasReacted: false }
  ]
})

const replies = ref([
  {
    id: 1,
    author: 'AdminUser',
    authorId: 2,
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    authorRole: 'Moderatör',
    authorLevel: 38,
    authorXpProgress: 60,
    authorPosts: 856,
    authorJoined: 'Mar 2023',
    authorOnline: true,
    created: '1 saat önce',
    content: 'Kesinlikle katıliyorum! Yeni admin paneli gercekten çok kullanisli. Özellikle **sunucu metriklerini** canli olarak gorebilmek harika.\n\n```bash\n# Sunucu durumunu kontrol et\nserverstatus --live\n```',
    likes: 5,
    hasLiked: false,
    isEdited: false,
    reactions: [
      { emoji: '👍', count: 3, hasReacted: false }
    ]
  },
  {
    id: 2,
    author: 'ProGamer',
    authorId: 3,
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    authorRole: 'VIP Üye',
    authorLevel: 27,
    authorXpProgress: 45,
    authorPosts: 623,
    authorJoined: 'Haz 2023',
    authorOnline: false,
    created: '45 dakika önce',
    content: 'DDoS korumasi sayesinde sunucum artik çok daha stabil çalışıyor. Gecen hafta büyük bir saldiri aldik ama hic kesinti olmadi. Harika bir güncelleme!',
    likes: 8,
    hasLiked: true,
    isEdited: true,
    quotedPost: {
      id: 1,
      author: 'AdminUser',
      content: 'Kesinlikle katıliyorum! Yeni admin paneli gercekten çok kullanisli.'
    },
    reactions: [
      { emoji: '🔥', count: 2, hasReacted: true },
      { emoji: '💪', count: 1, hasReacted: false }
    ]
  },
  {
    id: 3,
    author: 'NewbieCS',
    authorId: 4,
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
    authorRole: 'Yeni Üye',
    authorLevel: 5,
    authorXpProgress: 30,
    authorPosts: 42,
    authorJoined: 'Ara 2024',
    authorOnline: true,
    created: '30 dakika önce',
    content: 'Yeni başladım ama ben de çok memnunum. Dokümantasyon da çok iyi, kurulumu çok kolay yaptım. 😊',
    likes: 3,
    hasLiked: false,
    isEdited: false,
    reactions: [
      { emoji: '😊', count: 2, hasReacted: false }
    ]
  }
])

const newReply = ref('')

// Default badges for fallback
const defaultBadges = [
  { id: 1, name: 'Aktif Üye', icon: 'zap', color: 'linear-gradient(135deg, #f97316, #ea580c)' }
]

// Sort options
const sortOptions = [
  { label: 'En Eski', value: 'oldest' },
  { label: 'En Yeni', value: 'newest' },
  { label: 'En Çok Begenilen', value: 'likes' }
]

// Editor tools
const editorTools = [
  { action: 'bold', icon: BoldIcon, label: 'Kalın (Ctrl+B)' },
  { action: 'italic', icon: ItalicIcon, label: 'Italik (Ctrl+I)' },
  { action: 'code', icon: CodeIcon, label: 'Kod' },
  { action: 'quote', icon: QuoteIcon, label: 'Alıntı' },
  { action: 'list', icon: ListIcon, label: 'Liste' },
  { action: 'link', icon: Link2Icon, label: 'Link' },
  { action: 'image', icon: ImageIcon, label: 'Resim' }
]

// Available reactions
const availableReactions = [
  { emoji: '👍', name: 'Begen' },
  { emoji: '❤️', name: 'Sevgi' },
  { emoji: '🔥', name: 'Ates' },
  { emoji: '😂', name: 'Guldu' },
  { emoji: '😮', name: 'Saskin' },
  { emoji: '😢', name: 'Uzgun' }
]

// All emojis for picker
const allEmojis = ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '🥰', '😘', '😗', '😙', '😚', '🙂', '🤗', '🤩', '🤔', '🤨', '😐', '😑', '😶', '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', '🥱', '😴', '😌', '😛', '😜', '😝', '🤤', '😒', '😓', '😔', '😕', '🙃', '🤑', '😲', '☹️', '🙁', '😖', '😞', '😟', '😤', '😢', '😭', '😦', '😧', '😨', '😩', '🤯', '😬', '😰', '😱', '🥵', '🥶', '😳', '🤪', '😵', '🥴', '😠', '😡', '🤬', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '👍', '👎', '👏', '🙌', '🤝', '🔥', '⭐', '💯', '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '💪', '🎉', '🎊', '🏆', '🥇', '🚀', '💡', '✅', '❌', '⚠️', '❓', '❗']

// Report reasons with icons
const reportReasons = [
  { label: 'Spam veya reklam', value: 'spam', icon: BanIcon },
  { label: 'Hakaret veya kufur', value: 'abuse', icon: AlertTriangleIcon },
  { label: 'Yaniltici bilgi', value: 'misleading', icon: AlertTriangleIcon },
  { label: 'Telif hakki ihlali', value: 'copyright', icon: CopyrightIcon },
  { label: 'Diğer', value: 'other', icon: OtherIcon }
]

const reportForm = ref({
  reason: null,
  description: ''
})

// Social share options
const socialShareOptions = [
  { name: 'Twitter', icon: TwitterIcon, color: '#1DA1F2' },
  { name: 'Facebook', icon: FacebookIcon, color: '#4267B2' },
  { name: 'LinkedIn', icon: LinkedinIcon, color: '#0077B5' },
  { name: 'E-posta', icon: MailIcon, color: '#EA4335' }
]

// Post action options
const postActionOptions = [
  { label: 'Düzenle', key: 'edit', icon: () => h(EditIcon, { class: 'w-4 h-4' }) },
  { label: 'Sil', key: 'delete', icon: () => h(Trash2Icon, { class: 'w-4 h-4' }) }
]

const replyActionOptions = [
  { label: 'Düzenle', key: 'edit' },
  { label: 'Sil', key: 'delete' }
]

// Computed
const sortedReplies = computed(() => {
  const sorted = [...replies.value]
  switch (sortOrder.value) {
    case 'newest':
      return sorted.reverse()
    case 'likes':
      return sorted.sort((a, b) => b.likes - a.likes)
    default:
      return sorted
  }
})

const renderedContent = computed(() => {
  return renderMarkdown(topic.value?.content || '')
})

const previewContent = computed(() => {
  return renderMarkdown(newReply.value || '*Onizleme için bir seyler yazın...*')
})

const shareUrl = computed(() => {
  return `${window.location.origin}/forum/topic/${topicId}`
})

// Methods
function renderMarkdown(content) {
  if (!content) return ''
  try {
    const html = marked(content, {
      breaks: true,
      gfm: true
    })
    return DOMPurify.sanitize(html)
  } catch (e) {
    return content
  }
}

function getCategoryColor(categoryId) {
  return categoryColors[categoryId] || '#f97316'
}

function getLevelColor(level) {
  if (level >= 40) return '#f97316' // Orange - High level
  if (level >= 30) return '#8b5cf6' // Purple
  if (level >= 20) return '#06b6d4' // Cyan
  if (level >= 10) return '#22c55e' // Green
  return '#6b7280' // Gray - Beginner
}

function getRoleBadgeClass(role, size = 'normal') {
  const baseClass = size === 'small'
    ? 'role-badge-small'
    : 'role-badge'

  const roleClasses = {
    'Admin': 'role-admin',
    'Moderatör': 'role-mod',
    'VIP Üye': 'role-vip',
    'Üye': 'role-member',
    'Yeni Üye': 'role-newbie'
  }

  return `${baseClass} ${roleClasses[role] || 'role-member'}`
}

function getRoleIcon(role) {
  const icons = {
    'Admin': CrownIcon,
    'Moderatör': ShieldIcon,
    'VIP Üye': StarIcon,
    'Üye': UserIcon,
    'Yeni Üye': UsersIcon
  }
  return icons[role] || UserIcon
}

function getBadgeIcon(iconName) {
  const icons = {
    crown: CrownIcon,
    code: CodeIcon,
    star: StarIcon,
    shield: ShieldIcon,
    award: AwardIcon,
    zap: ZapIcon
  }
  return icons[iconName] || StarIcon
}

function isOwnPost(authorId) {
  return authorId === currentUserId.value
}

function hasReacted(emoji) {
  const reaction = topic.value?.reactions?.find(r => r.emoji === emoji)
  return reaction?.hasReacted || false
}

function getReactionCount(emoji) {
  const reaction = topic.value?.reactions?.find(r => r.emoji === emoji)
  return reaction?.count || 0
}

function toggleReaction(emoji) {
  const reaction = topic.value?.reactions?.find(r => r.emoji === emoji)
  if (reaction) {
    reaction.hasReacted = !reaction.hasReacted
    reaction.count += reaction.hasReacted ? 1 : -1
  } else {
    topic.value.reactions.push({ emoji, count: 1, hasReacted: true })
  }
}

function addReaction(emoji) {
  if (!hasReacted(emoji)) {
    toggleReaction(emoji)
  }
}

function toggleReplyReaction(replyId, emoji) {
  const reply = replies.value.find(r => r.id === replyId)
  if (reply) {
    const reaction = reply.reactions?.find(r => r.emoji === emoji)
    if (reaction) {
      reaction.hasReacted = !reaction.hasReacted
      reaction.count += reaction.hasReacted ? 1 : -1
    }
  }
}

function likeTopic() {
  if (topic.value) {
    hasLikedTopic.value = !hasLikedTopic.value
    topic.value.likes += hasLikedTopic.value ? 1 : -1

    if (hasLikedTopic.value) {
      likeAnimating.value = true
      setTimeout(() => {
        likeAnimating.value = false
      }, 600)
    }

    window.$message?.success(hasLikedTopic.value ? 'Begenildi' : 'Begeni kaldırıldı')
  }
}

function likeReply(replyId) {
  const reply = replies.value.find(r => r.id === replyId)
  if (reply) {
    reply.hasLiked = !reply.hasLiked
    reply.likes += reply.hasLiked ? 1 : -1
    window.$message?.success(reply.hasLiked ? 'Begenildi' : 'Begeni kaldırıldı')
  }
}

function bookmarkTopic() {
  hasBookmarked.value = !hasBookmarked.value
  window.$message?.success(hasBookmarked.value ? 'Yer işaretlerine eklendi' : 'Yer işaretlerinden kaldırıldı')
}

function quoteReply(reply) {
  quotedReply.value = reply
  const quoteText = `> **${reply.author}** yazdi:\n> ${reply.content.replace(/\n/g, '\n> ')}\n\n`
  newReply.value = quoteText + newReply.value
  scrollToReplyForm()
  window.$message?.info('Alıntı eklendi')
}

function replyToUser(reply) {
  newReply.value = `@${reply.author} ` + newReply.value
  scrollToReplyForm()
}

function clearQuote() {
  quotedReply.value = null
}

function scrollToReply(replyId) {
  const element = document.getElementById(`reply-${replyId}`)
  if (element) {
    highlightedReplyId.value = replyId
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })

    setTimeout(() => {
      highlightedReplyId.value = null
    }, 2000)
  }

  // Copy link to clipboard
  const url = `${window.location.origin}${window.location.pathname}#reply-${replyId}`
  navigator.clipboard.writeText(url)
  window.$message?.success('Yanıt linki kopyalandi')
}

function scrollToReplyForm() {
  nextTick(() => {
    const element = document.getElementById('reply-form')
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      editorRef.value?.focus()
    }
  })
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value)
  window.$message?.success('Link kopyalandi')
}

function shareToSocial(social) {
  const encodedUrl = encodeURIComponent(shareUrl.value)
  const encodedTitle = encodeURIComponent(topic.value?.title || '')

  const urls = {
    Twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
    Facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    LinkedIn: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    'E-posta': `mailto:?subject=${encodedTitle}&body=${encodedUrl}`
  }

  if (urls[social.name]) {
    window.open(urls[social.name], '_blank')
  }
  showShareModal.value = false
}

function reportReply(reply) {
  editingItem.value = reply
  showReportModal.value = true
}

function submitReport() {
  if (reportForm.value.reason) {
    window.$message?.success('Bildiriminiz alındı')
    showReportModal.value = false
    reportForm.value = { reason: null, description: '' }
  } else {
    window.$message?.error('Lütfen bir neden seçin')
  }
}

function handlePostAction(key) {
  if (key === 'edit') {
    editContent.value = topic.value?.content || ''
    editingItem.value = topic.value
    showEditModal.value = true
  } else if (key === 'delete') {
    deletingItem.value = topic.value
    showDeleteModal.value = true
  }
}

function handleReplyAction(key, reply) {
  if (key === 'edit') {
    editContent.value = reply.content
    editingItem.value = reply
    showEditModal.value = true
  } else if (key === 'delete') {
    deletingItem.value = reply
    showDeleteModal.value = true
  }
}

function saveEdit() {
  if (editingItem.value) {
    if (editingItem.value.id === topic.value?.id) {
      topic.value.content = editContent.value
      topic.value.isEdited = true
    } else {
      const reply = replies.value.find(r => r.id === editingItem.value.id)
      if (reply) {
        reply.content = editContent.value
        reply.isEdited = true
      }
    }
    window.$message?.success('Gönderi güncellendi')
    showEditModal.value = false
    editingItem.value = null
    editContent.value = ''
  }
}

function confirmDelete() {
  if (deletingItem.value) {
    if (deletingItem.value.id !== topic.value?.id) {
      const index = replies.value.findIndex(r => r.id === deletingItem.value.id)
      if (index > -1) {
        replies.value.splice(index, 1)
      }
    }
    window.$message?.success('Gönderi silindi')
    showDeleteModal.value = false
    deletingItem.value = null
  }
}

function applyFormat(action) {
  const textarea = editorRef.value?.$el?.querySelector('textarea')
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = newReply.value.substring(start, end)

  let replacement = ''
  let cursorOffset = 0

  switch (action) {
    case 'bold':
      replacement = `**${selectedText || 'kalın metin'}**`
      cursorOffset = selectedText ? 0 : -2
      break
    case 'italic':
      replacement = `*${selectedText || 'italik metin'}*`
      cursorOffset = selectedText ? 0 : -1
      break
    case 'code':
      replacement = selectedText.includes('\n')
        ? `\`\`\`\n${selectedText || 'kod'}\n\`\`\``
        : `\`${selectedText || 'kod'}\``
      break
    case 'quote':
      replacement = `> ${selectedText || 'alıntı'}`
      break
    case 'list':
      replacement = `- ${selectedText || 'liste ogesi'}`
      break
    case 'link':
      replacement = `[${selectedText || 'link metni'}](url)`
      cursorOffset = selectedText ? -1 : -4
      break
    case 'image':
      replacement = `![${selectedText || 'resim açıklamasi'}](url)`
      cursorOffset = selectedText ? -1 : -4
      break
  }

  newReply.value = newReply.value.substring(0, start) + replacement + newReply.value.substring(end)

  nextTick(() => {
    textarea.focus()
    const newPos = start + replacement.length + cursorOffset
    textarea.setSelectionRange(newPos, newPos)
  })
}

function insertEmoji(emoji) {
  const textarea = editorRef.value?.$el?.querySelector('textarea')
  if (!textarea) return

  const start = textarea.selectionStart
  newReply.value = newReply.value.substring(0, start) + emoji + newReply.value.substring(start)

  nextTick(() => {
    textarea.focus()
    const newPos = start + emoji.length
    textarea.setSelectionRange(newPos, newPos)
  })
}

function handleTyping() {
  // Simulate typing indicator (in real app, this would be websocket)
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }
}

function handleEditorFocus() {
  // Track focus for typing indicator
}

function saveDraft() {
  localStorage.setItem(`forum_draft_${topicId}`, newReply.value)
  window.$message?.success('Taslak kaydedildi')
}

function loadDraft() {
  const draft = localStorage.getItem(`forum_draft_${topicId}`)
  if (draft) {
    newReply.value = draft
    window.$message?.info('Taslak yüklendi')
  }
}

async function submitReply() {
  if (!newReply.value.trim()) return

  isSubmitting.value = true

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))

    replies.value.push({
      id: replies.value.length + 1,
      author: 'CurrentUser',
      authorId: currentUserId.value,
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=current',
      authorRole: 'Üye',
      authorLevel: 15,
      authorXpProgress: 40,
      authorPosts: 15,
      authorJoined: 'Oca 2025',
      authorOnline: true,
      created: 'Az önce',
      content: newReply.value,
      likes: 0,
      hasLiked: false,
      isEdited: false,
      quotedPost: quotedReply.value ? {
        id: quotedReply.value.id,
        author: quotedReply.value.author,
        content: quotedReply.value.content.substring(0, 100)
      } : null,
      reactions: []
    })

    newReply.value = ''
    quotedReply.value = null
    localStorage.removeItem(`forum_draft_${topicId}`)

    window.$message?.success('Yanıtiniz gönderildi')

    // Scroll to new reply
    nextTick(() => {
      const lastReply = document.getElementById(`reply-${replies.value[replies.value.length - 1].id}`)
      if (lastReply) {
        lastReply.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    })
  } catch (error) {
    window.$message?.error('Bir hata oluştu')
  } finally {
    isSubmitting.value = false
  }
}

// Scroll handling for floating bar and reading progress
function handleScroll() {
  showFloatingBar.value = window.scrollY > 400

  // Calculate reading progress
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
  const scrolled = window.scrollY
  readingProgress.value = Math.min((scrolled / scrollHeight) * 100, 100)
}

// Check for reply hash in URL
function checkUrlHash() {
  const hash = window.location.hash
  if (hash.startsWith('#reply-')) {
    const replyId = parseInt(hash.replace('#reply-', ''))
    if (replyId) {
      nextTick(() => {
        scrollToReply(replyId)
      })
    }
  }
}

// Simulate typing users (mock)
function simulateTypingUsers() {
  const users = ['AdminUser', 'ProGamer']
  const randomUser = users[Math.floor(Math.random() * users.length)]

  if (Math.random() > 0.7 && typingUsers.value.length === 0) {
    typingUsers.value.push(randomUser)
    setTimeout(() => {
      typingUsers.value = typingUsers.value.filter(u => u !== randomUser)
    }, 3000)
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  checkUrlHash()
  loadDraft()

  // Simulate typing indicator periodically
  const typingInterval = setInterval(simulateTypingUsers, 5000)

  onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
    clearInterval(typingInterval)
  })
})

// Watch for hash changes
watch(() => route.hash, () => {
  checkUrlHash()
})
</script>

<style scoped>
/* Reading Progress Indicator */
.reading-progress-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  z-index: 9999;
}

.reading-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fb923c, #fbbf24);
  transition: width 0.1s ease-out;
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
}

/* Animations */
@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

@keyframes float-delayed {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(-5deg); }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes like-pop {
  0% { transform: scale(1); }
  25% { transform: scale(1.3); }
  50% { transform: scale(0.9); }
  75% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 5px rgba(249, 115, 22, 0.5); }
  50% { box-shadow: 0 0 25px rgba(249, 115, 22, 0.8), 0 0 50px rgba(249, 115, 22, 0.4); }
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes level-progress {
  from { stroke-dasharray: 0 339; }
}

@keyframes particle-fly {
  0% { opacity: 1; transform: translate(0, 0) scale(1); }
  100% { opacity: 0; transform: translate(var(--tx), var(--ty)) scale(0); }
}

.animate-float {
  animation: float 8s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 10s ease-in-out infinite;
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out forwards;
  opacity: 0;
}

.animate-like {
  animation: like-pop 0.6s ease-out;
}

/* Glass Morphism */
.glass-morphism {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.glass-morphism-strong {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* Gradient Text */
.text-gradient-animated {
  background: linear-gradient(90deg, #f97316, #fb923c, #fbbf24, #f97316);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 3s linear infinite;
}

/* Floating Action Bar */
.floating-action-bar {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1), 0 0 60px rgba(249, 115, 22, 0.1);
}

.fab-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 12px;
  color: #9ca3af;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent;
  border: none;
  cursor: pointer;
}

.fab-button:hover {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  transform: translateY(-2px);
}

.fab-button.liked {
  color: #ef4444;
}

.fab-button.liked svg {
  fill: #ef4444;
}

.fab-count {
  font-size: 12px;
  font-weight: 600;
}

/* Breadcrumb */
.breadcrumb-nav {
  overflow-x: auto;
}

.breadcrumb-item {
  background: none;
  border: none;
  cursor: pointer;
}

/* Stat Chips */
.stat-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  color: #9ca3af;
  font-size: 13px;
  transition: all 0.3s ease;
}

.stat-chip:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

/* Tags */
.tag-glow-orange {
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.3);
}

.tag-glow-red {
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
}

.tag-hot {
  background: linear-gradient(135deg, #ef4444, #f97316) !important;
  border: none !important;
  color: white !important;
}

/* Avatar Level Ring */
.avatar-ring-container {
  position: relative;
  width: 112px;
  height: 112px;
}

.avatar-ring-small {
  position: relative;
  width: 72px;
  height: 72px;
}

.avatar-level-ring {
  width: 100%;
  height: 100%;
}

.level-progress {
  animation: level-progress 1s ease-out forwards;
  transition: stroke-dasharray 0.5s ease;
}

.level-badge {
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  font-size: 11px;
  font-weight: bold;
  padding: 3px 10px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.4);
  display: flex;
  align-items: center;
}

.level-badge-small {
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(249, 115, 22, 0.3);
}

/* Role Badges */
.role-badge, .role-badge-small {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-badge-small {
  padding: 2px 8px;
  font-size: 10px;
}

.role-admin {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);
}

.role-mod {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.role-vip {
  background: linear-gradient(135deg, #eab308, #ca8a04);
  color: white;
  box-shadow: 0 2px 8px rgba(234, 179, 8, 0.3);
}

.role-member {
  background: rgba(255, 255, 255, 0.1);
  color: #9ca3af;
}

.role-newbie {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

/* Author Stats Grid */
.author-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
}

.author-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.author-stat-item.full-width {
  grid-column: 1 / -1;
  flex-direction: row;
  justify-content: center;
  gap: 8px;
}

.author-stat-item .stat-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.author-stat-item .stat-label {
  font-size: 10px;
  color: #6b7280;
  text-transform: uppercase;
}

/* Reply Author Stats */
.reply-author-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
  font-size: 11px;
  color: #6b7280;
}

.reply-author-stats span {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

/* Badge Icons */
.badge-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.badge-icon:hover {
  transform: scale(1.15) rotate(5deg);
}

/* Reactions */
.reaction-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.reaction-button:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.reaction-button.active {
  background: rgba(249, 115, 22, 0.2);
  border-color: rgba(249, 115, 22, 0.4);
}

.reaction-button.add-reaction {
  color: #6b7280;
}

.reaction-count {
  font-size: 12px;
  color: #9ca3af;
}

.reaction-button-small {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.reaction-button-small.active {
  background: rgba(249, 115, 22, 0.15);
  border-color: rgba(249, 115, 22, 0.3);
}

.emoji-picker-item {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: none;
  border: none;
  font-size: 18px;
}

.emoji-picker-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.2);
}

/* Animated Like Button */
.like-button-animated {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.like-button-animated:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.like-button-animated.liked {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.like-button-animated.liked .like-icon {
  fill: #ef4444;
  color: #ef4444;
}

.like-button-animated.animating .like-icon {
  animation: like-pop 0.6s ease-out;
}

.like-button-animated .like-particles {
  position: absolute;
  top: 50%;
  left: 20px;
  pointer-events: none;
}

.like-button-animated.animating .particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #ef4444;
  border-radius: 50%;
  animation: particle-fly 0.6s ease-out forwards;
}

.like-button-animated.animating .particle:nth-child(1) { --tx: -20px; --ty: -20px; }
.like-button-animated.animating .particle:nth-child(2) { --tx: 20px; --ty: -20px; }
.like-button-animated.animating .particle:nth-child(3) { --tx: -25px; --ty: 0px; }
.like-button-animated.animating .particle:nth-child(4) { --tx: 25px; --ty: 0px; }
.like-button-animated.animating .particle:nth-child(5) { --tx: -15px; --ty: 15px; }
.like-button-animated.animating .particle:nth-child(6) { --tx: 15px; --ty: 15px; }

/* Reply Like Button */
.reply-like-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
}

.reply-like-btn:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.reply-like-btn.liked {
  color: #ef4444;
}

.reply-like-btn.liked svg {
  fill: #ef4444;
}

/* Action Buttons */
.action-button {
  transition: all 0.2s ease;
}

.action-button:hover {
  transform: translateY(-2px);
}

/* Reply Cards with Alternating Backgrounds */
.reply-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.reply-card.reply-even {
  background: rgba(255, 255, 255, 0.02);
}

.reply-card.reply-odd {
  background: rgba(249, 115, 22, 0.02);
}

.reply-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.reply-card.highlighted {
  border-color: #f97316 !important;
  box-shadow: 0 0 30px rgba(249, 115, 22, 0.3);
  animation: pulse-glow 1s ease-in-out 2;
}

.reply-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 22px;
  padding: 0 8px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
  color: #f97316;
  border-radius: 11px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.reply-action-btn {
  transition: all 0.2s ease;
}

.reply-action-btn:hover {
  transform: translateY(-1px);
}

/* Quote Block */
.quote-block {
  padding: 16px;
  border-left: 4px solid #f97316;
  background: linear-gradient(90deg, rgba(249, 115, 22, 0.08), transparent);
  border-radius: 0 12px 12px 0;
  position: relative;
}

.quote-block::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h20v20H0z' fill='none'/%3E%3Cpath d='M10 15l-5-5 1.41-1.41L10 12.17l7.59-7.59L19 6l-9 9z' fill='%23f9731608'/%3E%3C/svg%3E");
  pointer-events: none;
}

.quote-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.quote-content {
  color: #d1d5db;
  font-size: 14px;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.quote-jump-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 4px 8px;
  background: rgba(249, 115, 22, 0.1);
  border: none;
  border-radius: 6px;
  color: #f97316;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quote-jump-btn:hover {
  background: rgba(249, 115, 22, 0.2);
  transform: translateX(4px);
}

.quote-form-preview {
  background: linear-gradient(90deg, rgba(249, 115, 22, 0.08), transparent);
}

/* Editor Toolbar */
.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 12px;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.toolbar-group {
  display: flex;
  gap: 2px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.15);
  margin: 0 8px;
}

.editor-tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 8px;
  border-radius: 8px;
  color: #9ca3af;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 4px;
}

.editor-tool-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.editor-tool-btn.active {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.preview-toggle {
  padding: 0 12px;
}

.preview-toggle span {
  font-size: 12px;
}

.editor-container {
  display: flex;
  gap: 16px;
}

.editor-container.split-view .editor-pane {
  flex: 1;
}

.editor-pane {
  flex: 1;
}

.preview-pane {
  flex: 1;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: auto;
  max-height: 250px;
}

.preview-content {
  min-height: 100px;
}

.custom-textarea :deep(textarea) {
  background: rgba(0, 0, 0, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 12px !important;
  font-family: inherit;
  line-height: 1.7;
}

.custom-textarea :deep(textarea):focus {
  border-color: #f97316 !important;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15) !important;
}

.submit-btn {
  background: linear-gradient(135deg, #f97316, #ea580c) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(249, 115, 22, 0.4);
}

/* Typing Indicator */
.typing-indicator {
  display: inline-flex;
}

.typing-dots {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #f97316;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }
.typing-dots span:nth-child(3) { animation-delay: 0s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* Attachment Chips */
.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #9ca3af;
  font-size: 13px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.attachment-chip:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  color: #f97316;
  transform: translateY(-2px);
}

/* Share Modal */
.share-modal-content {
  padding: 8px 0;
}

.share-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
}

.share-preview-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 12px;
}

.share-preview-text {
  flex: 1;
  overflow: hidden;
}

.share-preview-text h4 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.share-url-container {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.share-url-input {
  flex: 1;
}

.copy-btn {
  flex-shrink: 0;
}

.share-divider {
  position: relative;
  text-align: center;
  margin-bottom: 24px;
}

.share-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.share-divider span {
  position: relative;
  padding: 0 16px;
  background: var(--n-color);
  color: #6b7280;
  font-size: 12px;
}

.social-share-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.social-share-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.social-share-btn:hover {
  background: var(--social-color);
  border-color: var(--social-color);
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.social-share-btn span {
  font-size: 11px;
}

/* Report Modal */
.report-modal-content {
  padding: 8px 0;
}

.report-icon-container {
  width: 64px;
  height: 64px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 50%;
  border: 2px solid rgba(239, 68, 68, 0.2);
}

.report-reasons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-reason-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.report-reason-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.report-reason-item.selected {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

/* Locked Message */
.locked-icon-container {
  width: 96px;
  height: 96px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 50%;
  border: 2px solid rgba(239, 68, 68, 0.3);
}

/* Markdown Body Styling */
.markdown-body {
  color: #d1d5db;
  line-height: 1.8;
  font-size: 15px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  color: var(--text-primary);
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 700;
}

.markdown-body :deep(p) {
  margin-bottom: 1em;
}

.markdown-body :deep(a) {
  color: #f97316;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s ease;
}

.markdown-body :deep(a:hover) {
  border-bottom-color: #f97316;
}

.markdown-body :deep(code) {
  background: rgba(249, 115, 22, 0.1);
  color: #fb923c;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: 'Fira Code', monospace;
}

.markdown-body :deep(pre) {
  background: rgba(0, 0, 0, 0.4);
  padding: 20px;
  border-radius: 16px;
  overflow-x: auto;
  margin: 1.5em 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  color: #e5e7eb;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #f97316;
  padding: 12px 20px;
  margin: 1.5em 0;
  background: linear-gradient(90deg, rgba(249, 115, 22, 0.08), transparent);
  border-radius: 0 12px 12px 0;
  color: #d1d5db;
  font-style: italic;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 28px;
  margin: 1em 0;
}

.markdown-body :deep(li) {
  margin-bottom: 0.5em;
}

.markdown-body :deep(li::marker) {
  color: #f97316;
}

.markdown-body :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 16px;
  margin: 1.5em 0;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.markdown-body :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  margin: 2em 0;
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.reply-list-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.reply-list-leave-active {
  transition: all 0.3s ease;
}

.reply-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.reply-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.reply-list-move {
  transition: transform 0.3s ease;
}

/* Responsive */
@media (max-width: 1024px) {
  .author-sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .reply-author-sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .editor-container.split-view {
    flex-direction: column;
  }

  .social-share-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .floating-action-bar {
    padding: 12px 16px;
  }

  .fab-button {
    padding: 8px;
  }

  .fab-count {
    display: none;
  }

  .stat-chip span {
    display: none;
  }

  .stat-chip {
    padding: 8px;
    border-radius: 50%;
  }

  .author-stats-grid {
    grid-template-columns: 1fr;
  }

  .like-button-animated .like-text {
    display: none;
  }
}
</style>
