<!-- Home.vue - Yeniden Yapılandırılmış Ana Sayfa -->
<template>
  <div class="home-layout">
    
    <!-- KOMPAKT HERO SECTION -->
    <section class="hero-compact">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="logo-icon">🔶</span>
          <span class="logo-text">AGTR Merkezi</span>
        </h1>
        
        <div class="stats-inline">
          <div class="stat-item">
            <span class="stat-icon">👥</span>
            <span class="stat-value">{{ stats.onlineUsers }}</span>
            <span class="stat-label">Online</span>
          </div>
          
          <div class="stat-item">
            <span class="stat-icon">💬</span>
            <span class="stat-value">{{ stats.totalTopics }}</span>
            <span class="stat-label">Konu</span>
          </div>
          
          <div class="stat-item">
            <span class="stat-icon">🎮</span>
            <span class="stat-value">{{ stats.activeServers }}</span>
            <span class="stat-label">Sunucu</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ANA GRID LAYOUT -->
    <div class="main-grid">
      
      <!-- SOL TARAF: FORUM İÇERİĞİ (60%) -->
      <main class="forum-section">
        
        <!-- CANLI AKTİVİTE AKIM -->
        <LiveActivityFeed :activities="liveActivities" />

        <!-- TREND KONULAR -->
        <TrendingTopicsSection 
          :topics="trendingTopics"
          :loading="loading.trending"
        />

        <!-- SON KONULAR -->
        <RecentTopicsSection 
          :topics="recentTopics"
          :loading="loading.recent"
        />

        <!-- TÜM KONULARI GÖR BUTONU -->
        <div class="view-all-container">
          <n-button 
            type="primary" 
            size="large" 
            @click="goToForum"
            class="view-all-button"
          >
            Tüm Konuları Gör →
          </n-button>
        </div>

      </main>

      <!-- SAĞ SIDEBAR (40%) -->
      <aside class="sidebar">
        
        <!-- HIZLI ERİŞİM -->
        <div class="quick-actions-card card">
          <h3 class="card-title">⚡ Hızlı Erişim</h3>
          <div class="quick-actions">
            <n-button 
              type="primary" 
              size="large" 
              block
              @click="goToForum"
              class="quick-action-btn"
            >
              <template #icon>
                <span>💬</span>
              </template>
              Forum'a Git
            </n-button>
            
            <n-button 
              type="success" 
              size="large" 
              block
              @click="createTopic"
              class="quick-action-btn"
            >
              <template #icon>
                <span>✍️</span>
              </template>
              Yeni Konu Aç
            </n-button>
          </div>
        </div>

        <!-- ONLINE KULLANICILAR -->
        <OnlineUsersWidget 
          :users="onlineUsers"
          :total="stats.onlineUsers"
        />

        <!-- KOMPAKT SUNUCULAR -->
        <CompactServersWidget 
          :servers="servers"
          :loading="loading.servers"
        />

        <!-- KATEGORİ HIZLI ERİŞİM -->
        <QuickCategoriesWidget 
          :categories="categories"
        />

      </aside>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import LiveActivityFeed from '@/components/forum/LiveActivityFeed.vue'
import TrendingTopicsSection from '@/components/forum/TrendingTopicsSection.vue'
import RecentTopicsSection from '@/components/forum/RecentTopicsSection.vue'
import OnlineUsersWidget from '@/components/sidebar/OnlineUsersWidget.vue'
import CompactServersWidget from '@/components/sidebar/CompactServersWidget.vue'
import QuickCategoriesWidget from '@/components/sidebar/QuickCategoriesWidget.vue'

const router = useRouter()
const authStore = useAuthStore()

// State
const stats = ref({
  onlineUsers: 0,
  totalTopics: 0,
  activeServers: 0
})

const liveActivities = ref([])
const trendingTopics = ref([])
const recentTopics = ref([])
const onlineUsers = ref([])
const servers = ref([])
const categories = ref([])

const loading = ref({
  trending: true,
  recent: true,
  servers: true
})

// WebSocket connection
let ws = null

// Methods
const fetchStats = async () => {
  try {
    const response = await api.get('/forum/stats')
    stats.value = response
  } catch (error) {
    console.error('Stats yüklenemedi:', error)
  }
}

const fetchTrendingTopics = async () => {
  loading.value.trending = true
  try {
    const response = await api.get('/forum/trending?days=7&limit=5')
    trendingTopics.value = response.topics
  } catch (error) {
    console.error('Trend konular yüklenemedi:', error)
  } finally {
    loading.value.trending = false
  }
}

const fetchRecentTopics = async () => {
  loading.value.recent = true
  try {
    const response = await api.get('/forum/topics?sort=recent&limit=10')
    recentTopics.value = response.topics
  } catch (error) {
    console.error('Son konular yüklenemedi:', error)
  } finally {
    loading.value.recent = false
  }
}

const fetchOnlineUsers = async () => {
  try {
    const response = await api.get('/forum/online-users')
    onlineUsers.value = response.users
  } catch (error) {
    console.error('Online kullanıcılar yüklenemedi:', error)
  }
}

const fetchServers = async () => {
  loading.value.servers = true
  try {
    const response = await api.get('/servers?status=online&limit=3')
    servers.value = response.servers
  } catch (error) {
    console.error('Sunucular yüklenemedi:', error)
  } finally {
    loading.value.servers = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await api.get('/forum/categories')
    categories.value = response.categories
  } catch (error) {
    console.error('Kategoriler yüklenemedi:', error)
  }
}

const connectWebSocket = () => {
  ws = new WebSocket('wss://agtrmerkezi.com/ws/forum-live')
  
  ws.onopen = () => {
    console.log('WebSocket bağlantısı açıldı')
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'new_activity') {
      // Yeni aktiviteyi başa ekle
      liveActivities.value.unshift(data.activity)
      
      // Max 20 aktivite tut
      if (liveActivities.value.length > 20) {
        liveActivities.value.pop()
      }
      
      // İstatistikleri güncelle
      if (data.activity.type === 'new_topic') {
        stats.value.totalTopics++
      }
    }
    
    if (data.type === 'online_users_update') {
      stats.value.onlineUsers = data.count
      onlineUsers.value = data.users
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket hatası:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket bağlantısı kapandı, yeniden bağlanılıyor...')
    // 5 saniye sonra yeniden bağlan
    setTimeout(connectWebSocket, 5000)
  }
}

const goToForum = () => {
  router.push('/forum')
}

const createTopic = () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  router.push('/forum/new-topic')
}

// Lifecycle
onMounted(async () => {
  // Tüm veriyi paralel yükle
  await Promise.all([
    fetchStats(),
    fetchTrendingTopics(),
    fetchRecentTopics(),
    fetchOnlineUsers(),
    fetchServers(),
    fetchCategories()
  ])
  
  // WebSocket bağlantısı aç
  connectWebSocket()
  
  // Periyodik güncellemeler
  const intervalId = setInterval(() => {
    fetchStats()
    fetchOnlineUsers()
  }, 30000) // 30 saniyede bir
  
  // Cleanup için kaydet
  onUnmounted(() => {
    clearInterval(intervalId)
    if (ws) {
      ws.close()
    }
  })
})
</script>

<style scoped>
/* Ana Layout */
.home-layout {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* Kompakt Hero */
.hero-compact {
  background: linear-gradient(135deg, 
    rgba(249, 115, 22, 0.1) 0%, 
    rgba(139, 92, 246, 0.1) 100%);
  border-radius: var(--radius-lg);
  padding: 30px;
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  overflow: hidden;
}

.hero-compact::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    var(--primary) 50%, 
    transparent 100%);
  animation: shine 3s infinite;
}

@keyframes shine {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.hero-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 20px 0;
  color: var(--text-primary);
}

.logo-icon {
  font-size: 2.5rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.stats-inline {
  display: flex;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Grid Layout */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
}

@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    grid-template-columns: 1fr;
  }
}

/* Forum Section */
.forum-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.view-all-container {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.view-all-button {
  min-width: 250px;
  font-size: 1.1rem;
  padding: 12px 30px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  transition: all 0.3s ease;
}

.view-all-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: var(--text-primary);
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-action-btn {
  font-size: 1rem;
  padding: 12px 20px;
  transition: all 0.3s ease;
}

.quick-action-btn:hover {
  transform: translateX(4px);
}
</style>
