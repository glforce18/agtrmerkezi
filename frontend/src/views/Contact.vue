<template>
  <div class="min-h-screen py-12">
    <div class="container-custom">
      <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl font-display font-bold mb-8 text-center">
          <span class="text-gradient-orange">İletişim</span>
        </h1>

        <div class="grid md:grid-cols-2 gap-8">
          <!-- Contact Form -->
          <div class="glass-card p-6">
            <h2 class="text-xl font-bold mb-4">Bize Ulasin</h2>

            <form v-if="!submitted" @submit.prevent="handleSubmit" class="space-y-4">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Adiniz</span>
                </label>
                <input
                  v-model="form.name"
                  type="text"
                  placeholder="Ad Soyad"
                  class="input input-bordered bg-base-200"
                  :class="{ 'input-error': validation.name.status === 'error', 'input-success': validation.name.status === 'success' }"
                  @blur="validateName"
                  required
                />
                <p v-if="validation.name.message" class="text-error text-sm mt-1">{{ validation.name.message }}</p>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">E-posta</span>
                </label>
                <input
                  v-model="form.email"
                  type="email"
                  placeholder="ornek@email.com"
                  class="input input-bordered bg-base-200"
                  :class="{ 'input-error': validation.email.status === 'error', 'input-success': validation.email.status === 'success' }"
                  @blur="validateEmail"
                  required
                />
                <p v-if="validation.email.message" class="text-error text-sm mt-1">{{ validation.email.message }}</p>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Konu</span>
                </label>
                <select
                  v-model="form.subject"
                  class="select select-bordered bg-base-200"
                  :class="{ 'select-error': validation.subject.status === 'error', 'select-success': validation.subject.status === 'success' }"
                  @change="validateSubject"
                  required
                >
                  <option value="">Konu Seçin</option>
                  <option value="general">Genel Soru</option>
                  <option value="support">Teknik Destek</option>
                  <option value="billing">Ödeme/Fatura</option>
                  <option value="partnership">Is Birligi</option>
                  <option value="other">Diğer</option>
                </select>
                <p v-if="validation.subject.message" class="text-error text-sm mt-1">{{ validation.subject.message }}</p>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Mesajiniz</span>
                </label>
                <textarea
                  v-model="form.message"
                  class="textarea textarea-bordered bg-base-200 h-32"
                  :class="{ 'textarea-error': validation.message.status === 'error', 'textarea-success': validation.message.status === 'success' }"
                  placeholder="Mesajinizi yazın... (min 20 karakter)"
                  @blur="validateMessage"
                  required
                ></textarea>
                <div class="flex justify-between mt-1">
                  <p v-if="validation.message.message" class="text-error text-sm">{{ validation.message.message }}</p>
                  <span v-else></span>
                  <span class="text-sm opacity-60">{{ form.message.length }} karakter</span>
                </div>
              </div>

              <button type="submit" class="btn-gaming w-full" :disabled="loading || !isFormValid">
                <span v-if="loading" class="loading loading-spinner loading-sm"></span>
                <span v-else>Mesaj Gönder</span>
              </button>
            </form>

            <div v-else class="text-center py-8">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-success/20 flex items-center justify-center">
                <svg class="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 class="text-xl font-bold mb-2">Mesajiniz Alindi!</h3>
              <p class="opacity-60">En kisa surede size donecegiz.</p>
            </div>
          </div>

          <!-- Contact Info -->
          <div class="space-y-6">
            <div class="glass-card p-6">
              <h2 class="text-xl font-bold mb-4">İletişim Bilgileri</h2>
              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                    <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-semibold">E-posta</p>
                    <p class="opacity-60">destek@agtrmerkezi.com</p>
                  </div>
                </div>

                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-secondary/20 flex items-center justify-center">
                    <svg class="w-5 h-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-semibold">Discord</p>
                    <a href="https://discord.gg/agtrmerkezi" target="_blank" class="link link-primary">discord.gg/agtrmerkezi</a>
                  </div>
                </div>
              </div>
            </div>

            <div class="glass-card p-6">
              <h2 class="text-xl font-bold mb-4">Çalışma Saatleri</h2>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="opacity-60">Pazartesi - Cuma</span>
                  <span>09:00 - 18:00</span>
                </div>
                <div class="flex justify-between">
                  <span class="opacity-60">Cumartesi</span>
                  <span>10:00 - 14:00</span>
                </div>
                <div class="flex justify-between">
                  <span class="opacity-60">Pazar</span>
                  <span class="text-error">Kapalı</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const loading = ref(false)
const submitted = ref(false)

const form = reactive({
  name: '',
  email: '',
  subject: '',
  message: ''
})

// Validation state
const validation = reactive({
  name: { status: '', message: '' },
  email: { status: '', message: '' },
  subject: { status: '', message: '' },
  message: { status: '', message: '' }
})

const validateName = () => {
  const trimmed = form.name.trim()
  if (trimmed.length === 0) {
    validation.name = { status: '', message: '' }
  } else if (trimmed.length < 2) {
    validation.name = { status: 'error', message: 'Ad en az 2 karakter olmalidir' }
  } else {
    validation.name = { status: 'success', message: '' }
  }
}

const validateEmail = () => {
  const trimmed = form.email.trim()
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (trimmed.length === 0) {
    validation.email = { status: '', message: '' }
  } else if (!emailRegex.test(trimmed)) {
    validation.email = { status: 'error', message: 'Gecerli bir e-posta adresi girin' }
  } else {
    validation.email = { status: 'success', message: '' }
  }
}

const validateSubject = () => {
  if (form.subject === '') {
    validation.subject = { status: 'error', message: 'Lutfen bir konu seçin' }
  } else {
    validation.subject = { status: 'success', message: '' }
  }
}

const validateMessage = () => {
  const trimmed = form.message.trim()
  if (trimmed.length === 0) {
    validation.message = { status: '', message: '' }
  } else if (trimmed.length < 20) {
    validation.message = { status: 'error', message: 'Mesaj en az 20 karakter olmalidir' }
  } else {
    validation.message = { status: 'success', message: '' }
  }
}

const isFormValid = computed(() => {
  return form.name.trim().length >= 2 &&
         /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()) &&
         form.subject !== '' &&
         form.message.trim().length >= 20
})

const handleSubmit = async () => {
  loading.value = true
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000))
  submitted.value = true
  loading.value = false
}
</script>
