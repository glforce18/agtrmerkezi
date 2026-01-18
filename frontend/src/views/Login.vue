<template>
  <div class="min-h-[calc(100vh-200px)] flex items-center justify-center py-12">
    <div class="container-main">
      <div class="grid lg:grid-cols-2 gap-12 items-center">
        <!-- Left Side - Branding -->
        <div class="hidden lg:block space-y-6">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
              <span class="text-white font-bold text-2xl">A</span>
            </div>
            <div>
              <span class="font-bold text-2xl">AGTR</span>
              <span class="text-orange-500 font-bold text-2xl">Merkezi</span>
            </div>
          </div>

          <div class="space-y-3">
            <h1 class="text-4xl font-bold text-gradient-orange">
              Hos Geldiniz!
            </h1>
            <p class="text-lg opacity-70">
              Counter-Strike 1.6 sunucu yonetiminde yeni nesil platform
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4 mt-8">
            <n-card size="small">
              <n-statistic label="Aktif Sunucu" :value="1000" />
            </n-card>
            <n-card size="small">
              <n-statistic label="Kullanici" value="50K+" />
            </n-card>
            <n-card size="small">
              <n-statistic label="Destek" value="24/7" />
            </n-card>
            <n-card size="small">
              <n-statistic label="Uptime" value="99.9%" />
            </n-card>
          </div>
        </div>

        <!-- Right Side - Login Form -->
        <div class="w-full max-w-md mx-auto">
          <n-card title="Giris Yap">
            <!-- Steam Login -->
            <div class="mb-6">
              <n-button
                block
                size="large"
                :loading="loading"
                @click="loginWithOAuth('steam')"
                class="steam-btn"
              >
                <template #icon>
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0z"/>
                  </svg>
                </template>
                Steam ile Giris Yap
              </n-button>
              <p class="text-center text-sm opacity-60 mt-2">Onerilen giris yontemi</p>
            </div>

            <n-divider>veya e-posta ile</n-divider>

            <!-- Login Form -->
            <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
              <n-form-item label="Kullanici Adi" path="username">
                <n-input
                  v-model:value="form.username"
                  placeholder="kullaniciadi"
                  size="large"
                />
              </n-form-item>

              <n-form-item label="Sifre" path="password">
                <n-input
                  v-model:value="form.password"
                  type="password"
                  show-password-on="click"
                  placeholder="Sifreniz"
                  size="large"
                />
              </n-form-item>

              <div class="flex items-center justify-between mb-4">
                <n-checkbox v-model:checked="form.remember">Beni Hatirla</n-checkbox>
                <router-link to="/forgot-password" class="text-sm text-orange-500 hover:underline">
                  Sifremi Unuttum
                </router-link>
              </div>

              <n-button
                type="primary"
                block
                size="large"
                :loading="loading"
                @click="handleLogin"
              >
                Giris Yap
              </n-button>
            </n-form>

            <div class="text-center mt-6">
              <p class="text-sm opacity-70">
                Hesabin yok mu?
                <router-link to="/register" class="text-orange-500 font-semibold hover:underline">
                  Kayit Ol
                </router-link>
              </p>
            </div>
          </n-card>
        </div>
      </div>
    </div>

    <!-- 2FA Modal -->
    <n-modal v-model:show="show2FAModal" preset="dialog" title="Iki Faktorlu Dogrulama">
      <n-space vertical>
        <p>Authenticator uygulamanizdan 6 haneli kodu girin:</p>
        <n-input
          v-model:value="twoFactorCode"
          placeholder="000000"
          size="large"
          :maxlength="6"
        />
      </n-space>
      <template #action>
        <n-button @click="show2FAModal = false">Iptal</n-button>
        <n-button type="primary" :loading="verifying2FA" @click="handle2FAVerify">
          Dogrula
        </n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessage } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const formRef = ref(null)
const loading = ref(false)
const show2FAModal = ref(false)
const verifying2FA = ref(false)
const pendingLoginData = ref(null)
const twoFactorCode = ref('')

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: {
    required: true,
    message: 'Kullanici adi gerekli',
    trigger: 'blur'
  },
  password: {
    required: true,
    message: 'Sifre gerekli',
    trigger: 'blur'
  }
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true

  try {
    const response = await authStore.login({
      username: form.username,
      password: form.password,
      remember: form.remember
    })

    if (response.requires_2fa) {
      pendingLoginData.value = response
      show2FAModal.value = true
    } else {
      message.success('Giris basarili!')
      router.push('/dashboard')
    }
  } catch (error) {
    message.error(error.response?.data?.detail || error.message || 'Giris basarisiz')
  } finally {
    loading.value = false
  }
}

const handle2FAVerify = async () => {
  if (!twoFactorCode.value || twoFactorCode.value.length !== 6) {
    message.warning('6 haneli kodu girin')
    return
  }

  verifying2FA.value = true

  try {
    await authStore.verify2FA({
      user_id: pendingLoginData.value.user_id,
      code: twoFactorCode.value
    })

    show2FAModal.value = false
    message.success('Giris basarili!')
    router.push('/dashboard')
  } catch (error) {
    message.error(error.response?.data?.detail || 'Dogrulama basarisiz')
  } finally {
    verifying2FA.value = false
  }
}

const loginWithOAuth = async (provider) => {
  loading.value = true
  window.location.href = `/api/auth/oauth/${provider}`
}
</script>

<style scoped>
.steam-btn {
  background: linear-gradient(135deg, #1b2838 0%, #171a21 100%) !important;
  border: 2px solid #66c0f4 !important;
  color: #ffffff !important;
}

.steam-btn:hover {
  background: linear-gradient(135deg, #2a475e 0%, #1b2838 100%) !important;
  border-color: #66c0f4 !important;
}
</style>
