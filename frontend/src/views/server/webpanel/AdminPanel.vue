<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <h2 class="text-2xl font-bold text-white">Admin & Ban Yönetimi</h2>
      <p class="text-gray-400 text-sm mt-1">users.ini ve banned.cfg dosyalarını yönetin</p>
    </div>

    <!-- Admin Management -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-white flex items-center gap-2">
          <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Admin Kullanıcılar
          <span class="text-sm text-gray-400 font-normal">({{ admins.length }})</span>
        </h3>
        <button
          @click="showAddAdmin = true"
          class="btn-primary"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Admin Ekle
        </button>
      </div>

      <AdminList
        :admins="admins"
        :loading="loadingAdmins"
        @delete="handleDeleteAdmin"
      />
    </div>

    <!-- Ban Management -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-white flex items-center gap-2">
          <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          Ban Listesi
          <span class="text-sm text-gray-400 font-normal">({{ bans.length }})</span>
        </h3>
        <button
          @click="showAddBan = true"
          class="btn-primary bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Ban Ekle
        </button>
      </div>

      <BanList
        :bans="bans"
        :loading="loadingBans"
        @delete="handleDeleteBan"
      />
    </div>

    <!-- Add Admin Modal -->
    <AddAdminModal
      v-if="showAddAdmin"
      :server-id="serverId"
      @close="showAddAdmin = false"
      @added="handleAdminAdded"
    />

    <!-- Add Ban Modal -->
    <AddBanModal
      v-if="showAddBan"
      :server-id="serverId"
      @close="showAddBan = false"
      @added="handleBanAdded"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import AdminList from '@/components/server/admin/AdminList.vue'
import BanList from '@/components/server/admin/BanList.vue'
import AddAdminModal from '@/components/server/admin/AddAdminModal.vue'
import AddBanModal from '@/components/server/admin/AddBanModal.vue'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loadingAdmins = ref(false)
const loadingBans = ref(false)

const admins = ref([])
const bans = ref([])

const showAddAdmin = ref(false)
const showAddBan = ref(false)

const fetchAdmins = async () => {
  loadingAdmins.value = true
  try {
    const response = await api.getAdminUsers(serverId.value)

    if (response.success) {
      admins.value = response.data.admins || []
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Adminler yüklenirken hata oluştu', 'error')
  } finally {
    loadingAdmins.value = false
  }
}

const fetchBans = async () => {
  loadingBans.value = true
  try {
    const response = await api.getBans(serverId.value)

    if (response.success) {
      bans.value = response.data.bans || []
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Banlar yüklenirken hata oluştu', 'error')
  } finally {
    loadingBans.value = false
  }
}

const handleDeleteAdmin = async (admin) => {
  if (!confirm(`"${admin.steam_id}" adminini silmek istediğinizden emin misiniz?`)) {
    return
  }

  try {
    const response = await api.deleteAdminUser(serverId.value, admin.steam_id)

    if (response.success) {
      toast.show(response.message, 'success')
      await fetchAdmins()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Admin silinemedi', 'error')
  }
}

const handleDeleteBan = async (ban) => {
  if (!confirm(`"${ban.value}" banını kaldırmak istediğinizden emin misiniz?`)) {
    return
  }

  try {
    const response = await api.deleteBan(serverId.value, ban.type, ban.value)

    if (response.success) {
      toast.show(response.message, 'success')
      await fetchBans()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Ban kaldırılamadı', 'error')
  }
}

const handleAdminAdded = () => {
  showAddAdmin.value = false
  fetchAdmins()
}

const handleBanAdded = () => {
  showAddBan.value = false
  fetchBans()
}

onMounted(() => {
  fetchAdmins()
  fetchBans()
})
</script>

<style scoped>
.glass-card {
  @apply bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl;
}

.btn-primary {
  @apply px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl flex items-center gap-2;
}
</style>
