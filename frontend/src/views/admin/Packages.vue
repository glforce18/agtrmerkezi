<template>
  <AdminLayout>
    <div class="admin-packages">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h1>Paket Yönetimi</h1>
          <p class="subtitle">Sunucu paketlerini düzenle</p>
        </div>
        <button class="btn-primary" @click="openCreateModal">
          <Plus :size="18" />
          Yeni Paket
        </button>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" />
          <input v-model="searchQuery" type="text" placeholder="Paket ara..." />
        </div>
        <select v-model="filterGame" class="filter-select">
          <option value="">Tüm Oyunlar</option>
          <option value="hldm">Half-Life</option>
          <option value="ag">Adrenaline Gamer</option>
          <option value="cs16">Counter-Strike 1.6</option>
        </select>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <Loader2 :size="32" class="spin" />
        <span>Yükleniyor...</span>
      </div>

      <!-- Packages Grid -->
      <div v-else class="packages-grid">
        <div
          v-for="pkg in filteredPackages"
          :key="pkg.id"
          class="package-card"
          :class="{ inactive: !pkg.is_active }"
        >
          <div class="package-header">
            <span class="game-badge" :class="pkg.game_type">{{ getGameLabel(pkg.game_type) }}</span>
            <div class="package-actions">
              <button class="btn-icon" @click="editPackage(pkg)" title="Düzenle">
                <Edit2 :size="16" />
              </button>
              <button class="btn-icon danger" @click="confirmDelete(pkg)" title="Sil">
                <Trash2 :size="16" />
              </button>
            </div>
          </div>

          <h3 class="package-name">{{ pkg.name }}</h3>
          <p class="package-desc">{{ pkg.description || 'Açıklama yok' }}</p>

          <div class="package-specs">
            <div class="spec">
              <Users :size="16" />
              <span>{{ pkg.slots }} Slot</span>
            </div>
          </div>

          <div class="package-features" v-if="pkg.features && pkg.features.length">
            <span v-for="feature in pkg.features.slice(0, 4)" :key="feature" class="feature-tag">
              {{ getFeatureLabel(feature) }}
            </span>
            <span v-if="pkg.features.length > 4" class="feature-more">+{{ pkg.features.length - 4 }}</span>
          </div>

          <div class="package-price">
            <span class="price">{{ pkg.price_monthly }} TL</span>
            <span class="period">/ ay</span>
          </div>

          <div class="package-footer">
            <span class="order-badge">Sıra: {{ pkg.display_order }}</span>
            <label class="toggle">
              <input type="checkbox" :checked="pkg.is_active" @change="toggleActive(pkg)" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div v-if="filteredPackages.length === 0" class="empty-state">
          <Package :size="48" />
          <p>Paket bulunamadı</p>
        </div>
      </div>

      <!-- Modal -->
      <Teleport to="body">
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal">
            <div class="modal-header">
              <h3>{{ editingPackage ? 'Paketi Düzenle' : 'Yeni Paket' }}</h3>
              <button class="close-btn" @click="closeModal">
                <X :size="20" />
              </button>
            </div>

            <div class="modal-body">
              <div class="form-row">
                <div class="form-group">
                  <label>Paket Adı *</label>
                  <input v-model="form.name" type="text" placeholder="Half-Life AG Pro" />
                </div>
                <div class="form-group">
                  <label>Slug *</label>
                  <input v-model="form.slug" type="text" placeholder="halflife_ag_pro" />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Oyun Tipi *</label>
                  <select v-model="form.game_type">
                    <option value="hldm">Half-Life Deathmatch</option>
                    <option value="ag">Adrenaline Gamer</option>
                    <option value="cs16">Counter-Strike 1.6</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Slot Sayısı *</label>
                  <input v-model.number="form.slots" type="number" min="8" max="64" />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Aylık Fiyat (TL) *</label>
                  <input v-model.number="form.price_monthly" type="number" min="0" step="0.01" />
                </div>
                <div class="form-group">
                  <label>Görüntüleme Sırası</label>
                  <input v-model.number="form.display_order" type="number" min="0" />
                </div>
              </div>

              <div class="form-group">
                <label>Açıklama</label>
                <textarea v-model="form.description" rows="2" placeholder="Paket açıklaması..."></textarea>
              </div>

              <div class="form-group">
                <label>Özellikler</label>
                <div class="features-grid">
                  <label v-for="feature in availableFeatures" :key="feature.value" class="feature-checkbox">
                    <input
                      type="checkbox"
                      :checked="form.features.includes(feature.value)"
                      @change="toggleFeature(feature.value)"
                    />
                    <span>{{ feature.label }}</span>
                  </label>
                </div>
              </div>

              <div class="form-row">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="form.is_active" />
                  <span>Aktif</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="form.is_popular" />
                  <span>Popüler</span>
                </label>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn-secondary" @click="closeModal">İptal</button>
              <button class="btn-primary" @click="savePackage" :disabled="saving">
                <Loader2 v-if="saving" :size="18" class="spin" />
                <span v-else>{{ editingPackage ? 'Güncelle' : 'Oluştur' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import {
  Plus, Search, Edit2, Trash2, Users, Package, X, Loader2
} from 'lucide-vue-next'

const authStore = useAuthStore()

const packages = ref([])
const loading = ref(true)
const searchQuery = ref('')
const filterGame = ref('')
const showModal = ref(false)
const editingPackage = ref(null)
const saving = ref(false)

const form = reactive({
  name: '',
  slug: '',
  game_type: 'ag',
  slots: 32,
  features: [],
  description: '',
  price_monthly: 100,
  is_active: true,
  is_popular: false,
  display_order: 0
})

const availableFeatures = [
  { value: 'ddos_protection', label: 'DDoS Koruma' },
  { value: 'rcon_access', label: 'RCON Erişimi' },
  { value: 'basic_plugins', label: 'Temel Pluginler' },
  { value: 'fun_plugins', label: 'Fun Pluginler' },
  { value: 'zombie_mod', label: 'Zombie Mod' },
  { value: 'anticheat', label: 'Anti-Cheat' },
  { value: 'amvp', label: 'AMVP' },
  { value: 'statsme', label: 'StatsMe' },
  { value: '247_support', label: '7/24 Destek' },
  { value: 'auto_backup', label: 'Otomatik Yedekleme' },
  { value: 'custom_domain', label: 'Özel Domain' },
  { value: 'priority_support', label: 'Öncelikli Destek' }
]

const filteredPackages = computed(() => {
  return packages.value.filter(pkg => {
    const matchesSearch = !searchQuery.value ||
      pkg.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesGame = !filterGame.value || pkg.game_type === filterGame.value
    return matchesSearch && matchesGame
  })
})

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

const fetchPackages = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/admin/packages', { headers: getHeaders() })
    if (res.ok) {
      const data = await res.json()
      packages.value = data.packages || data || []
    }
  } catch (e) {
    console.error('Fetch error:', e)
  }
  loading.value = false
}

const getGameLabel = (type) => {
  const labels = { hldm: 'Half-Life', ag: 'AG', cs16: 'CS 1.6' }
  return labels[type] || type
}

const getFeatureLabel = (feature) => {
  const found = availableFeatures.find(f => f.value === feature)
  return found ? found.label : feature
}

const toggleFeature = (feature) => {
  const idx = form.features.indexOf(feature)
  if (idx > -1) {
    form.features.splice(idx, 1)
  } else {
    form.features.push(feature)
  }
}

const openCreateModal = () => {
  editingPackage.value = null
  Object.assign(form, {
    name: '', slug: '', game_type: 'ag', slots: 32,
    features: [], description: '', price_monthly: 100,
    is_active: true, is_popular: false, display_order: 0
  })
  showModal.value = true
}

const editPackage = (pkg) => {
  editingPackage.value = pkg
  Object.assign(form, {
    name: pkg.name,
    slug: pkg.slug,
    game_type: pkg.game_type,
    slots: pkg.slots,
    features: pkg.features ? [...pkg.features] : [],
    description: pkg.description || '',
    price_monthly: pkg.price_monthly,
    is_active: pkg.is_active,
    is_popular: pkg.is_popular || false,
    display_order: pkg.display_order || 0
  })
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPackage.value = null
}

const savePackage = async () => {
  if (!form.name || !form.slug || !form.price_monthly) {
    alert('Lütfen zorunlu alanları doldurun')
    return
  }

  saving.value = true
  try {
    const url = editingPackage.value
      ? `/api/admin/packages/${editingPackage.value.id}`
      : '/api/admin/packages'

    const res = await fetch(url, {
      method: editingPackage.value ? 'PUT' : 'POST',
      headers: getHeaders(),
      body: JSON.stringify(form)
    })

    if (res.ok) {
      await fetchPackages()
      closeModal()
    } else {
      const data = await res.json()
      alert(data.detail || 'Kaydetme başarısız')
    }
  } catch (e) {
    alert('Bir hata oluştu')
  }
  saving.value = false
}

const confirmDelete = async (pkg) => {
  if (!confirm(`"${pkg.name}" paketini silmek istediğinize emin misiniz?`)) return

  try {
    const res = await fetch(`/api/admin/packages/${pkg.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (res.ok) {
      packages.value = packages.value.filter(p => p.id !== pkg.id)
    } else {
      const data = await res.json()
      alert(data.detail || 'Silme başarısız')
    }
  } catch (e) {
    alert('Bir hata oluştu')
  }
}

const toggleActive = async (pkg) => {
  try {
    const res = await fetch(`/api/admin/packages/${pkg.id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ ...pkg, is_active: !pkg.is_active })
    })
    if (res.ok) {
      pkg.is_active = !pkg.is_active
    }
  } catch (e) {
    console.error('Toggle error:', e)
  }
}

onMounted(fetchPackages)
</script>

<style scoped>
.admin-packages {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.subtitle {
  color: var(--text-secondary);
  margin: 4px 0 0;
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
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.filters-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0 14px;
}

.search-box input {
  flex: 1;
  background: none;
  border: none;
  padding: 12px 0;
  color: var(--text-primary);
}

.search-box svg {
  color: var(--text-muted);
}

.filter-select {
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px;
  color: var(--text-secondary);
  gap: 12px;
}

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.package-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s;
}

.package-card:hover {
  border-color: var(--primary-color);
}

.package-card.inactive {
  opacity: 0.6;
}

.package-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.game-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.game-badge.hldm { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.game-badge.ag { background: rgba(249, 115, 22, 0.15); color: #f97316; }
.game-badge.cs16 { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }

.package-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover { color: var(--primary-color); }
.btn-icon.danger:hover { color: #ef4444; }

.package-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.package-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.package-specs {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.spec {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.package-features {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.feature-tag {
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-secondary);
}

.feature-more {
  padding: 4px 8px;
  background: var(--primary-color);
  color: white;
  border-radius: 6px;
  font-size: 11px;
}

.package-price {
  margin-bottom: 16px;
}

.price {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

.period {
  font-size: 14px;
  color: var(--text-secondary);
}

.package-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.order-badge {
  font-size: 12px;
  color: var(--text-muted);
}

.toggle {
  position: relative;
  width: 44px;
  height: 24px;
}

.toggle input { display: none; }

.toggle-slider {
  position: absolute;
  inset: 0;
  background: var(--bg-tertiary);
  border-radius: 12px;
  cursor: pointer;
  transition: 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}

.toggle input:checked + .toggle-slider {
  background: var(--primary-color);
}

.toggle input:checked + .toggle-slider::before {
  transform: translateX(20px);
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
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

.modal {
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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.feature-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
}

.feature-checkbox input:checked + span {
  color: var(--primary-color);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

.btn-secondary {
  padding: 12px 24px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  cursor: pointer;
}

.modal-footer .btn-primary {
  min-width: 120px;
  justify-content: center;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
