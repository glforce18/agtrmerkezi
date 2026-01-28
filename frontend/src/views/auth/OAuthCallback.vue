<template>
  <div class="container mx-auto px-4 py-12 text-center">
    <div class="text-primary text-6xl mb-4">⏳</div>
    <h1 class="text-2xl font-lambda text-white mb-4">Giriş yapılıyor...</h1>
    <p class="text-gray-400">Lütfen bekleyin</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authAPI from '@/api/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  const token = route.query.token

  if (token) {
    try {
      const response = await authAPI.getMe()
      authStore.setAuth(token, response.data)

      setTimeout(() => {
        router.push('/servers/my')
      }, 1000)
    } catch (error) {
      console.error('OAuth callback error:', error)
      router.push('/login')
    }
  } else {
    router.push('/login')
  }
})
</script>
