<template>
  <AdminLayout>
    <div class="media-hub">
      <!-- Page Header -->
      <header class="hub-header">
        <div class="header-content">
          <div class="header-title-group">
            <h1 class="header-title">Medya Merkezi</h1>
            <p class="header-subtitle">Görselleri ve bannerlari tek bir yerden yönetin</p>
          </div>
          <div class="header-actions">
            <button class="btn-icon" @click="toggleTheme" title="Tema Degistir">
              <Sun v-if="isDarkMode" :size="20" />
              <Moon v-else :size="20" />
            </button>
            <button class="btn-primary" @click="showUploadModal = true">
              <Upload :size="18" />
              <span>Görsel Yükle</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Tab Navigation -->
      <nav class="tab-navigation">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'library' }"
          @click="activeTab = 'library'"
        >
          <ImageIcon :size="20" />
          <span>Medya Kutuphanesi</span>
          <span class="tab-badge">{{ images.length }}</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'banners' }"
          @click="activeTab = 'banners'"
        >
          <LayoutTemplate :size="20" />
          <span>Banner Yönetimi</span>
          <span class="tab-badge">{{ banners.length }}</span>
        </button>
      </nav>

      <!-- Media Library Tab -->
      <div v-show="activeTab === 'library'" class="tab-content">
        <!-- Toolbar -->
        <div class="toolbar">
          <div class="toolbar-left">
            <!-- View Toggle -->
            <div class="view-toggle">
              <button
                class="toggle-btn"
                :class="{ active: viewMode === 'grid' }"
                @click="viewMode = 'grid'"
                title="Izgara Görünüm"
              >
                <Grid3x3 :size="18" />
              </button>
              <button
                class="toggle-btn"
                :class="{ active: viewMode === 'list' }"
                @click="viewMode = 'list'"
                title="Liste Görünüm"
              >
                <List :size="18" />
              </button>
            </div>

            <!-- Category Filter -->
            <div class="filter-dropdown">
              <button class="dropdown-trigger" @click="showCategoryDropdown = !showCategoryDropdown">
                <Filter :size="16" />
                <span>{{ getCategoryLabel(selectedCategory) }}</span>
                <ChevronDown :size="16" />
              </button>
              <Transition name="dropdown">
                <div v-if="showCategoryDropdown" class="dropdown-menu">
                  <button
                    v-for="cat in categories"
                    :key="cat.value"
                    class="dropdown-item"
                    :class="{ active: selectedCategory === cat.value }"
                    @click="selectCategory(cat.value)"
                  >
                    <component :is="cat.icon" :size="16" />
                    <span>{{ cat.label }}</span>
                    <span class="item-count">{{ getCategoryCount(cat.value) }}</span>
                  </button>
                </div>
              </Transition>
            </div>

            <!-- Bulk Actions -->
            <Transition name="fade">
              <div v-if="selectedImages.length > 0" class="bulk-actions">
                <span class="selected-count">{{ selectedImages.length }} seçili</span>
                <button class="bulk-btn" @click="bulkCopyUrls" title="URL Kopyala">
                  <Link2 :size="16" />
                </button>
                <button class="bulk-btn danger" @click="bulkDelete" title="Sil">
                  <Trash2 :size="16" />
                </button>
                <button class="bulk-btn" @click="clearSelection" title="Seçimi Temizle">
                  <X :size="16" />
                </button>
              </div>
            </Transition>
          </div>

          <div class="toolbar-right">
            <!-- Search -->
            <div class="search-wrapper">
              <Search :size="18" class="search-icon" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Görsel ara..."
                class="search-input"
              />
              <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
                <X :size="16" />
              </button>
            </div>
          </div>
        </div>

        <!-- Drop Zone -->
        <Transition name="expand">
          <div
            v-if="isDraggingOver"
            class="drop-zone-overlay"
            @dragover.prevent
            @dragleave="isDraggingOver = false"
            @drop.prevent="handleDrop"
          >
            <div class="drop-zone-content">
              <Upload :size="64" class="drop-icon" />
              <h3>Görselleri Birakin</h3>
              <p>Dosyalari buraya birakin</p>
            </div>
          </div>
        </Transition>

        <!-- Images Grid/List -->
        <div
          class="media-container"
          @dragover.prevent="isDraggingOver = true"
        >
          <!-- Grid View -->
          <TransitionGroup
            v-if="viewMode === 'grid'"
            name="grid"
            tag="div"
            class="images-grid"
          >
            <div
              v-for="image in filteredImages"
              :key="image.id"
              class="image-card"
              :class="{ selected: isImageSelected(image.id) }"
              @click.exact="openImagePreview(image)"
              @click.ctrl="toggleImageSelection(image.id)"
              @click.meta="toggleImageSelection(image.id)"
            >
              <div class="card-checkbox" @click.stop="toggleImageSelection(image.id)">
                <div class="checkbox" :class="{ checked: isImageSelected(image.id) }">
                  <Check v-if="isImageSelected(image.id)" :size="12" />
                </div>
              </div>
              <div class="card-image">
                <img :src="getImageUrl(image)" :alt="image.name" loading="lazy" />
                <div class="card-overlay">
                  <div class="overlay-actions">
                    <button class="action-btn" @click.stop="openImagePreview(image)" title="Onizle">
                      <Eye :size="18" />
                    </button>
                    <button class="action-btn" @click.stop="copyImageUrl(image)" title="URL Kopyala">
                      <Link2 :size="18" />
                    </button>
                    <button class="action-btn" @click.stop="openEditModal(image)" title="Düzenle">
                      <Pencil :size="18" />
                    </button>
                    <button class="action-btn danger" @click.stop="deleteImage(image)" title="Sil">
                      <Trash2 :size="18" />
                    </button>
                  </div>
                </div>
              </div>
              <div class="card-info">
                <span class="card-name" :title="image.name">{{ image.name }}</span>
                <div class="card-meta">
                  <span class="category-tag" :class="image.category">
                    {{ getCategoryLabel(image.category) }}
                  </span>
                  <span class="file-size">{{ formatFileSize(image.file_size) }}</span>
                </div>
              </div>
            </div>
          </TransitionGroup>

          <!-- List View -->
          <div v-else class="images-list">
            <div class="list-header">
              <div class="list-col checkbox-col">
                <div
                  class="checkbox"
                  :class="{ checked: allSelected, indeterminate: someSelected }"
                  @click="toggleSelectAll"
                >
                  <Check v-if="allSelected" :size="12" />
                  <Minus v-else-if="someSelected" :size="12" />
                </div>
              </div>
              <div class="list-col preview-col">Onizleme</div>
              <div class="list-col name-col">Ad</div>
              <div class="list-col category-col">Kategori</div>
              <div class="list-col size-col">Boyut</div>
              <div class="list-col dimensions-col">Cozunurluk</div>
              <div class="list-col date-col">Tarih</div>
              <div class="list-col actions-col">İşlemler</div>
            </div>
            <TransitionGroup name="list" tag="div" class="list-body">
              <div
                v-for="image in filteredImages"
                :key="image.id"
                class="list-row"
                :class="{ selected: isImageSelected(image.id) }"
              >
                <div class="list-col checkbox-col">
                  <div
                    class="checkbox"
                    :class="{ checked: isImageSelected(image.id) }"
                    @click="toggleImageSelection(image.id)"
                  >
                    <Check v-if="isImageSelected(image.id)" :size="12" />
                  </div>
                </div>
                <div class="list-col preview-col">
                  <img :src="getImageUrl(image)" :alt="image.name" class="list-thumbnail" />
                </div>
                <div class="list-col name-col">
                  <span class="file-name">{{ image.name }}</span>
                </div>
                <div class="list-col category-col">
                  <span class="category-tag" :class="image.category">
                    {{ getCategoryLabel(image.category) }}
                  </span>
                </div>
                <div class="list-col size-col">
                  {{ formatFileSize(image.file_size) }}
                </div>
                <div class="list-col dimensions-col">
                  {{ image.width || '?' }}x{{ image.height || '?' }}
                </div>
                <div class="list-col date-col">
                  {{ formatDate(image.created_at) }}
                </div>
                <div class="list-col actions-col">
                  <div class="row-actions">
                    <button class="row-btn" @click="openImagePreview(image)" title="Onizle">
                      <Eye :size="16" />
                    </button>
                    <button class="row-btn" @click="copyImageUrl(image)" title="URL Kopyala">
                      <Link2 :size="16" />
                    </button>
                    <button class="row-btn" @click="openEditModal(image)" title="Düzenle">
                      <Pencil :size="16" />
                    </button>
                    <button class="row-btn danger" @click="deleteImage(image)" title="Sil">
                      <Trash2 :size="16" />
                    </button>
                  </div>
                </div>
              </div>
            </TransitionGroup>
          </div>

          <!-- Empty State -->
          <div v-if="filteredImages.length === 0" class="empty-state">
            <div class="empty-icon">
              <ImageIcon :size="64" />
            </div>
            <h3>Görsel Bulunamadı</h3>
            <p v-if="searchQuery">Arama kriterlerinize uygun görsel yok</p>
            <p v-else>Henüz görsel yüklenmemis</p>
            <button class="btn-primary" @click="showUploadModal = true">
              <Upload :size="18" />
              <span>İlk Görseli Yükle</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Banner Management Tab -->
      <div v-show="activeTab === 'banners'" class="tab-content">
        <!-- Banner Positions Grid -->
        <div class="banner-positions">
          <h2 class="section-title">
            <LayoutTemplate :size="20" />
            Banner Pozisyonlari
          </h2>
          <div class="positions-grid">
            <div
              v-for="position in bannerPositions"
              :key="position.id"
              class="position-card"
              :class="{ 'has-banner': getBannerByPosition(position.id) }"
            >
              <div class="position-header">
                <div class="position-info">
                  <component :is="position.icon" :size="20" class="position-icon" />
                  <div>
                    <h3>{{ position.name }}</h3>
                    <span class="position-dimensions">{{ position.dimensions }}</span>
                  </div>
                </div>
                <div class="position-status">
                  <span
                    class="status-dot"
                    :class="{ active: getBannerByPosition(position.id)?.is_active }"
                  ></span>
                  <span class="status-text">
                    {{ getBannerByPosition(position.id)?.is_active ? 'Aktif' : 'Pasif' }}
                  </span>
                </div>
              </div>
              <div class="position-preview" :style="{ aspectRatio: position.ratio }">
                <div v-if="getBannerByPosition(position.id)" class="banner-content">
                  <img :src="getBannerByPosition(position.id).image_url" :alt="position.name" />
                  <div class="banner-overlay">
                    <button
                      class="preview-btn"
                      @click="previewBanner(getBannerByPosition(position.id))"
                      title="Onizle"
                    >
                      <Eye :size="20" />
                    </button>
                    <button
                      class="preview-btn"
                      @click="editBanner(getBannerByPosition(position.id))"
                      title="Düzenle"
                    >
                      <Pencil :size="20" />
                    </button>
                    <button
                      class="preview-btn danger"
                      @click="deleteBanner(getBannerByPosition(position.id))"
                      title="Sil"
                    >
                      <Trash2 :size="20" />
                    </button>
                  </div>
                </div>
                <div v-else class="empty-slot" @click="createBannerForPosition(position.id)">
                  <Plus :size="32" class="plus-icon" />
                  <span>Banner Ekle</span>
                </div>
              </div>
              <div v-if="getBannerByPosition(position.id)" class="position-footer">
                <div class="schedule-info">
                  <Calendar :size="14" />
                  <span v-if="getBannerByPosition(position.id).start_date">
                    {{ formatDate(getBannerByPosition(position.id).start_date) }}
                  </span>
                  <span v-else>Surekli</span>
                </div>
                <div class="link-info" v-if="getBannerByPosition(position.id).link">
                  <ExternalLink :size="14" />
                  <span>Link mevcut</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- All Banners List -->
        <div class="banners-list-section">
          <div class="section-header">
            <h2 class="section-title">
              <Layers :size="20" />
              Tüm Bannerlar
            </h2>
            <button class="btn-primary" @click="openBannerModal()">
              <Plus :size="18" />
              <span>Yeni Banner</span>
            </button>
          </div>
          <div class="banners-table-wrapper">
            <table class="banners-table">
              <thead>
                <tr>
                  <th>Onizleme</th>
                  <th>Başlık</th>
                  <th>Pozisyon</th>
                  <th>Tarih Araligi</th>
                  <th>Link</th>
                  <th>Durum</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                <TransitionGroup name="table">
                  <tr v-for="banner in banners" :key="banner.id">
                    <td>
                      <div class="table-preview" @click="previewBanner(banner)">
                        <img :src="banner.image_url" :alt="banner.title" />
                      </div>
                    </td>
                    <td>
                      <span class="banner-title">{{ banner.title }}</span>
                    </td>
                    <td>
                      <span class="position-badge">
                        {{ getPositionName(banner.position) }}
                      </span>
                    </td>
                    <td>
                      <div class="date-range">
                        <span v-if="banner.start_date || banner.end_date">
                          {{ formatDate(banner.start_date) || 'Başlangıç yok' }}
                          <ArrowRight :size="12" />
                          {{ formatDate(banner.end_date) || 'Bitis yok' }}
                        </span>
                        <span v-else class="no-date">Surekli</span>
                      </div>
                    </td>
                    <td>
                      <a
                        v-if="banner.link"
                        :href="banner.link"
                        target="_blank"
                        class="link-preview"
                      >
                        <ExternalLink :size="14" />
                        <span>{{ truncateUrl(banner.link) }}</span>
                      </a>
                      <span v-else class="no-link">-</span>
                    </td>
                    <td>
                      <button
                        class="status-toggle"
                        :class="{ active: banner.is_active }"
                        @click="toggleBannerStatus(banner)"
                      >
                        <span class="toggle-track">
                          <span class="toggle-thumb"></span>
                        </span>
                        <span class="toggle-label">{{ banner.is_active ? 'Aktif' : 'Pasif' }}</span>
                      </button>
                    </td>
                    <td>
                      <div class="table-actions">
                        <button class="table-btn" @click="previewBanner(banner)" title="Onizle">
                          <Eye :size="16" />
                        </button>
                        <button class="table-btn" @click="editBanner(banner)" title="Düzenle">
                          <Pencil :size="16" />
                        </button>
                        <button class="table-btn danger" @click="deleteBanner(banner)" title="Sil">
                          <Trash2 :size="16" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </TransitionGroup>
              </tbody>
            </table>
            <div v-if="banners.length === 0" class="empty-table">
              <LayoutTemplate :size="48" />
              <p>Henüz banner eklenmemis</p>
              <button class="btn-primary" @click="openBannerModal()">
                <Plus :size="18" />
                <span>İlk Banneri Oluştur</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showUploadModal" class="modal-backdrop" @click.self="showUploadModal = false">
            <div class="modal upload-modal">
              <div class="modal-header">
                <h2>Görsel Yükle</h2>
                <button class="modal-close" @click="showUploadModal = false">
                  <X :size="24" />
                </button>
              </div>
              <div class="modal-body">
                <!-- Upload Drop Zone -->
                <div
                  class="upload-dropzone"
                  :class="{ dragging: isUploadDragging, 'has-files': uploadQueue.length > 0 }"
                  @dragover.prevent="isUploadDragging = true"
                  @dragleave="isUploadDragging = false"
                  @drop.prevent="handleUploadDrop"
                  @click="triggerFileInput"
                >
                  <input
                    ref="fileInput"
                    type="file"
                    accept="image/*"
                    multiple
                    hidden
                    @change="handleFileSelect"
                  />
                  <div class="dropzone-content">
                    <div class="dropzone-icon">
                      <CloudUpload :size="48" />
                    </div>
                    <h3>Görselleri sürükleyin veya tıklayin</h3>
                    <p>PNG, JPG, GIF, SVG, WEBP (max 10MB)</p>
                  </div>
                </div>

                <!-- Category Selection -->
                <div class="upload-options">
                  <label class="option-label">Kategori</label>
                  <div class="category-chips">
                    <button
                      v-for="cat in uploadCategories"
                      :key="cat.value"
                      class="category-chip"
                      :class="{ active: uploadCategory === cat.value }"
                      @click="uploadCategory = cat.value"
                    >
                      <component :is="cat.icon" :size="16" />
                      <span>{{ cat.label }}</span>
                    </button>
                  </div>
                </div>

                <!-- Upload Queue -->
                <Transition name="expand">
                  <div v-if="uploadQueue.length > 0" class="upload-queue">
                    <div class="queue-header">
                      <span>{{ uploadQueue.length }} dosya seçildi</span>
                      <button class="clear-queue" @click="clearUploadQueue">
                        Temizle
                      </button>
                    </div>
                    <div class="queue-list">
                      <TransitionGroup name="queue">
                        <div v-for="(file, index) in uploadQueue" :key="file.id" class="queue-item">
                          <img :src="file.preview" class="queue-thumbnail" />
                          <div class="queue-info">
                            <span class="queue-name">{{ file.name }}</span>
                            <span class="queue-size">{{ formatFileSize(file.size) }}</span>
                          </div>
                          <div v-if="file.uploading" class="queue-progress">
                            <div class="progress-bar" :style="{ width: file.progress + '%' }"></div>
                          </div>
                          <button v-else class="queue-remove" @click="removeFromQueue(index)">
                            <X :size="16" />
                          </button>
                        </div>
                      </TransitionGroup>
                    </div>
                  </div>
                </Transition>
              </div>
              <div class="modal-footer">
                <button class="btn-secondary" @click="showUploadModal = false">
                  İptal
                </button>
                <button
                  class="btn-primary"
                  :disabled="uploadQueue.length === 0 || uploading"
                  @click="uploadFiles"
                >
                  <Loader2 v-if="uploading" :size="18" class="spin" />
                  <Upload v-else :size="18" />
                  <span>{{ uploading ? 'Yükleniyor...' : `${uploadQueue.length} Dosya Yükle` }}</span>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Image Preview Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="previewImage" class="modal-backdrop preview-backdrop" @click.self="previewImage = null">
            <div class="preview-modal">
              <button class="preview-close" @click="previewImage = null">
                <X :size="24" />
              </button>
              <div class="preview-container">
                <div class="preview-image-wrapper">
                  <img
                    :src="getImageUrl(previewImage)"
                    :alt="previewImage.name"
                    :style="{ transform: `scale(${zoomLevel})` }"
                  />
                </div>
                <div class="zoom-controls">
                  <button @click="zoomOut" :disabled="zoomLevel <= 0.5">
                    <ZoomOut :size="20" />
                  </button>
                  <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
                  <button @click="zoomIn" :disabled="zoomLevel >= 3">
                    <ZoomIn :size="20" />
                  </button>
                  <button @click="resetZoom">
                    <Maximize2 :size="20" />
                  </button>
                </div>
              </div>
              <div class="preview-sidebar">
                <h3>Görsel Bilgileri</h3>
                <div class="info-group">
                  <label>Ad</label>
                  <span>{{ previewImage.name }}</span>
                </div>
                <div class="info-group">
                  <label>Kategori</label>
                  <span class="category-tag" :class="previewImage.category">
                    {{ getCategoryLabel(previewImage.category) }}
                  </span>
                </div>
                <div class="info-group">
                  <label>Boyut</label>
                  <span>{{ formatFileSize(previewImage.file_size) }}</span>
                </div>
                <div class="info-group">
                  <label>Cozunurluk</label>
                  <span>{{ previewImage.width || '?' }}x{{ previewImage.height || '?' }}px</span>
                </div>
                <div class="info-group">
                  <label>Yükleme Tarihi</label>
                  <span>{{ formatDate(previewImage.created_at) }}</span>
                </div>
                <div class="info-group url-group">
                  <label>URL</label>
                  <div class="url-copy-field">
                    <input :value="getFullImageUrl(previewImage)" readonly />
                    <button @click="copyImageUrl(previewImage)" title="Kopyala">
                      <Copy :size="16" />
                    </button>
                  </div>
                </div>
                <div class="preview-actions">
                  <button class="btn-secondary" @click="openEditModal(previewImage)">
                    <Pencil :size="16" />
                    Düzenle
                  </button>
                  <button class="btn-danger" @click="deleteImage(previewImage)">
                    <Trash2 :size="16" />
                    Sil
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Edit Image Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="editingImage" class="modal-backdrop" @click.self="editingImage = null">
            <div class="modal edit-modal">
              <div class="modal-header">
                <h2>Görseli Düzenle</h2>
                <button class="modal-close" @click="editingImage = null">
                  <X :size="24" />
                </button>
              </div>
              <div class="modal-body">
                <div class="edit-preview">
                  <img :src="getImageUrl(editingImage)" :alt="editingImage.name" />
                </div>
                <div class="form-group">
                  <label>Görsel Adi</label>
                  <input v-model="editingImage.name" type="text" />
                </div>
                <div class="form-group">
                  <label>Alt Text (SEO)</label>
                  <input v-model="editingImage.alt_text" type="text" placeholder="Görsel açıklamasi" />
                </div>
                <div class="form-group">
                  <label>Kategori</label>
                  <select v-model="editingImage.category">
                    <option v-for="cat in uploadCategories" :key="cat.value" :value="cat.value">
                      {{ cat.label }}
                    </option>
                  </select>
                </div>
                <div class="form-info">
                  <div class="info-item">
                    <HardDrive :size="16" />
                    <span>{{ formatFileSize(editingImage.file_size) }}</span>
                  </div>
                  <div class="info-item">
                    <Maximize2 :size="16" />
                    <span>{{ editingImage.width || '?' }}x{{ editingImage.height || '?' }}px</span>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn-secondary" @click="editingImage = null">
                  İptal
                </button>
                <button class="btn-primary" @click="saveImage">
                  <Save :size="18" />
                  Kaydet
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Banner Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showBannerModal" class="modal-backdrop" @click.self="closeBannerModal">
            <div class="modal banner-modal">
              <div class="modal-header">
                <h2>{{ editingBanner ? 'Banner Düzenle' : 'Yeni Banner' }}</h2>
                <button class="modal-close" @click="closeBannerModal">
                  <X :size="24" />
                </button>
              </div>
              <div class="modal-body">
                <div class="form-group">
                  <label>Başlık *</label>
                  <input v-model="bannerForm.title" type="text" placeholder="Banner basligi" />
                </div>

                <div class="form-group">
                  <label>Görsel *</label>
                  <div class="image-selector">
                    <div v-if="bannerForm.image_url" class="selected-image">
                      <img :src="bannerForm.image_url" />
                      <button class="remove-image" @click="bannerForm.image_url = ''">
                        <X :size="16" />
                      </button>
                    </div>
                    <div v-else class="image-placeholder" @click="showImagePicker = true">
                      <ImageIcon :size="32" />
                      <span>Görsel Seç</span>
                    </div>
                    <div class="image-input-group">
                      <input
                        v-model="bannerForm.image_url"
                        type="text"
                        placeholder="veya URL girin"
                      />
                      <button class="browse-btn" @click="showImagePicker = true">
                        <FolderOpen :size="16" />
                      </button>
                    </div>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Pozisyon *</label>
                    <select v-model="bannerForm.position">
                      <option v-for="pos in bannerPositions" :key="pos.id" :value="pos.id">
                        {{ pos.name }} ({{ pos.dimensions }})
                      </option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Link (opsiyonel)</label>
                    <input v-model="bannerForm.link" type="url" placeholder="https://..." />
                  </div>
                </div>

                <div class="form-group">
                  <label>Link Ayarları</label>
                  <div class="link-options">
                    <label class="checkbox-option">
                      <input type="checkbox" v-model="bannerForm.open_new_tab" />
                      <span>Yeni sekmede ac</span>
                    </label>
                    <label class="checkbox-option">
                      <input type="checkbox" v-model="bannerForm.nofollow" />
                      <span>Nofollow ekle</span>
                    </label>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Başlangıç Tarihi</label>
                    <input v-model="bannerForm.start_date" type="datetime-local" />
                  </div>
                  <div class="form-group">
                    <label>Bitis Tarihi</label>
                    <input v-model="bannerForm.end_date" type="datetime-local" />
                  </div>
                </div>

                <div class="form-group">
                  <label class="switch-label">
                    <span>Aktif</span>
                    <button
                      class="switch"
                      :class="{ active: bannerForm.is_active }"
                      @click="bannerForm.is_active = !bannerForm.is_active"
                    >
                      <span class="switch-thumb"></span>
                    </button>
                  </label>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn-secondary" @click="closeBannerModal">
                  İptal
                </button>
                <button class="btn-primary" @click="saveBanner">
                  <Save :size="18" />
                  {{ editingBanner ? 'Güncelle' : 'Oluştur' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Banner Preview Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="previewingBanner" class="modal-backdrop preview-backdrop" @click.self="previewingBanner = null">
            <div class="banner-preview-modal">
              <button class="preview-close" @click="previewingBanner = null">
                <X :size="24" />
              </button>
              <div class="banner-preview-content">
                <h3>{{ previewingBanner.title }}</h3>
                <div class="banner-preview-image">
                  <img :src="previewingBanner.image_url" :alt="previewingBanner.title" />
                </div>
                <div class="banner-preview-info">
                  <div class="info-item">
                    <LayoutTemplate :size="16" />
                    <span>{{ getPositionName(previewingBanner.position) }}</span>
                  </div>
                  <div v-if="previewingBanner.link" class="info-item">
                    <ExternalLink :size="16" />
                    <a :href="previewingBanner.link" target="_blank">{{ previewingBanner.link }}</a>
                  </div>
                  <div class="info-item">
                    <Calendar :size="16" />
                    <span v-if="previewingBanner.start_date || previewingBanner.end_date">
                      {{ formatDate(previewingBanner.start_date) || 'Başlangıç yok' }} -
                      {{ formatDate(previewingBanner.end_date) || 'Bitis yok' }}
                    </span>
                    <span v-else>Surekli</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Image Picker Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showImagePicker" class="modal-backdrop" @click.self="showImagePicker = false">
            <div class="modal picker-modal">
              <div class="modal-header">
                <h2>Görsel Seç</h2>
                <button class="modal-close" @click="showImagePicker = false">
                  <X :size="24" />
                </button>
              </div>
              <div class="modal-body">
                <div class="picker-search">
                  <Search :size="18" />
                  <input v-model="pickerSearch" type="text" placeholder="Görsel ara..." />
                </div>
                <div class="picker-grid">
                  <div
                    v-for="image in pickerFilteredImages"
                    :key="image.id"
                    class="picker-item"
                    :class="{ selected: pickerSelected === image.id }"
                    @click="pickerSelected = image.id"
                  >
                    <img :src="getImageUrl(image)" :alt="image.name" />
                    <div class="picker-check" v-if="pickerSelected === image.id">
                      <Check :size="16" />
                    </div>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn-secondary" @click="showImagePicker = false">
                  İptal
                </button>
                <button class="btn-primary" @click="selectPickerImage" :disabled="!pickerSelected">
                  <Check :size="18" />
                  Seç
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Toast Notifications -->
      <div class="toast-container">
        <TransitionGroup name="toast">
          <div v-for="toast in toasts" :key="toast.id" class="toast" :class="toast.type">
            <component :is="toast.icon" :size="18" />
            <span>{{ toast.message }}</span>
          </div>
        </TransitionGroup>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Upload, Search, Image as ImageIcon, Trash2, X, Loader2, Copy, Save,
  Grid3x3, List, Filter, ChevronDown, Link2, Eye, Pencil, Check, Minus,
  Plus, LayoutTemplate, Layers, Calendar, ExternalLink, ArrowRight,
  ZoomIn, ZoomOut, Maximize2, CloudUpload, HardDrive, FolderOpen,
  Sun, Moon, Star, Flag, Bookmark, FileImage, Monitor, Sidebar, Layout
} from 'lucide-vue-next'

const authStore = useAuthStore()

// ============================================
// UTILITY FUNCTIONS
// ============================================

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

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (date) => {
  if (!date) return null
  return new Date(date).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const truncateUrl = (url) => {
  if (!url) return ''
  try {
    const parsed = new URL(url)
    return parsed.hostname + (parsed.pathname.length > 20 ? parsed.pathname.slice(0, 20) + '...' : parsed.pathname)
  } catch {
    return url.length > 30 ? url.slice(0, 30) + '...' : url
  }
}

// ============================================
// STATE
// ============================================

// General
const activeTab = ref('library')
const isDarkMode = ref(true)
const toasts = ref([])
let toastId = 0

// Media Library
const images = ref([])
const selectedImages = ref([])
const viewMode = ref('grid')
const selectedCategory = ref('all')
const searchQuery = ref('')
const showCategoryDropdown = ref(false)
const isDraggingOver = ref(false)
const previewImage = ref(null)
const editingImage = ref(null)
const zoomLevel = ref(1)

// Upload
const showUploadModal = ref(false)
const uploadQueue = ref([])
const uploadCategory = ref('general')
const isUploadDragging = ref(false)
const uploading = ref(false)
const fileInput = ref(null)

// Banners
const banners = ref([])
const showBannerModal = ref(false)
const editingBanner = ref(null)
const previewingBanner = ref(null)
const bannerForm = reactive({
  title: '',
  image_url: '',
  position: 'hero',
  link: '',
  open_new_tab: true,
  nofollow: false,
  start_date: '',
  end_date: '',
  is_active: true
})

// Image Picker
const showImagePicker = ref(false)
const pickerSearch = ref('')
const pickerSelected = ref(null)

// ============================================
// CONSTANTS
// ============================================

const categories = [
  { value: 'all', label: 'Tümü', icon: Grid3x3 },
  { value: 'logo', label: 'Logolar', icon: Star },
  { value: 'icon', label: 'Ikonlar', icon: Flag },
  { value: 'banner', label: 'Bannerlar', icon: LayoutTemplate },
  { value: 'general', label: 'Yüklemeler', icon: FileImage }
]

const uploadCategories = [
  { value: 'general', label: 'Genel', icon: FileImage },
  { value: 'logo', label: 'Logo', icon: Star },
  { value: 'icon', label: 'Ikon', icon: Flag },
  { value: 'banner', label: 'Banner', icon: LayoutTemplate }
]

const bannerPositions = [
  { id: 'hero', name: 'Hero', dimensions: '1920x600', ratio: '1920/600', icon: Monitor },
  { id: 'sidebar', name: 'Sidebar', dimensions: '300x250', ratio: '300/250', icon: Sidebar },
  { id: 'footer', name: 'Footer', dimensions: '728x90', ratio: '728/90', icon: Layout },
  { id: 'popup', name: 'Popup', dimensions: '600x400', ratio: '600/400', icon: Maximize2 }
]

// ============================================
// COMPUTED
// ============================================

const filteredImages = computed(() => {
  let result = images.value

  if (selectedCategory.value !== 'all') {
    result = result.filter(img => img.category === selectedCategory.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(img =>
      img.name?.toLowerCase().includes(query) ||
      img.alt_text?.toLowerCase().includes(query)
    )
  }

  return result
})

const allSelected = computed(() => {
  return filteredImages.value.length > 0 &&
    filteredImages.value.every(img => selectedImages.value.includes(img.id))
})

const someSelected = computed(() => {
  return selectedImages.value.length > 0 && !allSelected.value
})

const pickerFilteredImages = computed(() => {
  if (!pickerSearch.value) return images.value
  const query = pickerSearch.value.toLowerCase()
  return images.value.filter(img =>
    img.name?.toLowerCase().includes(query)
  )
})

// ============================================
// METHODS - General
// ============================================

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
}

const showToast = (message, type = 'success') => {
  const icons = {
    success: Check,
    error: X,
    info: Eye
  }
  const toast = {
    id: ++toastId,
    message,
    type,
    icon: icons[type] || Check
  }
  toasts.value.push(toast)
  setTimeout(() => {
    const index = toasts.value.findIndex(t => t.id === toast.id)
    if (index > -1) toasts.value.splice(index, 1)
  }, 3000)
}

// ============================================
// METHODS - Media Library
// ============================================

const getCategoryLabel = (category) => {
  const cat = categories.find(c => c.value === category)
  return cat?.label || category || 'Genel'
}

const getCategoryCount = (category) => {
  if (category === 'all') return images.value.length
  return images.value.filter(img => img.category === category).length
}

const selectCategory = (category) => {
  selectedCategory.value = category
  showCategoryDropdown.value = false
}

const getImageUrl = (image) => {
  if (!image?.file_path) return ''
  if (image.file_path.startsWith('http')) return image.file_path
  if (image.file_path.startsWith('/')) return image.file_path
  return '/' + image.file_path
}

const getFullImageUrl = (image) => {
  return window.location.origin + getImageUrl(image)
}

const isImageSelected = (id) => {
  return selectedImages.value.includes(id)
}

const toggleImageSelection = (id) => {
  const index = selectedImages.value.indexOf(id)
  if (index > -1) {
    selectedImages.value.splice(index, 1)
  } else {
    selectedImages.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedImages.value = []
  } else {
    selectedImages.value = filteredImages.value.map(img => img.id)
  }
}

const clearSelection = () => {
  selectedImages.value = []
}

const openImagePreview = (image) => {
  previewImage.value = image
  zoomLevel.value = 1
}

const openEditModal = (image) => {
  editingImage.value = { ...image }
  previewImage.value = null
}

const zoomIn = () => {
  if (zoomLevel.value < 3) zoomLevel.value += 0.25
}

const zoomOut = () => {
  if (zoomLevel.value > 0.5) zoomLevel.value -= 0.25
}

const resetZoom = () => {
  zoomLevel.value = 1
}

const copyImageUrl = (image) => {
  const url = getFullImageUrl(image)
  navigator.clipboard.writeText(url)
  showToast('URL kopyalandi!')
}

const bulkCopyUrls = () => {
  const urls = selectedImages.value
    .map(id => images.value.find(img => img.id === id))
    .filter(Boolean)
    .map(img => getFullImageUrl(img))
    .join('\n')
  navigator.clipboard.writeText(urls)
  showToast(`${selectedImages.value.length} URL kopyalandi!`)
}

const bulkDelete = async () => {
  if (!confirm(`${selectedImages.value.length} görseli silmek istediğinize emin misiniz?`)) return

  for (const id of selectedImages.value) {
    try {
      await fetch(`/api/admin/media/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
      })
    } catch (e) {
      // Error handled
    }
  }

  selectedImages.value = []
  fetchImages()
  showToast('Görseller silindi!')
}

// ============================================
// METHODS - Upload
// ============================================

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addToQueue(files)
}

const handleDrop = (event) => {
  isDraggingOver.value = false
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  if (files.length > 0) {
    showUploadModal.value = true
    addToQueue(files)
  }
}

const handleUploadDrop = (event) => {
  isUploadDragging.value = false
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  addToQueue(files)
}

let fileId = 0
const addToQueue = (files) => {
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadQueue.value.push({
        id: ++fileId,
        file,
        name: file.name,
        size: file.size,
        preview: e.target.result,
        uploading: false,
        progress: 0
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeFromQueue = (index) => {
  uploadQueue.value.splice(index, 1)
}

const clearUploadQueue = () => {
  uploadQueue.value = []
}

const uploadFiles = async () => {
  uploading.value = true

  for (const item of uploadQueue.value) {
    item.uploading = true
    try {
      const formData = new FormData()
      formData.append('file', item.file)
      formData.append('category', uploadCategory.value)

      const response = await fetch('/api/admin/media/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        },
        body: formData
      })

      if (response.ok) {
        item.progress = 100
      }
    } catch (e) {
      // Error handled
    }
  }

  uploading.value = false
  showUploadModal.value = false
  uploadQueue.value = []
  fetchImages()
  showToast('Görseller yüklendi!')
}

// ============================================
// METHODS - Images CRUD
// ============================================

const fetchImages = async () => {
  try {
    const response = await fetch('/api/admin/media', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      images.value = data.images || data || []
    }
  } catch (e) {
    // Error handled
    // Fallback data
    images.value = [
      { id: 1, name: 'agtr-logo-main', file_path: '/static/images/logos/agtr-logo-main.png', category: 'logo', file_size: 1302574, width: 512, height: 512 },
      { id: 2, name: 'agtr-logo-alt', file_path: '/static/images/logos/agtr-logo-alt.png', category: 'logo', file_size: 1244335, width: 512, height: 512 },
      { id: 3, name: 'agtr-badge', file_path: '/static/images/icons/agtr-badge.png', category: 'icon', file_size: 2663961, width: 256, height: 256 },
      { id: 4, name: 'ct-icon', file_path: '/static/images/icons/ct-icon.png', category: 'icon', file_size: 1613324, width: 128, height: 128 },
      { id: 5, name: 'hero-banner', file_path: '/static/images/banners/hero-banner.png', category: 'banner', file_size: 2815763, width: 1920, height: 600 },
      { id: 6, name: 'logo-navbar', file_path: '/logo-navbar.png', category: 'logo', file_size: 14870, width: 200, height: 50 }
    ]
  }
}

const saveImage = async () => {
  try {
    const response = await fetch(`/api/admin/media/${editingImage.value.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(editingImage.value)
    })

    if (response.ok) {
      editingImage.value = null
      fetchImages()
      showToast('Görsel güncellendi!')
    }
  } catch (e) {
    // Error handled
    showToast('Hata oluştu!', 'error')
  }
}

const deleteImage = async (image) => {
  if (!confirm(`"${image.name}" görselini silmek istediğinize emin misiniz?`)) return

  try {
    const response = await fetch(`/api/admin/media/${image.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })

    if (response.ok) {
      previewImage.value = null
      editingImage.value = null
      fetchImages()
      showToast('Görsel silindi!')
    }
  } catch (e) {
    // Error handled
    showToast('Hata oluştu!', 'error')
  }
}

// ============================================
// METHODS - Banners
// ============================================

const getBannerByPosition = (positionId) => {
  return banners.value.find(b => b.position === positionId)
}

const getPositionName = (positionId) => {
  return bannerPositions.find(p => p.id === positionId)?.name || positionId
}

const openBannerModal = () => {
  showBannerModal.value = true
  editingBanner.value = null
  Object.assign(bannerForm, {
    title: '',
    image_url: '',
    position: 'hero',
    link: '',
    open_new_tab: true,
    nofollow: false,
    start_date: '',
    end_date: '',
    is_active: true
  })
}

const createBannerForPosition = (positionId) => {
  openBannerModal()
  bannerForm.position = positionId
}

const editBanner = (banner) => {
  editingBanner.value = banner
  Object.assign(bannerForm, {
    title: banner.title || '',
    image_url: banner.image_url || '',
    position: banner.position || 'hero',
    link: banner.link || '',
    open_new_tab: banner.open_new_tab ?? true,
    nofollow: banner.nofollow ?? false,
    start_date: banner.start_date || '',
    end_date: banner.end_date || '',
    is_active: banner.is_active ?? true
  })
  showBannerModal.value = true
}

const closeBannerModal = () => {
  showBannerModal.value = false
  editingBanner.value = null
}

const previewBanner = (banner) => {
  previewingBanner.value = banner
}

const toggleBannerStatus = async (banner) => {
  banner.is_active = !banner.is_active
  try {
    await fetch(`/api/admin/banners/${banner.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ is_active: banner.is_active })
    })
    showToast(banner.is_active ? 'Banner aktif edildi!' : 'Banner pasif edildi!')
  } catch (e) {
    // Error handled
    banner.is_active = !banner.is_active
  }
}

const fetchBanners = async () => {
  try {
    const response = await fetch('/api/admin/banners', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      banners.value = data.banners || data || []
    }
  } catch (e) {
    // Error handled
    banners.value = [
      {
        id: 1,
        title: 'Ana Sayfa Banner',
        image_url: '/static/images/banners/hero-banner.png',
        position: 'hero',
        link: '',
        is_active: true
      }
    ]
  }
}

const saveBanner = async () => {
  try {
    const method = editingBanner.value ? 'PUT' : 'POST'
    const url = editingBanner.value
      ? `/api/admin/banners/${editingBanner.value.id}`
      : '/api/admin/banners'

    const response = await fetch(url, {
      method,
      headers: getHeaders(),
      body: JSON.stringify(bannerForm)
    })

    if (response.ok) {
      closeBannerModal()
      fetchBanners()
      showToast(editingBanner.value ? 'Banner güncellendi!' : 'Banner oluşturuldu!')
    }
  } catch (e) {
    // Error handled
    showToast('Hata oluştu!', 'error')
  }
}

const deleteBanner = async (banner) => {
  if (!confirm('Bu banneri silmek istediğinize emin misiniz?')) return

  try {
    const response = await fetch(`/api/admin/banners/${banner.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (response.ok) {
      banners.value = banners.value.filter(b => b.id !== banner.id)
      showToast('Banner silindi!')
    }
  } catch (e) {
    // Error handled
    showToast('Hata oluştu!', 'error')
  }
}

// ============================================
// METHODS - Image Picker
// ============================================

const selectPickerImage = () => {
  const image = images.value.find(img => img.id === pickerSelected.value)
  if (image) {
    bannerForm.image_url = getImageUrl(image)
    showImagePicker.value = false
    pickerSelected.value = null
    pickerSearch.value = ''
  }
}

// ============================================
// LIFECYCLE
// ============================================

onMounted(() => {
  fetchImages()
  fetchBanners()
})

// Close dropdown on click outside
watch(showCategoryDropdown, (val) => {
  if (val) {
    const handler = (e) => {
      if (!e.target.closest('.filter-dropdown')) {
        showCategoryDropdown.value = false
        document.removeEventListener('click', handler)
      }
    }
    setTimeout(() => document.addEventListener('click', handler), 0)
  }
})
</script>

<style scoped>
/* ============================================
   CSS VARIABLES - Dark Theme with Orange Accent
   ============================================ */
.media-hub {
  --primary: #ff6b00;
  --primary-hover: #ff8533;
  --primary-light: rgba(255, 107, 0, 0.1);
  --primary-glow: rgba(255, 107, 0, 0.3);

  --bg-primary: #0a0a0b;
  --bg-secondary: #111113;
  --bg-tertiary: #1a1a1d;
  --bg-hover: #222225;
  --bg-active: #2a2a2d;

  --border-subtle: #1f1f22;
  --border-default: #2a2a2d;
  --border-hover: #3a3a3d;

  --text-primary: #f5f5f5;
  --text-secondary: #a0a0a5;
  --text-muted: #6a6a70;

  --success: #22c55e;
  --success-light: rgba(34, 197, 94, 0.1);
  --danger: #ef4444;
  --danger-light: rgba(239, 68, 68, 0.1);
  --warning: #f59e0b;
  --warning-light: rgba(245, 158, 11, 0.1);

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
  --shadow-glow: 0 0 20px var(--primary-glow);

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;

  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 400ms ease;

  min-height: 100vh;
  padding-bottom: 40px;
}

/* ============================================
   HEADER
   ============================================ */
.hub-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.header-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  letter-spacing: -0.02em;
}

.header-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ============================================
   BUTTONS
   ============================================ */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--border-hover);
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--danger-light);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  color: var(--danger);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
}

.btn-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-hover);
}

/* ============================================
   TAB NAVIGATION
   ============================================ */
.tab-navigation {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding: 6px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.tab-btn.active {
  background: var(--primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.tab-badge {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.tab-btn.active .tab-badge {
  background: rgba(255, 255, 255, 0.2);
}

/* ============================================
   TOOLBAR
   ============================================ */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* View Toggle */
.view-toggle {
  display: flex;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.toggle-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toggle-btn:hover {
  color: var(--text-secondary);
  background: var(--bg-tertiary);
}

.toggle-btn.active {
  color: var(--primary);
  background: var(--primary-light);
}

/* Filter Dropdown */
.filter-dropdown {
  position: relative;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dropdown-trigger:hover {
  border-color: var(--border-hover);
  background: var(--bg-tertiary);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  min-width: 200px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 100;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dropdown-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.dropdown-item.active {
  background: var(--primary-light);
  color: var(--primary);
}

.item-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
}

/* Bulk Actions */
.bulk-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--primary-light);
  border: 1px solid rgba(255, 107, 0, 0.3);
  border-radius: var(--radius-md);
}

.selected-count {
  font-size: 13px;
  font-weight: 500;
  color: var(--primary);
  margin-right: 4px;
}

.bulk-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.bulk-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.bulk-btn.danger:hover {
  background: var(--danger-light);
  color: var(--danger);
}

/* Search */
.search-wrapper {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 40px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg-tertiary);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
}

.search-clear:hover {
  color: var(--text-primary);
}

/* ============================================
   DROP ZONE OVERLAY
   ============================================ */
.drop-zone-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 11, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.drop-zone-content {
  text-align: center;
  padding: 60px;
  border: 3px dashed var(--primary);
  border-radius: var(--radius-xl);
  background: var(--primary-light);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.02); opacity: 0.9; }
}

.drop-icon {
  color: var(--primary);
  margin-bottom: 16px;
}

.drop-zone-content h3 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.drop-zone-content p {
  color: var(--text-secondary);
  margin: 0;
}

/* ============================================
   IMAGES GRID
   ============================================ */
.media-container {
  min-height: 400px;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.image-card {
  position: relative;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.image-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.image-card.selected {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-light);
}

.card-checkbox {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 10;
}

.checkbox {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 2px solid var(--border-default);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.checkbox:hover {
  border-color: var(--primary);
}

.checkbox.checked {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.checkbox.indeterminate {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.card-image {
  position: relative;
  height: 160px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform var(--transition-slow);
}

.image-card:hover .card-image img {
  transform: scale(1.05);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9) 0%, transparent 50%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 16px;
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.image-card:hover .card-overlay {
  opacity: 1;
}

.overlay-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary);
}

.action-btn.danger:hover {
  background: var(--danger-light);
  border-color: var(--danger);
  color: var(--danger);
}

.card-info {
  padding: 14px;
}

.card-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.category-tag {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-tag.logo { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.category-tag.icon { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.category-tag.banner { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.category-tag.general { background: var(--bg-tertiary); color: var(--text-secondary); }

.file-size {
  font-size: 12px;
  color: var(--text-muted);
}

/* ============================================
   IMAGES LIST
   ============================================ */
.images-list {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 50px 80px 1fr 100px 80px 100px 100px 120px;
  gap: 16px;
  padding: 14px 20px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.list-row {
  display: grid;
  grid-template-columns: 50px 80px 1fr 100px 80px 100px 100px 120px;
  gap: 16px;
  padding: 12px 20px;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle);
  transition: background var(--transition-fast);
}

.list-row:hover {
  background: var(--bg-tertiary);
}

.list-row.selected {
  background: var(--primary-light);
}

.list-thumbnail {
  width: 60px;
  height: 40px;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

.file-name {
  font-weight: 500;
  color: var(--text-primary);
}

.row-actions {
  display: flex;
  gap: 6px;
}

.row-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.row-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.row-btn.danger:hover {
  background: var(--danger-light);
  color: var(--danger);
}

/* ============================================
   EMPTY STATE
   ============================================ */
.empty-state {
  text-align: center;
  padding: 80px 40px;
}

.empty-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 2px dashed var(--border-default);
  border-radius: 50%;
  color: var(--text-muted);
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0 0 24px 0;
}

/* ============================================
   BANNER POSITIONS
   ============================================ */
.banner-positions {
  margin-bottom: 40px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.positions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.position-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.position-card:hover {
  border-color: var(--border-hover);
}

.position-card.has-banner {
  border-color: var(--success);
}

.position-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.position-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.position-icon {
  color: var(--primary);
}

.position-info h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 2px 0;
}

.position-dimensions {
  font-size: 12px;
  color: var(--text-muted);
}

.position-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}

.status-dot.active {
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
}

.status-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.position-preview {
  background: var(--bg-tertiary);
  position: relative;
  min-height: 120px;
  overflow: hidden;
}

.banner-content {
  width: 100%;
  height: 100%;
  position: relative;
}

.banner-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.banner-content:hover .banner-overlay {
  opacity: 1;
}

.preview-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.preview-btn:hover {
  background: var(--primary);
  color: white;
}

.preview-btn.danger:hover {
  background: var(--danger);
}

.empty-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 100%;
  min-height: 120px;
  cursor: pointer;
  color: var(--text-muted);
  transition: all var(--transition-normal);
}

.empty-slot:hover {
  background: var(--primary-light);
  color: var(--primary);
}

.plus-icon {
  transition: transform var(--transition-normal);
}

.empty-slot:hover .plus-icon {
  transform: scale(1.2);
}

.position-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}

.schedule-info,
.link-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

/* ============================================
   BANNERS LIST SECTION
   ============================================ */
.banners-list-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-default);
}

.section-header .section-title {
  margin: 0;
}

.banners-table-wrapper {
  overflow-x: auto;
}

.banners-table {
  width: 100%;
  border-collapse: collapse;
}

.banners-table th {
  padding: 14px 20px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
}

.banners-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

.banners-table tr:hover td {
  background: var(--bg-tertiary);
}

.table-preview {
  width: 100px;
  height: 56px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
}

.table-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-title {
  font-weight: 500;
  color: var(--text-primary);
}

.position-badge {
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-secondary);
}

.date-range {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.no-date {
  color: var(--text-muted);
}

.link-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--primary);
  text-decoration: none;
  font-size: 13px;
}

.link-preview:hover {
  text-decoration: underline;
}

.no-link {
  color: var(--text-muted);
}

.status-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  cursor: pointer;
}

.toggle-track {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  transition: all var(--transition-fast);
}

.status-toggle.active .toggle-track {
  background: var(--success);
  border-color: var(--success);
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.status-toggle.active .toggle-thumb {
  transform: translateX(20px);
}

.toggle-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.status-toggle.active .toggle-label {
  color: var(--success);
}

.table-actions {
  display: flex;
  gap: 6px;
}

.table-btn {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.table-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-hover);
}

.table-btn.danger:hover {
  background: var(--danger-light);
  color: var(--danger);
  border-color: var(--danger);
}

.empty-table {
  padding: 60px 40px;
  text-align: center;
  color: var(--text-muted);
}

.empty-table p {
  margin: 16px 0 24px;
  color: var(--text-secondary);
}

/* ============================================
   MODALS
   ============================================ */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(4px);
}

.modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
}

.upload-modal { max-width: 600px; }
.edit-modal { max-width: 550px; }
.banner-modal { max-width: 650px; }
.picker-modal { max-width: 800px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-default);
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-default);
}

/* Upload Modal */
.upload-dropzone {
  border: 2px dashed var(--border-default);
  border-radius: var(--radius-lg);
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.upload-dropzone:hover,
.upload-dropzone.dragging {
  border-color: var(--primary);
  background: var(--primary-light);
}

.dropzone-icon {
  color: var(--text-muted);
  margin-bottom: 16px;
  transition: color var(--transition-normal);
}

.upload-dropzone:hover .dropzone-icon,
.upload-dropzone.dragging .dropzone-icon {
  color: var(--primary);
}

.dropzone-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.dropzone-content p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.upload-options {
  margin-top: 24px;
}

.option-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-chip:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.category-chip.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.upload-queue {
  margin-top: 24px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 13px;
  color: var(--text-secondary);
}

.clear-queue {
  background: none;
  border: none;
  color: var(--primary);
  font-size: 13px;
  cursor: pointer;
}

.queue-list {
  max-height: 200px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.queue-item:last-child {
  border-bottom: none;
}

.queue-thumbnail {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

.queue-info {
  flex: 1;
  min-width: 0;
}

.queue-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.queue-size {
  font-size: 12px;
  color: var(--text-muted);
}

.queue-progress {
  width: 80px;
  height: 4px;
  background: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  transition: width var(--transition-normal);
}

.queue-remove {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
}

.queue-remove:hover {
  background: var(--danger-light);
  color: var(--danger);
}

/* Preview Modal */
.preview-backdrop {
  background: rgba(0, 0, 0, 0.95);
}

.preview-modal {
  display: flex;
  width: 100%;
  max-width: 1200px;
  height: 80vh;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.preview-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  cursor: pointer;
  z-index: 10;
  transition: all var(--transition-fast);
}

.preview-close:hover {
  background: var(--bg-hover);
}

.preview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-tertiary);
}

.preview-image-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 40px;
}

.preview-image-wrapper img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform var(--transition-normal);
}

.zoom-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-default);
}

.zoom-controls button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.zoom-controls button:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary);
}

.zoom-controls button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.zoom-level {
  min-width: 50px;
  text-align: center;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.preview-sidebar {
  width: 320px;
  padding: 24px;
  border-left: 1px solid var(--border-default);
  overflow-y: auto;
}

.preview-sidebar h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.info-group {
  margin-bottom: 16px;
}

.info-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-group span {
  color: var(--text-primary);
  font-size: 14px;
}

.url-group {
  margin-top: 24px;
}

.url-copy-field {
  display: flex;
  gap: 8px;
}

.url-copy-field input {
  flex: 1;
  padding: 10px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 12px;
}

.url-copy-field button {
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.url-copy-field button:hover {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.preview-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.preview-actions button {
  flex: 1;
}

/* Edit Modal */
.edit-preview {
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}

.edit-preview img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: var(--radius-sm);
}

/* Form Styles */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  transition: all var(--transition-fast);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg-hover);
}

.form-group input::placeholder {
  color: var(--text-muted);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-info {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.form-info .info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

/* Banner Modal Specifics */
.image-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selected-image {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.selected-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  aspect-ratio: 16/9;
  background: var(--bg-tertiary);
  border: 2px dashed var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.image-placeholder:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.image-input-group {
  display: flex;
  gap: 8px;
}

.image-input-group input {
  flex: 1;
}

.browse-btn {
  width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.browse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.link-options {
  display: flex;
  gap: 24px;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-option input {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
}

.switch-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.switch-label span {
  font-size: 14px;
  color: var(--text-primary);
}

.switch {
  position: relative;
  width: 48px;
  height: 26px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.switch.active {
  background: var(--success);
  border-color: var(--success);
}

.switch-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.switch.active .switch-thumb {
  transform: translateX(22px);
}

/* Banner Preview Modal */
.banner-preview-modal {
  max-width: 700px;
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.banner-preview-content {
  padding: 24px;
}

.banner-preview-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.banner-preview-image {
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-bottom: 16px;
}

.banner-preview-image img {
  width: 100%;
  display: block;
}

.banner-preview-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.banner-preview-info .info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.banner-preview-info .info-item a {
  color: var(--primary);
  text-decoration: none;
}

.banner-preview-info .info-item a:hover {
  text-decoration: underline;
}

/* Image Picker Modal */
.picker-search {
  position: relative;
  margin-bottom: 20px;
}

.picker-search svg {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.picker-search input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
}

.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.picker-item {
  position: relative;
  aspect-ratio: 1;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.picker-item:hover {
  border-color: var(--border-hover);
}

.picker-item.selected {
  border-color: var(--primary);
}

.picker-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.picker-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary);
  border-radius: 50%;
  color: white;
}

/* ============================================
   TOAST NOTIFICATIONS
   ============================================ */
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 2000;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  font-size: 14px;
  color: var(--text-primary);
}

.toast.success {
  border-color: var(--success);
  color: var(--success);
}

.toast.error {
  border-color: var(--danger);
  color: var(--danger);
}

/* ============================================
   ANIMATIONS
   ============================================ */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Dropdown */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all var(--transition-fast);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-fast);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Expand */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--transition-normal);
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Modal */
.modal-enter-active,
.modal-leave-active {
  transition: all var(--transition-normal);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal,
.modal-enter-from .preview-modal,
.modal-leave-to .preview-modal,
.modal-enter-from .banner-preview-modal,
.modal-leave-to .banner-preview-modal {
  transform: scale(0.95) translateY(20px);
}

/* Grid */
.grid-enter-active,
.grid-leave-active {
  transition: all var(--transition-normal);
}

.grid-enter-from,
.grid-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.grid-move {
  transition: transform var(--transition-slow);
}

/* List */
.list-enter-active,
.list-leave-active {
  transition: all var(--transition-normal);
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Table */
.table-enter-active,
.table-leave-active {
  transition: all var(--transition-normal);
}

.table-enter-from,
.table-leave-to {
  opacity: 0;
}

/* Queue */
.queue-enter-active,
.queue-leave-active {
  transition: all var(--transition-normal);
}

.queue-enter-from,
.queue-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Toast */
.toast-enter-active,
.toast-leave-active {
  transition: all var(--transition-normal);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .preview-modal {
    flex-direction: column;
    height: auto;
    max-height: 90vh;
  }

  .preview-sidebar {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--border-default);
  }

  .list-header,
  .list-row {
    grid-template-columns: 50px 60px 1fr 80px 80px;
  }

  .dimensions-col,
  .date-col,
  .actions-col {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    justify-content: flex-end;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    justify-content: space-between;
  }

  .search-wrapper {
    width: 100%;
  }

  .tab-navigation {
    flex-direction: column;
  }

  .tab-btn {
    justify-content: center;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .positions-grid {
    grid-template-columns: 1fr;
  }

  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  .images-list {
    display: none;
  }

  .view-toggle {
    display: none;
  }
}
</style>
