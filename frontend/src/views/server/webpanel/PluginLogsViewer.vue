<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Plugin Logs</h2>
          <p class="text-gray-400 text-sm mt-1">AMXModX plugin loglarını görüntüleyin</p>
        </div>
        <button
          @click="refreshLogs"
          :disabled="loading"
          class="btn-primary"
        >
          <svg class="w-5 h-5" :class="loading ? 'animate-spin' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Yenile
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Log</div>
          <div class="text-2xl font-bold text-white mt-1">{{ logFiles.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Seçili Dosya</div>
          <div class="text-lg font-bold text-blue-400 mt-1 truncate">{{ selectedLog || 'Yok' }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Satır</div>
          <div class="text-2xl font-bold text-purple-400 mt-1">{{ totalLines }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Gösterilen</div>
          <div class="text-2xl font-bold text-green-400 mt-1">{{ filteredLines }}</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div v-if="selectedLog" class="glass-card p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-gray-300 mb-2 text-sm">Seviye Filtresi</label>
          <select v-model="levelFilter" @change="loadLogContent" class="input-text w-full">
            <option value="">Tümü</option>
            <option value="error">Sadece Hatalar</option>
            <option value="warning">Sadece Uyarılar</option>
            <option value="info">Sadece Bilgi</option>
          </select>
        </div>
        <div>
          <label class="block text-gray-300 mb-2 text-sm">Satır Sayısı</label>
          <select v-model="lineLimit" @change="loadLogContent" class="input-text w-full">
            <option :value="100">Son 100 satır</option>
            <option :value="500">Son 500 satır</option>
            <option :value="1000">Son 1000 satır</option>
            <option :value="5000">Son 5000 satır</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <label class="block text-gray-300 mb-2 text-sm">Ara</label>
          <input
            v-model="searchTerm"
            @input="debouncedSearch"
            type="text"
            placeholder="Log içinde ara..."
            class="input-text w-full"
          />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Log Files List -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Log Dosyaları
        </h3>

        <div v-if="loading" class="space-y-2">
          <div v-for="i in 5" :key="i" class="animate-pulse bg-white/5 rounded-lg h-16"></div>
        </div>

        <div v-else-if="logFiles.length > 0" class="space-y-2">
          <div
            v-for="log in logFiles"
            :key="log.name"
            :class="[
              'p-3 rounded-lg transition-all',
              selectedLog === log.name
                ? 'bg-blue-500/20 border-blue-500/50 border'
                : 'bg-white/5 hover:bg-white/10'
            ]"
          >
            <button
              @click="loadLogFile(log.name)"
              class="w-full text-left"
            >
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div class="flex-1 min-w-0">
                  <p class="text-white font-medium text-sm truncate">{{ log.name }}</p>
                  <p class="text-gray-500 text-xs">{{ formatBytes(log.size) }}</p>
                </div>
              </div>
            </button>
            <button
              @click="deleteLog(log.name)"
              class="mt-2 w-full text-xs px-2 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded transition-colors"
            >
              Sil
            </button>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <svg class="w-12 h-12 text-gray-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-400">Log dosyası yok</p>
        </div>
      </div>

      <!-- Log Viewer -->
      <div class="lg:col-span-3 glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {{ selectedLog || 'Log Görüntüleyici' }}
        </h3>

        <div v-if="!selectedLog" class="text-center py-16">
          <svg class="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-400">Sol taraftan bir log dosyası seçin</p>
        </div>

        <div v-else-if="loadingLog" class="space-y-2">
          <div v-for="i in 10" :key="i" class="animate-pulse bg-white/5 rounded-lg h-6"></div>
        </div>

        <div v-else-if="logEntries.length > 0" class="space-y-1 max-h-[700px] overflow-y-auto">
          <div
            v-for="(entry, i) in logEntries"
            :key="i"
            :class="[
              'p-2 rounded text-sm font-mono',
              entry.level === 'error' ? 'bg-red-500/10 border-l-4 border-red-500' :
              entry.level === 'warning' ? 'bg-orange-500/10 border-l-4 border-orange-500' :
              'bg-white/5'
            ]"
          >
            <div class="flex items-start gap-3">
              <!-- Timestamp -->
              <span v-if="entry.timestamp" class="text-gray-500 text-xs flex-shrink-0">
                {{ formatTimestamp(entry.timestamp) }}
              </span>

              <!-- Level Badge -->
              <span
                :class="[
                  'px-2 py-0.5 rounded text-xs font-semibold flex-shrink-0',
                  entry.level === 'error' ? 'bg-red-500/20 text-red-400' :
                  entry.level === 'warning' ? 'bg-orange-500/20 text-orange-400' :
                  'bg-blue-500/20 text-blue-400'
                ]"
              >
                {{ entry.level.toUpperCase() }}
              </span>

              <!-- Module -->
              <span v-if="entry.module" class="text-purple-400 text-xs flex-shrink-0">
                [{{ entry.module }}]
              </span>

              <!-- Message -->
              <span class="text-gray-300 flex-1 break-words">{{ entry.message }}</span>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <p class="text-gray-400">Gösterilecek log kaydı yok</p>
          <p class="text-gray-500 text-sm mt-2">Filtrelerinizi kontrol edin</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)
const loadingLog = ref(false)

const logFiles = ref([])
const selectedLog = ref(null)
const logEntries = ref([])
const totalLines = ref(0)
const filteredLines = ref(0)

const levelFilter = ref('')
const lineLimit = ref(500)
const searchTerm = ref('')
let searchTimeout = null

const fetchLogFiles = async () => {
  loading.value = true
  try {
    const response = await api.listPluginLogs(serverId.value)
    if (response.success) {
      logFiles.value = response.data.logs
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Log listesi yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const loadLogFile = async (filename) => {
  selectedLog.value = filename
  await loadLogContent()
}

const loadLogContent = async () => {
  if (!selectedLog.value) return

  loadingLog.value = true
  try {
    const response = await api.getPluginLog(serverId.value, selectedLog.value, {
      lines: lineLimit.value,
      level: levelFilter.value || undefined,
      search: searchTerm.value || undefined
    })

    if (response.success) {
      logEntries.value = response.data.entries
      totalLines.value = response.data.total_lines
      filteredLines.value = response.data.filtered_lines
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Log yüklenemedi', 'error')
  } finally {
    loadingLog.value = false
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadLogContent()
  }, 500)
}

const deleteLog = async (filename) => {
  if (!confirm(`"${filename}" log dosyasını silmek istediğinizden emin misiniz?`)) return

  try {
    const response = await api.deletePluginLog(serverId.value, filename)
    if (response.success) {
      toast.show(response.message, 'success')

      if (selectedLog.value === filename) {
        selectedLog.value = null
        logEntries.value = []
        totalLines.value = 0
        filteredLines.value = 0
      }

      await fetchLogFiles()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Log silinemedi', 'error')
  }
}

const refreshLogs = async () => {
  await fetchLogFiles()
  if (selectedLog.value) {
    await loadLogContent()
  }
  toast.show('Loglar yenilendi', 'success')
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(() => {
  fetchLogFiles()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-primary {
  @apply px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.input-text {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all text-sm;
}
</style>
