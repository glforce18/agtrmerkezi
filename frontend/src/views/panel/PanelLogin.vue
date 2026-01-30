<template>
  <div class="min-h-screen bg-dark-bg flex items-center justify-center p-4">
    <!-- Background -->
    <div class="fixed inset-0 z-0">
      <div class="absolute inset-0 bg-gradient-to-br from-dark-bg via-dark-card to-dark-bg"></div>
      <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,107,53,0.3) 1px, transparent 0); background-size: 40px 40px;"></div>
    </div>

    <!-- Login Card -->
    <div class="glass-card p-8 max-w-md w-full relative z-10 fade-in-up">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gradient mb-2">🎮 AGTR Merkezi</h1>
        <p class="text-text-secondary">Server Panel Girişi</p>
      </div>

      <!-- Loading State -->
      <div v-if="loadingServers" class="text-center py-8">
        <div class="spinner mx-auto mb-4"></div>
        <p class="text-text-muted">Sunucular yükleniyor...</p>
      </div>

      <!-- Login Form -->
      <form v-else @submit.prevent="handleLogin" class="space-y-4">
        <!-- Server Selection -->
        <div>
          <label class="block text-sm font-medium text-text-primary mb-2">
            Sunucu Seçin
          </label>
          <select
            v-model="form.server_id"
            class="input"
            required
            @change="onServerChange"
          >
            <option value="">Bir sunucu seçin...</option>
            <option
              v-for="server in servers"
              :key="server.id"
              :value="server.id"
            >
              {{ server.display }}
            </option>
          </select>
          <p class="text-xs text-text-muted mt-1">
            {{ servers.length }} sunucu mevcut
          </p>
        </div>

        <!-- Selected Server Info -->
        <div v-if="selectedServer" class="bg-dark-elevated rounded-lg p-4 border border-primary/20">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-2xl">
              🖥️
            </div>
            <div>
              <div class="font-semibold text-text-primary">{{ selectedServer.name }}</div>
              <div class="text-sm text-text-muted">
                {{ selectedServer.game_type?.toUpperCase() }} • {{ selectedServer.ip_address }}:{{ selectedServer.port }}
              </div>
            </div>
          </div>
        </div>

        <!-- Panel Password -->
        <div>
          <label class="block text-sm font-medium text-text-primary mb-2">
            Panel Şifresi
          </label>
          <div class="relative">
            <input
              v-model="form.panel_password"
              :type="showPassword ? 'text' : 'password'"
              class="input pr-10"
              placeholder="Panel şifrenizi girin"
              required
              :disabled="!form.server_id"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <p class="text-xs text-text-muted mt-1">
            Panel şifrenizi sunucu sahibinden alabilirsiniz
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-error">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          {{ error }}
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading || !form.server_id"
          class="btn btn-primary w-full"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ loading ? 'Giriş Yapılıyor...' : 'Panele Giriş Yap' }}
        </button>
      </form>

      <!-- Divider -->
      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-dark-border"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-dark-card text-text-muted">veya</span>
        </div>
      </div>

      <!-- Steam Login -->
      <a
        href="https://agtrmerkezi.com/login"
        class="btn btn-secondary w-full flex items-center justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
        </svg>
        Steam ile Giriş Yap
      </a>

      <!-- Info -->
      <div class="mt-6 text-center text-xs text-text-muted">
        <p>Steam ile giriş yaparsanız tüm sunucularınızı yönetebilirsiniz</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'

const router = useRouter()

const form = ref({
  server_id: '',
  panel_password: ''
})

const servers = ref([])
const loadingServers = ref(true)
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const selectedServer = computed(() => {
  if (!form.value.server_id) return null
  return servers.value.find(s => s.id === parseInt(form.value.server_id))
})

// Load available servers
const loadServers = async () => {
  loadingServers.value = true
  try {
    const response = await apiClient.get('/panel/servers')
    servers.value = response.data.servers || []

    if (servers.value.length === 0) {
      error.value = 'Şu anda panel erişimi olan sunucu bulunmamaktadır'
    }
  } catch (err) {
    console.error('Failed to load servers:', err)
    error.value = 'Sunucular yüklenemedi. Lütfen daha sonra tekrar deneyin.'
  } finally {
    loadingServers.value = false
  }
}

const onServerChange = () => {
  error.value = ''
}

// Handle login
const handleLogin = async () => {
  if (!form.value.server_id) {
    error.value = 'Lütfen bir sunucu seçin'
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('[DEBUG] Starting panel login...')
    const response = await apiClient.post('/panel/auth', {
      server_id: parseInt(form.value.server_id),
      panel_password: form.value.panel_password
    })

    console.log('[DEBUG] Auth response:', response.data)

    if (response.data.success && response.data.token) {
      console.log('[DEBUG] Login successful! Saving to localStorage...')

      // Save panel token
      localStorage.setItem('panel_token', response.data.token)
      localStorage.setItem('panel_server_id', String(response.data.server_id))
      localStorage.setItem('panel_mode', 'true')

      console.log('[DEBUG] Saved to localStorage:', {
        panel_token: localStorage.getItem('panel_token'),
        panel_server_id: localStorage.getItem('panel_server_id'),
        panel_mode: localStorage.getItem('panel_mode')
      })

      // Small delay to ensure localStorage is saved
      await new Promise(resolve => setTimeout(resolve, 100))

      const targetUrl = `/servers/${response.data.server_id}/panel`
      console.log('[DEBUG] Redirecting to:', targetUrl)

      // Force navigation
      window.location.href = targetUrl
    } else {
      console.error('[DEBUG] Login failed:', response.data)
      error.value = response.data.message || 'Giriş başarısız'
    }
  } catch (err) {
    console.error('[DEBUG] Panel login error:', err)
    console.error('[DEBUG] Error response:', err.response)
    if (err.response?.status === 401) {
      error.value = 'Panel şifresi hatalı'
    } else if (err.response?.status === 404) {
      error.value = 'Sunucu bulunamadı'
    } else if (err.response?.status === 403) {
      error.value = err.response?.data?.detail || 'Panel erişimi aktif değil'
    } else {
      error.value = err.response?.data?.detail || err.message || 'Giriş başarısız oldu'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadServers()
})
</script>
