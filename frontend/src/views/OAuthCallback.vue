<template>
  <div class="min-h-screen flex items-center justify-center bg-base-100">
    <div class="text-center">
      <div class="loading loading-spinner loading-lg text-primary mb-4"></div>
      <p class="text-lg">Giriş yapılıyor...</p>
      <p v-if="error" class="text-error mt-4">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const error = ref(null)

onMounted(async () => {
  const token = route.query.token
  const provider = route.query.provider

  console.log('OAuth callback received, token:', token ? 'present' : 'missing')

  if (!token) {
    error.value = 'Token bulunamadı'
    setTimeout(() => router.push('/login?error=no_token'), 2000)
    return
  }

  try {
    // Token'ı localStorage'a kaydet
    localStorage.setItem('access_token', token)
    console.log('Token saved to localStorage')

    // Kullanıcı bilgilerini doğrudan API'den al
    const userData = await authAPI.me()
    console.log('User data fetched:', userData)

    if (userData && userData.id) {
      // Auth store'u güncelle (Pinia $patch kullan)
      authStore.$patch({
        token: token,
        user: userData
      })

      console.log('Auth store updated, redirecting to dashboard')
      // Başarılı giriş - dashboard'a yönlendir
      router.push('/dashboard')
    } else {
      throw new Error('Invalid user data received')
    }
  } catch (err) {
    console.error('OAuth callback error:', err)
    error.value = err.response?.data?.detail || err.message || 'Giriş işlemi başarısız'
    localStorage.removeItem('access_token')
    setTimeout(() => router.push('/login?error=fetch_failed'), 2000)
  }
})
</script>
