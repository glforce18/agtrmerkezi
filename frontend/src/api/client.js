import axios from 'axios'
import { STORAGE_KEYS, API_CONFIG } from '@/constants'
import { getCsrfToken, getAccessToken, setAccessToken, removeAccessToken } from '@/utils/http'

const API_BASE_URL = import.meta.env.VITE_API_URL || API_CONFIG.BASE_URL

// Token refresh state management
let isRefreshing = false
let refreshSubscribers = []

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb)
}

function onTokenRefreshed(token) {
  refreshSubscribers.forEach(cb => cb(token))
  refreshSubscribers = []
}

function onRefreshFailed() {
  refreshSubscribers = []
}

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

// Response interceptor - Hata yönetimi ve token yenileme
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config

    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Login/refresh/logout endpoint'lerinde retry yapma
          if (originalRequest.url.includes('/auth/login') ||
              originalRequest.url.includes('/auth/refresh') ||
              originalRequest.url.includes('/auth/logout') ||
              originalRequest._retry) {
            // Refresh de başarısız olduysa logout yap
            removeAccessToken()
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login'
            }
            return Promise.reject(error)
          }

          // Token refresh dene
          if (!isRefreshing) {
            isRefreshing = true
            originalRequest._retry = true

            try {
              const response = await axios.post(
                `${API_BASE_URL}/auth/refresh`,
                {},
                { headers: { 'Authorization': `Bearer ${getAccessToken()}` } }
              )

              const newToken = response.data?.access_token || response.data?.token
              if (newToken) {
                setAccessToken(newToken)
                onTokenRefreshed(newToken)

                // Orijinal isteği yeni token ile tekrarla
                originalRequest.headers['Authorization'] = `Bearer ${newToken}`
                return apiClient(originalRequest)
              }
            } catch (refreshError) {
              onRefreshFailed()
              removeAccessToken()
              if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login'
              }
              return Promise.reject(refreshError)
            } finally {
              isRefreshing = false
            }
          }

          // Başka bir refresh işlemi devam ediyorsa, tamamlanmasını bekle
          return new Promise((resolve) => {
            subscribeTokenRefresh((newToken) => {
              originalRequest.headers['Authorization'] = `Bearer ${newToken}`
              resolve(apiClient(originalRequest))
            })
          })

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
