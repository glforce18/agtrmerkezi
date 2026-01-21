<template>
  <AdminLayout>
    <div class="banners-management">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Banner Yonetimi</h1>
          <p class="page-desc">Site bannerlarini ve reklamlari yonetin</p>
        </div>
        <button class="btn-primary" @click="showAddModal = true">
          <Plus :size="18" />
          Yeni Banner
        </button>
      </div>

      <!-- Banner Locations -->
      <div class="locations-grid">
        <div
          v-for="location in bannerLocations"
          :key="location.id"
          class="location-card"
        >
          <div class="location-header">
            <h3>{{ location.name }}</h3>
            <span class="location-size">{{ location.size }}</span>
          </div>
          <div class="location-preview" :class="location.class">
            <div v-if="getBannerByLocation(location.id)" class="banner-preview">
              <img :src="getBannerByLocation(location.id).image_url" />
              <div class="banner-overlay">
                <button class="overlay-btn" @click="editBanner(getBannerByLocation(location.id))">
                  <Edit :size="16" />
                </button>
                <button class="overlay-btn danger" @click="removeBanner(getBannerByLocation(location.id))">
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>
            <div v-else class="empty-slot" @click="addBannerToLocation(location.id)">
              <Plus :size="24" />
              <span>Banner Ekle</span>
            </div>
          </div>
          <div class="location-info">
            <span v-if="getBannerByLocation(location.id)" class="status active">Aktif</span>
            <span v-else class="status">Bos</span>
          </div>
        </div>
      </div>

      <!-- All Banners -->
      <div class="all-banners">
        <h2>Tum Bannerlar</h2>
        <div class="banners-table">
          <table>
            <thead>
              <tr>
                <th>Onizleme</th>
                <th>Baslik</th>
                <th>Konum</th>
                <th>Link</th>
                <th>Durum</th>
                <th>Islemler</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="banner in banners" :key="banner.id">
                <td>
                  <img :src="banner.image_url" class="table-preview" />
                </td>
                <td>{{ banner.title }}</td>
                <td>{{ getLocationName(banner.location) }}</td>
                <td class="link-cell">{{ banner.link || '-' }}</td>
                <td>
                  <span class="status-badge" :class="{ active: banner.is_active }">
                    {{ banner.is_active ? 'Aktif' : 'Pasif' }}
                  </span>
                </td>
                <td>
                  <div class="action-btns">
                    <button @click="editBanner(banner)"><Edit :size="16" /></button>
                    <button class="danger" @click="removeBanner(banner)"><Trash2 :size="16" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Add/Edit Modal -->
      <Teleport to="body">
        <div v-if="showAddModal || editingBanner" class="modal-overlay" @click.self="closeModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>{{ editingBanner ? 'Banner Duzenle' : 'Yeni Banner' }}</h3>
              <button class="close-btn" @click="closeModal">
                <X :size="20" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Baslik</label>
                <input v-model="formData.title" placeholder="Banner basligi" />
              </div>

              <div class="form-group">
                <label>Gorsel URL</label>
                <div class="image-input">
                  <input v-model="formData.image_url" placeholder="/images/banners/..." />
                  <button class="browse-btn" @click="openMediaPicker">
                    <Image :size="16" />
                  </button>
                </div>
              </div>

              <div v-if="formData.image_url" class="preview-box">
                <img :src="formData.image_url" />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Konum</label>
                  <select v-model="formData.location">
                    <option v-for="loc in bannerLocations" :key="loc.id" :value="loc.id">
                      {{ loc.name }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Link (opsiyonel)</label>
                  <input v-model="formData.link" placeholder="https://..." />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Baslangic Tarihi</label>
                  <input type="datetime-local" v-model="formData.start_date" />
                </div>
                <div class="form-group">
                  <label>Bitis Tarihi</label>
                  <input type="datetime-local" v-model="formData.end_date" />
                </div>
              </div>

              <div class="form-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.is_active" />
                  Aktif
                </label>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="closeModal">Iptal</button>
              <button class="btn-primary" @click="saveBanner">
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
import { ref, reactive, onMounted } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { Plus, Edit, Trash2, X, Save, Image } from 'lucide-vue-next'

const authStore = useAuthStore()

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

const bannerLocations = [
  { id: 'hero', name: 'Ana Sayfa Hero', size: '1920x600', class: 'hero' },
  { id: 'sidebar', name: 'Sidebar', size: '300x250', class: 'sidebar' },
  { id: 'footer', name: 'Footer Banner', size: '728x90', class: 'footer' },
  { id: 'popup', name: 'Popup', size: '600x400', class: 'popup' }
]

const banners = ref([
  {
    id: 1,
    title: 'Hero Banner',
    image_url: '/static/images/banners/hero-banner.png',
    location: 'hero',
    link: '',
    is_active: true
  }
])

const showAddModal = ref(false)
const editingBanner = ref(null)
const selectedLocation = ref(null)
const formData = reactive({
  title: '',
  image_url: '',
  location: 'hero',
  link: '',
  start_date: '',
  end_date: '',
  is_active: true
})

const getBannerByLocation = (locationId) => {
  return banners.value.find(b => b.location === locationId && b.is_active)
}

const getLocationName = (locationId) => {
  return bannerLocations.find(l => l.id === locationId)?.name || locationId
}

const addBannerToLocation = (locationId) => {
  selectedLocation.value = locationId
  formData.location = locationId
  showAddModal.value = true
}

const editBanner = (banner) => {
  editingBanner.value = banner
  Object.assign(formData, banner)
}

const closeModal = () => {
  showAddModal.value = false
  editingBanner.value = null
  selectedLocation.value = null
  Object.assign(formData, {
    title: '',
    image_url: '',
    location: 'hero',
    link: '',
    start_date: '',
    end_date: '',
    is_active: true
  })
}

const openMediaPicker = () => {
  // Open media picker modal
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
      body: JSON.stringify(formData)
    })

    if (response.ok) {
      closeModal()
      fetchBanners()
    }
  } catch (e) {
    // Error handled
  }
}

const removeBanner = async (banner) => {
  if (!confirm('Bu banneri silmek istediginize emin misiniz?')) return

  try {
    const response = await fetch(`/api/admin/banners/${banner.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (response.ok) {
      banners.value = banners.value.filter(b => b.id !== banner.id)
    }
  } catch (e) {
    // Error handled
  }
}

onMounted(() => {
  fetchBanners()
})
</script>

<style scoped>
.banners-management {
  max-width: 1400px;
}

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
}

.btn-secondary {
  padding: 12px 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  cursor: pointer;
}

/* Locations Grid */
.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.location-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.location-header h3 {
  font-weight: 600;
  color: var(--text-primary);
}

.location-size {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 4px 8px;
  border-radius: 4px;
}

.location-preview {
  height: 150px;
  background: var(--bg-tertiary);
  position: relative;
}

.location-preview.hero { height: 120px; }
.location-preview.sidebar { height: 200px; }
.location-preview.footer { height: 80px; }
.location-preview.popup { height: 160px; }

.banner-preview {
  width: 100%;
  height: 100%;
  position: relative;
}

.banner-preview img {
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
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.banner-preview:hover .banner-overlay {
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

.empty-slot {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.empty-slot:hover {
  color: var(--primary-color);
  background: rgba(255, 107, 0, 0.05);
}

.location-info {
  padding: 12px 16px;
  display: flex;
  justify-content: flex-end;
}

.status {
  font-size: 12px;
  color: var(--text-secondary);
}

.status.active {
  color: #10b981;
}

/* All Banners */
.all-banners {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.all-banners h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.banners-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

th {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}

td {
  color: var(--text-primary);
}

.table-preview {
  width: 80px;
  height: 45px;
  object-fit: cover;
  border-radius: 4px;
}

.link-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.action-btns {
  display: flex;
  gap: 8px;
}

.action-btns button {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: var(--bg-tertiary);
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btns button.danger {
  color: #ef4444;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.image-input {
  display: flex;
  gap: 8px;
}

.image-input input {
  flex: 1;
}

.browse-btn {
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
}

.preview-box {
  margin-bottom: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  text-align: center;
}

.preview-box img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
}
</style>
