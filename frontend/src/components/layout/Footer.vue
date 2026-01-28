<template>
  <footer class="bg-dark-card border-t border-dark-border mt-auto">
    <div class="container mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        <!-- About -->
        <div class="md:col-span-2">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <span class="text-2xl font-bold text-white">λ</span>
            </div>
            <h3 class="text-lg font-bold text-text-primary">AGTR Merkezi</h3>
          </div>
          <p class="text-text-secondary text-sm max-w-md">
            Türkiye'nin en profesyonel Half-Life ve CS 1.6 oyun sunucusu platformu.
            Binlerce oyuncu ve yüzlerce aktif sunucu ile gaming deneyiminizi bir üst seviyeye taşıyın.
          </p>
        </div>

        <!-- Links -->
        <div>
          <h3 class="text-base font-semibold text-text-primary mb-4">Hızlı Bağlantılar</h3>
          <ul class="space-y-2 text-sm">
            <li>
              <router-link to="/" class="text-text-secondary hover:text-primary transition-colors">
                Ana Sayfa
              </router-link>
            </li>
            <li>
              <router-link to="/servers" class="text-text-secondary hover:text-primary transition-colors">
                Sunucular
              </router-link>
            </li>
            <li>
              <router-link to="/forum" class="text-text-secondary hover:text-primary transition-colors">
                Forum
              </router-link>
            </li>
            <li>
              <router-link to="/servers/rent" class="text-text-secondary hover:text-primary transition-colors">
                Sunucu Kirala
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Contact & Social -->
        <div>
          <h3 class="text-base font-semibold text-text-primary mb-4">İletişim</h3>
          <ul class="space-y-3 text-sm">
            <li class="flex items-center gap-2 text-text-secondary">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 0 0-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 0 0-5.487 0 12.36 12.36 0 0 0-.617-1.23A.077.077 0 0 0 8.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 0 0-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 0 0 .031.055 20.03 20.03 0 0 0 5.993 2.98.078.078 0 0 0 .084-.026 13.83 13.83 0 0 0 1.226-1.963.074.074 0 0 0-.041-.104 13.201 13.201 0 0 1-1.872-.878.075.075 0 0 1-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 0 1 .078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 0 1 .079.009c.12.098.245.195.372.288a.075.075 0 0 1-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 0 0-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 0 0 .084.028 19.963 19.963 0 0 0 6.002-2.981.076.076 0 0 0 .032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 0 0-.031-.028zM8.02 15.278c-1.182 0-2.157-1.069-2.157-2.38 0-1.312.956-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.956 2.38-2.157 2.38zm7.975 0c-1.183 0-2.157-1.069-2.157-2.38 0-1.312.955-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.946 2.38-2.157 2.38z"/>
              </svg>
              <span>Discord Sunucusu</span>
            </li>
            <li>
              <a href="https://discord.gg/nXXftzaccG" target="_blank" rel="noopener" class="text-primary hover:text-primary-light transition-colors">
                discord.gg/nXXftzaccG
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-dark-border pt-8">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-text-muted">
          <p>&copy; 2026 AGTR Merkezi. Tüm hakları saklıdır.</p>
          <div class="flex items-center gap-6">
            <router-link to="/privacy" class="hover:text-text-primary transition-colors">
              Gizlilik Politikası
            </router-link>
            <router-link to="/terms" class="hover:text-text-primary transition-colors">
              Kullanım Şartları
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
