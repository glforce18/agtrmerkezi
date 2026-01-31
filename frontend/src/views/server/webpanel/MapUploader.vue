<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Custom Map Uploader</h2>
          <p class="text-gray-400 text-sm mt-1">Upload .bsp map files to your server</p>
        </div>
        <button
          @click="showUploadModal = true"
          class="btn-primary"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload Map
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Total Maps</div>
          <div class="text-2xl font-bold text-white mt-1">{{ customMaps.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Total Size</div>
          <div class="text-2xl font-bold text-blue-400 mt-1">{{ totalSize }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Storage Used</div>
          <div class="text-2xl font-bold text-green-400 mt-1">{{ storagePercent }}%</div>
        </div>
      </div>
    </div>

    <!-- Maps List -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-bold text-white mb-4">Uploaded Maps</h3>

      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="customMaps.length === 0" class="py-12 text-center text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <p class="text-lg">Henüz custom map yüklenmemiş</p>
        <p class="text-sm text-gray-600 mt-2">Upload butonuna tıklayarak .bsp dosyası yükleyebilirsiniz</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="map in customMaps"
          :key="map.id"
          class="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors"
        >
          <!-- Map Icon -->
          <div class="w-full h-32 bg-gray-900 rounded-lg mb-3 flex items-center justify-center">
            <svg class="w-16 h-16 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>

          <!-- Map Info -->
          <div class="mb-3">
            <h4 class="text-white font-bold truncate">{{ map.display_name }}</h4>
            <p class="text-gray-500 text-sm font-mono truncate">{{ map.map_name }}.bsp</p>
            <p v-if="map.description" class="text-gray-400 text-xs mt-1 line-clamp-2">{{ map.description }}</p>
          </div>

          <!-- Meta -->
          <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
            <span v-if="map.author">By {{ map.author }}</span>
            <span>{{ formatBytes(map.file_size) }}</span>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button
              @click="viewMapDetails(map)"
              class="flex-1 px-3 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg text-sm transition-colors"
            >
              Details
            </button>
            <button
              @click="deleteMap(map)"
              class="px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div
      v-if="showUploadModal"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      @click.self="showUploadModal = false"
    >
      <div class="glass-card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto" @click.stop>
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-white">Upload Custom Map</h3>
          <button
            @click="showUploadModal = false"
            class="text-gray-400 hover:text-white"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="uploadMap" class="space-y-4">
          <!-- File Upload -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Map File (.bsp)</label>
            <div
              class="border-2 border-dashed border-white/20 rounded-lg p-8 text-center hover:border-blue-500/50 transition-colors cursor-pointer"
              @click="$refs.fileInput.click()"
              @dragover.prevent="dragOver = true"
              @dragleave.prevent="dragOver = false"
              @drop.prevent="handleDrop"
              :class="{ 'border-blue-500 bg-blue-500/10': dragOver }"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".bsp"
                @change="handleFileSelect"
                class="hidden"
              />
              <svg class="w-12 h-12 mx-auto mb-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p v-if="!selectedFile" class="text-gray-400">Click or drag .bsp file here</p>
              <p v-else class="text-white font-medium">{{ selectedFile.name }}</p>
              <p v-if="selectedFile" class="text-gray-500 text-sm mt-1">{{ formatBytes(selectedFile.size) }}</p>
            </div>
          </div>

          <!-- Map Name -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Map Name (without .bsp)</label>
            <input
              v-model="uploadForm.mapName"
              type="text"
              required
              placeholder="de_dust2"
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            />
          </div>

          <!-- Display Name -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Display Name (Optional)</label>
            <input
              v-model="uploadForm.displayName"
              type="text"
              placeholder="Dust 2"
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            />
          </div>

          <!-- Author -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Author (Optional)</label>
            <input
              v-model="uploadForm.author"
              type="text"
              placeholder="Map creator name"
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Description (Optional)</label>
            <textarea
              v-model="uploadForm.description"
              rows="3"
              placeholder="Map description..."
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
            ></textarea>
          </div>

          <!-- Warning -->
          <div class="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3">
            <div class="flex items-start gap-2">
              <svg class="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div class="text-orange-400 text-sm">
                <p class="font-medium">Important Notes:</p>
                <ul class="list-disc ml-4 mt-1 space-y-1">
                  <li>Max file size: 50 MB</li>
                  <li>Only .bsp format supported</li>
                  <li>Map name must be unique</li>
                  <li>Server restart may be required</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="showUploadModal = false"
              class="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="uploading || !selectedFile"
              class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ uploading ? 'Uploading...' : 'Upload Map' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Map Details Modal -->
    <div
      v-if="selectedMap"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      @click.self="selectedMap = null"
    >
      <div class="glass-card p-6 max-w-lg w-full" @click.stop>
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-white">Map Details</h3>
          <button
            @click="selectedMap = null"
            class="text-gray-400 hover:text-white"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <div class="text-gray-400 text-sm">Map Name</div>
            <div class="text-white font-mono">{{ selectedMap.map_name }}.bsp</div>
          </div>
          <div>
            <div class="text-gray-400 text-sm">Display Name</div>
            <div class="text-white">{{ selectedMap.display_name }}</div>
          </div>
          <div v-if="selectedMap.author">
            <div class="text-gray-400 text-sm">Author</div>
            <div class="text-white">{{ selectedMap.author }}</div>
          </div>
          <div v-if="selectedMap.description">
            <div class="text-gray-400 text-sm">Description</div>
            <div class="text-white">{{ selectedMap.description }}</div>
          </div>
          <div>
            <div class="text-gray-400 text-sm">File Size</div>
            <div class="text-white">{{ formatBytes(selectedMap.file_size) }}</div>
          </div>
          <div>
            <div class="text-gray-400 text-sm">Uploaded At</div>
            <div class="text-white">{{ formatDate(selectedMap.uploaded_at) }}</div>
          </div>
          <div>
            <div class="text-gray-400 text-sm">File Hash (SHA256)</div>
            <div class="text-white font-mono text-xs break-all">{{ selectedMap.file_hash }}</div>
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
const uploading = ref(false)
const dragOver = ref(false)
const showUploadModal = ref(false)
const selectedFile = ref(null)
const selectedMap = ref(null)
const customMaps = ref([])

const uploadForm = ref({
  mapName: '',
  displayName: '',
  author: '',
  description: ''
})

const totalSize = computed(() => {
  const bytes = customMaps.value.reduce((sum, map) => sum + (map.file_size || 0), 0)
  return formatBytes(bytes)
})

const storagePercent = computed(() => {
  const bytes = customMaps.value.reduce((sum, map) => sum + (map.file_size || 0), 0)
  const maxBytes = 500 * 1024 * 1024 // 500 MB max
  return Math.min(100, Math.round((bytes / maxBytes) * 100))
})

const fetchCustomMaps = async () => {
  loading.value = true
  try {
    const response = await api.getCustomMaps(serverId.value)
    if (response.success) {
      customMaps.value = response.data.maps
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Maps yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.name.endsWith('.bsp')) {
    selectedFile.value = file
    // Auto-fill map name from filename
    uploadForm.value.mapName = file.name.replace('.bsp', '')
  } else {
    toast.show('Sadece .bsp dosyaları seçebilirsiniz', 'error')
  }
}

const handleDrop = (event) => {
  dragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.name.endsWith('.bsp')) {
    selectedFile.value = file
    uploadForm.value.mapName = file.name.replace('.bsp', '')
  } else {
    toast.show('Sadece .bsp dosyaları yükleyebilirsiniz', 'error')
  }
}

const uploadMap = async () => {
  if (!selectedFile.value) {
    toast.show('Lütfen bir dosya seçin', 'error')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('map_name', uploadForm.value.mapName)
    if (uploadForm.value.displayName) {
      formData.append('display_name', uploadForm.value.displayName)
    }
    if (uploadForm.value.author) {
      formData.append('author', uploadForm.value.author)
    }
    if (uploadForm.value.description) {
      formData.append('description', uploadForm.value.description)
    }

    const response = await api.uploadCustomMap(serverId.value, formData)
    if (response.success) {
      toast.show('Map yüklendi', 'success')
      showUploadModal.value = false
      selectedFile.value = null
      uploadForm.value = { mapName: '', displayName: '', author: '', description: '' }
      await fetchCustomMaps()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Map yüklenemedi', 'error')
  } finally {
    uploading.value = false
  }
}

const deleteMap = async (map) => {
  if (!confirm(`"${map.display_name}" haritasını silmek istediğinizden emin misiniz?`)) return

  try {
    const response = await api.deleteCustomMap(serverId.value, map.id)
    if (response.success) {
      toast.show('Map silindi', 'success')
      await fetchCustomMaps()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Map silinemedi', 'error')
  }
}

const viewMapDetails = (map) => {
  selectedMap.value = map
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleString('tr-TR')
}

onMounted(async () => {
  await fetchCustomMaps()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-primary {
  @apply px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl flex items-center gap-2;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
