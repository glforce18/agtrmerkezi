<template>
  <div class="min-h-screen  flex items-center justify-center relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0">
      <div class="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 1s"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-accent/10 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 2s"></div>
    </div>

    <!-- Content -->
    <div class="container-custom relative z-10 py-12">
      <div class="max-w-3xl mx-auto">
        <BaseCard variant="glass" shadow class="text-center animate-slide-up">
          <div class="p-12">
            <!-- 404 Number with Animation -->
            <div class="relative mb-8">
              <h1 class="text-[180px] md:text-[240px] font-display font-black leading-none mb-4 neon-text-404 select-none">
                404
              </h1>
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20">
                <SearchXIcon class="w-64 h-64 text-primary animate-spin-slow" />
              </div>
            </div>

            <!-- Error Message -->
            <div class="mb-8">
              <h2 class="text-3xl md:text-4xl font-bold mb-4">
                <span class="neon-text">Sayfa Bulunamadı</span>
              </h2>
              <p class="text-xl opacity-60 mb-2">
                Aradığınız sayfa mevcut değil veya taşınmış olabilir.
              </p>
              <p class="text-sm opacity-50">
                URL'yi kontrol edin veya ana sayfaya dönün.
              </p>
            </div>

            <!-- Error Code -->
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-base-200/50 rounded-full mb-8">
              <AlertCircleIcon class="w-4 h-4 text-error" />
              <span class="text-sm font-mono text-error">ERROR_PAGE_NOT_FOUND</span>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <router-link to="/">
                <BaseButton variant="gaming" size="lg">
                  <HomeIcon class="w-5 h-5 mr-2" />
                  Ana Sayfaya Dön
                </BaseButton>
              </router-link>
              <BaseButton variant="outline" size="lg" @click="goBack">
                <ArrowLeftIcon class="w-5 h-5 mr-2" />
                Geri Git
              </BaseButton>
            </div>

            <!-- Quick Links -->
            <div class="pt-8 border-t border-base-300">
              <p class="text-sm opacity-60 mb-4">Hızlı Bağlantılar</p>
              <div class="flex flex-wrap gap-3 justify-center">
                <router-link to="/servers">
                  <button class="btn btn-sm btn-ghost">
                    <ServerIcon class="w-4 h-4 mr-1" />
                    Sunucular
                  </button>
                </router-link>
                <router-link to="/forum">
                  <button class="btn btn-sm btn-ghost">
                    <MessageSquareIcon class="w-4 h-4 mr-1" />
                    Forum
                  </button>
                </router-link>
                <router-link to="/shop">
                  <button class="btn btn-sm btn-ghost">
                    <ShoppingCartIcon class="w-4 h-4 mr-1" />
                    Paketler
                  </button>
                </router-link>
                <router-link to="/dashboard">
                  <button class="btn btn-sm btn-ghost">
                    <LayoutDashboardIcon class="w-4 h-4 mr-1" />
                    Panel
                  </button>
                </router-link>
              </div>
            </div>
          </div>
        </BaseCard>

        <!-- Additional Info -->
        <div class="text-center mt-8 animate-slide-up" style="animation-delay: 0.2s">
          <p class="text-sm opacity-50">
            Sorun devam ediyorsa,
            <router-link to="/contact" class="link link-primary">destek ekibimizle iletişime geçin</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
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
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

.neon-text-404 {
  @apply text-transparent bg-clip-text bg-gradient-to-br from-primary via-secondary to-accent;
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
