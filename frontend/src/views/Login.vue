<template>
  <div class="auth-page">
    <!-- Left Panel - Animated Background -->
    <div class="left-panel">
      <!-- Particle Canvas -->
      <canvas ref="particleCanvas" class="particle-canvas"></canvas>

      <!-- Gradient Orbs -->
      <div class="gradient-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
      </div>

      <!-- Floating Gaming Icons -->
      <div class="floating-icons">
        <div class="floating-icon icon-1">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M21.58 16.09l-1.09-7.66C20.21 6.46 18.52 5 16.53 5H7.47C5.48 5 3.79 6.46 3.51 8.43l-1.09 7.66C2.2 17.63 3.39 19 4.94 19c.68 0 1.32-.27 1.8-.75L9 16h6l2.25 2.25c.48.48 1.13.75 1.8.75 1.56 0 2.75-1.37 2.53-2.91zM11 11H9v2H8v-2H6v-1h2V8h1v2h2v1zm4-1c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm2 3c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
          </svg>
        </div>
        <div class="floating-icon icon-2">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <div class="floating-icon icon-3">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/>
          </svg>
        </div>
        <div class="floating-icon icon-4">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
          </svg>
        </div>
      </div>

      <!-- Content -->
      <div class="left-content">
        <!-- Animated Logo -->
        <div class="logo-container">
          <div class="logo-glow"></div>
          <div class="logo">
            <div class="logo-icon">
              <span>A</span>
            </div>
            <div class="logo-text">
              <span class="logo-agtr">AGTR</span>
              <span class="logo-merkezi">Merkezi</span>
            </div>
          </div>
        </div>

        <!-- Tagline -->
        <div class="tagline">
          <h1>Hos Geldiniz!</h1>
          <p>Counter-Strike 1.6 sunucu yönetiminde yeni nesil platform</p>
        </div>

        <!-- Feature Highlights -->
        <div class="features">
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3>7/24 Destek</h3>
              <p>Her zaman yaninizdayiz</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M13 2.05v2.02c3.95.49 7 3.85 7 7.93 0 3.21-1.92 6-4.72 7.28L13 17v5h5l-1.22-1.22C19.91 19.07 22 15.76 22 12c0-5.18-3.95-9.45-9-9.95zM11 2.05c-5.05.5-9 4.77-9 9.95 0 3.76 2.09 7.07 5.22 8.78L6 22h5v-5l-2.28 2.28C6.92 18 5 15.21 5 12c0-4.08 3.05-7.44 7-7.93V2.05z"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3>Hızlı Sunucular</h3>
              <p>Dusuk ping, yuksek performans</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3>Topluluk</h3>
              <p>Binlerce oyuncu ile tanis</p>
            </div>
          </div>
        </div>

        <!-- Animated Stats -->
        <div class="stats">
          <div class="stat-item">
            <div class="stat-value">
              <span class="counter" data-target="1000">{{ animatedStats.servers }}</span>
              <span class="stat-plus">+</span>
            </div>
            <div class="stat-label">Aktif Sunucu</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">
              <span class="counter">{{ animatedStats.users }}</span>
              <span class="stat-plus">K+</span>
            </div>
            <div class="stat-label">Kullanıcı</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">
              <span class="counter">{{ animatedStats.uptime }}</span>
              <span class="stat-plus">%</span>
            </div>
            <div class="stat-label">Uptime</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel - Login Form -->
    <div class="right-panel">
      <div class="login-container">
        <!-- Mobile Logo -->
        <div class="mobile-logo">
          <div class="logo">
            <div class="logo-icon">
              <span>A</span>
            </div>
            <div class="logo-text">
              <span class="logo-agtr">AGTR</span>
              <span class="logo-merkezi">Merkezi</span>
            </div>
          </div>
        </div>

        <!-- Glass Card -->
        <div class="glass-card">
          <div class="card-header">
            <h2>Giriş Yap</h2>
            <p>Hesabınıza erisim sağlayin</p>
          </div>

          <!-- OAuth Buttons -->
          <div class="oauth-buttons">
            <button
              class="oauth-btn steam-btn"
              :disabled="loading"
              @click="loginWithOAuth('steam')"
              @keydown.enter="loginWithOAuth('steam')"
            >
              <div class="btn-content">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0z"/>
                </svg>
                <span>Steam ile Giriş Yap</span>
              </div>
              <div class="btn-shine"></div>
            </button>

            <button
              class="oauth-btn discord-btn"
              :disabled="loading"
              @click="loginWithOAuth('discord')"
              @keydown.enter="loginWithOAuth('discord')"
            >
              <div class="btn-content">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
                <span>Discord ile Giriş Yap</span>
              </div>
              <div class="btn-shine"></div>
            </button>
          </div>

          <p class="oauth-hint">Önerilen giriş yöntemi</p>

          <!-- Divider -->
          <div class="divider">
            <span>veya e-posta ile</span>
          </div>

          <!-- Login Form -->
          <form @submit.prevent="handleLogin" class="login-form">
            <div class="input-group" :class="{ 'focused': focusedInput === 'username', 'has-value': form.username }">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <input
                id="login-username"
                type="text"
                v-model="form.username"
                placeholder="Kullanıcı Adı"
                @focus="focusedInput = 'username'"
                @blur="focusedInput = null"
                @keydown.tab.exact="focusedInput = 'password'"
                autocomplete="username"
                aria-label="Kullanıcı Adı"
                aria-required="true"
              />
              <div class="input-glow"></div>
            </div>

            <div class="input-group" :class="{ 'focused': focusedInput === 'password', 'has-value': form.password }">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                </svg>
              </div>
              <input
                id="login-password"
                :type="showPassword ? 'text' : 'password'"
                v-model="form.password"
                placeholder="Şifre"
                @focus="focusedInput = 'password'"
                @blur="focusedInput = null"
                autocomplete="current-password"
                aria-label="Şifre"
                aria-required="true"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                tabindex="-1"
                :aria-label="showPassword ? 'Şifreyi gizle' : 'Şifreyi göster'"
              >
                <svg v-if="!showPassword" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46A11.804 11.804 0 0 0 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>
                </svg>
              </button>
              <div class="input-glow"></div>
            </div>

            <!-- Remember Me & Forgot Password -->
            <div class="form-options">
              <label class="custom-checkbox">
                <input type="checkbox" v-model="form.remember" />
                <span class="checkmark"></span>
                <span class="checkbox-label">Beni Hatirla</span>
              </label>
              <router-link to="/forgot-password" class="forgot-link">
                Şifremi Unuttum
              </router-link>
            </div>

            <!-- Error Message -->
            <transition name="shake">
              <div v-if="errorMessage" class="error-message">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
                <span>{{ errorMessage }}</span>
              </div>
            </transition>

            <!-- Login Button -->
            <button
              type="submit"
              class="login-btn"
              :disabled="loading || !form.username || !form.password"
              :class="{ 'loading': loading }"
            >
              <span v-if="!loading">Giriş Yap</span>
              <div v-else class="spinner">
                <div class="spinner-ring"></div>
              </div>
            </button>
          </form>

          <!-- Register Link -->
          <div class="register-link">
            <p>Hesabin yok mu?</p>
            <router-link to="/register">Kayıt Ol</router-link>
          </div>
        </div>

        <!-- Footer -->
        <div class="login-footer">
          <p>&copy; 2024 AGTR Merkezi. Tüm hakları saklıdır.</p>
        </div>
      </div>
    </div>

    <!-- 2FA Modal -->
    <Teleport to="body">
      <transition name="modal">
        <div v-if="show2FAModal" class="modal-overlay" @click.self="show2FAModal = false">
          <div class="modal-2fa">
            <div class="modal-header">
              <div class="modal-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
                </svg>
              </div>
              <h3>İki Faktörlü Doğrulama</h3>
              <p>Authenticator uygulamanizdan 6 haneli kodu girin</p>
            </div>

            <div class="otp-container">
              <div class="otp-inputs">
                <input
                  v-for="(_, index) in 6"
                  :key="index"
                  :ref="el => otpInputs[index] = el"
                  type="text"
                  maxlength="1"
                  class="otp-input"
                  :value="otpDigits[index]"
                  @input="handleOtpInput($event, index)"
                  @keydown="handleOtpKeydown($event, index)"
                  @paste="handleOtpPaste"
                  @focus="$event.target.select()"
                  inputmode="numeric"
                  pattern="[0-9]*"
                />
              </div>
            </div>

            <div class="modal-actions">
              <button class="modal-btn cancel" @click="show2FAModal = false">
                İptal
              </button>
              <button
                class="modal-btn confirm"
                :disabled="verifying2FA || twoFactorCode.length !== 6"
                @click="handle2FAVerify"
              >
                <span v-if="!verifying2FA">Doğrula</span>
                <div v-else class="spinner small">
                  <div class="spinner-ring"></div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- Toast Notifications -->
    <Teleport to="body">
      <transition-group name="toast" tag="div" class="toast-container">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="toast.type"
        >
          <div class="toast-icon">
            <svg v-if="toast.type === 'success'" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
          </div>
          <span>{{ toast.message }}</span>
        </div>
      </transition-group>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { loginRateLimiter, sanitizeInput } from '@/utils/security'

const router = useRouter()
const authStore = useAuthStore()

// Refs
const particleCanvas = ref(null)
const focusedInput = ref(null)
const showPassword = ref(false)
const loading = ref(false)
const show2FAModal = ref(false)
const verifying2FA = ref(false)
const pendingLoginData = ref(null)
const twoFactorCode = ref('')
const otpDigits = ref(['', '', '', '', '', ''])
const otpInputs = ref([])
const errorMessage = ref('')
const toasts = ref([])
const animatedStats = reactive({
  servers: 0,
  users: 0,
  uptime: 0
})

// Form data
const form = reactive({
  username: '',
  password: '',
  remember: false
})

// Particle animation
let particleAnimationId = null
let particles = []
let resizeHandler = null

const initParticles = () => {
  const canvas = particleCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  resizeHandler = () => {
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight
  }
  resizeHandler()
  window.addEventListener('resize', resizeHandler)

  // Create particles
  for (let i = 0; i < 50; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 2 + 1,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      alpha: Math.random() * 0.5 + 0.2
    })
  }

  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    particles.forEach((p, i) => {
      p.x += p.vx
      p.y += p.vy

      if (p.x < 0 || p.x > canvas.width) p.vx *= -1
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(249, 115, 22, ${p.alpha})`
      ctx.fill()

      // Connect nearby particles
      particles.slice(i + 1).forEach(p2 => {
        const dx = p.x - p2.x
        const dy = p.y - p2.y
        const dist = Math.sqrt(dx * dx + dy * dy)

        if (dist < 100) {
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.strokeStyle = `rgba(249, 115, 22, ${0.1 * (1 - dist / 100)})`
          ctx.stroke()
        }
      })
    })

    particleAnimationId = requestAnimationFrame(animate)
  }

  animate()
}

// Animate stats
const animateStats = () => {
  const duration = 2000
  const startTime = Date.now()
  const targets = { servers: 1000, users: 50, uptime: 99.9 }

  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeOut = 1 - Math.pow(1 - progress, 3)

    animatedStats.servers = Math.floor(targets.servers * easeOut)
    animatedStats.users = Math.floor(targets.users * easeOut)
    animatedStats.uptime = (targets.uptime * easeOut).toFixed(1)

    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }

  animate()
}

// OTP handling
const handleOtpInput = (event, index) => {
  const value = event.target.value.replace(/\D/g, '')
  otpDigits.value[index] = value

  if (value && index < 5) {
    nextTick(() => {
      otpInputs.value[index + 1]?.focus()
    })
  }

  twoFactorCode.value = otpDigits.value.join('')
}

const handleOtpKeydown = (event, index) => {
  if (event.key === 'Backspace' && !otpDigits.value[index] && index > 0) {
    nextTick(() => {
      otpInputs.value[index - 1]?.focus()
    })
  }
  if (event.key === 'ArrowLeft' && index > 0) {
    otpInputs.value[index - 1]?.focus()
  }
  if (event.key === 'ArrowRight' && index < 5) {
    otpInputs.value[index + 1]?.focus()
  }
}

const handleOtpPaste = (event) => {
  event.preventDefault()
  const paste = event.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
  paste.split('').forEach((char, i) => {
    otpDigits.value[i] = char
  })
  twoFactorCode.value = otpDigits.value.join('')

  const focusIndex = Math.min(paste.length, 5)
  nextTick(() => {
    otpInputs.value[focusIndex]?.focus()
  })
}

// Toast notifications
const showToast = (message, type = 'success') => {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 4000)
}

// Login handlers
const handleLogin = async () => {
  if (!form.username || !form.password) {
    errorMessage.value = 'Kullanıcı adı ve şifre gerekli'
    return
  }

  // Rate limiting check
  const rateCheck = loginRateLimiter.check('login')
  if (!rateCheck.allowed) {
    errorMessage.value = `Çok fazla deneme. ${rateCheck.resetIn} saniye sonra tekrar deneyin.`
    return
  }

  errorMessage.value = ''
  loading.value = true

  try {
    const response = await authStore.login({
      username: sanitizeInput(form.username.trim()),
      password: form.password,
      remember: form.remember
    })

    if (response.requires_2fa) {
      pendingLoginData.value = response
      show2FAModal.value = true
      nextTick(() => {
        otpInputs.value[0]?.focus()
      })
    } else {
      showToast('Giriş başarılı!')
      router.push('/dashboard')
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || error.message || 'Giriş başarısız'
    showToast(errorMessage.value, 'error')
  } finally {
    loading.value = false
  }
}

const handle2FAVerify = async () => {
  if (!twoFactorCode.value || twoFactorCode.value.length !== 6) {
    showToast('6 haneli kodu girin', 'error')
    return
  }

  verifying2FA.value = true

  try {
    await authStore.verify2FA({
      user_id: pendingLoginData.value.user_id,
      code: twoFactorCode.value
    })

    show2FAModal.value = false
    showToast('Giriş başarılı!')
    router.push('/dashboard')
  } catch (error) {
    showToast(error.response?.data?.detail || 'Doğrulama başarısız', 'error')
  } finally {
    verifying2FA.value = false
  }
}

const loginWithOAuth = async (provider) => {
  loading.value = true
  window.location.href = `/api/auth/oauth/${provider}`
}

// Reset OTP when modal opens
watch(show2FAModal, (val) => {
  if (val) {
    otpDigits.value = ['', '', '', '', '', '']
    twoFactorCode.value = ''
  }
})

// Lifecycle
onMounted(() => {
  initParticles()
  animateStats()
})

onUnmounted(() => {
  if (particleAnimationId) {
    cancelAnimationFrame(particleAnimationId)
  }
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  particles = []
})
</script>

<style scoped>
/* Base Layout */
.auth-page {
  display: flex;
  min-height: 100vh;
  background: #0a0a0a;
}

/* Left Panel */
.left-panel {
  display: none;
  width: 55%;
  position: relative;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
  overflow: hidden;
}

@media (min-width: 1024px) {
  .left-panel {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* Gradient Orbs */
.gradient-orbs {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  bottom: -50px;
  right: -50px;
  animation-delay: -7s;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #fdba74, #f97316);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.1); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(10px, 10px) scale(1.05); }
}

/* Floating Icons */
.floating-icons {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}

.floating-icon {
  position: absolute;
  width: 50px;
  height: 50px;
  color: rgba(249, 115, 22, 0.3);
  animation: floatIcon 15s ease-in-out infinite;
}

.floating-icon svg {
  width: 100%;
  height: 100%;
}

.icon-1 { top: 10%; left: 10%; animation-delay: 0s; }
.icon-2 { top: 20%; right: 15%; animation-delay: -3s; }
.icon-3 { bottom: 30%; left: 20%; animation-delay: -6s; }
.icon-4 { bottom: 15%; right: 10%; animation-delay: -9s; }

@keyframes floatIcon {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.3; }
  50% { transform: translateY(-20px) rotate(10deg); opacity: 0.5; }
}

/* Left Content */
.left-content {
  position: relative;
  z-index: 10;
  padding: 3rem;
  max-width: 500px;
}

/* Logo */
.logo-container {
  position: relative;
  margin-bottom: 2rem;
}

.logo-glow {
  position: absolute;
  width: 80px;
  height: 80px;
  background: #f97316;
  filter: blur(40px);
  opacity: 0.5;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 40px rgba(249, 115, 22, 0.4);
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.logo-icon span {
  color: white;
  font-size: 2rem;
  font-weight: 800;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-agtr {
  font-size: 1.75rem;
  font-weight: 800;
  color: white;
  line-height: 1;
}

.logo-merkezi {
  font-size: 1.75rem;
  font-weight: 800;
  color: #f97316;
  line-height: 1;
}

/* Tagline */
.tagline {
  margin-bottom: 2.5rem;
}

.tagline h1 {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, #f97316);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.75rem;
}

.tagline p {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.6);
}

/* Features */
.features {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 2.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
  transform: translateX(10px);
}

.feature-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.feature-text h3 {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.feature-text p {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Stats */
.stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}

.stat-value .counter {
  font-size: 2rem;
  font-weight: 800;
  color: #f97316;
}

.stat-plus {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f97316;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 0.25rem;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
}

/* Right Panel */
.right-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
}

@media (min-width: 1024px) {
  .right-panel {
    width: 45%;
    flex: none;
  }
}

.login-container {
  width: 100%;
  max-width: 440px;
}

/* Mobile Logo */
.mobile-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

@media (min-width: 1024px) {
  .mobile-logo {
    display: none;
  }
}

.mobile-logo .logo-icon {
  width: 50px;
  height: 50px;
}

.mobile-logo .logo-icon span {
  font-size: 1.5rem;
}

.mobile-logo .logo-agtr,
.mobile-logo .logo-merkezi {
  font-size: 1.5rem;
}

/* Glass Card */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2.5rem;
  backdrop-filter: blur(20px);
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.card-header p {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* OAuth Buttons */
.oauth-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.oauth-btn {
  position: relative;
  width: 100%;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.oauth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.btn-icon {
  width: 22px;
  height: 22px;
}

.btn-content span {
  font-size: 0.95rem;
  font-weight: 600;
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  z-index: 1;
  transition: left 0.5s ease;
}

.oauth-btn:hover .btn-shine {
  left: 100%;
}

/* Steam Button */
.steam-btn {
  background: linear-gradient(135deg, #1b2838, #171a21);
  border: 2px solid #66c0f4;
  color: white;
}

.steam-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2a475e, #1b2838);
  box-shadow: 0 0 30px rgba(102, 192, 244, 0.3);
  transform: translateY(-2px);
}

/* Discord Button */
.discord-btn {
  background: linear-gradient(135deg, #5865f2, #4752c4);
  border: 2px solid #7289da;
  color: white;
}

.discord-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #6975f5, #5865f2);
  box-shadow: 0 0 30px rgba(88, 101, 242, 0.3);
  transform: translateY(-2px);
}

.oauth-hint {
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
}

.divider span {
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Login Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Input Group */
.input-group {
  position: relative;
}

.input-group input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
  outline: none;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.input-group.focused input,
.input-group input:focus {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

.input-group.has-value input {
  border-color: rgba(249, 115, 22, 0.5);
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.4);
  transition: color 0.3s ease;
  z-index: 2;
}

.input-group.focused .input-icon,
.input-group.has-value .input-icon {
  color: #f97316;
}

.input-glow {
  position: absolute;
  inset: -2px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  opacity: 0;
  filter: blur(8px);
  transition: opacity 0.3s ease;
  z-index: -1;
}

.input-group.focused .input-glow {
  opacity: 0.3;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s ease;
}

.password-toggle:hover {
  color: #f97316;
}

.password-toggle svg {
  width: 20px;
  height: 20px;
}

/* Form Options */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
}

/* Custom Checkbox */
.custom-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.custom-checkbox input {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.custom-checkbox input:checked + .checkmark {
  background: #f97316;
  border-color: #f97316;
}

.custom-checkbox input:checked + .checkmark::after {
  content: '';
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-bottom: 2px;
}

.checkbox-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* Forgot Link */
.forgot-link {
  font-size: 0.9rem;
  color: #f97316;
  text-decoration: none;
  position: relative;
  transition: color 0.3s ease;
}

.forgot-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: #f97316;
  transition: width 0.3s ease;
}

.forgot-link:hover::after {
  width: 100%;
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #ef4444;
  font-size: 0.9rem;
}

.error-message svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.shake-enter-active {
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}

/* Login Button */
.login-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
  position: relative;
  overflow: hidden;
}

.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #fb923c, #f97316);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.login-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(249, 115, 22, 0.4);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-btn span {
  position: relative;
  z-index: 1;
}

/* Spinner */
.spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-ring {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner.small .spinner-ring {
  width: 18px;
  height: 18px;
  border-width: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Register Link */
.register-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.register-link p {
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.register-link a {
  font-size: 0.95rem;
  font-weight: 600;
  color: #f97316;
  text-decoration: none;
  transition: all 0.3s ease;
}

.register-link a:hover {
  color: #fb923c;
  text-shadow: 0 0 20px rgba(249, 115, 22, 0.5);
}

/* Footer */
.login-footer {
  text-align: center;
  margin-top: 2rem;
}

.login-footer p {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* 2FA Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 1000;
}

.modal-2fa {
  background: linear-gradient(135deg, #1a1a1a, #0f0f0f);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-header {
  text-align: center;
  margin-bottom: 2rem;
}

.modal-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.modal-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.modal-header p {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* OTP Inputs */
.otp-container {
  margin-bottom: 2rem;
}

.otp-inputs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.otp-input {
  width: 48px;
  height: 56px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  outline: none;
  transition: all 0.3s ease;
}

.otp-input:focus {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  box-shadow: 0 0 20px rgba(249, 115, 22, 0.3);
}

.otp-input:not(:placeholder-shown) {
  border-color: rgba(249, 115, 22, 0.5);
}

/* Modal Actions */
.modal-actions {
  display: flex;
  gap: 1rem;
}

.modal-btn {
  flex: 1;
  padding: 0.875rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-btn.cancel {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

.modal-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.15);
}

.modal-btn.confirm {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
}

.modal-btn.confirm:hover:not(:disabled) {
  box-shadow: 0 5px 20px rgba(249, 115, 22, 0.4);
}

.modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-2fa,
.modal-leave-to .modal-2fa {
  transform: scale(0.9) translateY(20px);
}

/* Toast Container */
.toast-container {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 2000;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.toast.success {
  border-color: rgba(34, 197, 94, 0.3);
}

.toast.success .toast-icon {
  color: #22c55e;
}

.toast.error {
  border-color: rgba(239, 68, 68, 0.3);
}

.toast.error .toast-icon {
  color: #ef4444;
}

.toast-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.toast-icon svg {
  width: 100%;
  height: 100%;
}

/* Toast Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.9);
}

.toast-move {
  transition: transform 0.4s ease;
}

/* Responsive */
@media (max-width: 480px) {
  .glass-card {
    padding: 1.5rem;
  }

  .otp-input {
    width: 40px;
    height: 48px;
    font-size: 1.25rem;
  }
}
</style>
