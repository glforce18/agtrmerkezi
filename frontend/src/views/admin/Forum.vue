<template>
  <AdminLayout>
    <div class="forum-admin">
      <!-- Header Section -->
      <header class="page-header">
        <div class="header-content">
          <div class="header-info">
            <h1 class="page-title">
              <MessageSquare :size="28" class="title-icon" />
              Forum Yonetimi
            </h1>
            <p class="page-subtitle">Kategoriler, konular ve moderasyon araclari</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-secondary" @click="refreshData">
              <RefreshCw :size="18" :class="{ spinning: refreshing }" />
              <span>Yenile</span>
            </button>
            <button class="btn btn-primary" @click="openCategoryModal()">
              <Plus :size="18" />
              <span>Yeni Kategori</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Stats Grid -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card gradient-orange">
            <div class="stat-icon-wrapper">
              <FolderTree :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ animatedStats.categories }}</span>
              <span class="stat-label">Kategori</span>
            </div>
            <div class="stat-decoration"></div>
          </div>
          <div class="stat-card gradient-blue">
            <div class="stat-icon-wrapper">
              <MessageCircle :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ animatedStats.topics }}</span>
              <span class="stat-label">Konu</span>
            </div>
            <div class="stat-decoration"></div>
          </div>
          <div class="stat-card gradient-green">
            <div class="stat-icon-wrapper">
              <MessagesSquare :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ animatedStats.posts }}</span>
              <span class="stat-label">Mesaj</span>
            </div>
            <div class="stat-decoration"></div>
          </div>
          <div class="stat-card gradient-purple">
            <div class="stat-icon-wrapper">
              <Users :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ animatedStats.activeUsers }}</span>
              <span class="stat-label">Aktif Kullanici</span>
            </div>
            <div class="stat-decoration"></div>
          </div>
          <div class="stat-card gradient-yellow">
            <div class="stat-icon-wrapper">
              <TrendingUp :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ animatedStats.todayPosts }}</span>
              <span class="stat-label">Bugun</span>
            </div>
            <div class="stat-decoration"></div>
          </div>
          <div class="stat-card gradient-red" :class="{ 'has-alert': stats.reported > 0 }">
            <div class="stat-icon-wrapper">
              <Flag :size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ animatedStats.reported }}</span>
              <span class="stat-label">Raporlanan</span>
            </div>
            <div class="stat-decoration"></div>
            <span v-if="stats.reported > 0" class="alert-badge pulse">!</span>
          </div>
        </div>
      </section>

      <!-- Tabs Navigation -->
      <nav class="tabs-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-button"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" :size="18" />
          <span>{{ tab.label }}</span>
          <span v-if="tab.badge && tab.badge > 0" class="tab-badge">{{ tab.badge }}</span>
        </button>
      </nav>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Categories Tab -->
        <Transition name="fade-slide" mode="out-in">
          <div v-if="activeTab === 'categories'" key="categories" class="categories-panel">
            <div class="panel-header">
              <div class="panel-title">
                <h2>Kategoriler</h2>
                <p>Surukle birak ile siralamayı degistirin</p>
              </div>
              <div class="panel-actions">
                <div class="search-box">
                  <Search :size="16" class="search-icon" />
                  <input
                    v-model="categorySearch"
                    type="text"
                    placeholder="Kategori ara..."
                    class="search-input"
                  />
                </div>
              </div>
            </div>

            <div v-if="loading" class="loading-state">
              <Loader2 :size="40" class="spin" />
              <span>Yukleniyor...</span>
            </div>

            <div v-else-if="filteredCategories.length === 0" class="empty-state">
              <div class="empty-icon">
                <FolderOpen :size="64" />
              </div>
              <h3>Kategori Bulunamadi</h3>
              <p>Henuz kategori olusturulmamiş veya arama kriterinize uygun sonuc yok.</p>
              <button class="btn btn-primary" @click="openCategoryModal()">
                <Plus :size="18" />
                Ilk Kategoriyi Olustur
              </button>
            </div>

            <div
              v-else
              ref="categoriesContainer"
              class="categories-list"
            >
              <TransitionGroup name="category-list" tag="div">
                <div
                  v-for="(category, index) in filteredCategories"
                  :key="category.id"
                  class="category-card"
                  :class="{ dragging: draggedCategory === category.id }"
                  :style="{ '--accent-color': category.color || '#ff6b00' }"
                  draggable="true"
                  @dragstart="onDragStart($event, category, index)"
                  @dragover.prevent="onDragOver($event, index)"
                  @drop="onDrop($event, index)"
                  @dragend="onDragEnd"
                >
                  <div class="drag-handle">
                    <GripVertical :size="20" />
                  </div>

                  <div class="category-icon-wrapper">
                    <span class="category-emoji">{{ category.icon || getDefaultIcon(category.name) }}</span>
                  </div>

                  <div class="category-main">
                    <div class="category-header">
                      <h3 class="category-name">{{ category.name }}</h3>
                      <div class="category-badges">
                        <span v-if="category.is_locked" class="badge badge-locked" title="Kilitli">
                          <Lock :size="12" />
                        </span>
                        <span v-if="category.is_private" class="badge badge-private" title="Ozel">
                          <Eye :size="12" />
                        </span>
                      </div>
                    </div>
                    <p class="category-description">{{ category.description || 'Aciklama yok' }}</p>
                    <div class="category-meta">
                      <span class="meta-item">
                        <MessageSquare :size="14" />
                        {{ category.topic_count || 0 }} konu
                      </span>
                      <span class="meta-item">
                        <MessagesSquare :size="14" />
                        {{ category.post_count || 0 }} mesaj
                      </span>
                      <span class="meta-item slug">
                        <Link :size="14" />
                        /{{ category.slug }}
                      </span>
                    </div>
                  </div>

                  <div class="category-actions">
                    <button
                      class="action-btn edit"
                      @click.stop="openCategoryModal(category)"
                      title="Duzenle"
                    >
                      <Pencil :size="16" />
                    </button>
                    <button
                      class="action-btn view"
                      @click.stop="viewCategoryTopics(category)"
                      title="Konulari Gor"
                    >
                      <ExternalLink :size="16" />
                    </button>
                    <button
                      class="action-btn danger"
                      @click.stop="confirmDeleteCategory(category)"
                      title="Sil"
                    >
                      <Trash2 :size="16" />
                    </button>
                  </div>
                </div>
              </TransitionGroup>
            </div>
          </div>
        </Transition>

        <!-- Topics Tab -->
        <Transition name="fade-slide" mode="out-in">
          <div v-if="activeTab === 'topics'" key="topics" class="topics-panel">
            <div class="panel-header">
              <div class="panel-title">
                <h2>Konular</h2>
                <p>Tum forumdaki konulari yonetin</p>
              </div>
            </div>

            <!-- Filters -->
            <div class="filters-bar">
              <div class="filters-left">
                <div class="search-box large">
                  <Search :size="18" class="search-icon" />
                  <input
                    v-model="topicSearch"
                    type="text"
                    placeholder="Konu ara..."
                    class="search-input"
                    @input="debouncedTopicSearch"
                  />
                  <button v-if="topicSearch" class="clear-btn" @click="clearTopicSearch">
                    <X :size="16" />
                  </button>
                </div>

                <select v-model="topicFilter.category" class="filter-select" @change="fetchTopics">
                  <option value="">Tum Kategoriler</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                    {{ cat.icon }} {{ cat.name }}
                  </option>
                </select>

                <select v-model="topicFilter.status" class="filter-select" @change="fetchTopics">
                  <option value="">Tum Durumlar</option>
                  <option value="open">Acik</option>
                  <option value="closed">Kapali</option>
                  <option value="pinned">Sabitlenmis</option>
                </select>
              </div>

              <div class="filters-right">
                <div class="view-toggle">
                  <button
                    :class="{ active: topicViewMode === 'table' }"
                    @click="topicViewMode = 'table'"
                    title="Tablo Gorunumu"
                  >
                    <List :size="18" />
                  </button>
                  <button
                    :class="{ active: topicViewMode === 'cards' }"
                    @click="topicViewMode = 'cards'"
                    title="Kart Gorunumu"
                  >
                    <LayoutGrid :size="18" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Bulk Actions -->
            <Transition name="slide-down">
              <div v-if="selectedTopics.length > 0" class="bulk-actions-bar">
                <span class="selection-info">
                  <CheckSquare :size="18" />
                  {{ selectedTopics.length }} konu secildi
                </span>
                <div class="bulk-buttons">
                  <button class="bulk-btn" @click="bulkPinTopics">
                    <Pin :size="16" />
                    Sabitle
                  </button>
                  <button class="bulk-btn" @click="bulkLockTopics">
                    <Lock :size="16" />
                    Kilitle
                  </button>
                  <button class="bulk-btn" @click="showMoveModal = true">
                    <ArrowRightLeft :size="16" />
                    Tasi
                  </button>
                  <button class="bulk-btn danger" @click="bulkDeleteTopics">
                    <Trash2 :size="16" />
                    Sil
                  </button>
                </div>
                <button class="clear-selection" @click="selectedTopics = []">
                  <X :size="16" />
                </button>
              </div>
            </Transition>

            <div v-if="loadingTopics" class="loading-state">
              <Loader2 :size="40" class="spin" />
              <span>Konular yukleniyor...</span>
            </div>

            <div v-else-if="topics.length === 0" class="empty-state">
              <div class="empty-icon">
                <MessageSquare :size="64" />
              </div>
              <h3>Konu Bulunamadi</h3>
              <p>Arama veya filtre kriterlerinize uygun konu yok.</p>
            </div>

            <!-- Table View -->
            <div v-else-if="topicViewMode === 'table'" class="topics-table-container">
              <table class="topics-table">
                <thead>
                  <tr>
                    <th class="col-checkbox">
                      <input
                        type="checkbox"
                        :checked="allTopicsSelected"
                        :indeterminate="someTopicsSelected"
                        @change="toggleAllTopics"
                      />
                    </th>
                    <th class="col-topic">Konu</th>
                    <th class="col-category">Kategori</th>
                    <th class="col-author">Yazar</th>
                    <th class="col-stats">Istatistikler</th>
                    <th class="col-status">Durum</th>
                    <th class="col-date">Tarih</th>
                    <th class="col-actions">Islemler</th>
                  </tr>
                </thead>
                <TransitionGroup name="table-row" tag="tbody">
                  <tr
                    v-for="topic in topics"
                    :key="topic.id"
                    :class="{
                      selected: selectedTopics.includes(topic.id),
                      pinned: topic.is_pinned,
                      locked: topic.is_locked
                    }"
                  >
                    <td class="col-checkbox">
                      <input
                        type="checkbox"
                        :checked="selectedTopics.includes(topic.id)"
                        @change="toggleTopicSelection(topic.id)"
                      />
                    </td>
                    <td class="col-topic">
                      <div class="topic-cell">
                        <div class="topic-badges">
                          <Pin v-if="topic.is_pinned" :size="14" class="badge-icon pinned" title="Sabitlenmis" />
                          <Lock v-if="topic.is_locked" :size="14" class="badge-icon locked" title="Kilitli" />
                        </div>
                        <span class="topic-title">{{ topic.title }}</span>
                      </div>
                    </td>
                    <td class="col-category">
                      <span class="category-tag" :style="{ '--color': getCategoryColor(topic.category_id) }">
                        {{ getCategoryIcon(topic.category_id) }} {{ topic.category_name }}
                      </span>
                    </td>
                    <td class="col-author">
                      <div class="author-cell">
                        <img
                          :src="getAvatar(topic.author_username)"
                          :alt="topic.author_username"
                          class="author-avatar"
                        />
                        <div class="author-info">
                          <span class="author-name">{{ topic.author_username }}</span>
                          <span v-if="topic.author_badge" class="author-badge" :style="{ background: topic.author_badge.color }">
                            {{ topic.author_badge.name }}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td class="col-stats">
                      <div class="stats-cell">
                        <span class="stat-item">
                          <MessageCircle :size="14" />
                          {{ topic.reply_count || 0 }}
                        </span>
                        <span class="stat-item">
                          <Eye :size="14" />
                          {{ topic.view_count || 0 }}
                        </span>
                      </div>
                    </td>
                    <td class="col-status">
                      <span class="status-badge" :class="getTopicStatusClass(topic)">
                        {{ getTopicStatusLabel(topic) }}
                      </span>
                    </td>
                    <td class="col-date">
                      <span class="date-text">{{ formatDate(topic.created_at) }}</span>
                    </td>
                    <td class="col-actions">
                      <div class="quick-actions">
                        <button
                          class="quick-action"
                          :class="{ active: topic.is_pinned }"
                          @click="togglePin(topic)"
                          :title="topic.is_pinned ? 'Sabitlemeyi Kaldir' : 'Sabitle'"
                        >
                          <Pin :size="16" />
                        </button>
                        <button
                          class="quick-action"
                          :class="{ active: topic.is_locked }"
                          @click="toggleLock(topic)"
                          :title="topic.is_locked ? 'Kilidi Ac' : 'Kilitle'"
                        >
                          <component :is="topic.is_locked ? Unlock : Lock" :size="16" />
                        </button>
                        <button
                          class="quick-action"
                          @click="openMoveTopicModal(topic)"
                          title="Tasi"
                        >
                          <ArrowRightLeft :size="16" />
                        </button>
                        <button
                          class="quick-action danger"
                          @click="confirmDeleteTopic(topic)"
                          title="Sil"
                        >
                          <Trash2 :size="16" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </TransitionGroup>
              </table>
            </div>

            <!-- Cards View -->
            <div v-else class="topics-cards-grid">
              <TransitionGroup name="card-list">
                <div
                  v-for="topic in topics"
                  :key="topic.id"
                  class="topic-card"
                  :class="{
                    selected: selectedTopics.includes(topic.id),
                    pinned: topic.is_pinned,
                    locked: topic.is_locked
                  }"
                >
                  <div class="card-header">
                    <input
                      type="checkbox"
                      :checked="selectedTopics.includes(topic.id)"
                      @change="toggleTopicSelection(topic.id)"
                    />
                    <div class="card-badges">
                      <Pin v-if="topic.is_pinned" :size="14" class="pinned" />
                      <Lock v-if="topic.is_locked" :size="14" class="locked" />
                    </div>
                    <span class="category-tag small" :style="{ '--color': getCategoryColor(topic.category_id) }">
                      {{ getCategoryIcon(topic.category_id) }} {{ topic.category_name }}
                    </span>
                  </div>

                  <h3 class="card-title">{{ topic.title }}</h3>

                  <div class="card-author">
                    <img
                      :src="getAvatar(topic.author_username)"
                      :alt="topic.author_username"
                      class="author-avatar"
                    />
                    <div class="author-details">
                      <span class="author-name">{{ topic.author_username }}</span>
                      <span class="post-date">{{ formatDate(topic.created_at) }}</span>
                    </div>
                  </div>

                  <div class="card-stats">
                    <span class="stat">
                      <MessageCircle :size="14" />
                      {{ topic.reply_count || 0 }} yanit
                    </span>
                    <span class="stat">
                      <Eye :size="14" />
                      {{ topic.view_count || 0 }} goruntuleme
                    </span>
                  </div>

                  <div class="card-actions">
                    <button
                      class="card-action"
                      :class="{ active: topic.is_pinned }"
                      @click="togglePin(topic)"
                    >
                      <Pin :size="16" />
                    </button>
                    <button
                      class="card-action"
                      :class="{ active: topic.is_locked }"
                      @click="toggleLock(topic)"
                    >
                      <component :is="topic.is_locked ? Unlock : Lock" :size="16" />
                    </button>
                    <button class="card-action" @click="openMoveTopicModal(topic)">
                      <ArrowRightLeft :size="16" />
                    </button>
                    <button class="card-action danger" @click="confirmDeleteTopic(topic)">
                      <Trash2 :size="16" />
                    </button>
                  </div>
                </div>
              </TransitionGroup>
            </div>

            <!-- Pagination -->
            <div v-if="totalTopics > topicsPerPage" class="pagination-container">
              <div class="pagination-info">
                {{ (currentPage - 1) * topicsPerPage + 1 }} - {{ Math.min(currentPage * topicsPerPage, totalTopics) }} / {{ totalTopics }} konu
              </div>
              <div class="pagination">
                <button
                  class="page-btn"
                  :disabled="currentPage === 1"
                  @click="goToPage(currentPage - 1)"
                >
                  <ChevronLeft :size="18" />
                </button>
                <template v-for="page in visiblePages" :key="page">
                  <span v-if="page === '...'" class="page-ellipsis">...</span>
                  <button
                    v-else
                    class="page-btn"
                    :class="{ active: currentPage === page }"
                    @click="goToPage(page)"
                  >
                    {{ page }}
                  </button>
                </template>
                <button
                  class="page-btn"
                  :disabled="currentPage === totalPages"
                  @click="goToPage(currentPage + 1)"
                >
                  <ChevronRight :size="18" />
                </button>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Reported Posts Tab -->
        <Transition name="fade-slide" mode="out-in">
          <div v-if="activeTab === 'reports'" key="reports" class="reports-panel">
            <div class="panel-header">
              <div class="panel-title">
                <h2>Raporlanan Icerikler</h2>
                <p>Kullanicilarin raporladigi icerikler</p>
              </div>
            </div>

            <div v-if="loadingReports" class="loading-state">
              <Loader2 :size="40" class="spin" />
              <span>Raporlar yukleniyor...</span>
            </div>

            <div v-else-if="reports.length === 0" class="empty-state success">
              <div class="empty-icon">
                <CheckCircle :size="64" />
              </div>
              <h3>Tebrikler!</h3>
              <p>Incelenmesi gereken rapor bulunmuyor.</p>
            </div>

            <div v-else class="reports-list">
              <TransitionGroup name="report-list">
                <div
                  v-for="report in reports"
                  :key="report.id"
                  class="report-card"
                  :class="{ urgent: report.report_count >= 3 }"
                >
                  <div class="report-header">
                    <span class="report-type" :class="report.type">
                      <component :is="report.type === 'topic' ? MessageSquare : MessageCircle" :size="14" />
                      {{ report.type === 'topic' ? 'Konu' : 'Mesaj' }}
                    </span>
                    <span class="report-count">
                      <Flag :size="14" />
                      {{ report.report_count }} rapor
                    </span>
                    <span class="report-date">{{ formatDate(report.created_at) }}</span>
                  </div>

                  <div class="report-content">
                    <h4 class="report-title">{{ report.content_title || report.content_preview }}</h4>
                    <p class="report-preview">{{ report.content_preview }}</p>
                  </div>

                  <div class="report-meta">
                    <div class="reporter-info">
                      <img :src="getAvatar(report.content_author)" class="mini-avatar" />
                      <span>{{ report.content_author }}</span>
                    </div>
                    <div class="report-reasons">
                      <span v-for="reason in report.reasons" :key="reason" class="reason-tag">
                        {{ reason }}
                      </span>
                    </div>
                  </div>

                  <div class="report-actions">
                    <button class="report-btn view" @click="viewReportedContent(report)">
                      <Eye :size="16" />
                      Goruntule
                    </button>
                    <button class="report-btn approve" @click="dismissReport(report)">
                      <Check :size="16" />
                      Reddet
                    </button>
                    <button class="report-btn warn" @click="warnAuthor(report)">
                      <AlertTriangle :size="16" />
                      Uyar
                    </button>
                    <button class="report-btn danger" @click="deleteReportedContent(report)">
                      <Trash2 :size="16" />
                      Sil
                    </button>
                  </div>
                </div>
              </TransitionGroup>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Category Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showCategoryModal" class="modal-overlay" @click.self="closeCategoryModal">
            <div class="modal-container category-modal">
              <div class="modal-header">
                <h2>
                  <component :is="editingCategory ? Pencil : Plus" :size="20" />
                  {{ editingCategory ? 'Kategori Duzenle' : 'Yeni Kategori' }}
                </h2>
                <button class="modal-close" @click="closeCategoryModal">
                  <X :size="20" />
                </button>
              </div>

              <div class="modal-body">
                <div class="form-grid">
                  <div class="form-group full-width">
                    <label>
                      <Type :size="16" />
                      Kategori Adi
                    </label>
                    <input
                      v-model="categoryForm.name"
                      type="text"
                      placeholder="Ornek: Genel Tartismalar"
                      class="form-input"
                      @input="generateSlug"
                    />
                  </div>

                  <div class="form-group full-width">
                    <label>
                      <Link :size="16" />
                      Slug (URL)
                    </label>
                    <div class="input-with-prefix">
                      <span class="prefix">/forum/</span>
                      <input
                        v-model="categoryForm.slug"
                        type="text"
                        placeholder="genel-tartismalar"
                        class="form-input"
                      />
                    </div>
                  </div>

                  <div class="form-group full-width">
                    <label>
                      <FileText :size="16" />
                      Aciklama
                    </label>
                    <textarea
                      v-model="categoryForm.description"
                      rows="3"
                      placeholder="Kategori hakkinda kisa bir aciklama..."
                      class="form-textarea"
                    ></textarea>
                  </div>

                  <div class="form-group">
                    <label>
                      <Smile :size="16" />
                      Ikon (Emoji)
                    </label>
                    <div class="icon-picker-wrapper">
                      <input
                        v-model="categoryForm.icon"
                        type="text"
                        placeholder="Emoji secin"
                        class="form-input icon-input"
                        @focus="showIconPicker = true"
                      />
                      <div class="icon-preview">{{ categoryForm.icon || '📁' }}</div>
                    </div>
                    <div v-if="showIconPicker" class="emoji-grid">
                      <button
                        v-for="emoji in popularEmojis"
                        :key="emoji"
                        class="emoji-btn"
                        @click="selectEmoji(emoji)"
                      >
                        {{ emoji }}
                      </button>
                    </div>
                  </div>

                  <div class="form-group">
                    <label>
                      <Palette :size="16" />
                      Renk
                    </label>
                    <div class="color-picker-wrapper">
                      <input
                        v-model="categoryForm.color"
                        type="color"
                        class="color-input"
                      />
                      <div class="color-presets">
                        <button
                          v-for="color in colorPresets"
                          :key="color"
                          class="color-preset"
                          :style="{ background: color }"
                          :class="{ selected: categoryForm.color === color }"
                          @click="categoryForm.color = color"
                        ></button>
                      </div>
                    </div>
                  </div>

                  <div class="form-group">
                    <label>
                      <Hash :size="16" />
                      Siralama
                    </label>
                    <input
                      v-model.number="categoryForm.display_order"
                      type="number"
                      min="0"
                      class="form-input"
                    />
                  </div>

                  <div class="form-group">
                    <label>
                      <Settings :size="16" />
                      Ayarlar
                    </label>
                    <div class="checkbox-group">
                      <label class="checkbox-label">
                        <input v-model="categoryForm.is_locked" type="checkbox" />
                        <span class="checkbox-text">Kilitli (Yeni konu acilamaz)</span>
                      </label>
                      <label class="checkbox-label">
                        <input v-model="categoryForm.is_private" type="checkbox" />
                        <span class="checkbox-text">Ozel (Sadece yetkililere gorunur)</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn btn-secondary" @click="closeCategoryModal">
                  Iptal
                </button>
                <button
                  class="btn btn-primary"
                  @click="saveCategory"
                  :disabled="saving || !categoryForm.name || !categoryForm.slug"
                >
                  <Loader2 v-if="saving" :size="16" class="spin" />
                  <Save v-else :size="16" />
                  <span>{{ editingCategory ? 'Guncelle' : 'Olustur' }}</span>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Move Topic Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showMoveModal" class="modal-overlay" @click.self="showMoveModal = false">
            <div class="modal-container small">
              <div class="modal-header">
                <h2>
                  <ArrowRightLeft :size="20" />
                  Konuyu Tasi
                </h2>
                <button class="modal-close" @click="showMoveModal = false">
                  <X :size="20" />
                </button>
              </div>

              <div class="modal-body">
                <p class="modal-info">
                  {{ movingTopic ? `"${movingTopic.title}" konusu` : `${selectedTopics.length} konu` }} tasiniyor
                </p>
                <div class="form-group">
                  <label>Hedef Kategori</label>
                  <select v-model="targetCategoryId" class="form-select">
                    <option value="" disabled>Kategori secin...</option>
                    <option
                      v-for="cat in categories"
                      :key="cat.id"
                      :value="cat.id"
                      :disabled="movingTopic && cat.id === movingTopic.category_id"
                    >
                      {{ cat.icon }} {{ cat.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn btn-secondary" @click="showMoveModal = false">
                  Iptal
                </button>
                <button
                  class="btn btn-primary"
                  @click="executeMoveTopics"
                  :disabled="!targetCategoryId"
                >
                  <ArrowRightLeft :size="16" />
                  Tasi
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Delete Confirmation Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
            <div class="modal-container confirm-modal">
              <div class="confirm-icon danger">
                <AlertTriangle :size="32" />
              </div>
              <h2>{{ deleteModalTitle }}</h2>
              <p>{{ deleteModalMessage }}</p>
              <div class="confirm-actions">
                <button class="btn btn-secondary" @click="showDeleteModal = false">
                  Iptal
                </button>
                <button class="btn btn-danger" @click="executeDelete">
                  <Trash2 :size="16" />
                  Sil
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Toast Notifications -->
      <Teleport to="body">
        <TransitionGroup name="toast" tag="div" class="toast-container">
          <div
            v-for="toast in toasts"
            :key="toast.id"
            class="toast"
            :class="toast.type"
          >
            <component :is="getToastIcon(toast.type)" :size="18" />
            <span>{{ toast.message }}</span>
            <button class="toast-close" @click="removeToast(toast.id)">
              <X :size="14" />
            </button>
          </div>
        </TransitionGroup>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  MessageSquare, MessageCircle, MessagesSquare, FolderOpen, FolderTree,
  Plus, Pencil, Trash2, X, Loader2, Pin, Lock, Unlock, Search,
  Filter, ChevronLeft, ChevronRight, List, LayoutGrid, RefreshCw,
  TrendingUp, Users, Flag, ExternalLink, Eye, Link, GripVertical,
  CheckSquare, ArrowRightLeft, Settings, Palette, Hash, Type, FileText,
  Smile, Save, Check, CheckCircle, AlertTriangle
} from 'lucide-vue-next'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()

// State
const loading = ref(false)
const loadingTopics = ref(false)
const loadingReports = ref(false)
const saving = ref(false)
const refreshing = ref(false)
const activeTab = ref('categories')
const topicViewMode = ref('table')

// Stats
const stats = ref({
  categories: 0,
  topics: 0,
  posts: 0,
  todayPosts: 0,
  activeUsers: 0,
  reported: 0
})

const animatedStats = reactive({
  categories: 0,
  topics: 0,
  posts: 0,
  todayPosts: 0,
  activeUsers: 0,
  reported: 0
})

// Data
const categories = ref([])
const topics = ref([])
const reports = ref([])

// Search & Filters
const categorySearch = ref('')
const topicSearch = ref('')
const topicFilter = reactive({
  category: '',
  status: ''
})

// Selection
const selectedTopics = ref([])

// Pagination
const currentPage = ref(1)
const topicsPerPage = ref(20)
const totalTopics = ref(0)

// Category Modal
const showCategoryModal = ref(false)
const editingCategory = ref(null)
const showIconPicker = ref(false)
const categoryForm = reactive({
  name: '',
  slug: '',
  description: '',
  icon: '',
  color: '#ff6b00',
  display_order: 0,
  is_locked: false,
  is_private: false
})

// Move Modal
const showMoveModal = ref(false)
const movingTopic = ref(null)
const targetCategoryId = ref('')

// Delete Modal
const showDeleteModal = ref(false)
const deleteModalTitle = ref('')
const deleteModalMessage = ref('')
const deleteCallback = ref(null)

// Drag & Drop
const draggedCategory = ref(null)
const draggedIndex = ref(-1)

// Toasts
const toasts = ref([])
let toastId = 0

// Tabs configuration
const tabs = computed(() => [
  { id: 'categories', label: 'Kategoriler', icon: FolderTree, badge: 0 },
  { id: 'topics', label: 'Konular', icon: MessageSquare, badge: 0 },
  { id: 'reports', label: 'Raporlar', icon: Flag, badge: stats.value.reported }
])

// Popular emojis for picker
const popularEmojis = [
  '📁', '💬', '📢', '🎮', '🎯', '🔧', '💡', '🎨',
  '📚', '🎵', '🎬', '💻', '🌍', '🔥', '⭐', '❓',
  '📝', '🛒', '💰', '🏆', '🎁', '📊', '🔒', '👥'
]

// Color presets
const colorPresets = [
  '#ff6b00', '#ef4444', '#f59e0b', '#22c55e', '#3b82f6',
  '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#6366f1'
]

// Computed
const filteredCategories = computed(() => {
  if (!categorySearch.value) return categories.value
  const search = categorySearch.value.toLowerCase()
  return categories.value.filter(c =>
    c.name.toLowerCase().includes(search) ||
    c.slug.toLowerCase().includes(search)
  )
})

const totalPages = computed(() => Math.ceil(totalTopics.value / topicsPerPage.value) || 1)

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      pages.push(1, 2, 3, 4, '...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...', total - 3, total - 2, total - 1, total)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }

  return pages
})

const allTopicsSelected = computed(() =>
  topics.value.length > 0 && selectedTopics.value.length === topics.value.length
)

const someTopicsSelected = computed(() =>
  selectedTopics.value.length > 0 && selectedTopics.value.length < topics.value.length
)

// API helpers
const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authStore.token}`
})

const getAvatar = (username) => `https://api.dicebear.com/7.x/initials/svg?seed=${username}`

// Format date
const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'dd MMM yyyy', { locale: tr })
}

// Animate stats
const animateStats = () => {
  const duration = 1000
  const start = Date.now()
  const startValues = { ...animatedStats }

  const animate = () => {
    const elapsed = Date.now() - start
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)

    Object.keys(stats.value).forEach(key => {
      animatedStats[key] = Math.round(startValues[key] + (stats.value[key] - startValues[key]) * eased)
    })

    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }

  requestAnimationFrame(animate)
}

// Generate slug from name
const generateSlug = () => {
  if (editingCategory.value) return
  categoryForm.slug = categoryForm.name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
}

// Get default icon based on category name
const getDefaultIcon = (name) => {
  const lower = name?.toLowerCase() || ''
  if (lower.includes('genel') || lower.includes('sohbet')) return '💬'
  if (lower.includes('duyuru')) return '📢'
  if (lower.includes('oyun') || lower.includes('game')) return '🎮'
  if (lower.includes('destek') || lower.includes('yardim')) return '❓'
  if (lower.includes('proje') || lower.includes('goster')) return '🎨'
  if (lower.includes('oneri')) return '💡'
  return '📁'
}

// Category helpers
const getCategoryColor = (categoryId) => {
  const cat = categories.value.find(c => c.id === categoryId)
  return cat?.color || '#ff6b00'
}

const getCategoryIcon = (categoryId) => {
  const cat = categories.value.find(c => c.id === categoryId)
  return cat?.icon || '📁'
}

// Topic status helpers
const getTopicStatusClass = (topic) => {
  if (topic.is_pinned) return 'pinned'
  if (topic.is_locked) return 'locked'
  return 'open'
}

const getTopicStatusLabel = (topic) => {
  if (topic.is_pinned) return 'Sabit'
  if (topic.is_locked) return 'Kilitli'
  return 'Acik'
}

// Toast helpers
const showToast = (message, type = 'info') => {
  const id = ++toastId
  toasts.value.push({ id, message, type })
  setTimeout(() => removeToast(id), 4000)
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) toasts.value.splice(index, 1)
}

const getToastIcon = (type) => {
  switch (type) {
    case 'success': return CheckCircle
    case 'error': return AlertTriangle
    case 'warning': return AlertTriangle
    default: return MessageCircle
  }
}

// Select emoji
const selectEmoji = (emoji) => {
  categoryForm.icon = emoji
  showIconPicker.value = false
}

// API Calls
const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/admin/forum/categories', {
      headers: getHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      categories.value = data.categories || data || []
      categories.value.sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
      stats.value.categories = categories.value.length
    }
  } catch (e) {
    // Error handled
    showToast('Kategoriler yuklenemedi', 'error')
  }
  loading.value = false
}

const fetchTopics = async () => {
  loadingTopics.value = true
  try {
    let url = `/api/admin/forum/topics?limit=${topicsPerPage.value}&page=${currentPage.value}`
    if (topicFilter.category) url += `&category_id=${topicFilter.category}`
    if (topicFilter.status === 'closed') url += '&status=locked'
    if (topicFilter.status === 'open') url += '&status=active'
    if (topicFilter.status === 'pinned') url += '&status=pinned'
    if (topicSearch.value) url += `&search=${encodeURIComponent(topicSearch.value)}`

    const res = await fetch(url, {
      headers: getHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      topics.value = data.topics || data || []
      totalTopics.value = data.total || topics.value.length
    }
  } catch (e) {
    // Error handled
    showToast('Konular yuklenemedi', 'error')
  }
  loadingTopics.value = false
}

const fetchStats = async () => {
  try {
    const res = await fetch('/api/forum/stats', {
      headers: getHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      stats.value = {
        categories: data.categories || 0,
        topics: data.topics || 0,
        posts: data.posts || 0,
        todayPosts: data.today_posts || 0,
        activeUsers: data.active_users || 0,
        reported: data.reported || 0
      }
      animateStats()
    }
  } catch (e) {
    // Error handled
  }
}

const fetchReports = async () => {
  loadingReports.value = true
  try {
    const res = await fetch('/api/admin/forum/reports', {
      headers: getHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      reports.value = data.reports || data || []
    }
  } catch (e) {
    // Error handled
  }
  loadingReports.value = false
}

const refreshData = async () => {
  refreshing.value = true
  await Promise.all([fetchCategories(), fetchStats()])
  if (activeTab.value === 'topics') await fetchTopics()
  if (activeTab.value === 'reports') await fetchReports()
  refreshing.value = false
  showToast('Veriler guncellendi', 'success')
}

// Debounced search
let searchTimeout = null
const debouncedTopicSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchTopics()
  }, 300)
}

const clearTopicSearch = () => {
  topicSearch.value = ''
  currentPage.value = 1
  fetchTopics()
}

// Pagination
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchTopics()
  }
}

// Category Modal
const openCategoryModal = (category = null) => {
  editingCategory.value = category
  showIconPicker.value = false
  if (category) {
    Object.assign(categoryForm, {
      name: category.name,
      slug: category.slug,
      description: category.description || '',
      icon: category.icon || '',
      color: category.color || '#ff6b00',
      display_order: category.display_order || 0,
      is_locked: category.is_locked || false,
      is_private: category.is_private || false
    })
  } else {
    Object.assign(categoryForm, {
      name: '',
      slug: '',
      description: '',
      icon: '',
      color: '#ff6b00',
      display_order: categories.value.length,
      is_locked: false,
      is_private: false
    })
  }
  showCategoryModal.value = true
}

const closeCategoryModal = () => {
  showCategoryModal.value = false
  editingCategory.value = null
  showIconPicker.value = false
}

const saveCategory = async () => {
  if (!categoryForm.name || !categoryForm.slug) {
    showToast('Ad ve slug alanlari zorunludur', 'error')
    return
  }

  saving.value = true
  try {
    const url = editingCategory.value
      ? `/api/admin/forum/categories/${editingCategory.value.id}`
      : '/api/admin/forum/categories'

    const res = await fetch(url, {
      method: editingCategory.value ? 'PUT' : 'POST',
      headers: getHeaders(),
      body: JSON.stringify(categoryForm)
    })

    if (res.ok) {
      showToast(
        editingCategory.value ? 'Kategori guncellendi' : 'Kategori olusturuldu',
        'success'
      )
      closeCategoryModal()
      fetchCategories()
      fetchStats()
    } else {
      const data = await res.json()
      showToast(data.detail || 'Bir hata olustu', 'error')
    }
  } catch (e) {
    // Error handled
    showToast('Baglanti hatasi', 'error')
  }
  saving.value = false
}

// Delete Category
const confirmDeleteCategory = (category) => {
  deleteModalTitle.value = 'Kategoriyi Sil'
  deleteModalMessage.value = `"${category.name}" kategorisini silmek istediginize emin misiniz? Icindeki tum konular da silinecektir!`
  deleteCallback.value = () => deleteCategory(category.id)
  showDeleteModal.value = true
}

const deleteCategory = async (id) => {
  try {
    const res = await fetch(`/api/admin/forum/categories/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (res.ok) {
      showToast('Kategori silindi', 'success')
      fetchCategories()
      fetchStats()
    } else {
      showToast('Silme islemi basarisiz', 'error')
    }
  } catch (e) {
    // Error handled
    showToast('Baglanti hatasi', 'error')
  }
}

// View category topics
const viewCategoryTopics = (category) => {
  activeTab.value = 'topics'
  topicFilter.category = category.id
  nextTick(() => fetchTopics())
}

// Drag & Drop for categories
const onDragStart = (event, category, index) => {
  draggedCategory.value = category.id
  draggedIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
}

const onDragOver = (event, index) => {
  event.dataTransfer.dropEffect = 'move'
}

const onDrop = async (event, targetIndex) => {
  if (draggedIndex.value === targetIndex) return

  const newCategories = [...categories.value]
  const [removed] = newCategories.splice(draggedIndex.value, 1)
  newCategories.splice(targetIndex, 0, removed)

  // Update display orders
  newCategories.forEach((cat, idx) => {
    cat.display_order = idx
  })

  categories.value = newCategories

  // Save order to server
  try {
    await fetch('/api/admin/forum/categories/reorder', {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        orders: newCategories.map(c => ({ id: c.id, order: c.display_order }))
      })
    })
    showToast('Siralama kaydedildi', 'success')
  } catch (e) {
    // Error handled
    showToast('Siralama kaydedilemedi', 'error')
    fetchCategories()
  }
}

const onDragEnd = () => {
  draggedCategory.value = null
  draggedIndex.value = -1
}

// Topic Selection
const toggleTopicSelection = (topicId) => {
  const index = selectedTopics.value.indexOf(topicId)
  if (index === -1) {
    selectedTopics.value.push(topicId)
  } else {
    selectedTopics.value.splice(index, 1)
  }
}

const toggleAllTopics = (event) => {
  if (event.target.checked) {
    selectedTopics.value = topics.value.map(t => t.id)
  } else {
    selectedTopics.value = []
  }
}

// Topic Actions
const togglePin = async (topic) => {
  try {
    const res = await fetch(`/api/admin/forum/topics/${topic.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ is_pinned: !topic.is_pinned })
    })
    if (res.ok) {
      topic.is_pinned = !topic.is_pinned
      showToast(topic.is_pinned ? 'Konu sabitlendi' : 'Sabitleme kaldirildi', 'success')
    }
  } catch (e) {
    // Error handled
    showToast('Islem basarisiz', 'error')
  }
}

const toggleLock = async (topic) => {
  try {
    const res = await fetch(`/api/admin/forum/topics/${topic.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ is_locked: !topic.is_locked })
    })
    if (res.ok) {
      topic.is_locked = !topic.is_locked
      showToast(topic.is_locked ? 'Konu kilitlendi' : 'Kilit acildi', 'success')
    }
  } catch (e) {
    // Error handled
    showToast('Islem basarisiz', 'error')
  }
}

const confirmDeleteTopic = (topic) => {
  deleteModalTitle.value = 'Konuyu Sil'
  deleteModalMessage.value = `"${topic.title}" konusunu silmek istediginize emin misiniz?`
  deleteCallback.value = () => deleteTopic(topic.id)
  showDeleteModal.value = true
}

const deleteTopic = async (id) => {
  try {
    const res = await fetch(`/api/admin/forum/topics/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (res.ok) {
      topics.value = topics.value.filter(t => t.id !== id)
      selectedTopics.value = selectedTopics.value.filter(tid => tid !== id)
      showToast('Konu silindi', 'success')
      fetchStats()
    }
  } catch (e) {
    // Error handled
    showToast('Silme basarisiz', 'error')
  }
}

// Move Topic
const openMoveTopicModal = (topic) => {
  movingTopic.value = topic
  targetCategoryId.value = ''
  showMoveModal.value = true
}

const executeMoveTopics = async () => {
  const topicIds = movingTopic.value ? [movingTopic.value.id] : selectedTopics.value

  try {
    const res = await fetch('/api/admin/forum/topics/move', {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        topic_ids: topicIds,
        category_id: targetCategoryId.value
      })
    })

    if (res.ok) {
      showToast(`${topicIds.length} konu taşindi`, 'success')
      showMoveModal.value = false
      movingTopic.value = null
      selectedTopics.value = []
      fetchTopics()
      fetchCategories()
    } else {
      showToast('Tasima basarisiz', 'error')
    }
  } catch (e) {
    // Error handled
    showToast('Baglanti hatasi', 'error')
  }
}

// Bulk Actions
const bulkPinTopics = async () => {
  try {
    await fetch('/api/admin/forum/topics/bulk', {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        topic_ids: selectedTopics.value,
        action: 'pin'
      })
    })
    showToast(`${selectedTopics.value.length} konu sabitlendi`, 'success')
    selectedTopics.value = []
    fetchTopics()
  } catch (e) {
    showToast('Islem basarisiz', 'error')
  }
}

const bulkLockTopics = async () => {
  try {
    await fetch('/api/admin/forum/topics/bulk', {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        topic_ids: selectedTopics.value,
        action: 'lock'
      })
    })
    showToast(`${selectedTopics.value.length} konu kilitlendi`, 'success')
    selectedTopics.value = []
    fetchTopics()
  } catch (e) {
    showToast('Islem basarisiz', 'error')
  }
}

const bulkDeleteTopics = () => {
  deleteModalTitle.value = 'Toplu Silme'
  deleteModalMessage.value = `${selectedTopics.value.length} konuyu silmek istediginize emin misiniz?`
  deleteCallback.value = async () => {
    try {
      await fetch('/api/admin/forum/topics/bulk', {
        method: 'DELETE',
        headers: getHeaders(),
        body: JSON.stringify({ topic_ids: selectedTopics.value })
      })
      showToast(`${selectedTopics.value.length} konu silindi`, 'success')
      selectedTopics.value = []
      fetchTopics()
      fetchStats()
    } catch (e) {
      showToast('Silme basarisiz', 'error')
    }
  }
  showDeleteModal.value = true
}

// Execute delete callback
const executeDelete = () => {
  if (deleteCallback.value) {
    deleteCallback.value()
  }
  showDeleteModal.value = false
  deleteCallback.value = null
}

// Report Actions
const viewReportedContent = (report) => {
  window.open(`/forum/${report.type}/${report.content_id}`, '_blank')
}

const dismissReport = async (report) => {
  try {
    await fetch(`/api/admin/forum/reports/${report.id}/dismiss`, {
      method: 'POST',
      headers: getHeaders()
    })
    reports.value = reports.value.filter(r => r.id !== report.id)
    stats.value.reported--
    showToast('Rapor reddedildi', 'success')
  } catch (e) {
    showToast('Islem basarisiz', 'error')
  }
}

const warnAuthor = async (report) => {
  try {
    await fetch(`/api/admin/forum/reports/${report.id}/warn`, {
      method: 'POST',
      headers: getHeaders()
    })
    reports.value = reports.value.filter(r => r.id !== report.id)
    stats.value.reported--
    showToast('Kullanici uyarildi', 'success')
  } catch (e) {
    showToast('Islem basarisiz', 'error')
  }
}

const deleteReportedContent = async (report) => {
  try {
    await fetch(`/api/admin/forum/reports/${report.id}/delete-content`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    reports.value = reports.value.filter(r => r.id !== report.id)
    stats.value.reported--
    showToast('Icerik silindi', 'success')
    fetchStats()
  } catch (e) {
    showToast('Silme basarisiz', 'error')
  }
}

// Watch for tab changes
watch(activeTab, (tab) => {
  if (tab === 'topics' && topics.value.length === 0) {
    fetchTopics()
  }
  if (tab === 'reports' && reports.value.length === 0) {
    fetchReports()
  }
})

// Initialize
onMounted(() => {
  fetchCategories()
  fetchStats()
})
</script>

<style scoped>
/* Base Variables & Dark Theme */
.forum-admin {
  --primary: #ff6b00;
  --primary-light: rgba(255, 107, 0, 0.15);
  --primary-dark: #e65f00;
  --bg-primary: #0f0f1a;
  --bg-secondary: #1a1a2e;
  --bg-tertiary: #252540;
  --bg-elevated: #2a2a4a;
  --border-color: #2f2f4f;
  --text-primary: #ffffff;
  --text-secondary: #a0a0c0;
  --text-muted: #6b6b8a;
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #3b82f6;

  min-height: 100%;
  color: var(--text-primary);
}

/* Header */
.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, var(--text-primary), var(--primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-icon {
  color: var(--primary);
  -webkit-text-fill-color: initial;
}

.page-subtitle {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 0, 0.4);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-elevated);
  border-color: var(--primary);
}

.btn-danger {
  background: linear-gradient(135deg, var(--danger), #dc2626);
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Stats Grid */
.stats-section {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  position: relative;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
}

.stat-card.has-alert {
  border-color: var(--danger);
  animation: alertPulse 2s ease-in-out infinite;
}

@keyframes alertPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.gradient-orange .stat-icon-wrapper { background: linear-gradient(135deg, #ff6b00, #ff9500); }
.gradient-blue .stat-icon-wrapper { background: linear-gradient(135deg, #3b82f6, #60a5fa); }
.gradient-green .stat-icon-wrapper { background: linear-gradient(135deg, #22c55e, #4ade80); }
.gradient-purple .stat-icon-wrapper { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }
.gradient-yellow .stat-icon-wrapper { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.gradient-red .stat-icon-wrapper { background: linear-gradient(135deg, #ef4444, #f87171); }

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-decoration {
  position: absolute;
  right: -20px;
  bottom: -20px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  opacity: 0.1;
}

.gradient-orange .stat-decoration { background: #ff6b00; }
.gradient-blue .stat-decoration { background: #3b82f6; }
.gradient-green .stat-decoration { background: #22c55e; }
.gradient-purple .stat-decoration { background: #8b5cf6; }
.gradient-yellow .stat-decoration { background: #f59e0b; }
.gradient-red .stat-decoration { background: #ef4444; }

.alert-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 20px;
  height: 20px;
  background: var(--danger);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.alert-badge.pulse {
  animation: badgePulse 1s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

/* Tabs Navigation */
.tabs-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 6px;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.tab-button:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.tab-button.active {
  background: var(--primary);
  color: white;
}

.tab-badge {
  padding: 2px 8px;
  background: var(--danger);
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.tab-button.active .tab-badge {
  background: rgba(255, 255, 255, 0.3);
}

/* Tab Content */
.tab-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  overflow: hidden;
}

/* Panel Header */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
  flex-wrap: wrap;
}

.panel-title h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
}

.panel-title p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

/* Search Box */
.search-box {
  position: relative;
  min-width: 240px;
}

.search-box.large {
  min-width: 320px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 42px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.clear-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.clear-btn:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-icon {
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.empty-state p {
  margin: 0 0 24px;
  max-width: 400px;
}

.empty-state.success .empty-icon {
  color: var(--success);
  opacity: 1;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinning {
  animation: spin 1s linear infinite;
}

/* Categories List */
.categories-list {
  padding: 16px;
}

.category-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--accent-color);
  border-radius: 16px;
  margin-bottom: 12px;
  cursor: grab;
  transition: all 0.3s ease;
}

.category-card:hover {
  background: var(--bg-elevated);
  transform: translateX(4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.category-card.dragging {
  opacity: 0.5;
  cursor: grabbing;
}

.drag-handle {
  color: var(--text-muted);
  cursor: grab;
  padding: 4px;
}

.category-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--accent-color), rgba(255, 255, 255, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.category-emoji {
  font-size: 28px;
}

.category-main {
  flex: 1;
  min-width: 0;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.category-name {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.category-badges {
  display: flex;
  gap: 6px;
}

.badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  font-size: 10px;
}

.badge-locked {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger);
}

.badge-private {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
}

.category-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.category-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.meta-item.slug {
  font-family: monospace;
  color: var(--primary);
}

.category-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-elevated);
}

.action-btn.edit:hover {
  color: var(--warning);
  border-color: var(--warning);
}

.action-btn.view:hover {
  color: var(--info);
  border-color: var(--info);
}

.action-btn.danger:hover {
  color: var(--danger);
  border-color: var(--danger);
  background: rgba(239, 68, 68, 0.1);
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  flex-wrap: wrap;
}

.filters-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 10px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary);
}

.view-toggle {
  display: flex;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 4px;
}

.view-toggle button {
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggle button:hover {
  color: var(--text-primary);
}

.view-toggle button.active {
  background: var(--primary);
  color: white;
}

/* Bulk Actions Bar */
.bulk-actions-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  background: var(--primary-light);
  border-bottom: 1px solid var(--primary);
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--primary);
}

.bulk-buttons {
  display: flex;
  gap: 8px;
  flex: 1;
}

.bulk-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.bulk-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: rgba(239, 68, 68, 0.1);
}

.clear-selection {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  margin-left: auto;
}

.clear-selection:hover {
  color: var(--text-primary);
}

/* Topics Table */
.topics-table-container {
  overflow-x: auto;
}

.topics-table {
  width: 100%;
  border-collapse: collapse;
}

.topics-table th,
.topics-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.topics-table th {
  background: var(--bg-tertiary);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.topics-table tbody tr {
  transition: all 0.2s;
}

.topics-table tbody tr:hover {
  background: var(--bg-tertiary);
}

.topics-table tbody tr.selected {
  background: var(--primary-light);
}

.topics-table tbody tr.pinned {
  background: rgba(34, 197, 94, 0.05);
}

.topics-table tbody tr.locked {
  background: rgba(239, 68, 68, 0.05);
}

.col-checkbox {
  width: 48px;
  text-align: center !important;
}

.col-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
  cursor: pointer;
}

.topic-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topic-badges {
  display: flex;
  gap: 4px;
}

.badge-icon {
  padding: 4px;
  border-radius: 4px;
}

.badge-icon.pinned {
  color: var(--success);
  background: rgba(34, 197, 94, 0.15);
}

.badge-icon.locked {
  color: var(--danger);
  background: rgba(239, 68, 68, 0.15);
}

.topic-title {
  font-weight: 500;
  color: var(--text-primary);
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color);
  border-radius: 6px;
  font-size: 12px;
  color: var(--color);
}

.category-tag.small {
  padding: 2px 8px;
  font-size: 11px;
}

.author-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--bg-elevated);
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-weight: 500;
  font-size: 14px;
}

.author-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  color: white;
}

.stats-cell {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.status-badge {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.open {
  background: rgba(34, 197, 94, 0.15);
  color: var(--success);
}

.status-badge.pinned {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info);
}

.status-badge.locked {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.date-text {
  font-size: 13px;
  color: var(--text-muted);
}

.quick-actions {
  display: flex;
  gap: 4px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

tr:hover .quick-actions {
  opacity: 1;
}

.quick-action {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action:hover {
  color: var(--primary);
  border-color: var(--primary);
}

.quick-action.active {
  background: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary);
}

.quick-action.danger:hover {
  color: var(--danger);
  border-color: var(--danger);
  background: rgba(239, 68, 68, 0.1);
}

/* Topic Cards Grid */
.topics-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  padding: 20px;
}

.topic-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
}

.topic-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
  border-color: var(--primary);
}

.topic-card.selected {
  border-color: var(--primary);
  background: var(--primary-light);
}

.topic-card.pinned {
  border-left: 3px solid var(--success);
}

.topic-card.locked {
  border-left: 3px solid var(--danger);
}

.topic-card .card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.card-badges {
  display: flex;
  gap: 4px;
}

.card-badges .pinned {
  color: var(--success);
}

.card-badges .locked {
  color: var(--danger);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 16px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-author {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.post-date {
  font-size: 12px;
  color: var(--text-muted);
}

.card-stats {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 16px;
}

.card-stats .stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-action {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.card-action:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.card-action.active {
  background: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary);
}

.card-action.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: rgba(239, 68, 68, 0.1);
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

.pagination-info {
  font-size: 14px;
  color: var(--text-secondary);
}

.pagination {
  display: flex;
  gap: 4px;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary);
}

.page-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-ellipsis {
  padding: 0 8px;
  color: var(--text-muted);
}

/* Reports List */
.reports-list {
  padding: 20px;
}

.report-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.report-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.report-card.urgent {
  border-color: var(--danger);
  animation: urgentPulse 3s ease-in-out infinite;
}

@keyframes urgentPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
  50% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
}

.report-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.report-type {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.report-type.topic {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info);
}

.report-type.post {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.report-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--danger);
  font-weight: 600;
}

.report-date {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
}

.report-content {
  margin-bottom: 16px;
}

.report-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px;
}

.report-preview {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.report-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  flex-wrap: wrap;
}

.reporter-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.mini-avatar {
  width: 24px;
  height: 24px;
  border-radius: 6px;
}

.report-reasons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.reason-tag {
  padding: 2px 8px;
  background: rgba(239, 68, 68, 0.15);
  border-radius: 4px;
  font-size: 11px;
  color: var(--danger);
}

.report-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.report-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.report-btn.view:hover {
  border-color: var(--info);
  color: var(--info);
}

.report-btn.approve:hover {
  border-color: var(--success);
  color: var(--success);
}

.report-btn.warn:hover {
  border-color: var(--warning);
  color: var(--warning);
}

.report-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: rgba(239, 68, 68, 0.1);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-container.small {
  max-width: 450px;
}

.modal-container.category-modal {
  max-width: 560px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.modal-close {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-info {
  margin: 0 0 20px;
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

/* Form Styles */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input,
.form-select,
.form-textarea {
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: var(--text-muted);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.input-with-prefix {
  display: flex;
  align-items: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.input-with-prefix:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.input-with-prefix .prefix {
  padding: 12px;
  background: var(--bg-elevated);
  color: var(--text-muted);
  font-size: 14px;
  border-right: 1px solid var(--border-color);
}

.input-with-prefix .form-input {
  border: none;
  border-radius: 0;
  background: transparent;
}

.input-with-prefix .form-input:focus {
  box-shadow: none;
}

.icon-picker-wrapper {
  position: relative;
  display: flex;
  gap: 8px;
}

.icon-input {
  flex: 1;
}

.icon-preview {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 24px;
}

.emoji-grid {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  padding: 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 4px;
  z-index: 10;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}

.emoji-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.emoji-btn:hover {
  background: var(--bg-tertiary);
  transform: scale(1.1);
}

.color-picker-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.color-input {
  width: 50px;
  height: 46px;
  padding: 4px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
}

.color-presets {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.color-preset {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.color-preset:hover {
  transform: scale(1.1);
}

.color-preset.selected {
  border-color: white;
  box-shadow: 0 0 0 2px var(--bg-secondary);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
  cursor: pointer;
}

.checkbox-text {
  font-size: 14px;
  color: var(--text-primary);
}

/* Confirm Modal */
.confirm-modal {
  max-width: 400px;
  text-align: center;
  padding: 40px 32px;
}

.confirm-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  border-radius: 50%;
}

.confirm-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.confirm-modal h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 12px;
}

.confirm-modal p {
  color: var(--text-secondary);
  margin: 0 0 28px;
  line-height: 1.6;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Toast Container */
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 9999;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  min-width: 280px;
}

.toast.success {
  border-left: 4px solid var(--success);
}

.toast.success svg {
  color: var(--success);
}

.toast.error {
  border-left: 4px solid var(--danger);
}

.toast.error svg {
  color: var(--danger);
}

.toast.warning {
  border-left: 4px solid var(--warning);
}

.toast.warning svg {
  color: var(--warning);
}

.toast.info {
  border-left: 4px solid var(--info);
}

.toast.info svg {
  color: var(--info);
}

.toast-close {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
}

.toast-close:hover {
  color: var(--text-primary);
}

/* Animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
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

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container,
.modal-enter-from .confirm-modal,
.modal-leave-to .confirm-modal {
  transform: scale(0.95) translateY(10px);
}

.category-list-enter-active,
.category-list-leave-active {
  transition: all 0.4s ease;
}

.category-list-enter-from,
.category-list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.category-list-move {
  transition: transform 0.4s ease;
}

.table-row-enter-active,
.table-row-leave-active {
  transition: all 0.3s ease;
}

.table-row-enter-from,
.table-row-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.card-list-enter-active,
.card-list-leave-active {
  transition: all 0.4s ease;
}

.card-list-enter-from,
.card-list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.card-list-move {
  transition: transform 0.4s ease;
}

.report-list-enter-active,
.report-list-leave-active {
  transition: all 0.4s ease;
}

.report-list-enter-from,
.report-list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.toast-enter-active {
  transition: all 0.3s ease;
}

.toast-leave-active {
  transition: all 0.2s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.9);
}

.toast-move {
  transition: transform 0.3s ease;
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-group.full-width {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .tabs-nav {
    flex-wrap: wrap;
  }

  .tab-button {
    flex: 1;
    min-width: 100px;
    justify-content: center;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .search-box,
  .search-box.large {
    min-width: auto;
    width: 100%;
  }

  .bulk-actions-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .bulk-buttons {
    flex-wrap: wrap;
  }

  .category-card {
    flex-direction: column;
    text-align: center;
  }

  .category-main {
    width: 100%;
  }

  .category-meta {
    justify-content: center;
  }

  .category-actions {
    justify-content: center;
  }

  .topics-cards-grid {
    grid-template-columns: 1fr;
  }

  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }

  .toast-container {
    left: 16px;
    right: 16px;
    bottom: 16px;
  }

  .toast {
    min-width: auto;
  }
}
</style>
