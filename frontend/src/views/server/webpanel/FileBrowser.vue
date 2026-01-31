<template>
  <div class="space-y-6">
    <!-- Header with breadcrumb -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Dosya Tarayıcı</h2>
          <p class="text-gray-400 text-sm mt-1">Sunucu dosyalarını görüntüleyin ve yönetin</p>
        </div>
      </div>

      <!-- Breadcrumb -->
      <div class="flex items-center gap-2 text-sm">
        <button
          @click="navigateTo('')"
          class="text-blue-400 hover:text-blue-300 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </button>
        <template v-if="currentPath">
          <template v-for="(part, index) in pathParts" :key="index">
            <span class="text-gray-500">/</span>
            <button
              @click="navigateTo(pathParts.slice(0, index + 1).join('/'))"
              class="text-blue-400 hover:text-blue-300 transition-colors"
            >
              {{ part }}
            </button>
          </template>
        </template>
        <span v-else class="text-gray-500">/ (root)</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="glass-card p-12 text-center">
      <div class="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
      <p class="text-gray-400 mt-4">Yükleniyor...</p>
    </div>

    <!-- File list -->
    <div v-else class="glass-card p-6">
      <!-- Parent directory button -->
      <button
        v-if="parentPath !== null"
        @click="navigateTo(parentPath)"
        class="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors mb-2"
      >
        <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span class="text-gray-300">..</span>
      </button>

      <!-- Files and directories -->
      <div class="space-y-1">
        <div
          v-for="item in sortedItems"
          :key="item.path"
          @click="handleItemClick(item)"
          class="file-item flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-all cursor-pointer group"
        >
          <!-- Icon -->
          <div class="flex-shrink-0">
            <!-- Directory icon -->
            <svg
              v-if="item.type === 'directory'"
              class="w-6 h-6 text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            <!-- File icon -->
            <svg
              v-else
              class="w-6 h-6 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>

          <!-- Name and details -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <p class="text-white font-medium truncate">{{ item.name }}</p>
              <span
                v-if="item.is_symlink"
                class="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded-full"
              >
                Symlink
              </span>
            </div>
            <div class="flex items-center gap-4 text-xs text-gray-400 mt-1">
              <span v-if="item.type === 'file'">{{ formatSize(item.size) }}</span>
              <span>{{ formatDate(item.modified) }}</span>
            </div>
          </div>

          <!-- Chevron for directories -->
          <svg
            v-if="item.type === 'directory'"
            class="w-5 h-5 text-gray-500 group-hover:text-gray-300 transition-colors flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="files.length === 0" class="text-center py-12">
        <svg class="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <p class="text-gray-400">Bu dizin boş</p>
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

const files = ref([])
const currentPath = ref('')
const parentPath = ref(null)

const pathParts = computed(() => {
  return currentPath.value ? currentPath.value.split('/').filter(p => p) : []
})

const sortedItems = computed(() => {
  // Directories first, then files, alphabetically
  return [...files.value].sort((a, b) => {
    if (a.type === b.type) {
      return a.name.localeCompare(b.name)
    }
    return a.type === 'directory' ? -1 : 1
  })
})

const fetchFiles = async (path = '') => {
  loading.value = true
  try {
    const response = await api.browseFiles(serverId.value, path)

    if (response.success) {
      files.value = response.data.files || []
      currentPath.value = response.data.current_path || ''
      parentPath.value = response.data.parent_path
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Dosyalar yüklenirken hata oluştu', 'error')
  } finally {
    loading.value = false
  }
}

const navigateTo = (path) => {
  fetchFiles(path)
}

const handleItemClick = (item) => {
  if (item.type === 'directory') {
    navigateTo(item.path)
  } else {
    // For now, just show a message
    toast.show(`Dosya: ${item.name}`, 'info')
  }
}

const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(2)} MB`
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchFiles()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.file-item {
  transition: all 0.2s ease;
}
</style>
