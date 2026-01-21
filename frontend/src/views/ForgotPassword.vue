<template>
  <div class="min-h-screen flex items-center justify-center py-12">
    <div class="container-custom">
      <div class="max-w-md mx-auto">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-display font-bold mb-2">
            <span class="text-gradient-orange">Şifremi Unuttum</span>
          </h1>
          <p class="opacity-60">
            E-posta adresinizi girin, size şifre sıfırlama linki gönderelim.
          </p>
        </div>

        <div class="glass-card p-6">
          <form v-if="!submitted" @submit.prevent="handleSubmit" class="space-y-4">
            <div class="form-control">
              <label class="label">
                <span class="label-text">E-posta Adresi</span>
              </label>
              <input
                v-model="email"
                type="email"
                placeholder="ornek@email.com"
                class="input input-bordered bg-base-200"
                required
              />
            </div>

            <button type="submit" class="btn-gaming w-full" :disabled="loading">
              <span v-if="loading" class="loading loading-spinner loading-sm"></span>
              <span v-else>Sıfırlama Linki Gönder</span>
            </button>
          </form>

          <div v-else class="text-center py-8">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-success/20 flex items-center justify-center">
              <svg class="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-2">E-posta Gönderildi!</h3>
            <p class="opacity-60 mb-4">
              {{ email }} adresine şifre sıfırlama linki gönderdik.
            </p>
            <router-link to="/login" class="btn btn-outline btn-primary">
              Giriş Sayfasına Don
            </router-link>
          </div>

          <div class="text-center mt-6">
            <router-link to="/login" class="link link-primary text-sm">
              Giriş sayfasına don
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authAPI } from '@/api'

const email = ref('')
const loading = ref(false)
const submitted = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    await authAPI.forgotPassword(email.value)
    submitted.value = true
  } catch (err) {
    // Still show success to prevent email enumeration
    submitted.value = true
  } finally {
    loading.value = false
  }
}
</script>
