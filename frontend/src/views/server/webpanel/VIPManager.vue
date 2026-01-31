<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">VIP Manager</h2>
          <p class="text-gray-400 text-sm mt-1">Manage VIP members with custom flags and expiration</p>
        </div>
        <button
          @click="showAddModal = true"
          class="btn-primary"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add VIP
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Total VIPs</div>
          <div class="text-2xl font-bold text-white mt-1">{{ stats.total }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Active VIPs</div>
          <div class="text-2xl font-bold text-green-400 mt-1">{{ stats.active }}</div>
        </div>
        <div class="bg-white/5 rounded-lg p-4">
          <div class="text-gray-400 text-sm">Expired VIPs</div>
          <div class="text-2xl font-bold text-red-400 mt-1">{{ stats.expired }}</div>
        </div>
      </div>
    </div>

    <!-- VIP List -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-bold text-white mb-4">VIP Members</h3>

      <div v-if="loading" class="py-12 text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="vips.length === 0" class="py-12 text-center text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="text-lg">Henüz VIP member yok</p>
        <p class="text-sm text-gray-600 mt-2">"Add VIP" butonuna tıklayarak yeni VIP ekleyebilirsiniz</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-white/10">
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Status</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Player</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Steam ID</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Flags</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Expires</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Notes</th>
              <th class="text-left py-3 px-4 text-gray-400 font-medium text-sm">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="vip in vips"
              :key="vip.id"
              class="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              <td class="py-3 px-4">
                <span
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-500/20 text-green-400': vip.is_active && !vip.is_expired,
                    'bg-red-500/20 text-red-400': vip.is_expired,
                    'bg-gray-500/20 text-gray-400': !vip.is_active
                  }"
                >
                  {{ vip.is_expired ? 'Expired' : (vip.is_active ? 'Active' : 'Inactive') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <div class="text-white font-medium">{{ vip.player_name }}</div>
              </td>
              <td class="py-3 px-4">
                <div class="text-gray-400 font-mono text-sm">{{ vip.steam_id }}</div>
              </td>
              <td class="py-3 px-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="flag in vip.flags.split('')"
                    :key="flag"
                    class="inline-block px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-xs font-mono"
                  >
                    {{ flag }}
                  </span>
                </div>
              </td>
              <td class="py-3 px-4">
                <span v-if="vip.expires_at" class="text-gray-300 text-sm">
                  {{ formatDate(vip.expires_at) }}
                </span>
                <span v-else class="text-green-400 text-sm">Permanent</span>
              </td>
              <td class="py-3 px-4">
                <span class="text-gray-400 text-sm">{{ vip.notes || '-' }}</span>
              </td>
              <td class="py-3 px-4">
                <div class="flex items-center gap-2">
                  <button
                    @click="toggleVIP(vip)"
                    :title="vip.is_active ? 'Deactivate' : 'Activate'"
                    class="p-2 rounded hover:bg-white/10 transition-colors"
                  >
                    <svg v-if="vip.is_active" class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <svg v-else class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  <button
                    @click="editVIP(vip)"
                    class="p-2 rounded hover:bg-blue-500/20 text-blue-400 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteVIP(vip)"
                    class="p-2 rounded hover:bg-red-500/20 text-red-400 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div
      v-if="showAddModal || editingVIP"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      @click.self="closeModal"
    >
      <div class="glass-card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto" @click.stop>
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-white">{{ editingVIP ? 'Edit VIP' : 'Add VIP' }}</h3>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-white"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveVIP" class="space-y-4">
          <!-- Steam ID -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Steam ID *</label>
            <input
              v-model="vipForm.steam_id"
              type="text"
              required
              :disabled="!!editingVIP"
              placeholder="STEAM_0:1:12345678"
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none disabled:opacity-50"
            />
          </div>

          <!-- Player Name -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Player Name *</label>
            <input
              v-model="vipForm.player_name"
              type="text"
              required
              placeholder="Player Name"
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            />
          </div>

          <!-- Flags -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">VIP Flags *</label>
            <div class="grid grid-cols-7 gap-2 mb-2">
              <button
                v-for="flag in availableFlags"
                :key="flag.char"
                type="button"
                @click="toggleFlag(flag.char)"
                class="px-3 py-2 rounded-lg text-sm font-mono transition-colors"
                :class="vipForm.flags.includes(flag.char) ? 'bg-blue-500 text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'"
                :title="flag.description"
              >
                {{ flag.char }}
              </button>
            </div>
            <input
              v-model="vipForm.flags"
              type="text"
              required
              placeholder="abcde"
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white font-mono focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            />
            <p class="text-xs text-gray-500 mt-1">Selected flags: {{ vipForm.flags || 'none' }}</p>
          </div>

          <!-- Expiration -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Expiration Date (Optional)</label>
            <input
              v-model="vipForm.expires_at"
              type="datetime-local"
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
            />
            <p class="text-xs text-gray-500 mt-1">Leave empty for permanent VIP</p>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Notes (Optional)</label>
            <textarea
              v-model="vipForm.notes"
              rows="3"
              placeholder="Admin notes..."
              class="w-full px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
            ></textarea>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="closeModal"
              class="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ saving ? 'Saving...' : (editingVIP ? 'Update VIP' : 'Add VIP') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/api/servers'

const route = useRoute()
const toast = useToast()

const serverId = ref(parseInt(route.params.id))
const loading = ref(false)
const saving = ref(false)
const showAddModal = ref(false)
const editingVIP = ref(null)
const vips = ref([])

const vipForm = ref({
  steam_id: '',
  player_name: '',
  flags: '',
  expires_at: '',
  notes: ''
})

const availableFlags = [
  { char: 'a', description: 'Immunity' },
  { char: 'b', description: 'Reservation' },
  { char: 'c', description: 'Kick' },
  { char: 'd', description: 'Ban' },
  { char: 'e', description: 'Slay' },
  { char: 'f', description: 'Map' },
  { char: 'g', description: 'CVars' },
  { char: 'h', description: 'Config' },
  { char: 'i', description: 'Chat' },
  { char: 'j', description: 'Vote' },
  { char: 'k', description: 'Password' },
  { char: 'l', description: 'RCON' },
  { char: 'm', description: 'Level A' },
  { char: 'n', description: 'Level B' },
  { char: 'o', description: 'Level C' },
  { char: 'p', description: 'Level D' },
  { char: 'q', description: 'Level E' },
  { char: 'r', description: 'Level F' },
  { char: 's', description: 'Level G' },
  { char: 't', description: 'Level H' },
  { char: 'u', description: 'Menu Access' },
]

const stats = computed(() => ({
  total: vips.value.length,
  active: vips.value.filter(v => v.is_active && !v.is_expired).length,
  expired: vips.value.filter(v => v.is_expired).length
}))

const fetchVIPs = async () => {
  loading.value = true
  try {
    const response = await api.getVIPMembers(serverId.value)
    if (response.success) {
      vips.value = response.data.vips
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'VIP listesi yüklenemedi', 'error')
  } finally {
    loading.value = false
  }
}

const toggleFlag = (flag) => {
  if (vipForm.value.flags.includes(flag)) {
    vipForm.value.flags = vipForm.value.flags.replace(flag, '')
  } else {
    vipForm.value.flags += flag
  }
}

const saveVIP = async () => {
  saving.value = true
  try {
    const data = {
      steam_id: vipForm.value.steam_id,
      player_name: vipForm.value.player_name,
      flags: vipForm.value.flags,
      expires_at: vipForm.value.expires_at || null,
      notes: vipForm.value.notes || null
    }

    if (editingVIP.value) {
      const response = await api.updateVIPMember(serverId.value, editingVIP.value.id, data)
      if (response.success) {
        toast.show('VIP güncellendi', 'success')
      }
    } else {
      const response = await api.addVIPMember(serverId.value, data)
      if (response.success) {
        toast.show('VIP eklendi', 'success')
      }
    }

    closeModal()
    await fetchVIPs()
  } catch (error) {
    toast.show(error.response?.data?.detail || 'VIP kaydedilemedi', 'error')
  } finally {
    saving.value = false
  }
}

const editVIP = (vip) => {
  editingVIP.value = vip
  vipForm.value = {
    steam_id: vip.steam_id,
    player_name: vip.player_name,
    flags: vip.flags,
    expires_at: vip.expires_at ? vip.expires_at.substring(0, 16) : '',
    notes: vip.notes || ''
  }
}

const deleteVIP = async (vip) => {
  if (!confirm(`"${vip.player_name}" VIP'sini silmek istediğinizden emin misiniz?`)) return

  try {
    const response = await api.deleteVIPMember(serverId.value, vip.id)
    if (response.success) {
      toast.show('VIP silindi', 'success')
      await fetchVIPs()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'VIP silinemedi', 'error')
  }
}

const toggleVIP = async (vip) => {
  try {
    const response = await api.toggleVIPStatus(serverId.value, vip.id)
    if (response.success) {
      toast.show(response.message, 'success')
      await fetchVIPs()
    }
  } catch (error) {
    toast.show(error.response?.data?.detail || 'Durum değiştirilemedi', 'error')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingVIP.value = null
  vipForm.value = {
    steam_id: '',
    player_name: '',
    flags: '',
    expires_at: '',
    notes: ''
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  await fetchVIPs()
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
