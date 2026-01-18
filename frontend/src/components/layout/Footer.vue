<template>
  <footer class="border-t mt-auto py-8" :class="isDark ? 'bg-zinc-900 border-zinc-800' : 'bg-zinc-50 border-zinc-200'">
    <div class="container-main">
      <!-- Main Footer -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 pb-8">
        <!-- Brand -->
        <div class="space-y-4">
          <router-link to="/" class="flex items-center gap-2">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
              <span class="text-white font-bold text-xl">A</span>
            </div>
            <div>
              <span class="font-bold text-lg">AGTR</span>
              <span class="text-orange-500 font-bold text-lg">Merkezi</span>
            </div>
          </router-link>
          <p class="text-sm opacity-60">
            Counter-Strike 1.6 Turkiye Toplulugu. Binlerce oyuncunun bulustugu platform.
          </p>
          <div class="flex gap-2">
            <n-button quaternary circle tag="a" href="https://discord.gg/agtrmerkezi" target="_blank">
              <template #icon>
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03z"/>
                </svg>
              </template>
            </n-button>
            <n-button quaternary circle tag="a" href="https://twitter.com/agtrmerkezi" target="_blank">
              <template #icon>
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </template>
            </n-button>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="font-semibold mb-4">Hizli Linkler</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="link in quickLinks" :key="link.path">
              <router-link :to="link.path" class="opacity-60 hover:opacity-100 hover:text-orange-500 transition-colors">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Resources -->
        <div>
          <h3 class="font-semibold mb-4">Kaynaklar</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="link in resourceLinks" :key="link.path">
              <router-link :to="link.path" class="opacity-60 hover:opacity-100 hover:text-orange-500 transition-colors">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <h3 class="font-semibold mb-4">Yasal</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="link in legalLinks" :key="link.path">
              <router-link :to="link.path" class="opacity-60 hover:opacity-100 hover:text-orange-500 transition-colors">
                {{ link.label }}
              </router-link>
            </li>
          </ul>

          <!-- Status -->
          <n-tag type="success" :bordered="false" class="mt-4">
            <template #icon>
              <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            </template>
            Sistem Aktif
          </n-tag>
        </div>
      </div>

      <!-- Bottom -->
      <n-divider />
      <div class="flex flex-col md:flex-row justify-between items-center gap-4 text-sm opacity-60">
        <div>&copy; {{ currentYear }} AGTR Merkezi. Tum haklari saklidir.</div>
        <div>v7.0.0</div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
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
  { path: '/faq', label: 'SSS' },
  { path: '/support', label: 'Destek' }
]

const legalLinks = [
  { path: '/terms', label: 'Kullanim Kosullari' },
  { path: '/privacy', label: 'Gizlilik Politikasi' },
  { path: '/contact', label: 'Iletisim' }
]
</script>
