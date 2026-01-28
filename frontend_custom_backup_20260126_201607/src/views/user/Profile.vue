<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-5xl font-lambda font-bold mb-2">
          <span class="text-combine-green" style="text-shadow: 0 0 20px rgba(57, 255, 20, 0.6)">PROFİLİM</span>
        </h1>
        <p class="text-text-secondary font-hev">Hesap bilgilerinizi yönetin</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Sidebar -->
        <div class="lg:col-span-1">
          <!-- Profile Card -->
          <div class="bg-cyber-panel border border-cyber-border rounded-lg p-6 mb-6">
            <!-- Avatar -->
            <div class="text-center mb-4">
              <div class="w-32 h-32 mx-auto mb-4 rounded-full bg-lambda-orange bg-opacity-20 border-2 border-lambda-orange flex items-center justify-center text-5xl font-lambda text-lambda-orange">
                {{ user.username?.[0]?.toUpperCase() || 'U' }}
              </div>
              <button class="px-4 py-2 bg-cyber-darker border border-cyber-border text-text-secondary hover:border-lambda-orange hover:text-lambda-orange font-lambda text-sm rounded transition-all">
                <Upload :size="14" class="inline mr-1" />
                Avatar Değiştir
              </button>
            </div>

            <!-- User Info -->
            <div class="text-center border-t border-cyber-border pt-4">
              <h3 class="text-xl font-lambda font-bold text-text-primary mb-1">
                {{ user.username || 'Kullanıcı' }}
              </h3>
              <p class="text-sm text-text-secondary font-hev mb-2">
                {{ user.email }}
              </p>

              <div class="inline-block px-3 py-1 bg-lambda-orange bg-opacity-20 border border-lambda-orange text-lambda-orange rounded-full font-lambda text-xs">
                {{ getRoleName(user.role) }}
              </div>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-2 gap-4 mt-6 pt-4 border-t border-cyber-border">
              <div class="text-center">
                <div class="text-2xl font-lambda text-hev-cyan">{{ user.server_count || 0 }}</div>
                <div class="text-xs text-text-secondary font-hev">Sunucu</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-lambda text-xen-purple">{{ user.post_count || 0 }}</div>
                <div class="text-xs text-text-secondary font-hev">Mesaj</div>
              </div>
            </div>
          </div>

          <!-- Wallet Card -->
          <div class="bg-cyber-panel border border-combine-green rounded-lg p-6">
            <div class="flex items-center gap-2 mb-4">
              <Wallet :size="20" class="text-combine-green" />
              <h3 class="text-lg font-lambda font-bold text-text-primary">Cüzdan</h3>
            </div>

            <div class="text-center mb-4">
              <div class="text-4xl font-lambda text-combine-green mb-1">
                ₺{{ formatMoney(user.wallet_balance || 0) }}
              </div>
              <div class="text-xs text-text-secondary font-hev">Bakiye</div>
            </div>

            <button class="w-full px-4 py-3 bg-combine-green bg-opacity-10 border border-combine-green text-combine-green font-lambda rounded hover:bg-combine-green hover:text-cyber-black transition-all">
              <Plus :size="16" class="inline mr-2" />
              BAKİYE YÜKLE
            </button>
          </div>
        </div>

        <!-- Main Content -->
        <div class="lg:col-span-2">
          <!-- Tabs -->
          <div class="mb-6">
            <div class="flex gap-2 border-b border-cyber-border">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                class="px-6 py-3 font-lambda font-bold transition-all"
                :class="activeTab === tab.id
                  ? 'text-lambda-orange border-b-2 border-lambda-orange'
                  : 'text-text-secondary hover:text-text-primary'"
              >
                <component :is="tab.icon" :size="18" class="inline mr-2" />
                {{ tab.label }}
              </button>
            </div>
          </div>

          <!-- Account Settings Tab -->
          <div v-show="activeTab === 'account'" class="bg-cyber-panel border border-cyber-border rounded-lg p-6">
            <h3 class="text-xl font-lambda font-bold text-text-primary mb-6">HESAP BİLGİLERİ</h3>

            <form @submit.prevent="updateProfile" class="space-y-6">
              <!-- Username -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  Kullanıcı Adı
                </label>
                <input
                  v-model="profileForm.username"
                  type="text"
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                  required
                />
              </div>

              <!-- Email -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  E-posta
                </label>
                <input
                  v-model="profileForm.email"
                  type="email"
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                  required
                />
                <p v-if="!user.email_verified" class="text-xs text-combine-yellow font-hev mt-1">
                  E-posta adresiniz doğrulanmamış. <a href="#" class="underline">Doğrulama e-postası gönder</a>
                </p>
              </div>

              <!-- Phone -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  Telefon
                </label>
                <input
                  v-model="profileForm.phone"
                  type="tel"
                  placeholder="+90 5XX XXX XX XX"
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                />
              </div>

              <!-- Bio -->
              <div>
                <label class="block text-sm font-lambda text-text-primary mb-2">
                  Hakkında
                </label>
                <textarea
                  v-model="profileForm.bio"
                  rows="4"
                  placeholder="Kendiniz hakkında birkaç kelime..."
                  class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all resize-none"
                ></textarea>
              </div>

              <button
                type="submit"
                :disabled="saving"
                class="px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all disabled:opacity-30"
              >
                <Save :size="16" class="inline mr-2" />
                KAYDET
              </button>
            </form>
          </div>

          <!-- Security Tab -->
          <div v-show="activeTab === 'security'" class="bg-cyber-panel border border-cyber-border rounded-lg p-6">
            <h3 class="text-xl font-lambda font-bold text-text-primary mb-6">GÜVENLİK</h3>

            <!-- Change Password -->
            <div class="mb-8">
              <h4 class="text-lg font-lambda text-text-primary mb-4">Şifre Değiştir</h4>

              <form @submit.prevent="changePassword" class="space-y-4">
                <div>
                  <label class="block text-sm font-lambda text-text-primary mb-2">
                    Mevcut Şifre
                  </label>
                  <input
                    v-model="passwordForm.current_password"
                    type="password"
                    class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-lambda text-text-primary mb-2">
                    Yeni Şifre
                  </label>
                  <input
                    v-model="passwordForm.new_password"
                    type="password"
                    class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-lambda text-text-primary mb-2">
                    Yeni Şifre (Tekrar)
                  </label>
                  <input
                    v-model="passwordForm.new_password_confirm"
                    type="password"
                    class="w-full px-4 py-3 bg-cyber-darker border border-cyber-border rounded text-text-primary font-hev outline-none focus:border-hev-cyan transition-all"
                    required
                  />
                </div>

                <button
                  type="submit"
                  :disabled="saving"
                  class="px-6 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all disabled:opacity-30"
                >
                  <Key :size="16" class="inline mr-2" />
                  ŞİFREYİ GÜNCELLE
                </button>
              </form>
            </div>

            <!-- Two-Factor Authentication -->
            <div class="border-t border-cyber-border pt-6">
              <h4 class="text-lg font-lambda text-text-primary mb-4">İki Faktörlü Doğrulama (2FA)</h4>

              <div v-if="!user.two_factor_enabled" class="flex items-start gap-4 p-4 bg-cyber-darker border border-combine-yellow rounded">
                <ShieldAlert :size="24" class="text-combine-yellow flex-shrink-0 mt-1" />
                <div class="flex-1">
                  <p class="text-text-primary font-hev mb-2">
                    Hesabınızı ek bir güvenlik katmanıyla koruyun
                  </p>
                  <button class="px-4 py-2 bg-combine-green bg-opacity-10 border border-combine-green text-combine-green font-lambda text-sm rounded hover:bg-combine-green hover:text-cyber-black transition-all">
                    2FA AKTİFLEŞTİR
                  </button>
                </div>
              </div>

              <div v-else class="flex items-start gap-4 p-4 bg-cyber-darker border border-combine-green rounded">
                <ShieldCheck :size="24" class="text-combine-green flex-shrink-0 mt-1" />
                <div class="flex-1">
                  <p class="text-text-primary font-hev mb-2">
                    İki faktörlü doğrulama aktif
                  </p>
                  <button class="px-4 py-2 bg-combine-red bg-opacity-10 border border-combine-red text-combine-red font-lambda text-sm rounded hover:bg-combine-red hover:text-cyber-black transition-all">
                    2FA DEVRE DIŞI BIRAK
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Integrations Tab -->
          <div v-show="activeTab === 'integrations'" class="bg-cyber-panel border border-cyber-border rounded-lg p-6">
            <h3 class="text-xl font-lambda font-bold text-text-primary mb-6">ENTEGRASYONLAR</h3>

            <div class="space-y-4">
              <!-- Steam -->
              <div class="flex items-center justify-between p-4 bg-cyber-darker border border-cyber-border rounded">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 bg-lambda-orange bg-opacity-20 border border-lambda-orange rounded flex items-center justify-center">
                    <Gamepad2 :size="24" class="text-lambda-orange" />
                  </div>
                  <div>
                    <div class="font-lambda text-text-primary">Steam</div>
                    <div v-if="user.steam_id" class="text-sm text-text-secondary font-hev">
                      Bağlı: {{ user.steam_id }}
                    </div>
                    <div v-else class="text-sm text-text-secondary font-hev">
                      Bağlı değil
                    </div>
                  </div>
                </div>

                <button
                  v-if="!user.steam_id"
                  class="px-4 py-2 bg-lambda-orange bg-opacity-10 border border-lambda-orange text-lambda-orange font-lambda text-sm rounded hover:bg-lambda-orange hover:text-cyber-black transition-all"
                >
                  BAĞLA
                </button>
                <button
                  v-else
                  class="px-4 py-2 bg-combine-red bg-opacity-10 border border-combine-red text-combine-red font-lambda text-sm rounded hover:bg-combine-red hover:text-cyber-black transition-all"
                >
                  BAĞLANTIYI KES
                </button>
              </div>

              <!-- Discord -->
              <div class="flex items-center justify-between p-4 bg-cyber-darker border border-cyber-border rounded">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 bg-hev-cyan bg-opacity-20 border border-hev-cyan rounded flex items-center justify-center">
                    <MessageSquare :size="24" class="text-hev-cyan" />
                  </div>
                  <div>
                    <div class="font-lambda text-text-primary">Discord</div>
                    <div class="text-sm text-text-secondary font-hev">
                      Bağlı değil
                    </div>
                  </div>
                </div>

                <button class="px-4 py-2 bg-hev-cyan bg-opacity-10 border border-hev-cyan text-hev-cyan font-lambda text-sm rounded hover:bg-hev-cyan hover:text-cyber-black transition-all">
                  BAĞLA
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  Upload,
  Wallet,
  Plus,
  User,
  Shield,
  Link2,
  Save,
  Key,
  ShieldAlert,
  ShieldCheck,
  Gamepad2,
  MessageSquare
} from 'lucide-vue-next'

const authStore = useAuthStore()

const activeTab = ref('account')
const saving = ref(false)

const tabs = [
  { id: 'account', label: 'HESAP', icon: User },
  { id: 'security', label: 'GÜVENLİK', icon: Shield },
  { id: 'integrations', label: 'ENTEGRASYONLAR', icon: Link2 }
]

const user = computed(() => authStore.user || {})

const profileForm = ref({
  username: user.value.username || '',
  email: user.value.email || '',
  phone: user.value.phone || '',
  bio: user.value.bio || ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  new_password_confirm: ''
})

// Methods
function getRoleName(role) {
  const roleNames = {
    admin: 'Admin',
    moderator: 'Moderatör',
    user: 'Kullanıcı',
    vip: 'VIP'
  }
  return roleNames[role] || 'Kullanıcı'
}

function formatMoney(value) {
  return new Intl.NumberFormat('tr-TR').format(value)
}

async function updateProfile() {
  saving.value = true
  try {
    // API call to update profile
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('Profil güncellendi')
  } catch (err) {
    alert('Profil güncellenemedi')
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.new_password_confirm) {
    alert('Yeni şifreler eşleşmiyor')
    return
  }

  saving.value = true
  try {
    // API call to change password
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('Şifre güncellendi')
    passwordForm.value = {
      current_password: '',
      new_password: '',
      new_password_confirm: ''
    }
  } catch (err) {
    alert('Şifre güncellenemedi')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.bg-lambda-gradient {
  background: linear-gradient(135deg, #FF6B35 0%, #E85D2C 100%);
}

.shadow-neon-orange {
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}
</style>
