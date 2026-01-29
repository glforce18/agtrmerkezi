<template>
  <div class="min-h-screen bg-dark-bg py-8">
    <div class="container mx-auto px-4 max-w-7xl">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-2">
          Sunucu Onay Paneli
        </h1>
        <p class="text-gray-400">
          Bekleyen sunucu siparişlerini onaylayın veya reddedin
        </p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-dark-card border border-primary/20 rounded-lg p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm mb-1">Bekleyen Sunucular</p>
              <p class="text-3xl font-bold text-primary">{{ pendingServers.length }}</p>
            </div>
            <div class="text-4xl">🕐</div>
          </div>
        </div>

        <div class="bg-dark-card border border-green-500/20 rounded-lg p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm mb-1">Bugün Onaylanan</p>
              <p class="text-3xl font-bold text-green-400">{{ stats.approvedToday || 0 }}</p>
            </div>
            <div class="text-4xl">✅</div>
          </div>
        </div>

        <div class="bg-dark-card border border-red-500/20 rounded-lg p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm mb-1">Bugün Reddedilen</p>
              <p class="text-3xl font-bold text-red-400">{{ stats.rejectedToday || 0 }}</p>
            </div>
            <div class="text-4xl">❌</div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        <p class="text-gray-400 mt-4">Sunucular yükleniyor...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-500/10 border border-red-500/30 rounded-lg p-6 text-center">
        <p class="text-red-400">{{ error }}</p>
        <button @click="fetchPendingServers" class="mt-4 px-6 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition">
          Tekrar Dene
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="pendingServers.length === 0" class="bg-dark-card border border-primary/20 rounded-lg p-12 text-center">
        <div class="text-6xl mb-4">🎉</div>
        <h3 class="text-xl font-bold text-white mb-2">Bekleyen Sunucu Yok</h3>
        <p class="text-gray-400">Tüm siparişler işlenmiş durumda</p>
      </div>

      <!-- Servers Table -->
      <div v-else class="bg-dark-card border border-primary/20 rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-dark-bg/50 border-b border-primary/20">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Sunucu Adı
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Oyun
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Sahip
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  IP:Port
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Slot
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Fiyat
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Tarih
                </th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  İşlemler
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary/10">
              <tr v-for="server in pendingServers" :key="server.id" class="hover:bg-dark-bg/30 transition">
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-white font-mono text-sm">{{ server.id }}</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <span class="text-white font-semibold">{{ server.name }}</span>
                    <span v-if="server.package_id" class="text-xs text-gray-500">(Paket #{{ server.package_id }})</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold"
                    :class="getGameBadgeClass(server.game_type)">
                    {{ getGameLabel(server.game_type) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-gray-300">User #{{ server.owner_id }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-gray-300 font-mono text-sm">{{ server.ip }}:{{ server.port }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-white">{{ server.slots }} kişi</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-green-400 font-semibold">₺{{ server.monthly_price }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-gray-400 text-sm">{{ formatDate(server.created_at) }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center justify-center gap-2">
                    <button
                      @click="confirmApprove(server)"
                      :disabled="processing === server.id"
                      class="px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white rounded-lg font-semibold transition flex items-center gap-2"
                    >
                      <span v-if="processing === server.id">⏳</span>
                      <span v-else>✅</span>
                      <span>Onayla</span>
                    </button>
                    <button
                      @click="openRejectModal(server)"
                      :disabled="processing === server.id"
                      class="px-4 py-2 bg-red-500 hover:bg-red-600 disabled:bg-gray-600 text-white rounded-lg font-semibold transition flex items-center gap-2"
                    >
                      <span v-if="processing === server.id">⏳</span>
                      <span v-else>❌</span>
                      <span>Reddet</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Approve Confirmation Modal -->
    <div v-if="showApproveModal" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div class="bg-dark-card border border-primary/30 rounded-lg max-w-md w-full p-6">
        <h3 class="text-xl font-bold text-white mb-4">Sunucuyu Onayla</h3>
        <p class="text-gray-300 mb-6">
          <strong>{{ selectedServer?.name }}</strong> sunucusunu onaylamak istediğinize emin misiniz?
        </p>
        <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-6">
          <p class="text-blue-300 text-sm">
            ℹ️ Onaylandıktan sonra otomatik kurulum başlayacak ve kullanıcı sunucusunu yönetebilecek.
          </p>
        </div>
        <div class="flex gap-3">
          <button
            @click="approveServer(selectedServer)"
            class="flex-1 px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition"
          >
            Evet, Onayla
          </button>
          <button
            @click="showApproveModal = false"
            class="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition"
          >
            İptal
          </button>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div class="bg-dark-card border border-red-500/30 rounded-lg max-w-md w-full p-6">
        <h3 class="text-xl font-bold text-white mb-4">Sunucuyu Reddet</h3>
        <p class="text-gray-300 mb-4">
          <strong>{{ selectedServer?.name }}</strong> sunucusunu reddetmek istediğinize emin misiniz?
        </p>
        <div class="mb-6">
          <label class="block text-gray-400 text-sm mb-2">Red Sebebi (zorunlu)</label>
          <textarea
            v-model="rejectReason"
            placeholder="Örn: Sunucu adı uygunsuz, geçersiz bilgiler..."
            class="w-full px-4 py-3 bg-dark-bg border border-primary/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
            rows="4"
          ></textarea>
        </div>
        <div class="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
          <p class="text-red-300 text-sm">
            ⚠️ Reddedilen sunucu için kullanıcıya otomatik para iadesi yapılacaktır.
          </p>
        </div>
        <div class="flex gap-3">
          <button
            @click="rejectServer(selectedServer)"
            :disabled="!rejectReason.trim()"
            class="flex-1 px-6 py-3 bg-red-500 hover:bg-red-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition"
          >
            Evet, Reddet
          </button>
          <button
            @click="closeRejectModal"
            class="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition"
          >
            İptal
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast.show" class="fixed bottom-4 right-4 z-50 animate-slide-in-bottom">
      <div
        class="px-6 py-4 rounded-lg shadow-lg border flex items-center gap-3"
        :class="toast.type === 'success' ? 'bg-green-500/90 border-green-400 text-white' : 'bg-red-500/90 border-red-400 text-white'"
      >
        <span class="text-2xl">{{ toast.type === 'success' ? '✅' : '❌' }}</span>
        <span class="font-semibold">{{ toast.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminAPI from '@/api/admin'

// State
const pendingServers = ref([])
const loading = ref(true)
const error = ref(null)
const processing = ref(null)
const stats = ref({
  approvedToday: 0,
  rejectedToday: 0
})

// Modals
const showApproveModal = ref(false)
const showRejectModal = ref(false)
const selectedServer = ref(null)
const rejectReason = ref('')

// Toast
const toast = ref({
  show: false,
  type: 'success',
  message: ''
})

// Fetch pending servers
const fetchPendingServers = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await adminAPI.getPendingServers()
    pendingServers.value = response.data.servers || []
  } catch (err) {
    console.error('Failed to fetch pending servers:', err)
    error.value = err.response?.data?.detail || 'Sunucular yüklenirken hata oluştu'
  } finally {
    loading.value = false
  }
}

// Confirm approve
const confirmApprove = (server) => {
  selectedServer.value = server
  showApproveModal.value = true
}

// Approve server
const approveServer = async (server) => {
  showApproveModal.value = false
  processing.value = server.id

  try {
    const response = await adminAPI.approveServer(server.id, true)

    // Remove from list
    pendingServers.value = pendingServers.value.filter(s => s.id !== server.id)

    // Update stats
    stats.value.approvedToday++

    // Show success toast
    showToast('success', `${server.name} başarıyla onaylandı ve kurulum başlatıldı!`)
  } catch (err) {
    console.error('Failed to approve server:', err)
    showToast('error', err.response?.data?.detail || 'Sunucu onaylanırken hata oluştu')
  } finally {
    processing.value = null
  }
}

// Open reject modal
const openRejectModal = (server) => {
  selectedServer.value = server
  rejectReason.value = ''
  showRejectModal.value = true
}

// Close reject modal
const closeRejectModal = () => {
  showRejectModal.value = false
  selectedServer.value = null
  rejectReason.value = ''
}

// Reject server
const rejectServer = async (server) => {
  if (!rejectReason.value.trim()) {
    return
  }

  showRejectModal.value = false
  processing.value = server.id

  try {
    const response = await adminAPI.approveServer(server.id, false, rejectReason.value)

    // Remove from list
    pendingServers.value = pendingServers.value.filter(s => s.id !== server.id)

    // Update stats
    stats.value.rejectedToday++

    // Show success toast
    showToast('success', `${server.name} reddedildi`)
  } catch (err) {
    console.error('Failed to reject server:', err)
    showToast('error', err.response?.data?.detail || 'Sunucu reddedilirken hata oluştu')
  } finally {
    processing.value = null
    rejectReason.value = ''
  }
}

// Show toast
const showToast = (type, message) => {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 4000)
}

// Get game badge class
const getGameBadgeClass = (gameType) => {
  const classes = {
    'hldm': 'bg-orange-500/20 text-orange-300 border border-orange-500/30',
    'ag': 'bg-purple-500/20 text-purple-300 border border-purple-500/30',
    'cs16': 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
    'cs16_pro': 'bg-green-500/20 text-green-300 border border-green-500/30',
    'cs16_fun': 'bg-pink-500/20 text-pink-300 border border-pink-500/30'
  }
  return classes[gameType?.toLowerCase()] || 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
}

// Get game label
const getGameLabel = (gameType) => {
  const labels = {
    'hldm': 'Half-Life DM',
    'ag': 'HL: Adrenaline Gamer',
    'cs16': 'CS 1.6',
    'cs16_pro': 'CS 1.6 Pro',
    'cs16_fun': 'CS 1.6 Fun'
  }
  return labels[gameType?.toLowerCase()] || gameType
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// On mounted
onMounted(() => {
  fetchPendingServers()
})
</script>

<style scoped>
@keyframes slide-in-bottom {
  from {
    transform: translateY(100px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-in-bottom {
  animation: slide-in-bottom 0.3s ease-out;
}
</style>
