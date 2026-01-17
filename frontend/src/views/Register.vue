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
          <!-- Steam Register - Primary -->
          <div class="mb-6">
            <button
              @click="registerWithOAuth('steam')"
              class="steam-btn w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3 transition-all"
              :disabled="loading"
            >
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
              </svg>
              Steam ile Kayıt Ol
            </button>
            <p class="text-center text-sm opacity-60 mt-2">Önerilen kayıt yöntemi</p>
          </div>

          <div class="divider">veya e-posta ile</div>

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

.steam-btn {
  background: linear-gradient(135deg, #1b2838 0%, #171a21 100%);
  border: 2px solid #66c0f4;
  color: #ffffff;
  box-shadow: 0 0 20px rgba(102, 192, 244, 0.3);
}

.steam-btn:hover {
  background: linear-gradient(135deg, #2a475e 0%, #1b2838 100%);
  border-color: #66c0f4;
  box-shadow: 0 0 30px rgba(102, 192, 244, 0.5);
  transform: translateY(-2px);
}

.steam-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>
