<template>
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="glass-card p-6 max-w-lg w-full">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-white">Ban Ekle</h3>
        <button @click="$emit('close')" class="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="addBan" class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-2">Ban Tipi *</label>
          <select v-model="form.ban_type" required class="input-text w-full">
            <option value="steam_id">Steam ID</option>
            <option value="ip">IP Adresi</option>
          </select>
        </div>

        <div>
          <label class="block text-sm text-gray-400 mb-2">
            {{ form.ban_type === 'steam_id' ? 'Steam ID' : 'IP Adresi' }} *
          </label>
          <input
            v-model="form.value"
            type="text"
            :placeholder="form.ban_type === 'steam_id' ? 'STEAM_0:1:12345678' : '192.168.1.1'"
            required
            class="input-text w-full font-mono"
          />
        </div>

        <div>
          <label class="block text-sm text-gray-400 mb-2">Süre (dakika)</label>
          <input
            v-model.number="form.duration"
            type="number"
            min="0"
            placeholder="0 = Kalıcı"
            class="input-text w-full"
          />
          <p class="text-xs text-gray-500 mt-1">0 = Kalıcı ban</p>
        </div>

        <div class="flex gap-3 mt-6">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-all"
            :disabled="loading"
          >
            İptal
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white rounded-lg font-medium transition-all disabled:opacity-50"
          >
            {{ loading ? 'Ekleniyor...' : 'Ban Ekle' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const props = defineProps({
  serverId: { type: Number, required: true }
})

const emit = defineEmits(['close', 'added'])
const toast = useToast()

const loading = ref(false)
const form = ref({
  ban_type: 'steam_id',
  value: '',
  duration: 0
})

const addBan = async () => {
  loading.value = true
  try {
    const response = await api.addBan(props.serverId, form.value)

    if (response.success) {
      toast.show(response.message, 'success')
      emit('added')
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Ban eklenemedi', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.input-text {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all;
}
</style>
