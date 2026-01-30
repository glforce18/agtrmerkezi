<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h2 class="text-2xl font-bold text-text-primary">Dosya Yönetimi</h2>
      <p class="text-text-muted text-sm mt-1">Sunucu yapılandırma dosyalarını düzenleyin</p>
    </div>

    <!-- File Selector -->
    <div class="glass-card p-6 fade-in-up">
      <label class="block text-sm font-medium text-text-primary mb-3">
        Düzenlenecek Dosya
      </label>
      <select v-model="selectedFile" @change="loadFile" class="input">
        <option value="">Bir dosya seçin...</option>
        <option value="server.cfg">server.cfg - Ana sunucu ayarları</option>
        <option value="autoexec.cfg">autoexec.cfg - Başlangıç komutları</option>
        <option value="startup_server.cfg">startup_server.cfg - Startup config</option>
        <option value="addons/amxmodx/configs/amxx.cfg">amxx.cfg - AMXModX ayarları</option>
      </select>
    </div>

    <!-- File Editor -->
    <div v-if="selectedFile" class="glass-card p-6 fade-in-up delay-100">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-semibold text-text-primary">{{ selectedFile }}</h3>
          <p class="text-xs text-text-muted mt-1">Son düzenleme: {{ lastModified || 'Bilinmiyor' }}</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="loadFile"
            :disabled="loading"
            class="btn btn-secondary text-sm"
            title="Yeniden yükle"
          >
            🔄
          </button>
          <button
            @click="saveFile"
            :disabled="loading || !fileContent"
            class="btn btn-primary text-sm"
          >
            💾 Kaydet
          </button>
        </div>
      </div>

      <!-- Editor -->
      <div class="relative">
        <textarea
          v-model="fileContent"
          class="textarea font-mono text-sm min-h-[500px]"
          :placeholder="loading ? 'Yükleniyor...' : 'Dosya içeriği burada görünecek...'"
          :disabled="loading"
          spellcheck="false"
        ></textarea>
        <div class="absolute bottom-3 right-3 text-xs text-text-muted font-mono">
          {{ lineCount }} satır
        </div>
      </div>

      <!-- File Info -->
      <div class="mt-4 p-4 bg-dark-elevated rounded-lg">
        <h4 class="text-sm font-medium text-text-primary mb-2">💡 İpuçları</h4>
        <ul class="text-xs text-text-muted space-y-1">
          <li v-if="selectedFile === 'server.cfg'">
            • hostname: Sunucu adı<br>
            • sv_password: Sunucu şifresi<br>
            • mp_timelimit, mp_fraglimit: Oyun limitleri
          </li>
          <li v-else-if="selectedFile === 'autoexec.cfg'">
            • Sunucu her başladığında otomatik çalışır<br>
            • exec server.cfg ile diğer config'leri yükleyebilirsiniz<br>
            • Özel komutlarınızı buraya ekleyin
          </li>
          <li v-else>
            • Satır başına 1 ayar yazın<br>
            • // ile yorum satırı ekleyebilirsiniz
          </li>
        </ul>
      </div>
    </div>

    <!-- Placeholder -->
    <div v-else class="empty-state glass-card p-12">
      <div class="empty-state-icon">📄</div>
      <p class="empty-state-title">Dosya Seçilmedi</p>
      <p class="empty-state-description">
        Düzenlemek için yukarıdan bir dosya seçin
      </p>
    </div>

    <!-- Warning -->
    <div class="alert alert-warning fade-in-up delay-200">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-2" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <strong>Uyarı:</strong> Dosyaları düzenlerken dikkatli olun. Hatalı ayarlar sunucunuzun çalışmamasına neden olabilir.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
// import axios from 'axios'

const props = defineProps({
  serverId: Number,
  serverInfo: Object,
  serverStatus: Object
})

const selectedFile = ref('')
const fileContent = ref('')
const lastModified = ref('')
const loading = ref(false)

const lineCount = computed(() => {
  if (!fileContent.value) return 0
  return fileContent.value.split('\n').length
})

const loadFile = async () => {
  if (!selectedFile.value) return

  loading.value = true
  try {
    // TODO: Implement API call when backend is ready
    // const response = await axios.get(`/api/servers/${props.serverId}/files/${selectedFile.value}`)
    // fileContent.value = response.data.content
    // lastModified.value = new Date(response.data.last_modified).toLocaleString('tr-TR')

    // Mock data for now
    await new Promise(resolve => setTimeout(resolve, 500))

    if (selectedFile.value === 'server.cfg') {
      fileContent.value = `// AGTR Merkezi - Server Configuration
// Server Name
hostname "${props.serverInfo?.name || 'AGTR Server'}"

// RCON Password
rcon_password "${props.serverInfo?.rcon_password || 'changeme'}"

// Server Password (empty = public)
sv_password ""

// Game Settings
mp_timelimit 25
mp_fraglimit 50
mp_friendlyfire 0
mp_teamplay 0

// Server Settings
sv_maxrate 25000
sv_minrate 5000
sv_maxupdaterate 101
sv_minupdaterate 10

// Execute additional configs
exec startup_server.cfg`
    } else if (selectedFile.value === 'autoexec.cfg') {
      fileContent.value = `// AGTR Merkezi - Autoexec Configuration
// This file runs automatically when server starts

// Load server config
exec server.cfg

// Custom commands
log on
sv_log_onefile 1
sv_logbans 1

// AMXModX
amx_client_languages 1
amx_language "tr"`
    } else {
      fileContent.value = `// Configuration file for ${selectedFile.value}
// Add your settings here...`
    }

    lastModified.value = new Date().toLocaleString('tr-TR')
  } catch (error) {
    alert('Dosya yüklenemedi: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const saveFile = async () => {
  if (!selectedFile.value || !fileContent.value) return

  if (!confirm(`${selectedFile.value} dosyasını kaydetmek istediğinizden emin misiniz?`)) {
    return
  }

  loading.value = true
  try {
    // TODO: Implement API call when backend is ready
    // await axios.put(`/api/servers/${props.serverId}/files/${selectedFile.value}`, {
    //   content: fileContent.value
    // })

    // Mock save
    await new Promise(resolve => setTimeout(resolve, 500))

    alert('✅ Dosya başarıyla kaydedildi!\n\nBazı ayarların etkili olması için sunucuyu yeniden başlatmanız gerekebilir.')
    lastModified.value = new Date().toLocaleString('tr-TR')
  } catch (error) {
    alert('Kaydetme hatası: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
textarea.textarea {
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  line-height: 1.5;
  tab-size: 4;
}
</style>
