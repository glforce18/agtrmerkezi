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

app.mount('#app')
