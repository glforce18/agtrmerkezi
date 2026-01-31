<template>
  <div class="space-y-2">
    <!-- Loading -->
    <div v-if="loading" class="space-y-2">
      <div v-for="i in 3" :key="i" class="animate-pulse bg-white/5 rounded-lg p-4 h-20"></div>
    </div>

    <!-- Admin items -->
    <div v-else-if="admins.length > 0" class="space-y-2">
      <div
        v-for="admin in admins"
        :key="admin.steam_id"
        class="bg-white/5 hover:bg-white/10 rounded-lg p-4 transition-all"
      >
        <div class="flex items-center justify-between">
          <!-- Admin info -->
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h4 class="text-white font-medium font-mono">{{ admin.steam_id }}</h4>
              <span
                v-if="admin.password"
                class="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded-full"
              >
                Şifreli
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm">
              <div class="flex items-center gap-2">
                <span class="text-gray-400">Yetkiler:</span>
                <code class="px-2 py-1 bg-blue-500/20 text-blue-400 rounded font-mono text-xs">
                  {{ admin.flags }}
                </code>
              </div>
              <div v-if="admin.connection_flags" class="flex items-center gap-2">
                <span class="text-gray-400">Bağlantı:</span>
                <code class="px-2 py-1 bg-green-500/20 text-green-400 rounded font-mono text-xs">
                  {{ admin.connection_flags }}
                </code>
              </div>
            </div>
          </div>

          <!-- Delete button -->
          <button
            @click="$emit('delete', admin)"
            class="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
            title="Sil"
          >
            <svg
              class="w-5 h-5 text-gray-400 group-hover:text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12">
      <svg class="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
      <p class="text-gray-400">Henüz admin eklenmemiş</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  admins: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})

defineEmits(['delete'])
</script>
