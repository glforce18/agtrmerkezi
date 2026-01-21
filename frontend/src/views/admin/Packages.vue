<template>
  <AdminLayout>
    <div class="admin-packages">
      <!-- Header Section -->
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">
            <Package :size="28" class="title-icon" />
            Paket Yönetimi
          </h1>
          <p class="subtitle">Sunucu paketlerini yönet ve fiyatlandırmayı düzenle</p>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" @click="togglePreviewMode">
            <Eye v-if="!previewMode" :size="18" />
            <EyeOff v-else :size="18" />
            {{ previewMode ? 'Düzenle' : 'Onizleme' }}
          </button>
          <button class="btn-primary" @click="openCreateModal">
            <Plus :size="18" />
            Yeni Paket
          </button>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon packages">
            <Package :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ packages.length }}</span>
            <span class="stat-label">Toplam Paket</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <Zap :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ activePackagesCount }}</span>
            <span class="stat-label">Aktif Paket</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon sales">
            <ShoppingCart :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ totalSales }}</span>
            <span class="stat-label">Toplam Satış</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon revenue">
            <TrendingUp :size="24" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ formatCurrency(totalRevenue) }}</span>
            <span class="stat-label">Toplam Gelir</span>
          </div>
        </div>
      </div>

      <!-- Filters Bar -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Paket ara..."
            @input="debouncedSearch"
          />
          <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''">
            <X :size="14" />
          </button>
        </div>
        <div class="filter-group">
          <select v-model="filterGame" class="filter-select">
            <option value="">Tüm Oyunlar</option>
            <option value="hldm">Half-Life</option>
            <option value="ag">Adrenaline Gamer</option>
            <option value="cs16">Counter-Strike 1.6</option>
          </select>
          <select v-model="filterStatus" class="filter-select">
            <option value="">Tüm Durumlar</option>
            <option value="active">Aktif</option>
            <option value="inactive">Pasif</option>
          </select>
          <select v-model="sortBy" class="filter-select">
            <option value="display_order">Sıralama</option>
            <option value="price_asc">Fiyat (Artan)</option>
            <option value="price_desc">Fiyat (Azalan)</option>
            <option value="name">Ada Gore</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">
          <Loader2 :size="40" class="spin" />
        </div>
        <span>Paketler yükleniyor...</span>
      </div>

      <!-- Preview Mode - User View -->
      <div v-else-if="previewMode" class="preview-mode">
        <div class="preview-header">
          <Monitor :size="20" />
          <span>Kullanıcı Görünümu Onizlemesi</span>
        </div>
        <div class="preview-container">
          <div class="priçing-grid">
            <div
              v-for="(pkg, index) in sortedPackages"
              :key="pkg.id"
              class="priçing-card"
              :class="{
                popular: pkg.is_popular,
                inactive: !pkg.is_active
              }"
              :style="{ animationDelay: `${index * 0.1}s` }"
            >
              <!-- Discount Badge -->
              <div v-if="pkg.discount_percent" class="discount-badge">
                <Percent :size="14" />
                {{ pkg.discount_percent }}% INDIRIM
              </div>

              <!-- Popular Badge -->
              <div v-if="pkg.is_popular" class="popular-badge">
                <Star :size="14" />
                POPULER
              </div>

              <div class="priçing-header">
                <span class="game-tag" :class="pkg.game_type">
                  {{ getGameLabel(pkg.game_type) }}
                </span>
                <h3 class="priçing-name">{{ pkg.name }}</h3>
                <p class="priçing-desc">{{ pkg.description || 'Profesyonel oyun sunucusu paketi' }}</p>
              </div>

              <div class="priçing-price">
                <span v-if="pkg.discount_percent" class="original-price">
                  {{ pkg.price_monthly }} TL
                </span>
                <div class="current-price">
                  <span class="amount">{{ getDiscountedPrice(pkg) }}</span>
                  <span class="currency">TL</span>
                  <span class="period">/ ay</span>
                </div>
              </div>

              <div class="priçing-specs">
                <div class="spec-item">
                  <Users :size="16" />
                  <span>{{ pkg.slots }} Oyuncu Slotu</span>
                </div>
                <div class="spec-item">
                  <Shield :size="16" />
                  <span>DDoS Koruma</span>
                </div>
              </div>

              <div class="priçing-features">
                <div
                  v-for="feature in (pkg.features || []).slice(0, 6)"
                  :key="feature"
                  class="feature-item"
                >
                  <Check :size="16" class="check-icon" />
                  <span>{{ getFeatureLabel(feature) }}</span>
                </div>
                <div v-if="(pkg.features || []).length > 6" class="feature-more">
                  +{{ pkg.features.length - 6 }} özellik daha
                </div>
              </div>

              <button class="priçing-btn" :class="{ popular: pkg.is_popular }">
                <ShoppingCart :size="18" />
                Satın Al
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Edit Mode - Draggable Cards -->
      <div v-else class="packages-section">
        <div
          class="packages-grid"
          @dragover.prevent
          @drop="onDrop"
        >
          <TransitionGroup name="package-list">
            <div
              v-for="(pkg, index) in sortedPackages"
              :key="pkg.id"
              class="package-card"
              :class="{
                inactive: !pkg.is_active,
                dragging: draggedPackage?.id === pkg.id,
                'drag-over': dragOverPackage?.id === pkg.id
              }"
              :style="{ animationDelay: `${index * 0.05}s` }"
              draggable="true"
              @dragstart="onDragStart($event, pkg)"
              @dragenter="onDragEnter($event, pkg)"
              @dragleave="onDragLeave"
              @dragend="onDragEnd"
            >
              <!-- Drag Handle -->
              <div class="drag-handle">
                <GripVertical :size="16" />
              </div>

              <!-- Card Header -->
              <div class="card-header">
                <div class="header-left">
                  <span class="game-badge" :class="pkg.game_type">
                    {{ getGameLabel(pkg.game_type) }}
                  </span>
                  <span v-if="pkg.is_popular" class="popular-tag">
                    <Star :size="12" />
                    Popüler
                  </span>
                  <span v-if="pkg.discount_percent" class="discount-tag">
                    -{{ pkg.discount_percent }}%
                  </span>
                </div>
                <div class="header-right">
                  <label class="toggle-switch" @click.stop>
                    <input
                      type="checkbox"
                      :checked="pkg.is_active"
                      @change="toggleActive(pkg)"
                    />
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <!-- Package Info -->
              <div class="package-info">
                <h3 class="package-name">{{ pkg.name }}</h3>
                <p class="package-desc">{{ pkg.description || 'Açıklama yok' }}</p>
              </div>

              <!-- Package Specs -->
              <div class="package-specs">
                <div class="spec">
                  <Users :size="16" />
                  <span>{{ pkg.slots }} Slot</span>
                </div>
                <div class="spec">
                  <Layers :size="16" />
                  <span>Sira: {{ pkg.display_order }}</span>
                </div>
              </div>

              <!-- Features Preview -->
              <div class="features-preview" v-if="pkg.features && pkg.features.length">
                <div class="features-list">
                  <span
                    v-for="feature in pkg.features.slice(0, 3)"
                    :key="feature"
                    class="feature-tag"
                  >
                    <Check :size="10" />
                    {{ getFeatureLabel(feature) }}
                  </span>
                  <span v-if="pkg.features.length > 3" class="feature-count">
                    +{{ pkg.features.length - 3 }}
                  </span>
                </div>
              </div>

              <!-- Price Section -->
              <div class="price-section">
                <div class="price-display">
                  <span v-if="pkg.discount_percent" class="old-price">
                    {{ pkg.price_monthly }} TL
                  </span>
                  <span class="current-price">
                    {{ getDiscountedPrice(pkg) }} TL
                  </span>
                  <span class="price-period">/ ay</span>
                </div>
              </div>

              <!-- Stats Row -->
              <div class="stats-row">
                <div class="mini-stat">
                  <ShoppingCart :size="14" />
                  <span>{{ pkg.total_sales || 0 }} satış</span>
                </div>
                <div class="mini-stat">
                  <TrendingUp :size="14" />
                  <span>{{ formatCurrency(pkg.total_revenue || 0) }}</span>
                </div>
              </div>

              <!-- Card Actions -->
              <div class="card-actions">
                <button class="action-btn preview" @click="previewPackage(pkg)" title="Onizle">
                  <Eye :size="16" />
                </button>
                <button class="action-btn edit" @click="editPackage(pkg)" title="Düzenle">
                  <Edit2 :size="16" />
                </button>
                <button class="action-btn duplicate" @click="duplicatePackage(pkg)" title="Kopyala">
                  <Copy :size="16" />
                </button>
                <button class="action-btn delete" @click="confirmDelete(pkg)" title="Sil">
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>
          </TransitionGroup>

          <!-- Empty State -->
          <div v-if="sortedPackages.length === 0" class="empty-state">
            <div class="empty-icon">
              <Package :size="64" />
            </div>
            <h3>Paket Bulunamadı</h3>
            <p>Arama kriterlerinize uygun paket yok veya henüz paket oluşturmadiniz.</p>
            <button class="btn-primary" @click="openCreateModal">
              <Plus :size="18" />
              İlk Paketinizi Oluştürün
            </button>
          </div>
        </div>
      </div>

      <!-- Edit/Create Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal" :class="{ 'with-preview': showInlinePreview }">
              <!-- Modal Header -->
              <div class="modal-header">
                <div class="modal-title">
                  <component :is="editingPackage ? Edit2 : Plus" :size="20" />
                  <h3>{{ editingPackage ? 'Paketi Düzenle' : 'Yeni Paket Oluştur' }}</h3>
                </div>
                <div class="modal-header-actions">
                  <button
                    class="preview-toggle"
                    :class="{ active: showInlinePreview }"
                    @click="showInlinePreview = !showInlinePreview"
                  >
                    <Eye :size="16" />
                    Onizleme
                  </button>
                  <button class="close-btn" @click="closeModal">
                    <X :size="20" />
                  </button>
                </div>
              </div>

              <div class="modal-content">
                <!-- Form Section -->
                <div class="modal-body">
                  <!-- Basic Info -->
                  <div class="form-section">
                    <h4 class="section-title">
                      <Info :size="16" />
                      Temel Bilgiler
                    </h4>
                    <div class="form-grid">
                      <div class="form-group">
                        <label>Paket Adi *</label>
                        <input
                          v-model="form.name"
                          type="text"
                          placeholder="Half-Life AG Pro"
                          @input="autoGenerateSlug"
                        />
                      </div>
                      <div class="form-group">
                        <label>Slug *</label>
                        <input
                          v-model="form.slug"
                          type="text"
                          placeholder="halflife_ag_pro"
                        />
                      </div>
                      <div class="form-group">
                        <label>Oyun Tipi *</label>
                        <select v-model="form.game_type">
                          <option value="hldm">Half-Life Deathmatch</option>
                          <option value="ag">Adrenaline Gamer</option>
                          <option value="cs16">Counter-Strike 1.6</option>
                        </select>
                      </div>
                      <div class="form-group">
                        <label>Slot Sayisi *</label>
                        <input
                          v-model.number="form.slots"
                          type="number"
                          min="8"
                          max="64"
                        />
                      </div>
                    </div>
                    <div class="form-group full">
                      <label>Açıklama</label>
                      <textarea
                        v-model="form.description"
                        rows="2"
                        placeholder="Bu paket profesyonel oyuncular için tasarlandi..."
                      ></textarea>
                    </div>
                  </div>

                  <!-- Priçing -->
                  <div class="form-section">
                    <h4 class="section-title">
                      <DollarSign :size="16" />
                      Fiyatlandirma
                    </h4>
                    <div class="form-grid">
                      <div class="form-group">
                        <label>Aylık Fiyat (TL) *</label>
                        <div class="input-with-icon">
                          <input
                            v-model.number="form.price_monthly"
                            type="number"
                            min="0"
                            step="0.01"
                          />
                          <span class="input-suffix">TL</span>
                        </div>
                      </div>
                      <div class="form-group">
                        <label>İndirim Orani (%)</label>
                        <div class="input-with-icon">
                          <input
                            v-model.number="form.discount_percent"
                            type="number"
                            min="0"
                            max="100"
                          />
                          <span class="input-suffix">%</span>
                        </div>
                      </div>
                      <div class="form-group">
                        <label>Görüntüleme Sirasi</label>
                        <input
                          v-model.number="form.display_order"
                          type="number"
                          min="0"
                        />
                      </div>
                    </div>
                    <div v-if="form.discount_percent > 0" class="discount-preview">
                      <Tag :size="16" />
                      <span>İndirimli Fiyat: <strong>{{ getDiscountedPrice(form) }} TL</strong></span>
                    </div>
                  </div>

                  <!-- Features -->
                  <div class="form-section">
                    <h4 class="section-title">
                      <ListChecks :size="16" />
                      Özellikler
                    </h4>
                    <div class="features-grid">
                      <label
                        v-for="feature in availableFeatures"
                        :key="feature.value"
                        class="feature-checkbox"
                        :class="{ selected: form.features.includes(feature.value) }"
                      >
                        <input
                          type="checkbox"
                          :checked="form.features.includes(feature.value)"
                          @change="toggleFeature(feature.value)"
                        />
                        <div class="checkbox-custom">
                          <Check v-if="form.features.includes(feature.value)" :size="12" />
                        </div>
                        <span>{{ feature.label }}</span>
                      </label>
                    </div>
                  </div>

                  <!-- Status Options -->
                  <div class="form-section">
                    <h4 class="section-title">
                      <Settings :size="16" />
                      Durum ve Görünüm
                    </h4>
                    <div class="status-options">
                      <label class="status-checkbox" :class="{ active: form.is_active }">
                        <input type="checkbox" v-model="form.is_active" />
                        <div class="status-icon">
                          <Power :size="16" />
                        </div>
                        <div class="status-text">
                          <span class="status-label">Aktif</span>
                          <span class="status-desc">Kullanıcılara göster</span>
                        </div>
                      </label>
                      <label class="status-checkbox" :class="{ active: form.is_popular }">
                        <input type="checkbox" v-model="form.is_popular" />
                        <div class="status-icon popular">
                          <Star :size="16" />
                        </div>
                        <div class="status-text">
                          <span class="status-label">Popüler</span>
                          <span class="status-desc">Özel rozetle vurgula</span>
                        </div>
                      </label>
                    </div>
                  </div>
                </div>

                <!-- Inline Preview -->
                <div v-if="showInlinePreview" class="inline-preview">
                  <div class="preview-label">Canli Onizleme</div>
                  <div class="preview-card-wrapper">
                    <div class="priçing-card preview-card" :class="{ popular: form.is_popular }">
                      <div v-if="form.discount_percent" class="discount-badge">
                        <Percent :size="14" />
                        {{ form.discount_percent }}% INDIRIM
                      </div>
                      <div v-if="form.is_popular" class="popular-badge">
                        <Star :size="14" />
                        POPULER
                      </div>
                      <div class="priçing-header">
                        <span class="game-tag" :class="form.game_type">
                          {{ getGameLabel(form.game_type) }}
                        </span>
                        <h3 class="priçing-name">{{ form.name || 'Paket Adi' }}</h3>
                        <p class="priçing-desc">{{ form.description || 'Paket açıklamasi' }}</p>
                      </div>
                      <div class="priçing-price">
                        <span v-if="form.discount_percent" class="original-price">
                          {{ form.price_monthly }} TL
                        </span>
                        <div class="current-price">
                          <span class="amount">{{ getDiscountedPrice(form) }}</span>
                          <span class="currency">TL</span>
                          <span class="period">/ ay</span>
                        </div>
                      </div>
                      <div class="priçing-specs">
                        <div class="spec-item">
                          <Users :size="16" />
                          <span>{{ form.slots }} Oyuncu Slotu</span>
                        </div>
                      </div>
                      <div class="priçing-features">
                        <div
                          v-for="feature in form.features.slice(0, 4)"
                          :key="feature"
                          class="feature-item"
                        >
                          <Check :size="16" class="check-icon" />
                          <span>{{ getFeatureLabel(feature) }}</span>
                        </div>
                      </div>
                      <button class="priçing-btn" :class="{ popular: form.is_popular }">
                        <ShoppingCart :size="18" />
                        Satın Al
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Modal Footer -->
              <div class="modal-footer">
                <button class="btn-secondary" @click="closeModal">
                  <X :size="16" />
                  İptal
                </button>
                <button class="btn-primary" @click="savePackage" :disabled="saving">
                  <Loader2 v-if="saving" :size="18" class="spin" />
                  <Save v-else :size="18" />
                  <span>{{ editingPackage ? 'Güncelle' : 'Oluştur' }}</span>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Single Package Preview Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showPreviewModal" class="modal-overlay preview-modal-overlay" @click.self="showPreviewModal = false">
            <div class="preview-modal">
              <button class="preview-close" @click="showPreviewModal = false">
                <X :size="24" />
              </button>
              <div class="preview-modal-content">
                <div class="priçing-card preview-full" :class="{ popular: previewingPackage?.is_popular }">
                  <div v-if="previewingPackage?.discount_percent" class="discount-badge">
                    <Percent :size="14" />
                    {{ previewingPackage.discount_percent }}% INDIRIM
                  </div>
                  <div v-if="previewingPackage?.is_popular" class="popular-badge">
                    <Star :size="14" />
                    POPULER
                  </div>
                  <div class="priçing-header">
                    <span class="game-tag" :class="previewingPackage?.game_type">
                      {{ getGameLabel(previewingPackage?.game_type) }}
                    </span>
                    <h3 class="priçing-name">{{ previewingPackage?.name }}</h3>
                    <p class="priçing-desc">{{ previewingPackage?.description || 'Profesyonel oyun sunucusu paketi' }}</p>
                  </div>
                  <div class="priçing-price">
                    <span v-if="previewingPackage?.discount_percent" class="original-price">
                      {{ previewingPackage?.price_monthly }} TL
                    </span>
                    <div class="current-price">
                      <span class="amount">{{ getDiscountedPrice(previewingPackage) }}</span>
                      <span class="currency">TL</span>
                      <span class="period">/ ay</span>
                    </div>
                  </div>
                  <div class="priçing-specs">
                    <div class="spec-item">
                      <Users :size="16" />
                      <span>{{ previewingPackage?.slots }} Oyuncu Slotu</span>
                    </div>
                    <div class="spec-item">
                      <Shield :size="16" />
                      <span>DDoS Koruma</span>
                    </div>
                  </div>
                  <div class="priçing-features">
                    <div
                      v-for="feature in (previewingPackage?.features || [])"
                      :key="feature"
                      class="feature-item"
                    >
                      <Check :size="16" class="check-icon" />
                      <span>{{ getFeatureLabel(feature) }}</span>
                    </div>
                  </div>
                  <button class="priçing-btn" :class="{ popular: previewingPackage?.is_popular }">
                    <ShoppingCart :size="18" />
                    Satın Al
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Delete Confirmation -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
            <div class="confirm-modal">
              <div class="confirm-icon">
                <AlertTriangle :size="48" />
              </div>
              <h3>Paketi Sil</h3>
              <p>"<strong>{{ deletingPackage?.name }}</strong>" paketini silmek istediğinize emin misiniz?</p>
              <p class="warning-text">Bu işlem geri alınamaz!</p>
              <div class="confirm-actions">
                <button class="btn-secondary" @click="showDeleteModal = false">
                  İptal
                </button>
                <button class="btn-danger" @click="deletePackage" :disabled="deleting">
                  <Loader2 v-if="deleting" :size="16" class="spin" />
                  <Trash2 v-else :size="16" />
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
          </div>
        </TransitionGroup>
      </Teleport>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import {
  Plus, Search, Edit2, Trash2, Users, Package, X, Loader2,
  Eye, EyeOff, Star, Check, ShoppingCart, TrendingUp, Zap,
  GripVertical, Copy, Layers, Shield, Percent, Monitor,
  Info, DollarSign, ListChecks, Settings, Power, Tag, Save,
  AlertTriangle, CheckCircle, XCircle, AlertCircle
} from 'lucide-vue-next'

const authStore = useAuthStore()

// State
const packages = ref([])
const loading = ref(true)
const searchQuery = ref('')
const filterGame = ref('')
const filterStatus = ref('')
const sortBy = ref('display_order')
const showModal = ref(false)
const editingPackage = ref(null)
const saving = ref(false)
const previewMode = ref(false)
const showInlinePreview = ref(false)
const showPreviewModal = ref(false)
const previewingPackage = ref(null)
const showDeleteModal = ref(false)
const deletingPackage = ref(null)
const deleting = ref(false)
const toasts = ref([])

// Drag and drop state
const draggedPackage = ref(null)
const dragOverPackage = ref(null)

// Form state
const form = reactive({
  name: '',
  slug: '',
  game_type: 'ag',
  slots: 32,
  features: [],
  description: '',
  price_monthly: 100,
  discount_percent: 0,
  is_active: true,
  is_popular: false,
  display_order: 0
})

// Available features
const availableFeatures = [
  { value: 'ddos_protection', label: 'DDoS Koruma' },
  { value: 'rcon_access', label: 'RCON Erisimi' },
  { value: 'basic_plugins', label: 'Temel Pluginler' },
  { value: 'fun_plugins', label: 'Fun Pluginler' },
  { value: 'zombie_mod', label: 'Zombie Mod' },
  { value: 'anticheat', label: 'Anti-Cheat' },
  { value: 'amvp', label: 'AMVP' },
  { value: 'statsme', label: 'StatsMe' },
  { value: '247_support', label: '7/24 Destek' },
  { value: 'auto_backup', label: 'Otomatik Yedekleme' },
  { value: 'custom_domain', label: 'Özel Domain' },
  { value: 'priority_support', label: 'Oncelikli Destek' }
]

// Computed properties
const activePackagesCount = computed(() =>
  packages.value.filter(p => p.is_active).length
)

const totalSales = computed(() =>
  packages.value.reduce((sum, p) => sum + (p.total_sales || 0), 0)
)

const totalRevenue = computed(() =>
  packages.value.reduce((sum, p) => sum + (p.total_revenue || 0), 0)
)

const filteredPackages = computed(() => {
  return packages.value.filter(pkg => {
    const matchesSearch = !searchQuery.value ||
      pkg.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (pkg.description && pkg.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
    const matchesGame = !filterGame.value || pkg.game_type === filterGame.value
    const matchesStatus = !filterStatus.value ||
      (filterStatus.value === 'active' && pkg.is_active) ||
      (filterStatus.value === 'inactive' && !pkg.is_active)
    return matchesSearch && matchesGame && matchesStatus
  })
})

const sortedPackages = computed(() => {
  const sorted = [...filteredPackages.value]
  switch (sortBy.value) {
    case 'price_asc':
      return sorted.sort((a, b) => a.price_monthly - b.price_monthly)
    case 'price_desc':
      return sorted.sort((a, b) => b.price_monthly - a.price_monthly)
    case 'name':
      return sorted.sort((a, b) => a.name.localeCompare(b.name))
    default:
      return sorted.sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
  }
})

// Utility functions
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

const formatCurrency = (value) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const getGameLabel = (type) => {
  const labels = { hldm: 'Half-Life', ag: 'AG', cs16: 'CS 1.6' }
  return labels[type] || type
}

const getFeatureLabel = (feature) => {
  const found = availableFeatures.find(f => f.value === feature)
  return found ? found.label : feature
}

const getDiscountedPrice = (pkg) => {
  if (!pkg) return 0
  if (pkg.discount_percent && pkg.discount_percent > 0) {
    return Math.round(pkg.price_monthly * (1 - pkg.discount_percent / 100))
  }
  return pkg.price_monthly
}

const getToastIcon = (type) => {
  switch (type) {
    case 'success': return CheckCircle
    case 'error': return XCircle
    case 'warning': return AlertCircle
    default: return AlertCircle
  }
}

// Toast notifications
const showToast = (message, type = 'success') => {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

// API functions
const fetchPackages = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/admin/packages', { headers: getHeaders() })
    if (res.ok) {
      const data = await res.json()
      packages.value = data.packages || data || []
    }
  } catch (e) {
    // Error handled
    showToast('Paketler yüklenirken hata oluştu', 'error')
  }
  loading.value = false
}

const toggleFeature = (feature) => {
  const idx = form.features.indexOf(feature)
  if (idx > -1) {
    form.features.splice(idx, 1)
  } else {
    form.features.push(feature)
  }
}

const autoGenerateSlug = () => {
  if (!editingPackage.value) {
    form.slug = form.name
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '_')
      .replace(/-+/g, '_')
  }
}

const togglePreviewMode = () => {
  previewMode.value = !previewMode.value
}

const openCreateModal = () => {
  editingPackage.value = null
  Object.assign(form, {
    name: '', slug: '', game_type: 'ag', slots: 32,
    features: [], description: '', price_monthly: 100,
    discount_percent: 0, is_active: true, is_popular: false,
    display_order: packages.value.length
  })
  showInlinePreview.value = false
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
    discount_percent: pkg.discount_percent || 0,
    is_active: pkg.is_active,
    is_popular: pkg.is_popular || false,
    display_order: pkg.display_order || 0
  })
  showInlinePreview.value = false
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPackage.value = null
}

const savePackage = async () => {
  if (!form.name || !form.slug || !form.price_monthly) {
    showToast('Lütfen zorunlu alanlari doldürün', 'warning')
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
      showToast(editingPackage.value ? 'Paket güncellendi' : 'Paket oluşturuldu', 'success')
    } else {
      const data = await res.json()
      showToast(data.detail || 'Kaydetme başarısız', 'error')
    }
  } catch (e) {
    showToast('Bir hata oluştu', 'error')
  }
  saving.value = false
}

const confirmDelete = (pkg) => {
  deletingPackage.value = pkg
  showDeleteModal.value = true
}

const deletePackage = async () => {
  if (!deletingPackage.value) return

  deleting.value = true
  try {
    const res = await fetch(`/api/admin/packages/${deletingPackage.value.id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (res.ok) {
      packages.value = packages.value.filter(p => p.id !== deletingPackage.value.id)
      showDeleteModal.value = false
      deletingPackage.value = null
      showToast('Paket silindi', 'success')
    } else {
      const data = await res.json()
      showToast(data.detail || 'Silme başarısız', 'error')
    }
  } catch (e) {
    showToast('Bir hata oluştu', 'error')
  }
  deleting.value = false
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
      showToast(pkg.is_active ? 'Paket aktifleştirildi' : 'Paket pasif yapıldı', 'success')
    }
  } catch (e) {
    // Error handled
    showToast('Durum degistirilemedi', 'error')
  }
}

const duplicatePackage = (pkg) => {
  editingPackage.value = null
  Object.assign(form, {
    name: `${pkg.name} (Kopya)`,
    slug: `${pkg.slug}_copy`,
    game_type: pkg.game_type,
    slots: pkg.slots,
    features: pkg.features ? [...pkg.features] : [],
    description: pkg.description || '',
    price_monthly: pkg.price_monthly,
    discount_percent: pkg.discount_percent || 0,
    is_active: false,
    is_popular: false,
    display_order: packages.value.length
  })
  showModal.value = true
}

const previewPackage = (pkg) => {
  previewingPackage.value = pkg
  showPreviewModal.value = true
}

// Drag and drop handlers
const onDragStart = (event, pkg) => {
  draggedPackage.value = pkg
  event.dataTransfer.effectAllowed = 'move'
}

const onDragEnter = (event, pkg) => {
  if (draggedPackage.value && draggedPackage.value.id !== pkg.id) {
    dragOverPackage.value = pkg
  }
}

const onDragLeave = () => {
  dragOverPackage.value = null
}

const onDragEnd = () => {
  draggedPackage.value = null
  dragOverPackage.value = null
}

const onDrop = async () => {
  if (!draggedPackage.value || !dragOverPackage.value) return
  if (draggedPackage.value.id === dragOverPackage.value.id) return

  const draggedIndex = packages.value.findIndex(p => p.id === draggedPackage.value.id)
  const dropIndex = packages.value.findIndex(p => p.id === dragOverPackage.value.id)

  if (draggedIndex > -1 && dropIndex > -1) {
    // Reorder locally
    const [removed] = packages.value.splice(draggedIndex, 1)
    packages.value.splice(dropIndex, 0, removed)

    // Update display_order for all packages
    const updates = packages.value.map((pkg, index) => ({
      id: pkg.id,
      display_order: index
    }))

    // Update on server
    try {
      for (const update of updates) {
        const pkg = packages.value.find(p => p.id === update.id)
        if (pkg && pkg.display_order !== update.display_order) {
          pkg.display_order = update.display_order
          await fetch(`/api/admin/packages/${update.id}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify({ ...pkg, display_order: update.display_order })
          })
        }
      }
      showToast('Sıralama güncellendi', 'success')
    } catch (e) {
      // Error handled
      showToast('Sıralama güncellenemedi', 'error')
    }
  }

  draggedPackage.value = null
  dragOverPackage.value = null
}

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // Search is handled by computed property
  }, 300)
}

onMounted(fetchPackages)
</script>

<style scoped>
/* Base Variables */
.admin-packages {
  --card-bg: rgba(30, 30, 35, 0.8);
  --card-border: rgba(255, 255, 255, 0.08);
  --card-hover-border: rgba(249, 115, 22, 0.4);
  --text-primary: #ffffff;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;
  --accent-orange: #f97316;
  --accent-orange-light: #fb923c;
  --accent-green: #22c55e;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --accent-red: #ef4444;
  --bg-dark: #18181b;
  --bg-darker: #0f0f12;

  max-width: 1400px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 20px;
  flex-wrap: wrap;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.title-icon {
  color: var(--accent-orange);
}

.subtitle {
  color: var(--text-secondary);
  margin: 8px 0 0;
  font-size: 15px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Buttons */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--accent-orange) 0%, #ea580c 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  border-color: var(--accent-orange);
  color: var(--accent-orange);
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--accent-red) 0%, #dc2626 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: var(--card-hover-border);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.packages {
  background: rgba(249, 115, 22, 0.15);
  color: var(--accent-orange);
}

.stat-icon.active {
  background: rgba(34, 197, 94, 0.15);
  color: var(--accent-green);
}

.stat-icon.sales {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-blue);
}

.stat-icon.revenue {
  background: rgba(139, 92, 246, 0.15);
  color: var(--accent-purple);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* Filters Bar */
.filters-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 280px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 0 16px;
  transition: all 0.3s ease;
}

.search-box:focus-within {
  border-color: var(--accent-orange);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.search-box svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-box input {
  flex: 1;
  background: none;
  border: none;
  padding: 14px 0;
  color: var(--text-primary);
  font-size: 14px;
}

.search-box input::placeholder {
  color: var(--text-muted);
}

.search-box input:focus {
  outline: none;
}

.clear-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 14px 16px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 150px;
}

.filter-select:hover {
  border-color: var(--card-hover-border);
}

.filter-select:focus {
  outline: none;
  border-color: var(--accent-orange);
}

.filter-select option {
  background: var(--bg-dark);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-secondary);
  gap: 16px;
}

.loading-spinner {
  color: var(--accent-orange);
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
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

/* Package Card */
.package-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 24px;
  position: relative;
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease backwards;
  cursor: grab;
}

.package-card:hover {
  border-color: var(--card-hover-border);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.package-card.inactive {
  opacity: 0.6;
}

.package-card.inactive::after {
  content: 'PASIF';
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(239, 68, 68, 0.2);
  color: var(--accent-red);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}

.package-card.dragging {
  opacity: 0.5;
  transform: scale(1.02);
  cursor: grabbing;
}

.package-card.drag-over {
  border-color: var(--accent-orange);
  box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.3);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Drag Handle */
.drag-handle {
  position: absolute;
  top: 12px;
  left: 12px;
  color: var(--text-muted);
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s;
}

.package-card:hover .drag-handle {
  opacity: 1;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.game-badge {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.game-badge.hldm {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.game-badge.ag {
  background: rgba(249, 115, 22, 0.15);
  color: var(--accent-orange);
}

.game-badge.cs16 {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-blue);
}

.popular-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(234, 88, 12, 0.2) 100%);
  border: 1px solid rgba(249, 115, 22, 0.3);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  color: var(--accent-orange);
}

.discount-tag {
  padding: 4px 8px;
  background: rgba(34, 197, 94, 0.15);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-green);
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  width: 48px;
  height: 26px;
  cursor: pointer;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 13px;
  transition: all 0.3s ease;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch input:checked + .toggle-slider {
  background: linear-gradient(135deg, var(--accent-orange) 0%, #ea580c 100%);
}

.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(22px);
}

/* Package Info */
.package-info {
  margin-bottom: 16px;
}

.package-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.package-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Package Specs */
.package-specs {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid var(--card-border);
  border-bottom: 1px solid var(--card-border);
}

.spec {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.spec svg {
  color: var(--accent-orange);
}

/* Features Preview */
.features-preview {
  margin-bottom: 16px;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-secondary);
}

.feature-tag svg {
  color: var(--accent-green);
}

.feature-count {
  padding: 4px 10px;
  background: rgba(249, 115, 22, 0.15);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-orange);
}

/* Price Section */
.price-section {
  margin-bottom: 16px;
}

.price-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.old-price {
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: line-through;
}

.price-section .current-price {
  font-size: 28px;
  font-weight: 800;
  color: var(--accent-orange);
}

.price-period {
  font-size: 14px;
  color: var(--text-secondary);
}

/* Stats Row */
.stats-row {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid var(--card-border);
  margin-bottom: 16px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.mini-stat svg {
  color: var(--text-secondary);
}

/* Card Actions */
.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.action-btn.preview:hover {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
}

.action-btn.edit:hover {
  border-color: var(--accent-orange);
  color: var(--accent-orange);
}

.action-btn.duplicate:hover {
  border-color: var(--accent-purple);
  color: var(--accent-purple);
}

.action-btn.delete:hover {
  border-color: var(--accent-red);
  color: var(--accent-red);
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 80px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-orange);
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.empty-state p {
  margin: 0 0 24px;
}

/* Preview Mode */
.preview-mode {
  animation: fadeIn 0.3s ease;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  color: var(--accent-blue);
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 24px;
}

.preview-container {
  background: linear-gradient(180deg, #0a0a0c 0%, #141418 100%);
  border-radius: 20px;
  padding: 40px;
  border: 1px solid var(--card-border);
}

/* Priçing Grid (User View) */
.priçing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.priçing-card {
  background: linear-gradient(180deg, rgba(30, 30, 35, 0.9) 0%, rgba(20, 20, 24, 0.95) 100%);
  border: 1px solid var(--card-border);
  border-radius: 24px;
  padding: 32px;
  position: relative;
  transition: all 0.4s ease;
  animation: slideUp 0.5s ease backwards;
  overflow: hidden;
}

.priçing-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, transparent, rgba(249, 115, 22, 0.5), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.priçing-card:hover {
  border-color: var(--card-hover-border);
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), 0 0 40px rgba(249, 115, 22, 0.1);
}

.priçing-card:hover::before {
  opacity: 1;
}

.priçing-card.popular {
  border-color: rgba(249, 115, 22, 0.4);
  box-shadow: 0 0 40px rgba(249, 115, 22, 0.15);
}

.priçing-card.popular::before {
  opacity: 1;
  background: linear-gradient(90deg, var(--accent-orange), var(--accent-orange-light), var(--accent-orange));
}

.priçing-card.inactive {
  opacity: 0.5;
  filter: grayscale(0.5);
}

/* Badges */
.discount-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--accent-green) 0%, #16a34a 100%);
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  color: white;
  box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

.popular-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--accent-orange) 0%, #ea580c 100%);
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  color: white;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Priçing Header */
.priçing-header {
  text-align: center;
  margin-bottom: 24px;
  padding-top: 20px;
}

.game-tag {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 16px;
}

.game-tag.hldm {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.game-tag.ag {
  background: rgba(249, 115, 22, 0.15);
  color: var(--accent-orange);
}

.game-tag.cs16 {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-blue);
}

.priçing-name {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.priçing-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* Priçing Price */
.priçing-price {
  text-align: center;
  padding: 24px 0;
  margin-bottom: 24px;
  border-top: 1px solid var(--card-border);
  border-bottom: 1px solid var(--card-border);
}

.original-price {
  display: block;
  font-size: 16px;
  color: var(--text-muted);
  text-decoration: line-through;
  margin-bottom: 4px;
}

.priçing-price .current-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.priçing-price .amount {
  font-size: 48px;
  font-weight: 900;
  background: linear-gradient(135deg, var(--accent-orange) 0%, var(--accent-orange-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.priçing-price .currency {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent-orange);
}

.priçing-price .period {
  font-size: 16px;
  color: var(--text-secondary);
}

/* Priçing Specs */
.priçing-specs {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
}

.spec-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.spec-item svg {
  color: var(--accent-orange);
}

/* Priçing Features */
.priçing-features {
  margin-bottom: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 14px;
  color: var(--text-secondary);
}

.feature-item:last-child {
  border-bottom: none;
}

.check-icon {
  color: var(--accent-green);
  flex-shrink: 0;
}

.feature-more {
  text-align: center;
  padding: 12px;
  color: var(--accent-orange);
  font-size: 13px;
  font-weight: 500;
}

/* Priçing Button */
.priçing-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid var(--card-border);
  border-radius: 14px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.priçing-btn:hover {
  border-color: var(--accent-orange);
  background: rgba(249, 115, 22, 0.1);
  color: var(--accent-orange);
}

.priçing-btn.popular {
  background: linear-gradient(135deg, var(--accent-orange) 0%, #ea580c 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4);
}

.priçing-btn.popular:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(249, 115, 22, 0.5);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: linear-gradient(180deg, #1e1e23 0%, #16161a 100%);
  border: 1px solid var(--card-border);
  border-radius: 24px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5);
}

.modal.with-preview {
  max-width: 1100px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid var(--card-border);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--accent-orange);
}

.modal-title h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.modal-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-toggle:hover {
  border-color: var(--accent-orange);
  color: var(--accent-orange);
}

.preview-toggle.active {
  background: rgba(249, 115, 22, 0.1);
  border-color: var(--accent-orange);
  color: var(--accent-orange);
}

.close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--accent-red);
}

.modal-content {
  display: flex;
  overflow: hidden;
  flex: 1;
}

.modal-body {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Form Sections */
.form-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px;
}

.section-title svg {
  color: var(--accent-orange);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent-orange);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: var(--text-muted);
}

.form-group select option {
  background: var(--bg-dark);
}

.input-with-icon {
  position: relative;
}

.input-with-icon input {
  width: 100%;
  padding-right: 40px;
}

.input-suffix {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: var(--text-muted);
}

.discount-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 10px;
  color: var(--accent-green);
  font-size: 14px;
  margin-top: 16px;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.feature-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.feature-checkbox:hover {
  border-color: var(--card-hover-border);
}

.feature-checkbox.selected {
  background: rgba(249, 115, 22, 0.1);
  border-color: var(--accent-orange);
}

.feature-checkbox input {
  display: none;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid var(--card-border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.feature-checkbox.selected .checkbox-custom {
  background: var(--accent-orange);
  border-color: var(--accent-orange);
  color: white;
}

.feature-checkbox span {
  font-size: 13px;
  color: var(--text-secondary);
}

.feature-checkbox.selected span {
  color: var(--text-primary);
}

/* Status Options */
.status-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.status-checkbox {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.status-checkbox:hover {
  border-color: var(--card-hover-border);
}

.status-checkbox.active {
  border-color: var(--accent-orange);
  background: rgba(249, 115, 22, 0.05);
}

.status-checkbox input {
  display: none;
}

.status-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  transition: all 0.2s;
}

.status-checkbox.active .status-icon {
  background: rgba(249, 115, 22, 0.15);
  color: var(--accent-orange);
}

.status-checkbox.active .status-icon.popular {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.status-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-desc {
  font-size: 12px;
  color: var(--text-muted);
}

/* Inline Preview */
.inline-preview {
  width: 380px;
  background: linear-gradient(180deg, #0a0a0c 0%, #141418 100%);
  border-left: 1px solid var(--card-border);
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.preview-label {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 20px;
}

.preview-card-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-card {
  transform: scale(0.9);
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid var(--card-border);
}

/* Preview Modal */
.preview-modal-overlay {
  background: rgba(0, 0, 0, 0.9);
}

.preview-modal {
  position: relative;
  padding: 60px 40px 40px;
}

.preview-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: var(--accent-red);
}

.preview-full {
  max-width: 400px;
}

/* Confirm Modal */
.confirm-modal {
  background: linear-gradient(180deg, #1e1e23 0%, #16161a 100%);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 400px;
}

.confirm-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-red);
}

.confirm-modal h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.confirm-modal p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 8px;
}

.warning-text {
  color: var(--accent-red) !important;
  font-weight: 500;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.confirm-actions button {
  flex: 1;
}

/* Toast Container */
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 9999;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--bg-dark);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  animation: slideIn 0.3s ease;
}

.toast.success {
  border-color: rgba(34, 197, 94, 0.4);
}

.toast.success svg {
  color: var(--accent-green);
}

.toast.error {
  border-color: rgba(239, 68, 68, 0.4);
}

.toast.error svg {
  color: var(--accent-red);
}

.toast.warning {
  border-color: rgba(245, 158, 11, 0.4);
}

.toast.warning svg {
  color: #f59e0b;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal,
.modal-enter-from .confirm-modal,
.modal-leave-to .confirm-modal,
.modal-enter-from .preview-modal,
.modal-leave-to .preview-modal {
  transform: scale(0.95) translateY(20px);
}

.toast-enter-active {
  transition: all 0.3s ease;
}

.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* List Transitions */
.package-list-enter-active,
.package-list-leave-active {
  transition: all 0.3s ease;
}

.package-list-enter-from,
.package-list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.package-list-move {
  transition: transform 0.3s ease;
}

/* Responsive */
@media (max-width: 1024px) {
  .modal.with-preview {
    max-width: 700px;
  }

  .inline-preview {
    display: none;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .status-options {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions button {
    flex: 1;
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    min-width: 100%;
  }

  .filter-group {
    width: 100%;
  }

  .filter-select {
    flex: 1;
    min-width: 0;
  }

  .packages-grid {
    grid-template-columns: 1fr;
  }

  .priçing-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .modal {
    margin: 10px;
    max-height: calc(100vh - 20px);
  }

  .modal-body {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
  }

  .preview-container {
    padding: 20px;
  }

  .priçing-card {
    padding: 24px;
  }

  .priçing-price .amount {
    font-size: 36px;
  }
}
</style>
