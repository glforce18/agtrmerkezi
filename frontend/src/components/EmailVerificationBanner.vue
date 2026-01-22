<template>
  <Transition name="slide-down">
    <div
      v-if="showBanner"
      class="email-verification-banner"
    >
      <div class="banner-content">
        <div class="banner-icon">
          <MailWarningIcon class="w-5 h-5" />
        </div>
        <div class="banner-text">
          <span class="banner-title">E-posta Dogrulamasi Gerekli</span>
          <span class="banner-description">
            Tum ozellikleri kullanabilmek icin e-posta adresinizi dogrulayin.
          </span>
        </div>
        <div class="banner-actions">
          <button
            v-if="canResend"
            class="verify-btn"
            :disabled="sending"
            @click="sendVerification"
          >
            <SendIcon v-if="!sending" class="w-4 h-4" />
            <LoaderIcon v-else class="w-4 h-4 animate-spin" />
            <span>{{ sending ? 'Gonderiliyor...' : 'Email Dogrula' }}</span>
          </button>
          <button
            v-else
            class="verify-btn disabled"
            disabled
          >
            <ClockIcon class="w-4 h-4" />
            <span>{{ countdown }}s bekleyin</span>
          </button>
          <button
            class="close-btn"
            @click="dismissBanner"
            aria-label="Kapat"
          >
            <XIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { authAPI } from '@/api'
import {
  Mail as MailWarningIcon,
  Send as SendIcon,
  X as XIcon,
  Clock as ClockIcon,
  Loader2 as LoaderIcon
} from 'lucide-vue-next'

const authStore = useAuthStore()
const uiStore = useUIStore()

const sending = ref(false)
const countdown = ref(0)
const dismissed = ref(false)
let countdownInterval = null

const showBanner = computed(() => {
  if (dismissed.value) return false
  if (!authStore.user) return false
  // Steam kullanicilari icin gosterme
  if (authStore.user.steam_id) return false
  // Email zaten dogrulanmissa gosterme
  if (authStore.user.email_verified) return false
  return true
})

const canResend = computed(() => countdown.value <= 0)

async function sendVerification() {
  if (sending.value || !canResend.value) return

  sending.value = true
  try {
    await authAPI.sendVerificationEmail()
    uiStore.addNotification({
      type: 'success',
      message: 'Dogrulama emaili gonderildi! Lutfen gelen kutunuzu kontrol edin.'
    })
    startCountdown(60)
  } catch (error) {
    const message = error.response?.data?.detail || 'Email gonderilemedi'
    uiStore.addNotification({
      type: 'error',
      message
    })
    // Rate limit hatasi ise countdown baslat
    if (error.response?.status === 429) {
      const match = message.match(/(\d+)/)
      if (match) {
        startCountdown(parseInt(match[1]))
      }
    }
  } finally {
    sending.value = false
  }
}

function startCountdown(seconds) {
  countdown.value = seconds
  if (countdownInterval) clearInterval(countdownInterval)
  countdownInterval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownInterval)
    }
  }, 1000)
}

function dismissBanner() {
  dismissed.value = true
  // 1 saat sonra tekrar goster
  setTimeout(() => {
    dismissed.value = false
  }, 60 * 60 * 1000)
}

async function checkVerificationStatus() {
  if (!authStore.user || authStore.user.steam_id || authStore.user.email_verified) return

  try {
    const status = await authAPI.getEmailVerificationStatus()
    if (!status.resend_available && status.resend_wait_seconds > 0) {
      startCountdown(status.resend_wait_seconds)
    }
  } catch (error) {
    // Sessiz hata
  }
}

onMounted(() => {
  checkVerificationStatus()
})

onUnmounted(() => {
  if (countdownInterval) clearInterval(countdownInterval)
})
</script>

<style scoped>
.email-verification-banner {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%);
  border-bottom: 1px solid rgba(234, 179, 8, 0.3);
  padding: 12px 16px;
}

.banner-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.banner-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(234, 179, 8, 0.2);
  border-radius: 8px;
  color: #eab308;
  flex-shrink: 0;
}

.banner-text {
  flex: 1;
  min-width: 200px;
}

.banner-title {
  display: block;
  font-weight: 600;
  color: #fbbf24;
  font-size: 14px;
}

.banner-description {
  display: block;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  margin-top: 2px;
}

.banner-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.verify-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #eab308 0%, #f59e0b 100%);
  color: #1a1a2e;
  font-weight: 600;
  font-size: 13px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.verify-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(234, 179, 8, 0.3);
}

.verify-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.verify-btn.disabled {
  background: rgba(234, 179, 8, 0.2);
  color: #fbbf24;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

/* Transitions */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-100%);
}

/* Responsive */
@media (max-width: 640px) {
  .banner-content {
    flex-direction: column;
    text-align: center;
  }

  .banner-text {
    min-width: auto;
  }

  .banner-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
