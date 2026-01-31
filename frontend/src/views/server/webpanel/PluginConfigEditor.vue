<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Plugin Config Editor</h2>
          <p class="text-gray-400 text-sm mt-1">Plugin .ini ve .cfg dosyalarını düzenleyin</p>
        </div>
        <button
          v-if="selectedConfig && hasChanges"
          @click="saveConfig"
          :disabled="saving"
          class="btn-primary"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ saving ? 'Kaydediliyor...' : 'Kaydet' }}
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Config</div>
          <div class="text-2xl font-bold text-white mt-1">{{ configs.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Seçili Dosya</div>
          <div class="text-lg font-bold text-blue-400 mt-1 truncate">{{ selectedConfig || 'Yok' }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Değişiklik</div>
          <div class="text-2xl font-bold mt-1" :class="hasChanges ? 'text-yellow-400' : 'text-green-400'">
            {{ hasChanges ? 'Var' : 'Yok' }}
          </div>
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

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Config List -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Config Dosyaları
        </h3>

        <div v-if="loading" class="space-y-2">
          <div v-for="i in 5" :key="i" class="animate-pulse bg-white/5 rounded-lg h-12"></div>
        </div>

        <div v-else-if="configs.length > 0" class="space-y-2">
          <button
            v-for="config in configs"
            :key="config.name"
            @click="loadConfig(config.name)"
            :class="[
              'w-full text-left p-3 rounded-lg transition-all',
              selectedConfig === config.name
                ? 'bg-blue-500/20 border-blue-500/50 border'
                : 'bg-white/5 hover:bg-white/10'
            ]"
          >
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="flex-1">
                <p class="text-white font-medium text-sm">{{ config.name }}</p>
                <p class="text-gray-500 text-xs">{{ formatBytes(config.size) }}</p>
              </div>
              <svg v-if="selectedConfig === config.name" class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
        </div>

        <div v-else class="text-center py-12">
          <svg class="w-12 h-12 text-gray-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-400">Config dosyası yok</p>
        </div>
      </div>

      <!-- Editor -->
      <div class="lg:col-span-2 glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            {{ selectedConfig || 'Dosya Seçin' }}
          </h3>
          <div class="flex gap-2">
            <button
              v-if="selectedConfig && !viewMode"
              @click="viewMode = true"
              class="btn-secondary text-sm"
              title="Görünüm modu"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Görünüm
            </button>
            <button
              v-if="selectedConfig && viewMode"
              @click="viewMode = false"
              class="btn-secondary text-sm"
              title="Düzenleme modu"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Düzenle
            </button>
          </div>
        </div>

        <div v-if="!selectedConfig" class="text-center py-16">
          <svg class="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-400">Sol taraftan bir config dosyası seçin</p>
        </div>

        <!-- Parsed View (for .ini files) -->
        <div v-else-if="viewMode && parsedData" class="space-y-4">
          <!-- Global settings -->
          <div v-if="parsedData.globals.length > 0" class="bg-white/5 rounded-lg p-4">
            <h4 class="text-white font-medium mb-3">Global Ayarlar</h4>
            <div class="space-y-2">
              <div
                v-for="(item, i) in parsedData.globals"
                :key="i"
                class="flex items-center justify-between p-2 bg-white/5 rounded"
              >
                <span class="text-gray-300 font-mono text-sm">{{ item.key }}</span>
                <span class="text-blue-400 font-mono text-sm">{{ item.value }}</span>
              </div>
            </div>
          </div>

          <!-- Sections -->
          <div
            v-for="(items, section) in parsedData.sections"
            :key="section"
            class="bg-white/5 rounded-lg p-4"
          >
            <h4 class="text-white font-medium mb-3">[{{ section }}]</h4>
            <div class="space-y-2">
              <div
                v-for="(item, i) in items"
                :key="i"
                class="flex items-center justify-between p-2 bg-white/5 rounded"
              >
                <span class="text-gray-300 font-mono text-sm">{{ item.key }}</span>
                <span class="text-blue-400 font-mono text-sm">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Raw Editor -->
        <div v-else-if="selectedConfig">
          <textarea
            v-model="currentContent"
            class="code-editor w-full h-[600px] p-3 bg-gray-900 border border-white/10 rounded-lg text-gray-100 font-mono text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
            spellcheck="false"
          ></textarea>
          <div class="text-xs text-gray-500 mt-2">{{ currentContent.length }} karakter</div>
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
const saving = ref(false)

const configs = ref([])
const selectedConfig = ref(null)
const originalContent = ref('')
const currentContent = ref('')
const parsedData = ref(null)
const viewMode = ref(false)

const hasChanges = computed(() => {
  return originalContent.value !== currentContent.value
})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const response = await api.listPluginConfigs(serverId.value)
    if (response.success) {
      configs.value = response.data.configs
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Config listesi yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const loadConfig = async (filename) => {
  if (hasChanges.value) {
    if (!confirm('Kaydedilmemiş değişiklikler var. Yine de devam edilsin mi?')) {
      return
    }
  }

  selectedConfig.value = filename
  viewMode.value = false

  try {
    const response = await api.getPluginConfig(serverId.value, filename)
    if (response.success) {
      originalContent.value = response.data.content
      currentContent.value = response.data.content
      parsedData.value = response.data.parsed

      // Auto-enable view mode for .ini with parsed data
      if (parsedData.value && Object.keys(parsedData.value.sections).length > 0) {
        viewMode.value = true
      }
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Config yüklenemedi', 'error')
    selectedConfig.value = null
  }
}

const saveConfig = async () => {
  if (!selectedConfig.value || !hasChanges.value) return

  saving.value = true
  try {
    const response = await api.updatePluginConfig(serverId.value, selectedConfig.value, {
      content: currentContent.value
    })

    if (response.success) {
      toast.show(response.message, 'success')
      originalContent.value = currentContent.value

      // Reload to get new parsed data
      await loadConfig(selectedConfig.value)
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Config kaydedilemedi', 'error')
  } finally {
    saving.value = false
  }
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchConfigs()
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
  @apply px-3 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-all flex items-center gap-2;
}

.code-editor {
  line-height: 1.5;
  tab-size: 4;
}
</style>
