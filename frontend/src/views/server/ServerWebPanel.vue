<template>
  <div class="min-h-screen bg-dark-bg">
    <!-- Top Bar -->
    <div class="glass border-b border-dark-border sticky top-0 z-40">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <!-- Server Info -->
          <div class="flex items-center gap-4">
            <router-link to="/servers/my" class="btn-ghost px-3 py-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </router-link>
            <div>
              <h1 class="text-xl font-bold text-text-primary flex items-center gap-2">
                {{ serverInfo?.name || 'Yükleniyor...' }}
                <span
                  class="status-dot inline-block"
                  :class="serverInfo?.is_running ? 'online pulse' : 'offline'"
                ></span>
              </h1>
              <p class="text-sm text-text-muted font-mono">
                {{ serverInfo?.ip_address }}:{{ serverInfo?.port }}
              </p>
            </div>
          </div>

          <!-- Quick Stats -->
          <div class="hidden md:flex items-center gap-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-status-success">{{ serverStatus?.current_players || 0 }}</div>
              <div class="text-xs text-text-muted">Oyuncu</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-primary">{{ serverInfo?.slots || 0 }}</div>
              <div class="text-xs text-text-muted">Slot</div>
            </div>
            <div class="text-center">
              <div class="text-sm font-medium text-text-primary">{{ serverStatus?.current_map || 'N/A' }}</div>
              <div class="text-xs text-text-muted">Map</div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <button
              v-if="!serverInfo?.is_running"
              @click="startServer"
              :disabled="loading"
              class="btn btn-primary"
            >
              ▶ Başlat
            </button>
            <button
              v-else
              @click="stopServer"
              :disabled="loading"
              class="btn btn-secondary text-status-error border-status-error/30"
            >
              ⏹ Durdur
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-6">
      <div class="grid grid-cols-12 gap-6">
        <!-- Sidebar -->
        <div class="col-span-12 lg:col-span-3">
          <div class="glass-card p-4 sticky top-24">
            <nav class="space-y-1">
              <router-link
                :to="{ name: 'server-webpanel-dashboard' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span>Dashboard</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-settings' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>Ayarlar</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-files' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <span>Dosya Yönetimi</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-console' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>Console (RCON)</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-plugins' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                <span>Pluginler</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-plugin-compiler' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <span>Plugin Compiler</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-plugin-configs' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                <span>Plugin Configs</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-plugin-logs' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Plugin Logs</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-motd-editor' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>MOTD Editor</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-statistics' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00 2-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Statistics</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-performance' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Performance</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-config' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                <span>Config Editor</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-files-browser' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
                </svg>
                <span>Dosya Tarayıcı</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-admin' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span>Admin & Ban</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-maps' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                <span>Mapler</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-map-uploader' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>Map Upload</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-vip-manager' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                <span>VIP Manager</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-players' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <span>Oyuncular</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-logs' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Log Dosyaları</span>
              </router-link>

              <router-link
                :to="{ name: 'server-webpanel-backups' }"
                class="nav-item"
                active-class="active"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
                <span>Yedekler</span>
              </router-link>

              <div class="divider my-4"></div>

              <div class="text-text-muted text-xs px-3 py-2">
                <div class="flex justify-between mb-1">
                  <span>Server ID</span>
                  <span class="font-mono">{{ serverId }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Kod</span>
                  <span class="font-mono text-primary">{{ serverInfo?.unique_code }}</span>
                </div>
              </div>
            </nav>
          </div>
        </div>

        <!-- Content Area -->
        <div class="col-span-12 lg:col-span-9">
          <router-view
            :server-id="serverId"
            :server-info="serverInfo"
            :server-status="serverStatus"
            @refresh="loadServerData"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'

const route = useRoute()
const router = useRouter()
const serverId = ref(parseInt(route.params.id))

// Check if panel mode
const isPanelMode = ref(localStorage.getItem('panel_mode') === 'true')
const panelServerId = ref(parseInt(localStorage.getItem('panel_server_id')))

const serverInfo = ref(null)
const serverStatus = ref(null)
const loading = ref(false)
const refreshInterval = ref(null)

// Load server data
const loadServerData = async () => {
  console.log('[PANEL] loadServerData called')
  try {
    // Load server info
    console.log('[PANEL] Fetching server info...')
    const infoRes = await apiClient.get(`/servers/${serverId.value}/webpanel/info`)
    console.log('[PANEL] Server info loaded:', infoRes.data)
    serverInfo.value = infoRes.data

    // Load server status
    console.log('[PANEL] Fetching server status...')
    const statusRes = await apiClient.get(`/servers/${serverId.value}/webpanel/status`)
    console.log('[PANEL] Server status loaded:', statusRes.data)
    serverStatus.value = statusRes.data
  } catch (error) {
    console.error('[PANEL] Failed to load server data:', error)
    console.error('[PANEL] Error status:', error.response?.status)
    console.error('[PANEL] Error detail:', error.response?.data)
  }
}

// Server control
const startServer = async () => {
  loading.value = true
  try {
    await apiClient.post(`/servers/${serverId.value}/start`)
    setTimeout(loadServerData, 2000)
  } catch (error) {
    alert('Sunucu başlatılamadı: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const stopServer = async () => {
  if (!confirm('Sunucuyu durdurmak istediğinizden emin misiniz?')) return

  loading.value = true
  try {
    await apiClient.post(`/servers/${serverId.value}/stop`)
    setTimeout(loadServerData, 2000)
  } catch (error) {
    alert('Sunucu durdurulamadı: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  console.log('[PANEL] Component mounted')
  console.log('[PANEL] Server ID from route:', serverId.value)
  console.log('[PANEL] isPanelMode:', isPanelMode.value)
  console.log('[PANEL] panelServerId:', panelServerId.value)

  // Panel mode validation
  if (isPanelMode.value) {
    console.log('[PANEL] Panel mode detected')

    // Check if trying to access different server
    if (serverId.value !== panelServerId.value) {
      console.error('[PANEL] Server ID mismatch!', serverId.value, 'vs', panelServerId.value)
      alert('Panel modunda sadece kendi sunucunuze erişebilirsiniz')
      router.push({ name: 'server-webpanel-dashboard', params: { id: panelServerId.value } })
      return
    }

    // Use panel token instead of auth token
    const panelToken = localStorage.getItem('panel_token')
    console.log('[PANEL] Using panel token:', panelToken ? 'exists' : 'MISSING!')

    if (panelToken) {
      apiClient.defaults.headers.Authorization = `Bearer ${panelToken}`
      console.log('[PANEL] Authorization header set')
    } else {
      console.error('[PANEL] NO PANEL TOKEN FOUND!')
    }
  } else {
    console.log('[PANEL] NOT in panel mode - using Steam auth')
  }

  console.log('[PANEL] Loading server data...')
  loadServerData()

  // Auto-refresh every 30 seconds
  refreshInterval.value = setInterval(loadServerData, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.nav-item {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-lg;
  @apply text-text-secondary hover:text-text-primary;
  @apply transition-all duration-200;
  @apply hover:bg-dark-hover;
}

.nav-item.active {
  @apply bg-primary/10 text-primary border-l-4 border-primary;
  @apply shadow-md;
}

.nav-item svg {
  @apply flex-shrink-0;
}
</style>
