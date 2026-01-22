import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { darkTheme } from 'naive-ui'

const STORAGE_KEY = 'agtr-theme-mode'

export const useThemeStore = defineStore('theme', () => {
  // Theme mode: 'light', 'dark', or 'system'
  const mode = ref(localStorage.getItem(STORAGE_KEY) || 'dark')

  // System preference
  const systemPrefersDark = ref(
    window.matchMedia('(prefers-color-scheme: dark)').matches
  )

  // Simple dark/light mode (computed from mode)
  const isDark = computed(() => {
    if (mode.value === 'system') {
      return systemPrefersDark.value
    }
    return mode.value === 'dark'
  })

  // Theme mode label for UI
  const modeLabel = computed(() => {
    const labels = { light: 'Açık', dark: 'Koyu', system: 'Sistem' }
    return labels[mode.value]
  })

  // Naive UI theme object
  const naiveTheme = computed(() => isDark.value ? darkTheme : null)

  // Theme overrides for brand colors with enhanced button styling
  const themeOverrides = computed(() => ({
    common: {
      // Primary colors - Orange
      primaryColor: '#f97316',
      primaryColorHover: '#fb923c',
      primaryColorPressed: '#ea580c',
      primaryColorSuppl: '#f97316',
      // Info - Blue
      infoColor: '#3b82f6',
      infoColorHover: '#60a5fa',
      infoColorPressed: '#2563eb',
      // Success - Green
      successColor: '#10b981',
      successColorHover: '#34d399',
      successColorPressed: '#059669',
      // Warning - Amber
      warningColor: '#f59e0b',
      warningColorHover: '#fbbf24',
      warningColorPressed: '#d97706',
      // Error - Red
      errorColor: '#ef4444',
      errorColorHover: '#f87171',
      errorColorPressed: '#dc2626',
      // Border radius
      borderRadius: '10px',
      borderRadiusSmall: '8px',
      // Font
      fontFamily: "'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      fontWeightStrong: '700',
      // Body colors - Softer & Eye-friendly
      bodyColor: isDark.value ? '#1a1b21' : '#ffffff',
      cardColor: isDark.value ? 'rgba(255, 255, 255, 0.025)' : '#ffffff',
      modalColor: isDark.value ? '#22232a' : '#ffffff',
      popoverColor: isDark.value ? '#22232a' : '#ffffff',
      tableColor: isDark.value ? 'rgba(255, 255, 255, 0.02)' : '#ffffff',
      // Text colors - Better contrast
      textColorBase: isDark.value ? '#e8e8ec' : '#1a1a1a',
      textColor1: isDark.value ? '#f3f4f6' : '#18181b',
      textColor2: isDark.value ? '#9ca3af' : '#52525b',
      textColor3: isDark.value ? '#6b7280' : '#a1a1aa',
      // Border colors - Softer
      borderColor: isDark.value ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.1)',
      dividerColor: isDark.value ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.08)',
      // Hover colors
      hoverColor: isDark.value ? 'rgba(255, 255, 255, 0.04)' : 'rgba(0, 0, 0, 0.05)',
      // Heights
      heightTiny: '28px',
      heightSmall: '32px',
      heightMedium: '40px',
      heightLarge: '48px',
      heightHuge: '56px',
    },
    Button: {
      fontWeight: '600',
      fontWeightStrong: '700',
      textColorPrimary: '#ffffff',
      textColorHoverPrimary: '#ffffff',
      textColorPressedPrimary: '#ffffff',
      textColorFocusPrimary: '#ffffff',
      // Primary button - Gaming gradient style
      colorPrimary: '#f97316',
      colorHoverPrimary: '#fb923c',
      colorPressedPrimary: '#ea580c',
      colorFocusPrimary: '#f97316',
      borderPrimary: 'none',
      borderHoverPrimary: 'none',
      borderPressedPrimary: 'none',
      borderFocusPrimary: 'none',
      // Default button - Ghost style with border
      borderDefault: '2px solid rgba(249, 115, 22, 0.3)',
      borderHoverDefault: '2px solid #f97316',
      borderPressedDefault: '2px solid #ea580c',
      borderFocusDefault: '2px solid #f97316',
      colorHoverDefault: 'rgba(249, 115, 22, 0.1)',
      colorPressedDefault: 'rgba(249, 115, 22, 0.15)',
      // Success button
      colorSuccess: '#10b981',
      colorHoverSuccess: '#34d399',
      colorPressedSuccess: '#059669',
      borderSuccess: 'none',
      // Error button
      colorError: '#ef4444',
      colorHoverError: '#f87171',
      colorPressedError: '#dc2626',
      borderError: 'none',
      // Warning button
      colorWarning: '#f59e0b',
      colorHoverWarning: '#fbbf24',
      colorPressedWarning: '#d97706',
      borderWarning: 'none',
      // Info button
      colorInfo: '#3b82f6',
      colorHoverInfo: '#60a5fa',
      colorPressedInfo: '#2563eb',
      borderInfo: 'none',
      // Border radius
      borderRadiusTiny: '6px',
      borderRadiusSmall: '8px',
      borderRadiusMedium: '10px',
      borderRadiusLarge: '12px',
      // Padding
      paddingTiny: '0 12px',
      paddingSmall: '0 16px',
      paddingMedium: '0 20px',
      paddingLarge: '0 28px',
      // Icon margins
      iconMarginTiny: '6px',
      iconMarginSmall: '6px',
      iconMarginMedium: '8px',
      iconMarginLarge: '10px',
      // Wave animation
      waveOpacity: '0.6',
    },
    Card: {
      borderRadius: '16px',
      borderColor: isDark.value ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
      color: isDark.value ? 'rgba(255, 255, 255, 0.03)' : '#ffffff',
      colorModal: isDark.value ? '#1f1f23' : '#ffffff',
      colorPopover: isDark.value ? '#1f1f23' : '#ffffff',
      colorEmbedded: isDark.value ? 'rgba(255, 255, 255, 0.02)' : '#f9fafb',
      titleFontWeight: '700',
      paddingSmall: '16px',
      paddingMedium: '20px',
      paddingLarge: '24px',
      paddingHuge: '32px',
    },
    Input: {
      borderRadius: '10px',
      color: isDark.value ? 'rgba(255, 255, 255, 0.05)' : '#ffffff',
      colorFocus: isDark.value ? 'rgba(255, 255, 255, 0.08)' : '#ffffff',
      border: isDark.value ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
      borderHover: '1px solid #f97316',
      borderFocus: '1px solid #f97316',
      boxShadowFocus: '0 0 0 3px rgba(249, 115, 22, 0.2)',
      heightMedium: '42px',
      heightLarge: '48px',
      fontSizeMedium: '15px',
      fontSizeLarge: '16px',
      paddingMedium: '0 14px',
      paddingLarge: '0 16px',
    },
    Tabs: {
      tabFontWeight: '500',
      tabFontWeightActive: '700',
      tabTextColorLine: isDark.value ? '#a1a1aa' : '#52525b',
      tabTextColorActiveLine: '#f97316',
      tabTextColorHoverLine: '#f97316',
      barColor: '#f97316',
      tabGapMediumLine: '24px',
      tabGapLargeLine: '32px',
    },
    Tag: {
      borderRadius: '8px',
      fontWeight: '600',
      heightMedium: '28px',
      heightLarge: '32px',
      paddingMedium: '0 12px',
      paddingLarge: '0 16px',
    },
    Progress: {
      fillColor: '#f97316',
      railColor: isDark.value ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      textColorLineInner: '#ffffff',
      fontWeightCircle: '700',
    },
    Menu: {
      borderRadius: '12px',
      itemColorActive: 'rgba(249, 115, 22, 0.15)',
      itemColorActiveHover: 'rgba(249, 115, 22, 0.2)',
      itemTextColorActive: '#f97316',
      itemTextColorActiveHover: '#f97316',
      itemIconColorActive: '#f97316',
      itemIconColorActiveHover: '#f97316',
    },
    Avatar: {
      borderRadius: '12px',
    },
    Modal: {
      borderRadius: '20px',
      color: isDark.value ? '#1f1f23' : '#ffffff',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
    },
    Dialog: {
      borderRadius: '20px',
      titleFontWeight: '700',
    },
    Message: {
      borderRadius: '12px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
    },
    Notification: {
      borderRadius: '16px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
    },
    DataTable: {
      borderRadius: '12px',
      thColor: isDark.value ? 'rgba(255, 255, 255, 0.05)' : '#f9fafb',
      thTextColor: isDark.value ? '#a1a1aa' : '#52525b',
      thFontWeight: '600',
      tdColor: 'transparent',
      tdColorHover: isDark.value ? 'rgba(255, 255, 255, 0.03)' : 'rgba(0, 0, 0, 0.02)',
      tdColorStriped: isDark.value ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
      borderColor: isDark.value ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
    },
    Pagination: {
      itemBorderRadius: '8px',
      itemColor: 'transparent',
      itemColorHover: 'rgba(249, 115, 22, 0.1)',
      itemColorActive: '#f97316',
      itemColorActiveHover: '#fb923c',
      itemTextColorActive: '#ffffff',
      itemTextColorHover: '#f97316',
      buttonBorderRadius: '8px',
    },
    Select: {
      peers: {
        InternalSelection: {
          borderRadius: '10px',
          heightMedium: '42px',
          heightLarge: '48px',
        }
      }
    },
    Breadcrumb: {
      itemTextColor: isDark.value ? '#71717a' : '#a1a1aa',
      itemTextColorHover: '#f97316',
      itemTextColorActive: '#f97316',
      separatorColor: isDark.value ? '#52525b' : '#d4d4d8',
    },
    Empty: {
      iconColor: isDark.value ? '#52525b' : '#a1a1aa',
      textColor: isDark.value ? '#71717a' : '#a1a1aa',
    },
    Statistic: {
      valueFontSize: '28px',
      labelFontWeight: '500',
    },
  }))

  // Set theme mode
  function setMode(newMode) {
    mode.value = newMode
    localStorage.setItem(STORAGE_KEY, newMode)
    applyTheme()
  }

  // Toggle between light and dark (skip system)
  function toggleTheme() {
    setMode(isDark.value ? 'light' : 'dark')
  }

  // Cycle through modes: light -> dark -> system -> light
  function cycleMode() {
    const modes = ['light', 'dark', 'system']
    const currentIndex = modes.indexOf(mode.value)
    const nextIndex = (currentIndex + 1) % modes.length
    setMode(modes[nextIndex])
  }

  // Legacy support
  function setDarkMode(value) {
    setMode(value ? 'dark' : 'light')
  }

  // Apply theme to document
  function applyTheme() {
    const root = document.documentElement

    if (isDark.value) {
      root.classList.add('dark')
      root.classList.remove('light')
    } else {
      root.classList.add('light')
      root.classList.remove('dark')
    }

    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', isDark.value ? '#0f0f1a' : '#ffffff')
    }
  }

  // Listen for system preference changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    systemPrefersDark.value = e.matches
    if (mode.value === 'system') {
      applyTheme()
    }
  })

  // Watch isDark changes to apply theme
  watch(isDark, () => {
    applyTheme()
  }, { immediate: true })

  return {
    mode,
    isDark,
    modeLabel,
    naiveTheme,
    themeOverrides,
    setMode,
    setDarkMode,
    toggleTheme,
    cycleMode
  }
})
