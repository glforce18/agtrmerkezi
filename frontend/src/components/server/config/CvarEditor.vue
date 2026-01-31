<template>
  <div
    class="cvar-item bg-white/5 hover:bg-white/10 rounded-lg p-4 transition-all"
    :class="{ 'ring-2 ring-yellow-500/50': isModified }"
  >
    <div class="flex items-start gap-4">
      <!-- Name and description -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <h4 class="text-white font-medium font-mono text-sm">{{ cvar.name }}</h4>
          <span
            v-if="isModified"
            class="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded-full"
          >
            Değiştirildi
          </span>
        </div>
        <p class="text-gray-400 text-sm">{{ cvar.description || 'Açıklama yok' }}</p>
      </div>

      <!-- Value editor -->
      <div class="flex items-center gap-3">
        <!-- Boolean toggle -->
        <div v-if="cvar.type === 'boolean'" class="flex items-center gap-2">
          <span class="text-sm text-gray-400">{{ localValue === '0' ? 'Kapalı' : 'Açık' }}</span>
          <button
            @click="toggleBoolean"
            :class="[
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
              localValue === '0' ? 'bg-gray-600' : 'bg-green-500'
            ]"
          >
            <span
              :class="[
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                localValue === '0' ? 'translate-x-1' : 'translate-x-6'
              ]"
            ></span>
          </button>
        </div>

        <!-- Number input -->
        <div v-else-if="cvar.type === 'number'" class="flex items-center gap-2">
          <input
            v-model.number="localValue"
            type="number"
            :min="cvar.min"
            :max="cvar.max"
            @change="emitUpdate"
            class="input-number"
          />
          <span v-if="cvar.min !== undefined || cvar.max !== undefined" class="text-xs text-gray-500">
            {{ cvar.min !== undefined ? `${cvar.min}` : '' }}
            {{ cvar.min !== undefined && cvar.max !== undefined ? '-' : '' }}
            {{ cvar.max !== undefined ? `${cvar.max}` : '' }}
          </span>
        </div>

        <!-- Password input -->
        <div v-else-if="cvar.type === 'password'" class="flex items-center gap-2">
          <input
            v-model="localValue"
            :type="showPassword ? 'text' : 'password'"
            @input="emitUpdate"
            class="input-text"
            placeholder="••••••••"
          />
          <button
            @click="showPassword = !showPassword"
            class="p-2 hover:bg-white/10 rounded transition-colors"
          >
            <svg
              v-if="!showPassword"
              class="w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg
              v-else
              class="w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>

        <!-- String input -->
        <input
          v-else
          v-model="localValue"
          type="text"
          @input="emitUpdate"
          class="input-text"
          :placeholder="cvar.name"
        />

        <!-- Reset button (if modified) -->
        <button
          v-if="isModified"
          @click="resetValue"
          class="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
          title="Orijinal değere dön"
        >
          <svg
            class="w-5 h-5 text-gray-400 group-hover:text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  cvar: {
    type: Object,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  isModified: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update'])

const localValue = ref(props.value)
const showPassword = ref(false)

// Watch for external value changes
watch(() => props.value, (newValue) => {
  localValue.value = newValue
})

const emitUpdate = () => {
  emit('update', props.cvar.name, String(localValue.value))
}

const toggleBoolean = () => {
  localValue.value = localValue.value === '0' ? '1' : '0'
  emitUpdate()
}

const resetValue = () => {
  localValue.value = props.cvar.value
  emitUpdate()
}
</script>

<style scoped>
.cvar-item {
  transition: all 0.2s ease;
}

.input-text {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all w-64;
}

.input-number {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all w-32;
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  opacity: 1;
}
</style>
