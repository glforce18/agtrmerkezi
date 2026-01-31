<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Map Kütüphanesi</h2>
          <p class="text-gray-400 text-sm mt-1">Tüm mevcut mapları görüntüleyin ve yönetin</p>
        </div>
        <router-link
          :to="{ name: 'server-webpanel-mapcycle' }"
          class="btn-primary"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Mapcycle Düzenle
        </router-link>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Map</div>
          <div class="text-2xl font-bold text-white mt-1">{{ stats.total }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Base Maps</div>
          <div class="text-2xl font-bold text-blue-400 mt-1">{{ stats.base_count }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Custom Maps</div>
          <div class="text-2xl font-bold text-green-400 mt-1">{{ stats.custom_count }}</div>
        </div>
      </div>
    </div>

    <!-- Search and filter -->
    <div class="glass-card p-4">
      <div class="flex gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Map ara..."
            class="input-text w-full"
          />
        </div>
        <select v-model="filterType" class="input-text">
          <option value="all">Tümü</option>
          <option value="base">Base Maps</option>
          <option value="custom">Custom Maps</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="glass-card p-4">
        <div class="animate-pulse space-y-3">
          <div class="h-32 bg-white/10 rounded"></div>
          <div class="h-4 bg-white/10 rounded w-3/4"></div>
          <div class="h-3 bg-white/10 rounded w-1/2"></div>
        </div>
      </div>
    </div>

    <!-- Map grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="map in filteredMaps"
        :key="map.name"
        class="glass-card p-4 hover:shadow-xl transition-all group"
      >
        <!-- Thumbnail placeholder -->
        <div class="aspect-video bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
          <img
            v-if="map.thumbnail_url"
            :src="map.thumbnail_url"
            :alt="map.name"
            class="w-full h-full object-cover"
          />
          <div v-else class="text-center">
            <svg class="w-12 h-12 text-gray-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <p class="text-gray-500 text-xs">No preview</p>
          </div>
        </div>

        <!-- Map info -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="text-white font-medium truncate">{{ map.display_name || map.name }}</h3>
            <span
              :class="[
                'px-2 py-0.5 text-xs rounded-full',
                map.is_custom
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-blue-500/20 text-blue-400'
              ]"
            >
              {{ map.is_custom ? 'Custom' : 'Base' }}
            </span>
          </div>

          <div class="flex items-center gap-2 text-xs text-gray-400">
            <code class="px-2 py-1 bg-white/5 rounded font-mono">{{ map.name }}.bsp</code>
            <span v-if="map.is_symlink" class="px-2 py-1 bg-purple-500/20 text-purple-400 rounded">
              Symlink
            </span>
          </div>

          <div v-if="map.description" class="text-sm text-gray-400 line-clamp-2">
            {{ map.description }}
          </div>

          <div class="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-white/10">
            <span>{{ formatSize(map.file_size) }}</span>
            <span v-if="map.author">{{ map.author }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && filteredMaps.length === 0" class="glass-card p-12 text-center">
      <svg class="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
      <p class="text-gray-400">{{ searchQuery ? 'Map bulunamadı' : 'Henüz map yüklenmemiş' }}</p>
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

const maps = ref([])
const stats = ref({ total: 0, base_count: 0, custom_count: 0 })

const searchQuery = ref('')
const filterType = ref('all')

const filteredMaps = computed(() => {
  let filtered = maps.value

  // Filter by type
  if (filterType.value !== 'all') {
    filtered = filtered.filter(m =>
      filterType.value === 'custom' ? m.is_custom : !m.is_custom
    )
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(m =>
      m.name.toLowerCase().includes(query) ||
      (m.display_name && m.display_name.toLowerCase().includes(query))
    )
  }

  return filtered
})

const fetchMaps = async () => {
  loading.value = true
  try {
    const response = await api.getMapLibrary(serverId.value)

    if (response.success) {
      maps.value = response.data.maps || []
      stats.value = {
        total: response.data.total || 0,
        base_count: response.data.base_count || 0,
        custom_count: response.data.custom_count || 0
      }
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Mapler yüklenirken hata oluştu', 'error')
  } finally {
    loading.value = false
  }
}

const formatSize = (bytes) => {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

onMounted(() => {
  fetchMaps()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-primary {
  @apply px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl flex items-center gap-2;
}

.input-text {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
