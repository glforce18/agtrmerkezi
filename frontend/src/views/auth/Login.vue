<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-block w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-4">
          <span class="text-3xl font-bold text-white">λ</span>
        </div>
        <h1 class="text-3xl font-bold text-text-primary mb-2">Hoş Geldiniz</h1>
        <p class="text-text-secondary">Hesabınıza giriş yapın</p>
      </div>

      <!-- Login Card -->
      <div class="card p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username -->
          <div>
            <label class="block text-text-primary font-medium mb-2">Kullanıcı Adı</label>
            <input
              v-model="form.username"
              type="text"
              class="input"
              placeholder="Kullanıcı adınızı girin"
              required
              autofocus
            />
          </div>

          <!-- Password -->
          <div>
            <label class="block text-text-primary font-medium mb-2">Şifre</label>
            <input
              v-model="form.password"
              type="password"
              class="input"
              placeholder="••••••••"
              required
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-primary w-full" :disabled="loading">
            <span v-if="loading">Giriş yapılıyor...</span>
            <span v-else>Giriş Yap</span>
          </button>
        </form>

        <!-- Register Link -->
        <div class="mt-6 text-center">
          <p class="text-text-secondary text-sm">
            Hesabınız yok mu?
            <router-link to="/auth/register" class="text-primary hover:text-primary-light font-medium">
              Kayıt Olun
            </router-link>
          </p>
        </div>

        <!-- OAuth Options -->
        <div class="mt-8 pt-6 border-t border-dark-border">
          <p class="text-text-muted text-sm text-center mb-4">Veya şununla giriş yapın</p>
          <div class="grid grid-cols-2 gap-3">
            <a :href="authAPI.getOAuthUrl('steam')" class="btn btn-secondary text-sm">
              🎮 Steam
            </a>
            <a :href="authAPI.getOAuthUrl('discord')" class="btn btn-secondary text-sm">
              💬 Discord
            </a>
          </div>
        </div>
      </div>

      <!-- Back to Home -->
      <div class="text-center mt-6">
        <router-link to="/" class="text-text-muted hover:text-text-primary text-sm">
          ← Ana Sayfaya Dön
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authAPI from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  const result = await authStore.login(form.value)

  if (result.success) {
    router.push('/servers/my')
  } else {
    error.value = result.error || 'Giriş başarısız oldu'
  }

  loading.value = false
}
</script>
