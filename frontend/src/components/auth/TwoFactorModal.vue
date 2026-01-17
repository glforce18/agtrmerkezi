<template>
  <div class="modal modal-open">
    <div class="modal-box relative">
      <button
        class="btn btn-sm btn-circle absolute right-2 top-2"
        @click="$emit('close')"
        :disabled="loading"
      >
        ✕
      </button>

      <h3 class="font-bold text-2xl mb-4 text-center">
        <span class="neon-text">İki Faktörlü Doğrulama</span>
      </h3>

      <div class="text-center mb-6">
        <div class="mx-auto w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center mb-4">
          <svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
        <p class="text-sm opacity-70">
          Authenticator uygulamanızdaki 6 haneli kodu girin
        </p>
      </div>

      <!-- 2FA Code Input -->
      <div class="flex justify-center gap-2 mb-6">
        <input
          v-for="(digit, index) in code"
          :key="index"
          :ref="el => inputs[index] = el"
          v-model="code[index]"
          type="text"
          inputmode="numeric"
          maxlength="1"
          class="input input-bordered w-12 h-14 text-center text-xl font-bold"
          :class="{ 'input-error': error }"
          @input="handleInput(index, $event)"
          @keydown="handleKeyDown(index, $event)"
          @paste="handlePaste"
        />
      </div>

      <p v-if="error" class="text-error text-sm text-center mb-4">
        {{ error }}
      </p>

      <!-- Backup Code Option -->
      <div class="text-center mb-6">
        <button
          @click="useBackupCode = !useBackupCode"
          class="link link-primary text-sm"
        >
          {{ useBackupCode ? 'Authenticator kodu kullan' : 'Yedek kod kullan' }}
        </button>
      </div>

      <div v-if="useBackupCode" class="mb-6">
        <BaseInput
          v-model="backupCode"
          placeholder="XXXX-XXXX-XXXX"
          label="Yedek Kod"
          :error="error"
        />
      </div>

      <!-- Actions -->
      <div class="modal-action">
        <BaseButton
          variant="ghost"
          @click="$emit('close')"
          :disabled="loading"
        >
          İptal
        </BaseButton>
        <BaseButton
          variant="primary"
          @click="handleVerify"
          :loading="loading"
          :disabled="!canVerify"
        >
          Doğrula
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps({
  loading: Boolean
})

const emit = defineEmits(['verify', 'close'])

const code = reactive(['', '', '', '', '', ''])
const inputs = ref([])
const error = ref('')
const useBackupCode = ref(false)
const backupCode = ref('')

const canVerify = computed(() => {
  if (useBackupCode.value) {
    return backupCode.value.length > 0
  }
  return code.every(digit => digit !== '')
})

const handleInput = (index, event) => {
  const value = event.target.value

  // Only allow numbers
  if (!/^\d*$/.test(value)) {
    code[index] = ''
    return
  }

  code[index] = value

  // Auto-focus next input
  if (value && index < 5) {
    nextTick(() => {
      inputs.value[index + 1]?.focus()
    })
  }

  // Auto-submit when all filled
  if (index === 5 && value) {
    handleVerify()
  }

  error.value = ''
}

const handleKeyDown = (index, event) => {
  // Backspace: go to previous input
  if (event.key === 'Backspace' && !code[index] && index > 0) {
    inputs.value[index - 1]?.focus()
  }

  // Arrow keys
  if (event.key === 'ArrowLeft' && index > 0) {
    inputs.value[index - 1]?.focus()
  }
  if (event.key === 'ArrowRight' && index < 5) {
    inputs.value[index + 1]?.focus()
  }
}

const handlePaste = (event) => {
  event.preventDefault()
  const pastedData = event.clipboardData.getData('text').replace(/\D/g, '')

  if (pastedData.length === 6) {
    pastedData.split('').forEach((digit, index) => {
      code[index] = digit
    })
    inputs.value[5]?.focus()
  }
}

const handleVerify = () => {
  const verificationCode = useBackupCode.value
    ? backupCode.value
    : code.join('')

  if (!verificationCode) {
    error.value = 'Lütfen doğrulama kodunu girin'
    return
  }

  emit('verify', verificationCode)
}

// Focus first input on mount
nextTick(() => {
  inputs.value[0]?.focus()
})
</script>

<style scoped>
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type=number] {
  -moz-appearance: textfield;
}
</style>
