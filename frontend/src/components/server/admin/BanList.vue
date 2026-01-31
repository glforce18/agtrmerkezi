<template>
  <div class="space-y-2">
    <!-- Loading -->
    <div v-if="loading" class="space-y-2">
      <div v-for="i in 3" :key="i" class="animate-pulse bg-white/5 rounded-lg p-4 h-16"></div>
    </div>

    <!-- Ban items -->
    <div v-else-if="bans.length > 0" class="space-y-2">
      <div
        v-for="(ban, index) in bans"
        :key="index"
        class="bg-white/5 hover:bg-white/10 rounded-lg p-4 transition-all"
      >
        <div class="flex items-center justify-between">
          <!-- Ban info -->
          <div class="flex items-center gap-4 flex-1">
            <div
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                ban.type === 'steam_id'
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-orange-500/20 text-orange-400'
              ]"
            >
              {{ ban.type === 'steam_id' ? 'Steam ID' : 'IP' }}
            </div>
            <code class="text-white font-mono">{{ ban.value }}</code>
            <span class="text-gray-400 text-sm">
              {{ ban.duration === '0' ? 'Kalıcı' : `${ban.duration} dakika` }}
            </span>
          </div>

          <!-- Delete button -->
          <button
            @click="$emit('delete', ban)"
            class="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
            title="Banı Kaldır"
          >
            <svg
              class="w-5 h-5 text-gray-400 group-hover:text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12">
      <svg class="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-gray-400">Ban listesi boş</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  bans: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})

defineEmits(['delete'])
</script>
