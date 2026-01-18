<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0">
      <div class="absolute top-20 left-10 w-72 h-72 bg-orange-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 1s"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 2s"></div>
    </div>

    <!-- Content -->
    <div class="container-custom relative z-10 py-12">
      <div class="max-w-3xl mx-auto">
        <n-card class="glass-card text-center animate-slide-up">
          <div class="p-12">
            <!-- 404 Number with Animation -->
            <div class="relative mb-8">
              <h1 class="text-[180px] md:text-[240px] font-display font-black leading-none mb-4 neon-text-404 select-none">
                404
              </h1>
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20">
                <SearchXIcon class="w-64 h-64 text-orange-500 animate-spin-slow" />
              </div>
            </div>

            <!-- Error Message -->
            <div class="mb-8">
              <h2 class="text-3xl md:text-4xl font-bold mb-4">
                <span class="text-gradient">Sayfa Bulunamadı</span>
              </h2>
              <p class="text-xl text-gray-400 mb-2">
                Aradığınız sayfa mevcut değil veya taşınmış olabilir.
              </p>
              <p class="text-sm text-gray-500">
                URL'yi kontrol edin veya ana sayfaya dönün.
              </p>
            </div>

            <!-- Error Code -->
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/5 rounded-full mb-8">
              <AlertCircleIcon class="w-4 h-4 text-red-500" />
              <span class="text-sm font-mono text-red-500">ERROR_PAGE_NOT_FOUND</span>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <router-link to="/">
                <n-button type="primary" size="large">
                  <template #icon><HomeIcon class="w-5 h-5" /></template>
                  Ana Sayfaya Dön
                </n-button>
              </router-link>
              <n-button size="large" @click="goBack">
                <template #icon><ArrowLeftIcon class="w-5 h-5" /></template>
                Geri Git
              </n-button>
            </div>

            <!-- Quick Links -->
            <div class="pt-8 border-t border-white/10">
              <p class="text-sm text-gray-400 mb-4">Hızlı Bağlantılar</p>
              <div class="flex flex-wrap gap-3 justify-center">
                <router-link to="/servers">
                  <n-button quaternary size="small">
                    <template #icon><ServerIcon class="w-4 h-4" /></template>
                    Sunucular
                  </n-button>
                </router-link>
                <router-link to="/forum">
                  <n-button quaternary size="small">
                    <template #icon><MessageSquareIcon class="w-4 h-4" /></template>
                    Forum
                  </n-button>
                </router-link>
                <router-link to="/shop">
                  <n-button quaternary size="small">
                    <template #icon><ShoppingCartIcon class="w-4 h-4" /></template>
                    Paketler
                  </n-button>
                </router-link>
                <router-link to="/dashboard">
                  <n-button quaternary size="small">
                    <template #icon><LayoutDashboardIcon class="w-4 h-4" /></template>
                    Panel
                  </n-button>
                </router-link>
              </div>
            </div>
          </div>
        </n-card>

        <!-- Additional Info -->
        <div class="text-center mt-8 animate-slide-up" style="animation-delay: 0.2s">
          <p class="text-sm text-gray-500">
            Sorun devam ediyorsa,
            <router-link to="/contact" class="text-orange-500 hover:underline">destek ekibimizle iletişime geçin</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  SearchXIcon,
  AlertCircleIcon,
  HomeIcon,
  ArrowLeftIcon,
  ServerIcon,
  MessageSquareIcon,
  ShoppingCartIcon,
  LayoutDashboardIcon
} from 'lucide-vue-next'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.text-gradient {
  background: linear-gradient(to right, #f97316, #8b5cf6, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.neon-text-404 {
  background: linear-gradient(135deg, #f97316, #8b5cf6, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 80px rgba(99, 102, 241, 0.5);
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% {
    filter: brightness(1);
  }
  50% {
    filter: brightness(1.2);
  }
}

@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.1);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 6s ease-in-out infinite;
}

@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 20s linear infinite;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}
</style>
