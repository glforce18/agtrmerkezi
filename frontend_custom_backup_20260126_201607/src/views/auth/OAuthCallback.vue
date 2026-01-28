<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="max-w-md w-full text-center">
      <div class="animate-spin text-6xl neon-orange mb-4">λ</div>

      <h1 class="text-2xl font-lambda font-bold text-text-primary mb-2">
        {{ message }}
      </h1>

      <p v-if="provider" class="text-text-secondary font-hev text-sm">
        {{ providerName }} ile giriş yapılıyor...
      </p>

      <p v-if="error" class="text-combine-red font-hev text-sm mt-4">
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authAPI from '@/api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const message = ref('Giriş yapılıyor...')
const error = ref(null)
const provider = ref(null)

const providerNames = {
  steam: 'Steam',
  discord: 'Discord',
  google: 'Google'
}

const providerName = ref('')

onMounted(async () => {
  // URL parametrelerini al
  const token = route.query.token
  provider.value = route.query.provider
  const errorParam = route.query.error

  if (provider.value) {
    providerName.value = providerNames[provider.value] || provider.value
  }

  // Hata kontrolü
  if (errorParam) {
    error.value = getErrorMessage(errorParam)
    message.value = 'Giriş başarısız'

    setTimeout(() => {
      router.push('/login')
    }, 3000)
    return
  }

  // Token kontrolü
  if (!token) {
    error.value = 'Token bulunamadı'
    message.value = 'Giriş başarısız'

    setTimeout(() => {
      router.push('/login')
    }, 3000)
    return
  }

  try {
    // Token'ı localStorage'a kaydet
    localStorage.setItem('auth_token', token)

    // Kullanıcı bilgilerini çek
    const response = await authAPI.getMe()
    const user = response.data

    // Auth store'u güncelle
    authStore.setAuth(token, user)

    message.value = 'Giriş başarılı!'

    // Ana sayfaya yönlendir
    setTimeout(() => {
      router.push('/')
    }, 1000)

  } catch (err) {
    console.error('OAuth callback error:', err)
    error.value = 'Kullanıcı bilgileri alınamadı'
    message.value = 'Giriş başarısız'

    localStorage.removeItem('auth_token')

    setTimeout(() => {
      router.push('/login')
    }, 3000)
  }
})

function getErrorMessage(errorCode) {
  const errors = {
    'steam_verification_failed': 'Steam doğrulama başarısız',
    'steam_no_code': 'Steam kimlik kodu alınamadı',
    'steam_token_failed': 'Steam token alınamadı',
    'steam_failed': 'Steam girişi başarısız',
    'discord_no_code': 'Discord kimlik kodu alınamadı',
    'discord_token_failed': 'Discord token alınamadı',
    'discord_failed': 'Discord girişi başarısız',
    'google_no_code': 'Google kimlik kodu alınamadı',
    'google_token_failed': 'Google token alınamadı',
    'google_failed': 'Google girişi başarısız',
    'account_banned': 'Hesabınız engellenmiş',
    'account_suspended': 'Hesabınız askıya alınmış'
  }

  return errors[errorCode] || 'Bilinmeyen hata oluştu'
}
</script>

<style scoped>
.neon-orange {
  color: #FF6B35;
  text-shadow: 0 0 10px rgba(255, 107, 53, 0.8);
}
</style>
