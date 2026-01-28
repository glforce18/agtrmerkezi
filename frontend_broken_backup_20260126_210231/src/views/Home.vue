<template>
  <div class="relative">
    <!-- Hero Section -->
    <section class="min-h-screen flex items-center justify-center px-4">
      <div class="max-w-6xl w-full text-center">
        <!-- Lambda Symbol -->
        <div class="mb-8 inline-block">
          <div class="text-8xl md:text-9xl lambda-symbol neon-orange animate-pulse-glow">
            λ
          </div>
        </div>

        <!-- Title -->
        <h1 class="text-5xl md:text-7xl font-lambda font-bold mb-6 tracking-wider">
          <span class="neon-orange">AGTR</span>
          <span class="text-text-primary">MERKEZI</span>
        </h1>

        <!-- Subtitle -->
        <p class="text-xl md:text-2xl text-text-secondary mb-12 font-hev">
          Half-Life & Counter-Strike 1.6 Gaming Platform
        </p>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <router-link
            to="/servers/rent"
            class="px-8 py-4 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all duration-300 transform hover:scale-105"
          >
            SUNUCU KİRALA
          </router-link>

          <router-link
            to="/servers"
            class="px-8 py-4 border-2 border-lambda-orange text-lambda-orange font-lambda font-bold rounded hover:bg-lambda-orange hover:text-cyber-black transition-all duration-300"
          >
            SUNUCULARI KEŞFET
          </router-link>

          <router-link
            to="/forum"
            class="px-8 py-4 border-2 border-hev-cyan text-hev-cyan font-lambda font-bold rounded hover:bg-hev-cyan hover:text-cyber-black transition-all duration-300"
          >
            FORUM
          </router-link>
        </div>

        <!-- Stats -->
        <div class="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div class="stat-card">
            <div class="text-4xl font-lambda font-bold neon-orange">{{ stats.servers }}</div>
            <div class="text-text-secondary mt-2">Aktif Sunucu</div>
          </div>
          <div class="stat-card">
            <div class="text-4xl font-lambda font-bold neon-cyan">{{ stats.players }}</div>
            <div class="text-text-secondary mt-2">Oyuncu</div>
          </div>
          <div class="stat-card">
            <div class="text-4xl font-lambda font-bold neon-purple">{{ stats.users }}</div>
            <div class="text-text-secondary mt-2">Kayıtlı Kullanıcı</div>
          </div>
          <div class="stat-card">
            <div class="text-4xl font-lambda font-bold neon-green">{{ stats.forumTopics }}</div>
            <div class="text-text-secondary mt-2">Forum Konusu</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  servers: 0,
  players: 0,
  users: 0,
  forumTopics: 0
})

// Animate numbers on mount
onMounted(() => {
  animateValue('servers', 0, 156, 2000)
  animateValue('players', 0, 2847, 2000)
  animateValue('users', 0, 15432, 2000)
  animateValue('forumTopics', 0, 8921, 2000)
})

function animateValue(key, start, end, duration) {
  const startTime = performance.now()
  const step = (currentTime) => {
    const progress = Math.min((currentTime - startTime) / duration, 1)
    stats.value[key] = Math.floor(progress * (end - start) + start)
    if (progress < 1) {
      requestAnimationFrame(step)
    }
  }
  requestAnimationFrame(step)
}
</script>

<style scoped>
.stat-card {
  @apply p-6 bg-cyber-elevated border border-cyber-border rounded-lg hover:border-lambda-orange transition-colors duration-300;
}
</style>
