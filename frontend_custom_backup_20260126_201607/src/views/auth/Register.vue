<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="text-7xl neon-orange mb-4">λ</div>
        <h1 class="text-4xl font-lambda font-bold neon-orange mb-2">KAYIT OL</h1>
        <p class="text-text-secondary font-hev">AGTR Merkezi'ne katıl</p>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mb-6 p-4 bg-combine-red bg-opacity-10 border border-combine-red rounded">
        <p class="text-combine-red font-hev text-sm">{{ error }}</p>
      </div>

      <!-- Success Message -->
      <div v-if="success" class="mb-6 p-4 bg-combine-green bg-opacity-10 border border-combine-green rounded">
        <p class="text-combine-green font-hev text-sm">{{ success }}</p>
      </div>

      <!-- Register Form -->
      <form v-if="!success" @submit.prevent="handleRegister" class="bg-cyber-panel border border-cyber-border rounded-lg p-8">
        <!-- Username -->
        <div class="mb-4">
          <label class="block text-sm font-lambda text-text-primary mb-2">
            Kullanıcı Adı
          </label>
          <input
            v-model="form.username"
            type="text"
            placeholder="kullaniciadi"
            class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
            required
            minlength="3"
            maxlength="20"
          />
          <p class="text-xs text-text-secondary font-hev mt-1">3-20 karakter, harf ve rakam</p>
        </div>

        <!-- Email -->
        <div class="mb-4">
          <label class="block text-sm font-lambda text-text-primary mb-2">
            E-posta
          </label>
          <input
            v-model="form.email"
            type="email"
            placeholder="email@example.com"
            class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
            required
          />
        </div>

        <!-- Password -->
        <div class="mb-4">
          <label class="block text-sm font-lambda text-text-primary mb-2">
            Şifre
          </label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
            required
            minlength="6"
          />
          <p class="text-xs text-text-secondary font-hev mt-1">En az 6 karakter</p>
        </div>

        <!-- Password Confirm -->
        <div class="mb-6">
          <label class="block text-sm font-lambda text-text-primary mb-2">
            Şifre (Tekrar)
          </label>
          <input
            v-model="form.password_confirm"
            type="password"
            placeholder="••••••••"
            class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
            required
          />
        </div>

        <!-- Terms Checkbox -->
        <div class="mb-6">
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="form.accept_terms"
              type="checkbox"
              class="mt-1 w-5 h-5 text-lambda-orange rounded"
              required
            />
            <span class="text-sm text-text-secondary font-hev">
              <a href="#" class="text-lambda-orange hover:underline">Kullanım Koşulları</a>'nı ve
              <a href="#" class="text-lambda-orange hover:underline">Gizlilik Politikası</a>'nı okudum ve kabul ediyorum
            </span>
          </label>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all disabled:opacity-30 disabled:cursor-not-allowed mb-4"
        >
          <span v-if="!loading">KAYIT OL</span>
          <span v-else>KAYIT OLUŞTURULUYOR...</span>
        </button>

        <!-- OAuth Options -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-cyber-border"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-4 bg-cyber-panel text-text-secondary font-hev">veya</span>
          </div>
        </div>

        <div class="space-y-3">
          <a
            :href="`/api/auth/oauth/steam`"
            class="flex items-center justify-center gap-3 w-full px-6 py-3 bg-cyber-darker border border-cyber-border text-text-primary font-lambda rounded hover:border-lambda-orange transition-all"
          >
            <Gamepad2 :size="20" />
            Steam ile Kayıt Ol
          </a>

          <a
            :href="`/api/auth/oauth/discord`"
            class="flex items-center justify-center gap-3 w-full px-6 py-3 bg-cyber-darker border border-cyber-border text-text-primary font-lambda rounded hover:border-hev-cyan transition-all"
          >
            <MessageSquare :size="20" />
            Discord ile Kayıt Ol
          </a>
        </div>

        <!-- Login Link -->
        <div class="mt-6 text-center">
          <span class="text-text-secondary font-hev text-sm">Zaten hesabın var mı? </span>
          <router-link to="/login" class="text-lambda-orange hover:underline font-lambda text-sm">
            Giriş Yap
          </router-link>
        </div>
      </form>

      <!-- Success State -->
      <div v-else class="text-center">
        <div class="mb-6 p-8 bg-combine-green bg-opacity-10 border border-combine-green rounded-lg">
          <div class="text-6xl text-combine-green mb-4">✓</div>
          <h2 class="text-2xl font-lambda font-bold text-combine-green mb-2">Kayıt Başarılı!</h2>
          <p class="text-text-secondary font-hev mb-4">
            E-posta adresinize bir doğrulama bağlantısı gönderdik.
          </p>
          <router-link
            to="/login"
            class="inline-block px-8 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all"
          >
            GİRİŞ YAP
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import authAPI from '@/api/auth'
import { Gamepad2, MessageSquare } from 'lucide-vue-next'

const router = useRouter()

const loading = ref(false)
const error = ref(null)
const success = ref(false)

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  accept_terms: false
})

async function handleRegister() {
  error.value = null

  // Validation
  if (form.value.password !== form.value.password_confirm) {
    error.value = 'Şifreler eşleşmiyor'
    return
  }

  if (!form.value.accept_terms) {
    error.value = 'Kullanım koşullarını kabul etmelisiniz'
    return
  }

  loading.value = true

  try {
    await authAPI.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })

    success.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || 'Kayıt oluşturulamadı. Lütfen tekrar deneyin.'
    console.error('Register error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.bg-lambda-gradient {
  background: linear-gradient(135deg, #FF6B35 0%, #E85D2C 100%);
}

.neon-orange {
  color: #FF6B35;
  text-shadow: 0 0 10px rgba(255, 107, 53, 0.8);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}
</style>
