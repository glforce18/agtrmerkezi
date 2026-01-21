import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref({
    // Site Info
    site_name: 'AGTR Merkezi',
    site_description: '',

    // Logo Settings
    logo_url: '/logo-navbar.png',
    logo_dark_url: '',
    logo_mobile_url: '',
    logo_width: 'auto',
    logo_height: '36',
    logo_text: 'AGTR',
    logo_subtitle: 'MERKEZİ',
    show_logo_text: false,

    // Footer Logo
    footer_logo_url: '',
    footer_logo_width: 'auto',
    footer_logo_height: '48',

    // Favicon
    favicon_url: '/favicon.ico',

    // Social
    discord_url: '',
    support_email: '',

    // Feature Flags
    maintenance_mode: false,
    registration_enabled: true
  })

  const loading = ref(false)
  const loaded = ref(false)

  // Computed logo URL based on theme
  const currentLogoUrl = computed(() => {
    return settings.value.logo_url || '/logo-navbar.png'
  })

  const logoStyle = computed(() => ({
    width: settings.value.logo_width === 'auto' ? 'auto' : `${settings.value.logo_width}px`,
    height: settings.value.logo_height === 'auto' ? 'auto' : `${settings.value.logo_height}px`,
    maxHeight: '40px',
    objectFit: 'contain'
  }))

  const footerLogoStyle = computed(() => ({
    width: settings.value.footer_logo_width === 'auto' ? 'auto' : `${settings.value.footer_logo_width}px`,
    height: settings.value.footer_logo_height === 'auto' ? 'auto' : `${settings.value.footer_logo_height}px`,
    maxHeight: '60px',
    objectFit: 'contain'
  }))

  async function fetchSettings() {
    if (loading.value) return

    loading.value = true
    try {
      const response = await fetch('/api/public/settings')
      if (response.ok) {
        const data = await response.json()
        // Merge with defaults
        Object.keys(data).forEach(key => {
          if (data[key] !== null && data[key] !== undefined) {
            settings.value[key] = data[key]
          }
        })
        loaded.value = true
      }
    } catch {
      // Settings fetch failed - using defaults
    } finally {
      loading.value = false
    }
  }

  function updateSettings(newSettings) {
    Object.assign(settings.value, newSettings)
  }

  return {
    settings,
    loading,
    loaded,
    currentLogoUrl,
    logoStyle,
    footerLogoStyle,
    fetchSettings,
    updateSettings
  }
})
