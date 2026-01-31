<template>
  <div class="space-y-6">
    <!-- Header with stats -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Plugin Yönetimi</h2>
          <p class="text-gray-400 text-sm mt-1">Sunucu ve kullanıcı pluginlerini yönetin</p>
        </div>
        <button
          @click="showUploadModal = true"
          class="btn-primary flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Plugin Yükle
        </button>
      </div>

      <!-- Stats -->
      <div v-if="stats" class="grid grid-cols-4 gap-4 mt-6">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Sunucu Pluginleri</div>
          <div class="text-2xl font-bold text-white mt-1">{{ stats.server_plugins_count }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Kullanıcı Pluginleri</div>
          <div class="text-2xl font-bold text-white mt-1">{{ stats.user_plugins_count }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Aktif Pluginler</div>
          <div class="text-2xl font-bold text-green-400 mt-1">{{ stats.user_plugins_enabled }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Toplam Boyut</div>
          <div class="text-2xl font-bold text-white mt-1">
            {{ stats.user_plugins_size_mb }} MB
            <span class="text-sm text-gray-400">/ {{ stats.max_size_mb }} MB</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Server Plugins -->
    <div class="glass-card p-6">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
        Sunucu Pluginleri
        <span class="text-sm text-gray-400 font-normal">(salt-okunur)</span>
      </h3>

      <PluginList
        :plugins="serverPlugins"
        type="server"
        :loading="loading"
        @toggle="handleToggle"
        @delete="handleDelete"
      />
    </div>

    <!-- User Plugins -->
    <div class="glass-card p-6">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        Kullanıcı Pluginleri
        <span class="text-sm text-gray-400 font-normal">(yönetilebilir)</span>
      </h3>

      <PluginList
        :plugins="userPlugins"
        type="user"
        :loading="loading"
        @toggle="handleToggle"
        @delete="handleDelete"
      />

      <div v-if="!loading && userPlugins.length === 0" class="text-center py-12">
        <svg class="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p class="text-gray-400 mb-4">Henüz plugin yüklemediniz</p>
        <button @click="showUploadModal = true" class="btn-primary">
          İlk Plugininizi Yükleyin
        </button>
      </div>
    </div>

    <!-- Upload Modal -->
    <PluginUploader
      v-if="showUploadModal"
      :server-id="serverId"
      @close="showUploadModal = false"
      @uploaded="handlePluginUploaded"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import PluginList from '@/components/server/plugins/PluginList.vue'
import PluginUploader from '@/components/server/plugins/PluginUploader.vue'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)
const showUploadModal = ref(false)

const serverPlugins = ref([])
const userPlugins = ref([])
const stats = ref(null)

const fetchPlugins = async () => {
  loading.value = true
  try {
    const response = await api.getAllPlugins(serverId.value)

    if (response.success) {
      serverPlugins.value = response.data.server_plugins || []
      userPlugins.value = response.data.user_plugins || []
      stats.value = response.data.stats || {}
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Pluginler yüklenirken hata oluştu', 'error')
  } finally {
    loading.value = false
  }
}

const handleToggle = async (plugin, enable) => {
  try {
    const response = await api.togglePlugin(serverId.value, plugin.name, enable)

    if (response.success) {
      toast.show(response.message, 'success')
      await fetchPlugins()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Plugin durumu değiştirilemedi', 'error')
  }
}

const handleDelete = async (plugin) => {
  if (!confirm(`"${plugin.name}" pluginini silmek istediğinizden emin misiniz?`)) {
    return
  }

  try {
    const response = await api.deletePlugin(serverId.value, plugin.name)

    if (response.success) {
      toast.show(response.message, 'success')
      await fetchPlugins()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Plugin silinemedi', 'error')
  }
}

const handlePluginUploaded = () => {
  showUploadModal.value = false
  fetchPlugins()
}

onMounted(() => {
  fetchPlugins()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-primary {
  @apply px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl;
}
</style>
