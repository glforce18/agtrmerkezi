<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Profile Header -->
      <div class="mb-8">
        <BaseCard variant="glass">
          <div class="flex flex-col md:flex-row items-center gap-6">
            <!-- Avatar -->
            <div class="relative">
              <div class="avatar">
                <div class="w-32 h-32 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
                  <img :src="user?.avatar || '/default-avatar.png'" :alt="user?.username" />
                </div>
              </div>
              <button class="btn btn-circle btn-sm btn-primary absolute bottom-0 right-0">
                <CameraIcon class="w-4 h-4" />
              </button>
            </div>

            <!-- User Info -->
            <div class="flex-1 text-center md:text-left">
              <h1 class="text-3xl font-bold mb-2">
                {{ user?.username }}
                <span v-if="user?.verified" class="badge badge-primary badge-sm ml-2">
                  <CheckCircleIcon class="w-3 h-3 mr-1" /> Doğrulanmış
                </span>
              </h1>
              <p class="opacity-60 mb-4">{{ user?.email }}</p>
              <div class="flex flex-wrap gap-2 justify-center md:justify-start">
                <div class="badge badge-outline">
                  <CalendarIcon class="w-3 h-3 mr-1" />
                  {{ formatDate(user?.created_at) }} tarihinde katıldı
                </div>
                <div class="badge badge-outline">
                  <ServerIcon class="w-3 h-3 mr-1" />
                  {{ user?.servers_count || 0 }} Sunucu
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="flex gap-2">
              <BaseButton variant="primary" size="sm" @click="activeTab = 'settings'">
                <SettingsIcon class="w-4 h-4 mr-1" /> Ayarlar
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Tabs -->
      <div class="tabs tabs-boxed bg-base-200/50 mb-6">
        <a class="tab" :class="{ 'tab-active': activeTab === 'profile' }" @click="activeTab = 'profile'">
          <UserIcon class="w-4 h-4 mr-2" /> Profil
        </a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'security' }" @click="activeTab = 'security'">
          <ShieldCheckIcon class="w-4 h-4 mr-2" /> Güvenlik
        </a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'settings' }" @click="activeTab = 'settings'">
          <SettingsIcon class="w-4 h-4 mr-2" /> Ayarlar
        </a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'activity' }" @click="activeTab = 'activity'">
          <ActivityIcon class="w-4 h-4 mr-2" /> Aktivite
        </a>
      </div>

      <!-- Tab Content -->
      <div v-if="activeTab === 'profile'">
        <BaseCard variant="glass">
          <template #title>Profil Bilgileri</template>

          <form @submit.prevent="updateProfile" class="space-y-6">
            <div class="grid md:grid-cols-2 gap-4">
              <BaseInput
                v-model="profileForm.username"
                label="Kullanıcı Adı"
                placeholder="kullaniciadi"
                required
              />

              <BaseInput
                v-model="profileForm.email"
                label="E-posta"
                type="email"
                placeholder="ornek@email.com"
                required
              />

              <BaseInput
                v-model="profileForm.first_name"
                label="Ad"
                placeholder="Adınız"
              />

              <BaseInput
                v-model="profileForm.last_name"
                label="Soyad"
                placeholder="Soyadınız"
              />

              <BaseInput
                v-model="profileForm.phone"
                label="Telefon"
                placeholder="+90 555 123 4567"
              />

              <BaseInput
                v-model="profileForm.country"
                label="Ülke"
                placeholder="Türkiye"
              />
            </div>

            <div>
              <label class="label">
                <span class="label-text">Biyografi</span>
              </label>
              <textarea
                v-model="profileForm.bio"
                class="textarea textarea-bordered w-full"
                placeholder="Kendinizden bahsedin..."
                rows="4"
              ></textarea>
            </div>

            <div class="flex justify-end gap-2">
              <BaseButton variant="ghost" type="button">İptal</BaseButton>
              <BaseButton variant="primary" type="submit" :loading="saving">
                Kaydet
              </BaseButton>
            </div>
          </form>
        </BaseCard>
      </div>

      <div v-else-if="activeTab === 'security'">
        <div class="space-y-6">
          <!-- Change Password -->
          <BaseCard variant="glass">
            <template #title>Şifre Değiştir</template>

            <form @submit.prevent="changePassword" class="space-y-4">
              <BaseInput
                v-model="passwordForm.current_password"
                label="Mevcut Şifre"
                type="password"
                placeholder="••••••••"
                required
              />

              <BaseInput
                v-model="passwordForm.new_password"
                label="Yeni Şifre"
                type="password"
                placeholder="••••••••"
                required
              />

              <BaseInput
                v-model="passwordForm.confirm_password"
                label="Yeni Şifre (Tekrar)"
                type="password"
                placeholder="••••••••"
                required
              />

              <div class="flex justify-end gap-2">
                <BaseButton variant="primary" type="submit" :loading="savingPassword">
                  Şifreyi Güncelle
                </BaseButton>
              </div>
            </form>
          </BaseCard>

          <!-- Two-Factor Authentication -->
          <BaseCard variant="glass">
            <template #title>
              <div class="flex items-center justify-between">
                <span>İki Faktörlü Doğrulama (2FA)</span>
                <span v-if="user?.two_factor_enabled" class="badge badge-success">Aktif</span>
                <span v-else class="badge badge-warning">Pasif</span>
              </div>
            </template>

            <div class="space-y-4">
              <p class="text-sm opacity-60">
                İki faktörlü doğrulama, hesabınıza ek bir güvenlik katmanı ekler.
                Giriş yaparken şifrenizin yanında authenticator uygulamanızdan bir kod girmeniz gerekir.
              </p>

              <div v-if="!user?.two_factor_enabled">
                <BaseButton variant="primary" @click="enable2FA">
                  <ShieldCheckIcon class="w-4 h-4 mr-2" /> 2FA'yı Etkinleştir
                </BaseButton>
              </div>

              <div v-else class="space-y-4">
                <div class="alert alert-success">
                  <CheckCircleIcon class="w-5 h-5" />
                  <span>2FA başarıyla etkinleştirildi!</span>
                </div>

                <div class="flex gap-2">
                  <BaseButton variant="outline" size="sm" @click="show2FABackupCodes = true">
                    <KeyIcon class="w-4 h-4 mr-1" /> Yedek Kodları Gör
                  </BaseButton>
                  <BaseButton variant="error" size="sm" @click="disable2FA">
                    <XCircleIcon class="w-4 h-4 mr-1" /> 2FA'yı Devre Dışı Bırak
                  </BaseButton>
                </div>
              </div>
            </div>
          </BaseCard>

          <!-- Active Sessions -->
          <BaseCard variant="glass">
            <template #title>Aktif Oturumlar</template>

            <div class="space-y-3">
              <div v-for="session in sessions" :key="session.id"
                   class="flex items-center justify-between p-4 bg-base-200/50 rounded-lg">
                <div class="flex items-center gap-4">
                  <div class="p-3 bg-base-200/50 rounded-lg">
                    <MonitorIcon v-if="session.device_type === 'desktop'" class="w-5 h-5" />
                    <SmartphoneIcon v-else class="w-5 h-5" />
                  </div>
                  <div>
                    <h4 class="font-medium">{{ session.device_name }}</h4>
                    <p class="text-sm opacity-60">{{ session.ip }} • {{ session.location }}</p>
                    <p class="text-xs opacity-50">
                      Son aktivite: {{ formatTime(session.last_activity) }}
                    </p>
                  </div>
                </div>

                <div>
                  <span v-if="session.is_current" class="badge badge-success badge-sm">Mevcut</span>
                  <BaseButton v-else variant="ghost" size="sm" @click="revokeSession(session.id)">
                    Sonlandır
                  </BaseButton>
                </div>
              </div>
            </div>

            <div class="mt-4 flex justify-end">
              <BaseButton variant="error" size="sm" @click="revokeAllSessions">
                Tüm Oturumları Sonlandır
              </BaseButton>
            </div>
          </BaseCard>
        </div>
      </div>

      <div v-else-if="activeTab === 'settings'">
        <BaseCard variant="glass">
          <template #title>Tercihler</template>

          <div class="space-y-6">
            <!-- Notifications -->
            <div>
              <h3 class="font-semibold mb-4">Bildirimler</h3>
              <div class="space-y-3">
                <label class="flex items-center justify-between cursor-pointer">
                  <span class="text-sm">E-posta bildirimleri</span>
                  <input type="checkbox" v-model="settings.email_notifications" class="toggle toggle-primary" />
                </label>
                <label class="flex items-center justify-between cursor-pointer">
                  <span class="text-sm">Sunucu uyarıları</span>
                  <input type="checkbox" v-model="settings.server_alerts" class="toggle toggle-primary" />
                </label>
                <label class="flex items-center justify-between cursor-pointer">
                  <span class="text-sm">Güvenlik bildirimleri</span>
                  <input type="checkbox" v-model="settings.security_alerts" class="toggle toggle-primary" />
                </label>
              </div>
            </div>

            <div class="divider"></div>

            <!-- Privacy -->
            <div>
              <h3 class="font-semibold mb-4">Gizlilik</h3>
              <div class="space-y-3">
                <label class="flex items-center justify-between cursor-pointer">
                  <span class="text-sm">Profili herkese açık yap</span>
                  <input type="checkbox" v-model="settings.public_profile" class="toggle toggle-primary" />
                </label>
                <label class="flex items-center justify-between cursor-pointer">
                  <span class="text-sm">Online durumunu göster</span>
                  <input type="checkbox" v-model="settings.show_online_status" class="toggle toggle-primary" />
                </label>
              </div>
            </div>

            <div class="flex justify-end gap-2">
              <BaseButton variant="primary" @click="saveSettings" :loading="savingSettings">
                Ayarları Kaydet
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>

      <div v-else-if="activeTab === 'activity'">
        <BaseCard variant="glass">
          <template #title>Son Aktiviteler</template>

          <div class="space-y-3">
            <div v-for="activity in activities" :key="activity.id"
                 class="flex gap-4 p-4 bg-base-200/50 rounded-lg">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full flex items-center justify-center"
                     :class="getActivityIconClass(activity.type)">
                  <component :is="getActivityIcon(activity.type)" class="w-5 h-5" />
                </div>
              </div>
              <div class="flex-1">
                <p class="font-medium">{{ activity.title }}</p>
                <p class="text-sm opacity-60">{{ activity.description }}</p>
                <p class="text-xs opacity-50 mt-1">{{ formatTime(activity.created_at) }}</p>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>

    <!-- 2FA Backup Codes Modal -->
    <div v-if="show2FABackupCodes" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Yedek Kodlar</h3>
        <p class="text-sm opacity-60 mb-4">
          Bu kodları güvenli bir yerde saklayın. Authenticator uygulamanıza erişiminizi kaybederseniz
          bu kodları kullanarak giriş yapabilirsiniz.
        </p>
        <div class="grid grid-cols-2 gap-2 mb-6">
          <div v-for="code in backupCodes" :key="code"
               class="p-3 bg-base-200 rounded font-mono text-center">
            {{ code }}
          </div>
        </div>
        <div class="modal-action">
          <BaseButton variant="ghost" @click="show2FABackupCodes = false">Kapat</BaseButton>
          <BaseButton variant="primary" @click="downloadBackupCodes">İndir</BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
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
  return formatDistanceToNow(new Date(timestamp), {
    addSuffix: true,
    locale: tr
  })
}

const formatDate = (timestamp) => {
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
    info: 'bg-info/20 text-info',
    success: 'bg-success/20 text-success',
    warning: 'bg-warning/20 text-warning',
    error: 'bg-error/20 text-error'
  }
  return classes[type] || 'bg-base-200/50 opacity-60'
}

const updateProfile = async () => {
  saving.value = true
  // TODO: API call
  setTimeout(() => {
    saving.value = false
  }, 1000)
}

const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    alert('Şifreler eşleşmiyor!')
    return
  }
  savingPassword.value = true
  // TODO: API call
  setTimeout(() => {
    savingPassword.value = false
  }, 1000)
}

const enable2FA = () => {
  // TODO: Show 2FA setup modal
  alert('2FA setup modal gösterilecek')
}

const disable2FA = () => {
  if (confirm('2FA\'yı devre dışı bırakmak istediğinizden emin misiniz?')) {
    // TODO: API call
  }
}

const revokeSession = (sessionId) => {
  if (confirm('Bu oturumu sonlandırmak istediğinizden emin misiniz?')) {
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
  }
}

const revokeAllSessions = () => {
  if (confirm('Mevcut oturum hariç tüm oturumları sonlandırmak istediğinizden emin misiniz?')) {
    sessions.value = sessions.value.filter(s => s.is_current)
  }
}

const saveSettings = async () => {
  savingSettings.value = true
  // TODO: API call
  setTimeout(() => {
    savingSettings.value = false
  }, 1000)
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
}

onMounted(() => {
  if (user.value) {
    profileForm.username = user.value.username || ''
    profileForm.email = user.value.email || ''
  }
})
</script>
