import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Check if in panel mode first
    const isPanelMode = localStorage.getItem('panel_mode') === 'true'
    const panelToken = localStorage.getItem('panel_token')

    if (isPanelMode && panelToken) {
      // Use panel token in panel mode
      config.headers.Authorization = `Bearer ${panelToken}`
    } else {
      // Use regular auth token
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Check if in panel mode
      const isPanelMode = localStorage.getItem('panel_mode') === 'true'

      if (isPanelMode) {
        // In panel mode - clear panel credentials and redirect to panel login
        localStorage.removeItem('panel_token')
        localStorage.removeItem('panel_server_id')
        localStorage.removeItem('panel_mode')
        window.location.href = '/panel'
      } else {
        // Regular mode - clear auth and redirect to login
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
