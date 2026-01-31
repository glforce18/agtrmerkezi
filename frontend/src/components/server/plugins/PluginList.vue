<template>
  <div class="space-y-2">
    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-2">
      <div v-for="i in 3" :key="i" class="animate-pulse bg-white/5 rounded-lg p-4 h-16"></div>
    </div>

    <!-- Plugin items -->
    <div v-else-if="plugins.length > 0" class="space-y-2">
      <div
        v-for="plugin in plugins"
        :key="plugin.name"
        class="plugin-item bg-white/5 hover:bg-white/10 rounded-lg p-4 transition-all"
      >
        <div class="flex items-center justify-between">
          <!-- Plugin info -->
          <div class="flex items-center gap-4 flex-1">
            <!-- Status indicator -->
            <div
              :class="[
                'w-3 h-3 rounded-full',
                plugin.enabled ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
              ]"
            ></div>

            <!-- Name and details -->
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <h4 class="text-white font-medium">{{ plugin.name }}</h4>
                <span
                  v-if="type === 'server'"
                  class="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded-full"
                >
                  Server
                </span>
                <span
                  v-else
                  class="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full"
                >
                  User
                </span>
              </div>
              <div class="text-sm text-gray-400 mt-1">
                {{ formatSize(plugin.size) }} • {{ formatDate(plugin.modified) }}
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <!-- Toggle switch -->
            <button
              v-if="plugin.can_toggle"
              @click="$emit('toggle', plugin, !plugin.enabled)"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                plugin.enabled ? 'bg-green-500' : 'bg-gray-600'
              ]"
              :title="plugin.enabled ? 'Devre dışı bırak' : 'Aktif et'"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  plugin.enabled ? 'translate-x-6' : 'translate-x-1'
                ]"
              ></span>
            </button>

            <!-- Status badge (read-only) -->
            <span
              v-else
              :class="[
                'px-3 py-1 text-xs rounded-full',
                plugin.enabled
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-gray-500/20 text-gray-400'
              ]"
            >
              {{ plugin.enabled ? 'Aktif' : 'Pasif' }}
            </span>

            <!-- Delete button -->
            <button
              v-if="plugin.can_delete"
              @click="$emit('delete', plugin)"
              class="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
              title="Sil"
            >
              <svg
                class="w-5 h-5 text-gray-400 group-hover:text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>

            <!-- Read-only lock icon -->
            <div
              v-else
              class="p-2 opacity-50"
              title="Salt-okunur (sunucu plugini)"
            >
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-8 text-gray-400">
      <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p>{{ type === 'server' ? 'Sunucu plugini yok' : 'Kullanıcı plugini yok' }}</p>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  plugins: {
    type: Array,
    required: true
  },
  type: {
    type: String,
    required: true,
    validator: (value) => ['server', 'user'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle', 'delete'])

const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

const formatDate = (dateString) => {
  if (!dateString) return 'Bilinmiyor'
  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.plugin-item {
  transition: all 0.2s ease;
}
</style>
