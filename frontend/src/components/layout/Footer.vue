<template>
  <footer class="footer-main" :class="isDark ? 'footer-dark' : 'footer-light'">
    <!-- Animated Gradient Top Bar -->
    <div class="footer-gradient-bar">
      <div class="gradient-animation"></div>
    </div>

    <!-- Main Footer Content -->
    <div class="container-main py-12">
      <!-- Top Section: Logo, Newsletter, Social -->
      <div class="footer-top-section">
        <!-- Logo & Brand Section -->
        <div class="footer-brand-section glass-card">
          <router-link to="/" class="footer-logo-wrapper">
            <div class="footer-logo-container">
              <img
                v-if="footerLogoUrl"
                :src="footerLogoUrl"
                :style="footerLogoStyle"
                alt="AGTR Merkezi"
                class="footer-logo-img"
                @error="$event.target.style.display='none'"
              />
              <div v-else class="footer-logo-fallback">
                <span class="fallback-letter">A</span>
              </div>
              <div class="footer-logo-glow"></div>
              <div class="footer-logo-ring"></div>
            </div>
            <div class="footer-brand-text">
              <span class="brand-main">{{ logoText }}</span>
              <span class="brand-sub">{{ logoSubtitle }}</span>
            </div>
          </router-link>
          <p class="brand-description">
            Counter-Strike 1.6 Turkiye Toplulugu. Binlerce oyuncunun bulustugu profesyonel oyun platformu.
          </p>

          <!-- Social Media Links -->
          <div class="social-links">
            <a
              v-for="social in socialLinks"
              :key="social.name"
              :href="social.url"
              target="_blank"
              class="social-link"
              :class="social.class"
              :title="social.name"
            >
              <div class="social-icon" v-html="DOMPurify.sanitize(social.icon)"></div>
              <span class="social-tooltip">{{ social.name }}</span>
            </a>
          </div>
        </div>

        <!-- Newsletter Section -->
        <div class="newsletter-section glass-card">
          <div class="newsletter-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
          </div>
          <h3 class="newsletter-title">Bulten Aboneligi</h3>
          <p class="newsletter-desc">Yeni güncellemeler ve kampanyalardan haberdar olun</p>
          <form @submit.prevent="subscribeNewsletter" class="newsletter-form">
            <div class="input-wrapper">
              <input
                v-model="newsletterEmail"
                type="email"
                placeholder="E-posta adresiniz"
                class="newsletter-input"
                :class="{ 'has-error': newsletterError }"
              />
              <button type="submit" class="newsletter-btn" :disabled="isSubscribing">
                <span v-if="!isSubscribing">Abone Ol</span>
                <span v-else class="loading-spinner"></span>
              </button>
            </div>
            <p v-if="newsletterError" class="newsletter-error">{{ newsletterError }}</p>
            <p v-if="newsletterSuccess" class="newsletter-success">{{ newsletterSuccess }}</p>
          </form>
        </div>

        <!-- Server Stats Section -->
        <div class="stats-section glass-card">
          <h3 class="stats-title">Canli İstatistikler</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon servers">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
                  <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
                  <line x1="6" y1="6" x2="6.01" y2="6"/>
                  <line x1="6" y1="18" x2="6.01" y2="18"/>
                </svg>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ serverStats.onlineServers }}</span>
                <span class="stat-label">Aktif Sunucu</span>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon players">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ serverStats.playersOnline }}</span>
                <span class="stat-label">Oyuncu Online</span>
              </div>
            </div>
          </div>

          <!-- System Status -->
          <div class="system-status" :class="systemStatus.status">
            <div class="status-indicator">
              <div class="status-dot"></div>
              <div class="status-pulse"></div>
            </div>
            <span class="status-text">{{ systemStatus.text }}</span>
          </div>
        </div>
      </div>

      <!-- Animated Divider -->
      <div class="animated-divider">
        <div class="divider-line"></div>
        <div class="divider-glow"></div>
      </div>

      <!-- Links Section -->
      <div class="footer-links-section">
        <!-- Quick Links -->
        <div class="links-column">
          <h4 class="column-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
            </span>
            Hızlı Linkler
          </h4>
          <ul class="links-list">
            <li v-for="link in quickLinks" :key="link.path" class="link-item">
              <router-link :to="link.path" class="footer-link">
                <span class="link-arrow">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </span>
                <span class="link-text">{{ link.label }}</span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Resource Links -->
        <div class="links-column">
          <h4 class="column-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
            </span>
            Kaynaklar
          </h4>
          <ul class="links-list">
            <li v-for="link in resourceLinks" :key="link.path" class="link-item">
              <router-link :to="link.path" class="footer-link">
                <span class="link-arrow">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </span>
                <span class="link-text">{{ link.label }}</span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Legal Links -->
        <div class="links-column">
          <h4 class="column-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </span>
            Yasal
          </h4>
          <ul class="links-list">
            <li v-for="link in legalLinks" :key="link.path" class="link-item">
              <router-link :to="link.path" class="footer-link">
                <span class="link-arrow">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </span>
                <span class="link-text">{{ link.label }}</span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Language Selector -->
        <div class="links-column language-column">
          <h4 class="column-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
            </span>
            Dil Seçimi
          </h4>
          <n-dropdown
            trigger="click"
            :options="languageOptions"
            @select="handleLanguageSelect"
            placement="top-start"
          >
            <button class="language-selector">
              <span class="lang-flag">{{ currentLanguage.flag }}</span>
              <span class="lang-name">{{ currentLanguage.name }}</span>
              <svg class="lang-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>
          </n-dropdown>
        </div>
      </div>

      <!-- Partner Logos Section -->
      <div class="partners-section">
        <h4 class="partners-title">Partnerlerimiz</h4>
        <div class="partners-logos">
          <a
            v-for="partner in partners"
            :key="partner.name"
            :href="partner.url"
            target="_blank"
            class="partner-logo"
            :title="partner.name"
          >
            <img :src="partner.logo" :alt="partner.name" />
          </a>
        </div>
      </div>

      <!-- Animated Divider -->
      <div class="animated-divider">
        <div class="divider-line"></div>
        <div class="divider-glow"></div>
      </div>

      <!-- Bottom Bar -->
      <div class="footer-bottom">
        <div class="copyright">
          <span class="copyright-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M14.83 14.83a4 4 0 1 1 0-5.66"/>
            </svg>
          </span>
          <span>&copy; {{ currentYear }} AGTR Merkezi. Tüm hakları saklıdır.</span>
        </div>

        <div class="footer-meta">
          <a href="/changelog" class="version-link">
            <span class="version-badge">v7.0.0</span>
            <span class="changelog-text">Değişiklik Notlari</span>
          </a>
        </div>
      </div>
    </div>

    <!-- Back to Top Button -->
    <transition name="fade-slide">
      <button
        v-show="showBackToTop"
        class="back-to-top"
        @click="scrollToTop"
        title="Yukariya Don"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="18 15 12 9 6 15"/>
        </svg>
        <div class="btn-glow"></div>
      </button>
    </transition>
  </footer>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import DOMPurify from 'dompurify'
import { useThemeStore } from '@/stores/theme'
import { useSettingsStore } from '@/stores/settings'

const themeStore = useThemeStore()
const settingsStore = useSettingsStore()

const isDark = computed(() => themeStore.isDark)
const currentYear = computed(() => new Date().getFullYear())

// Logo settings from settings store
const footerLogoUrl = computed(() => {
  const settings = settingsStore.settings
  return settings.footer_logo_url || settings.logo_url || '/logo-navbar.png'
})

const footerLogoStyle = computed(() => {
  const settings = settingsStore.settings
  return {
    width: settings.footer_logo_width === 'auto' ? 'auto' : `${settings.footer_logo_width}px`,
    height: settings.footer_logo_height === 'auto' ? 'auto' : `${settings.footer_logo_height}px`,
    maxHeight: '56px',
    objectFit: 'contain'
  }
})

const logoText = computed(() => settingsStore.settings.logo_text || 'AGTR')
const logoSubtitle = computed(() => settingsStore.settings.logo_subtitle || 'MERKEZi')

// Newsletter
const newsletterEmail = ref('')
const newsletterError = ref('')
const newsletterSuccess = ref('')
const isSubscribing = ref(false)

const subscribeNewsletter = async () => {
  newsletterError.value = ''
  newsletterSuccess.value = ''

  if (!newsletterEmail.value) {
    newsletterError.value = 'Lütfen e-posta adresinizi girin'
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(newsletterEmail.value)) {
    newsletterError.value = 'Geçerli bir e-posta adresi girin'
    return
  }

  isSubscribing.value = true

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    newsletterSuccess.value = 'Başarıyla abone oldunuz!'
    newsletterEmail.value = ''
  } catch (error) {
    newsletterError.value = 'Bir hata oluştu, tekrar deneyin'
  } finally {
    isSubscribing.value = false
  }
}

// Server Stats (mock data - integrate with real API)
const serverStats = ref({
  onlineServers: 24,
  playersOnline: 1247
})

// System Status
const systemStatus = ref({
  status: 'online',
  text: 'Sistem Aktif'
})

// Back to Top
const showBackToTop = ref(false)

const handleScroll = () => {
  showBackToTop.value = window.scrollY > 400
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// Language
const currentLanguage = ref({
  code: 'tr',
  name: 'Turkce',
  flag: '\ud83c\uddf9\ud83c\uddf7'
})

const languageOptions = [
  { label: '\ud83c\uddf9\ud83c\uddf7 Turkce', key: 'tr' },
  { label: '\ud83c\uddfa\ud83c\uddf8 English', key: 'en' },
  { label: '\ud83c\udde9\ud83c\uddea Deutsch', key: 'de' }
]

const handleLanguageSelect = (key) => {
  const langs = {
    tr: { code: 'tr', name: 'Turkce', flag: '\ud83c\uddf9\ud83c\uddf7' },
    en: { code: 'en', name: 'English', flag: '\ud83c\uddfa\ud83c\uddf8' },
    de: { code: 'de', name: 'Deutsch', flag: '\ud83c\udde9\ud83c\uddea' }
  }
  currentLanguage.value = langs[key] || langs.tr
}

// Social Links
const socialLinks = [
  {
    name: 'Discord',
    url: 'https://discord.gg/agtrmerkezi',
    class: 'discord',
    icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03z"/></svg>'
  },
  {
    name: 'Twitter',
    url: 'https://twitter.com/agtrmerkezi',
    class: 'twitter',
    icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
  },
  {
    name: 'YouTube',
    url: 'https://youtube.com/@agtrmerkezi',
    class: 'youtube',
    icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
  },
  {
    name: 'Telegram',
    url: 'https://t.me/agtrmerkezi',
    class: 'telegram',
    icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>'
  },
  {
    name: 'Instagram',
    url: 'https://instagram.com/agtrmerkezi',
    class: 'instagram',
    icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.757-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"/></svg>'
  }
]

// Quick Links
const quickLinks = [
  { path: '/', label: 'Ana Sayfa' },
  { path: '/servers', label: 'Sunucular' },
  { path: '/forum', label: 'Forum' },
  { path: '/leaderboard', label: 'Sıralamalar' },
  { path: '/shop', label: 'Premium' }
]

// Resource Links
const resourceLinks = [
  { path: '/docs', label: 'Dokümantasyon' },
  { path: '/faq', label: 'Sikca Sorulan Sorular' },
  { path: '/support', label: 'Destek Merkezi' },
  { path: '/api', label: 'API Dokümanları' },
  { path: '/downloads', label: 'İndirmeler' }
]

// Legal Links
const legalLinks = [
  { path: '/terms', label: 'Kullanım Kosullari' },
  { path: '/privacy', label: 'Gizlilik Politikasi' },
  { path: '/cookies', label: 'Çerez Politikasi' },
  { path: '/contact', label: 'İletişim' }
]

// Partners (mock data)
const partners = ref([
  { name: 'Partner 1', logo: '/images/partners/partner1.png', url: '#' },
  { name: 'Partner 2', logo: '/images/partners/partner2.png', url: '#' },
  { name: 'Partner 3', logo: '/images/partners/partner3.png', url: '#' }
])

// Fetch settings on mount
onMounted(() => {
  if (!settingsStore.loaded) {
    settingsStore.fetchSettings()
  }
  window.addEventListener('scroll', handleScroll)
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* Base Styles */
.footer-main {
  position: relative;
  overflow: hidden;
  margin-top: auto;
}

.footer-dark {
  background: linear-gradient(180deg, #0a0a0a 0%, #111111 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  color: #e5e5e5;
}

.footer-light {
  background: linear-gradient(180deg, #fafafa 0%, #f0f0f0 100%);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  color: #1a1a1a;
}

/* Animated Gradient Bar */
.footer-gradient-bar {
  height: 4px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(90deg,
    transparent 0%,
    #f97316 20%,
    #fb923c 40%,
    #f97316 60%,
    #ea580c 80%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: gradientMove 4s ease-in-out infinite;
}

.gradient-animation {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes gradientMove {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Glass Card */
.glass-card {
  background: rgba(249, 115, 22, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(249, 115, 22, 0.1);
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s ease;
}

.footer-dark .glass-card {
  background: rgba(255, 255, 255, 0.02);
  border-color: rgba(255, 255, 255, 0.06);
}

.footer-light .glass-card {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
}

.glass-card:hover {
  border-color: rgba(249, 115, 22, 0.2);
  transform: translateY(-2px);
}

/* Top Section Layout */
.footer-top-section {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

@media (max-width: 1024px) {
  .footer-top-section {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .footer-top-section {
    grid-template-columns: 1fr;
  }
}

/* Logo Section */
.footer-brand-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.footer-logo-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  padding: 10px 14px;
  margin: -10px -14px;
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  width: fit-content;
}

.footer-logo-wrapper:hover {
  background: rgba(249, 115, 22, 0.08);
}

.footer-logo-wrapper:hover .footer-logo-glow {
  opacity: 1;
  transform: scale(1.2);
}

.footer-logo-wrapper:hover .footer-logo-ring {
  opacity: 1;
  transform: scale(1.15) rotate(180deg);
}

.footer-logo-wrapper:hover .footer-logo-img {
  transform: scale(1.08);
}

.footer-logo-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-logo-img {
  position: relative;
  z-index: 2;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 4px 16px rgba(249, 115, 22, 0.4));
}

.footer-logo-fallback {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
  position: relative;
  z-index: 2;
}

.footer-logo-fallback .fallback-letter {
  color: white;
  font-size: 28px;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.footer-logo-glow {
  position: absolute;
  inset: -20px;
  background: radial-gradient(ellipse at center, rgba(249, 115, 22, 0.6) 0%, transparent 70%);
  filter: blur(20px);
  opacity: 0;
  transition: all 0.5s ease;
  pointer-events: none;
  z-index: 1;
}

.footer-logo-ring {
  position: absolute;
  inset: -8px;
  border: 2px dashed rgba(249, 115, 22, 0.3);
  border-radius: 20px;
  opacity: 0;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  z-index: 1;
}

.footer-brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.footer-brand-text .brand-main {
  font-size: 26px;
  font-weight: 800;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #f97316 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.05em;
  animation: textGradient 4s ease infinite;
}

@keyframes textGradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.footer-brand-text .brand-sub {
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-top: 2px;
}

.footer-dark .brand-sub {
  color: #94a3b8;
}

.brand-description {
  font-size: 14px;
  line-height: 1.7;
  opacity: 0.7;
  max-width: 320px;
}

/* Social Links */
.social-links {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.social-link {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.footer-dark .social-link {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #a1a1aa;
}

.footer-light .social-link {
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
  color: #52525b;
}

.social-link:hover {
  transform: scale(1.12) translateY(-3px);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.3);
}

.social-link.discord:hover { background: #5865F2; color: white; }
.social-link.twitter:hover { background: #1DA1F2; color: white; }
.social-link.youtube:hover { background: #FF0000; color: white; }
.social-link.telegram:hover { background: #0088cc; color: white; }
.social-link.instagram:hover { background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); color: white; }

.social-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.social-link:hover .social-icon {
  transform: scale(1.1);
}

.social-tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) translateY(5px);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s ease;
}

.social-link:hover .social-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* Newsletter Section */
.newsletter-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.newsletter-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  color: #f97316;
  animation: bounce 2s ease infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.newsletter-icon svg {
  width: 100%;
  height: 100%;
}

.newsletter-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.newsletter-desc {
  font-size: 13px;
  opacity: 0.6;
  margin-bottom: 16px;
}

.newsletter-form {
  width: 100%;
}

.input-wrapper {
  display: flex;
  gap: 8px;
}

.newsletter-input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid rgba(249, 115, 22, 0.2);
  background: rgba(255, 255, 255, 0.05);
  font-size: 14px;
  transition: all 0.3s ease;
  outline: none;
}

.footer-dark .newsletter-input {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.footer-light .newsletter-input {
  background: white;
  color: #1a1a1a;
}

.newsletter-input:focus {
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
}

.newsletter-input.has-error {
  border-color: #ef4444;
}

.newsletter-input::placeholder {
  color: #a1a1aa;
}

.newsletter-btn {
  padding: 12px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.newsletter-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
}

.newsletter-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.newsletter-error {
  color: #ef4444;
  font-size: 12px;
  margin-top: 8px;
}

.newsletter-success {
  color: #22c55e;
  font-size: 12px;
  margin-top: 8px;
}

/* Stats Section */
.stats-section {
  display: flex;
  flex-direction: column;
}

.stats-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  border-radius: 14px;
  transition: all 0.3s ease;
}

.footer-dark .stat-item {
  background: rgba(255, 255, 255, 0.03);
}

.footer-light .stat-item {
  background: rgba(0, 0, 0, 0.02);
}

.stat-item:hover {
  transform: translateX(6px);
  background: rgba(249, 115, 22, 0.1);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 22px;
  height: 22px;
}

.stat-icon.servers {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
  color: #22c55e;
}

.stat-icon.players {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
  color: #3b82f6;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 22px;
  font-weight: 800;
  color: #f97316;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  opacity: 0.6;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* System Status */
.system-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.system-status.online {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.system-status.offline {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.system-status.maintenance {
  background: rgba(234, 179, 8, 0.1);
  color: #eab308;
}

.status-indicator {
  position: relative;
  width: 12px;
  height: 12px;
}

.status-dot {
  position: absolute;
  inset: 2px;
  border-radius: 50%;
  background: currentColor;
}

.status-pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid currentColor;
  animation: pulse 2s ease-out infinite;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

.status-text {
  flex: 1;
}

/* Animated Divider */
.animated-divider {
  position: relative;
  height: 1px;
  margin: 32px 0;
}

.divider-line {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(249, 115, 22, 0.3) 50%,
    transparent 100%
  );
}

.divider-glow {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 20px;
  background: radial-gradient(ellipse at center, rgba(249, 115, 22, 0.2) 0%, transparent 70%);
  filter: blur(8px);
  animation: glowPulse 3s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Links Section */
.footer-links-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
  margin-bottom: 40px;
}

@media (max-width: 1024px) {
  .footer-links-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .footer-links-section {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

.links-column {
  display: flex;
  flex-direction: column;
}

.column-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 20px;
  position: relative;
}

.column-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 32px;
  height: 3px;
  background: linear-gradient(90deg, #f97316, transparent);
  border-radius: 2px;
}

.title-icon {
  width: 20px;
  height: 20px;
  color: #f97316;
}

.title-icon svg {
  width: 100%;
  height: 100%;
}

.links-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.link-item {
  position: relative;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin: 0 -12px;
  border-radius: 10px;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.footer-dark .footer-link {
  color: #a1a1aa;
}

.footer-light .footer-link {
  color: #52525b;
}

.footer-link:hover {
  background: rgba(249, 115, 22, 0.08);
  color: #f97316;
  padding-left: 18px;
}

.link-arrow {
  width: 16px;
  height: 16px;
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.3s ease;
}

.link-arrow svg {
  width: 100%;
  height: 100%;
}

.footer-link:hover .link-arrow {
  opacity: 1;
  transform: translateX(0);
}

.link-text {
  transition: transform 0.3s ease;
}

.footer-link:hover .link-text {
  transform: translateX(4px);
}

/* Language Selector */
.language-column {
  display: flex;
  flex-direction: column;
}

.language-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid rgba(249, 115, 22, 0.2);
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  width: fit-content;
}

.footer-dark .language-selector {
  color: #e5e5e5;
}

.footer-light .language-selector {
  color: #1a1a1a;
}

.language-selector:hover {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

.lang-flag {
  font-size: 18px;
}

.lang-name {
  font-weight: 500;
}

.lang-arrow {
  width: 16px;
  height: 16px;
  opacity: 0.6;
  transition: transform 0.3s ease;
}

.language-selector:hover .lang-arrow {
  transform: rotate(180deg);
}

/* Partners Section */
.partners-section {
  text-align: center;
  padding: 24px 0;
}

.partners-title {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.5;
  margin-bottom: 20px;
}

.partners-logos {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}

.partner-logo {
  opacity: 0.4;
  transition: all 0.3s ease;
  filter: grayscale(100%);
}

.partner-logo:hover {
  opacity: 1;
  filter: grayscale(0%);
  transform: scale(1.1);
}

.partner-logo img {
  height: 32px;
  width: auto;
  object-fit: contain;
}

/* Footer Bottom */
.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

@media (max-width: 640px) {
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}

.copyright {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.6;
}

.copyright-icon {
  width: 18px;
  height: 18px;
  opacity: 0.6;
}

.copyright-icon svg {
  width: 100%;
  height: 100%;
}

.footer-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.version-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.version-badge {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
  transition: all 0.3s ease;
}

.version-link:hover .version-badge {
  background: #f97316;
  color: white;
}

.changelog-text {
  font-size: 13px;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.footer-dark .changelog-text {
  color: #a1a1aa;
}

.footer-light .changelog-text {
  color: #52525b;
}

.version-link:hover .changelog-text {
  opacity: 1;
  color: #f97316;
}

/* Back to Top Button */
.back-to-top {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 50px;
  height: 50px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(249, 115, 22, 0.4);
  transition: all 0.3s ease;
  z-index: 100;
  overflow: hidden;
}

.back-to-top svg {
  width: 24px;
  height: 24px;
  position: relative;
  z-index: 2;
}

.back-to-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(249, 115, 22, 0.5);
}

.back-to-top:hover svg {
  animation: arrowBounce 0.6s ease infinite;
}

@keyframes arrowBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.btn-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.3) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.back-to-top:hover .btn-glow {
  opacity: 1;
  animation: rotate 3s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Container */
.container-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
}

@media (max-width: 640px) {
  .container-main {
    padding: 0 16px;
  }
}
</style>
