import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Available themes with metadata
const AVAILABLE_THEMES = [
  { id: 'agtr_dark', name: 'AGTR Dark', icon: '🎮', category: 'agtr' },
  { id: 'agtr_light', name: 'AGTR Light', icon: '☀️', category: 'agtr' },
  { id: 'agtr_cyber', name: 'Cyberpunk', icon: '🌃', category: 'agtr' },
  { id: 'agtr_halflife', name: 'Half-Life', icon: '🔶', category: 'agtr' },
  { id: 'agtr_cs', name: 'Counter-Strike', icon: '🔫', category: 'agtr' },
  { id: 'synthwave', name: 'Synthwave', icon: '🌆', category: 'gaming' },
  { id: 'cyberpunk', name: 'Cyberpunk 2077', icon: '🤖', category: 'gaming' },
  { id: 'halloween', name: 'Halloween', icon: '🎃', category: 'gaming' },
  { id: 'dracula', name: 'Dracula', icon: '🧛', category: 'gaming' },
  { id: 'forest', name: 'Forest', icon: '🌲', category: 'nature' },
  { id: 'black', name: 'Pure Black', icon: '⬛', category: 'minimal' },
  { id: 'luxury', name: 'Luxury', icon: '💎', category: 'minimal' },
]

const DARK_THEMES = ['agtr_dark', 'agtr_cyber', 'agtr_halflife', 'agtr_cs', 'synthwave', 'cyberpunk', 'halloween', 'dracula', 'forest', 'black', 'luxury']

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('agtr-theme') || 'agtr_dark')
  const soundEnabled = ref(localStorage.getItem('agtr-sound-enabled') !== 'false')

  const availableThemes = computed(() => AVAILABLE_THEMES)
  const isDark = computed(() => DARK_THEMES.includes(currentTheme.value))

  function setTheme(theme) {
    // Validate theme exists
    const validTheme = AVAILABLE_THEMES.find(t => t.id === theme)
    if (!validTheme) {
      theme = 'agtr_dark'
    }

    currentTheme.value = theme
    document.documentElement.setAttribute('data-theme', theme)

    // Set dark class for Tailwind utilities
    if (DARK_THEMES.includes(theme)) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    localStorage.setItem('agtr-theme', theme)

    // Dispatch event for components that need to react
    window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme } }))
  }

  function toggleTheme() {
    // Cycle through main themes
    const mainThemes = ['agtr_dark', 'agtr_halflife', 'agtr_cyber', 'agtr_cs', 'agtr_light']
    const currentIndex = mainThemes.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % mainThemes.length
    setTheme(mainThemes[nextIndex])
  }

  function toggleSound() {
    soundEnabled.value = !soundEnabled.value
    localStorage.setItem('agtr-sound-enabled', soundEnabled.value.toString())
  }

  // Initialize theme on mount
  setTheme(currentTheme.value)

  return {
    currentTheme,
    soundEnabled,
    availableThemes,
    isDark,
    setTheme,
    toggleTheme,
    toggleSound
  }
})
