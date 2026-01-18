<template>
  <div class="min-h-[calc(100vh-200px)] flex items-center justify-center py-12">
    <div class="container-main">
      <div class="max-w-xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="flex items-center justify-center gap-3 mb-4">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
              <span class="text-white font-bold text-2xl">A</span>
            </div>
          </div>
          <h1 class="text-3xl font-bold mb-2">
            <span class="text-gradient-orange">Hesap Olustur</span>
          </h1>
          <p class="opacity-60">CS 1.6 sunucu yonetimine hemen basla!</p>
        </div>

        <n-card>
          <!-- Steam Register -->
          <div class="mb-6">
            <n-button
              block
              size="large"
              :loading="loading"
              @click="registerWithOAuth('steam')"
              class="steam-btn"
            >
              <template #icon>
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0z"/>
                </svg>
              </template>
              Steam ile Kayit Ol
            </n-button>
            <p class="text-center text-sm opacity-60 mt-2">Onerilen kayit yontemi</p>
          </div>

          <n-divider>veya e-posta ile</n-divider>

          <!-- Registration Form -->
          <n-form ref="formRef" :model="form" :rules="rules">
            <div class="grid md:grid-cols-2 gap-4">
              <n-form-item label="Kullanici Adi" path="username">
                <n-input v-model:value="form.username" placeholder="kullaniciadi" />
              </n-form-item>

              <n-form-item label="E-posta" path="email">
                <n-input v-model:value="form.email" placeholder="ornek@email.com" />
              </n-form-item>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <n-form-item label="Sifre" path="password">
                <n-input
                  v-model:value="form.password"
                  type="password"
                  show-password-on="click"
                  placeholder="Sifreniz"
                />
              </n-form-item>

              <n-form-item label="Sifre (Tekrar)" path="confirm_password">
                <n-input
                  v-model:value="form.confirm_password"
                  type="password"
                  show-password-on="click"
                  placeholder="Sifre tekrar"
                />
              </n-form-item>
            </div>

            <!-- Password Requirements -->
            <div class="mb-4 text-xs space-y-1">
              <p class="font-semibold opacity-70 mb-2">Sifre gereksinimleri:</p>
              <n-text :type="passwordChecks.length ? 'success' : 'default'">
                <n-icon :component="passwordChecks.length ? CheckCircle : XCircle" size="14" class="mr-1" />
                En az 8 karakter
              </n-text>
              <br />
              <n-text :type="passwordChecks.uppercase ? 'success' : 'default'">
                <n-icon :component="passwordChecks.uppercase ? CheckCircle : XCircle" size="14" class="mr-1" />
                En az 1 buyuk harf
              </n-text>
              <br />
              <n-text :type="passwordChecks.number ? 'success' : 'default'">
                <n-icon :component="passwordChecks.number ? CheckCircle : XCircle" size="14" class="mr-1" />
                En az 1 rakam
              </n-text>
            </div>

            <!-- Terms -->
            <n-form-item :show-label="false">
              <n-checkbox v-model:checked="form.accept_terms">
                <span class="text-sm">
                  <router-link to="/terms" class="text-orange-500 hover:underline">Kullanim Kosullari</router-link> ve
                  <router-link to="/privacy" class="text-orange-500 hover:underline">Gizlilik Politikasi</router-link>'ni
                  okudum ve kabul ediyorum
                </span>
              </n-checkbox>
            </n-form-item>

            <n-form-item :show-label="false">
              <n-checkbox v-model:checked="form.newsletter">
                <span class="text-sm opacity-70">Yeni ozellikler ve promosyonlar hakkinda e-posta almak istiyorum</span>
              </n-checkbox>
            </n-form-item>

            <n-button
              type="primary"
              block
              size="large"
              :loading="loading"
              :disabled="!form.accept_terms"
              @click="handleRegister"
            >
              Hesap Olustur
            </n-button>
          </n-form>

          <div class="text-center mt-6">
            <p class="text-sm opacity-70">
              Zaten hesabin var mi?
              <router-link to="/login" class="text-orange-500 font-semibold hover:underline">
                Giris Yap
              </router-link>
            </p>
          </div>
        </n-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessage } from 'naive-ui'
import { CheckCircle, XCircle } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  accept_terms: false,
  newsletter: false
})

const passwordChecks = computed(() => ({
  length: form.password.length >= 8,
  uppercase: /[A-Z]/.test(form.password),
  number: /[0-9]/.test(form.password)
}))

const rules = {
  username: [
    { required: true, message: 'Kullanici adi gerekli', trigger: 'blur' },
    { min: 3, message: 'Kullanici adi en az 3 karakter olmali', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'E-posta gerekli', trigger: 'blur' },
    { type: 'email', message: 'Gecerli bir e-posta adresi girin', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Sifre gerekli', trigger: 'blur' },
    {
      validator: (rule, value) => {
        return passwordChecks.value.length && passwordChecks.value.uppercase && passwordChecks.value.number
      },
      message: 'Sifre gereksinimleri karsilanmiyor',
      trigger: 'blur'
    }
  ],
  confirm_password: [
    { required: true, message: 'Sifre tekrari gerekli', trigger: 'blur' },
    {
      validator: (rule, value) => value === form.password,
      message: 'Sifreler eslesmiyor',
      trigger: 'blur'
    }
  ]
}

const handleRegister = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  if (!form.accept_terms) {
    message.warning('Kullanim kosullarini kabul etmelisiniz')
    return
  }

  loading.value = true

  try {
    await authStore.register({
      username: form.username,
      email: form.email,
      password: form.password,
      newsletter: form.newsletter
    })

    message.success('Kayit basarili!')
    router.push('/dashboard')
  } catch (error) {
    message.error(error.response?.data?.detail || error.message || 'Kayit basarisiz')
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
.steam-btn {
  background: linear-gradient(135deg, #1b2838 0%, #171a21 100%) !important;
  border: 2px solid #66c0f4 !important;
  color: #ffffff !important;
}

.steam-btn:hover {
  background: linear-gradient(135deg, #2a475e 0%, #1b2838 100%) !important;
}
</style>
