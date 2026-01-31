<template>
  <!-- Modal overlay -->
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="glass-card p-6 max-w-lg w-full">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-white">Plugin Yükle</h3>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-white/10 rounded-lg transition-colors"
        >
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Upload area -->
      <div
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        :class="[
          'border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer',
          isDragging
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-gray-600 hover:border-gray-500 bg-white/5'
        ]"
        @click="$refs.fileInput.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".amxx"
          class="hidden"
          @change="handleFileSelect"
        />

        <div v-if="!selectedFile">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="text-white mb-2">
            Dosyayı sürükleyip bırakın veya
            <span class="text-blue-400 hover:text-blue-300 cursor-pointer">seçmek için tıklayın</span>
          </p>
          <p class="text-gray-400 text-sm">Sadece .amxx dosyaları (Max 5MB)</p>
        </div>

        <div v-else class="space-y-4">
          <!-- File info -->
          <div class="flex items-center gap-4 bg-white/5 rounded-lg p-4">
            <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="flex-1 text-left">
              <p class="text-white font-medium">{{ selectedFile.name }}</p>
              <p class="text-gray-400 text-sm">{{ formatSize(selectedFile.size) }}</p>
            </div>
            <button
              @click.stop="selectedFile = null"
              class="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Upload progress -->
          <div v-if="uploading" class="space-y-2">
            <div class="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                class="bg-gradient-to-r from-blue-500 to-blue-600 h-full transition-all duration-300"
                :style="{ width: `${uploadProgress}%` }"
              ></div>
            </div>
            <p class="text-sm text-gray-400">Yükleniyor... {{ uploadProgress }}%</p>
          </div>
        </div>
      </div>

      <!-- Error message -->
      <div v-if="error" class="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <p class="text-red-400 text-sm">{{ error }}</p>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 mt-6">
        <button
          @click="$emit('close')"
          class="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-all"
          :disabled="uploading"
        >
          İptal
        </button>
        <button
          @click="uploadPlugin"
          :disabled="!selectedFile || uploading"
          class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ uploading ? 'Yükleniyor...' : 'Yükle' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const props = defineProps({
  serverId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['close', 'uploaded'])
const toast = useToast()

const selectedFile = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref(null)

const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files

  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

const validateAndSetFile = (file) => {
  error.value = null

  // Check extension
  if (!file.name.endsWith('.amxx')) {
    error.value = 'Sadece .amxx dosyaları yüklenebilir'
    return
  }

  // Check size (5MB)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    error.value = 'Dosya boyutu 5MB\'dan büyük olamaz'
    return
  }

  selectedFile.value = file
}

const uploadPlugin = async () => {
  if (!selectedFile.value || uploading.value) return

  uploading.value = true
  uploadProgress.value = 0
  error.value = null

  try {
    // Read file as base64
    const base64 = await fileToBase64(selectedFile.value)

    // Simulate progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    const response = await api.uploadPlugin(props.serverId, {
      filename: selectedFile.value.name,
      content_base64: base64
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100

    if (response.success) {
      toast.show(response.message || 'Plugin başarıyla yüklendi', 'success')
      emit('uploaded')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Plugin yüklenirken hata oluştu'
    toast.show(error.value, 'error')
  } finally {
    uploading.value = false
  }
}

const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      // Remove "data:application/octet-stream;base64," prefix
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = (error) => reject(error)
  })
}

const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}
</style>
