<template>
  <div id="app" class="min-h-screen flex flex-col">
    <Navbar />
    <main class="flex-1">
      <RouterView />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.init()
})
</script>
