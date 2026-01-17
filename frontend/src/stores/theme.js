import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('agtr-theme') || 'dark')
  const soundEnabled = ref(localStorage.getItem('agtr-sound-enabled') !== 'false')

  function setTheme(theme) {
    currentTheme.value = theme

    // Map simple theme names to DaisyUI theme names
    const daisyTheme = theme === 'dark' ? 'agtr_dark' : 'agtr_light'
    document.documentElement.setAttribute('data-theme', daisyTheme)

    // Also set dark class for Tailwind dark mode utilities
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    localStorage.setItem('agtr-theme', theme)

    // Dispatch event for legacy compatibility
    window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme } }))
  }

  function toggleTheme() {
    const newTheme = currentTheme.value === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
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
    setTheme,
    toggleTheme,
    toggleSound
  }
})
