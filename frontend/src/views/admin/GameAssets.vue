<template>
  <AdminLayout>
    <div class="game-assets-admin">
      <!-- Page Header -->
      <header class="admin-header">
        <div class="header-content">
          <div class="header-title-group">
            <h1 class="header-title">
              <Gamepad2 :size="28" />
              Oyun Görselleri
            </h1>
            <p class="header-subtitle">CS 1.6 ve Half-Life oyun görsellerini yonetin</p>
          </div>
          <div class="header-actions">
            <button class="btn-secondary" @click="refreshAssets" :disabled="loading">
              <RefreshCw :size="18" :class="{ 'animate-spin': loading }" />
              <span>Yenile</span>
            </button>
            <button class="btn-primary" @click="showScrapeModal = true">
              <Download :size="18" />
              <span>Asset Cek</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon stat-icon--orange">
            <Image :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalAssets }}</span>
            <span class="stat-label">Toplam Görsel</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--blue">
            <Gamepad2 :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ Object.keys(gameGroups).length }}</span>
            <span class="stat-label">Oyun</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--green">
            <CheckCircle :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ loadedAssets }}</span>
            <span class="stat-label">Yüklenen</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--red">
            <AlertCircle :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ errorAssets }}</span>
            <span class="stat-label">Hata</span>
          </div>
        </div>
      </div>

      <!-- Game Tabs -->
      <div class="game-tabs">
        <button
          v-for="game in games"
          :key="game.slug"
          class="game-tab"
          :class="{ active: activeGame === game.slug }"
          @click="activeGame = game.slug"
        >
          <img
            v-if="getGameIcon(game.slug)"
            :src="getGameIcon(game.slug)"
            :alt="game.name"
            class="game-tab-icon"
          />
          <span>{{ game.name }}</span>
          <span class="game-tab-count">{{ getGameAssetCount(game.slug) }}</span>
        </button>
      </div>

      <!-- Assets Grid -->
      <div class="assets-section">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner" />
          <span>Görsel yükleniyor...</span>
        </div>

        <div v-else-if="filteredAssets.length === 0" class="empty-state">
          <Package :size="64" />
          <h3>Görsel Bulunamadi</h3>
          <p>Bu oyun icin henuz görsel eklenmemis.</p>
          <button class="btn-primary" @click="showScrapeModal = true">
            <Download :size="18" />
            <span>Görsel Cek</span>
          </button>
        </div>

        <div v-else class="assets-grid">
          <div
            v-for="asset in filteredAssets"
            :key="asset.id"
            class="asset-card"
            :class="`asset-card--${asset.asset_type}`"
          >
            <div class="asset-image">
              <img
                :src="asset.file_path"
                :alt="asset.name"
                @load="onAssetLoad(asset)"
                @error="onAssetError(asset)"
              />
              <div class="asset-type-badge">{{ formatAssetType(asset.asset_type) }}</div>
              <div class="asset-overlay">
                <button class="overlay-btn" @click="previewAsset(asset)" title="Onizle">
                  <Eye :size="18" />
                </button>
                <button class="overlay-btn" @click="copyAssetUrl(asset)" title="URL Kopyala">
                  <Link :size="18" />
                </button>
                <button class="overlay-btn danger" @click="deleteAsset(asset)" title="Sil">
                  <Trash2 :size="18" />
                </button>
              </div>
              <div v-if="asset.loadStatus === 'error'" class="asset-error">
                <AlertCircle :size="32" />
                <span>Yüklenemedi</span>
              </div>
            </div>
            <div class="asset-info">
              <h4 class="asset-name">{{ asset.name }}</h4>
              <div class="asset-meta">
                <span class="asset-source">{{ asset.source }}</span>
                <span class="asset-date">{{ formatDate(asset.created_at) }}</span>
              </div>
              <code class="asset-path">{{ asset.file_path }}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Scrape Modal -->
      <n-modal v-model:show="showScrapeModal" :mask-closable="false" class="admin-modal">
        <div class="modal-content">
          <div class="modal-header">
            <Download :size="24" class="text-orange-500" />
            <div>
              <h2>Asset Cek</h2>
              <p>SteamGridDB'den oyun görsellerini cek</p>
            </div>
            <button class="modal-close" @click="showScrapeModal = false">
              <X :size="20" />
            </button>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Oyun Seç</label>
              <div class="game-select-grid">
                <button
                  v-for="game in games"
                  :key="game.slug"
                  class="game-select-item"
                  :class="{ selected: scrapeForm.games.includes(game.slug) }"
                  @click="toggleGameSelection(game.slug)"
                >
                  <img
                    v-if="getGameIcon(game.slug)"
                    :src="getGameIcon(game.slug)"
                    :alt="game.name"
                    class="game-select-icon"
                  />
                  <span>{{ game.name }}</span>
                  <CheckCircle v-if="scrapeForm.games.includes(game.slug)" :size="18" class="check-icon" />
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Asset Turleri</label>
              <div class="asset-type-select">
                <label v-for="type in assetTypes" :key="type.value" class="checkbox-label">
                  <input
                    type="checkbox"
                    v-model="scrapeForm.types"
                    :value="type.value"
                  />
                  <span class="checkbox-box">
                    <Check :size="12" />
                  </span>
                  <span>{{ type.label }}</span>
                </label>
              </div>
            </div>

            <div v-if="scrapeProgress.active" class="scrape-progress">
              <div class="progress-header">
                <span>{{ scrapeProgress.message }}</span>
                <span>{{ scrapeProgress.current }} / {{ scrapeProgress.total }}</span>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: `${(scrapeProgress.current / scrapeProgress.total) * 100}%` }"
                />
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="showScrapeModal = false">İptal</button>
            <button
              class="btn-primary"
              :disabled="scrapeProgress.active || scrapeForm.games.length === 0"
              @click="startScrape"
            >
              <Download :size="18" />
              <span>{{ scrapeProgress.active ? 'Cekiliyor...' : 'Baslat' }}</span>
            </button>
          </div>
        </div>
      </n-modal>

      <!-- Preview Modal -->
      <n-modal v-model:show="showPreviewModal" class="preview-modal">
        <div class="preview-content">
          <button class="preview-close" @click="showPreviewModal = false">
            <X :size="24" />
          </button>
          <img
            v-if="previewAssetData"
            :src="previewAssetData.file_path"
            :alt="previewAssetData.name"
            class="preview-image"
          />
          <div v-if="previewAssetData" class="preview-info">
            <h3>{{ previewAssetData.name }}</h3>
            <p>{{ previewAssetData.game_slug }} - {{ formatAssetType(previewAssetData.asset_type) }}</p>
            <code>{{ previewAssetData.file_path }}</code>
          </div>
        </div>
      </n-modal>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import AdminLayout from '@/components/admin/AdminLayout.vue'
import api from '@/services/api'
import {
  Gamepad2,
  RefreshCw,
  Download,
  Image,
  CheckCircle,
  AlertCircle,
  Package,
  Eye,
  Link,
  Trash2,
  X,
  Check
} from 'lucide-vue-next'

// State
const loading = ref(false)
const assets = ref([])
const activeGame = ref('cs16')
const showScrapeModal = ref(false)
const showPreviewModal = ref(false)
const previewAssetData = ref(null)

// Asset load tracking
const assetLoadStatus = reactive({})
const loadedAssets = computed(() => Object.values(assetLoadStatus).filter(s => s === 'loaded').length)
const errorAssets = computed(() => Object.values(assetLoadStatus).filter(s => s === 'error').length)

// Games configuration
const games = [
  { slug: 'cs16', name: 'Counter-Strike 1.6', steamgriddb_id: 119 },
  { slug: 'halflife', name: 'Half-Life', steamgriddb_id: 21207 }
]

const assetTypes = [
  { value: 'hero', label: 'Hero (Banner)' },
  { value: 'logo', label: 'Logo' },
  { value: 'grid', label: 'Grid (Poster)' },
  { value: 'icon', label: 'Icon' }
]

// Scrape form
const scrapeForm = reactive({
  games: ['cs16', 'halflife'],
  types: ['hero', 'logo', 'grid', 'icon']
})

const scrapeProgress = reactive({
  active: false,
  current: 0,
  total: 0,
  message: ''
})

// Computed
const totalAssets = computed(() => assets.value.length)

const gameGroups = computed(() => {
  const groups = {}
  assets.value.forEach(asset => {
    if (!groups[asset.game_slug]) {
      groups[asset.game_slug] = []
    }
    groups[asset.game_slug].push(asset)
  })
  return groups
})

const filteredAssets = computed(() => {
  return assets.value.filter(a => a.game_slug === activeGame.value)
})

// Methods
const getGameAssetCount = (slug) => {
  return gameGroups.value[slug]?.length || 0
}

const getGameIcon = (slug) => {
  const asset = assets.value.find(a => a.game_slug === slug && a.asset_type === 'icon')
  return asset?.file_path || null
}

const formatAssetType = (type) => {
  const labels = {
    hero: 'Hero',
    logo: 'Logo',
    grid: 'Grid',
    icon: 'Icon',
    banner: 'Banner'
  }
  return labels[type] || type
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

const onAssetLoad = (asset) => {
  assetLoadStatus[asset.id] = 'loaded'
  asset.loadStatus = 'loaded'
}

const onAssetError = (asset) => {
  assetLoadStatus[asset.id] = 'error'
  asset.loadStatus = 'error'
}

const refreshAssets = async () => {
  loading.value = true
  try {
    const response = await api.get('/game-assets/games')
    if (response.success && response.games) {
      assets.value = []
      for (const gameSlug of Object.keys(response.games)) {
        const gameResponse = await api.get(`/game-assets/games/${gameSlug}`)
        if (gameResponse.success && gameResponse.assets) {
          assets.value.push(...gameResponse.assets)
        }
      }
    }
  } catch (error) {
    console.error('Failed to fetch assets:', error)
    window.$message?.error('Görsel yüklenemedi')
  } finally {
    loading.value = false
  }
}

const toggleGameSelection = (slug) => {
  const index = scrapeForm.games.indexOf(slug)
  if (index > -1) {
    scrapeForm.games.splice(index, 1)
  } else {
    scrapeForm.games.push(slug)
  }
}

const startScrape = async () => {
  if (scrapeForm.games.length === 0) {
    window.$message?.warning('Lutfen en az bir oyun seçin')
    return
  }

  scrapeProgress.active = true
  scrapeProgress.total = scrapeForm.games.length
  scrapeProgress.current = 0

  try {
    for (const gameSlug of scrapeForm.games) {
      scrapeProgress.message = `${gameSlug} görselleri cekiliyor...`
      scrapeProgress.current++

      try {
        await api.post(`/game-assets/scrape/${gameSlug}`, {
          types: scrapeForm.types
        })
      } catch (e) {
        console.error(`Failed to scrape ${gameSlug}:`, e)
      }
    }

    window.$message?.success('Görsel cekme işlemi tamamlandı')
    showScrapeModal.value = false
    refreshAssets()
  } catch (error) {
    console.error('Scrape failed:', error)
    window.$message?.error('Görsel cekme işlemi başarısız')
  } finally {
    scrapeProgress.active = false
  }
}

const previewAsset = (asset) => {
  previewAssetData.value = asset
  showPreviewModal.value = true
}

const copyAssetUrl = async (asset) => {
  try {
    await navigator.clipboard.writeText(window.location.origin + asset.file_path)
    window.$message?.success('URL kopyalandi')
  } catch (e) {
    window.$message?.error('URL kopyalanamadi')
  }
}

const deleteAsset = async (asset) => {
  if (!confirm(`"${asset.name}" görselini silmek istediginize emin misiniz?`)) return

  try {
    await api.delete(`/game-assets/${asset.id}`)
    assets.value = assets.value.filter(a => a.id !== asset.id)
    window.$message?.success('Görsel silindi')
  } catch (error) {
    console.error('Delete failed:', error)
    window.$message?.error('Görsel silinemedi')
  }
}

onMounted(() => {
  refreshAssets()
})
</script>

<style scoped>
.game-assets-admin {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.admin-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-title-group h1 {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
}

.header-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 15px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ea580c, #dc2626);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon--orange { background: rgba(249, 115, 22, 0.15); color: #f97316; }
.stat-icon--blue { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.stat-icon--green { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.stat-icon--red { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* Game Tabs */
.game-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.game-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.game-tab:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.game-tab.active {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(139, 92, 246, 0.1));
  border-color: rgba(249, 115, 22, 0.5);
  color: #fff;
}

.game-tab-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  object-fit: cover;
}

.game-tab-count {
  padding: 2px 8px;
  background: rgba(249, 115, 22, 0.2);
  border-radius: 20px;
  font-size: 12px;
  color: #f97316;
}

/* Assets Grid */
.assets-section {
  min-height: 400px;
}

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.asset-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.asset-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}

.asset-card--hero { border-left: 3px solid #f97316; }
.asset-card--logo { border-left: 3px solid #8b5cf6; }
.asset-card--grid { border-left: 3px solid #22d3ee; }
.asset-card--icon { border-left: 3px solid #22c55e; }

.asset-image {
  position: relative;
  height: 160px;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.asset-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.asset-type-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  text-transform: uppercase;
}

.asset-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.asset-card:hover .asset-overlay {
  opacity: 1;
}

.overlay-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.overlay-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.overlay-btn.danger:hover {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.asset-error {
  position: absolute;
  inset: 0;
  background: rgba(239, 68, 68, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #ef4444;
}

.asset-info {
  padding: 16px;
}

.asset-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px;
}

.asset-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.asset-source,
.asset-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.asset-path {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(0, 0, 0, 0.3);
  padding: 6px 10px;
  border-radius: 6px;
  word-break: break-all;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(249, 115, 22, 0.2);
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state h3 {
  font-size: 18px;
  color: #fff;
  margin: 0;
}

.empty-state p {
  margin: 0;
}

/* Modal */
.modal-content {
  width: 100%;
  max-width: 600px;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px;
}

.modal-header p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.modal-close {
  margin-left: auto;
  padding: 8px;
  color: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Form Elements */
.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 12px;
}

.game-select-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.game-select-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: all 0.2s ease;
  position: relative;
}

.game-select-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.game-select-item.selected {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.5);
  color: #fff;
}

.game-select-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  object-fit: cover;
}

.check-icon {
  margin-left: auto;
  color: #22c55e;
}

.asset-type-select {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.checkbox-label:hover {
  background: rgba(255, 255, 255, 0.05);
}

.checkbox-label input {
  display: none;
}

.checkbox-box {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
  transition: all 0.2s ease;
}

.checkbox-label input:checked + .checkbox-box {
  background: #f97316;
  border-color: #f97316;
  color: #fff;
}

/* Scrape Progress */
.scrape-progress {
  margin-top: 20px;
  padding: 16px;
  background: rgba(249, 115, 22, 0.05);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #ea580c);
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Preview Modal */
.preview-content {
  position: relative;
  background: #0a0a0a;
  border-radius: 16px;
  overflow: hidden;
  max-width: 90vw;
  max-height: 90vh;
}

.preview-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.2s ease;
}

.preview-close:hover {
  background: rgba(0, 0, 0, 0.7);
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  display: block;
  margin: 0 auto;
}

.preview-info {
  padding: 20px;
  text-align: center;
}

.preview-info h3 {
  font-size: 18px;
  color: #fff;
  margin: 0 0 8px;
}

.preview-info p {
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 12px;
}

.preview-info code {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 8px;
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .game-tabs {
    flex-wrap: wrap;
  }

  .game-select-grid {
    grid-template-columns: 1fr;
  }
}

/* Animation */
.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
