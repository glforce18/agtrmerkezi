<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-base-100 to-secondary/10">
    <div class="container-custom py-12">
      <div class="grid lg:grid-cols-2 gap-8 items-center">

        <!-- Left Side - Branding -->
        <div class="hidden lg:block space-y-6 animate-slide-right">
          <Logo size="xl" variant="glow" :show-subtitle="true" />

          <div class="space-y-4">
            <h1 class="text-5xl font-display font-bold neon-text">
              Hoş Geldiniz!
            </h1>
            <p class="text-xl opacity-80">
              Counter-Strike 1.6 sunucu yönetiminde yeni nesil platform
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4 mt-8">
            <div class="glass-card p-4 rounded-lg">
              <div class="text-3xl font-bold text-primary">1000+</div>
              <div class="text-sm opacity-70">Aktif Sunucu</div>
            </div>
            <div class="glass-card p-4 rounded-lg">
              <div class="text-3xl font-bold text-secondary">50K+</div>
              <div class="text-sm opacity-70">Kullanıcı</div>
            </div>
            <div class="glass-card p-4 rounded-lg">
              <div class="text-3xl font-bold text-accent">24/7</div>
              <div class="text-sm opacity-70">Destek</div>
            </div>
            <div class="glass-card p-4 rounded-lg">
              <div class="text-3xl font-bold text-success">99.9%</div>
              <div class="text-sm opacity-70">Uptime</div>
            </div>
          </div>
        </div>

        <!-- Right Side - Login Form -->
        <div class="w-full max-w-md mx-auto animate-slide-left">
          <BaseCard variant="glass" shadow>
            <template #title>
              <span class="text-gradient-primary">Giriş Yap</span>
            </template>

            <!-- OAuth Buttons -->
            <div class="space-y-3 mb-6">
              <button
                @click="loginWithOAuth('steam')"
                class="btn btn-block bg-[#171a21] hover:bg-[#0a0b0e] text-white border-0"
                :disabled="loading"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
                </svg>
                Steam ile Giriş Yap
              </button>

              <button
                @click="loginWithOAuth('discord')"
                class="btn btn-block bg-[#5865F2] hover:bg-[#4752C4] text-white border-0"
                :disabled="loading"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
                Discord ile Giriş Yap
              </button>

              <button
                @click="loginWithOAuth('google')"
                class="btn btn-block bg-base-100 hover:bg-base-200 text-base-content border border-base-300"
                :disabled="loading"
              >
                <svg class="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google ile Giriş Yap
              </button>
            </div>

            <div class="divider">VEYA</div>

            <!-- Traditional Login Form -->
            <form @submit.prevent="handleLogin" class="space-y-4">
              <BaseInput
                v-model="form.username"
                label="Kullanıcı Adı"
                placeholder="kullaniciadi"
                :error="errors.username"
                required
              />

              <BaseInput
                v-model="form.password"
                type="password"
                label="Şifre"
                placeholder="••••••••"
                :error="errors.password"
                required
              />

              <div class="flex items-center justify-between">
                <label class="label cursor-pointer gap-2">
                  <input type="checkbox" v-model="form.remember" class="checkbox checkbox-sm" />
                  <span class="label-text">Beni Hatırla</span>
                </label>
                <router-link to="/forgot-password" class="link link-primary text-sm">
                  Şifremi Unuttum
                </router-link>
              </div>

              <BaseButton
                type="submit"
                variant="gaming"
                size="lg"
                block
                :loading="loading"
              >
                Giriş Yap
              </BaseButton>
            </form>

            <div class="text-center mt-6">
              <p class="text-sm">
                Hesabın yok mu?
                <router-link to="/register" class="link link-primary font-semibold">
                  Kayıt Ol
                </router-link>
              </p>
            </div>
          </BaseCard>
        </div>
      </div>
    </div>

    <!-- 2FA Modal -->
    <TwoFactorModal
      v-if="show2FAModal"
      :loading="verifying2FA"
      @verify="handle2FAVerify"
      @close="show2FAModal = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Logo from '@/components/common/Logo.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import TwoFactorModal from '@/components/auth/TwoFactorModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const show2FAModal = ref(false)
const verifying2FA = ref(false)
const pendingLoginData = ref(null)

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const errors = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  // Validate
  errors.username = form.username ? '' : 'Kullanıcı adı gerekli'
  errors.password = form.password ? '' : 'Şifre gerekli'

  if (errors.username || errors.password) return

  loading.value = true

  try {
    const response = await authStore.login({
      username: form.username,
      password: form.password,
      remember: form.remember
    })

    // Check if 2FA required
    if (response.requires_2fa) {
      pendingLoginData.value = response
      show2FAModal.value = true
    } else {
      router.push('/')
    }
  } catch (error) {
    errors.password = error.message || 'Giriş başarısız'
  } finally {
    loading.value = false
  }
}

const handle2FAVerify = async (code) => {
  verifying2FA.value = true

  try {
    await authStore.verify2FA({
      token: pendingLoginData.value.temp_token,
      code: code
    })

    show2FAModal.value = false
    router.push('/')
  } catch (error) {
    // Error handled in modal
  } finally {
    verifying2FA.value = false
  }
}

const loginWithOAuth = async (provider) => {
  loading.value = true

  try {
    // Redirect to OAuth endpoint
    window.location.href = `/api/auth/oauth/${provider}`
  } catch (error) {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes slideRight {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideLeft {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-right {
  animation: slideRight 0.6s ease-out;
}

.animate-slide-left {
  animation: slideLeft 0.6s ease-out;
}
</style>
