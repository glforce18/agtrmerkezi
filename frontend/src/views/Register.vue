<template>
  <div class="min-h-screen flex items-center justify-center py-12">
    <div class="container-custom">
      <div class="max-w-2xl mx-auto">
        <div class="text-center mb-8 animate-slide-down">
          <Logo size="lg" variant="glow" />
          <h1 class="text-4xl font-display font-bold mt-6 mb-2">
            <span class="text-gradient-orange">Hesap Oluştur</span>
          </h1>
          <p class="opacity-60">
            CS 1.6 sunucu yönetimine hemen başla!
          </p>
        </div>

        <BaseCard variant="glass" shadow class="animate-slide-up">
          <!-- OAuth Buttons -->
          <div class="space-y-3 mb-6">
            <button
              @click="registerWithOAuth('steam')"
              class="btn btn-block bg-[#171a21] hover:bg-[#0a0b0e] text-white border-0"
              :disabled="loading"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
              </svg>
              Steam ile Kayıt Ol
            </button>

            <button
              @click="registerWithOAuth('discord')"
              class="btn btn-block bg-[#5865F2] hover:bg-[#4752C4] text-white border-0"
              :disabled="loading"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
              Discord ile Kayıt Ol
            </button>

            <button
              @click="registerWithOAuth('google')"
              class="btn btn-block bg-white hover:bg-gray-100 text-gray-800 border border-gray-300"
              :disabled="loading"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google ile Kayıt Ol
            </button>
          </div>

          <div class="divider">VEYA</div>

          <!-- Registration Form -->
          <form @submit.prevent="handleRegister" class="space-y-4">
            <div class="grid md:grid-cols-2 gap-4">
              <BaseInput
                v-model="form.username"
                label="Kullanıcı Adı"
                placeholder="kullaniciadi"
                :error="errors.username"
                required
              />

              <BaseInput
                v-model="form.email"
                label="E-posta"
                type="email"
                placeholder="ornek@email.com"
                :error="errors.email"
                required
              />
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <BaseInput
                v-model="form.password"
                label="Şifre"
                type="password"
                placeholder="••••••••"
                :error="errors.password"
                required
              />

              <BaseInput
                v-model="form.confirm_password"
                label="Şifre (Tekrar)"
                type="password"
                placeholder="••••••••"
                :error="errors.confirm_password"
                required
              />
            </div>

            <!-- Password Requirements -->
            <div class="text-xs opacity-60 space-y-1">
              <p class="font-semibold mb-2">Şifre gereksinimleri:</p>
              <div class="flex items-center gap-2" :class="passwordChecks.length ? 'text-success' : ''">
                <CheckCircleIcon v-if="passwordChecks.length" class="w-3 h-3" />
                <XCircleIcon v-else class="w-3 h-3" />
                En az 8 karakter
              </div>
              <div class="flex items-center gap-2" :class="passwordChecks.uppercase ? 'text-success' : ''">
                <CheckCircleIcon v-if="passwordChecks.uppercase" class="w-3 h-3" />
                <XCircleIcon v-else class="w-3 h-3" />
                En az 1 büyük harf
              </div>
              <div class="flex items-center gap-2" :class="passwordChecks.number ? 'text-success' : ''">
                <CheckCircleIcon v-if="passwordChecks.number" class="w-3 h-3" />
                <XCircleIcon v-else class="w-3 h-3" />
                En az 1 rakam
              </div>
            </div>

            <!-- Terms & Conditions -->
            <label class="flex items-start gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.accept_terms" class="checkbox checkbox-sm mt-1" required />
              <span class="text-sm opacity-60">
                <router-link to="/terms" class="link link-primary">Kullanım Koşulları</router-link> ve
                <router-link to="/privacy" class="link link-primary">Gizlilik Politikası</router-link>'nı
                okudum ve kabul ediyorum
              </span>
            </label>

            <label class="flex items-start gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.newsletter" class="checkbox checkbox-sm mt-1" />
              <span class="text-sm opacity-60">
                Yeni özellikler ve promosyonlar hakkında e-posta almak istiyorum
              </span>
            </label>

            <BaseButton
              type="submit"
              variant="gaming"
              size="lg"
              block
              :loading="loading"
              :disabled="!form.accept_terms"
            >
              Hesap Oluştur
            </BaseButton>
          </form>

          <div class="text-center mt-6">
            <p class="text-sm">
              Zaten hesabın var mı?
              <router-link to="/login" class="link link-primary font-semibold">
                Giriş Yap
              </router-link>
            </p>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Logo from '@/components/common/Logo.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import { CheckCircleIcon, XCircleIcon } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)

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

const passwordChecks = computed(() => ({
  length: form.password.length >= 8,
  uppercase: /[A-Z]/.test(form.password),
  number: /[0-9]/.test(form.password)
}))

const validateForm = () => {
  let isValid = true

  // Username
  if (!form.username) {
    errors.username = 'Kullanıcı adı gerekli'
    isValid = false
  } else if (form.username.length < 3) {
    errors.username = 'Kullanıcı adı en az 3 karakter olmalı'
    isValid = false
  } else {
    errors.username = ''
  }

  // Email
  if (!form.email) {
    errors.email = 'E-posta gerekli'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Geçerli bir e-posta adresi girin'
    isValid = false
  } else {
    errors.email = ''
  }

  // Password
  if (!form.password) {
    errors.password = 'Şifre gerekli'
    isValid = false
  } else if (!passwordChecks.value.length || !passwordChecks.value.uppercase || !passwordChecks.value.number) {
    errors.password = 'Şifre gereksinimleri karşılanmıyor'
    isValid = false
  } else {
    errors.password = ''
  }

  // Confirm Password
  if (form.password !== form.confirm_password) {
    errors.confirm_password = 'Şifreler eşleşmiyor'
    isValid = false
  } else {
    errors.confirm_password = ''
  }

  return isValid
}

const handleRegister = async () => {
  if (!validateForm()) return

  loading.value = true

  try {
    await authStore.register({
      username: form.username,
      email: form.email,
      password: form.password,
      newsletter: form.newsletter
    })

    router.push('/dashboard')
  } catch (error) {
    errors.email = error.message || 'Kayıt başarısız'
  } finally {
    loading.value = false
  }
}

const registerWithOAuth = async (provider) => {
  loading.value = true

  try {
    window.location.href = `/api/auth/oauth/${provider}`
  } catch (error) {
    console.error('OAuth error:', error)
    loading.value = false
  }
}
</script>

<style scoped>
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-down {
  animation: slideDown 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}
</style>
