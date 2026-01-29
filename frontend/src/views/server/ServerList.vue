<template>
  <div class="relative min-h-screen">
    <!-- Background -->
    <div class="fixed inset-0 z-0">
      <img :src="getBackgroundImage('gaming')" alt="" class="absolute inset-0 w-full h-full object-cover opacity-65" />
      <div class="absolute inset-0 bg-gradient-to-b from-dark-bg/40 via-dark-bg/55 to-dark-bg/70"></div>
    </div>

    <div class="container mx-auto px-4 py-12 relative z-10">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-text-primary mb-4">
          Sunucu Listesi
        </h1>
        <div class="divider w-24 mx-auto mb-6"></div>
        <p class="text-text-secondary text-lg">Topluluk sunucularını keşfedin</p>
      </div>

      <!-- Coming Soon Card -->
      <div class="card p-12 text-center max-w-2xl mx-auto">
        <div class="mb-6">
          <div class="w-24 h-24 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto">
            <span class="text-6xl">🎮</span>
          </div>
        </div>
        <h2 class="text-3xl font-bold text-text-primary mb-4">Çok Yakında!</h2>
        <p class="text-text-secondary text-lg mb-8">
          Sunucu listesi özelliği üzerinde çalışıyoruz. Kısa süre içinde tüm topluluk sunucularını keşfedebileceksiniz.
        </p>
        <router-link to="/servers/rent" class="btn btn-primary text-lg px-8 py-4">
          Sunucu Kirala
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Background image helper
const getBackgroundImage = (name) => {
  const baseUrl = window.location.origin
  return `${baseUrl}/static/images/backgrounds/${name}.jpg`
}
</script>
