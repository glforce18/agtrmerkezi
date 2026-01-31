<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Config Editor</h2>
          <p class="text-gray-400 text-sm mt-1">server.cfg CVAR'larını görsel olarak düzenleyin</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="showBackupModal = true"
            class="btn-secondary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Yedekler
          </button>
          <button
            @click="resetChanges"
            v-if="hasChanges"
            class="btn-secondary"
            :disabled="saving"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Sıfırla
          </button>
          <button
            @click="saveChanges"
            v-if="hasChanges"
            class="btn-primary"
            :disabled="saving"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ saving ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet' }}
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam CVAR</div>
          <div class="text-2xl font-bold text-white mt-1">{{ totalCvars }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Kategoriler</div>
          <div class="text-2xl font-bold text-white mt-1">{{ Object.keys(categorized).length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Değiştirilen</div>
          <div class="text-2xl font-bold text-yellow-400 mt-1">{{ changesCount }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Yeniden Başlatma</div>
          <div class="text-2xl font-bold text-orange-400 mt-1">{{ hasChanges ? 'Gerekli' : 'Yok' }}</div>
        </div>
      </div>

      <!-- Warning banner -->
      <div v-if="hasChanges" class="mt-4 p-4 bg-orange-500/10 border border-orange-500/20 rounded-lg">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-orange-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div class="flex-1">
            <p class="text-orange-400 font-medium">Kaydedilmemiş değişiklikler var!</p>
            <p class="text-orange-300 text-sm mt-1">
              Değişikliklerin etkili olması için sunucuyu yeniden başlatmanız gerekecek.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Config Templates (Phase 2 Feature #14) -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
        </svg>
        Hazır Şablonlar
      </h3>
      <p class="text-gray-400 text-sm mb-4">Hızlı kurulum için hazır config şablonlarını kullanın</p>

      <div v-if="templates.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <button
          v-for="template in templates"
          :key="template.name"
          @click="applyTemplate(template)"
          :disabled="applyingTemplate"
          class="template-card p-4 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-purple-500/50 rounded-lg transition-all text-left"
        >
          <div class="flex items-start justify-between mb-2">
            <h4 class="text-white font-medium">{{ template.name }}</h4>
            <span class="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full">
              {{ Object.keys(template.cvars).length }} CVAR
            </span>
          </div>
          <p class="text-gray-400 text-sm">{{ template.description }}</p>
        </button>
      </div>

      <div v-else class="text-center py-8 text-gray-400">
        Bu oyun tipi için hazır şablon bulunamadı
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="glass-card p-6">
        <div class="animate-pulse space-y-4">
          <div class="h-6 bg-white/10 rounded w-1/4"></div>
          <div class="space-y-3">
            <div class="h-4 bg-white/5 rounded"></div>
            <div class="h-4 bg-white/5 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Categories -->
    <div v-else class="space-y-6">
      <div
        v-for="(category, key) in categorized"
        :key="key"
        class="glass-card p-6"
      >
        <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <component :is="getCategoryIcon(key)" class="w-6 h-6" :class="getCategoryColor(key)" />
          {{ category.name }}
          <span class="text-sm text-gray-400 font-normal">({{ category.cvars.length }})</span>
        </h3>

        <div class="space-y-3">
          <CvarEditor
            v-for="cvar in category.cvars"
            :key="cvar.name"
            :cvar="cvar"
            :value="modifiedCvars[cvar.name] !== undefined ? modifiedCvars[cvar.name] : cvar.value"
            :is-modified="modifiedCvars[cvar.name] !== undefined"
            @update="updateCvar"
          />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && totalCvars === 0" class="glass-card p-12 text-center">
      <svg class="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-400 mb-2">server.cfg bulunamadı veya boş</p>
      <p class="text-gray-500 text-sm">Sunucu dosyalarını kontrol edin</p>
    </div>

    <!-- Backup Modal -->
    <div v-if="showBackupModal" class="modal-overlay" @click.self="showBackupModal = false">
      <div class="modal-content max-w-4xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-white">Config Yedekleri</h3>
          <button @click="showBackupModal = false" class="text-gray-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex justify-between items-center mb-4">
          <p class="text-gray-400 text-sm">{{ backups.length }} yedek bulundu</p>
          <button @click="createBackup" :disabled="creatingBackup" class="btn-primary text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            {{ creatingBackup ? 'Oluşturuluyor...' : 'Yeni Yedek Oluştur' }}
          </button>
        </div>

        <div v-if="backups.length > 0" class="space-y-2 max-h-96 overflow-y-auto">
          <div
            v-for="backup in backups"
            :key="backup.filename"
            class="p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-all"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <p class="text-white font-medium text-sm">{{ formatBackupDate(backup.created_at) }}</p>
                <p class="text-gray-500 text-xs">{{ formatBytes(backup.size) }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="viewDiff(backup)"
                  class="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded text-xs"
                >
                  Fark Göster
                </button>
                <button
                  @click="restoreBackup(backup)"
                  class="px-3 py-1 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded text-xs"
                >
                  Geri Yükle
                </button>
                <button
                  @click="deleteBackup(backup)"
                  class="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded text-xs"
                >
                  Sil
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <p class="text-gray-400">Henüz yedek oluşturulmamış</p>
        </div>
      </div>
    </div>

    <!-- Diff Viewer Modal -->
    <div v-if="showDiffModal" class="modal-overlay" @click.self="showDiffModal = false">
      <div class="modal-content max-w-6xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-white">Config Farkları</h3>
          <button @click="showDiffModal = false" class="text-gray-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="diffLines.length > 0" class="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto font-mono text-sm">
          <div v-for="(line, i) in diffLines" :key="i"
            :class="[
              'leading-relaxed',
              line.startsWith('+') && !line.startsWith('+++') ? 'text-green-400 bg-green-500/10' :
              line.startsWith('-') && !line.startsWith('---') ? 'text-red-400 bg-red-500/10' :
              line.startsWith('@@') ? 'text-blue-400 font-bold' :
              'text-gray-400'
            ]"
          >{{ line }}</div>
        </div>

        <div v-else class="text-center py-12">
          <p class="text-gray-400">Fark bulunamadı</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import CvarEditor from '@/components/server/config/CvarEditor.vue'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)
const saving = ref(false)
const applyingTemplate = ref(false)
const creatingBackup = ref(false)

const originalCvars = ref({})
const categorized = ref({})
const modifiedCvars = ref({})
const templates = ref([])
const backups = ref([])
const showBackupModal = ref(false)
const showDiffModal = ref(false)
const diffLines = ref([])

const totalCvars = computed(() => Object.keys(originalCvars.value).length)
const changesCount = computed(() => Object.keys(modifiedCvars.value).length)
const hasChanges = computed(() => changesCount.value > 0)

const fetchConfig = async () => {
  loading.value = true
  try {
    const response = await api.getServerConfig(serverId.value)

    if (response.success) {
      originalCvars.value = response.data.cvars || {}
      categorized.value = response.data.categorized || {}
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Config yüklenirken hata oluştu', 'error')
  } finally {
    loading.value = false
  }
}

const updateCvar = (name, value) => {
  // Check if value changed from original
  if (value !== originalCvars.value[name]) {
    modifiedCvars.value[name] = value
  } else {
    // Remove from modified if reverted to original
    delete modifiedCvars.value[name]
  }
}

const resetChanges = () => {
  if (confirm('Tüm değişiklikleri geri almak istediğinizden emin misiniz?')) {
    modifiedCvars.value = {}
    toast.show('Değişiklikler sıfırlandı', 'info')
  }
}

const saveChanges = async () => {
  if (!hasChanges.value) return

  if (!confirm(`${changesCount.value} CVAR değiştirilecek. Devam etmek istiyor musunuz?\n\nNot: Değişikliklerin etkili olması için sunucuyu yeniden başlatmanız gerekecek.`)) {
    return
  }

  saving.value = true
  try {
    const response = await api.updateServerConfig(serverId.value, {
      cvars: modifiedCvars.value
    })

    if (response.success) {
      toast.show(response.message, 'success')

      // Update original cvars with modified values
      Object.assign(originalCvars.value, modifiedCvars.value)
      modifiedCvars.value = {}

      // Reload to reflect changes
      await fetchConfig()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Config kaydedilemedi', 'error')
  } finally {
    saving.value = false
  }
}

const getCategoryIcon = (category) => {
  const icons = {
    server: () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01' })
    ]),
    game: () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z' })
    ]),
    network: () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9' })
    ]),
    security: () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' })
    ]),
    other: () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4' })
    ])
  }
  return icons[category] || icons.other
}

const getCategoryColor = (category) => {
  const colors = {
    server: 'text-blue-400',
    game: 'text-green-400',
    network: 'text-purple-400',
    security: 'text-red-400',
    other: 'text-gray-400'
  }
  return colors[category] || 'text-gray-400'
}

const fetchTemplates = async () => {
  try {
    const response = await api.getConfigTemplates(serverId.value)
    if (response.success) {
      templates.value = response.data?.templates || []
    }
  } catch (error) {
    console.error('Templates yüklenemedi:', error)
  }
}

const applyTemplate = async (template) => {
  if (hasChanges.value) {
    if (!confirm('Kaydedilmemiş değişiklikler var. Template uygulanırsa kaybolacak. Devam edilsin mi?')) {
      return
    }
  }

  if (!confirm(`"${template.name}" template uygulanacak.\n${Object.keys(template.cvars).length} CVAR değiştirilecek.\n\nDevam edilsin mi?`)) {
    return
  }

  applyingTemplate.value = true
  try {
    const response = await api.applyConfigTemplate(serverId.value, {
      template_name: template.name
    })

    if (response.success) {
      toast.show(response.message, 'success')
      modifiedCvars.value = {}
      await fetchConfig()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Template uygulanamadı', 'error')
  } finally {
    applyingTemplate.value = false
  }
}

const fetchBackups = async () => {
  try {
    const response = await api.getConfigBackups(serverId.value)
    if (response.success) {
      backups.value = response.data.backups
    }
  } catch (error) {
    console.error('Backups yüklenemedi:', error)
  }
}

const createBackup = async () => {
  creatingBackup.value = true
  try {
    const response = await api.createConfigBackup(serverId.value)
    if (response.success) {
      toast.show(response.message, 'success')
      await fetchBackups()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Yedek oluşturulamadı', 'error')
  } finally {
    creatingBackup.value = false
  }
}

const viewDiff = async (backup) => {
  try {
    const response = await api.getConfigDiff(serverId.value, backup.filename)
    if (response.success) {
      diffLines.value = response.data.diff
      showDiffModal.value = true
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Fark gösterilemedi', 'error')
  }
}

const restoreBackup = async (backup) => {
  if (!confirm(`${formatBackupDate(backup.created_at)} tarihli yedek geri yüklenecek.\n\nMevcut config üzerine yazılacak. Devam edilsin mi?`)) {
    return
  }

  try {
    const response = await api.restoreConfigBackup(serverId.value, backup.filename)
    if (response.success) {
      toast.show(response.message, 'success')
      showBackupModal.value = false
      await fetchConfig()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Geri yükleme başarısız', 'error')
  }
}

const deleteBackup = async (backup) => {
  if (!confirm(`${formatBackupDate(backup.created_at)} tarihli yedek silinecek. Emin misiniz?`)) {
    return
  }

  try {
    const response = await api.deleteConfigBackup(serverId.value, backup.filename)
    if (response.success) {
      toast.show(response.message, 'success')
      await fetchBackups()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Yedek silinemedi', 'error')
  }
}

const formatBackupDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('tr-TR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Watch showBackupModal to fetch backups when opened
const watchBackupModal = () => {
  if (showBackupModal.value) {
    fetchBackups()
  }
}

onMounted(() => {
  fetchConfig()
  fetchTemplates()
})

// Add watcher for backup modal
import { watch } from 'vue'
watch(showBackupModal, watchBackupModal)
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-primary {
  @apply px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl flex items-center gap-2;
}

.btn-secondary {
  @apply px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-all flex items-center gap-2;
}

.modal-overlay {
  @apply fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4;
}

.modal-content {
  @apply bg-gradient-to-br from-gray-900 to-gray-800 border border-white/20 rounded-xl p-6 w-full shadow-2xl;
}
</style>
