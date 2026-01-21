import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Naive UI - discrete API for composables
import { createDiscreteApi } from 'naive-ui'

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

// Global error handler
app.config.errorHandler = (err, _instance, _info) => {
  // Log to external service in production
  if (import.meta.env.DEV) {
    console.error('Vue error:', err) // eslint-disable-line no-console
  }
  window.$message?.error('Bir hata oluştu')
}

app.mount('#app')
