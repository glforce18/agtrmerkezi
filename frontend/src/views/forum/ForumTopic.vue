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
      <div class="glass-card p-6 mb-6 fade-in-up">
        <!-- Title & Badges -->
        <div class="flex items-start gap-3 mb-4">
          <h1 class="text-2xl md:text-3xl font-bold text-gradient-animated flex-1">
            {{ topic.title }}
          </h1>
          <div class="flex gap-2 flex-shrink-0 flex-wrap">
            <span v-if="topic.is_pinned" class="badge bg-yellow-500/10 text-yellow-500 border border-yellow-500/30">
              📌 Sabitlendi
            </span>
            <span v-if="topic.is_locked" class="badge bg-red-500/10 text-red-500 border border-red-500/30">
              🔒 Kilitli
            </span>
            <span v-if="topic.is_solved" class="badge bg-green-500/10 text-green-500 border border-green-500/30">
              ✅ Çözüldü
            </span>
          </div>
        </div>

        <!-- Meta Info with Steam -->
        <div class="flex flex-wrap items-center gap-4 text-sm text-text-secondary">
          <div class="flex items-center gap-2">
            <img
              v-if="topic.author?.avatar"
              :src="topic.author.avatar"
              :alt="topic.author?.username"
              class="w-7 h-7 rounded-full ring-2 ring-primary/30"
            />
            <div v-else class="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white text-xs font-bold">
              {{ getInitials(topic.author?.username) }}
            </div>
            <span class="font-semibold text-text-primary">{{ topic.author?.username || 'Anonim' }}</span>
            <a
              v-if="topic.author?.steam_id"
              :href="`https://steamcommunity.com/profiles/${topic.author.steam_id}`"
              target="_blank"
              class="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-blue-600/20 to-blue-500/20 hover:from-blue-600/30 hover:to-blue-500/30 text-blue-400 text-xs font-medium rounded-md border border-blue-500/30 hover:border-blue-500/50 transition-all"
              title="Steam Profiline Git">
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
              </svg>
              <span>Steam</span>
            </a>
          </div>
          <span class="hidden sm:inline">•</span>
          <span class="hidden sm:inline">{{ formatDate(topic.created_at) }}</span>
          <span class="hidden sm:inline">•</span>
          <div class="flex items-center gap-1.5 px-2 py-1 bg-dark-elevated rounded">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
            <span class="font-medium">{{ topic.view_count || 0 }}</span>
          </div>
          <div class="flex items-center gap-1.5 px-2 py-1 bg-primary/10 text-primary rounded">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <span class="font-bold">{{ topic.post_count || 0 }} yanıt</span>
          </div>
        </div>
      </div>

      <!-- Original Post (OP) -->
      <div class="glass-card mb-6 fade-in-up delay-100">
        <div class="p-6 border-b border-dark-border/50">
          <!-- Author Info Bar -->
          <div class="flex items-start gap-4">
            <!-- Author Sidebar -->
            <div class="flex-shrink-0 w-32 hidden md:block">
              <div class="sticky top-24">
                <div class="flex flex-col items-center">
                  <img
                    v-if="topic.author?.avatar"
                    :src="topic.author.avatar"
                    :alt="topic.author?.username"
                    class="w-20 h-20 rounded-full ring-2 ring-primary/30 mb-3"
                  />
                  <div v-else class="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white text-2xl font-bold mb-3">
                    {{ getInitials(topic.author?.username) }}
                  </div>
                  <div class="text-center mb-2">
                    <div class="font-semibold text-text-primary text-sm">{{ topic.author?.username || 'Anonim' }}</div>
                    <div class="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded mt-1">
                      {{ getRoleBadge(topic.author?.role) }}
                    </div>
                  </div>
                  <div v-if="topic.author?.steam_id" class="w-full">
                    <a
                      :href="`https://steamcommunity.com/profiles/${topic.author.steam_id}`"
                      target="_blank"
                      class="flex items-center justify-center gap-1.5 text-xs px-3 py-2 bg-gradient-to-r from-blue-600/20 to-blue-500/20 hover:from-blue-600/30 hover:to-blue-500/30 text-blue-400 font-medium rounded-lg border border-blue-500/30 hover:border-blue-500/50 transition-all group"
                      title="Steam Profiline Git">
                      <svg class="w-3.5 h-3.5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
                      </svg>
                      <span>Steam</span>
                    </a>
                  </div>
                  <div class="text-xs text-text-muted mt-2 text-center">
                    {{ topic.author?.post_count || 0 }} mesaj
                  </div>
                </div>
              </div>
            </div>

            <!-- Mobile Author Header -->
            <div class="flex items-center gap-3 md:hidden mb-4 w-full">
              <img
                v-if="topic.author?.avatar"
                :src="topic.author.avatar"
                :alt="topic.author?.username"
                class="w-12 h-12 rounded-full ring-2 ring-primary/30"
              />
              <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white font-bold">
                {{ getInitials(topic.author?.username) }}
              </div>
              <div class="flex-1">
                <div class="font-semibold text-text-primary">{{ topic.author?.username || 'Anonim' }}</div>
                <div class="flex items-center gap-2 text-xs text-text-muted">
                  <span>{{ getRoleBadge(topic.author?.role) }}</span>
                  <span v-if="topic.author?.steam_id">• 🎮 Steam</span>
                </div>
              </div>
            </div>

            <!-- Post Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-4 md:mb-3">
                <div class="text-xs px-2 py-1 bg-primary/5 text-primary rounded border border-primary/20">
                  KONU YAZARI
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
        <div class="px-6 py-3 bg-dark-elevated/50 flex items-center justify-between flex-wrap gap-3">
          <div class="flex items-center gap-2 flex-wrap">
            <button
              @click="handleTopicLike"
              :disabled="likeLoading || !authStore.isAuthenticated"
              :class="topicLiked ? 'text-green-500 bg-green-500/10' : ''"
              class="btn btn-ghost text-sm px-3 py-1.5 hover:bg-green-500/10 hover:text-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              <span v-if="likeLoading" class="text-base">⏳</span>
              <span v-else class="text-base">👍</span>
              <span>{{ topicLiked ? 'Beğendin' : 'Beğen' }}</span>
              <span class="text-xs opacity-60">({{ topicLikes }})</span>
            </button>
            <button
              @click="handleBookmark"
              :disabled="bookmarkLoading || !authStore.isAuthenticated"
              :class="isBookmarked ? 'text-blue-500 bg-blue-500/10' : ''"
              class="btn btn-ghost text-sm px-3 py-1.5 hover:bg-blue-500/10 hover:text-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              <span v-if="bookmarkLoading" class="text-base">⏳</span>
              <span v-else class="text-base">🔖</span>
              <span>{{ isBookmarked ? 'Kaydedildi' : 'Kaydet' }}</span>
            </button>
            <button
              @click="handleShare"
              :disabled="shareLoading"
              class="btn btn-ghost text-sm px-3 py-1.5 hover:bg-primary/10 hover:text-primary transition-colors">
              <span v-if="shareLoading" class="text-base">⏳</span>
              <span v-else class="text-base">🔗</span>
              <span>Paylaş</span>
            </button>
          </div>
          <div v-if="canModerate" class="flex items-center gap-2">
            <button
              @click="handleEdit"
              class="btn btn-ghost text-sm px-3 py-1.5 text-yellow-500 hover:bg-yellow-500/10">
              📝 Düzenle
            </button>
            <button
              @click="handleDelete"
              class="btn btn-ghost text-sm px-3 py-1.5 text-red-500 hover:bg-red-500/10">
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
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="font-semibold text-text-primary">
                      {{ reply.author?.username || 'Anonim' }}
                    </span>
                    <span v-if="reply.is_best_answer" class="badge badge-success text-xs">
                      ✅ En İyi Cevap
                    </span>
                    <span v-if="reply.parent_reply_id" class="text-xs px-2 py-1 bg-primary/10 text-primary rounded border border-primary/30">
                      💬 Bir yanıta yanıt
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm text-text-muted">#{{ index + 1 }}</span>
                    <span class="text-sm text-text-muted">{{ formatDateTime(reply.created_at) }}</span>
                  </div>
                </div>

                <!-- Reply Text (Edit Mode) -->
                <div v-if="editingReply === reply.id" class="mb-3">
                  <textarea
                    v-model="editReplyContent"
                    class="textarea mb-2"
                    rows="4"
                  ></textarea>
                  <div class="flex gap-2">
                    <button @click="handleReplyEditSave(reply)" class="btn btn-primary btn-sm">
                      Kaydet
                    </button>
                    <button @click="handleReplyEditCancel" class="btn btn-secondary btn-sm">
                      İptal
                    </button>
                  </div>
                </div>

                <!-- Reply Text (View Mode) -->
                <div v-else class="prose prose-invert max-w-none">
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
          <div class="px-6 py-3 bg-dark-elevated flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center gap-2">
              <button
                @click="handleReplyLike(reply.id)"
                :disabled="replyLikeLoading[reply.id]"
                :class="replyLikes[reply.id]?.liked ? 'text-green-500 bg-green-500/10' : ''"
                class="btn btn-ghost text-sm px-3 py-1 hover:bg-green-500/10 hover:text-green-500 transition-colors">
                <span v-if="replyLikeLoading[reply.id]">⏳</span>
                <span v-else>👍</span>
                {{ replyLikes[reply.id]?.liked ? 'Beğendin' : 'Beğen' }} ({{ replyLikes[reply.id]?.count || 0 }})
              </button>
              <button
                @click="handleReplyToReply(reply)"
                class="btn btn-ghost text-sm px-3 py-1 hover:bg-primary/10 hover:text-primary transition-colors">
                💬 Yanıtla
              </button>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="canMarkBestAnswer(reply)"
                @click="handleBestAnswer(reply)"
                :class="reply.is_best_answer ? 'text-green-500 bg-green-500/10' : 'text-text-muted hover:bg-green-500/10 hover:text-green-500'"
                class="btn btn-ghost text-sm px-3 py-1 transition-colors">
                {{ reply.is_best_answer ? '✅ En İyi Cevap' : '✅ En İyi Cevap Olarak İşaretle' }}
              </button>
              <button
                v-if="canEditReply(reply)"
                @click="handleReplyEdit(reply)"
                class="btn btn-ghost text-sm px-3 py-1 text-yellow-500 hover:bg-yellow-500/10">
                📝 Düzenle
              </button>
              <button
                v-if="canEditReply(reply)"
                @click="handleReplyDelete(reply)"
                class="btn btn-ghost text-sm px-3 py-1 text-red-500 hover:bg-red-500/10">
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
      <div v-if="!topic.is_locked && authStore.isAuthenticated" class="card p-6 reply-form">
        <h3 class="text-lg font-semibold text-text-primary mb-4">Yanıt Yaz</h3>

        <!-- Replying To Indicator -->
        <div v-if="replyingTo" class="bg-primary/10 border border-primary/30 rounded-lg px-4 py-3 mb-4 flex items-center justify-between">
          <div class="flex items-center gap-2 text-primary">
            <span class="text-lg">💬</span>
            <span class="font-medium">@{{ replyingTo.username }} kullanıcısına yanıt veriyorsunuz</span>
          </div>
          <button
            @click="replyingTo = null"
            class="text-primary hover:bg-primary/10 rounded p-1 transition-colors"
            type="button">
            ❌
          </button>
        </div>

        <form @submit.prevent="submitReply">
          <textarea
            v-model="replyContent"
            class="textarea mb-4"
            rows="6"
            placeholder="Yanıtınızı yazın..."
            required
          ></textarea>
          <div class="flex justify-end gap-3">
            <button type="button" class="btn btn-secondary" @click="replyContent = ''; replyingTo = null">
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
        Yanıt yazmak için <router-link to="/login" class="font-semibold underline">giriş yapın</router-link>.
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

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm" @click.self="showEditModal = false" @keydown.esc="showEditModal = false" tabindex="0">
      <div class="card max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h3 class="text-2xl font-bold text-text-primary mb-4">Konuyu Düzenle</h3>

          <div class="mb-4">
            <label class="block text-sm font-medium text-text-secondary mb-2">Başlık</label>
            <input
              v-model="editTitle"
              type="text"
              class="input"
              placeholder="Konu başlığı..."
            />
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-text-secondary mb-2">İçerik</label>
            <textarea
              v-model="editContent"
              class="textarea"
              rows="10"
              placeholder="Konu içeriği..."
            ></textarea>
          </div>

          <div class="flex justify-end gap-3">
            <button
              @click="showEditModal = false"
              class="btn btn-secondary">
              İptal
            </button>
            <button
              @click="handleEditSave"
              class="btn btn-primary">
              Kaydet
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Topic Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm" @click.self="showDeleteModal = false" @keydown.esc="showDeleteModal = false" tabindex="0">
      <div class="card max-w-md w-full">
        <div class="p-6">
          <div class="text-center mb-6">
            <div class="text-5xl mb-3">⚠️</div>
            <h3 class="text-xl font-bold text-text-primary mb-2">Konuyu Sil</h3>
            <p class="text-text-secondary">Bu işlem geri alınamaz. Konu ve tüm yanıtlar silinecek.</p>
          </div>

          <div class="flex justify-center gap-3">
            <button
              @click="showDeleteModal = false"
              class="btn btn-secondary">
              İptal
            </button>
            <button
              @click="handleDeleteConfirm"
              class="btn bg-red-500 hover:bg-red-600 text-white">
              Evet, Sil
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Reply Confirmation Modal -->
    <div v-if="showDeleteReplyModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm" @click.self="showDeleteReplyModal = false" @keydown.esc="showDeleteReplyModal = false" tabindex="0">
      <div class="card max-w-md w-full">
        <div class="p-6">
          <div class="text-center mb-6">
            <div class="text-5xl mb-3">⚠️</div>
            <h3 class="text-xl font-bold text-text-primary mb-2">Yanıtı Sil</h3>
            <p class="text-text-secondary">Bu işlem geri alınamaz. Yanıt kalıcı olarak silinecek.</p>
          </div>

          <div class="flex justify-center gap-3">
            <button
              @click="showDeleteReplyModal = false; deletingReply = null"
              class="btn btn-secondary">
              İptal
            </button>
            <button
              @click="handleReplyDeleteConfirm"
              class="btn bg-red-500 hover:bg-red-600 text-white">
              Evet, Sil
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import forumAPI from '@/api/forum'
import { useToast } from '@/composables/useToast'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(true)
const topic = ref(null)
const replies = ref([])
const replyContent = ref('')
const submitting = ref(false)

// Like system state
const topicLiked = ref(false)
const topicLikes = ref(0)
const replyLikes = ref({}) // { replyId: { liked: bool, count: number } }

// Bookmark state
const isBookmarked = ref(false)

// Edit/Delete state
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showDeleteReplyModal = ref(false)
const deletingReply = ref(null)
const editContent = ref('')
const editTitle = ref('')
const editingReply = ref(null)
const editReplyContent = ref('')

// Nested reply state
const replyingTo = ref(null) // { id, username } of parent reply

// Loading states
const likeLoading = ref(false)
const bookmarkLoading = ref(false)
const shareLoading = ref(false)
const replyLikeLoading = ref({}) // { replyId: boolean }

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

    // Initialize like state for topic
    if (topic.value) {
      topicLiked.value = topic.value.is_liked || false
      topicLikes.value = topic.value.likes || 0
      isBookmarked.value = topic.value.is_bookmarked || false
    }

    // Fetch replies for the topic
    if (topic.value?.id) {
      try {
        const repliesResponse = await forumAPI.getReplies(topic.value.id)
        // API returns: { success: true, data: [...], pagination: {...} }
        const replyData = repliesResponse.data.data || repliesResponse.data
        replies.value = Array.isArray(replyData) ? replyData : []

        // Initialize like state for each reply
        replies.value.forEach(reply => {
          replyLikes.value[reply.id] = {
            liked: reply.is_liked || false,
            count: reply.likes || 0
          }
        })
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
      content: replyContent.value,
      parent_reply_id: replyingTo.value?.id || null
    })

    replyContent.value = ''
    replyingTo.value = null
    await fetchTopic()
    toast.show('Yanıt gönderildi ✅', 'success')
  } catch (error) {
    console.error('Failed to submit reply:', error)
    toast.show('Yanıt gönderilemedi', 'error')
  } finally {
    submitting.value = false
  }
}

// Handle nested reply
const handleReplyToReply = (reply) => {
  replyingTo.value = { id: reply.id, username: reply.author?.username || 'Anonim' }
  // Scroll to reply form
  setTimeout(() => {
    const replyForm = document.querySelector('.reply-form')
    if (replyForm) {
      replyForm.scrollIntoView({ behavior: 'smooth', block: 'center' })
      const textarea = replyForm.querySelector('textarea')
      if (textarea) textarea.focus()
    }
  }, 100)
}

// Like handlers with optimistic updates
const handleTopicLike = async () => {
  if (!authStore.isAuthenticated) {
    toast.show('Beğenmek için giriş yapmalısınız', 'warning')
    return
  }

  if (likeLoading.value) return

  // Optimistic update
  const previousLiked = topicLiked.value
  const previousCount = topicLikes.value

  try {
    likeLoading.value = true

    // Update UI immediately
    if (topicLiked.value) {
      topicLikes.value--
      topicLiked.value = false
    } else {
      topicLikes.value++
      topicLiked.value = true
    }

    // Then make API call
    if (previousLiked) {
      await forumAPI.unlikeTopic(topic.value.id)
      toast.show('Beğeni kaldırıldı', 'info')
    } else {
      await forumAPI.likeTopic(topic.value.id)
      toast.show('Konu beğenildi ❤️', 'success')
    }
  } catch (error) {
    // Rollback on error
    topicLiked.value = previousLiked
    topicLikes.value = previousCount
    console.error('Failed to toggle topic like:', error)
    toast.show('Bir hata oluştu', 'error')
  } finally {
    likeLoading.value = false
  }
}

const handleReplyLike = async (replyId) => {
  if (!authStore.isAuthenticated) {
    toast.show('Beğenmek için giriş yapmalısınız', 'warning')
    return
  }

  if (replyLikeLoading.value[replyId]) return

  // Optimistic update
  const currentState = replyLikes.value[replyId]
  const previousState = { ...currentState }

  try {
    replyLikeLoading.value[replyId] = true

    // Update UI immediately
    if (currentState.liked) {
      replyLikes.value[replyId] = {
        liked: false,
        count: currentState.count - 1
      }
    } else {
      replyLikes.value[replyId] = {
        liked: true,
        count: currentState.count + 1
      }
    }

    // Then make API call
    if (previousState.liked) {
      await forumAPI.unlikeReply(replyId)
      toast.show('Beğeni kaldırıldı', 'info')
    } else {
      await forumAPI.likeReply(replyId)
      toast.show('Yanıt beğenildi ❤️', 'success')
    }
  } catch (error) {
    // Rollback on error
    replyLikes.value[replyId] = previousState
    console.error('Failed to toggle reply like:', error)
    toast.show('Bir hata oluştu', 'error')
  } finally {
    replyLikeLoading.value[replyId] = false
  }
}

// Bookmark handler with optimistic updates
const handleBookmark = async () => {
  if (!authStore.isAuthenticated) {
    toast.show('Kaydetmek için giriş yapmalısınız', 'warning')
    return
  }

  if (bookmarkLoading.value) return

  const previousBookmarked = isBookmarked.value

  try {
    bookmarkLoading.value = true

    // Update UI immediately
    isBookmarked.value = !isBookmarked.value

    // Then make API call
    if (previousBookmarked) {
      await forumAPI.unbookmarkTopic(topic.value.id)
      toast.show('Kaydedilenlerden kaldırıldı', 'info')
    } else {
      await forumAPI.bookmarkTopic(topic.value.id)
      toast.show('Kaydedilenlere eklendi 🔖', 'success')
    }
  } catch (error) {
    // Rollback on error
    isBookmarked.value = previousBookmarked
    console.error('Failed to toggle bookmark:', error)
    toast.show('Bir hata oluştu', 'error')
  } finally {
    bookmarkLoading.value = false
  }
}

// Share handler with loading state
const handleShare = async () => {
  if (shareLoading.value) return

  const url = window.location.href
  const title = topic.value.title

  try {
    shareLoading.value = true
    if (navigator.share) {
      // Mobile share API
      await navigator.share({ title, url })
    } else {
      // Desktop: Copy to clipboard
      await navigator.clipboard.writeText(url)
      toast.show('Link kopyalandı 🔗', 'success')
    }
  } catch (error) {
    // User cancelled or error occurred
    if (error.name !== 'AbortError') {
      console.error('Failed to share:', error)
      toast.show('Paylaşım başarısız', 'error')
    }
  } finally {
    shareLoading.value = false
  }
}

// Edit/Delete handlers for topics
const handleEdit = () => {
  editTitle.value = topic.value.title
  editContent.value = topic.value.content
  showEditModal.value = true
}

const handleEditSave = async () => {
  try {
    await forumAPI.updateTopic(topic.value.id, {
      title: editTitle.value,
      content: editContent.value
    })
    topic.value.title = editTitle.value
    topic.value.content = editContent.value
    showEditModal.value = false
    toast.show('Konu güncellendi ✅', 'success')
  } catch (error) {
    console.error('Failed to update topic:', error)
    toast.show('Güncelleme başarısız', 'error')
  }
}

const handleDelete = () => {
  showDeleteModal.value = true
}

const handleDeleteConfirm = async () => {
  try {
    await forumAPI.deleteTopic(topic.value.id)
    toast.show('Konu silindi 🗑️', 'success')
    setTimeout(() => {
      router.push('/forum')
    }, 1000)
  } catch (error) {
    console.error('Failed to delete topic:', error)
    toast.show('Silme başarısız', 'error')
    showDeleteModal.value = false
  }
}

// Edit/Delete handlers for replies
const handleReplyEdit = (reply) => {
  editingReply.value = reply.id
  editReplyContent.value = reply.content
}

const handleReplyEditSave = async (reply) => {
  try {
    await forumAPI.updateReply(reply.id, {
      content: editReplyContent.value
    })
    reply.content = editReplyContent.value
    editingReply.value = null
    editReplyContent.value = ''
    toast.show('Yanıt güncellendi ✅', 'success')
  } catch (error) {
    console.error('Failed to update reply:', error)
    toast.show('Güncelleme başarısız', 'error')
  }
}

const handleReplyEditCancel = () => {
  editingReply.value = null
  editReplyContent.value = ''
}

const handleReplyDelete = (reply) => {
  deletingReply.value = reply
  showDeleteReplyModal.value = true
}

const handleReplyDeleteConfirm = async () => {
  if (!deletingReply.value) return

  try {
    await forumAPI.deleteReply(deletingReply.value.id)
    replies.value = replies.value.filter(r => r.id !== deletingReply.value.id)
    toast.show('Yanıt silindi 🗑️', 'success')
    showDeleteReplyModal.value = false
    deletingReply.value = null
  } catch (error) {
    console.error('Failed to delete reply:', error)
    toast.show('Silme başarısız', 'error')
    showDeleteReplyModal.value = false
    deletingReply.value = null
  }
}

// Check if user can edit/delete reply
const canEditReply = (reply) => {
  return authStore.user && (authStore.user.is_admin || authStore.user.id === reply.author?.id)
}

// Best answer handler
const handleBestAnswer = async (reply) => {
  try {
    if (reply.is_best_answer) {
      await forumAPI.unmarkBestAnswer(reply.id)
      reply.is_best_answer = false
      toast.show('En iyi cevap işareti kaldırıldı', 'info')
    } else {
      // Remove best answer from any other reply first
      replies.value.forEach(r => {
        if (r.is_best_answer) r.is_best_answer = false
      })
      await forumAPI.markBestAnswer(reply.id)
      reply.is_best_answer = true
      topic.value.is_solved = true
      toast.show('En iyi cevap işaretlendi ✅', 'success')
    }
  } catch (error) {
    console.error('Failed to toggle best answer:', error)
    toast.show('İşlem başarısız', 'error')
  }
}

// Check if user can mark best answer (only topic author)
const canMarkBestAnswer = (reply) => {
  return authStore.user && authStore.user.id === topic.value?.author?.id
}

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const formatContent = (content) => {
  if (!content) return ''
  // Convert newlines to <br> and sanitize with DOMPurify
  const htmlContent = content.replace(/\n/g, '<br>')
  return DOMPurify.sanitize(htmlContent, {
    ALLOWED_TAGS: ['br', 'b', 'i', 'u', 'strong', 'em', 'p', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel']
  })
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

const getRoleBadge = (role) => {
  const roleBadges = {
    'superadmin': '👑 Yönetici',
    'admin': '⚡ Admin',
    'moderator': '🛡️ Moderatör',
    'user': '👤 Üye'
  }
  return roleBadges[role] || roleBadges['user']
}
</script>
