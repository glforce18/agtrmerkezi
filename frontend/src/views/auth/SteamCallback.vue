<template>
  <div class="relative min-h-screen flex items-center justify-center px-4 overflow-hidden">
    <!-- Background -->
    <div class="fixed inset-0 z-0">
      <img :src="getBackgroundImage()" alt="" class="absolute inset-0 w-full h-full object-cover opacity-60" />
      <div class="absolute inset-0 bg-gradient-to-b from-dark-bg/40 via-dark-bg/60 to-dark-bg/80"></div>
    </div>

    <div class="text-center relative z-10">
      <div class="glass-card p-12 inline-block">
        <div class="spinner mx-auto mb-6" style="width: 60px; height: 60px; border-width: 4px;"></div>
        <h2 class="text-2xl font-bold text-white mb-2">Steam ile Giriş Yapılıyor...</h2>
        <p class="text-text-secondary">Lütfen bekleyin</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const getBackgroundImage = () => {
  const baseUrl = window.location.origin
  return `${baseUrl}/static/images/backgrounds/gaming.jpg`
}

onMounted(async () => {
  const token = route.query.token
  const error = route.query.error

  if (error) {
    console.error('Steam auth error:', error)
    router.push('/?error=' + error)
    return
  }

  if (token) {
    // Save token with correct key
    localStorage.setItem('auth_token', token)

    // Small delay to ensure session is fully committed in database
    await new Promise(resolve => setTimeout(resolve, 200))

    // Fetch user profile and save to localStorage
    try {
      await authStore.fetchProfile()

      // Full page reload to ensure navbar updates
      window.location.href = '/'
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      window.location.href = '/?error=profile_fetch_failed'
    }
  } else {
    window.location.href = '/?error=no_token'
  }
})
</script>
