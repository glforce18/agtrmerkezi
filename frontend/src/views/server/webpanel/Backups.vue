<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Sunucu Yedekleri</h2>
          <p class="text-gray-400 text-sm mt-1">Yedeklerinizi oluşturun, geri yükleyin veya silin</p>
        </div>
        <button
          @click="showCreateModal = true"
          class="btn-primary"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Yeni Yedek Oluştur
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Yedek</div>
          <div class="text-2xl font-bold text-white mt-1">{{ backups.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Config Yedekleri</div>
          <div class="text-2xl font-bold text-blue-400 mt-1">{{ configBackups.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Full Yedekler</div>
          <div class="text-2xl font-bold text-green-400 mt-1">{{ fullBackups.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Boyut</div>
          <div class="text-2xl font-bold text-purple-400 mt-1">{{ formatBytes(totalSize) }}</div>
        </div>
      </div>
    </div>

    <!-- Backup Schedule Info -->
    <div v-if="schedule" class="glass-card p-6">
      <div class="flex items-start gap-3">
        <svg class="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <h3 class="text-lg font-bold text-white mb-2">Otomatik Yedekleme Planı</h3>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="bg-white/5 rounded-lg p-3">
              <p class="text-gray-400">Config Yedekleme</p>
              <p class="text-white font-medium mt-1">{{ schedule.config_backup.interval }} - {{ schedule.config_backup.time }}</p>
              <p class="text-gray-500 text-xs mt-1">{{ schedule.config_backup.retention_days }} gün saklanır</p>
            </div>
            <div class="bg-white/5 rounded-lg p-3">
              <p class="text-gray-400">Full Yedekleme</p>
              <p class="text-white font-medium mt-1">{{ schedule.full_backup.interval }} ({{ schedule.full_backup.day }}) - {{ schedule.full_backup.time }}</p>
              <p class="text-gray-500 text-xs mt-1">{{ schedule.full_backup.retention_days }} gün saklanır</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter -->
    <div class="glass-card p-4">
      <div class="flex items-center gap-3">
        <span class="text-gray-400 text-sm">Filtre:</span>
        <button
          v-for="type in ['all', 'config', 'full']"
          :key="type"
          @click="selectedType = type"
          :class="selectedType === type ? 'badge-active' : 'badge'"
        >
          {{ type === 'all' ? 'Tümü' : type === 'config' ? 'Config' : 'Full' }}
        </button>
      </div>
    </div>

    <!-- Backups List -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
        Yedekler ({{ filteredBackups.length }})
      </h3>

      <div v-if="loading" class="space-y-2">
        <div v-for="i in 3" :key="i" class="animate-pulse bg-white/5 rounded-lg h-20"></div>
      </div>

      <div v-else-if="filteredBackups.length > 0" class="space-y-2">
        <div
          v-for="backup in filteredBackups"
          :key="backup.filename"
          class="bg-white/5 hover:bg-white/10 rounded-lg p-4 transition-all group"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <span :class="getBackupTypeClass(backup.type)">
                  {{ getBackupTypeLabel(backup.type) }}
                </span>
                <p class="text-white font-medium">{{ backup.filename }}</p>
              </div>
              <div class="flex items-center gap-4 mt-2 text-sm">
                <span class="text-gray-400 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ formatDate(backup.created_at) }}
                </span>
                <span class="text-gray-400 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  {{ formatBytes(backup.size) }}
                </span>
              </div>
            </div>

            <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                @click="openRestoreModal(backup)"
                class="btn-action btn-restore"
                title="Geri yükle"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Geri Yükle
              </button>
              <button
                @click="deleteBackupHandler(backup)"
                class="btn-action btn-delete"
                title="Sil"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Sil
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12">
        <svg class="w-12 h-12 text-gray-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
        <p class="text-gray-400">Henüz yedek yok</p>
      </div>
    </div>

    <!-- Create Backup Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-white">Yeni Yedek Oluştur</h3>
          <button @click="showCreateModal = false" class="text-gray-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-gray-300 mb-2">Yedek Tipi</label>
            <select v-model="createBackupType" class="input-text w-full">
              <option value="config">Config Yedek (Hızlı - Sadece ayar dosyaları)</option>
              <option value="full">Full Yedek (Yavaş - Tüm dosyalar)</option>
            </select>
          </div>

          <div class="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
            <p class="text-blue-400 text-sm flex items-start gap-2">
              <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                <strong>{{ createBackupType === 'config' ? 'Config Yedek' : 'Full Yedek' }}:</strong>
                {{ createBackupType === 'config'
                  ? 'server.cfg, mapcycle.txt, users.ini, plugins.ini gibi ayar dosyalarını yedekler. Hızlı ve küçük boyutludur.'
                  : 'Tüm sunucu dosyalarını (mapsler, modeller, sesler, pluginler) yedekler. Yavaş ve büyük boyutludur.'
                }}
              </span>
            </p>
          </div>

          <div class="flex gap-3 justify-end">
            <button @click="showCreateModal = false" class="btn-secondary">İptal</button>
            <button
              @click="createBackupHandler"
              :disabled="creating"
              class="btn-primary"
            >
              {{ creating ? 'Oluşturuluyor...' : 'Yedek Oluştur' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Restore Backup Modal -->
    <div v-if="showRestoreModal" class="modal-overlay" @click.self="showRestoreModal = false">
      <div class="modal-content">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-white">Yedek Geri Yükle</h3>
          <button @click="showRestoreModal = false" class="text-gray-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div class="bg-orange-500/10 border border-orange-500/20 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <svg class="w-6 h-6 text-orange-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <p class="text-orange-400 font-medium mb-1">DİKKAT!</p>
                <p class="text-orange-300 text-sm">Bu işlem mevcut dosyaları yedeğinizle değiştirecektir. Sunucunuzun çalışmadığından emin olun.</p>
              </div>
            </div>
          </div>

          <div v-if="selectedBackup" class="bg-white/5 rounded-lg p-4">
            <p class="text-gray-400 text-sm mb-2">Geri yüklenecek yedek:</p>
            <p class="text-white font-medium">{{ selectedBackup.filename }}</p>
            <p class="text-gray-400 text-sm mt-2">{{ formatDate(selectedBackup.created_at) }} - {{ formatBytes(selectedBackup.size) }}</p>
          </div>

          <div class="flex gap-3 justify-end">
            <button @click="showRestoreModal = false" class="btn-secondary">İptal</button>
            <button
              @click="restoreBackupHandler"
              :disabled="restoring"
              class="btn-danger"
            >
              {{ restoring ? 'Geri Yükleniyor...' : 'Geri Yükle' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)
const creating = ref(false)
const restoring = ref(false)

const backups = ref([])
const schedule = ref(null)
const selectedType = ref('all')

const showCreateModal = ref(false)
const showRestoreModal = ref(false)
const createBackupType = ref('config')
const selectedBackup = ref(null)

const configBackups = computed(() => backups.value.filter(b => b.type === 'config'))
const fullBackups = computed(() => backups.value.filter(b => b.type === 'full'))
const totalSize = computed(() => backups.value.reduce((sum, b) => sum + b.size, 0))

const filteredBackups = computed(() => {
  if (selectedType.value === 'all') return backups.value
  return backups.value.filter(b => b.type === selectedType.value)
})

const fetchBackups = async () => {
  loading.value = true
  try {
    const response = await api.getBackups(serverId.value)
    if (response.success) {
      backups.value = response.data?.backups || []
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Yedekler yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const fetchSchedule = async () => {
  try {
    const response = await api.getBackupSchedule(serverId.value)
    if (response.success) {
      schedule.value = response.data?.schedule || null
    }
  } catch (error) {
    console.error('Schedule yüklenemedi:', error)
  }
}

const createBackupHandler = async () => {
  creating.value = true
  try {
    const response = await api.createBackup(serverId.value, createBackupType.value)
    if (response.success) {
      toast.show(response.message, 'success')
      showCreateModal.value = false
      await fetchBackups()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Yedek oluşturulamadı', 'error')
  } finally {
    creating.value = false
  }
}

const openRestoreModal = (backup) => {
  selectedBackup.value = backup
  showRestoreModal.value = true
}

const restoreBackupHandler = async () => {
  if (!selectedBackup.value) return

  restoring.value = true
  try {
    const response = await api.restoreBackup(serverId.value, selectedBackup.value.filename)
    if (response.success) {
      toast.show(response.message, 'success')
      showRestoreModal.value = false
      selectedBackup.value = null
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Yedek geri yüklenemedi', 'error')
  } finally {
    restoring.value = false
  }
}

const deleteBackupHandler = async (backup) => {
  if (!confirm(`"${backup.filename}" yedegini silmek istediğinizden emin misiniz?`)) return

  try {
    const response = await api.deleteBackup(serverId.value, backup.filename)
    if (response.success) {
      toast.show(response.message, 'success')
      await fetchBackups()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Yedek silinemedi', 'error')
  }
}

const getBackupTypeClass = (type) => {
  const classes = {
    config: 'badge badge-blue',
    full: 'badge badge-green',
    database: 'badge badge-purple'
  }
  return classes[type] || 'badge'
}

const getBackupTypeLabel = (type) => {
  const labels = {
    config: 'Config',
    full: 'Full',
    database: 'Database'
  }
  return labels[type] || type
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('tr-TR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchBackups()
  fetchSchedule()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-primary {
  @apply px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-all;
}

.btn-danger {
  @apply px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-action {
  @apply px-3 py-2 rounded-lg transition-all flex items-center gap-2 text-sm;
}

.btn-restore {
  @apply bg-blue-500/20 hover:bg-blue-500/30 text-blue-400;
}

.btn-delete {
  @apply bg-red-500/20 hover:bg-red-500/30 text-red-400;
}

.badge {
  @apply px-2 py-1 text-xs font-medium rounded-full;
}

.badge-active {
  @apply badge bg-blue-500/20 text-blue-400 border border-blue-500/50;
}

.badge-blue {
  @apply bg-blue-500/20 text-blue-400;
}

.badge-green {
  @apply bg-green-500/20 text-green-400;
}

.badge-purple {
  @apply bg-purple-500/20 text-purple-400;
}

.input-text {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all;
}

.modal-overlay {
  @apply fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4;
}

.modal-content {
  @apply bg-gradient-to-br from-gray-900 to-gray-800 border border-white/20 rounded-xl p-6 max-w-lg w-full shadow-2xl;
}
</style>
