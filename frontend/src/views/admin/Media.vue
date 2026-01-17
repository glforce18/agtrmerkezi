<template>
  <AdminLayout>
    <div class="media-management">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Gorsel Yonetimi</h1>
          <p class="page-desc">Site logolari, ikonlar, bannerlar ve diger gorselleri yonetin</p>
        </div>
        <button class="btn-primary" @click="showUploadModal = true">
          <Upload :size="18" />
          Gorsel Yukle
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <div class="action-card" @click="setAsLogo">
          <div class="action-icon logo">
            <ImageIcon :size="24" />
          </div>
          <div class="action-info">
            <h3>Site Logosu</h3>
            <p>{{ currentLogo || 'Belirlenmedi' }}</p>
          </div>
          <button class="action-btn">Degistir</button>
        </div>

        <div class="action-card" @click="setAsFavicon">
          <div class="action-icon favicon">
            <Star :size="24" />
          </div>
          <div class="action-info">
            <h3>Favicon</h3>
            <p>{{ currentFavicon || 'Belirlenmedi' }}</p>
          </div>
          <button class="action-btn">Degistir</button>
        </div>

        <div class="action-card" @click="setAsHeroBanner">
          <div class="action-icon banner">
            <Layout :size="24" />
          </div>
          <div class="action-info">
            <h3>Hero Banner</h3>
            <p>{{ currentHeroBanner || 'Belirlenmedi' }}</p>
          </div>
          <button class="action-btn">Degistir</button>
        </div>
      </div>

      <!-- Category Filter -->
      <div class="filter-bar">
        <div class="filter-tabs">
          <button
            v-for="cat in categories"
            :key="cat.value"
            class="filter-tab"
            :class="{ active: selectedCategory === cat.value }"
            @click="selectedCategory = cat.value"
          >
            {{ cat.label }}
          </button>
        </div>
        <div class="search-box">
          <Search :size="18" />
          <input v-model="searchQuery" placeholder="Gorsel ara..." />
        </div>
      </div>

      <!-- Images Grid -->
      <div class="images-grid">
        <div
          v-for="image in filteredImages"
          :key="image.id"
          class="image-card"
          :class="{ selected: selectedImage?.id === image.id }"
          @click="selectImage(image)"
        >
          <div class="image-preview">
            <img :src="getImageUrl(image)" :alt="image.name" />
            <div class="image-overlay">
              <button class="overlay-btn" @click.stop="copyUrl(image)">
                <Link :size="16" />
              </button>
              <button class="overlay-btn danger" @click.stop="deleteImage(image)">
                <Trash2 :size="16" />
              </button>
            </div>
          </div>
          <div class="image-info">
            <span class="image-name">{{ image.name }}</span>
            <span class="image-size">{{ formatSize(image.file_size) }}</span>
          </div>
          <div class="image-category">
            <span class="category-badge" :class="image.category">
              {{ getCategoryLabel(image.category) }}
            </span>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredImages.length === 0" class="empty-state">
          <ImageIcon :size="48" />
          <p>Gorsel bulunamadi</p>
          <button class="btn-secondary" @click="showUploadModal = true">
            Ilk gorseli yukle
          </button>
        </div>
      </div>

      <!-- Upload Modal -->
      <Teleport to="body">
        <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
          <div class="modal-content upload-modal">
            <div class="modal-header">
              <h3>Gorsel Yukle</h3>
              <button class="close-btn" @click="showUploadModal = false">
                <X :size="20" />
              </button>
            </div>
            <div class="modal-body">
              <!-- Drop Zone -->
              <div
                class="drop-zone"
                :class="{ dragging: isDragging }"
                @dragover.prevent="isDragging = true"
                @dragleave="isDragging = false"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  multiple
                  @change="handleFileSelect"
                  hidden
                />
                <Upload :size="48" class="drop-icon" />
                <p class="drop-text">Gorselleri surukleyip birakin</p>
                <p class="drop-hint">veya tiklayarak secin</p>
              </div>

              <!-- Upload Options -->
              <div class="upload-options">
                <div class="form-group">
                  <label>Kategori</label>
                  <select v-model="uploadCategory">
                    <option value="general">Genel</option>
                    <option value="logo">Logo</option>
                    <option value="icon">Ikon</option>
                    <option value="banner">Banner</option>
                    <option value="mascot">Maskot</option>
                  </select>
                </div>
              </div>

              <!-- Upload Queue -->
              <div v-if="uploadQueue.length > 0" class="upload-queue">
                <div v-for="(file, index) in uploadQueue" :key="index" class="queue-item">
                  <img :src="file.preview" class="queue-preview" />
                  <div class="queue-info">
                    <span class="queue-name">{{ file.name }}</span>
                    <span class="queue-size">{{ formatSize(file.size) }}</span>
                  </div>
                  <div class="queue-progress" v-if="file.uploading">
                    <div class="progress-bar" :style="{ width: file.progress + '%' }"></div>
                  </div>
                  <button v-else class="queue-remove" @click="removeFromQueue(index)">
                    <X :size="16" />
                  </button>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="showUploadModal = false">Iptal</button>
              <button class="btn-primary" @click="uploadFiles" :disabled="uploadQueue.length === 0 || uploading">
                <Loader2 v-if="uploading" :size="18" class="spin" />
                <span v-else>{{ uploadQueue.length }} Gorsel Yukle</span>
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Image Detail Modal -->
      <Teleport to="body">
        <div v-if="selectedImage && showDetailModal" class="modal-overlay" @click.self="showDetailModal = false">
          <div class="modal-content detail-modal">
            <div class="modal-header">
              <h3>Gorsel Detaylari</h3>
              <button class="close-btn" @click="showDetailModal = false">
                <X :size="20" />
              </button>
            </div>
            <div class="modal-body">
              <div class="detail-preview">
                <img :src="getImageUrl(selectedImage)" :alt="selectedImage.name" />
              </div>
              <div class="detail-form">
                <div class="form-group">
                  <label>Gorsel Adi</label>
                  <input v-model="selectedImage.name" />
                </div>
                <div class="form-group">
                  <label>Alt Text (SEO)</label>
                  <input v-model="selectedImage.alt_text" placeholder="Gorsel aciklamasi" />
                </div>
                <div class="form-group">
                  <label>Kategori</label>
                  <select v-model="selectedImage.category">
                    <option value="general">Genel</option>
                    <option value="logo">Logo</option>
                    <option value="icon">Ikon</option>
                    <option value="banner">Banner</option>
                    <option value="mascot">Maskot</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Dosya URL</label>
                  <div class="url-copy">
                    <input :value="getImageUrl(selectedImage)" readonly />
                    <button @click="copyUrl(selectedImage)">
                      <Copy :size="16" />
                    </button>
                  </div>
                </div>
                <div class="detail-meta">
                  <span>Boyut: {{ formatSize(selectedImage.file_size) }}</span>
                  <span>{{ selectedImage.width }}x{{ selectedImage.height }}px</span>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-danger" @click="deleteImage(selectedImage)">
                <Trash2 :size="18" />
                Sil
              </button>
              <button class="btn-primary" @click="updateImage">
                <Save :size="18" />
                Kaydet
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import {
  Upload,
  Search,
  Image as ImageIcon,
  Star,
  Layout,
  Link,
  Trash2,
  X,
  Loader2,
  Copy,
  Save
} from 'lucide-vue-next'

const authStore = useAuthStore()

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authStore.token}`
})

// State
const images = ref([])
const selectedImage = ref(null)
const selectedCategory = ref('all')
const searchQuery = ref('')
const showUploadModal = ref(false)
const showDetailModal = ref(false)
const isDragging = ref(false)
const uploading = ref(false)
const uploadQueue = ref([])
const uploadCategory = ref('general')
const fileInput = ref(null)

// Site settings
const currentLogo = ref('logo-navbar.png')
const currentFavicon = ref('favicon.ico')
const currentHeroBanner = ref('hero-banner.png')

// Categories
const categories = [
  { value: 'all', label: 'Tumu' },
  { value: 'logo', label: 'Logolar' },
  { value: 'icon', label: 'Ikonlar' },
  { value: 'banner', label: 'Bannerlar' },
  { value: 'mascot', label: 'Maskotlar' },
  { value: 'general', label: 'Genel' }
]

// Computed
const filteredImages = computed(() => {
  let result = images.value

  if (selectedCategory.value !== 'all') {
    result = result.filter(img => img.category === selectedCategory.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(img =>
      img.name.toLowerCase().includes(query) ||
      img.alt_text?.toLowerCase().includes(query)
    )
  }

  return result
})

// Methods
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
    console.error('Fetch images error:', e)
    // Use static images as fallback
    images.value = [
      { id: 1, name: 'agtr-logo-main', file_path: '/static/images/logos/agtr-logo-main.png', category: 'logo', file_size: 1302574 },
      { id: 2, name: 'agtr-logo-alt', file_path: '/static/images/logos/agtr-logo-alt.png', category: 'logo', file_size: 1244335 },
      { id: 3, name: 'agtr-badge', file_path: '/static/images/icons/agtr-badge.png', category: 'icon', file_size: 2663961 },
      { id: 4, name: 'ct-icon', file_path: '/static/images/icons/ct-icon.png', category: 'icon', file_size: 1613324 },
      { id: 5, name: 'hero-banner', file_path: '/static/images/banners/hero-banner.png', category: 'banner', file_size: 2815763 },
      { id: 6, name: 'gordon-orange', file_path: '/static/images/mascots/gordon-orange.png', category: 'mascot', file_size: 2423004 },
      { id: 7, name: 'gordon-green', file_path: '/static/images/mascots/gordon-green.png', category: 'mascot', file_size: 1763943 },
      { id: 8, name: 'logo-navbar', file_path: '/logo-navbar.png', category: 'logo', file_size: 14870 },
      { id: 9, name: 'favicon', file_path: '/favicon.ico', category: 'icon', file_size: 32038 }
    ]
  }
}

const getImageUrl = (image) => {
  if (image.file_path.startsWith('http')) return image.file_path
  if (image.file_path.startsWith('/')) return image.file_path
  return '/' + image.file_path
}

const getCategoryLabel = (category) => {
  const cat = categories.find(c => c.value === category)
  return cat?.label || category
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const selectImage = (image) => {
  selectedImage.value = { ...image }
  showDetailModal.value = true
}

const copyUrl = (image) => {
  const url = window.location.origin + getImageUrl(image)
  navigator.clipboard.writeText(url)
  alert('URL kopyalandi!')
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addToQueue(files)
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  addToQueue(files)
}

const addToQueue = (files) => {
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadQueue.value.push({
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
      console.error('Upload error:', e)
    }
  }

  uploading.value = false
  showUploadModal.value = false
  uploadQueue.value = []
  fetchImages()
}

const updateImage = async () => {
  try {
    const response = await fetch(`/api/admin/media/${selectedImage.value.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(selectedImage.value)
    })

    if (response.ok) {
      showDetailModal.value = false
      fetchImages()
    }
  } catch (e) {
    console.error('Update error:', e)
  }
}

const deleteImage = async (image) => {
  if (!confirm(`"${image.name}" gorselini silmek istediginize emin misiniz?`)) return

  try {
    const response = await fetch(`/api/admin/media/${image.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })

    if (response.ok) {
      showDetailModal.value = false
      fetchImages()
    }
  } catch (e) {
    console.error('Delete error:', e)
  }
}

const setAsLogo = () => {
  // Open image selector for logo
}

const setAsFavicon = () => {
  // Open image selector for favicon
}

const setAsHeroBanner = () => {
  // Open image selector for hero banner
}

onMounted(() => {
  fetchImages()
})
</script>

<style scoped>
.media-management {
  max-width: 1400px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 10px;
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 0, 0.3);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #ef4444;
  font-weight: 500;
  cursor: pointer;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon.logo { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.action-icon.favicon { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.action-icon.banner { background: rgba(16, 185, 129, 0.1); color: #10b981; }

.action-info {
  flex: 1;
}

.action-info h3 {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.action-info p {
  font-size: 13px;
  color: var(--text-secondary);
}

.action-btn {
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--bg-primary);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.search-box input {
  background: none;
  border: none;
  color: var(--text-primary);
  outline: none;
  width: 200px;
}

/* Images Grid */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.image-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.image-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.image-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(255, 107, 0, 0.2);
}

.image-preview {
  position: relative;
  height: 150px;
  background: var(--bg-tertiary);
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.overlay-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.overlay-btn.danger {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.image-info {
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.image-category {
  padding: 0 12px 12px;
}

.category-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.category-badge.logo { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.category-badge.icon { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.category-badge.banner { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.category-badge.mascot { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.category-badge.general { background: var(--bg-tertiary); color: var(--text-secondary); }

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-state p {
  margin: 16px 0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid var(--border-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

/* Drop Zone */
.drop-zone {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.drop-zone:hover,
.drop-zone.dragging {
  border-color: var(--primary-color);
  background: rgba(255, 107, 0, 0.05);
}

.drop-icon {
  color: var(--text-muted);
  margin-bottom: 16px;
}

.drop-text {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.drop-hint {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Upload Options */
.upload-options {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 16px;
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
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
}

/* Upload Queue */
.upload-queue {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.queue-preview {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
}

.queue-info {
  flex: 1;
}

.queue-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 13px;
}

.queue-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.queue-progress {
  width: 100px;
  height: 4px;
  background: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s;
}

.queue-remove {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

/* Detail Modal */
.detail-modal {
  max-width: 700px;
}

.detail-preview {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}

.detail-preview img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

.url-copy {
  display: flex;
  gap: 8px;
}

.url-copy input {
  flex: 1;
}

.url-copy button {
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
}

.detail-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 16px;
}

/* Animations */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .quick-actions {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .filter-tabs {
    flex-wrap: wrap;
  }

  .search-box {
    width: 100%;
  }

  .search-box input {
    width: 100%;
  }
}
</style>
