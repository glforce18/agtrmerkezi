import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Naive UI - discrete API for composables
import { createDiscreteApi } from 'naive-ui'

// Error Tracking
import { initErrorTracking } from './services/errorTracking'

// Analytics
import { initAnalytics } from './services/analytics'

// Security
import { initSecurity } from './utils/security'

// Import minimal global styles
import './style.css'

const app = createApp(App)
const pinia = createPinia()

// Create discrete API for use outside of setup
const { message, notification, dialog, loadingBar } = createDiscreteApi(
  ['message', 'notification', 'dialog', 'loadingBar'],
  {
    configProviderProps: {
      // Will be synced with theme store
    }
  }
)

// Make available globally
window.$message = message
window.$notification = notification
window.$dialog = dialog
window.$loadingBar = loadingBar

app.use(pinia)
app.use(router)

// Initialize security (CSP, clickjacking protection)
initSecurity()

// Initialize error tracking (must be before mount)
initErrorTracking(app)

// Initialize analytics
initAnalytics(router)

// Register Service Worker for offline support (production only)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  navigator.serviceWorker.register('/sw.js', { scope: '/' })
    .then((registration) => {
      console.log('[App] Service Worker registered:', registration.scope)

      // Check for updates periodically
      setInterval(() => {
        registration.update()
      }, 60 * 60 * 1000) // Check every hour
    })
    .catch((error) => {
      console.warn('[App] Service Worker registration failed:', error)
    })
}

app.mount('#app')
