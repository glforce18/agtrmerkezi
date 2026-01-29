<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-primary text-4xl mb-4">⏳</div>
      <p class="text-gray-400">Profil yükleniyor...</p>
    </div>

    <div v-else-if="user" class="max-w-4xl mx-auto">
      <!-- Profile Header -->
      <div class="card mb-6">
        <div class="flex items-center space-x-6">
          <!-- Avatar -->
          <div class="w-24 h-24 bg-primary rounded-full flex items-center justify-center overflow-hidden">
            <img v-if="user.avatar" :src="user.avatar" :alt="user.username" class="w-full h-full object-cover" />
            <span v-else class="text-white text-4xl font-bold">{{ getInitials(user.username) }}</span>
          </div>

          <!-- User Info -->
          <div class="flex-1">
            <h1 class="text-3xl font-bold text-white mb-2">{{ user.username }}</h1>
            <div class="flex items-center space-x-4 text-sm">
              <span class="badge badge-primary">
                {{ getRoleText(user.role) }}
              </span>
              <span class="text-gray-400">Üyelik: {{ formatDate(user.created_at) }}</span>
            </div>
          </div>

          <!-- Edit Button -->
          <button
            @click="showEditModal = true"
            class="btn btn-primary"
          >
            Profili Düzenle
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div class="card">
          <div class="text-gray-400 text-sm mb-1">Sunucularım</div>
          <div class="text-3xl font-bold text-white">{{ user.server_count || 0 }}</div>
        </div>

        <div class="card">
          <div class="text-gray-400 text-sm mb-1">Forum Mesajları</div>
          <div class="text-3xl font-bold text-white">{{ user.post_count || 0 }}</div>
        </div>

        <div class="card">
          <div class="text-gray-400 text-sm mb-1">Toplam Harcama</div>
          <div class="text-3xl font-bold text-primary">₺{{ formatMoney(user.total_spent) }}</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="mb-6">
        <div class="flex space-x-2 border-b border-gray-700">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            class="px-4 py-2 font-semibold transition-colors"
            :class="activeTab === tab.id
              ? 'text-primary border-b-2 border-primary'
              : 'text-gray-400 hover:text-white'"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="card">
        <!-- Account Info Tab -->
        <div v-if="activeTab === 'info'">
          <h2 class="text-xl font-bold text-white mb-4">Hesap Bilgileri</h2>

          <div class="space-y-4">
            <div>
              <label class="block text-gray-400 text-sm mb-1">Kullanıcı Adı</label>
              <div class="text-white">{{ user.username }}</div>
            </div>

            <div v-if="user.steam_id">
              <label class="block text-gray-400 text-sm mb-1">Steam ID</label>
              <div class="text-white">{{ user.steam_id }}</div>
            </div>

            <div>
              <label class="block text-gray-400 text-sm mb-1">Rol</label>
              <div class="text-white">{{ getRoleText(user.role) }}</div>
            </div>

            <div>
              <label class="block text-gray-400 text-sm mb-1">Üyelik Tarihi</label>
              <div class="text-white">{{ formatFullDate(user.created_at) }}</div>
            </div>

            <div>
              <label class="block text-gray-400 text-sm mb-1">Son Giriş</label>
              <div class="text-white">{{ formatFullDate(user.last_login) }}</div>
            </div>
          </div>
        </div>

        <!-- Activity Tab -->
        <div v-else-if="activeTab === 'activity'">
          <h2 class="text-xl font-bold text-white mb-4">Son Aktiviteler</h2>

          <div v-if="activities.length" class="space-y-3">
            <div
              v-for="activity in activities"
              :key="activity.id"
              class="flex items-center justify-between p-3 bg-dark-elevated border border-dark-border rounded"
            >
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-primary/20 rounded flex items-center justify-center">
                  <span>{{ getActivityIcon(activity.type) }}</span>
                </div>
                <div>
                  <div class="text-white">{{ activity.description }}</div>
                  <div class="text-gray-400 text-xs">{{ formatDate(activity.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-12 text-gray-400">
            <div class="text-6xl mb-4">📊</div>
            <p>Henüz aktivite bulunmuyor</p>
          </div>
        </div>

        <!-- Security Tab -->
        <div v-else-if="activeTab === 'security'">
          <h2 class="text-xl font-bold text-white mb-4">Güvenlik</h2>

          <div class="space-y-6">
            <!-- Steam Account -->
            <div>
              <h3 class="text-lg text-white mb-3">Steam Hesabı</h3>
              <div v-if="user.steam_id" class="bg-dark-elevated border border-dark-border rounded p-4">
                <div class="flex items-center space-x-4">
                  <img v-if="user.avatar" :src="user.avatar" :alt="user.username" class="w-16 h-16 rounded-full" />
                  <div>
                    <div class="text-white font-semibold">{{ user.username }}</div>
                    <div class="text-gray-400 text-sm">Steam ID: {{ user.steam_id }}</div>
                    <div class="text-green-500 text-sm mt-1">✓ Bağlı</div>
                  </div>
                </div>
              </div>
              <div v-else class="bg-dark-elevated border border-dark-border rounded p-4 text-gray-400">
                Steam hesabı bağlı değil
              </div>
            </div>

            <!-- Two Factor Authentication -->
            <div class="pt-6 border-t border-dark-border">
              <h3 class="text-lg text-white mb-3">İki Faktörlü Kimlik Doğrulama</h3>
              <p class="text-gray-400 text-sm mb-4">Hesabınızı daha güvenli hale getirin</p>
              <button class="btn btn-secondary">
                {{ user.two_factor_enabled ? 'Devre Dışı Bırak' : 'Etkinleştir' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4">
      <div class="card max-w-md w-full">
        <h2 class="text-2xl font-bold text-white mb-4">Profili Düzenle</h2>

        <form @submit.prevent="handleUpdateProfile" class="space-y-4">
          <div>
            <label class="block text-gray-400 text-sm mb-1">E-posta</label>
            <input
              v-model="editForm.email"
              type="email"
              class="input"
              required
            />
          </div>

          <div>
            <label class="block text-gray-400 text-sm mb-1">İmza</label>
            <textarea
              v-model="editForm.signature"
              rows="3"
              class="input"
              placeholder="Forum mesajlarınızda görünecek imza..."
              maxlength="200"
            ></textarea>
            <p class="text-gray-500 text-xs mt-1">{{ editForm.signature?.length || 0 }}/200</p>
          </div>

          <div v-if="editError" class="alert alert-danger">
            {{ editError }}
          </div>

          <div class="flex space-x-3">
            <button
              type="button"
              @click="showEditModal = false"
              class="flex-1 btn btn-secondary"
            >
              İptal
            </button>
            <button
              type="submit"
              :disabled="editLoading"
              class="flex-1 btn btn-primary"
              :class="{ 'opacity-50 cursor-not-allowed': editLoading }"
            >
              {{ editLoading ? 'Kaydediliyor...' : 'Kaydet' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import authAPI from '@/api/auth'

const authStore = useAuthStore()

const loading = ref(true)
const user = ref(null)
const activeTab = ref('info')
const activities = ref([])

const showEditModal = ref(false)
const editForm = ref({
  email: '',
  signature: ''
})
const editLoading = ref(false)
const editError = ref(null)

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})
const passwordLoading = ref(false)
const passwordError = ref(null)
const passwordSuccess = ref(false)

const tabs = [
  { id: 'info', label: 'Hesap Bilgileri' },
  { id: 'activity', label: 'Aktiviteler' },
  { id: 'security', label: 'Güvenlik' }
]

onMounted(async () => {
  await fetchProfile()
})

const fetchProfile = async () => {
  try {
    const response = await authAPI.getMe()
    user.value = response.data
    editForm.value = {
      email: user.value.email,
      signature: user.value.signature || ''
    }

    // Fetch activities
    // TODO: Add activities API endpoint
  } catch (error) {
    console.error('Failed to fetch profile:', error)
  } finally {
    loading.value = false
  }
}

const handleUpdateProfile = async () => {
  editLoading.value = true
  editError.value = null

  try {
    await authAPI.updateProfile(editForm.value)
    await fetchProfile()
    showEditModal.value = false
  } catch (error) {
    editError.value = error.response?.data?.detail || 'Profil güncellenemedi'
  } finally {
    editLoading.value = false
  }
}

const handleChangePassword = async () => {
  passwordError.value = null
  passwordSuccess.value = false

  if (passwordForm.value.new !== passwordForm.value.confirm) {
    passwordError.value = 'Yeni şifreler eşleşmiyor'
    return
  }

  passwordLoading.value = true

  try {
    await authAPI.changePassword({
      current_password: passwordForm.value.current,
      new_password: passwordForm.value.new
    })

    passwordSuccess.value = true
    passwordForm.value = { current: '', new: '', confirm: '' }
  } catch (error) {
    passwordError.value = error.response?.data?.detail || 'Şifre değiştirilemedi'
  } finally {
    passwordLoading.value = false
  }
}

const getInitials = (username) => {
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
}

const getRoleText = (role) => {
  const roles = {
    admin: 'Yönetici',
    moderator: 'Moderatör',
    user: 'Kullanıcı'
  }
  return roles[role] || 'Kullanıcı'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Bilinmiyor'

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffDays === 0) return 'Bugün'
  if (diffDays === 1) return 'Dün'
  if (diffDays < 30) return `${diffDays} gün önce`

  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatFullDate = (dateString) => {
  if (!dateString) return 'Bilinmiyor'

  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatMoney = (amount) => {
  if (!amount) return '0'
  return new Intl.NumberFormat('tr-TR').format(amount)
}

const getActivityIcon = (type) => {
  const icons = {
    server_created: '🖥️',
    server_deleted: '🗑️',
    payment: '💳',
    forum_post: '💬',
    profile_update: '👤'
  }
  return icons[type] || '📝'
}
</script>

<style scoped>
</style>
