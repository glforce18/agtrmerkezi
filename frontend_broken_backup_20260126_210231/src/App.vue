<template>
  <div id="app" class="min-h-screen bg-cyber-black">
    <!-- Background Effects -->
    <div class="fixed inset-0 grid-bg pointer-events-none"></div>
    <div class="scan-lines fixed inset-0 pointer-events-none opacity-30"></div>

    <!-- Navigation -->
    <Navbar />

    <!-- Main Content -->
    <main class="relative z-10">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="relative z-10 mt-16 border-t border-cyber-border bg-cyber-darker bg-opacity-50 backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Brand -->
          <div>
            <div class="flex items-center gap-2 mb-4">
              <div class="text-3xl text-lambda-orange">λ</div>
              <div class="flex flex-col">
                <span class="text-lg font-lambda font-bold text-lambda-orange">AGTR MERKEZI</span>
                <span class="text-xs font-hev text-text-secondary">Gaming Platform</span>
              </div>
            </div>
            <p class="text-sm text-text-secondary font-hev">
              Türkiye'nin en büyük Half-Life ve Counter-Strike 1.6 oyun sunucusu platformu
            </p>
          </div>

          <!-- Links -->
          <div>
            <h4 class="font-lambda font-bold text-text-primary mb-3">HIZLI ERİŞİM</h4>
            <ul class="space-y-2">
              <li><router-link to="/servers" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Sunucular</router-link></li>
              <li><router-link to="/servers/rent" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Sunucu Kirala</router-link></li>
              <li><router-link to="/forum" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Forum</router-link></li>
              <li><router-link to="/profile" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Profilim</router-link></li>
            </ul>
          </div>

          <!-- Support -->
          <div>
            <h4 class="font-lambda font-bold text-text-primary mb-3">DESTEK</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">SSS</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Kullanım Kılavuzu</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">İletişim</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Destek Talebi</a></li>
            </ul>
          </div>

          <!-- Legal -->
          <div>
            <h4 class="font-lambda font-bold text-text-primary mb-3">YASAL</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Kullanım Koşulları</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Gizlilik Politikası</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">Çerez Politikası</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-lambda-orange font-hev transition-all">KVKK</a></li>
            </ul>
          </div>
        </div>

        <div class="mt-8 pt-6 border-t border-cyber-border text-center">
          <p class="text-sm text-text-secondary font-hev">
            © 2024 AGTR Merkezi. Tüm hakları saklıdır.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth from localStorage
  authStore.init()

  // Check auth status if token exists
  if (authStore.token) {
    authStore.checkAuth()
  }
})
</script>

<style>
/* Additional global styles if needed */
</style>
