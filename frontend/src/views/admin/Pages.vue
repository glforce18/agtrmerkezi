<template>
  <AdminLayout>
    <div class="pages-management">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Sayfa İçerikleri</h1>
          <p class="page-desc">Site sayfalarinin içeriklerini düzenleyin</p>
        </div>
        <button class="btn-primary" @click="showAddModal = true">
          <Plus :size="18" />
          Yeni İçerik Ekle
        </button>
      </div>

      <!-- Pages List -->
      <div class="pages-grid">
        <div
          v-for="page in pages"
          :key="page.id"
          class="page-card"
          @click="editPage(page)"
        >
          <div class="page-icon" :class="page.icon_class">
            <component :is="getIcon(page.icon)" :size="24" />
          </div>
          <div class="page-info">
            <h3>{{ page.title }}</h3>
            <p>{{ page.page_slug }} / {{ page.section_slug }}</p>
          </div>
          <div class="page-status">
            <span class="status-badge" :class="{ active: page.is_active }">
              {{ page.is_active ? 'Aktif' : 'Pasif' }}
            </span>
          </div>
          <button class="edit-btn">
            <Edit :size="16" />
          </button>
        </div>
      </div>

      <!-- Add/Edit Modal -->
      <Teleport to="body">
        <div v-if="showAddModal || editingPage" class="modal-overlay" @click.self="closeModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>{{ editingPage ? 'İçerik Düzenle' : 'Yeni İçerik Ekle' }}</h3>
              <button class="close-btn" @click="closeModal">
                <X :size="20" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-row">
                <div class="form-group">
                  <label>Sayfa</label>
                  <select v-model="formData.page_slug">
                    <option value="home">Ana Sayfa</option>
                    <option value="about">Hakkında</option>
                    <option value="contact">İletişim</option>
                    <option value="servers">Sunucular</option>
                    <option value="jackpot">Jackpot</option>
                    <option value="forum">Forum</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Bolum</label>
                  <select v-model="formData.section_slug">
                    <option value="hero">Hero</option>
                    <option value="features">Özellikler</option>
                    <option value="cta">CTA</option>
                    <option value="stats">İstatistikler</option>
                    <option value="testimonials">Yorumlar</option>
                    <option value="footer">Footer</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Başlık</label>
                <input v-model="formData.title" placeholder="İçerik basligi" />
              </div>

              <div class="form-group">
                <label>Alt Başlık</label>
                <input v-model="formData.subtitle" placeholder="Alt başlık (opsiyonel)" />
              </div>

              <div class="form-group">
                <label>İçerik</label>
                <textarea v-model="formData.content" rows="6" placeholder="HTML veya Markdown içerik"></textarea>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Görsel URL</label>
                  <input v-model="formData.image_url" placeholder="/images/..." />
                </div>
                <div class="form-group">
                  <label>Arkaplan Görsel</label>
                  <input v-model="formData.background_image_url" placeholder="/images/..." />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>CTA Buton Metni</label>
                  <input v-model="formData.cta_text" placeholder="Hemen Başla" />
                </div>
                <div class="form-group">
                  <label>CTA Link</label>
                  <input v-model="formData.cta_link" placeholder="/register" />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Sıra</label>
                  <input v-model.number="formData.display_order" type="number" />
                </div>
                <div class="form-group">
                  <label>Durum</label>
                  <select v-model="formData.is_active">
                    <option :value="true">Aktif</option>
                    <option :value="false">Pasif</option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="closeModal">İptal</button>
              <button class="btn-primary" @click="savePage">
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
import {
  Plus,
  Edit,
  X,
  Save,
  Home,
  Server,
  MessageSquare,
  Trophy,
  ShoppingBag,
  Info
} from 'lucide-vue-next'

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

const pages = ref([])
const loading = ref(false)

const fetchPages = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/pages', {
      headers: getHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      pages.value = data.pages || []
    }
  } catch (e) {
    // Error handled
  }
  loading.value = false
}

const showAddModal = ref(false)
const editingPage = ref(null)
const formData = reactive({
  page_slug: 'home',
  section_slug: 'hero',
  title: '',
  subtitle: '',
  content: '',
  image_url: '',
  background_image_url: '',
  cta_text: '',
  cta_link: '',
  display_order: 0,
  is_active: true
})

const getIcon = (iconName) => {
  const icons = { Home, Server, MessageSquare, Trophy, ShoppingBag, Info }
  return icons[iconName] || Info
}

const editPage = (page) => {
  editingPage.value = page
  Object.assign(formData, page)
}

const closeModal = () => {
  showAddModal.value = false
  editingPage.value = null
  Object.assign(formData, {
    page_slug: 'home',
    section_slug: 'hero',
    title: '',
    subtitle: '',
    content: '',
    image_url: '',
    background_image_url: '',
    cta_text: '',
    cta_link: '',
    display_order: 0,
    is_active: true
  })
}

const savePage = async () => {
  try {
    const method = editingPage.value ? 'PUT' : 'POST'
    const url = editingPage.value
      ? `/api/admin/pages/${editingPage.value.id}`
      : '/api/admin/pages'

    const response = await fetch(url, {
      method,
      headers: getHeaders(),
      body: JSON.stringify(formData)
    })

    if (response.ok) {
      closeModal()
      fetchPages()
    }
  } catch (e) {
    // Error handled
  }
}

onMounted(() => {
  fetchPages()
})
</script>

<style scoped>
.pages-management {
  max-width: 1200px;
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

.pages-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-card {
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

.page-card:hover {
  border-color: var(--primary-color);
}

.page-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 107, 0, 0.1);
  color: var(--primary-color);
}

.page-info {
  flex: 1;
}

.page-info h3 {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.page-info p {
  font-size: 13px;
  color: var(--text-secondary);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.edit-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Modal styles same as Media.vue */
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
  max-width: 700px;
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
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
  font-family: monospace;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
</style>
