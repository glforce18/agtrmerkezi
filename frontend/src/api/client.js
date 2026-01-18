import axios from 'axios'
import { STORAGE_KEYS, API_CONFIG } from '@/constants'
import { getCsrfToken, getAccessToken, removeAccessToken } from '@/utils/http'

const API_BASE_URL = import.meta.env.VITE_API_URL || API_CONFIG.BASE_URL

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - Otomatik header ekleme
apiClient.interceptors.request.use(
  (config) => {
    // CSRF token ekle
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken
    }

    // Auth token ekle
    const token = getAccessToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - Hata yönetimi
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Token geçersiz - temizle ve login'e yönlendir
          removeAccessToken()
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login'
          }
          break
        case 403:
          console.error('Yetkisiz erişim:', error.response.data)
          break
        case 404:
          console.error('Bulunamadı:', error.response.data)
          break
        case 500:
          console.error('Sunucu hatası:', error.response.data)
          break
      }
    }
    return Promise.reject(error)
  }
)

// Re-export utilities for backward compatibility
export { getCsrfToken }

export default apiClient
