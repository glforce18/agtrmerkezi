<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Plugin Compiler</h2>
          <p class="text-gray-400 text-sm mt-1">AMXModX .sma dosyalarını .amxx'e derleyin</p>
        </div>
        <div class="flex gap-3">
          <button
            v-if="compilerInfo && !compilerInfo.available"
            class="btn-warning"
            disabled
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Compiler Kurulu Değil
          </button>
          <button
            v-else
            @click="compileCode"
            :disabled="!sourceCode.trim() || !pluginName.trim() || compiling"
            class="btn-primary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
            </svg>
            {{ compiling ? 'Derleniyor...' : 'Derle' }}
          </button>
        </div>
      </div>

      <!-- Compiler Info -->
      <div v-if="compilerInfo" class="grid grid-cols-3 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Compiler Durumu</div>
          <div class="text-2xl font-bold mt-1" :class="compilerInfo.available ? 'text-green-400' : 'text-red-400'">
            {{ compilerInfo.available ? 'Aktif' : 'Kurulu Değil' }}
          </div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Versiyon</div>
          <div class="text-lg font-bold text-white mt-1">{{ compilerInfo.version || 'N/A' }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Compiler Path</div>
          <div class="text-xs text-gray-300 mt-1 font-mono truncate">{{ compilerInfo.compiler_path }}</div>
        </div>
      </div>
    </div>

    <!-- Editor Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Source Code Editor -->
      <div class="glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            Source Code (.sma)
          </h3>
          <div class="flex gap-2">
            <button
              @click="loadExample"
              class="btn-secondary text-sm"
              title="Örnek kod yükle"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Örnek
            </button>
            <button
              @click="clearCode"
              class="btn-secondary text-sm"
              title="Temizle"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Temizle
            </button>
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-gray-300 mb-2 text-sm">Plugin Adı</label>
            <input
              v-model="pluginName"
              type="text"
              placeholder="my_plugin"
              class="input-text w-full"
              maxlength="50"
            />
          </div>

          <div>
            <label class="block text-gray-300 mb-2 text-sm">Kaynak Kod</label>
            <textarea
              v-model="sourceCode"
              class="code-editor w-full h-96 p-3 bg-gray-900 border border-white/10 rounded-lg text-gray-100 font-mono text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
              placeholder="#include <amxmodx>&#10;&#10;public plugin_init() {&#10;    register_plugin(&quot;My Plugin&quot;, &quot;1.0&quot;, &quot;Author&quot;)&#10;}"
              spellcheck="false"
            ></textarea>
            <div class="text-xs text-gray-500 mt-1">{{ sourceCode.length }} karakter</div>
          </div>
        </div>
      </div>

      <!-- Output Panel -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Derleme Çıktısı
        </h3>

        <div v-if="!compiled && !compileError" class="text-center py-16">
          <svg class="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <p class="text-gray-400">Kod derlemek için "Derle" butonuna tıklayın</p>
        </div>

        <!-- Success Output -->
        <div v-else-if="compiled" class="space-y-4">
          <div class="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
            <div class="flex items-center gap-2 text-green-400 font-medium mb-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Derleme Başarılı!
            </div>
            <p class="text-sm text-green-300">{{ compiledFilename }}</p>
          </div>

          <!-- Warnings -->
          <div v-if="warnings.length > 0" class="bg-orange-500/10 border border-orange-500/20 rounded-lg p-4">
            <div class="flex items-center gap-2 text-orange-400 font-medium mb-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {{ warnings.length }} Uyarı
            </div>
            <div class="space-y-1">
              <p v-for="(warning, i) in warnings" :key="i" class="text-xs text-orange-300 font-mono">{{ warning }}</p>
            </div>
          </div>

          <!-- Compiler Output -->
          <div v-if="compilerOutput" class="bg-white/5 rounded-lg p-4">
            <p class="text-gray-400 text-sm mb-2">Compiler Çıktısı:</p>
            <pre class="text-xs text-gray-300 font-mono whitespace-pre-wrap">{{ compilerOutput }}</pre>
          </div>

          <!-- Download Button -->
          <button
            @click="downloadCompiledPlugin"
            class="btn-primary w-full"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            {{ compiledFilename }} İndir
          </button>
        </div>

        <!-- Error Output -->
        <div v-else-if="compileError" class="space-y-4">
          <div class="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div class="flex items-center gap-2 text-red-400 font-medium mb-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Derleme Hatası
            </div>
            <pre class="text-sm text-red-300 font-mono whitespace-pre-wrap">{{ compileError }}</pre>
          </div>

          <!-- Warnings on error -->
          <div v-if="warnings.length > 0" class="bg-orange-500/10 border border-orange-500/20 rounded-lg p-4">
            <div class="flex items-center gap-2 text-orange-400 font-medium mb-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {{ warnings.length }} Uyarı
            </div>
            <div class="space-y-1">
              <p v-for="(warning, i) in warnings" :key="i" class="text-xs text-orange-300 font-mono">{{ warning }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const compiling = ref(false)

const pluginName = ref('my_plugin')
const sourceCode = ref('')
const compilerInfo = ref(null)

const compiled = ref(false)
const compiledData = ref('')
const compiledFilename = ref('')
const warnings = ref([])
const compilerOutput = ref('')
const compileError = ref('')

const fetchCompilerInfo = async () => {
  try {
    const response = await api.getCompilerInfo(serverId.value)
    if (response.success) {
      compilerInfo.value = response.data || {}
    }
  } catch (error) {
    console.error('Compiler info yüklenemedi:', error)
  }
}

const compileCode = async () => {
  if (!sourceCode.value.trim() || !pluginName.value.trim()) {
    toast.show('Plugin adı ve kaynak kod gerekli', 'error')
    return
  }

  compiling.value = true
  compiled.value = false
  compileError.value = ''
  warnings.value = []
  compilerOutput.value = ''

  try {
    const response = await api.compilePlugin(serverId.value, {
      source_code: sourceCode.value,
      plugin_name: pluginName.value
    })

    if (response.success) {
      const data = response.data

      if (data.success) {
        compiled.value = true
        compiledData.value = data.compiled_data || ''
        compiledFilename.value = data.filename || ''
        warnings.value = data.warnings || []
        compilerOutput.value = data.output || ''
        toast.show('Plugin başarıyla derlendi!', 'success')
      } else {
        compileError.value = data.error
        warnings.value = data.warnings || []
        toast.show('Derleme başarısız', 'error')
      }
    }
  } catch (error) {
    compileError.value = error.response?.data?.detail || 'Derleme hatası oluştu'
    toast.show('Derleme hatası', 'error')
  } finally {
    compiling.value = false
  }
}

const downloadCompiledPlugin = () => {
  if (!compiledData.value) return

  // Decode base64 to binary
  const binaryString = atob(compiledData.value)
  const bytes = new Uint8Array(binaryString.length)
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i)
  }

  // Create blob and download
  const blob = new Blob([bytes], { type: 'application/octet-stream' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = compiledFilename.value
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)

  toast.show('İndirme başladı', 'success')
}

const loadExample = () => {
  pluginName.value = 'hello_world'
  sourceCode.value = `#include <amxmodx>

public plugin_init() {
    register_plugin("Hello World", "1.0", "Author")
    register_clcmd("say /hello", "cmd_hello")
}

public cmd_hello(id) {
    client_print(id, print_chat, "[AMX] Hello World!")
    return PLUGIN_HANDLED
}`
  toast.show('Örnek kod yüklendi', 'info')
}

const clearCode = () => {
  if (sourceCode.value && !confirm('Kodu temizlemek istediğinizden emin misiniz?')) return

  sourceCode.value = ''
  compiled.value = false
  compileError.value = ''
  warnings.value = []
  compilerOutput.value = ''
}

onMounted(() => {
  fetchCompilerInfo()
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

.btn-warning {
  @apply px-4 py-2 bg-orange-500/20 text-orange-400 rounded-lg font-medium flex items-center gap-2 cursor-not-allowed;
}

.input-text {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all;
}

.code-editor {
  line-height: 1.5;
  tab-size: 4;
}

.code-editor::placeholder {
  @apply text-gray-600;
}
</style>
