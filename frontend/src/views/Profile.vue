<template>
  <div class="min-h-screen">
    <div class="container-custom py-8">
      <!-- Profile Header -->
      <n-card class="glass-card mb-8">
        <div class="flex flex-col md:flex-row items-center gap-6">
          <!-- Avatar -->
          <div class="relative">
            <n-avatar
              round
              :size="128"
              :src="user?.avatar || '/default-avatar.png'"
              class="ring-4 ring-orange-500 ring-offset-2 ring-offset-gray-900"
            />
            <n-button circle size="small" type="primary" class="absolute bottom-0 right-0">
              <template #icon><CameraIcon class="w-4 h-4" /></template>
            </n-button>
          </div>

          <!-- User Info -->
          <div class="flex-1 text-center md:text-left">
            <h1 class="text-3xl font-bold mb-2">
              {{ user?.username }}
              <n-tag v-if="user?.verified" type="primary" size="small" class="ml-2">
                <template #icon><CheckCircleIcon class="w-3 h-3" /></template>
                Doğrulanmış
              </n-tag>
            </h1>
            <p class="text-gray-400 mb-4">{{ user?.email }}</p>
            <div class="flex flex-wrap gap-2 justify-center md:justify-start">
              <n-tag :bordered="false">
                <template #icon><CalendarIcon class="w-3 h-3" /></template>
                {{ formatDate(user?.created_at) }} tarihinde katıldı
              </n-tag>
              <n-tag :bordered="false">
                <template #icon><ServerIcon class="w-3 h-3" /></template>
                {{ user?.servers_count || 0 }} Sunucu
              </n-tag>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="flex gap-2">
            <n-button type="primary" size="small" @click="activeTab = 'settings'">
              <template #icon><SettingsIcon class="w-4 h-4" /></template>
              Ayarlar
            </n-button>
          </div>
        </div>
      </n-card>

      <!-- Tabs -->
      <n-tabs v-model:value="activeTab" type="segment" animated class="mb-6">
        <n-tab-pane name="profile" tab="Profil">
          <template #tab>
            <div class="flex items-center gap-2">
              <UserIcon class="w-4 h-4" />
              <span>Profil</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="security" tab="Güvenlik">
          <template #tab>
            <div class="flex items-center gap-2">
              <ShieldCheckIcon class="w-4 h-4" />
              <span>Güvenlik</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="settings" tab="Ayarlar">
          <template #tab>
            <div class="flex items-center gap-2">
              <SettingsIcon class="w-4 h-4" />
              <span>Ayarlar</span>
            </div>
          </template>
        </n-tab-pane>
        <n-tab-pane name="activity" tab="Aktivite">
          <template #tab>
            <div class="flex items-center gap-2">
              <ActivityIcon class="w-4 h-4" />
              <span>Aktivite</span>
            </div>
          </template>
        </n-tab-pane>
      </n-tabs>

      <!-- Tab Content -->
      <div v-if="activeTab === 'profile'">
        <n-card class="glass-card" title="Profil Bilgileri">
          <n-form @submit.prevent="updateProfile" class="space-y-6">
            <div class="grid md:grid-cols-2 gap-4">
              <n-form-item label="Kullanıcı Adı">
                <n-input v-model:value="profileForm.username" placeholder="kullaniciadi" />
              </n-form-item>

              <n-form-item label="E-posta">
                <n-input v-model:value="profileForm.email" type="email" placeholder="ornek@email.com" />
              </n-form-item>

              <n-form-item label="Ad">
                <n-input v-model:value="profileForm.first_name" placeholder="Adınız" />
              </n-form-item>

              <n-form-item label="Soyad">
                <n-input v-model:value="profileForm.last_name" placeholder="Soyadınız" />
              </n-form-item>

              <n-form-item label="Telefon">
                <n-input v-model:value="profileForm.phone" placeholder="+90 555 123 4567" />
              </n-form-item>

              <n-form-item label="Ülke">
                <n-input v-model:value="profileForm.country" placeholder="Türkiye" />
              </n-form-item>
            </div>

            <n-form-item label="Biyografi">
              <n-input
                v-model:value="profileForm.bio"
                type="textarea"
                placeholder="Kendinizden bahsedin..."
                :rows="4"
              />
            </n-form-item>

            <div class="flex justify-end gap-2">
              <n-button quaternary>İptal</n-button>
              <n-button type="primary" attr-type="submit" :loading="saving">
                Kaydet
              </n-button>
            </div>
          </n-form>
        </n-card>
      </div>

      <div v-else-if="activeTab === 'security'">
        <div class="space-y-6">
          <!-- Change Password - Only show for non-OAuth users -->
          <n-card v-if="!isOAuthUser" class="glass-card" title="Şifre Değiştir">
            <n-form @submit.prevent="changePassword" class="space-y-4">
              <n-form-item label="Mevcut Şifre">
                <n-input
                  v-model:value="passwordForm.current_password"
                  type="password"
                  show-password-on="click"
                  placeholder="••••••••"
                />
              </n-form-item>

              <n-form-item label="Yeni Şifre">
                <n-input
                  v-model:value="passwordForm.new_password"
                  type="password"
                  show-password-on="click"
                  placeholder="••••••••"
                />
              </n-form-item>

              <n-form-item label="Yeni Şifre (Tekrar)">
                <n-input
                  v-model:value="passwordForm.confirm_password"
                  type="password"
                  show-password-on="click"
                  placeholder="••••••••"
                />
              </n-form-item>

              <div class="flex justify-end gap-2">
                <n-button type="primary" attr-type="submit" :loading="savingPassword">
                  Şifreyi Güncelle
                </n-button>
              </div>
            </n-form>
          </n-card>

          <!-- OAuth User Notice -->
          <n-card v-else class="glass-card" title="Şifre Yönetimi">
            <n-alert type="info" title="Bilgi">
              <template #icon><InfoIcon class="w-5 h-5" /></template>
              Steam veya Discord ile giriş yaptığınız için şifre belirlemeniz gerekmemektedir.
              Hesabınız OAuth sağlayıcısı üzerinden güvence altındadır.
            </n-alert>
          </n-card>

          <!-- Two-Factor Authentication -->
          <n-card class="glass-card">
            <template #header>
              <div class="flex items-center justify-between">
                <span>İki Faktörlü Doğrulama (2FA)</span>
                <n-tag v-if="user?.two_factor_enabled" type="success" size="small">Aktif</n-tag>
                <n-tag v-else type="warning" size="small">Pasif</n-tag>
              </div>
            </template>

            <div class="space-y-4">
              <p class="text-sm text-gray-400">
                İki faktörlü doğrulama, hesabınıza ek bir güvenlik katmanı ekler.
                Giriş yaparken şifrenizin yanında authenticator uygulamanızdan bir kod girmeniz gerekir.
              </p>

              <div v-if="!user?.two_factor_enabled">
                <n-button type="primary" @click="enable2FA">
                  <template #icon><ShieldCheckIcon class="w-4 h-4" /></template>
                  2FA'yı Etkinleştir
                </n-button>
              </div>

              <div v-else class="space-y-4">
                <n-alert type="success" title="2FA Aktif">
                  2FA başarıyla etkinleştirildi!
                </n-alert>

                <div class="flex gap-2">
                  <n-button size="small" secondary @click="show2FABackupCodes = true">
                    <template #icon><KeyIcon class="w-4 h-4" /></template>
                    Yedek Kodları Gör
                  </n-button>
                  <n-button size="small" type="error" @click="disable2FA">
                    <template #icon><XCircleIcon class="w-4 h-4" /></template>
                    2FA'yı Devre Dışı Bırak
                  </n-button>
                </div>
              </div>
            </div>
          </n-card>

          <!-- Active Sessions -->
          <n-card class="glass-card" title="Aktif Oturumlar">
            <div class="space-y-3">
              <div v-for="session in sessions" :key="session.id"
                   class="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div class="flex items-center gap-4">
                  <div class="p-3 bg-white/10 rounded-lg">
                    <MonitorIcon v-if="session.device_type === 'desktop'" class="w-5 h-5" />
                    <SmartphoneIcon v-else class="w-5 h-5" />
                  </div>
                  <div>
                    <h4 class="font-medium">{{ session.device_name }}</h4>
                    <p class="text-sm text-gray-400">{{ session.ip }} • {{ session.location }}</p>
                    <p class="text-xs text-gray-500">
                      Son aktivite: {{ formatTime(session.last_activity) }}
                    </p>
                  </div>
                </div>

                <div>
                  <n-tag v-if="session.is_current" type="success" size="small">Mevcut</n-tag>
                  <n-button v-else quaternary size="small" @click="revokeSession(session.id)">
                    Sonlandır
                  </n-button>
                </div>
              </div>
            </div>

            <div class="mt-4 flex justify-end">
              <n-button type="error" size="small" @click="revokeAllSessions">
                Tüm Oturumları Sonlandır
              </n-button>
            </div>
          </n-card>
        </div>
      </div>

      <div v-else-if="activeTab === 'settings'">
        <n-card class="glass-card" title="Tercihler">
          <div class="space-y-6">
            <!-- Notifications -->
            <div>
              <h3 class="font-semibold mb-4">Bildirimler</h3>

              <!-- Email warning for users without email -->
              <n-alert v-if="!hasEmail" type="warning" title="Uyarı" class="mb-4">
                E-posta bildirimleri için önce profil sayfanızdan e-posta adresinizi eklemeniz gerekmektedir.
              </n-alert>

              <div class="space-y-4">
                <div class="flex items-center justify-between" :class="{ 'opacity-50': !hasEmail }">
                  <span class="text-sm">E-posta bildirimleri</span>
                  <n-switch v-model:value="settings.email_notifications" :disabled="!hasEmail" />
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm">Sunucu uyarıları</span>
                  <n-switch v-model:value="settings.server_alerts" />
                </div>
                <div class="flex items-center justify-between" :class="{ 'opacity-50': !hasEmail }">
                  <span class="text-sm">Güvenlik bildirimleri (E-posta)</span>
                  <n-switch v-model:value="settings.security_alerts" :disabled="!hasEmail" />
                </div>
              </div>
            </div>

            <n-divider />

            <!-- Privacy -->
            <div>
              <h3 class="font-semibold mb-4">Gizlilik</h3>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm">Profili herkese açık yap</span>
                  <n-switch v-model:value="settings.public_profile" />
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm">Online durumunu göster</span>
                  <n-switch v-model:value="settings.show_online_status" />
                </div>
              </div>
            </div>

            <div class="flex justify-end gap-2">
              <n-button type="primary" @click="saveSettings" :loading="savingSettings">
                Ayarları Kaydet
              </n-button>
            </div>
          </div>
        </n-card>
      </div>

      <div v-else-if="activeTab === 'activity'">
        <n-card class="glass-card" title="Son Aktiviteler">
          <div class="space-y-3">
            <div v-for="activity in activities" :key="activity.id"
                 class="flex gap-4 p-4 bg-white/5 rounded-lg">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full flex items-center justify-center"
                     :class="getActivityIconClass(activity.type)">
                  <component :is="getActivityIcon(activity.type)" class="w-5 h-5" />
                </div>
              </div>
              <div class="flex-1">
                <p class="font-medium">{{ activity.title }}</p>
                <p class="text-sm text-gray-400">{{ activity.description }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ formatTime(activity.created_at) }}</p>
              </div>
            </div>
          </div>
        </n-card>
      </div>
    </div>

    <!-- 2FA Backup Codes Modal -->
    <n-modal v-model:show="show2FABackupCodes" preset="dialog" title="Yedek Kodlar">
      <p class="text-sm text-gray-400 mb-4">
        Bu kodları güvenli bir yerde saklayın. Authenticator uygulamanıza erişiminizi kaybederseniz
        bu kodları kullanarak giriş yapabilirsiniz.
      </p>
      <div class="grid grid-cols-2 gap-2 mb-6">
        <div v-for="code in backupCodes" :key="code"
             class="p-3 bg-white/10 rounded font-mono text-center">
          {{ code }}
        </div>
      </div>
      <template #action>
        <n-button quaternary @click="show2FABackupCodes = false">Kapat</n-button>
        <n-button type="primary" @click="downloadBackupCodes">İndir</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  UserIcon,
  ShieldCheckIcon,
  SettingsIcon,
  ActivityIcon,
  CameraIcon,
  CheckCircleIcon,
  CalendarIcon,
  ServerIcon,
  KeyIcon,
  XCircleIcon,
  MonitorIcon,
  SmartphoneIcon,
  InfoIcon,
  AlertCircleIcon
} from 'lucide-vue-next'
import { formatDistanceToNow, format } from 'date-fns'
import { tr } from 'date-fns/locale'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// Check if user logged in via OAuth (Steam, Discord, etc.) - they don't have a password
const isOAuthUser = computed(() => {
  const provider = user.value?.auth_provider || user.value?.oauth_provider
  return provider && provider !== 'local' && provider !== 'email'
})

// Check if user has email set for email-related features
const hasEmail = computed(() => !!user.value?.email)

const activeTab = ref('profile')
const saving = ref(false)
const savingPassword = ref(false)
const savingSettings = ref(false)
const show2FABackupCodes = ref(false)

const profileForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  country: '',
  bio: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const settings = reactive({
  email_notifications: true,
  server_alerts: true,
  security_alerts: true,
  public_profile: false,
  show_online_status: true
})

const sessions = ref([
  {
    id: 1,
    device_name: 'Chrome on Windows',
    device_type: 'desktop',
    ip: '192.168.1.100',
    location: 'İstanbul, Türkiye',
    last_activity: new Date(),
    is_current: true
  }
])

const activities = ref([
  {
    id: 1,
    type: 'success',
    title: 'Şifre değiştirildi',
    description: 'Hesap şifreniz başarıyla güncellendi',
    created_at: new Date(Date.now() - 1000 * 60 * 30)
  },
  {
    id: 2,
    type: 'info',
    title: 'Yeni oturum açıldı',
    description: 'Chrome on Windows - İstanbul, Türkiye',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2)
  }
])

const backupCodes = ref([
  'XXXX-XXXX-XXXX',
  'YYYY-YYYY-YYYY',
  'ZZZZ-ZZZZ-ZZZZ',
  'AAAA-AAAA-AAAA'
])

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return formatDistanceToNow(new Date(timestamp), {
    addSuffix: true,
    locale: tr
  })
}

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  return format(new Date(timestamp), 'dd MMMM yyyy', { locale: tr })
}

const getActivityIcon = (type) => {
  const icons = {
    info: InfoIcon,
    success: CheckCircleIcon,
    warning: AlertCircleIcon,
    error: AlertCircleIcon
  }
  return icons[type] || InfoIcon
}

const getActivityIconClass = (type) => {
  const classes = {
    info: 'bg-blue-500/20 text-blue-500',
    success: 'bg-green-500/20 text-green-500',
    warning: 'bg-yellow-500/20 text-yellow-500',
    error: 'bg-red-500/20 text-red-500'
  }
  return classes[type] || 'bg-white/10 text-gray-400'
}

const updateProfile = async () => {
  saving.value = true
  try {
    // TODO: API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    window.$message?.success('Profil güncellendi')
  } catch (error) {
    window.$message?.error('Profil güncellenemedi')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    window.$message?.error('Şifreler eşleşmiyor!')
    return
  }
  savingPassword.value = true
  try {
    // TODO: API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    window.$message?.success('Şifre güncellendi')
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    window.$message?.error('Şifre güncellenemedi')
  } finally {
    savingPassword.value = false
  }
}

const enable2FA = () => {
  window.$message?.info('2FA kurulum modalı açılacak')
}

const disable2FA = () => {
  window.$dialog?.warning({
    title: 'Uyarı',
    content: '2FA\'yı devre dışı bırakmak istediğinizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: () => {
      // TODO: API call
      window.$message?.success('2FA devre dışı bırakıldı')
    }
  })
}

const revokeSession = (sessionId) => {
  window.$dialog?.warning({
    title: 'Oturumu Sonlandır',
    content: 'Bu oturumu sonlandırmak istediğinizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: () => {
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      window.$message?.success('Oturum sonlandırıldı')
    }
  })
}

const revokeAllSessions = () => {
  window.$dialog?.warning({
    title: 'Tüm Oturumları Sonlandır',
    content: 'Mevcut oturum hariç tüm oturumları sonlandırmak istediğinizden emin misiniz?',
    positiveText: 'Evet',
    negativeText: 'İptal',
    onPositiveClick: () => {
      sessions.value = sessions.value.filter(s => s.is_current)
      window.$message?.success('Tüm oturumlar sonlandırıldı')
    }
  })
}

const saveSettings = async () => {
  savingSettings.value = true
  try {
    // TODO: API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    window.$message?.success('Ayarlar kaydedildi')
  } catch (error) {
    window.$message?.error('Ayarlar kaydedilemedi')
  } finally {
    savingSettings.value = false
  }
}

const downloadBackupCodes = () => {
  const content = backupCodes.value.join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '2fa-backup-codes.txt'
  a.click()
  URL.revokeObjectURL(url)
  window.$message?.success('Yedek kodlar indirildi')
}

onMounted(() => {
  if (user.value) {
    profileForm.username = user.value.username || ''
    profileForm.email = user.value.email || ''
  }
})
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
