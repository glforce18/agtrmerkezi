<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">MOTD Editor</h2>
          <p class="text-gray-400 text-sm mt-1">Message of the Day (motd.txt) HTML düzenleyici</p>
        </div>
        <div class="flex gap-3">
          <button
            v-if="hasChanges"
            @click="resetChanges"
            class="btn-secondary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Sıfırla
          </button>
          <button
            v-if="hasChanges"
            @click="saveMotd"
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
          <div class="text-gray-400 text-sm">Karakter Sayısı</div>
          <div class="text-2xl font-bold text-white mt-1">{{ content.length }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Boyut</div>
          <div class="text-2xl font-bold text-blue-400 mt-1">{{ formatBytes(new TextEncoder().encode(content).length) }}</div>
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
        <p class="text-orange-400">Kaydedilmemiş değişiklikler var!</p>
      </div>
    </div>

    <!-- Editor -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- HTML Editor -->
      <div class="glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            HTML Editör
          </h3>
          <button
            @click="insertTemplate"
            class="btn-secondary text-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
            Şablon Yükle
          </button>
        </div>

        <textarea
          v-model="content"
          class="code-editor w-full h-[600px] p-3 bg-gray-900 border border-white/10 rounded-lg text-gray-100 font-mono text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
          spellcheck="false"
          placeholder="<html>&#10;<body>&#10;  <h1>Welcome!</h1>&#10;</body>&#10;</html>"
        ></textarea>

        <div class="mt-3 flex items-center justify-between">
          <p class="text-xs text-gray-500">HTML kod yazın. Inline CSS kullanabilirsiniz.</p>
          <p class="text-xs text-gray-500">Max: 100 KB</p>
        </div>
      </div>

      <!-- Preview -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          Önizleme
        </h3>

        <div class="bg-gray-900 border border-white/10 rounded-lg p-4 h-[600px] overflow-auto">
          <iframe
            ref="previewFrame"
            :srcdoc="content"
            class="w-full h-full bg-white"
            sandbox="allow-same-origin"
          ></iframe>
        </div>

        <div class="mt-3 flex items-center gap-2 text-xs text-gray-500">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Oyuncular sunucuya katıldığında bu mesajı görecek
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

const originalContent = ref('')
const content = ref('')

const hasChanges = computed(() => {
  return originalContent.value !== content.value
})

const fetchMotd = async () => {
  loading.value = true
  try {
    const response = await api.getMotd(serverId.value)
    if (response.success) {
      originalContent.value = response.data.content
      content.value = response.data.content
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'MOTD yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const saveMotd = async () => {
  if (!hasChanges.value) return

  saving.value = true
  try {
    const response = await api.updateMotd(serverId.value, {
      content: content.value
    })

    if (response.success) {
      toast.show(response.message, 'success')
      originalContent.value = content.value
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'MOTD kaydedilemedi', 'error')
  } finally {
    saving.value = false
  }
}

const resetChanges = () => {
  if (!confirm('Değişiklikler sıfırlanacak. Emin misiniz?')) return
  content.value = originalContent.value
}

const insertTemplate = () => {
  if (hasChanges.value) {
    if (!confirm('Mevcut içerik silinecek. Devam edilsin mi?')) return
  }

  content.value = `<html>
<head>
<title>Welcome to Our Server</title>
<style>
body {
  background-color: #1a1a1a;
  color: #ffffff;
  font-family: Arial, sans-serif;
  padding: 20px;
}
h1 {
  color: #4CAF50;
  text-align: center;
}
.info {
  background-color: #2a2a2a;
  border-left: 4px solid #4CAF50;
  padding: 15px;
  margin: 20px 0;
}
.rules {
  list-style-type: none;
  padding: 0;
}
.rules li {
  padding: 5px 0;
  border-bottom: 1px solid #333;
}
</style>
</head>
<body>
<h1>Welcome to Our Server!</h1>

<div class="info">
  <h2>Server Information</h2>
  <p>Enjoy your game and have fun!</p>
</div>

<div class="info">
  <h2>Server Rules</h2>
  <ul class="rules">
    <li>1. Be respectful to other players</li>
    <li>2. No cheating or hacking</li>
    <li>3. No spam in chat</li>
    <li>4. Follow admin instructions</li>
  </ul>
</div>

<p style="text-align: center; margin-top: 30px;">
  <small>Have a great time!</small>
</p>
</body>
</html>`

  toast.show('Şablon yüklendi', 'success')
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchMotd()
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
  tab-size: 2;
}

.code-editor::placeholder {
  @apply text-gray-600;
}
</style>
