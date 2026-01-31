<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Mapcycle Editor</h2>
          <p class="text-gray-400 text-sm mt-1">Sürükle-bırak ile map sırasını düzenleyin</p>
        </div>
        <div class="flex gap-3">
          <router-link
            :to="{ name: 'server-webpanel-maps' }"
            class="btn-secondary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Geri
          </router-link>
          <button
            v-if="hasChanges"
            @click="saveMapcycle"
            :disabled="saving"
            class="btn-primary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ saving ? 'Kaydediliyor...' : 'Kaydet' }}
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Mapcycle'daki Map</div>
          <div class="text-2xl font-bold text-white mt-1">{{ currentMaps.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Değişiklik</div>
          <div class="text-2xl font-bold text-yellow-400 mt-1">{{ hasChanges ? 'Var' : 'Yok' }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Mevcut Map</div>
          <div class="text-2xl font-bold text-blue-400 mt-1">{{ availableMaps.length }}</div>
        </div>
      </div>
    </div>

    <!-- Warning -->
    <div v-if="hasChanges" class="glass-card p-4 bg-orange-500/10 border-orange-500/20">
      <div class="flex items-center gap-3">
        <svg class="w-6 h-6 text-orange-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-orange-400">Kaydedilmemiş değişiklikler var! Kaydetmeyi unutmayın.</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Current Mapcycle (Drag source) -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Aktif Mapcycle
        </h3>

        <div v-if="loading" class="space-y-2">
          <div v-for="i in 5" :key="i" class="animate-pulse bg-white/5 rounded-lg h-12"></div>
        </div>

        <div v-else-if="currentMaps.length > 0" class="space-y-2">
          <draggable
            v-model="currentMaps"
            item-key="name"
            class="space-y-2"
            :animation="200"
            handle=".drag-handle"
            @change="markAsChanged"
          >
            <template #item="{ element, index }">
              <div class="map-item bg-white/5 hover:bg-white/10 rounded-lg p-3 transition-all group">
                <div class="flex items-center gap-3">
                  <!-- Drag handle -->
                  <div class="drag-handle cursor-move p-1 hover:bg-white/10 rounded">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                    </svg>
                  </div>

                  <!-- Order number -->
                  <div class="w-8 h-8 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-sm font-bold">
                    {{ index + 1 }}
                  </div>

                  <!-- Map name -->
                  <div class="flex-1">
                    <p class="text-white font-medium">{{ element }}</p>
                  </div>

                  <!-- Remove button -->
                  <button
                    @click="removeMap(index)"
                    class="p-2 hover:bg-red-500/20 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    title="Kaldır"
                  >
                    <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </template>
          </draggable>
        </div>

        <div v-else class="text-center py-12">
          <svg class="w-12 h-12 text-gray-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p class="text-gray-400">Mapcycle boş</p>
        </div>
      </div>

      <!-- Available Maps (Add to mapcycle) -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Mevcut Mapler
        </h3>

        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Map ara..."
          class="input-text w-full mb-4"
        />

        <div v-if="loading" class="space-y-2">
          <div v-for="i in 5" :key="i" class="animate-pulse bg-white/5 rounded-lg h-12"></div>
        </div>

        <div v-else class="space-y-2 max-h-[600px] overflow-y-auto">
          <div
            v-for="map in filteredAvailableMaps"
            :key="map"
            @click="addMap(map)"
            class="map-item bg-white/5 hover:bg-white/10 rounded-lg p-3 transition-all cursor-pointer group"
          >
            <div class="flex items-center gap-3">
              <!-- Add icon -->
              <div class="p-1 group-hover:bg-green-500/20 rounded">
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </div>

              <!-- Map name -->
              <div class="flex-1">
                <p class="text-white font-medium">{{ map }}</p>
              </div>

              <!-- Already in mapcycle indicator -->
              <span
                v-if="currentMaps.includes(map)"
                class="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full"
              >
                Eklendi
              </span>
            </div>
          </div>
        </div>

        <div v-if="!loading && filteredAvailableMaps.length === 0" class="text-center py-8">
          <p class="text-gray-400">{{ searchQuery ? 'Map bulunamadı' : 'Mevcut map yok' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import draggable from 'vuedraggable'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)
const saving = ref(false)

const currentMaps = ref([])
const originalMaps = ref([])
const availableMaps = ref([])

const searchQuery = ref('')
const hasChanges = ref(false)

const filteredAvailableMaps = computed(() => {
  if (!searchQuery.value) return availableMaps.value

  const query = searchQuery.value.toLowerCase()
  return availableMaps.value.filter(m => m.toLowerCase().includes(query))
})

const fetchData = async () => {
  loading.value = true
  try {
    // Fetch both mapcycle and map library
    const [mapcycleRes, libraryRes] = await Promise.all([
      api.getMapcycleList(serverId.value),
      api.getMapLibrary(serverId.value)
    ])

    if (mapcycleRes.success) {
      currentMaps.value = [...(mapcycleRes.data.maps || [])]
      originalMaps.value = [...(mapcycleRes.data.maps || [])]
    }

    if (libraryRes.success) {
      availableMaps.value = (libraryRes.data.maps || []).map(m => m.name)
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Veriler yüklenirken hata oluştu', 'error')
  } finally {
    loading.value = false
  }
}

const markAsChanged = () => {
  hasChanges.value = JSON.stringify(currentMaps.value) !== JSON.stringify(originalMaps.value)
}

const addMap = (mapName) => {
  if (!currentMaps.value.includes(mapName)) {
    currentMaps.value.push(mapName)
    markAsChanged()
    toast.show(`${mapName} eklendi`, 'success')
  }
}

const removeMap = (index) => {
  const mapName = currentMaps.value[index]
  currentMaps.value.splice(index, 1)
  markAsChanged()
  toast.show(`${mapName} kaldırıldı`, 'info')
}

const saveMapcycle = async () => {
  if (!hasChanges.value || saving.value) return

  saving.value = true
  try {
    const response = await api.updateMapcycleList(serverId.value, {
      maps: currentMaps.value
    })

    if (response.success) {
      toast.show(response.message, 'success')
      originalMaps.value = [...currentMaps.value]
      hasChanges.value = false
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Mapcycle kaydedilemedi', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchData()
})
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

.input-text {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all;
}

.map-item {
  transition: all 0.2s ease;
}

.drag-handle {
  cursor: grab;
}

.drag-handle:active {
  cursor: grabbing;
}
</style>
