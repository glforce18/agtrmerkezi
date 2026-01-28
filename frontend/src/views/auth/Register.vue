<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-block w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-4">
          <span class="text-3xl font-bold text-white">λ</span>
        </div>
        <h1 class="text-3xl font-bold text-text-primary mb-2">Hesap Oluştur</h1>
        <p class="text-text-secondary">AGTR Merkezi'ne katılın</p>
      </div>

      <!-- Register Card -->
      <div class="card p-8">
        <form @submit.prevent="handleRegister" class="space-y-5">
          <!-- Username -->
          <div>
            <label class="block text-text-primary font-medium mb-2">Kullanıcı Adı</label>
            <input
              v-model="form.username"
              type="text"
              class="input"
              placeholder="kullaniciadi"
              required
              minlength="3"
              maxlength="20"
              :disabled="loading"
            />
            <p class="text-text-muted text-xs mt-1">3-20 karakter, sadece harf, rakam ve alt çizgi</p>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-text-primary font-medium mb-2">E-posta</label>
            <input
              v-model="form.email"
              type="email"
              class="input"
              placeholder="ornek@email.com"
              required
              :disabled="loading"
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
              minlength="8"
              :disabled="loading"
            />
            <p class="text-text-muted text-xs mt-1">En az 8 karakter</p>
          </div>

          <!-- Password Confirm -->
          <div>
            <label class="block text-text-primary font-medium mb-2">Şifre Tekrar</label>
            <input
              v-model="form.password_confirm"
              type="password"
              class="input"
              placeholder="••••••••"
              required
              minlength="8"
              :disabled="loading"
            />
          </div>

          <!-- Terms -->
          <div class="flex items-start gap-3">
            <input
              v-model="form.accept_terms"
              type="checkbox"
              id="terms"
              class="mt-1 w-4 h-4 text-primary bg-dark-elevated border-dark-border rounded focus:ring-primary"
              required
              :disabled="loading"
            />
            <label for="terms" class="text-text-secondary text-sm">
              <router-link to="/terms" class="text-primary hover:text-primary-light">Kullanım Şartlarını</router-link>
              ve
              <router-link to="/privacy" class="text-primary hover:text-primary-light">Gizlilik Politikasını</router-link>
              kabul ediyorum
            </label>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading || !form.accept_terms"
            class="btn btn-primary w-full"
          >
            <span v-if="loading">Kayıt Yapılıyor...</span>
            <span v-else">Kayıt Ol</span>
          </button>
        </form>

        <!-- Divider -->
        <div class="divider my-6"></div>

        <!-- OAuth Buttons -->
        <div class="space-y-3">
          <p class="text-text-muted text-sm text-center mb-4">Veya şununla kayıt olun</p>
          <div class="grid grid-cols-2 gap-3">
            <a :href="steamLoginUrl" class="btn btn-secondary text-sm">
              🎮 Steam
            </a>
            <a :href="discordLoginUrl" class="btn btn-secondary text-sm">
              💬 Discord
            </a>
          </div>
        </div>

        <!-- Login Link -->
        <div class="mt-6 text-center">
          <p class="text-text-secondary text-sm">
            Zaten hesabınız var mı?
            <router-link to="/login" class="text-primary hover:text-primary-light font-medium">
              Giriş Yapın
            </router-link>
          </p>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authAPI from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref(null)

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  accept_terms: false
})

const steamLoginUrl = computed(() => '/api/auth/steam/login')
const discordLoginUrl = computed(() => '/api/auth/discord/login')

const handleRegister = async () => {
  error.value = null

  // Validate passwords match
  if (form.value.password !== form.value.password_confirm) {
    error.value = 'Şifreler eşleşmiyor'
    return
  }

  // Validate username format
  if (!/^[a-zA-Z0-9_]+$/.test(form.value.username)) {
    error.value = 'Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir'
    return
  }

  loading.value = true

  try {
    // Register API returns AuthResponse with token and user
    const response = await authAPI.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      password_confirm: form.value.password_confirm
    })

    // Backend returns token and user in response.data
    const token = response.data.token || response.data.access_token
    const user = response.data.user

    if (token && user) {
      // Set auth directly from registration response
      authStore.setAuth(token, user)
      router.push('/servers/my')
    } else {
      // Registration successful but no token, try auto-login
      const result = await authStore.login({
        username: form.value.username,
        password: form.value.password
      })

      if (result.success) {
        router.push('/servers/my')
      } else {
        // Registration successful but login failed, redirect to login page
        router.push({
          path: '/login',
          query: { message: 'Kayıt başarılı! Giriş yapabilirsiniz.' }
        })
      }
    }
  } catch (err) {
    console.error('Register error:', err.response?.data)
    error.value = err.response?.data?.detail || 'Kayıt sırasında bir hata oluştu'
  } finally {
    loading.value = false
  }
}
</script>
