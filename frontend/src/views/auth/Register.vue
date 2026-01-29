<template>
  <div class="relative min-h-screen flex items-center justify-center px-4 py-12 overflow-hidden">
    <!-- Background -->
    <div class="fixed inset-0 z-0">
      <img :src="getBackgroundImage()" alt="" class="absolute inset-0 w-full h-full object-cover opacity-60" />
      <div class="absolute inset-0 bg-gradient-to-b from-dark-bg/40 via-dark-bg/60 to-dark-bg/80"></div>
    </div>

    <div class="w-full max-w-md relative z-10">
      <!-- Logo & Title -->
      <div class="text-center mb-8 fade-in-up">
        <div class="inline-block w-20 h-20 bg-gradient-to-br from-primary to-orange-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg glow">
          <span class="text-4xl font-bold text-white">λ</span>
        </div>
        <h1 class="text-4xl font-bold mb-3">
          <span class="text-gradient-animated">Hesap Oluştur</span>
        </h1>
        <p class="text-text-secondary text-lg">Steam ile hızlıca kayıt olun</p>
      </div>

      <!-- Steam Register Card -->
      <div class="glass-card p-10 neon-border fade-in-up delay-100">
        <!-- Steam Info -->
        <div class="text-center mb-8">
          <div class="w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-lg">
            <svg class="w-14 h-14 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10c-4.6 0-8.45-3.08-9.64-7.27l3.83 1.58a2.84 2.84 0 0 0 2.78 2.27c1.56 0 2.83-1.27 2.83-2.83v-.13l3.4-2.43h.08c2.08 0 3.77-1.69 3.77-3.77s-1.69-3.77-3.77-3.77-3.78 1.69-3.78 3.77v.05l-2.37 3.46-.16-.01c-.59 0-1.14.18-1.59.49L2 11.2C2.43 6.05 6.73 2 12 2M8.28 17.17c.8.33 1.72-.04 2.05-.84.33-.8-.05-1.71-.83-2.04l-1.28-.53c.49-.18 1.04-.19 1.56.03.53.21.94.62 1.15 1.15.22.52.22 1.10 0 1.62-.43 1.08-1.7 1.6-2.78 1.15s-1.6-1.7-1.15-2.78l1.28.53v.71zm9.52-7.75c0 1.39-1.13 2.52-2.52 2.52a2.52 2.52 0 0 1-2.51-2.52 2.5 2.5 0 0 1 2.51-2.51c1.39 0 2.52 1.12 2.52 2.51zm-4.4 0c0 1.04.84 1.89 1.89 1.89 1.04 0 1.88-.85 1.88-1.89s-.84-1.89-1.88-1.89c-1.05 0-1.89.85-1.89 1.89z"/>
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-white mb-2">Steam ile Kayıt Ol</h2>
          <p class="text-text-secondary">
            Steam hesabınızla anında kayıt olun.<br/>
            Kullanıcı adı, şifre gerekmez.
          </p>
        </div>

        <!-- Steam Register Button -->
        <a
          :href="steamLoginUrl"
          class="btn-steam group"
        >
          <svg class="w-6 h-6 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10c-4.6 0-8.45-3.08-9.64-7.27l3.83 1.58a2.84 2.84 0 0 0 2.78 2.27c1.56 0 2.83-1.27 2.83-2.83v-.13l3.4-2.43h.08c2.08 0 3.77-1.69 3.77-3.77s-1.69-3.77-3.77-3.77-3.78 1.69-3.78 3.77v.05l-2.37 3.46-.16-.01c-.59 0-1.14.18-1.59.49L2 11.2C2.43 6.05 6.73 2 12 2M8.28 17.17c.8.33 1.72-.04 2.05-.84.33-.8-.05-1.71-.83-2.04l-1.28-.53c.49-.18 1.04-.19 1.56.03.53.21.94.62 1.15 1.15.22.52.22 1.10 0 1.62-.43 1.08-1.7 1.6-2.78 1.15s-1.6-1.7-1.15-2.78l1.28.53v.71zm9.52-7.75c0 1.39-1.13 2.52-2.52 2.52a2.52 2.52 0 0 1-2.51-2.52 2.5 2.5 0 0 1 2.51-2.51c1.39 0 2.52 1.12 2.52 2.51zm-4.4 0c0 1.04.84 1.89 1.89 1.89 1.04 0 1.88-.85 1.88-1.89s-.84-1.89-1.88-1.89c-1.05 0-1.89.85-1.89 1.89z"/>
          </svg>
          <span class="text-lg font-bold">Steam ile Kayıt Ol</span>
          <span class="text-sm opacity-80">→</span>
        </a>

        <!-- Info -->
        <div class="mt-6 p-4 bg-primary/10 border border-primary/30 rounded-lg">
          <p class="text-sm text-text-secondary text-center">
            <span class="text-primary font-semibold">✅ Hızlı</span> ·
            Tek tıkla kayıt ·
            Profil otomatik oluşturulur
          </p>
        </div>

        <!-- Already have account -->
        <div class="mt-6 text-center">
          <p class="text-text-secondary text-sm">
            Zaten hesabınız var mı?
            <router-link to="/login" class="text-primary hover:text-primary-light font-medium">
              Giriş Yapın
            </router-link>
          </p>
        </div>
      </div>

      <!-- Back to Home -->
      <div class="text-center mt-6 fade-in-up delay-200">
        <router-link to="/" class="text-text-primary hover:text-primary text-sm inline-flex items-center gap-2 transition-colors">
          <span>←</span> Ana Sayfaya Dön
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const steamLoginUrl = computed(() => {
  return `${API_URL}/api/auth/steam/login`
})

const getBackgroundImage = () => {
  const baseUrl = window.location.origin
  return `${baseUrl}/static/images/backgrounds/energy.jpg`
}
</script>

<style scoped>
.btn-steam {
  @apply w-full py-4 px-6 rounded-xl font-bold text-white;
  @apply flex items-center justify-center gap-3;
  @apply transition-all duration-300;
  background: linear-gradient(135deg, #1b2838 0%, #2a475e 100%);
  border: 2px solid rgba(102, 192, 244, 0.3);
  box-shadow: 0 8px 24px rgba(27, 40, 56, 0.4);
}

.btn-steam:hover {
  background: linear-gradient(135deg, #2a475e 0%, #1b2838 100%);
  border-color: rgba(102, 192, 244, 0.6);
  box-shadow: 0 12px 32px rgba(27, 40, 56, 0.6);
  transform: translateY(-2px);
}

.btn-steam:active {
  transform: translateY(0);
}
</style>
