<template>
  <div id="app" class="min-h-screen relative">
    <!-- Particle Background Effect -->
    <ParticleBackground />

    <!-- Main Content -->
    <div class="relative z-10">
      <!-- Navbar -->
      <Navbar />

      <!-- Notifications -->
      <Notifications />

      <!-- Router View -->
      <router-view />

      <!-- Footer -->
      <Footer />
    </div>

    <!-- Command Palette (Cmd+K) -->
    <CommandPalette />

    <!-- Floating Action Button -->
    <FloatingActionButton />

    <!-- Scroll Progress Bar -->
    <div class="scroll-progress fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-secondary to-accent z-[9999] origin-left" :style="{ transform: `scaleX(${scrollProgress})` }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import Notifications from '@/components/common/Notifications.vue'
import CommandPalette from '@/components/common/CommandPalette.vue'
import FloatingActionButton from '@/components/common/FloatingActionButton.vue'
import ParticleBackground from '@/components/effects/ParticleBackground.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const scrollProgress = ref(0)

const handleScroll = () => {
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
  const scrollTop = window.scrollY
  scrollProgress.value = scrollHeight > 0 ? scrollTop / scrollHeight : 0
}

onMounted(async () => {
  // Initialize theme
  themeStore.setTheme(themeStore.currentTheme)

  // Try to restore auth session
  if (authStore.token) {
    await authStore.fetchUser()
  }

  // Mark app as loaded (prevent FOUC)
  document.documentElement.classList.add('loaded')

  // Add scroll listener for progress bar
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style>
/* Global styles are in style.css */
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
