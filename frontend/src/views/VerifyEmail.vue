<template>
  <div class="verify-email-page">
    <div class="verify-container">
      <!-- Loading State -->
      <div v-if="loading" class="verify-card">
        <div class="verify-icon loading">
          <Loader2Icon class="w-12 h-12 animate-spin" />
        </div>
        <h1 class="verify-title">E-posta Doğrulaniyor</h1>
        <p class="verify-description">Lutfen bekleyin...</p>
      </div>

      <!-- Success State -->
      <div v-else-if="success" class="verify-card">
        <div class="verify-icon success">
          <CheckCircleIcon class="w-12 h-12" />
        </div>
        <h1 class="verify-title">E-posta Doğrulandi!</h1>
        <p class="verify-description">
          E-posta adresiniz başarıyla doğrulandi. Artik tüm ozellikleri kullanabilirsiniz.
        </p>
        <router-link to="/profile" class="verify-btn success">
          <UserIcon class="w-4 h-4" />
          <span>Profile Git</span>
        </router-link>
      </div>

      <!-- Error State -->
      <div v-else class="verify-card">
        <div class="verify-icon error">
          <XCircleIcon class="w-12 h-12" />
        </div>
        <h1 class="verify-title">Doğrulama Başarısiz</h1>
        <p class="verify-description">
          {{ errorMessage }}
        </p>
        <div class="verify-actions">
          <button
            v-if="canResend"
            class="verify-btn primary"
            :disabled="resending"
            @click="resendVerification"
          >
            <SendIcon v-if="!resending" class="w-4 h-4" />
            <Loader2Icon v-else class="w-4 h-4 animate-spin" />
            <span>{{ resending ? 'Gönderiliyor...' : 'Yeni Link Gönder' }}</span>
          </button>
          <router-link to="/" class="verify-btn secondary">
            <HomeIcon class="w-4 h-4" />
            <span>Ana Sayfaya Don</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { authAPI } from '@/api'
import {
  Loader2 as Loader2Icon,
  CheckCircle as CheckCircleIcon,
  XCircle as XCircleIcon,
  User as UserIcon,
  Send as SendIcon,
  Home as HomeIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const loading = ref(true)
const success = ref(false)
const errorMessage = ref('')
const canResend = ref(false)
const resending = ref(false)

async function verifyEmail() {
  const token = route.query.token

  if (!token) {
    loading.value = false
    errorMessage.value = 'Doğrulama tokeni bulunamadi.'
    return
  }

  try {
    await authAPI.verifyEmail(token)
    success.value = true

    // Kullanıcı giriş yapmissa bilgilerini güncelle
    if (authStore.isAuthenticated) {
      await authStore.fetchUser()
    }

    uiStore.addNotification({
      type: 'success',
      message: 'E-posta adresiniz başarıyla doğrulandi!'
    })

    // 3 saniye sonra profile yonlendir
    setTimeout(() => {
      if (authStore.isAuthenticated) {
        router.push('/profile')
      } else {
        router.push('/login')
      }
    }, 3000)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Doğrulama başarısız oldu.'
    canResend.value = authStore.isAuthenticated
  } finally {
    loading.value = false
  }
}

async function resendVerification() {
  if (resending.value || !authStore.isAuthenticated) return

  resending.value = true
  try {
    await authAPI.sendVerificationEmail()
    uiStore.addNotification({
      type: 'success',
      message: 'Yeni doğrulama emaili gönderildi!'
    })
    errorMessage.value = 'Yeni doğrulama emaili gönderildi. Lutfen gelen kutunuzu kontrol edin.'
    canResend.value = false
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: error.response?.data?.detail || 'Email gönderilemedi.'
    })
  } finally {
    resending.value = false
  }
}

onMounted(() => {
  verifyEmail()
})
</script>

<style scoped>
.verify-email-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.verify-container {
  width: 100%;
  max-width: 440px;
}

.verify-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 48px 32px;
  text-align: center;
}

.verify-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 24px;
}

.verify-icon.loading {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.verify-icon.success {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.verify-icon.error {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.verify-title {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin-bottom: 12px;
}

.verify-description {
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.verify-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.verify-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.verify-btn.primary {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
}

.verify-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.3);
}

.verify-btn.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.verify-btn.success:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}

.verify-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.verify-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.verify-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
