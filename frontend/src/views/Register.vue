<template>
  <div class="register-page">
    <!-- Animated Background -->
    <div class="animated-bg">
      <!-- Gradient Orbs -->
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>

      <!-- Particles (Reduced for performance) -->
      <div class="particles">
        <div v-for="i in 15" :key="i" class="particle" :style="getParticleStyle(i)"></div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="register-container">
      <!-- Glass Card -->
      <div
        class="glass-card"
        :class="{ 'shake-error': shakeError, 'success-animation': showSuccess }"
      >
        <!-- Success Overlay -->
        <transition name="success-fade">
          <div v-if="showSuccess" class="success-overlay">
            <div class="success-content">
              <div class="success-checkmark">
                <svg viewBox="0 0 52 52" class="checkmark-svg">
                  <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                  <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                </svg>
              </div>
              <h2 class="success-title">Kayıt Başarılı!</h2>
              <p class="success-text">Hosgeldiniz, yonlendiriliyorsunuz...</p>
            </div>
          </div>
        </transition>

        <!-- Step Indicator -->
        <div class="step-indicator">
          <div
            v-for="step in 3"
            :key="step"
            class="step-dot"
            :class="{ 'active': currentStep >= step, 'completed': currentStep > step }"
          >
            <span v-if="currentStep > step" class="step-check">
              <Check :size="12" />
            </span>
            <span v-else>{{ step }}</span>
          </div>
          <div class="step-line">
            <div class="step-line-progress" :style="{ width: stepProgress + '%' }"></div>
          </div>
        </div>

        <!-- Logo -->
        <div class="logo-container">
          <div class="logo-glow"></div>
          <div class="logo">
            <span class="logo-text">A</span>
          </div>
          <h1 class="title">
            <span class="title-gradient">Hesap Oluştur</span>
          </h1>
          <p class="subtitle">CS 1.6 sunucu yönetimine hemen başla!</p>
        </div>

        <!-- OAuth Buttons -->
        <div class="oauth-section">
          <button
            class="oauth-btn steam-btn"
            :disabled="loading"
            @click="registerWithOAuth('steam')"
          >
            <div class="btn-bg"></div>
            <svg class="oauth-icon" fill="currentColor" viewBox="0 0 24 24">
              <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0z"/>
            </svg>
            <span>Steam ile Kayıt Ol</span>
            <div class="btn-shine"></div>
          </button>

          <button
            class="oauth-btn discord-btn"
            :disabled="loading"
            @click="registerWithOAuth('discord')"
          >
            <div class="btn-bg"></div>
            <svg class="oauth-icon" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
            <span>Discord ile Kayıt Ol</span>
            <div class="btn-shine"></div>
          </button>

          <p class="oauth-hint">Önerilen kayıt yöntemi</p>
        </div>

        <!-- Divider -->
        <div class="divider">
          <div class="divider-line"></div>
          <span class="divider-text">veya e-posta ile</span>
          <div class="divider-line"></div>
        </div>

        <!-- Registration Form -->
        <form @submit.prevent="handleRegister" class="register-form">
          <!-- Username Input -->
          <div class="input-group" :class="{ 'focused': focusedField === 'username', 'has-value': form.username, 'has-error': errors.username }">
            <div class="input-icon">
              <User :size="20" />
            </div>
            <input
              v-model="form.username"
              type="text"
              placeholder="Kullanıcı Adı"
              @focus="focusedField = 'username'"
              @blur="focusedField = null; validateField('username')"
            />
            <div class="input-border"></div>
            <div class="input-glow"></div>
          </div>
          <transition name="error-slide">
            <p v-if="errors.username" class="field-error">{{ errors.username }}</p>
          </transition>

          <!-- Email Input -->
          <div class="input-group" :class="{ 'focused': focusedField === 'email', 'has-value': form.email, 'has-error': errors.email }">
            <div class="input-icon">
              <Mail :size="20" />
            </div>
            <input
              v-model="form.email"
              type="email"
              placeholder="E-posta Adresi"
              @focus="focusedField = 'email'"
              @blur="focusedField = null; validateField('email')"
            />
            <div class="input-border"></div>
            <div class="input-glow"></div>
          </div>
          <transition name="error-slide">
            <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
          </transition>

          <!-- Password Input -->
          <div class="input-group" :class="{ 'focused': focusedField === 'password', 'has-value': form.password, 'has-error': errors.password }">
            <div class="input-icon">
              <Lock :size="20" />
            </div>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Şifre"
              @focus="focusedField = 'password'"
              @blur="focusedField = null"
              @input="updatePasswordStrength"
            />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <Eye v-if="!showPassword" :size="20" />
              <EyeOff v-else :size="20" />
            </button>
            <div class="input-border"></div>
            <div class="input-glow"></div>
          </div>

          <!-- Password Strength Meter -->
          <div class="password-strength" v-if="form.password">
            <div class="strength-bar">
              <div
                class="strength-fill"
                :style="{ width: passwordStrength.percent + '%' }"
                :class="passwordStrength.class"
              ></div>
            </div>
            <span class="strength-text" :class="passwordStrength.class">{{ passwordStrength.label }}</span>
          </div>

          <!-- Password Requirements Checklist -->
          <div class="password-requirements" v-if="form.password">
            <div
              v-for="(check, key) in passwordChecks"
              :key="key"
              class="requirement"
              :class="{ 'met': check.met }"
            >
              <div class="requirement-icon">
                <transition name="check-pop" mode="out-in">
                  <Check v-if="check.met" :size="14" class="check-icon" />
                  <X v-else :size="14" class="x-icon" />
                </transition>
              </div>
              <span>{{ check.label }}</span>
            </div>
          </div>

          <!-- Confirm Password Input -->
          <div class="input-group" :class="{ 'focused': focusedField === 'confirm_password', 'has-value': form.confirm_password, 'has-error': errors.confirm_password, 'password-match': passwordsMatch && form.confirm_password }">
            <div class="input-icon">
              <Lock :size="20" />
            </div>
            <input
              v-model="form.confirm_password"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="Şifre (Tekrar)"
              @focus="focusedField = 'confirm_password'"
              @blur="focusedField = null; validateField('confirm_password')"
            />
            <div class="match-indicator" v-if="form.confirm_password">
              <transition name="check-pop" mode="out-in">
                <CheckCircle v-if="passwordsMatch" :size="20" class="match-icon" />
                <XCircle v-else :size="20" class="no-match-icon" />
              </transition>
            </div>
            <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
              <Eye v-if="!showConfirmPassword" :size="20" />
              <EyeOff v-else :size="20" />
            </button>
            <div class="input-border"></div>
            <div class="input-glow"></div>
          </div>
          <transition name="error-slide">
            <p v-if="errors.confirm_password" class="field-error">{{ errors.confirm_password }}</p>
          </transition>

          <!-- Checkboxes -->
          <div class="checkbox-group">
            <label class="custom-checkbox" :class="{ 'checked': form.accept_terms }">
              <input type="checkbox" v-model="form.accept_terms" />
              <div class="checkbox-box">
                <Check :size="14" class="checkbox-check" />
              </div>
              <span class="checkbox-label">
                <router-link to="/terms" class="link">Kullanım Kosullari</router-link> ve
                <router-link to="/privacy" class="link">Gizlilik Politikasi</router-link>'ni
                okudum ve kabul ediyorum
              </span>
            </label>

            <label class="custom-checkbox" :class="{ 'checked': form.newsletter }">
              <input type="checkbox" v-model="form.newsletter" />
              <div class="checkbox-box">
                <Check :size="14" class="checkbox-check" />
              </div>
              <span class="checkbox-label muted">
                Yeni özellikler ve promosyonlar hakkında e-posta almak istiyorum
              </span>
            </label>
          </div>

          <!-- Register Button -->
          <button
            type="submit"
            class="register-btn"
            :class="{ 'loading': loading }"
            :disabled="!form.accept_terms || loading"
          >
            <div class="btn-gradient"></div>
            <div class="btn-content">
              <Loader2 v-if="loading" :size="20" class="spinner" />
              <span v-else>Hesap Oluştur</span>
            </div>
            <div class="btn-shine"></div>
          </button>
        </form>

        <!-- Login Link -->
        <div class="login-link">
          <p>
            Zaten hesabin var mi?
            <router-link to="/login" class="link">Giriş Yap</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessage } from 'naive-ui'
import {
  User, Mail, Lock, Eye, EyeOff, Check, X,
  CheckCircle, XCircle, Loader2
} from 'lucide-vue-next'
import { registerRateLimiter, sanitizeInput, isValidEmail } from '@/utils/security'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const focusedField = ref(null)
const shakeError = ref(false)
const showSuccess = ref(false)
const currentStep = ref(1)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  accept_terms: false,
  newsletter: false
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: ''
})

// Password checks with labels
const passwordChecks = computed(() => ({
  length: { met: form.password.length >= 8, label: 'En az 8 karakter' },
  uppercase: { met: /[A-Z]/.test(form.password), label: 'En az 1 büyük harf' },
  lowercase: { met: /[a-z]/.test(form.password), label: 'En az 1 küçük harf' },
  number: { met: /[0-9]/.test(form.password), label: 'En az 1 rakam' },
  special: { met: /[!@#$%^&*(),.?":{}|<>]/.test(form.password), label: 'En az 1 özel karakter' }
}))

// Password strength calculation (5 levels)
const passwordStrength = computed(() => {
  const checks = Object.values(passwordChecks.value).filter(c => c.met).length
  const levels = [
    { min: 0, max: 1, label: 'Çok Zayif', class: 'very-weak', percent: 20 },
    { min: 2, max: 2, label: 'Zayif', class: 'weak', percent: 40 },
    { min: 3, max: 3, label: 'Orta', class: 'medium', percent: 60 },
    { min: 4, max: 4, label: 'Guclu', class: 'strong', percent: 80 },
    { min: 5, max: 5, label: 'Çok Guclu', class: 'very-strong', percent: 100 }
  ]
  return levels.find(l => checks >= l.min && checks <= l.max) || levels[0]
})

// Password match check
const passwordsMatch = computed(() => {
  return form.password && form.confirm_password && form.password === form.confirm_password
})

// Step progress calculation
const stepProgress = computed(() => {
  if (currentStep.value === 1) return 0
  if (currentStep.value === 2) return 50
  return 100
})

// Watch form fields to update step
watch(() => [form.username, form.email], () => {
  if (form.username && form.email) {
    currentStep.value = Math.max(currentStep.value, 2)
  }
}, { deep: true })

watch(() => [form.password, form.confirm_password], () => {
  if (form.password && form.confirm_password && passwordsMatch.value) {
    currentStep.value = Math.max(currentStep.value, 3)
  }
}, { deep: true })

// Particle style generator
const getParticleStyle = (i) => {
  const random = (min, max) => Math.random() * (max - min) + min
  return {
    left: `${random(0, 100)}%`,
    top: `${random(0, 100)}%`,
    width: `${random(2, 6)}px`,
    height: `${random(2, 6)}px`,
    animationDelay: `${random(0, 5)}s`,
    animationDuration: `${random(3, 8)}s`
  }
}

// Field validation
const validateField = (field) => {
  errors[field] = ''

  switch (field) {
    case 'username':
      if (!form.username) {
        errors.username = 'Kullanıcı adı gerekli'
      } else if (form.username.length < 3) {
        errors.username = 'Kullanıcı adı en az 3 karakter olmalı'
      }
      break
    case 'email':
      if (!form.email) {
        errors.email = 'E-posta gerekli'
      } else if (!isValidEmail(form.email)) {
        errors.email = 'Geçerli bir e-posta adresi girin'
      }
      break
    case 'confirm_password':
      if (!form.confirm_password) {
        errors.confirm_password = 'Şifre tekrari gerekli'
      } else if (form.password !== form.confirm_password) {
        errors.confirm_password = 'Şifreler eşleşmiyor'
      }
      break
  }
}

// Update password strength (for any additional logic)
const updatePasswordStrength = () => {
  // Strength is computed automatically
}

// Trigger shake animation
const triggerShake = () => {
  shakeError.value = true
  setTimeout(() => {
    shakeError.value = false
  }, 500)
}

// Handle registration
const handleRegister = async () => {
  // Rate limiting check
  const rateCheck = registerRateLimiter.check('register')
  if (!rateCheck.allowed) {
    message.error(`Çok fazla deneme. ${rateCheck.resetIn} saniye sonra tekrar deneyin.`)
    return
  }

  // Validate all fields
  validateField('username')
  validateField('email')
  validateField('confirm_password')

  // Check password requirements
  const allChecksMet = Object.values(passwordChecks.value).every(c => c.met)
  if (!allChecksMet) {
    errors.password = 'Şifre gereksinimleri karşılanmıyor'
    triggerShake()
    return
  }

  // Check for any errors
  if (Object.values(errors).some(e => e)) {
    triggerShake()
    return
  }

  if (!form.accept_terms) {
    message.warning('Kullanım kosullarini kabul etmelisiniz')
    triggerShake()
    return
  }

  loading.value = true

  try {
    await authStore.register({
      username: sanitizeInput(form.username.trim()),
      email: sanitizeInput(form.email.trim().toLowerCase()),
      password: form.password,
      newsletter: form.newsletter
    })

    // Show success animation
    showSuccess.value = true

    setTimeout(() => {
      router.push('/dashboard')
    }, 2000)
  } catch (error) {
    triggerShake()
    message.error(error.response?.data?.detail || error.message || 'Kayıt başarısız')
  } finally {
    loading.value = false
  }
}

const registerWithOAuth = async (provider) => {
  loading.value = true
  window.location.href = `/api/auth/oauth/${provider}`
}
</script>

<style scoped>
/* Page Container */
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  position: relative;
  overflow: hidden;
}

/* Animated Background */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
}

/* Gradient Orbs */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: float 15s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #f97316 0%, transparent 70%);
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #fb923c 0%, transparent 70%);
  bottom: -50px;
  left: -50px;
  animation-delay: -5s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, #ea580c 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  75% {
    transform: translate(-30px, -20px) scale(1.05);
  }
}

/* Particles */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(249, 115, 22, 0.6);
  border-radius: 50%;
  animation: particle-float linear infinite;
}

@keyframes particle-float {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(720deg);
    opacity: 0;
  }
}

/* Main Container */
.register-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 480px;
}

/* Glass Card */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2.5rem;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(249, 115, 22, 0.5), transparent);
}

/* Shake Animation */
.shake-error {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* Success Animation */
.success-animation {
  transform: scale(1.02);
}

.success-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 10, 10, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: 24px;
}

.success-content {
  text-align: center;
}

.success-checkmark {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
}

.checkmark-svg {
  width: 100%;
  height: 100%;
}

.checkmark-circle {
  stroke: #22c55e;
  stroke-width: 2;
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}

.checkmark-check {
  stroke: #22c55e;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

@keyframes stroke {
  100% { stroke-dashoffset: 0; }
}

.success-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #22c55e;
  margin-bottom: 0.5rem;
}

.success-text {
  color: var(--text-secondary);
}

.success-fade-enter-active {
  animation: success-fade-in 0.5s ease;
}

@keyframes success-fade-in {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Step Indicator */
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 2rem;
  position: relative;
}

.step-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.step-dot.active {
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-color: #f97316;
  color: white;
  box-shadow: 0 0 20px rgba(249, 115, 22, 0.5);
}

.step-dot.completed {
  background: #22c55e;
  border-color: #22c55e;
  color: white;
}

.step-check {
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-line {
  position: absolute;
  top: 50%;
  left: 50px;
  right: 50px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-50%);
  z-index: 1;
}

.step-line-progress {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #f97316);
  transition: width 0.5s ease;
}

/* Logo */
.logo-container {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  animation: logo-pulse 2s ease-in-out infinite;
}

.logo-glow {
  position: absolute;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: #f97316;
  filter: blur(20px);
  opacity: 0.5;
  animation: glow-pulse 2s ease-in-out infinite;
}

@keyframes logo-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

.logo-text {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.title-gradient {
  background: linear-gradient(135deg, #f97316, #fb923c, #f97316);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 3s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* OAuth Section */
.oauth-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.oauth-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  color: white;
  border: none;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.oauth-btn .btn-bg {
  position: absolute;
  inset: 0;
  transition: all 0.3s ease;
}

.oauth-btn .btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.oauth-btn:hover .btn-shine {
  left: 100%;
}

.oauth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.steam-btn .btn-bg {
  background: linear-gradient(135deg, #1b2838 0%, #171a21 100%);
}

.steam-btn {
  border: 2px solid #66c0f4;
}

.steam-btn:hover:not(:disabled) {
  border-color: #8ed0f8;
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 192, 244, 0.3);
}

.discord-btn .btn-bg {
  background: linear-gradient(135deg, #5865F2 0%, #4752c4 100%);
}

.discord-btn {
  border: 2px solid #7289da;
}

.discord-btn:hover:not(:disabled) {
  border-color: #99aab5;
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(114, 137, 218, 0.3);
}

.oauth-icon {
  width: 20px;
  height: 20px;
  position: relative;
  z-index: 1;
}

.oauth-btn span {
  position: relative;
  z-index: 1;
}

.oauth-hint {
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
}

.divider-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Form */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Input Group */
.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: rgba(255, 255, 255, 0.4);
  transition: color 0.3s ease;
  z-index: 2;
}

.input-group input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 0.95rem;
  color: var(--text-primary);
  transition: all 0.3s ease;
  outline: none;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-border {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  pointer-events: none;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.input-glow {
  position: absolute;
  inset: -2px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
  filter: blur(8px);
}

.input-group.focused .input-icon {
  color: #f97316;
}

.input-group.focused input {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

.input-group.focused .input-glow {
  opacity: 0.3;
}

.input-group.has-value .input-icon {
  color: #f97316;
}

.input-group.has-error input {
  border-color: #ef4444;
}

.input-group.has-error .input-icon {
  color: #ef4444;
}

.input-group.password-match input {
  border-color: #22c55e;
}

.input-group.password-match .input-icon {
  color: #22c55e;
}

.toggle-password {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.3s ease;
  z-index: 2;
}

.toggle-password:hover {
  color: #f97316;
}

.match-indicator {
  position: absolute;
  right: 3rem;
  z-index: 2;
}

.match-icon {
  color: #22c55e;
  animation: pop-in 0.3s ease;
}

.no-match-icon {
  color: #ef4444;
}

@keyframes pop-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.field-error {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: -0.5rem;
  padding-left: 1rem;
}

.error-slide-enter-active,
.error-slide-leave-active {
  transition: all 0.3s ease;
}

.error-slide-enter-from,
.error-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Password Strength */
.password-strength {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: -0.5rem;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.strength-fill.very-weak { background: #ef4444; }
.strength-fill.weak { background: #f97316; }
.strength-fill.medium { background: #eab308; }
.strength-fill.strong { background: #84cc16; }
.strength-fill.very-strong { background: #22c55e; }

.strength-text {
  font-size: 0.7rem;
  font-weight: 600;
  min-width: 70px;
  text-align: right;
}

.strength-text.very-weak { color: #ef4444; }
.strength-text.weak { color: #f97316; }
.strength-text.medium { color: #eab308; }
.strength-text.strong { color: #84cc16; }
.strength-text.very-strong { color: #22c55e; }

/* Password Requirements */
.password-requirements {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  margin-top: -0.5rem;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
  transition: color 0.3s ease;
}

.requirement.met {
  color: #22c55e;
}

.requirement-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  color: #22c55e;
}

.x-icon {
  color: rgba(255, 255, 255, 0.3);
}

.check-pop-enter-active {
  animation: check-pop 0.3s ease;
}

@keyframes check-pop {
  0% { transform: scale(0) rotate(-45deg); }
  50% { transform: scale(1.3) rotate(10deg); }
  100% { transform: scale(1) rotate(0deg); }
}

/* Checkboxes */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 0.5rem 0;
}

.custom-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
}

.custom-checkbox input {
  display: none;
}

.checkbox-box {
  width: 20px;
  height: 20px;
  min-width: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
}

.checkbox-check {
  color: white;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s ease;
}

.custom-checkbox.checked .checkbox-box {
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-color: #f97316;
}

.custom-checkbox.checked .checkbox-check {
  opacity: 1;
  transform: scale(1);
}

.checkbox-label {
  font-size: 0.8rem;
  color: var(--text-primary);
  line-height: 1.4;
}

.checkbox-label.muted {
  color: var(--text-secondary);
}

.checkbox-label .link {
  color: #f97316;
  text-decoration: none;
  transition: color 0.3s ease;
}

.checkbox-label .link:hover {
  color: #fb923c;
  text-decoration: underline;
}

/* Register Button */
.register-btn {
  position: relative;
  width: 100%;
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.register-btn .btn-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #c2410c 100%);
  background-size: 200% auto;
  transition: all 0.3s ease;
}

.register-btn:hover:not(:disabled) .btn-gradient {
  background-position: right center;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 40px rgba(249, 115, 22, 0.4);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.register-btn .btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.register-btn .btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.register-btn:hover:not(:disabled) .btn-shine {
  left: 100%;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.register-btn.loading .btn-gradient {
  animation: gradient-pulse 1.5s ease-in-out infinite;
}

@keyframes gradient-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Login Link */
.login-link {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.login-link p {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.login-link .link {
  color: #f97316;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.3s ease;
  margin-left: 0.25rem;
}

.login-link .link:hover {
  color: #fb923c;
  text-decoration: underline;
}

/* Mobile Responsive */
@media (max-width: 640px) {
  .register-page {
    padding: 1rem 0.75rem;
  }

  .glass-card {
    padding: 1.5rem;
    border-radius: 20px;
  }

  .logo {
    width: 56px;
    height: 56px;
  }

  .logo-glow {
    width: 56px;
    height: 56px;
  }

  .logo-text {
    font-size: 1.75rem;
  }

  .title {
    font-size: 1.5rem;
  }

  .step-indicator {
    margin-bottom: 1.5rem;
  }

  .step-dot {
    width: 24px;
    height: 24px;
    font-size: 0.7rem;
  }

  .step-line {
    left: 40px;
    right: 40px;
  }

  .password-requirements {
    grid-template-columns: 1fr;
  }

  .oauth-btn {
    padding: 0.75rem 1.25rem;
    font-size: 0.85rem;
  }

  .input-group input {
    padding: 0.875rem 0.875rem 0.875rem 2.75rem;
    font-size: 0.9rem;
  }

  .orb-1 {
    width: 250px;
    height: 250px;
  }

  .orb-2 {
    width: 200px;
    height: 200px;
  }

  .orb-3 {
    width: 150px;
    height: 150px;
  }
}

@media (max-width: 380px) {
  .glass-card {
    padding: 1.25rem;
  }

  .title {
    font-size: 1.25rem;
  }

  .subtitle {
    font-size: 0.8rem;
  }

  .checkbox-label {
    font-size: 0.75rem;
  }
}
</style>
