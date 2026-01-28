<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12">
    <div class="max-w-md w-full">
      <!-- Logo/Title -->
      <div class="text-center mb-8">
        <div class="text-6xl lambda-symbol neon-orange mb-4">λ</div>
        <h1 class="text-3xl font-lambda font-bold neon-orange">GİRİŞ YAP</h1>
        <p class="text-text-secondary mt-2">AGTR Merkezi'ne hoş geldiniz</p>
      </div>

      <!-- Error Message -->
      <div
        v-if="error"
        class="mb-6 p-4 bg-combine-red bg-opacity-10 border border-combine-red rounded text-combine-red text-sm"
      >
        {{ error }}
      </div>

      <!-- Login Form -->
      <form v-if="!requires2FA" @submit.prevent="handleLogin" class="space-y-6">
        <!-- Username/Email -->
        <div>
          <label for="username" class="block text-sm font-medium text-text-primary mb-2">
            Kullanıcı Adı veya E-posta
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-3 bg-cyber-elevated border border-cyber-border rounded focus:outline-none focus:border-lambda-orange text-text-primary"
            placeholder="kullanici_adi"
          />
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-sm font-medium text-text-primary mb-2">
            Şifre
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-3 bg-cyber-elevated border border-cyber-border rounded focus:outline-none focus:border-lambda-orange text-text-primary"
            placeholder="••••••••"
          />
        </div>

        <!-- Remember Me -->
        <div class="flex items-center justify-between">
          <label class="flex items-center">
            <input
              v-model="form.remember"
              type="checkbox"
              class="mr-2 rounded bg-cyber-elevated border-cyber-border"
            />
            <span class="text-sm text-text-secondary">Beni Hatırla</span>
          </label>

          <router-link to="/forgot-password" class="text-sm text-lambda-orange hover:text-lambda-orange-dark">
            Şifremi Unuttum?
          </router-link>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="inline-block spinner"></span>
          <span v-else>GİRİŞ YAP</span>
        </button>

        <!-- OAuth Buttons -->
        <div class="space-y-3">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-cyber-border"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-cyber-black text-text-secondary">veya</span>
            </div>
          </div>

          <a
            :href="`/api/auth/oauth/steam`"
            class="w-full flex items-center justify-center gap-3 py-3 border-2 border-text-secondary text-text-primary font-medium rounded hover:border-lambda-orange hover:text-lambda-orange transition-colors"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2a10 10 0 0 0-10 10 9.97 9.97 0 0 0 6.51 9.36l1.31-3.18a3.98 3.98 0 1 1 5.29-1.62l3.44.92A10 10 0 0 0 12 2z"/>
            </svg>
            Steam ile Giriş Yap
          </a>
        </div>

        <!-- Register Link -->
        <p class="text-center text-sm text-text-secondary">
          Hesabınız yok mu?
          <router-link to="/register" class="text-lambda-orange hover:text-lambda-orange-dark font-medium">
            Kayıt Ol
          </router-link>
        </p>
      </form>

      <!-- 2FA Form -->
      <form v-else @submit.prevent="handle2FA" class="space-y-6">
        <div>
          <label for="code" class="block text-sm font-medium text-text-primary mb-2">
            2FA Kodu
          </label>
          <input
            id="code"
            v-model="twoFactorCode"
            type="text"
            required
            maxlength="6"
            class="w-full px-4 py-3 bg-cyber-elevated border border-cyber-border rounded focus:outline-none focus:border-lambda-orange text-text-primary text-center text-2xl font-hev tracking-widest"
            placeholder="000000"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all duration-300 disabled:opacity-50"
        >
          <span v-if="loading" class="inline-block spinner"></span>
          <span v-else>DOĞRULA</span>
        </button>

        <button
          type="button"
          @click="requires2FA = false"
          class="w-full py-2 text-text-secondary hover:text-text-primary text-sm"
        >
          Geri
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
  remember: false
})

const twoFactorCode = ref('')
const requires2FA = ref(false)
const loading = ref(false)
const error = ref(null)

async function handleLogin() {
  loading.value = true
  error.value = null

  try {
    const result = await authStore.login({
      username: form.value.username,
      password: form.value.password,
      remember_me: form.value.remember
    })

    if (result.requires2FA) {
      requires2FA.value = true
    } else {
      // Redirect to intended page or home
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    }
  } catch (err) {
    error.value = authStore.error || 'Giriş başarısız'
  } finally {
    loading.value = false
  }
}

async function handle2FA() {
  loading.value = true
  error.value = null

  try {
    await authStore.login2FA(twoFactorCode.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    error.value = authStore.error || '2FA doğrulama başarısız'
  } finally {
    loading.value = false
  }
}
</script>
