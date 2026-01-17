<template>
  <div class="min-h-screen flex items-center justify-center">
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

            <!-- Steam Login - Primary -->
            <div class="mb-6">
              <button
                @click="loginWithOAuth('steam')"
                class="steam-btn w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3 transition-all"
                :disabled="loading"
              >
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
                </svg>
                Steam ile Giriş Yap
              </button>
              <p class="text-center text-sm opacity-60 mt-2">Önerilen giriş yöntemi</p>
            </div>

            <div class="divider">veya e-posta ile</div>

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
      router.push('/dashboard')
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
    router.push('/dashboard')
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

.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

.text-gradient-primary {
  @apply bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent;
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
