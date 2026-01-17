<template>
  <footer class="section-alt border-t border-base-300 mt-auto">
    <div class="container-custom">
      <!-- Main Footer Content -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 py-12">
        <!-- Brand Column -->
        <div class="space-y-4">
          <router-link to="/" class="flex items-center gap-2">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
              <span class="text-white font-bold text-xl">λ</span>
            </div>
            <div>
              <span class="font-display font-bold text-lg">AGTR</span>
              <span class="text-orange-500 font-display font-bold text-lg">Merkezi</span>
            </div>
          </router-link>
          <p class="text-sm opacity-60">
            Counter-Strike 1.6 Turkiye Toplulugu. Binlerce oyuncunun bulustugu,
            turnuvalarin duzenlendigi platform.
          </p>
          <div class="flex gap-3">
            <!-- Discord -->
            <a
              href="https://discord.gg/agtrmerkezi"
              target="_blank"
              class="social-btn w-10 h-10 rounded-lg flex items-center justify-center transition-all group"
              title="Discord"
            >
              <svg class="w-5 h-5 opacity-60 group-hover:opacity-100 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03z"/>
              </svg>
            </a>
            <!-- Twitter/X -->
            <a
              href="https://twitter.com/agtrmerkezi"
              target="_blank"
              class="social-btn w-10 h-10 rounded-lg flex items-center justify-center transition-all group"
              title="Twitter"
            >
              <svg class="w-5 h-5 opacity-60 group-hover:opacity-100 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
              </svg>
            </a>
            <!-- Steam -->
            <a
              href="https://steamcommunity.com/groups/agtrmerkezi"
              target="_blank"
              class="social-btn w-10 h-10 rounded-lg flex items-center justify-center transition-all group"
              title="Steam"
            >
              <svg class="w-5 h-5 opacity-60 group-hover:opacity-100 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0z"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="font-bold text-lg mb-4">Hizli Linkler</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="link in quickLinks" :key="link.path">
              <router-link :to="link.path" class="opacity-60 hover:opacity-100 hover:text-orange-500 transition-all">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Resources -->
        <div>
          <h3 class="font-bold text-lg mb-4">Kaynaklar</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="link in resourceLinks" :key="link.path">
              <router-link :to="link.path" class="opacity-60 hover:opacity-100 hover:text-orange-500 transition-all">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Status & Legal -->
        <div>
          <h3 class="font-bold text-lg mb-4">Yasal</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="link in legalLinks" :key="link.path">
              <router-link :to="link.path" class="opacity-60 hover:opacity-100 hover:text-orange-500 transition-all">
                {{ link.label }}
              </router-link>
            </li>
          </ul>

          <!-- System Status -->
          <div class="status-box mt-6 p-3 rounded-lg">
            <div class="flex items-center gap-2 mb-1">
              <div class="status-online w-2 h-2"></div>
              <span class="text-xs font-semibold text-green-500">Sistem Calisiyor</span>
            </div>
            <div class="text-xs opacity-50">99.9% Uptime</div>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-base-300 py-6">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <div class="text-sm opacity-60">
            &copy; {{ currentYear }} <span class="text-gradient-orange font-semibold">AGTR Merkezi</span>.
            Tum haklari saklidir.
          </div>

          <div class="flex items-center gap-6 text-xs opacity-50">
            <a href="https://discord.gg/agtrmerkezi" target="_blank" class="flex items-center gap-2 hover:text-orange-500 transition-colors">
              <span>Discord'a Katıl</span>
            </a>
          </div>

          <div class="text-sm opacity-50">
            v7.0.0
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())

const quickLinks = [
  { path: '/', label: 'Ana Sayfa' },
  { path: '/servers', label: 'Sunucular' },
  { path: '/forum', label: 'Forum' },
  { path: '/leaderboard', label: 'Siralamalar' },
  { path: '/shop', label: 'Premium' }
]

const resourceLinks = [
  { path: '/docs', label: 'Dokumantasyon' },
  { path: '/tutorials', label: 'Egitimler' },
  { path: '/faq', label: 'SSS' },
  { path: '/support', label: 'Destek' }
]

const legalLinks = [
  { path: '/terms', label: 'Kullanim Kosullari' },
  { path: '/privacy', label: 'Gizlilik Politikasi' },
  { path: '/contact', label: 'Iletisim' }
]
</script>

<style scoped>
/* Social Media Buttons */
.social-btn {
  background-color: var(--bg-secondary, #1e293b);
  border: 1px solid var(--border-color, #475569);
}

.social-btn:hover {
  background-color: var(--primary-color, #f97316);
  border-color: var(--primary-color, #f97316);
}

/* System Status Box */
.status-box {
  background-color: var(--bg-secondary, #1e293b);
  border: 1px solid var(--border-color, #475569);
}

.status-online {
  background-color: var(--success-color, #10b981);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
