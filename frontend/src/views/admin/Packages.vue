<template>
  <AdminLayout>
    <div class="admin-packages">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Paket Yönetimi</h1>
          <p class="subtitle">Sunucu paketleri ve fiyatlandırma</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="openCreateModal">
            <Plus :size="18" />
            <span>Yeni Paket</span>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Paket ara..."
            @input="filterPackages"
          />
        </div>
        <select v-model="filterGame" class="filter-select" @change="filterPackages">
          <option value="">Tüm Oyunlar</option>
          <option value="hldm">Half-Life</option>
          <option value="ag">Half-Life AG</option>
          <option value="cs16">Counter-Strike 1.6</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="filterPackages">
          <option value="">Tüm Durumlar</option>
          <option value="active">Aktif</option>
          <option value="inactive">Pasif</option>
        </select>
      </div>

      <!-- Packages Grid -->
      <div v-if="loading" class="loading-state">
        <Loader2 :size="32" class="spin" />
        <span>Yükleniyor...</span>
      </div>

      <div v-else class="packages-grid">
        <div
          v-for="pkg in filteredPackages"
          :key="pkg.id"
          class="package-card"
          :class="{ inactive: !pkg.is_active, featured: pkg.is_featured }"
        >
          <div class="package-header">
            <span class="game-badge" :class="pkg.game_type">
              {{ getGameLabel(pkg.game_type) }}
            </span>
            <div class="package-actions">
              <button class="btn-icon" @click="editPackage(pkg)" title="Düzenle">
                <Edit2 :size="16" />
              </button>
              <button class="btn-icon danger" @click="deletePackage(pkg)" title="Sil">
                <Trash2 :size="16" />
              </button>
            </div>
          </div>

          <h3 class="package-name">{{ pkg.name }}</h3>
          <p class="package-desc">{{ pkg.description }}</p>

          <div class="package-features">
            <div class="feature">
              <Users :size="16" />
              <span>{{ pkg.slots }} Slot</span>
            </div>
            <div class="feature">
              <HardDrive :size="16" />
              <span>{{ pkg.ram }} MB RAM</span>
            </div>
            <div class="feature">
              <Cpu :size="16" />
              <span>{{ pkg.cpu }}% CPU</span>
            </div>
            <div class="feature">
              <Database :size="16" />
              <span>{{ pkg.disk }} GB Disk</span>
            </div>
          </div>

          <div class="package-price">
            <span class="price">{{ pkg.price }} ₺</span>
            <span class="period">/ {{ getDurationLabel(pkg.duration) }}</span>
          </div>

          <div class="package-footer">
            <span class="sales-count">
              <ShoppingCart :size="14" />
              {{ pkg.sales_count || 0 }} satış
            </span>
            <label class="toggle">
              <input
                type="checkbox"
                :checked="pkg.is_active"
                @change="togglePackage(pkg)"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div v-if="filteredPackages.length === 0" class="empty-state">
          <Package :size="48" />
          <p>Paket bulunamadı</p>
        </div>
      </div>

      <!-- Create/Edit Modal -->
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h3>{{ editingPackage ? 'Paketi Düzenle' : 'Yeni Paket' }}</h3>
            <button class="btn-icon" @click="closeModal">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label>Paket Adı *</label>
                <input v-model="form.name" type="text" placeholder="Örn: Starter Paket" />
              </div>
              <div class="form-group">
                <label>Oyun *</label>
                <select v-model="form.game_type">
                  <option value="hldm">Half-Life</option>
                  <option value="ag">Half-Life AG</option>
                  <option value="cs16">Counter-Strike 1.6</option>
                </select>
              </div>
              <div class="form-group full">
                <label>Açıklama</label>
                <textarea v-model="form.description" rows="2" placeholder="Paket açıklaması..."></textarea>
              </div>
              <div class="form-group">
                <label>Slot Sayısı *</label>
                <input v-model.number="form.slots" type="number" min="1" />
              </div>
              <div class="form-group">
                <label>RAM (MB) *</label>
                <input v-model.number="form.ram" type="number" min="128" step="64" />
              </div>
              <div class="form-group">
                <label>CPU (%) *</label>
                <input v-model.number="form.cpu" type="number" min="10" max="100" />
              </div>
              <div class="form-group">
                <label>Disk (GB) *</label>
                <input v-model.number="form.disk" type="number" min="1" />
              </div>
              <div class="form-group">
                <label>Fiyat (₺) *</label>
                <input v-model.number="form.price" type="number" min="0" step="0.01" />
              </div>
              <div class="form-group">
                <label>Süre *</label>
                <select v-model="form.duration">
                  <option value="monthly">Aylık</option>
                  <option value="quarterly">3 Aylık</option>
                  <option value="yearly">Yıllık</option>
                </select>
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="form.is_featured" />
                  <span>Öne Çıkan Paket</span>
                </label>
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="form.is_active" />
                  <span>Aktif</span>
                </label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">İptal</button>
            <button class="btn btn-primary" @click="savePackage" :disabled="saving">
              <Loader2 v-if="saving" :size="16" class="spin" />
              <span>{{ editingPackage ? 'Güncelle' : 'Oluştur' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import {
  Search,
  Plus,
  Edit2,
  Trash2,
  Users,
  HardDrive,
  Cpu,
  Database,
  ShoppingCart,
  Package,
  Loader2,
  X
} from 'lucide-vue-next'

const loading = ref(false)
const saving = ref(false)
const packages = ref([])
const searchQuery = ref('')
const filterGame = ref('')
const filterStatus = ref('')

const showModal = ref(false)
const editingPackage = ref(null)
const form = reactive({
  name: '',
  game_type: 'hldm',
  description: '',
  slots: 12,
  ram: 512,
  cpu: 50,
  disk: 5,
  price: 0,
  duration: 'monthly',
  is_featured: false,
  is_active: true
})

const filteredPackages = computed(() => {
  return packages.value.filter(pkg => {
    const matchSearch = !searchQuery.value ||
      pkg.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchGame = !filterGame.value || pkg.game_type === filterGame.value
    const matchStatus = !filterStatus.value ||
      (filterStatus.value === 'active' ? pkg.is_active : !pkg.is_active)
    return matchSearch && matchGame && matchStatus
  })
})

const fetchPackages = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/packages')
    if (response.ok) {
      const data = await response.json()
      packages.value = data.packages || []
    }
  } catch (error) {
    // Fetch error - will show empty state
  }
  loading.value = false
}

const filterPackages = () => {
  // Computed handles filtering
}

const getGameLabel = (game) => {
  const labels = {
    hldm: 'Half-Life',
    ag: 'Half-Life AG',
    cs16: 'CS 1.6'
  }
  return labels[game] || game
}

const getDurationLabel = (duration) => {
  const labels = {
    monthly: 'ay',
    quarterly: '3 ay',
    yearly: 'yıl'
  }
  return labels[duration] || duration
}

const openCreateModal = () => {
  editingPackage.value = null
  Object.assign(form, {
    name: '',
    game_type: 'hldm',
    description: '',
    slots: 12,
    ram: 512,
    cpu: 50,
    disk: 5,
    price: 0,
    duration: 'monthly',
    is_featured: false,
    is_active: true
  })
  showModal.value = true
}

const editPackage = (pkg) => {
  editingPackage.value = pkg
  Object.assign(form, { ...pkg })
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPackage.value = null
}

const savePackage = async () => {
  if (!form.name || !form.price) {
    alert('Lütfen zorunlu alanları doldurun')
    return
  }

  saving.value = true
  try {
    const url = editingPackage.value
      ? `/api/admin/packages/${editingPackage.value.id}`
      : '/api/admin/packages'

    const response = await fetch(url, {
      method: editingPackage.value ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })

    if (response.ok) {
      await fetchPackages()
      closeModal()
    } else {
      const data = await response.json()
      alert(data.detail || 'Kaydetme başarısız')
    }
  } catch (error) {
    alert('Bir hata oluştu')
  }
  saving.value = false
}

const deletePackage = async (pkg) => {
  if (!confirm(`${pkg.name} paketini silmek istediğinize emin misiniz?`)) return

  try {
    const response = await fetch(`/api/admin/packages/${pkg.id}`, { method: 'DELETE' })
    if (response.ok) {
      packages.value = packages.value.filter(p => p.id !== pkg.id)
    }
  } catch (error) {
    // Delete error - package remains in list
  }
}

const togglePackage = async (pkg) => {
  try {
    const response = await fetch(`/api/admin/packages/${pkg.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !pkg.is_active })
    })

    if (response.ok) {
      pkg.is_active = !pkg.is_active
    }
  } catch (error) {
    // Toggle error - state unchanged
  }
}

onMounted(() => {
  fetchPackages()
})
</script>

<style scoped>
.admin-packages {
  max-width: 1400px;
  margin: 0 auto;
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
}

/* Buttons */
.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: var(--primary-color);
  color: var(--bg-primary);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn:hover {
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Filters */
.filters-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
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
  font-size: 14px;
}

.search-box input::placeholder {
  color: var(--text-muted);
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
  font-size: 14px;
  cursor: pointer;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-secondary);
  gap: 12px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Packages Grid */
.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.package-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
}

.package-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.package-card.featured {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.package-card.inactive {
  opacity: 0.6;
}

.package-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.game-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.game-badge.hldm {
  background: rgba(255, 107, 0, 0.15);
  color: #ff6b00;
}

.game-badge.ag {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.game-badge.cs16 {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.package-actions {
  display: flex;
  gap: 6px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

.btn-icon.danger:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.package-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.package-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  line-height: 1.5;
}

.package-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.feature svg {
  color: var(--primary-color);
}

.package-price {
  text-align: center;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  margin-bottom: 16px;
}

.price {
  font-size: 28px;
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
}

.sales-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--bg-tertiary);
  border-radius: 24px;
  transition: 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  left: 3px;
  bottom: 3px;
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
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-state svg {
  opacity: 0.5;
  margin-bottom: 12px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
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
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-lg {
  max-width: 600px;
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

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
}

.checkbox-group {
  justify-content: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .packages-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    min-width: 100%;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
