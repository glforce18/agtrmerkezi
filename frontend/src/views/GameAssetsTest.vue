<template>
  <div class="asset-test-page">
    <h1>Game Assets Test Sayfasi</h1>

    <!-- API Test -->
    <section class="test-section">
      <h2>1. API Test</h2>
      <div class="api-buttons">
        <button @click="testAPI('games')" :disabled="loading">Oyunlari Getir</button>
        <button @click="testAPI('cs16')" :disabled="loading">CS 1.6 Assets</button>
        <button @click="testAPI('halflife')" :disabled="loading">Half-Life Assets</button>
        <button @click="testAPI('csgo')" :disabled="loading">CS:GO Assets</button>
      </div>
      <div v-if="loading" class="loading">Yükleniyor...</div>
      <pre v-if="apiResponse" class="api-response">{{ JSON.stringify(apiResponse, null, 2) }}</pre>
      <div v-if="apiError" class="error">{{ apiError }}</div>
    </section>

    <!-- Database Assets -->
    <section class="test-section">
      <h2>2. Veritabanindaki Tüm Assets ({{ allAssets.length }} adet)</h2>
      <button @click="loadAllAssets" :disabled="loading">Tüm Assets'i Yükle</button>

      <div v-if="allAssets.length > 0" class="assets-grid">
        <div v-for="asset in allAssets" :key="asset.id" class="asset-card">
          <div class="asset-image">
            <img
              :src="asset.file_path"
              :alt="asset.name"
              @error="handleImageError($event, asset)"
              @load="handleImageLoad($event, asset)"
            />
            <span class="asset-status" :class="asset.loadStatus">
              {{ asset.loadStatus || 'loading' }}
            </span>
          </div>
          <div class="asset-info">
            <strong>{{ asset.name }}</strong>
            <span class="asset-type">{{ asset.asset_type }}</span>
            <span class="asset-game">{{ asset.game_slug }}</span>
            <code class="asset-path">{{ asset.file_path }}</code>
          </div>
        </div>
      </div>
    </section>

    <!-- Direct Image Test -->
    <section class="test-section">
      <h2>3. Direkt Görsel Testi</h2>
      <div class="direct-test">
        <input v-model="testImageUrl" placeholder="/static/assets/games/cs16/heroes/cs16_hero.webp" />
        <button @click="testDirectImage">Test Et</button>
      </div>
      <div v-if="directTestResult" class="direct-result">
        <img :src="directTestResult" alt="Test" @error="directTestError = true" @load="directTestError = false" />
        <p v-if="directTestError" class="error">Görsel yüklenemedi!</p>
        <p v-else class="success">Görsel yüklendi!</p>
      </div>
    </section>

    <!-- Game Sections Preview -->
    <section class="test-section">
      <h2>4. Forum Bolum Onizleme</h2>
      <div v-for="game in ['cs16', 'halflife']" :key="game" class="section-preview">
        <h3>{{ game.toUpperCase() }}</h3>
        <div class="preview-assets">
          <div class="preview-item" v-for="type in ['hero', 'logo', 'banner', 'grid', 'icon']" :key="type">
            <span class="preview-label">{{ type }}:</span>
            <img
              v-if="getAsset(game, type)"
              :src="getAsset(game, type)"
              :alt="`${game} ${type}`"
              @error="$event.target.style.border = '2px solid red'"
              @load="$event.target.style.border = '2px solid green'"
            />
            <span v-else class="no-asset">YOK</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/services/api'

const loading = ref(false)
const apiResponse = ref(null)
const apiError = ref(null)
const allAssets = ref([])
const testImageUrl = ref('/static/assets/games/cs16/heroes/cs16_hero.webp')
const directTestResult = ref(null)
const directTestError = ref(false)

// Grouped assets by game
const gameAssets = reactive({
  cs16: {},
  halflife: {},
  csgo: {},
  css: {},
  tf2: {},
  sven: {}
})

const testAPI = async (endpoint) => {
  loading.value = true
  apiResponse.value = null
  apiError.value = null

  try {
    let url = '/game-assets/games'
    if (endpoint !== 'games') {
      url = `/game-assets/games/${endpoint}`
    }

    const response = await api.get(url)
    apiResponse.value = response
    console.log('API Response:', response)
  } catch (e) {
    apiError.value = e.message
    console.error('API Error:', e)
  } finally {
    loading.value = false
  }
}

const loadAllAssets = async () => {
  loading.value = true
  allAssets.value = []

  const games = ['cs16', 'halflife', 'csgo', 'css', 'tf2', 'sven']

  for (const game of games) {
    try {
      const response = await api.get(`/game-assets/games/${game}`)
      if (response.success && response.assets) {
        for (const asset of response.assets) {
          asset.loadStatus = 'loading'
          allAssets.value.push(asset)

          // Group by game
          if (!gameAssets[game]) gameAssets[game] = {}
          gameAssets[game][asset.asset_type] = asset.file_path
        }
      }
    } catch (e) {
      console.error(`Failed to load ${game}:`, e)
    }
  }

  loading.value = false
}

const handleImageError = (event, asset) => {
  asset.loadStatus = 'error'
  console.error('Image load failed:', asset.file_path)
}

const handleImageLoad = (event, asset) => {
  asset.loadStatus = 'loaded'
  console.log('Image loaded:', asset.file_path)
}

const testDirectImage = () => {
  directTestResult.value = testImageUrl.value
  directTestError.value = false
}

const getAsset = (game, type) => {
  return gameAssets[game]?.[type] || null
}

onMounted(() => {
  loadAllAssets()
})
</script>

<style scoped>
.asset-test-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background: #0a0a0a;
  min-height: 100vh;
  color: #fff;
}

h1 {
  color: #f97316;
  margin-bottom: 30px;
}

h2 {
  color: #22d3ee;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #333;
}

.test-section {
  background: #111;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.api-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

button {
  padding: 10px 20px;
  background: #f97316;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

button:hover {
  background: #ea580c;
}

button:disabled {
  background: #666;
  cursor: not-allowed;
}

.api-response {
  background: #1a1a1a;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.loading {
  color: #22d3ee;
  padding: 20px;
}

.error {
  color: #ef4444;
  padding: 10px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
}

.success {
  color: #22c55e;
}

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.asset-card {
  background: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #333;
}

.asset-image {
  position: relative;
  height: 150px;
  background: #222;
  display: flex;
  align-items: center;
  justify-content: center;
}

.asset-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.asset-status {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.asset-status.loading {
  background: #f59e0b;
  color: #000;
}

.asset-status.loaded {
  background: #22c55e;
  color: #fff;
}

.asset-status.error {
  background: #ef4444;
  color: #fff;
}

.asset-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.asset-info strong {
  color: #fff;
  font-size: 14px;
}

.asset-type {
  display: inline-block;
  padding: 2px 8px;
  background: #f97316;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  width: fit-content;
}

.asset-game {
  color: #22d3ee;
  font-size: 12px;
}

.asset-path {
  font-size: 10px;
  color: #888;
  word-break: break-all;
  background: #0a0a0a;
  padding: 6px;
  border-radius: 4px;
}

.direct-test {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.direct-test input {
  flex: 1;
  padding: 10px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  color: #fff;
}

.direct-result {
  text-align: center;
}

.direct-result img {
  max-width: 400px;
  max-height: 300px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.section-preview {
  background: #1a1a1a;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.section-preview h3 {
  color: #f97316;
  margin-bottom: 15px;
}

.preview-assets {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.preview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #222;
  border-radius: 8px;
  min-width: 120px;
}

.preview-label {
  font-size: 12px;
  color: #888;
  text-transform: uppercase;
}

.preview-item img {
  width: 100px;
  height: 80px;
  object-fit: contain;
  border-radius: 4px;
  border: 2px solid #333;
}

.no-asset {
  color: #ef4444;
  font-size: 12px;
}
</style>
